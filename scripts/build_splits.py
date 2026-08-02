"""
Build group-aware train/validation/test splits from dialogue JSONL.
Uses template_family or scenario as the grouping key to prevent leakage.
"""
import json
import random
from collections import defaultdict
from pathlib import Path

import click


@click.command()
@click.option("--input", default="data/dialogues/sample_dialogues.jsonl", help="Input JSONL")
@click.option("--output-dir", default="data/dialogues/v1.0.0", help="Output directory")
@click.option("--group-by", default="scenario", help="Group key: scenario, template_family")
@click.option("--seed", default=42, help="Random seed")
@click.option("--test-ratio", default=0.2, type=float)
@click.option("--val-ratio", default=0.15, type=float)
def main(input, output_dir, group_by, seed, test_ratio, val_ratio):
    random.seed(seed)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input, encoding="utf-8-sig") as f:
        dialogues = [json.loads(line) for line in f if line.strip()]

    groups: dict[str, list[dict]] = defaultdict(list)
    for d in dialogues:
        key = d.get(group_by, d.get("scenario", "UNKNOWN"))
        groups[key].append(d)

    group_names = list(groups.keys())
    random.shuffle(group_names)

    n = len(group_names)
    n_test = max(1, int(n * test_ratio))
    n_val = max(1, int(n * val_ratio))

    test_groups = set(group_names[:n_test])
    val_groups = set(group_names[n_test:n_test + n_val])
    train_groups = set(group_names[n_test + n_val:])

    train_data = [d for g in train_groups for d in groups[g]]
    val_data = [d for g in val_groups for d in groups[g]]
    test_data = [d for g in test_groups for d in groups[g]]

    def write_split(data, filename):
        path = output_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            for d in data:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        print(f"  {filename}: {len(data)} dialogues")

    write_split(train_data, "train.jsonl")
    write_split(val_data, "validation.jsonl")
    write_split(test_data, "test.jsonl")
    write_split(dialogues, "conversations.jsonl")

    manifest = {
        "version": "1.0.0",
        "source": str(input),
        "group_by": group_by,
        "seed": seed,
        "total_dialogues": len(dialogues),
        "train": len(train_data),
        "validation": len(val_data),
        "test": len(test_data),
        "groups": {g: len(v) for g, v in groups.items()},
    }
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest: {manifest_path}")
    print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")


if __name__ == "__main__":
    main()
