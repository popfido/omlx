> Publication copy: local paths are redacted. Raw logs, environments and the source archive remain local. Published measurements and qualifications are unchanged.

# Conclusion on exposing decode_fair_share

**Tuning can help particular workloads, and the evidence supports an advanced
scheduling control with the existing 0.5 default retained.** It does not
support an automatic change to 0.1. The non-MTP measurements show a useful
latency/progress tradeoff; the new repaired-MTP comparison favors 0.5 on
newcomer TTFT and completion time. Measurements support configurability;
whether it belongs in the GUI is also a product decision.

The new measurement closes the earlier MTP correctness gap. All four fresh
servers completed in the frozen 0.5 / 0.1 / 0.1 / 0.5 order, with 8/8 measured
responses matching complete known-correct text hashes and exact work counts.
There were also 20 successful warmup responses. No measured trial was retried.

The common workload is the local mixed 4/8-bit Qwen3.8-27B-MTPLX checkpoint on
this M3 Max / 64 GiB Mac: one 2048-input / 768-output response, then one
16384-input / 128-output newcomer one second after first visible content.
Sampling is greedy, prefix caching and DFlash are off. Figures are medians
of two fresh-server trials per ratio, with full ranges in brackets. These
ranges are not confidence intervals.

The AR table is historical evidence from 24 October, oMLX 0.7.2 and its older
dependency pins. The MTP table is a new 25 October experiment using
0.7.3.dev2-based PR 4837 head plus the same numeric-setting prototype and the
latest pinned dependency environment from the correctness-fix validation.
Compare ratios **within** each table. These are not matched current AR-versus-MTP
speed measurements, and the timings are not pooled across stacks.

## Without MTP: a useful preference tradeoff

| Metric | Default 0.5 | Ratio 0.1 | Change from default |
| --- | --- | --- | --- |
| Newcomer TTFT, s | 152.96 [143.53, 162.38] | 112.38 [111.26, 113.49] | 26.5% lower |
| Ongoing full client completion, s | 166.05 [155.40, 176.70] | 173.58 [170.66, 176.50] | 4.5% longer |
| Whole-case completion, s | 174.93 [163.60, 186.25] | 173.58 [170.66, 176.50] | 0.8% lower; essentially unchanged at this sample size |

Server-observed ongoing generation during the overlap fell from 5.40 to
1.92 tok/s, about 64%. Lower newcomer latency therefore has a cost for the
existing response even when total time changes little. The existing off
switch gave 103.99 s newcomer TTFT but only 0.019 tok/s ongoing overlap
progress and 181.00 s whole-case completion. A numeric value supplies a useful
intermediate choice with the other controls held fixed.

The broader prior study also contains throughput gains in some 4B burst
cases and regressions in other model/workload combinations. The lower ratio
is not uniformly beneficial. See the original
report (retained locally),
full one-model tables (retained locally), and
the exact values reconstructed here in historical-ar.json (retained locally).

## With repaired native MTP: lowering to 0.1 did not help this workload

| Metric | Default 0.5 | Ratio 0.1 | Change from default |
| --- | --- | --- | --- |
| Newcomer TTFT, s | 104.21 [98.20, 110.23] | 117.64 [113.99, 121.29] | 12.9% longer |
| Ongoing full client completion, s | 54.73 [48.55, 60.92] | 136.99 [130.51, 143.46] | 150.3% longer, about 2.5 times |
| Whole-case completion, s | 119.23 [112.68, 125.78] | 138.01 [132.56, 143.46] | 15.8% longer |
| Aggregate fixed-output rate, tok/s | 7.54 [7.12, 7.95] | 6.50 [6.25, 6.76] | 13.7% lower |

The first pair's newcomer TTFT was 23.5% worse at 0.1; the reversed pair was
3.4% worse. Whole-case completion was 27.3% and 5.4% worse respectively. Thus
both pairs moved against 0.1, with substantial variation in the size of the
effect. The predeclared material TTFT-benefit screen was not met.

| Arm | Ratio | Newcomer TTFT, s | Ongoing completion, s | Whole-case completion, s | Exact reference text |
| --- | --- | --- | --- | --- | --- |
| 01 | 0.5 | 98.20 | 60.92 | 112.68 | Both match |
| 02 | 0.1 | 121.29 | 143.46 | 143.46 | Both match |
| 03 | 0.1 | 113.99 | 130.51 | 132.56 | Both match |
| 04 | 0.5 | 110.23 | 48.55 | 125.78 | Both match |

The stock logs recorded a late-join MTP handoff in both 0.1 trials. In both
0.5 trials the ongoing response completed before the newcomer joined decoding.
The ongoing response logged 124/126 MTP verification cycles at 0.5, versus
188/193 summed across its pre/post-handoff states at 0.1, with additional
batched AR handoff tokens. This supports an interaction with MTP lifecycle and
work performed. It does not isolate which phase caused the TTFT difference.
No phase timestamps or inference hooks were added for this measurement.

Client delivery remains a separate metric. Ongoing maximum SSE gaps were
21.58/1.75 s at 0.5 and 3.72/3.47 s at 0.1; ongoing p95 gaps were 1.51/1.63 s
and 3.48/1.85 s respectively. The large default gap appeared in only one
repeat. A completion-time win does not establish uniformly smoother streaming,
and this experiment does not establish the cause of that delivery variation.

## Interpretation for the setting

The source multiplies measured contended prefill time by the ratio to accrue
decode debt. In a simplified continuously contended schedule, decode's time
fraction is approximately ratio / (1 + ratio): 0.5 corresponds to one-third,
and 0.1 to about one-eleventh. This is scheduling accounting, not a hard GPU
allocation, token-rate guarantee, or monotonic TTFT control. MTP changes how
long requests overlap and can change handoff, batching and speculative work.

The case for exposing the parameter comes from repeated useful tradeoffs in
the non-MTP study. The MTP results strengthen the case for preserving the
default and avoiding a universal low-ratio preset. They do not establish a
better MTP value, nor rule out benefits for other MTP workloads or values.
Do not reuse correctness-failed timings from the pre-fix MTP study as if the
repair retrospectively validated those runs.

A proposal should retain 0.5, retain the existing fairness switch, and label
the control as time reserved for ongoing generation while reading new prompts.
Avoid promising that a smaller number always improves TTFT. The prototype is
not a completed API/GUI feature: persistence, validation, live engine/pool
updates, debt/hold behavior, and the constant still used by ForwardFairnessGate
need a consistent implementation. See the existing
PR scope (retained locally). No exposure change was
added to the singleton-MTP correctness PR.

## Validation and provenance

- Fixed source: `04a5be43dc2f91ea2fa0aa26fbbe3a78147bf7c9`, based on upstream
  `78fa08bc1aef7290c93c83bb70811547763ebf33`, plus the retained numeric-setting
  patch. [Source record](source.json), frozen inputs (retained locally).
- MLX 0.32.4; mlx-lm `0d4d3d04f8ab7ce4a51e7209e8615755a48ba94d`;
  mlx-vlm `4319ef2c837b7226b758c3dd69edda51b7079785`.
- Native MTP active in every server, stock adaptive depth/learned-head/copy
  behavior and fallback retained. Concurrency cap 4, context 32768, ordinary
  chunked-prefill option false; fairness contention chunking remains active.
- Actual scheduler ratios recorded at startup. No per-step, model-forward or
  native-token observation hooks. Exact full text and usage counts were
  checked; this run does not independently capture native generated token IDs.
- Preflight (retained locally): 353 passed, including numeric-setting,
  settings and all six singleton-position regression cases.
- All four measured arms passed the 40 GiB process/machine resource policy.
  Minimum sampled available memory was 11.91 GiB, with no positive swap-used
  growth in any measured arm. Existing system swap remained in use; this does
  not prove zero paging or exclusive machine use.
- A premeasurement logger error caused a failed model load and swap guard
  abort. It produced no successful warmup or measured case. The full failure
  is retained in setup-failure-01 (retained locally). Only the logger
  field was corrected, then attributes/memory/preservation were checked and
  the entire four-arm study was refrozen before measurement. See
  [plan](PLAN.md) and startup check (retained locally).

One Mac, one current MTP checkpoint, two repetitions per value, one contention
workload. Copy-friendly MTP behavior does not establish natural-answer quality
or behavior on low-acceptance prompts, other models, cache hits, multiple
engines, or other parameter values. The ratio comparison is complete for this
fixed experiment; broad model-independent optimization is unproven.

Raw requests/SSE and per-trial summaries are under `wire/` and `runs/`.
[Results and paired changes](results.json), [reproduction](REPRODUCE.md), and
final hashes/preservation/process checks (retained locally) retain the
evidence. The user checkout and correctness-fix worktree were preserved;
benchmark servers are stopped.
