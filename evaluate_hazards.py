
import csv
import time
from pathlib import Path

from app.agents.scene_analyst import scene_analyst


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent
IMAGE_DIR = PROJECT_DIR / "data" / "test_images"
OUTPUT_FILE = PROJECT_DIR / "hazard_evaluation.csv"


# Expected hazards for each test image
TEST_CASES = [
    {
        "image": "indian_room_hazards.jpg",
        "expected": ["electrical cables", "clutter", "trip hazard"],
    },
    {
        "image": "kitchen_wet_floor.jpg",
        "expected": ["wet floor", "slip hazard"],
    },
    {
        "image": "bathroom_wet_floor.jpg",
        "expected": ["wet floor", "slip hazard"],
    },
    {
        "image": "living_room_cables.jpg",
        "expected": ["electrical cables", "clutter", "trip hazard"],
    },
    {
        "image": "bedroom_safe.jpg",
        "expected": [],
    },
]


# Synonyms for approximate text-based matching
SYNONYMS = {
    "electrical cables": [
        "electrical cable",
        "electrical cables",
        "electrical cord",
        "electrical cords",
        "power cord",
        "power strip",
        "extension cord",
        "extension cords",
        "electrical wire",
        "electrical wires",
        "loose wires",
    ],
    "clutter": [
        "clutter",
        "scattered",
        "backpack",
        "footwear",
        "loose papers",
        "papers on the floor",
        "objects on the floor",
        "items on the floor",
        "slippers",
    ],
    "trip hazard": [
        "trip hazard",
        "tripping hazard",
        "trip hazards",
        "tripping hazards",
        "walkway obstruction",
        "across the walkway",
        "across the main floor walkway",
        "trip or slip hazard",
    ],
    "wet floor": [
        "wet floor",
        "wet flooring",
        "puddle",
        "puddles",
        "liquid spill",
        "spilled liquid",
        "water spill",
        "wet tile",
        "wet tiles",
    ],
    "slip hazard": [
        "slip hazard",
        "slipping hazard",
        "slip and fall",
        "slippery floor",
        "fall hazard",
    ],
}


def matches_expected(detected_hazards, expected_hazard):
    """Return True if any detected description matches an expected hazard."""
    expected = expected_hazard.lower()
    terms = SYNONYMS.get(expected, [expected])

    return any(
        term in str(hazard).lower()
        for hazard in detected_hazards
        for term in terms
    )


def analyze_image(image_path, retries=3):
    """Analyze an image, retrying temporary API failures."""
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            result = scene_analyst({"image_path": str(image_path)})

            if not isinstance(result, dict):
                return {
                    "setting": "unknown",
                    "hazards": [],
                    "confidence": 0.0,
                    "error": "Invalid response from scene analyst",
                }

            error = result.get("error")

            if error:
                last_error = str(error)
            else:
                hazards = result.get("hazards", [])

                if not isinstance(hazards, list):
                    return {
                        "setting": result.get("setting", "unknown"),
                        "hazards": [],
                        "confidence": result.get("confidence", 0.0),
                        "error": "Invalid hazards format",
                    }

                return {
                    "setting": result.get("setting", "unknown"),
                    "hazards": hazards,
                    "confidence": result.get("confidence", 0.0),
                    "error": "",
                }

        except Exception as exc:
            last_error = str(exc)

        if attempt < retries:
            wait_seconds = attempt * 5
            print(
                f"Attempt {attempt} failed: {last_error}\n"
                f"Retrying in {wait_seconds} seconds..."
            )
            time.sleep(wait_seconds)

    return {
        "setting": "unknown",
        "hazards": [],
        "confidence": 0.0,
        "error": last_error or "Analysis failed",
    }


def main():
    results = []

    total_images = len(TEST_CASES)
    successful = 0
    failed = 0

    print("=" * 65)
    print("HAZARD PRECAUTION ADVISOR - IMAGE EVALUATION")
    print("=" * 65)

    for index, test_case in enumerate(TEST_CASES, start=1):
        filename = test_case["image"]
        expected = test_case["expected"]
        image_path = IMAGE_DIR / filename

        print(f"\n[{index}/{total_images}] Analyzing: {filename}")

        if not image_path.is_file():
            error = f"Image file not found: {image_path}"
            print(f"ERROR: {error}")
            failed += 1

            results.append({
                "image": filename,
                "status": "ERROR",
                "setting": "unknown",
                "detected_hazards": "",
                "expected_hazards": "; ".join(expected),
                "matched_hazards": "",
                "missed_hazards": "",
                "false_positive": "",
                "confidence": 0.0,
                "error": error,
            })
            continue

        result = analyze_image(image_path)

        setting = result["setting"]
        detected = result["hazards"]
        confidence = result["confidence"]
        error = result["error"]

        # Do not score failed API responses as valid detections.
        if error:
            print(f"Analysis failed: {error}")
            failed += 1

            results.append({
                "image": filename,
                "status": "ERROR",
                "setting": setting,
                "detected_hazards": "; ".join(map(str, detected)),
                "expected_hazards": "; ".join(expected),
                "matched_hazards": "",
                "missed_hazards": "",
                "false_positive": "",
                "confidence": confidence,
                "error": error,
            })
            continue

        successful += 1

        matched = [
            item for item in expected
            if matches_expected(detected, item)
        ]

        missed = [
            item for item in expected
            if item not in matched
        ]

        # For the clean bedroom, any reported hazard is a potential
        # false positive that needs manual review.
        false_positive = (
            "YES - review detected hazards"
            if not expected and detected
            else "NO obvious hazards detected"
            if not expected
            else ""
        )

        print(f"Setting: {setting}")
        print(f"Detected hazards: {detected}")
        print(f"Confidence: {confidence}")
        print(f"Expected hazards: {expected}")
        print(f"Matched expected hazards: {matched}")
        print(f"Potentially missed hazards: {missed}")

        if false_positive:
            print(f"Safe-scene check: {false_positive}")

        results.append({
            "image": filename,
            "status": "SUCCESS",
            "setting": setting,
            "detected_hazards": "; ".join(map(str, detected)),
            "expected_hazards": "; ".join(expected),
            "matched_hazards": "; ".join(matched),
            "missed_hazards": "; ".join(missed),
            "false_positive": false_positive,
            "confidence": confidence,
            "error": "",
        })

    # Save every result, including missing images and API errors.
    fieldnames = [
        "image",
        "status",
        "setting",
        "detected_hazards",
        "expected_hazards",
        "matched_hazards",
        "missed_hazards",
        "false_positive",
        "confidence",
        "error",
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 65)
    print("EVALUATION SUMMARY")
    print("=" * 65)
    print(f"Total images: {total_images}")
    print(f"Successful analyses: {successful}")
    print(f"Failed analyses: {failed}")
    print(f"CSV report: {OUTPUT_FILE}")
    print("\nNote: Text matching is approximate. Review detections manually.")


if __name__ == "__main__":
    main()
