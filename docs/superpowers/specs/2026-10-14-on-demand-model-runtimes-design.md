# On-demand model runtimes

The user wants the existing Strata chat model, unsloth/Qwen3-Embedding-4B, and
unsloth/Qwen-Image-2.1-GGUF available on request without loading them together.
Switching and cold-start delays are acceptable. Use Python for embeddings and
stable-diffusion.cpp for images; do not use llama.cpp. Keep LAN access with an API key.
The user approved this direction and explicitly requested starting implementation.

## Interface and ownership

An opt-in `python -m serve.model_gateway --config PATH` starts a lightweight gateway.
The existing server and native engine are unchanged. The gateway advertises all three
model names at `/v1/models`, proxies existing chat APIs, and implements
`/v1/embeddings`, `/v1/images/generations`, `/v1/load`, `/v1/unload`, and `/v1/status`.
Requests must name a configured model; omitted chat model uses the configured chat
default. Unknown models and invalid inputs return 400/404 before disturbing a model.

A FIFO queue owns the runtime for the entire request, including streaming. Switching
unloads the previous runtime and waits for completion before loading another. A failed
unload keeps ownership and blocks a switch; it must not silently start another model.
After 600 seconds without active or queued requests the runtime unloads. Idle timeout
and process timeouts are configurable. All heavyweight workers start on demand.

The managed Strata child listens on loopback on a private port and starts with `--lazy`.
Switching uses its existing authenticated `/v1/unload` and `/v1/load` controls. A worker
process owns the embedding model; stopping and waiting for that process releases its
CPU/GPU weights. Image generation uses sd-cli in a subprocess that exits after each
image, so images reload even on successive requests. The gateway holds the FIFO until
sd-cli exits. No process remains holding image weights after a response.

## Embeddings and images

The embedding worker uses the requested Unsloth BF16 Safetensors model with
Transformers, SDPA, last-token pooling and float32 L2 normalization. It returns the
OpenAI embedding format, supports string or string-list input, float/base64 encoding,
and dimensions from 32 through 2560. Requests exceeding a configured token limit are
rejected, never silently truncated. Tokenization can happen during worker loading.
Model downloads and dependencies are installed separately from Strata's environment.

The image adapter uses the Q4_K_M denoiser, Qwen3-VL-8B UD-Q4_K_XL text encoder,
and BF16 VAE. Initial support is text-to-image, one PNG per request, base64 output.
Image editing and URL-hosted results are outside this implementation. Default output
is 1024x1024, 20 Euler steps, CFG 6.0. Inputs are bounded and passed as argument arrays,
never shell commands. Temporary output and logs are removed after the response.

## Access, installation and rollback

The gateway rejects non-loopback binding without a key. LAN setup generates a new key
in an ignored local configuration and requires Bearer or x-api-key authentication.
Keys, generated configs, runtime environments and weights are never committed or logged.
No model name or HTTP input can select arbitrary commands, paths or network backends.

Back up the existing config and launcher before cutover. Keep the original engine
arguments byte-for-byte. Only the gateway's private copy changes host, port, lazy load
and authentication. Wait until the old server has no running or queued requests before
unloading/stopping it. Retain a rollback launcher and backup config.

## Validation

Use fake workers without GPUs to prove switching order, FIFO ownership during streams,
idle unloading, failed cleanup, worker startup failures, model validation, authorization
and OpenAI response formats. Run existing server tests to establish the default path is
unchanged. Then install and smoke-test actual chat, embeddings and image generation,
including embedding similarity and one generated PNG. Record NVIDIA VRAM and process
memory before/after switches. Do not claim GPU validation until those checks succeed.
