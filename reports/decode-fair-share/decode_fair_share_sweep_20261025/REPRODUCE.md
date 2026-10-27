# Reproduce the tuning workloads

The published report records the frozen 2026-10-25 numeric prototype experiment.
Its exact source revision, patch, package pins, checkpoint hashes, input IDs,
run order and reference outputs are retained here. The original machine-specific
commands are in [HISTORICAL_REPRODUCTION.md](HISTORICAL_REPRODUCTION.md); the old
runners, raw logs and source archive remain local.

The portable runner supplied with the exposure PR is
`scripts/benchmark_decode_fair_share.py`. It validates the supported setting on
the selected checkout, including effective API values and actual MTP activation.
It recreates the study workloads; it does not make measurements from different
source/dependency versions interchangeable.

From the feature checkout, with its native MLX environment active:

```sh
python scripts/benchmark_decode_fair_share.py \
  --model-path /path/to/Qwen3.8-27B-MTPLX-Optimized-Speed \
  --output-dir /path/to/new-results \
  --corpus-file /path/to/this-evidence/decode_fair_share_sweep_20261025/corpora.json \
  --ratios 0.1 0.25 0.5 0.75 1.0 --modes ar mtp --repeats 2 \
  --cases solo burst overlap natural
```

The full order starts with AR/default, uses fresh servers and equal warmups,
and reverses profile and contention-case order in the second pass. The protocol
is 20 arms, 220 timed responses and 100 warmups. The runner checks continuation,
work and reference text/counts for structured cases. Divergent natural answers
remain performance-only. No generated native-ID capture or exclusive GPU-phase
timing is claimed.

Use `--quick --cases solo burst overlap` for shorter integration checks, without
`--corpus-file`. Those timings are separate from the full report. The
`--baseline-default --ratios 0.5` option permits an untouched pre-exposure server
with its stock default; the historical numeric prototype is not the supported
settings API and its old runner remains part of the local archive.
