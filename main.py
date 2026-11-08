import argparse
import json
import sys

from extraction.llm import GeminiExtractionError
from extraction.prompt import DOMAIN_GUIDANCE
from run_extract import extract_doc_details


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a medical CV profile as JSON.")
    parser.add_argument("path", nargs="?", default="samples/CvResume-1.pdf")
    parser.add_argument("--professional-group", choices=DOMAIN_GUIDANCE, default="unknown")
    args = parser.parse_args()
    try:
        details = extract_doc_details(args.path, professional_group=args.professional_group)
    except (GeminiExtractionError, ValueError, FileNotFoundError) as exc:
        print(f"Extraction failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(details["candidate_profile"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
