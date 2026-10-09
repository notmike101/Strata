# RTX 3090 / i9-10900KF: IQ3_S thinking-mode optimization ledger

Status: **active investigation; 80 tok/s has not been demonstrated under the current contract.**

This report records the local setup, every completed throughput experiment, rejected configurations, profiler observations, validation coverage, and unresolved measurement problems. It is a personal fork campaign, not an upstream performance claim. The source baseline is `fb58e0dbc8399662c0e47c76578c6e878b14f6cf` and the installed release engine is 0.1.41. Git fetch and the GitHub release API on 2026-10-09 found no newer Strata source or release to install. No engine source changes have been made at this checkpoint.

## Hardware and invariant configuration

- Windows 11; Intel Core i9-10900KF, 10 physical / 20 logical cores; 128 GiB DDR4-3200.
- NVIDIA RTX 3090, 24,576 MiB VRAM; PCIe 3.0 x8 on this host; driver 610.88.
- Release CUDA 13.0 engine; CUDA Toolkit 13.3.73 and Nsight Systems 2026.1.3 available for development.
- Target: `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF`, **IQ3_S**, two GGUF shards. The PLE/ngram shard is always supplied.
- Compatible Flash-Next **F16** vision projector remains loaded on the GPU, with 1,024 image tokens. The initially requested 27B projector was incompatible (5120 vs 2560 embedding width); the compatible Flash-Next projector was selected with user approval.
- Maximum context 262,144; INT8 KV; 32,768 cells resident in VRAM, remaining KV streamed from RAM. Maximum configured context is not equivalent to maximum occupied context.
- Single request at a time, OpenAI-compatible API, LAN binding `0.0.0.0:8080`. The user explicitly selected keyless access on their private network. Public evidence omits host addresses and credentials.
- Model weights, quantization, KV precision, context, vision capability and target sampling must not be reduced to obtain a speed result.

Current retained runtime tuning before this campaign: `--pcie-frac 0.20 --spec-min-p 0.70`, `--spec 4`, default nine worker threads plus the coordinating thread, automatic expert cache and prompt chunking. Prompt lookup can extend verification windows to six tokens even though MTP is capped at four. A startup in this campaign filled 7,882 expert slots, about 14.95 GiB. The CPU arena contains approximately 46.84 GiB of experts. Windows refused large pages (error 1314); ordinary 4 KiB pages were used. This is observed behavior, not a recommendation to alter OS privileges.

## Frozen thinking and sampling contract

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

Rates are tok/s; ordinary medians. `experiment-index.json` contains every completed workload's raw seed rates, medians, spread, E2E, streaming total and TTFT. `all-runs.csv` includes warmups. The raw JSON files preserve full timing fields and draft counters.

**Unresolved:** after Nsight profiling, the restored unmodified configuration also measures substantially below B001. Therefore the entire drop in R001 cannot be attributed to moving the host thread. R001 is not a valid demonstration of a 19% placement regression. It is slightly slower than the subsequent three-run control, but promotion is suspended until the environment discrepancy is reproduced and explained. The current serving config has been restored to the original control. B003 reproduced the slowdown after exact cleanup of a leftover profiler agent; the cause remains unresolved. A later uninstrumented B004 control recovered to73.7/71.4 without a tuning change, so the low-throughput controls must not be used to inflate subsequent improvement claims.

## Evidence layout and reproduction

- `ledger.md`: chronological hypotheses, interventions, correctness, rejections and follow-up work.
- `raw/<campaign>/<arm>/`: complete per-run timing records, original summaries and allowlisted identity metadata.
- `historical-calibration.json`: every built-in sweep arm and paired confirmation.
- `fixed-thinking-previous-summary.json`: previous all-run thinking aggregation.
- `P001-*.csv`: Nsight kernel and CUDA API aggregates. Full `.nsys-rep` (about 55 MiB), SQLite, raw SSE and outputs remain local; no profiler throughput is used as a headline.
- `artifact-manifest.json`: SHA256 and byte count for each public evidence file.
- `replay.py`: lightweight replay of an exact example payload. It does not perform the full identity/cold-start protocol; use it for reproduction, not as automatic proof of a speed claim.

```powershell
python replay.py --base-url http://YOUR_HOST:8080 --request requests/short.json
python replay.py --base-url http://YOUR_HOST:8080 --request requests/longer.json
```

A repeated example may hit cache; inspect `timings.cache_n`. For paired new-prompt tests, vary the opening nonce identically across arms, preserve the seed list and every other payload field, and retain all runs. Starting a second engine concurrently invalidates memory and timing comparisons.

## Validation coverage and limitations

Five completed sampled coding outputs compiled and passed objective interval-merging tests in the previous thinking campaign. Exact-output instructions with/without unused tools, natural stop, multi-turn latest instruction, prompt-cache reuse, default high thinking, and F16 image OCR passed. An initial historical test failure involved ambiguous adjacent intervals; the prompt was clarified identically for control and candidate and the failed output was retained.

A historical 52,542-token exact retrieval check passed; that check predates the fixed-thinking campaign. Full 262,144 occupied context has not yet been stress-tested. Neither successful allocation nor one retrieval sample proves universal long-context quality or 80 tok/s at full occupancy. No source-code candidate has yet passed a new full regression matrix.

The additional restart check in the early hardware campaign was blocked by automatic approval review at that time; the report retains that limitation. Later authorized campaigns did perform fresh starts. No upstream issue/PR has been opened and no upstream branch is modified by this ledger.

## Sources

- [Model sampling and context guidance](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF#best-practices), checked 2026-10-09.
- [Strata releases](https://github.com/Niko1221/Strata/releases) and fetched upstream main, checked 2026-10-09.
- [Strata implementation/details](https://github.com/Niko1221/Strata/blob/fb58e0dbc8399662c0e47c76578c6e878b14f6cf/docs/DETAILS.md): calibration, CPU placement, graph flags, numerical caveats.
- [NVIDIA Nsight CUDA graph tracing](https://docs.nvidia.com/nsight-systems/UserGuide/index.html#cuda-graph-trace): node-level traces have substantial overhead.
- [Different-host RTX 3090 report](https://github.com/Niko1221/Strata/issues/165): research lead only; different CPU/PCIe/model, not a matched result.
