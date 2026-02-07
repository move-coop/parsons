import json
import logging
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCEDIR = ROOT_DIR / "docs"
BUILDDIR = SOURCEDIR / "_build"
LINKCHECKDIR = BUILDDIR / "linkcheck"


def parse_json_lines(file_path: Path) -> Iterator[dict[str, Any]]:
    """Generates dictionaries from a JSON file."""
    with file_path.open(mode="r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            clean_line = line.strip()
            if not clean_line:
                continue
            try:
                yield json.loads(clean_line)
            except json.JSONDecodeError as e:
                logger.warning("Line %s: Invalid JSON. Skipping. Error: %s", line_num, e)


def transform_to_sarif_result(data: dict[str, Any]) -> dict[str, Any]:
    """Transforms a single linkcheck entry into a SARIF result object."""
    status = data.get("status", "").lower()
    raw_filename = data.get("filename", "unknown_file")
    posix_filename = str(Path(raw_filename).as_posix())

    info_text = data.get("info", "")
    error_code = data.get("code")

    detail = f"Status: {status}"
    if error_code:
        detail += f" (Code: {error_code})"
    if info_text:
        clean_info = info_text.split("for url:")[0].strip()
        detail += f" - {clean_info}"

    return {
        "ruleId": "LINK001",
        "level": "error" if status == "broken" else "note",
        "message": {"text": f"🔗 {detail} | URL: {data.get('uri')}"},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": posix_filename},
                    "region": {"startLine": data.get("lineno", 1)},
                }
            }
        ],
    }


def create_sarif_report(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Wraps results into the standard SARIF log structure."""
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "LinkChecker",
                        "rules": [
                            {
                                "id": "LINK001",
                                "shortDescription": {"text": "Broken or invalid link detected."},
                            }
                        ],
                    }
                },
                "results": results,
            }
        ],
    }


def convert_linkcheck_to_sarif(input_file: Path, output_file: Path) -> None:
    """Orchestrates the conversion from linkcheck output to SARIF."""
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    results = []
    logger.info("Processing %s...", input_file)

    try:
        for entry in parse_json_lines(input_file):
            if entry.get("status", "").lower() in ("working", "unchecked"):
                continue

            results.append(transform_to_sarif_result(entry))

        sarif_report = create_sarif_report(results)

        with output_file.open(mode="w", encoding="utf-8") as f:
            json.dump(sarif_report, f, indent=2)

        logger.info("Generated SARIF with %s results: %s", len(results), output_file)

    except (OSError, UnicodeDecodeError) as e:
        logger.error("IO error during conversion: %s", e)
        raise


def main() -> None:
    input_path = LINKCHECKDIR / "output.json"
    output_path = LINKCHECKDIR / "results.sarif"

    try:
        convert_linkcheck_to_sarif(input_path, output_path)
    except FileNotFoundError as e:
        logger.error(e)
        sys.exit(1)
    except (OSError, UnicodeDecodeError) as e:
        logger.error("System error: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.critical("Unexpected error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
