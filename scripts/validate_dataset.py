"""
Validate LIMBA instruction-tuning datasets in JSONL format.

The validator checks:

- valid JSON on every non-empty line;
- required fields;
- expected data types;
- empty instructions or responses;
- duplicate instruction-response pairs;
- unexpected fields.

Example:
    python scripts/validate_dataset.py data/sample_dataset.jsonl
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {"instruction", "context", "response"}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a LIMBA JSONL instruction dataset."
    )
    parser.add_argument(
        "dataset",
        type=Path,
        help="Path to the JSONL dataset.",
    )
    return parser.parse_args()


def validate_record(
    record: Any,
    line_number: int,
    seen_pairs: set[tuple[str, str]],
) -> list[str]:
    """Return validation errors found in a single dataset record."""

    errors: list[str] = []

    if not isinstance(record, dict):
        return [f"Line {line_number}: record must be a JSON object."]

    fields = set(record.keys())

    missing_fields = REQUIRED_FIELDS - fields
    if missing_fields:
        errors.append(
            f"Line {line_number}: missing fields: "
            f"{', '.join(sorted(missing_fields))}."
        )

    unexpected_fields = fields - REQUIRED_FIELDS
    if unexpected_fields:
        errors.append(
            f"Line {line_number}: unexpected fields: "
            f"{', '.join(sorted(unexpected_fields))}."
        )

    for field in REQUIRED_FIELDS:
        if field in record and not isinstance(record[field], str):
            errors.append(
                f"Line {line_number}: '{field}' must be a string."
            )

    instruction = record.get("instruction", "")
    context = record.get("context", "")
    response = record.get("response", "")

    if isinstance(instruction, str) and not instruction.strip():
        errors.append(
            f"Line {line_number}: 'instruction' cannot be empty."
        )

    if isinstance(response, str) and not response.strip():
        errors.append(
            f"Line {line_number}: 'response' cannot be empty."
        )

    if isinstance(context, str) and context != context.strip():
        errors.append(
            f"Line {line_number}: 'context' contains leading or trailing spaces."
        )

    if isinstance(instruction, str) and isinstance(response, str):
        pair = (instruction.strip(), response.strip())

        if pair in seen_pairs:
            errors.append(
                f"Line {line_number}: duplicate instruction-response pair."
            )
        else:
            seen_pairs.add(pair)

    return errors


def validate_dataset(dataset_path: Path) -> tuple[int, list[str]]:
    """Validate the dataset and return record count and errors."""

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}"
        )

    if not dataset_path.is_file():
        raise ValueError(
            f"Path is not a file: {dataset_path}"
        )

    record_count = 0
    errors: list[str] = []
    seen_pairs: set[tuple[str, str]] = set()

    with dataset_path.open("r", encoding="utf-8") as dataset:
        for line_number, line in enumerate(dataset, start=1):
            if not line.strip():
                continue

            record_count += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"Line {line_number}: invalid JSON "
                    f"({exc.msg}, column {exc.colno})."
                )
                continue

            errors.extend(
                validate_record(
                    record=record,
                    line_number=line_number,
                    seen_pairs=seen_pairs,
                )
            )

    return record_count, errors


def main() -> None:
    args = parse_arguments()

    try:
        record_count, errors = validate_dataset(args.dataset)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Records checked: {record_count}")

    if errors:
        print(f"Validation errors: {len(errors)}")

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("Dataset validation completed successfully.")


if __name__ == "__main__":
    main()
