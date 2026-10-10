## E166 / C053 request-conditional cache-accounting composition

Distinct combination hypothesis: C049 enabled accepted-row accounting even on
short requests where its token barrier was inactive. Its paired short89.1 versus
89.4 control did not qualify; C052's HC-only control90.5/84.5 shows useful short
performance without accepted-row accounting, but is NOT a same-day causal proof
against C049. Test that distinction on one binary, not pooled historical arms.

Add default-off STRATA_ACCEPTED_USAGE_BARRIER_ONLY=1. Requires acceptedusage1 and
configured positive barrier interval; malformed values reject before loading.
Effective accepted-row accounting is active only when this request has a positive
barrier interval. The existing minfresh1025 threshold is retained, not tuned to
seeds. Thus the combined experimental policy applies after longer fresh prompts;
short or small cached suffixes retain ordinary all-row accounting and window
adaptation. Minimum0 remains the old all-request mode. No sampling, routing,
weights, quantization or context change. Cache placement can affect CPU/GPU
rounding; no byte-identical whole-model output or quality claim follows.

Test first: enabled/disabled and gated/ungated predicates, inactive/positive
request intervals, alternating request policy with independent accepted/all-row
accounting oracles; malformed/dependency CLI configurations, C051 split rejection.
CUDA build and existing accepted-usage/token-barrier tests. HIP/SYCL unavailable.

Then finite same-binary ABBA: R106 control barrier-only0, R107 candidate1. Both
HC1,acceptedusage1,conditional64/minfresh1025,auto shareMAX1024,DMA0/deviceplan0,
lag2,9workers30tasks,MTP4/.70,PCIe.20. Unsplit only. Exact IQ3_S262144 INT8KV/
32768resident CPUF16vision. Numeric thinking1/.95/20/0/0/1,frequency0 unchanged.
Same original short/~3K requests,512tokens,cachemiss,stream/concurrency1,onewarmup
and five measured seeds101..105 each. If any decode/E2E median falls>3% or prompt
falls>2%, close without confirmation. Else exactly one reversed R108B/R109A pair,
ordinary all10medians per cell, no further threshold or interval sweep. Require
runtime proof of short ordinary accounting and long accepted accounting/barriers.
If retained, reverse-workload history, boundary/cache-hit tests and full frozen
random coding/quality/cold-warm/vision/tools/reasoning/cancel/maxcontext gates
remain. No promotion from screening metrics.16GiB guards and exact cleanup apply.
