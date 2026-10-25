"""One model per process, JSON lines on stdin/stdout, diagnostics on stderr."""
from __future__ import annotations

import argparse
import base64
import json
import sys

from serve.model_runtimes import validate_embedding


def emit(value):
    print(json.dumps(value, allow_nan=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, help='local Safetensors model directory')
    parser.add_argument('--device', default='cuda')
    parser.add_argument('--max-tokens', type=int, default=32768,
                        help='maximum total input tokens per request; never truncates')
    args = parser.parse_args()
    try:
        import torch
        import torch.nn.functional as functional
        from transformers import AutoModel, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(args.model, padding_side='left', local_files_only=True)
        model = AutoModel.from_pretrained(args.model, dtype=torch.bfloat16,
                                         attn_implementation='sdpa', local_files_only=True)
        model = model.to(args.device).eval()
        emit({'status': 'ready'})
    except Exception as exc:
        print(f'embedding load failed: {exc}', file=sys.stderr, flush=True)
        emit({'error': 'embedding model failed to load; inspect the worker log', 'status': 500})
        return 1
    for line in sys.stdin:
        try:
            payload = json.loads(line)
            validate_embedding(payload)
            texts = payload['input'] if isinstance(payload['input'], list) else [payload['input']]
            if payload.get('instruction'):
                texts = [f"Instruct: {payload['instruction']}\nQuery: {text}" for text in texts]
            encoded = tokenizer(texts, padding=False, truncation=False)
            lengths = [len(ids) for ids in encoded['input_ids']]
            if max(lengths) > 32768 or sum(lengths) > args.max_tokens:
                raise ValueError(f'input exceeds the {args.max_tokens}-token request limit; split the batch')
            vectors = []
            # Sequential inputs bound activation memory even when one batch mixes short/long documents.
            with torch.inference_mode():
                for ids, mask in zip(encoded['input_ids'], encoded['attention_mask']):
                    input_ids = torch.tensor([ids], device=args.device)
                    attention_mask = torch.tensor([mask], device=args.device)
                    hidden = model(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
                    vector = hidden[:, -1, :payload.get('dimensions', 2560)].float()
                    vector = functional.normalize(vector, p=2, dim=1).cpu().numpy()[0]
                    if payload.get('encoding_format', 'float') == 'base64':
                        vectors.append(base64.b64encode(vector.astype('<f4').tobytes()).decode('ascii'))
                    else:
                        vectors.append(vector.tolist())
                    del hidden, input_ids, attention_mask
            emit({'object': 'list', 'model': payload['model'],
                  'data': [{'object': 'embedding', 'index': i, 'embedding': vector}
                           for i, vector in enumerate(vectors)],
                  'usage': {'prompt_tokens': sum(lengths), 'total_tokens': sum(lengths)}})
        except ValueError as exc:
            emit({'error': str(exc), 'status': 400})
        except Exception as exc:
            print(f'embedding request failed: {exc}', file=sys.stderr, flush=True)
            emit({'error': 'embedding inference failed; inspect the worker log', 'status': 500})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
