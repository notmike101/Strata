# Independent coding cache-profile preparation

The eight exact synthetic requests and responses are retained here. They use seeds201-208, the frozen recommended thinking sampler and512-token caps. None is the measured TTLCache prompt. This is a cache placement ranking, not weight training.

For the original preparation, the normal promoted config additionally set expert_profile_save to an absolute new T001-learned-profile.bin path and expert_profile_save_every to0.001 minutes. The preparation script sends eight tasks and an unrelated sentinel so the engine saves the eighth task's ranking before processing the sentinel. It then freezes a separate copy. Disable both save options for measurements and point --expert-profile at the frozen file. The benchmark asserts that its bytes do not change between requests.

frozen-profile.json contains the exact bytes as base64, byte count and SHA256. Decode it to reproduce the measured startup ranking; rerunning model generation is not guaranteed to recreate identical bytes. The original script, adapted only to take root/URL arguments, is prepare.py; it expects the campaign sampling.json content at <root>/local-setup/coding-best-practices/profile.json and the selected config at <root>/strata-iq3_s.json. Model tensors are unchanged.
