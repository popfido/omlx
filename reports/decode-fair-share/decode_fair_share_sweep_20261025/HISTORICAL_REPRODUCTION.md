> Publication copy: local paths are redacted. Raw logs, environments and the source archive remain local. Published measurements and qualifications are unchanged.

# Reproduce the matched ratio sweep

`PLAN.md` and `order.json` specify the frozen design, measurements, gates and
decision rules. Source, models and dependencies are shared by all 20 profiles;
earlier timing studies do not enter this analysis.

Actual source is `<LOCAL_TEMP>/omlx-fair-share-fixed-20261025/source`, created
by archiving PR 4837 head `04a5be43dc2f91ea2fa0aa26fbbe3a78147bf7c9` and
applying the retained numeric-setting prototype. The patch location/hash is
in `source.json`; `source-inventory.json` records 1626 source files and
`frozen-inputs.json` records scripts, inputs, dependency commits and versions.
The verified source is also retained in `source.tar.gz`; its hash and the
standalone `decode-fair-share.patch` copy are recorded in `source-bundle.json`.
No checkpoint weights or Python environment are bundled.

Native Python is `<LOCAL_TEMP>/omlx-mtp-pr-20261025/env/bin/python`.
The exact mixed 4/8-bit local checkpoint is
`<LOCAL_USER>/.omlx/models/Youssofal/Qwen3.8-27B-MTPLX-Optimized-Speed`;
its 16 recorded file hashes are in `models.json`. `corpora.json` contains
the rendered prompts, native input IDs and their original JSON-ID hashes.
`reference.json` records the correct complete visible structured outputs.

The experiment used the following commands, run from `<LOCAL_TEMP>`:

```sh
<LOCAL_TEMP>/omlx-mtp-pr-20261025/env/bin/python -u \
  <LOCAL_USER>/workspace/omlx/benchmarks/decode_fair_share_sweep_20261025/preflight.py
<LOCAL_TEMP>/omlx-mtp-pr-20261025/env/bin/python -u \
  <LOCAL_USER>/workspace/omlx/benchmarks/decode_fair_share_sweep_20261025/driver.py
```

The driver requires new arm directories and never overwrites a measured trial.
To repeat independently, copy the input/scripts into a fresh output directory,
change the `TEMP` state path in `run.py` and the helper home in `launch.py` to
an unused temporary location, and refreeze with preflight before measurement.
Keep the same verified source snapshot or reproduce it from the recorded
commit and patch. Do not rerun the driver inside this completed result folder.

Each arm's full command, runtime config, effective scheduler/model settings,
server log, memory samples, system snapshots, warmups and case summaries are
under `runs/`. Full request bodies and raw SSE are under `wire/`.
There are no added inference or native-token hooks; `launch.py` wraps only
scheduler construction to record effective settings before warmup.

After completion, run `analyze.py` using native Python. `--partial` writes
separate progress artifacts without treating unfinished arms as primary.
The completed analysis writes `results.json`, `TABLES.md`, request/trial CSVs,
same-pass comparisons, per-condition preferred-value sets and their
intersections. Natural responses are matched against first AR/0.5 text/work;
divergent cases are performance-only, and natural cases do not enter the
structured-condition common-winner decision.

`plot.py` renders standalone PNG/SVG figures after timing, using the separate
existing plotting Python at `<LOCAL_TEMP>/omlx-fair-analysis-20261024/bin/python`.
`final_verify.py` rechecks source/model/script hashes,
user/PR files, the normal cluster helper, exact native package versions and
process shutdown. These artifacts remain local. No exposure feature or PR
publication is performed by this experiment.
