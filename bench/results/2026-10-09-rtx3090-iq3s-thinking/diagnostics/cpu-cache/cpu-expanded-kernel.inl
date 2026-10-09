// C015 isolated prototype. Never used by the serving engine.
#include <stdexcept>
namespace expanded_probe {
struct alignas(32) Block { int8_t weights[256]; int8_t scales[16]; float d; };
static_assert(sizeof(Block)==288);
template<int TY> std::vector<Block> expand_t(const uint8_t* data,size_t blocks) {
    std::vector<Block> out(blocks);
    for(size_t i=0;i<blocks;++i) {
        const uint8_t* b=data+i*cpu::Fmt32<TY>::bytes;
        out[i].d=cpu::h2f(cpu::u16(b))*cpu::Fmt32<TY>::K;
        for(int j=0;j<4;++j)for(int h=0;h<2;++h) {
            __m256i g,sgn,sc; cpu::Fmt32<TY>::decode(b,j,h,g,sgn,sc);
            alignas(32) uint8_t magnitude[32];alignas(32) int16_t scales[16];
            _mm256_store_si256(reinterpret_cast<__m256i*>(magnitude),g);
            _mm256_store_si256(reinterpret_cast<__m256i*>(scales),sc);
            for(int q=0;q<32;++q)if(magnitude[q]>127)throw std::runtime_error("signed grid representation overflow");
            for(int q=0;q<16;++q)if(scales[q]<0||scales[q]>127||scales[q]!=scales[q<8?0:8])throw std::runtime_error("unsupported scale layout");
            int H=2*j+h;
            _mm256_storeu_si256(reinterpret_cast<__m256i*>(out[i].weights+32*H),_mm256_sign_epi8(g,sgn));
            out[i].scales[2*H]=static_cast<int8_t>(scales[0]);out[i].scales[2*H+1]=static_cast<int8_t>(scales[8]);
        }
    }
    return out;
}
std::vector<Block> expand(const uint8_t* data,size_t blocks,int type) {
    switch(type) {
        case 18:return expand_t<18>(data,blocks);
        case 21:return expand_t<21>(data,blocks);
        case 22:return expand_t<22>(data,blocks);
        default:throw std::runtime_error("unsupported type");
    }
}
template<int NT> inline void dot(const Block* row,int nb,const block_q8_K* const* y,float* res) {
    __m256 accf[NT];for(int t=0;t<NT;++t)accf[t]=_mm256_setzero_ps();
    const int pf=cpu::prefetch_distance();
    for(int i=0;i<nb;++i) {
        const Block& b=row[i]; cpu::rows_ahead(reinterpret_cast<const uint8_t*>(&b),pf);
        __m256i acci[NT];for(int t=0;t<NT;++t)acci[t]=_mm256_setzero_si256();
        for(int H=0;H<8;++H) {
            const __m256i signed_g=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(b.weights+32*H));
            const __m256i g=_mm256_abs_epi8(signed_g);
            const __m256i sgn=_mm256_sign_epi8(_mm256_set1_epi8(1),signed_g);
            const __m256i sc=cpu::sc16(b.scales[2*H],b.scales[2*H+1]);
            for(int t=0;t<NT;++t) {
                const __m256i yv=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(y[t][i].qs+32*H));
                const __m256i ys=_mm256_sign_epi8(yv,sgn);
                acci[t]=cpu::plain::madd_add(acci[t],_mm256_maddubs_epi16(g,ys),sc);
            }
        }
        for(int t=0;t<NT;++t)accf[t]=_mm256_fmadd_ps(_mm256_set1_ps(b.d*y[t][i].d),_mm256_cvtepi32_ps(acci[t]),accf[t]);
    }
    for(int t=0;t<NT;++t)res[t]=cpu::hsum8(accf[t]);
}
template<int NT> void gu_t(const Block* data,int nb,const void* const* act,float* const* out,int rows,int r0=0,int r1=-1) {
    const block_q8_K* y[NT];for(int t=0;t<NT;++t)y[t]=reinterpret_cast<const block_q8_K*>(act[t]);
    float g[NT],u[NT];
    if(r1<0)r1=rows;
    for(int r=r0;r<r1;++r) {
        dot<NT>(data+size_t(r)*nb,nb,y,g);dot<NT>(data+size_t(rows+r)*nb,nb,y,u);
        for(int t=0;t<NT;++t)out[t][r]=(g[t]/(1.f+std::exp(-g[t])))*u[t];
    }
}
void gu(const Block* data,int nb,const void* const* act,int nt,float* const* out,int rows) {
    switch(nt) {
#define C015_NT(N) case N:gu_t<N>(data,nb,act,out,rows);break
        C015_NT(1);C015_NT(2);C015_NT(3);C015_NT(4);C015_NT(5);C015_NT(6);C015_NT(7);C015_NT(8);
#undef C015_NT
        default:throw std::runtime_error("unsupported token count");
    }
}
void gu_range(const Block* data,int nb,const void* const* act,int nt,float* const* out,int rows,int r0,int r1) {
    if(r0<0 || r1<r0 || r1>rows)throw std::runtime_error("invalid row range");
    switch(nt) {
#define C016_NT(N) case N:gu_t<N>(data,nb,act,out,rows,r0,r1);break
        C016_NT(1);C016_NT(2);C016_NT(3);C016_NT(4);C016_NT(5);C016_NT(6);C016_NT(7);C016_NT(8);
#undef C016_NT
        default:throw std::runtime_error("unsupported token count");
    }
}
}
