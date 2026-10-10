# RTX 3090 / i9-10900KF: IQ3_S thinking-mode optimization ledger

Current goal checkpoint (E149): **90 tok/s is not qualified**. C048 fails the predeclared no-confirmation screen: short85.2 versus88.7 decode (-3.95%), E2E75.6242 versus78.2182 (-3.32%). Longer89.6 versus84.4 decode (+6.16%), E2E43.2796 versus41.9663 (+3.13%). All12 requests show seven cache barriers. Mixed workload response; not promoted and no reverse pair. Full launcher-tree cleanup is enforced and verified. Process-memory queries stay outside timed generation; GPU telemetry and independent16GiB physical/commit guards remain. The retained production stack is unchanged. Q007 still has two incomplete coding answers out of five; no full quality/matrix qualification is claimed. No benchmark model is resident at this checkpoint.

Active goal: **90 tok/s server_decode_tps** on the fixed short and approximately3K coding matrix; goal created without a token budget at the user's request. See [goal-90-contract.md](goal-90-contract.md). The target remains unproven. Fresh control B010 measured85.9 /84.8 tok/s but included short-run stalls of21.7 and17.5; prompt-read medians77.0 /495.3. No new candidate is promoted. Earlier90/85 follow-up results remain in [follow-up-summary.json](follow-up-summary.json). The B010 stalls remain unexplained; later B011/B012 cells and the Q007 failures are retained without discarding slow or incomplete runs.

Historical 80 tok/s milestone: **80 tok/s server-decode target demonstrated on both established coding cells.** Two fresh-process five-seed repeats, in opposite workload order, produced 20/20 measured runs above80. Combined medians: **87.35 short / 83.30 longer**; client end-to-end **75.29 / 41.67** tok/s. The fixed recommended thinking sampler is unchanged. At258901 input tokens, a separate successful recall check measured only **2.6 decode tok/s**. This is not an80tok/s end-to-end or full-context claim.

Measured on 2026-10-09 by notmike101. This report follows [the community report guide](../../../docs/COMMUNITY_BENCHMARKS.md) and is listed in [the community index](../COMMUNITY.md). [RESULTS.md](RESULTS.md) contains the guide's complete results table for every completed cell: actual/fresh/reused/generated tokens, repetitions, prompt/decode throughput, TTFT and client total latency, with ordinary medians and full ranges. The compact table below is an overview, not a replacement for the all-run evidence.

This report records the local setup, every completed throughput experiment, rejected configurations, profiler observations, validation coverage, and unresolved measurement problems. It is a fork campaign, not an upstream performance claim. The source baseline is `fb58e0dbc8399662c0e47c76578c6e878b14f6cf` and the installed release engine is 0.1.41. Git fetch and the GitHub release API on 2026-10-09 found no newer Strata source or release to install. The optional per-format CPU dispatch candidate [1fb2fc6](https://github.com/notmike101/Strata/commit/1fb2fc6b303423784b6c10a3cb88021d749383df) was merged into the sole working branch `perf/rtx3090-thinking-80` at [e3aef5f](https://github.com/notmike101/Strata/commit/e3aef5fe6f78c3f4ea8734e1a41f65d1e06250bb), as requested by the user. Its temporary branch and worktree were cleaned up. Build and validation details are in E013 of the ledger; the finalist is retained after repeated served throughput and the documented correctness checks.

## Hardware and invariant configuration

- Windows 11; Intel Core i9-10900KF, 10 physical / 20 logical cores; 128 GiB DDR4-3200.
- NVIDIA RTX 3090, 24,576 MiB VRAM; PCIe 3.0 x8 on this host; driver 610.88.
- Selected device GPU 0; 350 W reported power limit, also the device default. C: storage is a KIOXIA KXG60PNV2T04 NVMe SSD, 2,048,408,248,320 bytes. These are live checkpoint observations, not historical per-run telemetry. CPU package power limit was not recorded. See `hardware-supplement.json`.
- Release CUDA 13.0 engine; CUDA Toolkit 13.4.92 and Nsight Systems 2026.5.1.161 are now available side by side; historical builds/captures used 13.3.73 and 2026.1.3.
- Target: `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF`, **IQ3_S**, two GGUF shards. The PLE/ngram shard is always supplied.
- Compatible Flash-Next **F16** vision projector remains loaded, with 1,024 image tokens. The baseline uses GPU vision; R007 separately tests CPU execution with identical F16 weights and records the latency tradeoff. The initially requested 27B projector was incompatible (5120 vs 2560 embedding width); the compatible Flash-Next projector was selected with user approval.
- Maximum context 262,144; INT8 KV; 32,768 cells resident in VRAM, remaining KV streamed from RAM. Maximum configured context is not equivalent to maximum occupied context.
- Single request at a time, OpenAI-compatible API, LAN binding `0.0.0.0:8080`. The user explicitly selected keyless access on their private network. Public evidence omits host addresses and credentials.
- Model weights, quantization, KV precision, context, vision capability and target sampling must not be reduced to obtain a speed result.

Current retained runtime tuning before this campaign: `--pcie-frac 0.20 --spec-min-p 0.70`, `--spec 4`, default nine worker threads plus the coordinating thread, automatic expert cache and prompt chunking. Prompt lookup can extend verification windows to six tokens even though MTP is capped at four. A startup in this campaign filled 7,882 expert slots, about 14.95 GiB. The CPU arena contains approximately 46.84 GiB of experts. Windows refused large pages (error 1314); ordinary 4 KiB pages were used. This is observed behavior, not a recommendation to alter OS privileges.

Exact model files are `Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf` and `Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf`; setup-verified SHA256 values are in each arm's `identity.json`. The download revision was not recorded. `preparation-hashes.json` identifies the expert ranking profile, native pack layout/index/conversions, MTP layout and draft vocabulary. Large generated pack tensors are not attached. Low-RAM mode and experimental speed projection are disabled. Earlier calibration produced the retained PCIe share and draft threshold; its full sweep is `historical-calibration.json`. The current campaign does not recalibrate between arms.

Per-arm `identity.json` contains every engine argument, environment override, sampling default, vision device and loaded backend hash. The launch pattern is `python -m serve.server --engine strata --config <STRATA_ROOT>/strata-iq3_s.json --host 0.0.0.0 --port 8080`; production config binds `0.0.0.0:8080`, with one request and the settings above. Exact local launcher paths are omitted from public evidence. Source-build options and compiler changes are recorded in the chronological ledger separately from release-binary trials.

## Frozen thinking and sampling contract

The finalist uses the locally built CUDA 13.3/sm86 engine with the opt-in per-format CPU dispatch patch. Its SHA256 is `6048736d7674d8f3c66ce50060f11ca6623df33d3e885030941a6ef9e62f427c`. The compatible F16 vision encoder stays loaded on the CPU, freeing VRAM for 8409 expert slots (about 15.95 GiB). CPU image encoding has an explicit latency tradeoff: the earlier paired OCR requests took 3.752 s CPU versus 2.538 s GPU, with slightly different generated token counts; these are total request times, not isolated encoder timings.

Finalist environment, in addition to the invariant arguments above:

```text
STRATA_IQ256_GATHER=1
STRATA_IQ_MT_MIN=1
STRATA_IQ256_GATHER_IQ2_S=0
STRATA_ADAPT_LAG=2
```

IQ3 formats use gathered AVX2 loads while IQ2_S retains the faster scalar-load path on this CPU. Adaptive expert copies are admitted one generation window later, retaining synchronization. QFUSE, the 10-task override and diagnostic timing flags are absent. No tensor precision, model, sampler, reasoning, KV precision or context limit is reduced.

`sampling.json` is the exact profile used by the thinking campaigns:

```json
{
  "temperature": 1.0,
  "top_p": 0.95,
  "top_k": 20,
  "min_p": 0.0,
  "presence_penalty": 0.0,
  "repetition_penalty": 1.0,
  "frequency_penalty": 0.0,
  "reasoning_effort": "high",
  "reasoning_budget_tokens": 0,
  "chat_template_kwargs": {"enable_thinking": true, "preserve_thinking": true}
}
```

Strata maps `high` to the model's `xhigh`. Zero reasoning budget means no forced reasoning cutoff. The six model-card sampling recommendations are unchanged throughout every thinking benchmark and optimization. Frequency penalty is explicitly zero. The native context requires no YaRN. Model-card output budgets intended for a 1M context are not imposed on a 262,144-token allocation.

Production defaults are installed at both configuration and shared-settings layers. Explicit per-request reasoning remains available as `xhigh`, `medium`, `low`, or `off`; all four were verified through the LAN API. Those capability checks are **not** speed trials and do not change this campaign's fixed high-effort workload. Off disables thinking without changing numeric sampling defaults. No global output cap was added; individual benchmark caps are explicit and excluded from the production launcher.

## Measurement protocol

The 80 tok/s target is **server decode TPS**, ordinary median of all qualifying seeds, for each established short and approximately 3K-token coding cell. End-to-end and streamed total TPS are reported separately and are not expected to equal decode TPS.

- Route: `POST /v1/chat/completions`; production streaming path; concurrency one.
- Prompt: a complete Python TTLCache implementation, fake-clock unit tests, thread-safety and complexity explanation. The longer version prepends 64 synthetic design requirements. Exact payloads are in `requests/`.
- Short input: 165-168 tokens with high thinking; longer input: 3033-3035 tokens. Historical no-thinking prompts had smaller template overhead and are not interchangeable controls.
- Output: 512 generated tokens including reasoning. This probe can end inside reasoning; it does not substitute for completed coding answers. Separate correctness tests allow 8192 tokens and require natural stop.
- Cache: unique opening nonce per request; inspect reported `cache_n`, do not infer cache state from latency. Published speed cells report zero cached tokens. The threshold sweep disables checkpoints equally in all arms to prevent cross-arm reuse.
- One excluded warmup per workload. Quick candidates: three measured seeds. Finalists: five seeds 101-105, a fresh-process repeat, and behavioral validation. Historical final thinking control contains ten qualifying runs per workload across two separate starts.
- Client runs on this host through its LAN address. No remote-device network or UI rendering measurement is claimed.
- Before requests: resolve listener PID and command, engine path/hash, loaded CUDA library hashes, model alias and file identity, vision identity, context, effective sampler, and unchanged config/profile bytes. Model shard hashes were taken during setup; benchmark manifests explicitly identify reused prior hashes rather than claiming repeated multi-gigabyte rehashing.
- `server_decode_tps`: server generation count / generation interval. `request_e2e_tps`: completion count / request-start to response-complete. `stream_total_tps`: completion count / request-start to last content token. TTFT is request-start to first reasoning/content chunk.
- All measured runs, slow seeds, warmups, failures and losing arms are retained. No favorable seed subset, upper median, changed model or disabled-thinking result can complete the target.

The expert cache is prefilled from the same ranking profile at each process start, then retained within an arm. **Correction:** the startup cache-policy banner says PROFILE/no eviction, but the separate adaptive tier remains enabled by source defaults: `--adapt-every 4 --adapt-swaps 96 --adapt-decay 0.7 --adapt-async 0`. It can swap expert residency during requests. Calling the complete engine cache static based on that banner was incorrect. These defaults are unchanged across arms; R016/F001/F002 change only admission lag from1 to2 windows. Prefix reuse is independently measured. A fresh process precedes each arm; the excluded warmup also builds CUDA graphs. Client total latency includes HTTP transport, any queueing and prompt processing; startup/model loading is excluded. Text speed requests do not invoke image encoding, although vision remains loaded. The vision comparison includes image encoding in total request time. TTFT observes the first nonempty reasoning or answer delta and ignores keep-alives/empty deltas; it is not answer-only latency.

`memory-snapshots.json` preserves before/after GPU snapshots, not inference peaks. Readiness headroom and Windows large-page failures are recorded in the ledger. Peak RAM/VRAM and OS paging were not continuously measured; low-headroom warnings are evidence of risk, not proof of paging. Codex and normal desktop services remained present. Earlier browser/profiler confounds are identified by arm; current benchmark requests do not overlap compilation or another model.

## Results and current uncertainty

| Campaign / arm | Short decode | Longer decode | Short E2E | Longer E2E | Decision |
|---|---:|---:|---:|---:|---|
| Historical Q4 setup, greedy / thinking off | 37.5 | 32.7 | 33.24 | 19.39 | Different model; historical only |
| Initial IQ3_S setup, greedy / thinking off | 83.7 | 82.1 | 74.58 | 41.05 | Different context/sampling phase |
| 262K hardware control, sampled / thinking off | 78.0 | 75.9 | 69.26 | 39.26 | Superseded contract |
| 262K hardware tuned, sampled / thinking off | 81.1 | 80.6 | 72.2 | 40.5 | Retained tuning, ineligible as thinking result |
| Fixed-thinking previous control, ten runs per cell | 76.8 | 72.0 | 67.65 | 38.17 | Prior reference |
| Fixed-thinking threshold .50 diagnostic | 73.9 | 69.9 | See raw data | See raw data | Rejected vs .70 control |
| Fixed-thinking threshold .70 diagnostic | 75.2 | 70.4 | See raw data | See raw data | Retained |
| Fixed-thinking threshold .90 diagnostic | 74.1 | 69.3 | See raw data | See raw data | Rejected |
| Fixed-thinking coupled draft | 76.0 | 72.7 | See raw data | See raw data | No material gain; removed |
| target-80 B001 fresh baseline, five runs | 75.1 | 71.3 | 66.59 | 37.96 | Initial same-day control |
| target-80 R001 host-core last, three runs | 61.1 | 59.5 | 54.63 | 32.55 | Not promoted; environment discrepancy |
| target-80 B002 restored control, three runs | 62.8 | 60.4 | 56.32 | 32.82 | Control failed to recover; investigate |
| target-80 B003 quiet control, three runs | 63.1 | 58.0 | 56.39 | 32.17 | Profiler-agent cleanup did not restore baseline |
| target-80 B004 recovery control, three runs | 73.7 | 71.4 | 65.38 | 37.98 | Prior performance range recovered; cause of transient slowdown unresolved |
| target-80 R006 reserve1200, three runs | 71.3 | 67.4 | 63.35 | 36.61 | Rejected: smaller expert cache costs throughput |
| target-80 R007 CPU vision, three runs | 80.2 | 72.9 | 70.36 | 38.89 | Candidate; F16 vision stays loaded on CPU, OCR passed |
| target-80 R008 CPU vision + QFUSE, three runs | 82.4 | 75.0 | 73.49 | 39.55 | Provisional gain; wide short spread, longer below80 |
| target-80 R013 mixed-format CPU gather, three runs | 79.3 | 76.9 | 70.06 | 39.95 | Longer improves vs normal control; target unmet |
| target-80 R014 mixed gather + QFUSE, three runs | 80.8 | 71.9 | 72.01 | 38.67 | Rejected combination |
| target-80 R015 mixed gather + 10 tasks, three runs | 78.1 | 72.0 | See full table | See full table | Rejected task granularity |
| target-80 R016 mixed gather + adaptive lag2, three runs | 86.3 | 81.1 | 74.97 | 41.14 | Candidate; slow warmups and one slow measured seed retained |
| target-80 F001 same candidate, five runs | 88.0 | 82.2 | 76.43 | 41.41 | All ten measured runs >80 |
| target-80 F002 fresh process, reversed order, five runs | 84.4 | 85.4 | 73.52 | 42.13 | All ten measured runs >80; checks passed |
| F001 + F002, ten runs per cell | 87.35 | 83.30 | 75.29 | 41.67 | Retained production configuration |

Rates are tok/s; ordinary medians. `experiment-index.json` contains every completed workload's raw seed rates, medians, spread, E2E, streaming total and TTFT. `all-runs.csv` includes warmups. The raw JSON files preserve full timing fields and draft counters.

**Unresolved:** after Nsight profiling, the restored unmodified configuration also measures substantially below B001. Therefore the entire drop in R001 cannot be attributed to moving the host thread. R001 is not a valid demonstration of a 19% placement regression. It is slightly slower than the subsequent three-run control, but promotion is suspended until the environment discrepancy is reproduced and explained. The original control is retained for comparisons; subsequent candidate settings and promotion status are recorded in the chronological ledger. B003 reproduced the slowdown after exact cleanup of a leftover profiler agent; the cause remains unresolved. A later uninstrumented B004 control recovered to73.7/71.4 without a tuning change, so the low-throughput controls must not be used to inflate subsequent improvement claims.

## Evidence layout and reproduction

- `ledger.md`: chronological hypotheses, interventions, correctness, rejections and follow-up work.
- `raw/<campaign>/<arm>/`: complete per-run timing records, original summaries and allowlisted identity metadata.
- `historical-calibration.json`: every built-in sweep arm and paired confirmation.
- `fixed-thinking-previous-summary.json`: previous all-run thinking aggregation.
- `P001-*.csv`: Nsight kernel and CUDA API aggregates. Full `.nsys-rep` (about 55 MiB), SQLite, raw SSE and outputs remain local; no profiler throughput is used as a headline.
- `artifact-manifest.json`: SHA256 and byte count for each public evidence file.
- `replay.py`: lightweight replay of an exact example payload. It does not perform the full identity/cold-start protocol; use it for reproduction, not as automatic proof of a speed claim.
- `measure.py`: full Windows campaign measurement script, with only root/config/server address changed to command-line arguments and the profile filename changed to `sampling.json`. Process discovery was corrected before B005's first request to accept the configured executable filename and Windows PowerShell 5.1 singleton arrays. Earlier successful release-binary measurements used the same timing, prompt and seed logic.
- The current script obtains workspace Git metadata through the user's GitHub App identity helper (`--git-helper`, default `~/github-agent/identity.mjs`). It requires that local helper and Node.js; this affects provenance collection only, not requests or timing. Repository contributions use `agent-notmike101[bot]`. A separately coordinated identity correction changed seven earlier personal author/committer pairs while preserving all source trees, messages, timestamps and merge topology. Historical artifact IDs remain unchanged; `identity-rewrite-commit-map.txt` maps them to current history.
- `engine-timings.txt`: verbatim prompt/decode timing lines from the cumulative engine log, with original line numbers. Includes warmups and capability tests; associate with the per-run token counts, TPS and draft counters instead of pooling the log into a single result.
- `raw/*/*/samples/`: exact synthetic request payloads and generated output text for completed fixed-thinking arms. Raw SSE remains local; timing/draft counters and text are published.
- `failures.json`: pre-request and incomplete measurement attempts, excluded from successful throughput summaries. `TRIMMED.md` identifies larger/private artifacts retained locally and measurements not available.

```powershell
python replay.py --base-url http://YOUR_HOST:8080 --request requests/short.json
python replay.py --base-url http://YOUR_HOST:8080 --request requests/longer.json
python measure.py --root C:/Strata --config C:/Strata/strata-iq3_s.json --base-url http://YOUR_HOST:8080 --out ./new-run --runs 5
# Restart the same configuration, then repeat into another directory with --reverse-order.
```

A repeated example may hit cache; inspect `timings.cache_n`. For paired new-prompt tests, vary the opening nonce identically across arms, preserve the seed list and every other payload field, and retain all runs. Starting a second engine concurrently invalidates memory and timing comparisons.

## Validation coverage and limitations

Five completed sampled coding outputs compiled and passed objective interval-merging tests in the previous thinking campaign. Exact-output instructions with/without unused tools, natural stop, multi-turn latest instruction, prompt-cache reuse, default high thinking, and F16 image OCR passed. An initial historical test failure involved ambiguous adjacent intervals; the prompt was clarified identically for control and candidate and the failed output was retained.

A historical 52,542-token exact retrieval check passed; that check predates the fixed-thinking campaign. Fixed-thinking Q003 passed at258901 input tokens with three correct retrieval codes,162 output tokens and natural stop; prompt1067.0tok/s, decode2.6tok/s and306.267s total. Neither successful allocation nor one retrieval sample proves universal long-context quality or 80 tok/s at full occupancy. The CPU dispatch candidate passed dispatch and numerical parity tests. Q001 repeated the completed coding, exact-output, history and prefix-reuse checks on the finalist and passed. Q002 and final-process Q005 verified live sampler defaults, keyless LAN service, F16 vision OCR and all four remote reasoning levels. Q004 passed five structured-tool round trips. Qualification requests, responses and scripts are in `qualification/`; broader quality equivalence is not established by these smoke tests.

The additional restart check in the early hardware campaign was blocked by automatic approval review at that time; the report retains that limitation. Later authorized campaigns did perform fresh starts. No upstream issue/PR has been opened and no upstream branch is modified by this ledger.

## Sources

- [Model sampling and context guidance](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF#best-practices), checked 2026-10-09.
- [Strata releases](https://github.com/Niko1221/Strata/releases) and fetched upstream main, checked 2026-10-09.
- [Strata implementation/details](https://github.com/Niko1221/Strata/blob/fb58e0dbc8399662c0e47c76578c6e878b14f6cf/docs/DETAILS.md): calibration, CPU placement, graph flags, numerical caveats.
- [NVIDIA Nsight CUDA graph tracing](https://docs.nvidia.com/nsight-systems/UserGuide/index.html#cuda-graph-trace): node-level traces have substantial overhead.
- [Different-host RTX 3090 report](https://github.com/Niko1221/Strata/issues/165): research lead only; different CPU/PCIe/model, not a matched result.


Latest E101: HC fast cumulative15-run medians and rejected PCIe interaction are in [the detailed report](diagnostics/hyper-connection/README.md). No production promotion; goal90 remains unqualified.

Latest E102: [C035 exact HC source screen](diagnostics/hyper-connection/C035/README.md) rejected source-Q8 reconstruction because no such blocks exist in the selected model. No production changes.

Latest E103: [C036 exact BF16 storage screen](diagnostics/hyper-connection/C036/README.md) saved18.54% storage but failed GPU timing; rejected without production changes.

Latest E104: [C037 expert-fetch screen](diagnostics/expert-fetch/C037/README.md) passed byte parity but produced no useful timing gain; rejected. Goal API is active.

Latest E105: [C038 shared quantization](diagnostics/shared-quant/C038/README.md) rejected on three reproducible byte mismatches. No engine or launcher change. Goal remains active.

E106-E108: [C039 dual-output quantization](diagnostics/shared-quant/C039/README.md) passed exact offline parity but lost the served comparison. Production edits removed; no launcher promotion.
