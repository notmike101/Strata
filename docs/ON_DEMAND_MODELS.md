# Models on demand

The optional Python gateway serves Strata chat, a Python embedding model, and an
image-generation process through one API address. It loads the requested runtime
after unloading the previous one. The existing Strata server, engine and installer
are unchanged; the gateway runs only when explicitly launched.

```text
python -m serve.model_gateway --config model-gateway.local.json
```

Use `examples/model-gateway.json` as a starting point. Its paths describe a Windows
installation in `C:/strata` and `C:/models`; change them for another checkout or OS.
The model names are configuration keys, and clients send those exact names in `model`.

## Installed runtimes

- **Chat:** the existing Strata engine and config. Run its API on loopback on a private
  port, with `--lazy`. Preserve the native engine arguments. The gateway owns this
  server and uses `/v1/load` and `/v1/unload` to control its model and vision encoder.
- **Embeddings:** `unsloth/Qwen3-Embedding-4B` in a separate Python environment,
  using PyTorch and Transformers. Safetensors are loaded locally, without custom
  remote Python code. The worker uses BF16, SDPA, last-token pooling and float32
  normalization. There is no llama.cpp dependency.
- **Images:** `stable-diffusion.cpp`'s CUDA `sd-cli` with the Qwen-Image-2.1 Q4_K_M
  denoiser, Qwen3-VL-8B UD-Q4_K_XL text encoder and BF16 VAE. The CLI exits after
  each image; its weights are released immediately, and the next image reloads them.

The Python gateway itself imports no GPU libraries. Install the embedding dependencies
in a separate environment. On the tested Windows NVIDIA setup:

```text
python -m venv .model-runtimes/embedding
.model-runtimes/embedding/Scripts/python.exe -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cu126
.model-runtimes/embedding/Scripts/python.exe -m pip install transformers==5.19.0 accelerate==1.15.0 safetensors==0.8.0
```

Download the full [embedding model](https://huggingface.co/unsloth/Qwen3-Embedding-4B)
including its tokenizer and config into the worker's `--model` directory. Download the
[image denoiser](https://huggingface.co/unsloth/Qwen-Image-2.1-GGUF),
[VAE](https://huggingface.co/unsloth/Qwen-Image-2.1-FP8/tree/main/vae), and
[text encoder](https://huggingface.co/unsloth/Qwen3-VL-8B-Instruct-GGUF) to the paths
in the image configuration. The selected model files total approximately 18.1 GB.

The installed CUDA image CLI is release `master-964-1d0a58a` from
[stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp/releases/tag/master-964-1d0a58a).
No native Strata backend files are changed or rebuilt by this feature.

On Windows the image runtime's `lib_dirs` can name the separate PyTorch environment's
`Lib/site-packages/torch/lib` directory, which contains CUDA 12 DLLs. These paths are
added only to the image child's environment. The local config explicitly selects
`CUDA0` so a missing GPU backend fails instead of silently running on the CPU.

## Access and model controls

All API and metadata requests except `/health` require the configured key when one
is set. Supply `Authorization: Bearer KEY` or `x-api-key: KEY`. The existing chat web
page and its scripts/styles remain public so you can enter the key in its Settings.
The chat web page remains a chat interface; embeddings and generated images are API
features in this first implementation.

Non-loopback binding, such as `"host": "0.0.0.0"`, requires an API key. Set it in an
ignored local config, or set `STRATA_GATEWAY_API_KEY` in the gateway's environment.
The gateway supplies the same key to the private Strata API through its environment.
The private config must not contain a different key. Do not bind the private API to
the network or point a client at it: only the gateway controls cross-model ownership.

| Method and path | Behavior |
| --- | --- |
| `GET /v1/models` | List all configured model names and types without loading any |
| `GET /v1/status` | Active runtime, busy/queued counts and each model's loaded state |
| `POST /v1/load {"model":"NAME"}` | Switch to the model; image CLI reports `ready` and loads during generation |
| `POST /v1/unload {}` | Unload the active model after earlier requests finish |
| `POST /v1/unload {"model":"NAME"}` | Unload only if that model is active |
| `GET /health` | Lightweight public health check |

The request queue is FIFO. It holds ownership through the full streamed response.
A switch waits for cleanup, including cancellation after a disconnected chat stream.
If cleanup fails, the gateway retains ownership and reports an error rather than
starting another model. `idle_unload_s` defaults to 600; zero disables idle unloading.
The timer begins when the last request finishes and does not unload while work is queued.

Existing OpenAI chat, Anthropic Messages and Responses APIs are forwarded to Strata.
An omitted chat model uses `default_model`. Embedding and image requests should specify
their model explicitly. Unknown models return 404; wrong model types and malformed
inputs return 400 before the gateway changes runtimes.

## Embedding requests

Send JSON to `/v1/embeddings`:

```json
{
  "model": "unsloth/Qwen3-Embedding-4B",
  "input": ["Paris is the capital of France.", "A recipe for chocolate cookies."],
  "dimensions": 2560,
  "encoding_format": "float"
}
```

`input` is a nonempty string or a list of 1 to 32 nonempty strings. Token-ID arrays
are not supported. `dimensions` is an integer from 32 through 2560. `encoding_format`
can be `float` or `base64`; base64 contains little-endian float32 values. The response
uses OpenAI's embedding list format and includes token usage.

The optional `instruction` field prefixes each input with `Instruct: ...\nQuery: ...`.
Use it on retrieval queries when appropriate; embed documents separately without a
query instruction. Inputs run sequentially to bound activation memory. The worker's
default maximum is 32768 total tokens per request, and no individual input may exceed
32768 tokens. Oversized inputs are rejected, never truncated.

## Image requests

Send JSON to `/v1/images/generations`:

```json
{
  "model": "unsloth/Qwen-Image-2.1-GGUF",
  "prompt": "A cheerful orange fox in a sunny meadow, storybook illustration.",
  "size": "1024x1024",
  "steps": 20,
  "cfg_scale": 6.0,
  "seed": 42,
  "response_format": "b64_json"
}
```

The response contains a PNG in `data[0].b64_json`. This adapter supports text-to-image,
one image per request, and base64 output. It does not implement editing or hosted URL
results. Width and height must be multiples of 64 from 256 through 2048, with at most
1048576 total pixels. Steps must be 1..100, CFG 0..20, and the seed -1..2147483647.
The default seed is -1, allowing the image engine to choose a random seed. Prompts are
passed as individual process arguments; the gateway never executes them in a shell.

## Local files and rollback

Generated configs, keys, environments and logs belong in ignored local files.
`model-gateway.local.json`, `model-gateway-api-key.txt` and `.model-runtimes/` are ignored.
Keep keys out of commits and command output. Model weights belong in your model folder.

Before replacing a working launcher, back it and the original config up. Wait for the
old server to become idle, unload its model, and stop that server before using its port.
The local installation retains the original launcher/config under
`.model-runtimes/backups/`. To roll back, stop/unload the gateway and run the saved
launcher. Preserve LAN authentication when restoring a config that previously lacked it.

Run CPU-only verification without downloads or a GPU:

```text
python -m unittest serve.test_runtime_manager serve.test_model_runtimes serve.test_model_gateway -v
```

The existing server tests are `python -m unittest serve.test_server -q`.
Live GPU results, pinned model revisions and installation package versions are stored
locally in `.model-runtimes/verification/`, `models-manifest.json` and
`embedding-requirements.lock.txt`. Check those records before making performance claims.
