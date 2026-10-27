# Current-source 27B integration validation

These **short integration checks** validate the supported setting on an untouched
upstream baseline and the feature. They do not replace the full 2026-10-25 tuning
study or establish a new speed ranking. Baseline and feature were separate,
sequential source blocks, so thermal/time effects were not balanced across sources.
Each source block balanced its own AR/MTP profile and contention-case order.

- Baseline `891758cf4034b3e4230c11821dc2c1674e57061c`: four fresh servers, stock `0.5`, AR/MTP, two trials; **28 timed + 20 warmups**.
- Feature measured at `cf6e6811f19dcecb8bf82c218d441c9d0a2acb9d`: eight fresh servers, `0.5` and `0.1`, AR/MTP, two trials; **56 timed + 40 warmups**. Final commit `1293e959` only adds settings POST logging, invalid-persistence tests and removes unrelated formatting.
- All **84 timed and 60 warmup** responses passed expected continuation, exact input/output work, and response text/count references. References also matched **between sources**. Effective ratio and actual MTP activation matched every arm.
- Same local mixed 4/8-bit `Youssofal/Qwen3.8-27B-MTPLX-Optimized-Speed` checkpoint, model file hashes, tokenized input corpus and package versions. M3 Max, 64 GiB, MLX 0.32.4, mlx-lm `0d4d3d04`, mlx-vlm 0.7.10 (`4319ef2c`), Transformers 5.20.2, oMLX 0.7.3.dev2.
- Greedy, prefix cache/DFlash off, context 32768, concurrency cap four, stock adaptive MTP. Warmup: serial plus four concurrent `256/32` requests. Timed: solo `512/16`, four-way burst `512/16`, overlap `512/128` plus `2048/16`, newcomer submitted one second after first visible content.
- Minimum sampled available memory: baseline **10.91 GiB**, feature **10.88 GiB**. Maximum per-arm swap growth **0 GiB**. No resource guard aborts; every owned server stopped. No model weights, raw authenticated server state or environments are published.

## Descriptive default comparison

Medians of two trials. Overlap TTFT is the mean of the existing and newcomer
request TTFTs; individual timings are in the CSVs. These small observations are
not a regression budget or a statistically controlled source comparison.

| Mode / case | Upstream TTFT (s) | Feature 0.5 TTFT (s) | Upstream whole case (s) | Feature 0.5 whole case (s) | Upstream output tok/s | Feature 0.5 output tok/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AR / solo | 2.37 | 2.43 | 3.18 | 3.24 | 5.03 | 4.94 |
| AR / burst | 7.74 | 7.53 | 12.43 | 12.20 | 5.19 | 5.25 |
| AR / overlap | 8.17 | 8.27 | 18.83 | 19.00 | 7.65 | 7.58 |
| MTP / solo | 2.44 | 2.51 | 2.70 | 2.78 | 5.93 | 5.77 |
| MTP / burst | 7.85 | 7.99 | 11.35 | 11.61 | 5.64 | 5.53 |
| MTP / overlap | 6.26 | 6.46 | 13.79 | 14.18 | 10.45 | 10.19 |

## Reproduce

Run the feature's portable harness in its native MLX environment, once per
fresh output directory:

```sh
python scripts/benchmark_decode_fair_share.py \
  --source-root /path/to/untouched-upstream-checkout \
  --server-python /path/to/native-mlx-env/bin/python \
  --model-path /path/to/local-model --output-dir /path/to/new-baseline-results \
  --baseline-default --ratios 0.5 --modes ar mtp --repeats 2 \
  --quick --cases solo burst overlap

python scripts/benchmark_decode_fair_share.py \
  --server-python /path/to/native-mlx-env/bin/python \
  --model-path /path/to/local-model --output-dir /path/to/new-feature-results \
  --ratios 0.5 0.1 --modes ar mtp --repeats 2 \
  --quick --cases solo burst overlap
```

`validation.json` records source/harness/model/corpus hashes, runtime versions,
references, ordering, memory and cleanup checks. The two CSVs retain per-trial
metrics, including feature `0.1`; `quick-corpora.json` contains the exact inputs.
Raw SSE, server logs and full per-request results remain local. No generated
native token-ID capture or exclusive phase timing is claimed.
