> Publication copy: local paths are redacted. Raw logs, environments and the source archive remain local. Published measurements and qualifications are unchanged.

# Reproduce the repaired-MTP fairness comparison

Use an Apple Silicon Mac with native Metal access and enough free unified
memory for this exact 27B checkpoint. The local paths below describe the
actual experiment, not a model-name compatibility claim.

The experiment source was created with `git archive` from PR 4837 head
`04a5be43dc2f91ea2fa0aa26fbbe3a78147bf7c9` into
`<LOCAL_TEMP>/omlx-fair-share-fixed-20261025/source`, followed by `git apply`
of the retained prototype
`../vllm_metal_comparison_20261023_ttft/decode-fair-share.patch`.
The patch hash and source location are in `source.json`; the exact dependency
commits and source/input/script hashes are in `frozen-inputs.json`.

Python is `<LOCAL_TEMP>/omlx-mtp-pr-20261025/env/bin/python`. Dependencies are
the latest pinned upstream dependencies from the singleton-MTP fix validation,
not the older environment used for the historical non-MTP fairness matrix.
See `frozen-inputs.json` for versions and direct installation URLs.

Preflight, executed in the temporary source directory:

```sh
PYTHONPATH=<LOCAL_TEMP>/omlx-fair-share-fixed-20261025/source \
  <LOCAL_TEMP>/omlx-mtp-pr-20261025/env/bin/python -m pytest \
  tests/test_decode_fair_share.py tests/test_settings.py \
  tests/test_mlx_lm_mtp_patch.py::test_singleton_mtp_rebinds_positions_after_prefill_clear \
  -q
```

The driver uses the exact corpus bytes and per-role expected text in
`corpora.json` and `reference.json`. The only requested and loaded model is a temporary
`qwen27b` symlink to
`<LOCAL_USER>/.omlx/models/Youssofal/Qwen3.8-27B-MTPLX-Optimized-Speed`.
Its 16 checkpoint file hashes are under `qwen27b` in `models.json`.

Run from `<LOCAL_TEMP>`, with a fresh output directory and fresh temporary
state for every independent study. The driver deliberately rejects existing
arm directories; do not overwrite a previous result:

```sh
<LOCAL_TEMP>/omlx-mtp-pr-20261025/env/bin/python -u \
  <LOCAL_USER>/workspace/omlx/benchmarks/decode_fair_share_fixed_20261025/driver.py
```

`driver.py` fixes the order at MTP/0.5, MTP/0.1, MTP/0.1, MTP/0.5. Each arm
starts a fresh server on localhost port 18109, warms it equally, performs the
same two-request contention case, and shuts down its own process group.
`launch.py` records the scheduler configuration once at construction and
redirects the cluster helper into temporary state. It does not wrap inference
or collect native generated token IDs. `run.py` records full request bodies,
raw SSE events, visible text, usage counts, wall times and memory samples.

After four complete valid arms, run `analyze.py` with that same Python.
It checks counts, expected continuations and complete reference-text hashes
before producing descriptive `results.json`. `PLAN.md` defines the decision
screen, all stop rules and the retained premeasurement setup failure.

No user settings, normal cluster helper, GUI files or PR source are modified.
The exposure patch is experimental and is not a completed admin/API/GUI
implementation. The historical non-MTP study is retained separately under
`../decode_fair_share_20261024/`; do not pool timing values across its older
dependency stack and this run.
