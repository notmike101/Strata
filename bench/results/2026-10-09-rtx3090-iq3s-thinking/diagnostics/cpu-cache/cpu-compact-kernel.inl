// C017 exact nibble cache, isolated from production. No weight requantization.
#include <stdexcept>
namespace compact_probe {
struct Block { uint8_t weights[128]; uint8_t scales[8]; uint16_t d; };
static_assert(sizeof(Block)==138);
template<int TY> const int8_t* values() {
    static constexpr int8_t three[16]={1,3,5,7,9,11,13,15,-1,-3,-5,-7,-9,-11,-13,-15};
    static constexpr int8_t xxs[16]={4,12,20,28,36,44,52,62,-4,-12,-20,-28,-36,-44,-52,-62};
    static constexpr int8_t two[16]={8,25,43,0,0,0,0,0,-8,-25,-43,0,0,0,0,0};
    if constexpr(TY==18)return xxs;
    else if constexpr(TY==21)return three;
    else return two;
}
template<int TY> std::vector<Block> expand_t(const uint8_t* data,size_t blocks) {
    std::vector<Block> out(blocks);const int8_t* table=values<TY>();
    for(size_t i=0;i<blocks;++i) {
        const uint8_t* b=data+i*cpu::Fmt32<TY>::bytes;out[i].d=cpu::u16(b);
        for(int j=0;j<4;++j)for(int h=0;h<2;++h) {
            __m256i g,sgn,sc;cpu::Fmt32<TY>::decode(b,j,h,g,sgn,sc);
            alignas(32) int8_t weights[32];alignas(32) int16_t scales[16];uint8_t codes[32];
            _mm256_store_si256(reinterpret_cast<__m256i*>(weights),_mm256_sign_epi8(g,sgn));
            _mm256_store_si256(reinterpret_cast<__m256i*>(scales),sc);
            for(int q=0;q<32;++q) {
                int code=0;while(code<16 && table[code]!=weights[q])++code;
                if(code==16)throw std::runtime_error("unrepresentable signed grid value");
                codes[q]=static_cast<uint8_t>(code);
            }
            for(int q=0;q<16;++q)if(scales[q]<1||scales[q]>31||!(scales[q]&1)||scales[q]!=scales[q<8?0:8])throw std::runtime_error("unsupported scale");
            const int H=2*j+h;
            for(int q=0;q<16;++q)out[i].weights[16*H+q]=codes[q]|(codes[q+16]<<4);
            out[i].scales[H]=static_cast<uint8_t>(((scales[0]-1)/2)|(((scales[8]-1)/2)<<4));
        }
    }
    return out;
}
std::vector<Block> expand(const uint8_t* data,size_t blocks,int type) {
    switch(type){case 18:return expand_t<18>(data,blocks);case 21:return expand_t<21>(data,blocks);case 22:return expand_t<22>(data,blocks);default:throw std::runtime_error("unsupported type");}
}
template<int TY,int NT> inline void dot(const Block* row,int nb,const block_q8_K* const* y,float* res) {
    const __m128i table=_mm_loadu_si128(reinterpret_cast<const __m128i*>(values<TY>())),mask=_mm_set1_epi8(15);
    __m256 accf[NT];for(int t=0;t<NT;++t)accf[t]=_mm256_setzero_ps();
    const int pf=cpu::prefetch_distance();
    for(int i=0;i<nb;++i) {
        const Block& b=row[i];cpu::rows_ahead(reinterpret_cast<const uint8_t*>(&b),pf);
        __m256i acci[NT];for(int t=0;t<NT;++t)acci[t]=_mm256_setzero_si256();
        for(int H=0;H<8;++H) {
            const __m128i q=_mm_loadu_si128(reinterpret_cast<const __m128i*>(b.weights+16*H));
            const __m128i lo=_mm_shuffle_epi8(table,_mm_and_si128(q,mask));
            const __m128i hi=_mm_shuffle_epi8(table,_mm_and_si128(_mm_srli_epi16(q,4),mask));
            const __m256i signed_g=_mm256_inserti128_si256(_mm256_castsi128_si256(lo),hi,1);
            const __m256i g=_mm256_abs_epi8(signed_g),sgn=_mm256_sign_epi8(_mm256_set1_epi8(1),signed_g);
            const int s=b.scales[H];const __m256i sc=cpu::sc16(2*(s&15)+1,2*(s>>4)+1);
            for(int t=0;t<NT;++t) {
                const __m256i yv=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(y[t][i].qs+32*H));
                acci[t]=cpu::plain::madd_add(acci[t],_mm256_maddubs_epi16(g,_mm256_sign_epi8(yv,sgn)),sc);
            }
        }
        const float d=cpu::h2f(b.d)*cpu::Fmt32<TY>::K;
        for(int t=0;t<NT;++t)accf[t]=_mm256_fmadd_ps(_mm256_set1_ps(d*y[t][i].d),_mm256_cvtepi32_ps(acci[t]),accf[t]);
    }
    for(int t=0;t<NT;++t)res[t]=cpu::hsum8(accf[t]);
}
template<int TY,int NT> void gu_t(const Block* data,int nb,const void* const* act,float* const* out,int rows,int r0,int r1) {
    const block_q8_K* y[NT];for(int t=0;t<NT;++t)y[t]=reinterpret_cast<const block_q8_K*>(act[t]);
    float g[NT],u[NT];
    for(int r=r0;r<r1;++r) {
        dot<TY,NT>(data+size_t(r)*nb,nb,y,g);dot<TY,NT>(data+size_t(rows+r)*nb,nb,y,u);
        for(int t=0;t<NT;++t)out[t][r]=(g[t]/(1.f+std::exp(-g[t])))*u[t];
    }
}
template<int TY> void gu_type(const Block* data,int nb,const void* const* act,int nt,float* const* out,int rows,int r0,int r1) {
    switch(nt) {
#define C017_NT(N) case N:gu_t<TY,N>(data,nb,act,out,rows,r0,r1);break
        C017_NT(1);C017_NT(2);C017_NT(3);C017_NT(4);C017_NT(5);C017_NT(6);C017_NT(7);C017_NT(8);
#undef C017_NT
        default:throw std::runtime_error("unsupported token count");
    }
}
void gu(int type,const Block* data,int nb,const void* const* act,int nt,float* const* out,int rows,int r0=0,int r1=-1) {
    if(r1<0)r1=rows;
    if(r0<0||r1<r0||r1>rows)throw std::runtime_error("invalid row range");
    switch(type){case 18:gu_type<18>(data,nb,act,nt,out,rows,r0,r1);break;case 21:gu_type<21>(data,nb,act,nt,out,rows,r0,r1);break;case 22:gu_type<22>(data,nb,act,nt,out,rows,r0,r1);break;default:throw std::runtime_error("unsupported type");}
}
}
