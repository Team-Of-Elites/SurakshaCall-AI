"""
Seed/update the trusted directory from seed.json.
Generates organizations.jsonl, official_numbers.jsonl, policies.jsonl.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "trusted_directory"
SEED_PATH = DATA_DIR / "seed.json"


def main():
    if not SEED_PATH.exists():
        print(f"Seed file not found: {SEED_PATH}")
        return

    with open(SEED_PATH, encoding="utf-8-sig") as f:
        orgs = json.load(f)

    orgs_list = []
    numbers_list = []
    policies_list = []
    sources_list = []

    for org in orgs:
        org_id = org.get("canonical_name", "").lower().replace(" ", "_")
        orgs_list.append({
            "organization_id": org_id,
            "canonical_name": org["canonical_name"],
            "organization_type": org.get("organization_type", "UNKNOWN"),
            "aliases": org.get("aliases", []),
            "source_url": org.get("source_url", ""),
            "last_verified_at": org.get("last_verified_at", ""),
        })

        for number in org.get("official_numbers", []):
            numbers_list.append({
                "number_id": f"num_{org_id}_{number}",
                "organization_id": org_id,
                "normalized_number": number,
                "number_type": "TOLL_FREE",
            })

        never_request = org.get("never_request", [])
        if never_request:
            policies_list.append({
                "organization_id": org_id,
                "forbidden_actions": never_request,
                "description": org.get("policy_note", f"{org['canonical_name']} never requests: {', '.join(never_request)}"),
            })

        sources_list.append({
            "source_record_id": f"src_{org_id}",
            "source_url": org.get("source_url", ""),
            "source_organization": org["canonical_name"],
            "verification_method": "manual_official_page_review",
            "verified_at": org.get("last_verified_at", ""),
        })

    def write_jsonl(data, filename):
        path = DATA_DIR / filename
        with open(path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"  {filename}: {len(data)} records")

    write_jsonl(orgs_list, "organizations.jsonl")
    write_jsonl(numbers_list, "official_numbers.jsonl")
    write_jsonl(policies_list, "policies.jsonl")
    write_jsonl(sources_list, "sources.jsonl")
    print(f"\nTrusted directory seeded at {DATA_DIR}")


if __name__ == "__main__":
    main()
