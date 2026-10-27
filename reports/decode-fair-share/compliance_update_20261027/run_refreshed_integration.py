#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Use the unchanged portable harness for an ABBA current-source integration check."""

import argparse
import asyncio
import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace


async def run(options):
    spec = importlib.util.spec_from_file_location(
        "decode_fairness_harness",
        options.feature_root / "scripts/benchmark_decode_fair_share.py",
    )
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    output = options.output_dir
    output.mkdir(parents=True, exist_ok=False)
    args = SimpleNamespace(
        model_path=options.model_path,
        source_root=options.feature_root,
        server_python=Path(sys.executable).absolute(),
        output_dir=output,
        quick=True,
        corpus_file=None,
        cases=["solo", "burst", "overlap"],
        memory_guard_gb=40.0,
        port=18109,
        baseline_default=False,
    )
    inputs = harness.corpus(args)
    harness.save(output / "corpora.json", inputs)
    sources = {
        "baseline": options.baseline_root,
        "feature": options.feature_root,
    }
    identities = {key: harness.source_identity(root) for key, root in sources.items()}
    order = []
    for source, repeat in [
        ("baseline", 1),
        ("feature", 1),
        ("feature", 2),
        ("baseline", 2),
    ]:
        modes = ["ar", "mtp"] if repeat == 1 else ["mtp", "ar"]
        cases = (
            ["solo", "overlap", "burst"]
            if repeat == 1
            else ["solo", "burst", "overlap"]
        )
        for mode in modes:
            order.append(
                {
                    "source_label": source,
                    "pass": repeat,
                    "mode": mode,
                    "ratio": 0.5,
                    "cases": cases,
                }
            )
    for mode in ["ar", "mtp"]:
        order.append(
            {
                "source_label": "feature",
                "pass": 1,
                "mode": mode,
                "ratio": 0.1,
                "cases": ["solo", "overlap", "burst"],
            }
        )
    harness.save(
        output / "provenance.json",
        {
            "purpose": "Short integration validation; ABBA source blocks at stock 0.5 plus separate non-default AR/MTP smoke. Not a new performance ranking.",
            "sources": identities,
            "order": order,
            "quick": True,
            "corpus_sha256": harness.sha(output / "corpora.json"),
            "model_files": [
                {"name": p.name, "bytes": p.stat().st_size, "sha256": harness.sha(p)}
                for p in sorted(options.model_path.iterdir())
                if p.suffix in (".json", ".jinja", ".safetensors")
            ],
        },
    )
    references, results = {}, []
    try:
        for i, profile in enumerate(order):
            source = profile["source_label"]
            args.source_root = sources[source]
            args.baseline_default = source == "baseline"
            assert harness.source_identity(args.source_root) == identities[source]
            arm_dir = (
                output / f"{i+1:02d}-{source}-{profile['mode']}-{profile['ratio']}"
            )
            print(json.dumps({"event": "arm", "arm": arm_dir.name}), flush=True)
            results.append(
                await harness.arm(args, profile, arm_dir, inputs, references)
            )
            harness.save(output / "results.json", results)
            harness.save(output / "reference.json", references)
            assert harness.source_identity(args.source_root) == identities[source]
    except BaseException as error:
        harness.save(
            output / "failure.json",
            {"error": repr(error), "completed_arms": len(results)},
        )
        raise
    rows = [
        {
            **{k: v for k, v in arm.items() if k != "cases"},
            **{k: v for k, v in case.items() if k != "requests"},
        }
        for arm in results
        for case in arm["cases"]
    ]
    with (output / "trial-metrics.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"event": "complete", "arms": len(results)}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["feature-root", "baseline-root", "model-path", "output-dir"]:
        parser.add_argument("--" + name, type=Path, required=True)
    options = parser.parse_args()
    for name, value in vars(options).items():
        setattr(options, name, value.expanduser().absolute())
    asyncio.run(run(options))
