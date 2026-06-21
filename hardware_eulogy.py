#!/usr/bin/env python3
"""
hardware_eulogy: Generate poetic obituaries for retired hardware

USAGE:
  python hardware_eulogy.py --input rig_data.json --output eulogy.md
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


@dataclass
class HardwareRecord:
    """Hardware specification and performance data"""
    model: str
    year_purchased: int
    year_retired: int
    processors: int
    cores_failed: int
    hashes_completed: int
    earnings_rtc: float
    standout_moments: List[str]

    @property
    def total_years(self) -> int:
        return self.year_retired - self.year_purchased

    @property
    def lifespan_days(self) -> int:
        start = datetime(self.year_purchased, 1, 1)
        end = datetime(self.year_retired, 1, 1)
        return (end - start).days or 1  # Avoid division by zero

    def calculate_efficiency(self) -> Dict[str, float]:
        """Calculate key efficiency metrics"""
        return {
            "hashes_per_day": self.hashes_completed / self.lifespan_days,
            "rtc_per_hash": self.earnings_rtc / self.hashes_completed if self.hashes_completed else 0,
            "uptime_percent": (self.processors - self.cores_failed) / self.processors if self.processors else 0
        }


class EulogyGenerator:
    """Generate hardware eulogies with poetic tributes"""

    def __init__(self, hardware: HardwareRecord):
        self.hw = hardware
        self.efficiency = hardware.calculate_efficiency()

    def generate_opening(self) -> str:
        """Opening paragraph with model and service years"""
        return (
            f"# The {self.hw.model}\n\n"
            f"A monument to perseverance: {self.hw.year_purchased}–{self.hw.year_retired}. "
            f"{self.hw.total_years} years of faithful service.\n"
        )

    def generate_body(self) -> str:
        """Main tribute with achievements, challenges, and character"""
        moments_text = "\n".join([f"- {m}" for m in self.hw.standout_moments])

        return f"""
## Service Record

**Hashes Completed:** {self.hw.hashes_completed:,}
**Total Earnings:** {self.hw.earnings_rtc:.4f} RTC
**Peak Rate:** {self.efficiency['hashes_per_day']:,.0f} hashes/day
**Overall Uptime:** {self.efficiency['uptime_percent']*100:.1f}%

## Notable Moments

{moments_text}

## The Challenge

{self.hw.cores_failed} of {self.hw.processors} cores surrendered to the passage of time.
Yet it persisted. This is the measure of character.
"""

    def generate_closing(self) -> str:
        """Closing tribute and ASCII art"""
        return """
## In Memoriam

May this rig's legacy inspire the next generation.
May its hashes be remembered. May its thermal output cool.
Rest well, old friend. You earned your peace.

```
    ╔═══════════════════════════════╗
    ║  R.I.P.  ═  REST IN PIXELS  ═ R.I.P.  ║
    ║                               ║
    ║  Rest In Performance          ║
    ║  Rest In Prosperity           ║
    ╚═══════════════════════════════╝
```
"""

    def generate_full_eulogy(self) -> str:
        """Generate complete eulogy with YAML metadata"""
        opening = self.generate_opening()
        body = self.generate_body()
        closing = self.generate_closing()

        metadata = f"""---
model: {self.hw.model}
years_service: {self.hw.total_years}
total_hashes: {self.hw.hashes_completed}
earnings_rtc: {self.hw.earnings_rtc}
retired_date: {self.hw.year_retired}-01-01
generated_at: {datetime.now().isoformat()}
---

"""

        return metadata + opening + body + closing


def load_hardware_data(path: str) -> HardwareRecord:
    """Load hardware data from JSON file"""
    file_path = Path(path).expanduser()

    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {str(e)}")

    # Extract hardware object
    hw = data.get("hardware", data)

    required = [
        "model",
        "year_purchased",
        "year_retired",
        "processors",
        "cores_failed",
        "hashes_completed",
        "total_earnings_rtc",
        "standout_moments",
    ]

    for field in required:
        if field not in hw:
            raise ValueError(f"Missing required field: {field}")

    return HardwareRecord(
        model=hw["model"],
        year_purchased=int(hw["year_purchased"]),
        year_retired=int(hw["year_retired"]),
        processors=int(hw["processors"]),
        cores_failed=int(hw["cores_failed"]),
        hashes_completed=int(hw["hashes_completed"]),
        earnings_rtc=float(hw["total_earnings_rtc"]),
        standout_moments=hw["standout_moments"]
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate poetic eulogies for retired hardware",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--input", required=True, help="Path to hardware JSON data file")
    parser.add_argument("--output", required=True, help="Output markdown file path")

    args = parser.parse_args()

    try:
        # Load hardware data
        hardware = load_hardware_data(args.input)

        # Generate eulogy
        generator = EulogyGenerator(hardware)
        eulogy = generator.generate_full_eulogy()

        # Write to output file
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(eulogy)

        print(f"✅ Eulogy created: {output_path}", file=sys.stderr)
        return 0

    except FileNotFoundError as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
