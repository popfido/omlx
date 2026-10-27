# Implementation validation, 2026-10-27

Base: `891758cf4034b3e4230c11821dc2c1674e57061c`.
Final feature: `1293e9591d168ae54cf103eedb4bb2b093b2017e`.

- Final affected backend suite: **663 passed** (settings, decode fairness, shared forward fairness, admin aliases, prefill OOM handling).
- WebUI resource behavior: **5 passed**. Six standalone JavaScript files passed their Node tests.
- Native DTO and Performance view-model: **24 passed**.
- `make web` and `make app`: passed. The app build used an isolated Python 3.11 environment with the existing native build requirements. The feature environment uses Python 3.12 and the current upstream dependency pins.
- Actual GUI Apply and WebUI Save/reload retained `0.25` while fairness was off; WebUI rejected `1.1` before sending an update. UI fixture context limit was explicitly `32768`.
- Full default feature suite: **18,244 passed, 1 failed, 1,166 skipped**.
- Untouched upstream full suite, same environment: **18,225 passed, 1 failed, 1,163 skipped**. Both failed the same pre-existing, order-dependent DeepSeek test: `tests/test_deepseek_v4_patch.py::TestDeepseekV4CompressedNativeAttention::test_ratio128_dispatch_and_reference_fallbacks` (`dense_masks` length 2, expected 3). That test passed in isolation on both sources; the baseline DeepSeek file passed 141 tests with four skips.

The full suite is therefore **not green**. Its shared baseline failure remains
outside this settings/UI change. Full suites ran before the final POST logging
and invalid-persisted-setting tests; the final affected suite passed 663 tests
afterward. Hardware measurements use feature commit `cf6e6811`; the final delta
adds settings POST logging, two validation cases and removes unrelated formatting.
No timed inference path changed after those measurements.

Logs in this directory retain diagnostics with local absolute paths normalized.
The original logs remain local. `checks.json` provides a compact index.
