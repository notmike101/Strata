from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'run-c062.py').read_text().replace('C062','C062-ctest')
s=s.replace("[str(p/'c062-screen.exe')]","[str(p.parents[1]/'.venv/Scripts/ctest.exe'),'--test-dir',str(p/'build-cuda86-main'),'--output-on-failure','-R','^(shared_scale_fusion_test|qfuse_gdn_test|native_multi_parity|shared_expert_parity|verify_parity|gr_parity|gdn_parity)$']")
# Identify the actual test executable, not the earlier standalone screen.
s=s.replace("p/'c062-screen.exe'","p/'build-cuda86-main/shared_scale_fusion_test.exe'").replace("p/'c062-screen.cu'","p.parents[1]/'tests/shared_scale_fusion.cu'")
(p/'run-c062-ctest.py').write_text(s)
(p/'C062-ctest-manifest.json').write_bytes((p/'C062-manifest.json').read_bytes())
