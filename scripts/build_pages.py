import json
import os
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site"
OUTPUT = ROOT / "dist"


def main() -> None:
    supabase_url = os.environ.get("SUPABASE_URL", "").strip()
    anon_key = os.environ.get("SUPABASE_ANON_KEY", "").strip()
    if not supabase_url or not anon_key:
        raise SystemExit(
            "SUPABASE_URL and SUPABASE_ANON_KEY are required to build the Pages site."
        )

    if OUTPUT.exists():
        raise SystemExit(
            f"{OUTPUT} already exists. Move or remove that build output before rebuilding."
        )
    shutil.copytree(SOURCE, OUTPUT)
    config = json.dumps(
        {"url": supabase_url, "anonKey": anon_key},
        ensure_ascii=True,
        separators=(",", ":"),
    )
    (OUTPUT / "config.js").write_text(
        f"window.SUPABASE_CONFIG = {config};\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
