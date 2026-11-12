"""Regressions for generated HTML and SVG code-scanning findings."""

from html import unescape
from xml.etree import ElementTree

from src.diff_analyzer import DiffAnalyzer
from src.venn_diagram_generator import VennDiagramGenerator


def test_diff_html_escapes_untrusted_text_without_changing_source(tmp_path):
    file_a = "a</title><script>alert(1)</script>.json"
    file_b = 'b<img src=x onerror="alert(2)">.json'
    key = "</span><svg onload=alert(3)>"
    value = "</pre><script>alert(4)</script> & retained"
    diff_result = {
        "only_in_a": {key: value},
        "only_in_b": {key: value},
        "common": {key: {"a": value, "b": value}},
        "modified": {key: {"a": value, "b": value}},
    }
    output = tmp_path / "diff.html"

    DiffAnalyzer.export_diff_html(diff_result, file_a, file_b, output)

    exported = output.read_text(encoding="utf-8")
    assert "<script>" not in exported
    assert "<img src=x" not in exported
    assert "<svg onload" not in exported
    assert "&lt;/title&gt;" in exported
    assert "&lt;/span&gt;&lt;svg onload=alert(3)&gt;" in exported
    assert "&lt;/pre&gt;&lt;script&gt;alert(4)&lt;/script&gt; &amp; retained" in exported
    assert unescape(exported).count(value) == 6
    assert diff_result["only_in_a"][key] == value


def test_venn_svg_escapes_untrusted_text_and_remains_well_formed(tmp_path):
    file_a = "a</text><script>alert(1)</script>.json"
    file_b = "b</title><image href=x onerror=alert(2)>.json"
    venn_data = VennDiagramGenerator.generate(
        {
            "only_in_a": {"a": 1},
            "only_in_b": {"b": 2},
            "common": {},
            "modified": {},
        },
        file_a,
        file_b,
    )
    venn_data["summary"] = "</text><script>alert(3)</script>"
    output = tmp_path / "venn.svg"

    VennDiagramGenerator.export_svg(venn_data, output)

    exported = output.read_text(encoding="utf-8")
    assert "<script>" not in exported
    assert "<image href=" not in exported
    assert "&lt;/text&gt;&lt;script&gt;alert(1)&lt;/script&gt;" in exported
    assert "&lt;/title&gt;&lt;image href=x onerror=alert(2)&gt;" in exported
    assert "&lt;/text&gt;&lt;script&gt;alert(3)&lt;/script&gt;" in exported
    root = ElementTree.fromstring(exported)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert not root.findall(".//{http://www.w3.org/2000/svg}script")
