import os
import json
from pathlib import Path
from typing import Dict, Any
from services.renderer.pptx_builder import PPTXBuilder

class Exporter:
    """
    Exports decks to PPTX presentations and generates rich HTML verification reports.
    """
    def __init__(self, export_dir: str):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_pptx(self, deck_data: Dict[str, Any]) -> str:
        deck_id = deck_data.get("deck_id", "deck")
        output_file = self.export_dir / f"{deck_id}.pptx"
        builder = PPTXBuilder()
        builder.build_deck(deck_data, str(output_file))
        return str(output_file)

    def export_html_report(self, report_data: Dict[str, Any], deck_data: Dict[str, Any]) -> str:
        deck_id = report_data.get("deck_id", "deck")
        output_file = self.export_dir / f"{deck_id}_verification_report.html"

        exec_rows = ""
        for item in report_data.get("execution_summary", []):
            status_badge = f'<span class="badge passed">PASSED</span>' if item["status"] == "passed" else f'<span class="badge failed">FAILED</span>'
            cached_badge = '<span class="badge cache">CACHE HIT</span>' if item.get("cached") else '<span class="badge run">SANDBOX RUN</span>'
            exec_rows += f"""
            <tr>
                <td><code>{item.get('snippet_id')}</code></td>
                <td>{item.get('slide_id')}</td>
                <td>{item.get('lang')} {item.get('version')}</td>
                <td>{status_badge}</td>
                <td>{item.get('duration_ms')} ms</td>
                <td>{item.get('attempts', 1)}</td>
                <td>{cached_badge}</td>
            </tr>
            """

        proof_rows = ""
        for ex in report_data.get("exercises_proven", []):
            proof_rows += f"""
            <tr>
                <td><code>{ex.get('exercise_id')}</code></td>
                <td>{ex.get('title')}</td>
                <td><span class="badge passed">✓ TRUE</span></td>
                <td><span class="badge passed">✓ TRUE (Caught)</span></td>
                <td><span class="badge proven">PROVEN</span></td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Verification Report - {deck_data.get('topic')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 32px; border: 1px solid #334155; }}
        h1 {{ color: #38bdf8; margin-top: 0; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }}
        .stat-card {{ background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; }}
        .stat-val {{ font-size: 28px; font-weight: bold; color: #10b981; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th, td {{ text-align: left; padding: 10px 14px; border-bottom: 1px solid #334155; font-size: 14px; }}
        th {{ background: #0f172a; color: #94a3b8; text-transform: uppercase; font-size: 11px; letter-spacing: 0.05em; }}
        .badge {{ padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        .badge.passed {{ background: #064e3b; color: #34d399; }}
        .badge.failed {{ background: #7f1d1d; color: #f87171; }}
        .badge.proven {{ background: #312e81; color: #a5b4fc; }}
        .badge.cache {{ background: #1e3a8a; color: #60a5fa; }}
        .badge.run {{ background: #374151; color: #d1d5db; }}
        code {{ font-family: Consolas, monospace; color: #a7f3d0; background: #0f172a; padding: 2px 6px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Zero-Trust Verification Report</h1>
        <p style="color: #94a3b8;">Deck ID: <code>{deck_data.get('deck_id')}</code> | Topic: <strong>{deck_data.get('topic')}</strong> | Generated: {report_data.get('generated_at')}</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div style="color: #94a3b8; font-size: 12px;">Total Snippets</div>
                <div class="stat-val">{report_data.get('total_snippets', 0)}</div>
            </div>
            <div class="stat-card">
                <div style="color: #94a3b8; font-size: 12px;">Passed Sandbox</div>
                <div class="stat-val">{report_data.get('passed', 0)}</div>
            </div>
            <div class="stat-card">
                <div style="color: #94a3b8; font-size: 12px;">Verification Rate</div>
                <div class="stat-val">{report_data.get('verification_rate_pct', 100)}%</div>
            </div>
            <div class="stat-card">
                <div style="color: #94a3b8; font-size: 12px;">Exercises Proven</div>
                <div class="stat-val">{len(report_data.get('exercises_proven', []))}</div>
            </div>
        </div>

        <h2>Snippet Sandbox Verifications</h2>
        <table>
            <thead>
                <tr>
                    <th>Snippet ID</th>
                    <th>Slide</th>
                    <th>Runtime</th>
                    <th>Status</th>
                    <th>Execution Time</th>
                    <th>Attempts</th>
                    <th>Origin</th>
                </tr>
            </thead>
            <tbody>
                {exec_rows}
            </tbody>
        </table>

        <h2 style="margin-top: 36px;">Exercise Prover Contracts ("Tests Must Bite")</h2>
        <table>
            <thead>
                <tr>
                    <th>Exercise ID</th>
                    <th>Title</th>
                    <th>Reference Solution Passes</th>
                    <th>Naive Buggy Solution Fails</th>
                    <th>Contract Status</th>
                </tr>
            </thead>
            <tbody>
                {proof_rows}
            </tbody>
        </table>
    </div>
</body>
</html>"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        return str(output_file)
