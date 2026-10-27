> Publication copy: local paths are redacted. Raw logs, environments and the source archive remain local. Published measurements and qualifications are unchanged.

# TTFT diagnosis and an optional oMLX scheduling adjustment

Measured on 23 October 2026. Earlier first tokens are partly a scheduling
choice, not proof of faster raw decode kernels. The controlled oMLX intervention
reduced concurrent TTFT while changing how smoothly active requests streamed.
It did not require sacrificing aggregate output throughput in these trials.
The tests do not isolate the entire historical oMLX/vllm-metal difference.

## Direct answers

1. Lower per-request speed after the first token and lower aggregate throughput
   are different. Prioritizing prompt work can start requests earlier and delay
   existing streams. It can also improve batching and raise aggregate throughput.
2. We confirmed a scheduling lever in oMLX: decode-time debt. Reducing that lever
   changes TTFT without changing the model or replacing its kernels.
3. We also observed vllm-metal executing mixed prefill/decode forwards. That is a
   real implementation difference. Measuring its independent performance benefit
   still requires a controlled kernel/runner experiment.
4. The 0.1 setting passed the predeclared local screening gates. It is a candidate optional TTFT preference, with the current 0.5 default retained.

## Matched work and source

- Apple M3 Max, 40 GPU cores, 64 GiB unified RAM, macOS 27.0; same Mac as the
  previous comparison. One benchmark server ran at a time.
- oMLX 0.7.2, commit `23b671f64f0a64f532e38d692a6c480ea704418d`, MLX 0.32.4,
  the same pinned mlx-lm/mlx-vlm dependencies and native kernels as the previous
  experiment. Source was reconstructed from the pinned Git tree into a fresh
  temporary snapshot. The candidate differs only by the retained patch.
- vllm-metal 0.32.0, commit `6d6f2c37f8242f1ff1a336534adf6c2d2fe2936d`, official
  wheel, MLX 0.32.2. The installed runner and inspected Git source have identical
  SHA-256. These remain different shipped dependency stacks.
- Same cached Qwen3.5-4B-MLX-4bit snapshot
  `32f3e8ecf65426fc3306969496342d504bfa13f3`; exactly 4096 input tokens,
  256 actual greedy output tokens, streaming HTTP `/v1/completions`.
- Same rendered ledger continuation corpus, no prefix reuse/storage, speculation,
  sparse prefill, KV compression, external engine, or ANE. Memory ceiling is
  16 GiB for oMLX; vllm-metal retains its previous 0.25 memory fraction.
- Explicit chunked-prefill setting remains false. Fairness can force resumable
  and packed prefill under contention; false does not mean those paths never run.
- Every arm starts a fresh server and discards two warmup batches of four
  concurrent 4096/64 requests. Each timed cell contains eight closed-loop
  requests. No model loading or warmup is included in the timing.

All **128 new timed responses** passed actual token counts and have the same
byte-for-byte output hash as the previous comparison. All 112 oMLX responses
also have the same complete generated token-ID sequence in the scheduler trace.
vllm-metal generated IDs were not collected; its checks cover text and reported
counts. This bounded synthetic-copy check is not broad model quality validation.

## First intervention: isolate the time-debt policy

Order: stock, zero debt, zero debt, stock. Each arm runs C=1 then C=4.
This contributes 64 timed requests, two fresh-server trials per policy/cell.
The intervention changes only `_DECODE_FAIR_SHARE` from 0.5 to 0.0; capped
chunks, memory guards, the fairness switch and model routes remain active.

| Metric, concurrency 4 | Default, ratio 0.5 | Experimental |
|---|---:|---:|
| Mean first-content latency, s | 13.09 (10.85–15.33) | 7.68 (7.40–7.96) |
| Aggregate output tokens/s, including prefill | 43.23 (37.59–48.86) | 51.40 (50.96–51.85) |
| Mean completion latency, s | 21.86 (19.12–24.60) | 19.83 (19.64–20.02) |
| Mean time after first content, s | 8.77 (8.27–9.26) | 12.15 (11.69–12.62) |
| 95th-percentile SSE content gap, s | 0.73 (0.61–0.84) | 1.12 (1.11–1.13) |
| Maximum SSE content gap, s | 0.90 (0.73–1.07) | 1.31 (1.26–1.35) |

Values are medians of two run values; parentheses are their full range. Latency
is a per-run request mean. These are not confidence intervals.

The observed mean-TTFT reduction is approximately 41%. The throughput increase
is descriptive: stock runs varied substantially and the serial null control
also varied despite the policy being inactive. Completion ranges overlap.
The consistent cost was larger gaps during streaming and longer post-first
intervals. Zero debt is not an unconditional improvement.

The C=1 null control used exactly the same path and accrued no decode debt.
Stock C=1 throughput was 45.51 (44.15–46.87) tokens/s and zero-debt
was 42.64 (42.38–42.90); first-content times were
3.21 (3.15–3.26) and 3.34 (3.32–3.36) s.
This variation is not an effect of a scheduling policy inactive at C=1.

## What the oMLX traces establish

Default C=4 trials spent 11.20 and 15.31 seconds in scheduler steps where
prefill was held by outstanding decode debt. Those steps did useful decoding;
this is not idle GPU time and must not be called wasted time. The experimental
policy eliminated that debt in both trials. Each C=4 cell still processed
32,760 external/chunked prefill tokens, with each request's final input token
processed by BatchGenerator before generation.

All four C=4 trials used one initial external prefill and 42 chunk forwards;
4–5 of the latter packed two prompt rows. The main chunk length was 704 tokens.
Thus oMLX already used packed prefill here. It did not put prompt and active
decode tokens in the same forward.

Default decode output steps were mostly batches of one or two requests:
1,208 output steps in arm 01 and 1,406 in arm 04, with no four-request output
steps. The zero-debt trials used 541 and 545 output steps, including 475 steps
of four requests each. Earlier prefill completion filled decode batches sooner.
This explains how earlier first tokens and higher aggregate throughput can
coexist with less-smooth streams for individual requests.

All timings above are host wall time around existing synchronous boundaries;
the instrumentation adds no MLX eval or synchronization. Lazy model submission,
host overhead, waiting and GPU execution are not separated into exclusive GPU
kernel durations.

## Confirmed vllm-metal execution

The separate diagnostic arm used the same workload and warmup protocol. At C=4,
the installed runner executed **17 mixed forwards** out
of 524 total forwards; 4 forwards
contained multiple prefill rows. It processed 28,672 of
32,768 prompt tokens in forwards that also included decode
rows. At C=1 there were no mixed forwards.

Its C=4 mean TTFT was 9.45 s and aggregate output rate was
50.89 tokens/s. This single instrumented trial confirms dispatch
composition, not a new repeated ranking or a causal GPU-kernel speed claim.
It must not be pooled with yesterday's benchmarks or the oMLX ABBA trials.

## Moderate setting: preserve positive decode repayment

A second ABBA uses the actual candidate configuration field at 0.5, 0.1, 0.1,
0.5, C=4 only. Both policies use identical candidate source and warmups. There
are 32 timed responses. The comparison and screening gates were written before
running it in balanced-plan.json (retained locally).

| Metric, concurrency 4 | Default, ratio 0.5 | Experimental |
|---|---:|---:|
| Mean first-content latency, s | 12.49 (10.07–14.92) | 5.96 (5.71–6.21) |
| Aggregate output tokens/s, including prefill | 45.37 (38.34–52.39) | 55.90 (52.61–59.20) |
| Mean completion latency, s | 20.96 (17.91–24.01) | 18.03 (17.00–19.05) |
| Mean time after first content, s | 8.47 (7.85–9.10) | 12.06 (11.28–12.85) |
| 95th-percentile SSE content gap, s | 0.71 (0.58–0.83) | 0.61 (0.57–0.64) |
| Maximum SSE content gap, s | 0.85 (0.66–1.05) | 1.06 (1.05–1.06) |

Screening result: **passed**.
Exact gates and outcomes: balanced-gates.json (retained locally).
The 0.1 setting passed the predeclared local screening gates. It is a candidate optional TTFT preference, with the current 0.5 default retained. No user-defined streaming SLO was supplied, and passing this
screen does not justify changing a release-wide default.

## Implemented candidate

decode-fair-share.patch (retained locally) adds `scheduler.decode_fair_share`
as an advanced settings-file option and `SchedulerConfig` field. It validates
finite values in [0,1], preserves the 0.5 default, and keeps capped chunks and
memory guards active at zero. It is per scheduler, so a tuned engine does not
change another engine's ratio. This patch requires server restart; it does not
add a UI or live API field. The existing `prefill_priority` setting controls
memory admission and is not this time-sharing preference.

Example partial settings, after applying the patch to oMLX 0.7.2:

```json
{"scheduler": {"decode_fairness": true, "decode_fair_share": 0.1}}
```

The patch applies cleanly to the pinned 0.7.2 tree. **95 focused tests passed**,
including existing fairness and settings tests, per-engine isolation, unchanged
default repayment, zero-debt chunk caps, positive 0.1 repayment, persistence and
invalid-number rejection. See tests.json (retained locally).

A separate 16-request HTTP integration arm using the saved zero setting verified
the same behavior without monkeypatching the ratio. Every response passed text
and token-ID checks, and the effective saved settings retained the configured
value. That arm is excluded from both ABBA estimates.

The patch is prepared against the compared stable release in an isolated
temporary source tree. The older user checkout and normal app settings were
not modified. Patch SHA-256: `ebb6250773510333edb2845989b7b05b5674f7527b017f18131169945dfbecab`.

## Limits and next validation

- Do not equate post-first wall time with raw decode-kernel throughput. It
  includes competing prefills, batching, scheduler stalls and stream delivery.
- Two trials per policy are a screening result. There is visible run-order and
  machine-state variation, background applications stayed open, and stable GPU
  clocks were not established. Memory traces and machine-wide paging deltas
  are retained; flat swap occupancy alone does not prove a paging-free system.
- Before adopting a profile broadly, use natural and ragged 1K/4K/8K prompts,
  C=1/2/4/8, long ongoing decodes with newly arriving requests, and explicit
  first-token and streaming-gap targets. Exercise cancellation and memory pressure;
  keep prefix-cache hits and speculative decoding separate.
- To improve both scheduling fronts through execution changes, prototype mixed
  prompt/decode forwards in oMLX and compare them with the same policy, model,
  dependency stack and outputs. Profile actual attention/GDN/projection routes
  with exclusive GPU timings. Mixed-forward counts alone cannot prove the
  independent kernel benefit, and this prototype does not implement that port.

## Inspectable evidence

- analysis.json (retained locally): all cells, ranges, token-ID hashes, chunk
  counts, debt timing, decode output batch widths and observed mixed forwards.
- run_diagnostic.py (retained locally), trace_omlx.py (retained locally),
  trace_candidate.py (retained locally), trace_vllm.py (retained locally),
  analyze.py (retained locally): launch and observation code.
- `runs/`: all request-level text, usage, SSE timestamps, launch commands,
  server logs, memory samples and scheduler/runner traces.
- candidate_manifest.json (retained locally),
  runtime-source-validation.json (retained locally),
  memory-deltas.json (retained locally), cleanup.json (retained locally).
- Previous exact corpus, model hashes and runtime inventories remain under
  `../vllm_metal_comparison_20261022/local_m3max/`; they are reused controls,
  not new head-to-head timing samples.
