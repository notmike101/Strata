# C035: source-Q8 reconstruction hypothesis rejected

The exact GSQ-RCO IQ3_S target has no Q8_0 hyper-connection source tensors.
All387 target HC tensors were enumerated across both actual GGUF shards and
matched to the live configuration's pack index:290BF16 and97F32 tensors.
Every one of640,624,640 coefficients was compared across1,283,235,840 packed
bytes, with zero mismatching bytes. Per-tensor source/packed/reconstructed
SHA256, shapes, types, byte sizes and counts are preserved in C035-result.json.

The draft model was separately checked:11HC tensors,19,773,440 coefficients,
zero Q8 source tensors and zero mismatching bytes. BF16 values are unchanged;
F32 normalization follows the existing packer's FP32 source+1 transform.
C035-draft-result.json records the exact method and hashes for every tensor.

This disproves the prerequisite of E101's proposed source-Q8 storage strategy.
The source comment about Q8 projections applies to other model variants; it
does not describe this resolved GSQ-RCO artifact. No new quantization, model
substitution or output-changing STRATA_HC_Q8 path was used. The finite plan
closed at its eligibility gate: no CUDA microbenchmark, source integration,
server launch or TPS claim. No repeat is warranted for the same artifacts.

The target comparison took12.392s. Minimum physical/commit headroom during it
was120,180,817,920/123,979,243,520 bytes, above both16GiB floors. Only tensor
metadata and HC coefficients were read; no full model allocation. The initial
WMI enumeration included stale Python process records, but live-process cleanup
verification found no live Strata launcher, server, engine or vision process.
Initial GPU usage523MiB. Production config hash and all quality requirements
remain unchanged. The90 TPS objective is still unqualified, not completed.

Next: reframe around the actual BF16 source representation or measured host/
device scheduling costs. A lossless format would require its own demonstrated
compression and exact reconstruction, not assumed source Q8 blocks. Do not
repeat Q6, device-planning or lower-PCIe combinations already closed in ledger.
