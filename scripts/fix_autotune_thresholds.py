#!/usr/bin/env python3
"""Sync the `autotune_thresholds` field of the congruence analysis JSON to the
thresholds the networks were actually built at.

Background (see GitHub issue #7)
--------------------------------
The "AUTO-TUNE Thresholds Used" panel on the HCV Congruence Analysis page reads
`autotune_thresholds` from `network_congruence_analysis.json`. Those values were
populated from the per-region `*.threshold.json` files, which frequently hold a
degenerate *fallback* "best guess" (AUTO-TUNE emits `hasError: true` when it can
not find a strong outlier, e.g. `1a_0.2_ns5b -> 0.00099`). The networks shown on
the same page (and every alpha / ARI / Krippendorff statistic) were instead built
at the score-optimal threshold recorded in each network's HIV-TRACE output under
`Settings.threshold` (e.g. `1a_0.2_ns5b -> 0.01386`). The panel therefore
contradicted the page's own Network Statistics table and the manuscript.

Fix
---
Source the displayed thresholds from the same place network construction does:
each region's `results/<combo>_<region>.hivtrace.json` -> `Settings.threshold`.
`autotune_thresholds` is rebuilt to mirror the regions present in
`network_statistics`, so the panel and the statistics table always agree.

A region is only populated when AUTO-TUNE actually produced a distance sweep for
it (a `results/<combo>_<region>.aligned.report.tsv` exists). When the sweep
failed outright the network is built at a hardcoded default (e.g. the 2a combos
all fall back to 0.005); that default is not an AUTO-TUNE result, so the region is
left out of the panel rather than mislabeled as one.

Run from the repo root:
    python3 scripts/fix_autotune_thresholds.py            # apply
    python3 scripts/fix_autotune_thresholds.py --check     # report drift, no write
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONGRUENCE_JSON = REPO_ROOT / "src/data/hcv/autotune/network_congruence_analysis.json"
RESULTS_DIR = REPO_ROOT / "results"


def autotune_threshold(combo: str, region: str):
    """Return the AUTO-TUNE threshold the network was built at, formatted like the
    sweep report (`%g`, e.g. 0.01386 / 1e-05), or None when AUTO-TUNE did not
    produce a sweep for this region (so the network used a non-AUTO-TUNE default).
    """
    if not (RESULTS_DIR / f"{combo}_{region}.aligned.report.tsv").exists():
        # No distance sweep -> the network's threshold is a hardcoded fallback,
        # not an AUTO-TUNE result. Don't present it as one.
        return None
    path = RESULTS_DIR / f"{combo}_{region}.hivtrace.json"
    settings = json.loads(path.read_text()).get("Settings", {})
    threshold = settings.get("threshold")
    if threshold is None:
        raise ValueError(f"{path} has no Settings.threshold")
    return "%g" % float(threshold)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report mismatches and exit non-zero without modifying the file",
    )
    args = parser.parse_args()

    data = json.loads(CONGRUENCE_JSON.read_text())
    changes = []
    for combo, entry in data.items():
        if combo == "_summary" or not isinstance(entry, dict):
            continue
        network_stats = entry.get("network_statistics") or {}
        if not network_stats:
            continue
        old = entry.get("autotune_thresholds") or {}
        new = {}
        for region in network_stats:
            value = autotune_threshold(combo, region)
            if value is None:
                continue
            new[region] = value
            if old.get(region) != value:
                changes.append((combo, region, old.get(region), value))
        entry["autotune_thresholds"] = new

    if not changes:
        print("autotune_thresholds already match network thresholds; nothing to do.")
        return 0

    print(f"{'combo':<9}{'region':<16}{'old':<12}{'new'}")
    print("-" * 45)
    for combo, region, old_value, new_value in changes:
        print(f"{combo:<9}{region:<16}{str(old_value):<12}{new_value}")
    print(f"\n{len(changes)} threshold(s) {'drifted' if args.check else 'updated'}.")

    if args.check:
        return 1

    CONGRUENCE_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {CONGRUENCE_JSON.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
