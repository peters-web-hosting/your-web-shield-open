import json

from db import fetch_records


if __name__ == "__main__":
    records = fetch_records()
    with open("export.json", "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2, default=str)
    print(f"Exported {len(records)} community records")
