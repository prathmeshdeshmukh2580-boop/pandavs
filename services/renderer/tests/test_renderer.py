import os
import json
import pytest
from services.renderer.fit_check import FitChecker
from services.renderer.diagrams import DiagramEngine
from services.renderer.pptx_builder import PPTXBuilder
from services.renderer.exporter import Exporter

def test_fit_checker():
    clean_slide = {
        "id": "s_01",
        "bullets": ["Point 1", "Point 2", "Point 3"],
        "code": [{"id": "c_01", "source": "print(1)\nprint(2)"}]
    }
    res = FitChecker.inspect_slide(clean_slide)
    assert res["fits"] is True
    assert len(res["warnings"]) == 0

    overflow_slide = {
        "id": "s_02",
        "bullets": [f"Point {i}" for i in range(10)],
        "code": [{"id": "c_02", "source": "\n".join([f"line {i}" for i in range(25)])}]
    }
    res_overflow = FitChecker.inspect_slide(overflow_slide)
    assert res_overflow["fits"] is False
    assert len(res_overflow["warnings"]) >= 2
    assert res_overflow["recommended_code_font_pt"] == 10

def test_diagram_engine(tmp_path):
    engine = DiagramEngine(output_dir=str(tmp_path))
    sample_diagram = """
    graph LR
      Client --> Gateway
      Gateway --> Service
    """
    png = engine.render_to_png(sample_diagram, name_hint="test_flow")
    assert os.path.exists(png)
    assert os.path.getsize(png) > 0

def test_pptx_builder_and_exporter(tmp_path):
    sample_deck_file = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "samples", "spring_boot_deck.json"
    )
    with open(sample_deck_file, "r") as f:
        deck_data = json.load(f)

    exporter = Exporter(export_dir=str(tmp_path))
    pptx_path = exporter.export_pptx(deck_data)
    assert os.path.exists(pptx_path)
    assert os.path.getsize(pptx_path) > 1000

    report_path = exporter.export_html_report({
        "deck_id": "d_001",
        "generated_at": "2026-10-16",
        "total_snippets": 3,
        "passed": 3,
        "verification_rate_pct": 100,
        "execution_summary": [],
        "exercises_proven": []
    }, deck_data)
    assert os.path.exists(report_path)
    assert os.path.getsize(report_path) > 200
