> Publication copy: local paths are redacted. Raw logs, environments and the source archive remain local. Published measurements and qualifications are unchanged.

# Matched AR/MTP decode_fair_share sweep

Frozen before measurement on 25 October 2026, Asia/Singapore. The hypothesis is
that useful ratios depend on workload, MTP mode and metric. Report evidence
against that hypothesis as well: do not seek a predetermined crossover.
A finite sweep can find no common winner among tested settings/conditions;
it cannot prove a statement about every real-valued ratio and future workload.

Reuse the verified fixed source at PR 4837 head
04a5be43dc2f91ea2fa0aa26fbbe3a78147bf7c9 (0.7.3.dev2, based on 78fa08bc),
plus only the retained numeric-setting prototype. The temporary source is
<LOCAL_TEMP>/omlx-fair-share-fixed-20261025/source. All profiles use the same
source, native Python environment and checkpoint. No dependency upgrade,
production change, GUI change, PR update or external publication is part of
this study. Earlier studies are context only; do not pool their timings.

Only the local mixed 4/8-bit Qwen3.8-27B-MTPLX checkpoint may load. Same
streaming completions API, frozen rendered prompts, temperature 0, top_p 1,
repetition penalty 1, other penalties 0. Prefix cache and DFlash disabled,
context 32768, concurrent request cap 4, ordinary chunked-prefill option
false, decode fairness true. Fairness contention chunking remains active.
MTP-on retains stock adaptive learned-head/copy behavior and AR fallback;
MTP-off is the same backend with the model's mtp_enabled setting false.
Current source/config/logs take precedence over historical depth-cap notes.

## Fixed design

Five ratios: 0.1, 0.25, 0.5, 0.75, 1.0; modes AR and MTP; two fresh servers
per profile, 20 arms. The 10-profile first pass in order.json is followed by
its exact reverse, placing each profile's repetitions symmetrically in time.
No replacement or retry of measured trials. No ratio, model or workload is
added after observing results. This is a descriptive screening sweep, not a
continuous optimization or adequately powered population-tail study.

Each server has one serial and four concurrent 1024/32 copy warmups. Require
the serial warmup and actual startup scheduler config to pass before starting
concurrent warmups. After warmup, one 4096/128 solo copy is always first as an
uncontended control. The first pass then runs protect, burst, natural; the
reverse pass runs natural, burst, protect. Idle two seconds between cases.

| Case | Timed requests in every arm |
| --- | --- |
| Solo control | One 4096-input / 128-output copy continuation |
| Protect | One 2048/768 copy, then 16384/128 newcomer one second after first visible ongoing content |
| Burst | Four simultaneous 4096/128 copy continuations |
| Natural ragged | Four engineering prompts with 1024/2048/4096/8192 inputs, each with output cap 128 |

220 timed requests and 100 warmup responses are planned. Roles within a case
are correlated. Lower copy/MTP acceptance in the natural case is a hypothesis
to check in stock logs, not an assumed property of every response.

## Validity and resource gates

All structured cases require HTTP success, exact prompt/output counts,
expected ledger continuation and full raw-text hash equality with the fixed
correct reference. The reference bytes are independently backed by prior
correct runs; old performance values are not reused. Any structured or
transport/count failure stops the study and remains recorded. Natural output
may end before its cap; retain actual work counts and response text. Compare
natural responses to the same corpus role in the first AR/0.5 arm. Divergent
text/work means performance-only: do not use that cell as a quality-equivalent
speed result or as evidence rejecting a common optimum. If the AR reference's
own repetition diverges, flag that limitation too. No semantic-quality claim.

Use the prior 40 GiB process guard and machine guard: three consecutive
samples below 1.25 GiB available, or more than 1.5 GiB swap-used growth, stop
the owned server group and the study. Preserve all partial/failure outputs.
No guard is weakened or retried. Run sequentially, on AC power, with no other
known model job. Isolate state/helper paths and retain user/PR file hashes.
Do not interpret unchanged swap-used as proof of zero paging. Before starting,
validate logger attributes against the pinned source without loading weights.

No per-step, model-forward, or generated-token observation hooks. The startup
logger only records actual scheduler config; it must run before measurement.
Save request bodies, raw SSE, visible text, usage, client times, native system
snapshots and memory samples. Retain native MTP stock summaries (acceptance,
copy acceptance, cycles, tokens/cycle, handoff, existing phase counters).
These are not exclusive GPU timings or direct native-token timestamps.

## Analysis fixed before measurement

Primary metrics are fixed-response whole-case completion, newcomer TTFT and
ongoing full client completion in protect. Also report mean request completion,
aggregate actual output / case wall time, per-role TTFT/completion, and each
response's content-event gap p50/p95/p99/max. SSE chunks can contain multiple
tokens; do not call these server token intervals. Natural work/output parity,
memory/thermal/paging snapshots and MTP efficiency are separate checks.

Report both repetitions, median and full range, not confidence intervals.
Request p95/p99 across four simultaneous responses are not population-tail
estimates. Keep modes separate except for matched comparisons on this stack.
Solo controls reveal baseline variation; the ratio is expected to be inactive
without contention, so solo differences do not establish a tuning benefit.

For every structured contended condition, compare each candidate to default
using the two same-pass trials. A material directional change is >=10% in
the ratio of medians with the same sign in both passes. Show smaller or
inconsistent changes as inconclusive; report exact paired magnitudes. This
screen does not replace uncertainty estimates or a mechanistic experiment.

For every mode/workload/metric, list the descriptive best tested value and
all values within 10% of it. Check intersections across contended structured
conditions, both within mode and across modes. An empty intersection means
no tested ratio is within that descriptive tolerance everywhere. Separately
look for repeatable >=10% tradeoffs where one ratio improves TTFT and another
improves ongoing completion or whole-case completion. Do not conflate best
median, meaningful dominance, and a causal proof that MTP alone changed an
optimum. State whether a common best/default remains plausible given noise.

Keep streaming gap tradeoffs visible, but do not let a single maximum-gap
outlier decide a universal winner. Do not form an arbitrary weighted composite
score or change the default. Any future parameter refinement or holdout
confirmation is a separate preregistered experiment, not a search for the
desired conclusion inside this fixed sweep.
