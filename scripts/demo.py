from __future__ import annotations

import json
import os
import time
from pathlib import Path

from demotenant_switchboard.services.switchboard import SwitchboardService

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = [
    ROOT / "examples" / "ecommerce.yaml",
    ROOT / "examples" / "project_management.yaml",
    ROOT / "examples" / "support_desk.yaml",
]


def main() -> None:
    service = SwitchboardService()
    output_root = ROOT / "demo-output"
    output_root.mkdir(exist_ok=True)
    started = time.perf_counter()
    results: list[dict[str, object]] = []
    for recipe in EXAMPLES:
        scenario_output = output_root / recipe.stem
        result = service.generate(recipe, scenario_output)
        validation = service.validate(scenario_output)
        results.append(
            {
                "recipe": str(recipe.relative_to(ROOT)),
                "output": str(scenario_output.relative_to(ROOT)),
                "checksum": result.checksum,
                "records": validation["records"],
                "personas": validation["personas"],
            }
        )
    elapsed = time.perf_counter() - started
    if os.environ.get("DEMOTENANT_SKIP_BENCHMARK_WRITE") != "1":
        benchmark = ROOT / "docs" / "BENCHMARK.md"
        benchmark.write_text(
            "# Benchmark\n\n"
            "Machine: local development environment used for release validation.\n\n"
            f"Generated {len(EXAMPLES)} scenarios with 100 records each in {elapsed:.3f} seconds.\n\n"
            "```json\n"
            + json.dumps(results, indent=2, sort_keys=True)
            + "\n```\n",
            encoding="utf-8",
        )
    print(json.dumps({"elapsed_seconds": round(elapsed, 3), "results": results}, sort_keys=True))


if __name__ == "__main__":
    main()
