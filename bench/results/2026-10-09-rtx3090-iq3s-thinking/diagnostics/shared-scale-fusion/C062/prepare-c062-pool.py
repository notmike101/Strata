from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'pool-c056-stream-cache.py').read_text()
s=s.replace("['R128-stream-cache-control','R129-stream-cache-prefix','R130-stream-cache-prefix-reverse','R131-stream-cache-control-reverse']","['R132-shared-scale-control','R133-shared-scale-candidate','R134-shared-scale-candidate-reverse','R135-shared-scale-control-reverse']").replace('STRATA_PREFILL_STAGE_PREFIX','STRATA_SHARED_SCALE_FUSE').replace('c056-stream-cache-pooled','c062-stream-cache-pooled')
s=s.replace("    cell['decode_target_pass']=", "    cell['individual_candidate_process_target_pass']=all(statistics.median([r['server_decode_tps'] for r in armrows[i]]) >= (90 if w.startswith('short/') else 85) for i in (1,2))\n    cell['stream_no_degradation']=m['stream_total_tps']['candidate']>=m['stream_total_tps']['control']\n    cell['decode_target_pass']=")
(p/'pool-c062-stream-cache.py').write_text(s)
