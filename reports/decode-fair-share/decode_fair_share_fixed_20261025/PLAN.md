> Publication copy: local paths are redacted. Raw logs, environments and the source archive remain local. Published measurements and qualifications are unchanged.

# Fixed-MTP fairness follow-up

Frozen before measurement, 25 October 2026, Asia/Singapore.

Premeasurement setup amendment: the initial launch failed in a startup-only
logger because it read SchedulerConfig.max_concurrent_requests rather than
max_num_seqs. The model loader attempted its fallback and the swap-growth
guard stopped that server. Zero warmup responses or timed cases succeeded.
All original files, logs, failed requests and the frozen manifest are retained
under setup-failure-01/. Correct only the logger field; verify its attributes
without loading weights and check memory/process state before refreezing and
starting the complete four-arm sequence below. These are setup-failure data,
not a replacement for any measured trial. No further startup retries or
measured-trial replacements are planned.

Question: does reducing decode_fair_share from 0.5 to 0.1 provide a useful
TTFT/completion tradeoff with native MTP after the position-state repair?
The earlier AR study remains separate historical evidence; do not pool its
timings with this newer dependency stack or turn this into an AR/MTP ranking.

Source: PR 4837 head 04a5be43dc2f91ea2fa0aa26fbbe3a78147bf7c9, based on
upstream 78fa08bc (0.7.3.dev2), plus only the previously tested numeric-setting
prototype in a temporary snapshot. Use the current pinned native environment
from the PR validation: MLX 0.32.4, mlx-lm 0d4d3d04, mlx-vlm 4319ef2c.
Preserve the PR worktree and the existing user checkout and settings.

Four fresh-server arms in ABBA order: MTP/0.5, MTP/0.1, MTP/0.1, MTP/0.5.
No replacement attempts. Each arm has one serial and four concurrent 1024/32
warmups, followed only by the unchanged contention case: 2048/768 ongoing,
then a 16384/128 newcomer one second after first visible content. Omit the
solo case equally from all arms; the policy is inactive without contention
and the earlier studies already retain those null controls. No off/1.0 sweep
or other workload is added after looking at results.

Same cached mixed 4/8-bit Qwen3.8-27B-MTPLX checkpoint and frozen corpora.
Greedy sampling; stock adaptive native MTP, learned-head/copy behavior and
fallback; DFlash and prefix cache off; context 32768; concurrency cap 4;
chunked-prefill option false while fairness retains its contention chunk cap.
Only this 27B model may load. No per-step, model-forward or token observation
hooks. Log the actual scheduler configuration once at construction, before
warmup; capture raw SSE on the client. Port 18109 and isolated temporary
helper/settings state. Keep the prior 40 GiB process guard and machine guards:
three samples below 1.25 GiB available, or >1.5 GiB new swap-used growth,
terminate only the experiment server group and stop the study.

Require HTTP success, exact input/output counts, expected copy continuation,
and complete raw-text hash equality to the correct per-role reference from
the latest fixed plain-server validation. Client text/tokenization is not a
new native-ID observation. A copy failure disqualifies that profile from a
quality-equivalent performance conclusion; retain it and complete the fixed
sequence only if transport/work counts/resources are otherwise sound.

Primary metrics: newcomer first-visible-content latency, ongoing full client
latency, and whole-case completion. Also retain visible SSE gap distribution
and aggregate fixed output tokens / whole-case wall time. No backend token-rate
claim from client packet timestamps. Report both repetitions and ranges;
requests within a trial are correlated. Pair arms 1/2 and 4/3. A >=10% TTFT
change, with the same direction in both pairs, is the materiality screen;
show ongoing and batch costs regardless. Smaller or inconsistent changes are
not strong evidence of useful MTP tuning for this workload. Do not infer a
universal optimum or change the 0.5 default.

Recheck sources/model hashes, effective ratios, preserved files, native MTP
activation and process shutdown. No parameter-exposure PR, GUI edit or update
to the correctness-fix PR is part of this measurement.
