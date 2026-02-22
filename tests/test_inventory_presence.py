import os
from pathlib import Path


def test_inventory_present_and_has_sections():
    root = Path(__file__).resolve().parents[1]
    inv = root / "INVENTORY.md"
    assert inv.exists(), "INVENTORY.md must exist at repository root"
    text = inv.read_text(encoding="utf-8")
    assert "## Folders" in text or "## Files" in text, "INVENTORY.md must include ## Folders or ## Files sections"


def test_inventory_in_subfolders():
    # every first-level folder should have its own INVENTORY.md
    root = Path(__file__).resolve().parents[1]
    for child in root.iterdir():
        if child.is_dir() and not child.name.startswith('.') and not child.name.endswith('.egg-info'):
            inv = child / "INVENTORY.md"
            # allow empty directories that may not need inventories
            assert inv.exists(), f"{child} missing INVENTORY.md"
