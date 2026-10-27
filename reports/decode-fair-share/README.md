# Decode Fairness Ratio PR evidence

- [Contribution-guide compliance update and refreshed validation](compliance_update_20261027/README.md)
- [Full matched AR/MTP report](decode_fair_share_sweep_20261025/REPORT.md)
- [Protocol reproduction](decode_fair_share_sweep_20261025/REPRODUCE.md)
- [Earlier vLLM Metal / oMLX TTFT investigation](vllm_metal_comparison_20261023_ttft/REPORT.md)
- [Earlier two-value MTP experiment](decode_fair_share_fixed_20261025/REPORT.md), qualified and updated by the full sweep
- [Actual GUI and WebUI captures](screenshots/)
- [Current-source 27B integration checks](integration_20261027/README.md)
- [Implementation tests and build diagnostics](implementation_checks_20261027/README.md)

The historical benchmark used the fixed singleton-MTP source at
`04a5be43dc2f91ea2fa0aa26fbbe3a78147bf7c9` plus its retained numeric prototype.
Its measured values and qualifications are preserved. Publication copies redact
local paths and identify unpublished logs/scripts/source archives as retained
locally. Original file hashes are recorded in `publication-provenance.json`.
The synthetic input fixtures contain no real production incidents or customer
requests.

The portable tuning script belongs to the separate feature commit. It is linked
from the prepared PR description. The short current-upstream/feature integration
checks are recorded separately; their timings must not be pooled with the frozen
report or used as a new engine ranking.

Screenshots are actual debug builds and the real WebUI, using isolated settings.
Before: upstream `891758cf4034b3e4230c11821dc2c1674e57061c`. After: the exposure
implementation. The images also show that the disabled numeric field retains
`0.25`. Window focus differs between native captures.

This evidence stays outside the production feature diff on a separate branch.
