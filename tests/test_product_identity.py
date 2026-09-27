"""Tests for active Clarify Toolkit identity surfaces."""

import json
from pathlib import Path

from src.product_identity import EDITOR_NAME, PRODUCT_NAME


def test_public_name_and_editor_name_are_distinct():
    assert PRODUCT_NAME == "Clarify Toolkit"
    assert EDITOR_NAME == "Clarify Editor"


def test_all_window_titles_use_public_product_name():
    catalogs = Path("src/i18n").glob("*.json")
    titles = [json.loads(path.read_text(encoding="utf-8"))["app.title"] for path in catalogs]

    assert len(titles) == 7
    assert all(title.startswith(PRODUCT_NAME) for title in titles)


def test_packaged_icon_assets_exist():
    icon_directory = Path("assets/icons")
    expected = {
        "icon.svg",
        "icon.png",
        "icon-32.png",
        "icon-64.png",
        "icon-128.png",
        "icon-512.png",
        "favicon.ico",
    }

    assert expected <= {path.name for path in icon_directory.iterdir() if path.is_file()}
