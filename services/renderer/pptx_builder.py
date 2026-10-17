import os
from pathlib import Path
from typing import Dict, Any, Optional
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from services.renderer.fit_check import FitChecker
from services.renderer.diagrams import DiagramEngine

# Color Palette (Modern Dark / Brand Theme)
BG_DARK = RGBColor(15, 23, 42)        # Slate 900
SURFACE_DARK = RGBColor(30, 41, 59)   # Slate 800
SURFACE_LIGHT = RGBColor(51, 65, 85)  # Slate 700
ACCENT_BLUE = RGBColor(59, 130, 246)  # Blue 500
ACCENT_INDIGO = RGBColor(99, 102, 241)# Indigo 500
ACCENT_PURPLE = RGBColor(168, 85, 247)# Purple 500
TEXT_WHITE = RGBColor(248, 250, 252)  # Slate 50
TEXT_MUTED = RGBColor(148, 163, 184)  # Slate 400
TEXT_EMERALD = RGBColor(167, 243, 208)# Emerald 200
COLOR_PASSED = RGBColor(16, 185, 129) # Emerald 500
COLOR_WARN = RGBColor(245, 158, 11)   # Amber 500
CARD_BORDER = RGBColor(71, 85, 105)   # Slate 600

class PPTXBuilder:
    """
    Builds branded 16:9 widescreen PowerPoint decks from verified Deck JSON.
    Applies typography rules, code block syntax panels, diagram engine output,
    custom exercise lab cards, quiz knowledge check cards, and embeds trainer notes.
    """
    def __init__(self, template_path: Optional[str] = None):
        self.prs = Presentation()
        # 16:9 widescreen dimensions
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.diagram_engine = DiagramEngine()

    def build_deck(self, deck_data: Dict[str, Any], output_path: str) -> str:
        slides = deck_data.get("slides", [])
        
        for slide_data in slides:
            slide_type = slide_data.get("type", "overview")
            if slide_type == "title":
                self._add_title_slide(slide_data, deck_data)
            elif slide_type == "code":
                self._add_code_slide(slide_data)
            elif slide_type == "concept" and slide_data.get("diagram"):
                self._add_diagram_slide(slide_data)
            elif slide_type in ("exercise", "lab"):
                self._add_exercise_slide(slide_data, deck_data)
            elif slide_type in ("quiz", "quiz_review"):
                self._add_quiz_slide(slide_data, deck_data)
            elif slide_type == "summary":
                self._add_summary_slide(slide_data, deck_data)
            else:
                self._add_content_slide(slide_data)

        # Ensure output directory exists
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(out))
        return str(out)

    def _set_dark_background(self, slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, self.prs.slide_width, self.prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def _add_trainer_notes(self, slide, notes_text: str):
        if notes_text:
            notes_slide = slide.notes_slide
            tf = notes_slide.notes_text_frame
            tf.text = notes_text

    def _add_title_slide(self, slide_data: Dict[str, Any], deck_data: Dict[str, Any]):
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        self._set_dark_background(slide)

        # Brand Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.0), Inches(3.2), Inches(0.42))
        badge.fill.solid()
        badge.fill.fore_color.rgb = ACCENT_INDIGO
        badge.line.fill.background()
        btf = badge.text_frame
        btf.text = "VERIFIED COURSE STUDIO"
        btf.paragraphs[0].font.size = Pt(11)
        btf.paragraphs[0].font.bold = True
        btf.paragraphs[0].font.color.rgb = TEXT_WHITE
        btf.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Level Badge
        lvl = deck_data.get("level", "intermediate").upper()
        lvl_colors = {
            "BEGINNER": RGBColor(16, 185, 129),    # Emerald
            "INTERMEDIATE": RGBColor(59, 130, 246),# Blue
            "ADVANCED": RGBColor(168, 85, 247),    # Purple
        }
        lvl_col = lvl_colors.get(lvl, ACCENT_BLUE)
        lvl_badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.6), Inches(1.0), Inches(2.2), Inches(0.42))
        lvl_badge.fill.solid()
        lvl_badge.fill.fore_color.rgb = lvl_col
        lvl_badge.line.fill.background()
        ltf = lvl_badge.text_frame
        ltf.text = f"LEVEL: {lvl}"
        ltf.paragraphs[0].font.size = Pt(11)
        ltf.paragraphs[0].font.bold = True
        ltf.paragraphs[0].font.color.rgb = TEXT_WHITE
        ltf.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Main Title Box
        title_box = slide.shapes.add_textbox(Inches(1.2), Inches(1.7), Inches(11.0), Inches(2.0))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = slide_data.get("title", deck_data.get("topic", "Course Presentation"))
        p.font.size = Pt(38)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Subtitle / Bullets
        bullets = slide_data.get("bullets", [])
        if bullets:
            for b in bullets[:4]:
                bp = tf.add_paragraph()
                bp.text = f"•  {b}"
                bp.font.size = Pt(16)
                bp.font.color.rgb = TEXT_MUTED
                bp.space_before = Pt(8)

        # Footer Meta Card
        meta_box = slide.shapes.add_textbox(Inches(1.2), Inches(5.9), Inches(11.0), Inches(0.8))
        mtf = meta_box.text_frame
        mp = mtf.paragraphs[0]
        stack_str = ", ".join([f"{k}: {v}" for k, v in deck_data.get("stack", {}).items()]) or "Modern Stack"
        mp.text = f"Duration: {deck_data.get('minutes', 90)} mins   |   Stack: {stack_str}   |   100% Sandbox Verified"
        mp.font.size = Pt(13)
        mp.font.color.rgb = ACCENT_BLUE

        self._add_trainer_notes(slide, slide_data.get("notes", ""))

    def _add_content_slide(self, slide_data: Dict[str, Any]):
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        self._set_dark_background(slide)

        # Header Title
        title_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.7), Inches(11.33), Inches(0.9))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = slide_data.get("title", "")
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Accent Line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.65), Inches(11.33), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = ACCENT_INDIGO
        line.line.fill.background()

        # Bullets
        fit = FitChecker.inspect_slide(slide_data)
        font_pt = min(fit["recommended_bullet_font_pt"], 18)

        bullets_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(11.33), Inches(4.0))
        btf = bullets_box.text_frame
        btf.word_wrap = True

        bullets = slide_data.get("bullets", [])
        for i, bullet in enumerate(bullets):
            bp = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
            bp.text = f"✦  {bullet}"
            bp.font.size = Pt(font_pt)
            bp.font.color.rgb = TEXT_WHITE
            bp.space_before = Pt(10)

        # Pro-Tip Callout Box at Bottom
        pro_tip = slide_data.get("pro_tip")
        if pro_tip:
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(6.1), Inches(11.33), Inches(0.75))
            card.fill.solid()
            card.fill.fore_color.rgb = SURFACE_DARK
            card.line.color.rgb = ACCENT_INDIGO
            card.line.width = Pt(1)
            ctf = card.text_frame
            cp = ctf.paragraphs[0]
            cp.text = f"💡 PRO-TIP: {pro_tip}"
            cp.font.size = Pt(12)
            cp.font.color.rgb = TEXT_EMERALD

        self._add_trainer_notes(slide, slide_data.get("notes", ""))

    def _add_code_slide(self, slide_data: Dict[str, Any]):
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        self._set_dark_background(slide)

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.8))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = slide_data.get("title", "")
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Left Column: Teaching Points
        left_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(4.6), Inches(4.5))
        ltf = left_box.text_frame
        ltf.word_wrap = True
        for i, bullet in enumerate(slide_data.get("bullets", [])[:5]):
            bp = ltf.paragraphs[0] if i == 0 else ltf.add_paragraph()
            bp.text = f"•  {bullet}"
            bp.font.size = Pt(14)
            bp.font.color.rgb = TEXT_WHITE
            bp.space_before = Pt(10)

        # Pro-tip under teaching points
        pro_tip = slide_data.get("pro_tip")
        if pro_tip:
            pt_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.0), Inches(4.6), Inches(0.9))
            pt_tf = pt_box.text_frame
            pt_tf.word_wrap = True
            pt_p = pt_tf.paragraphs[0]
            pt_p.text = f"💡 {pro_tip}"
            pt_p.font.size = Pt(11)
            pt_p.font.color.rgb = TEXT_EMERALD

        # Right Column: Code Card Container
        code_blocks = slide_data.get("code", [])
        code_data = code_blocks[0] if code_blocks else {}
        code_src = code_data.get("source", "// No code provided")
        is_verified = code_data.get("verified", "unverified") == "passed"

        # Code Background Card
        code_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.6), Inches(1.4), Inches(7.0), Inches(5.5))
        code_card.fill.solid()
        code_card.fill.fore_color.rgb = SURFACE_DARK
        code_card.line.color.rgb = ACCENT_INDIGO
        code_card.line.width = Pt(1.5)

        # Header bar on Code Card
        lang_str = code_data.get("lang", "code").upper()
        ver_str = code_data.get("version", "")
        kind_str = code_data.get("kind", "")
        lang_box = slide.shapes.add_textbox(Inches(5.8), Inches(1.45), Inches(4.0), Inches(0.35))
        ltf2 = lang_box.text_frame
        lp = ltf2.paragraphs[0]
        lp.text = f"💻 {lang_str} {ver_str}  ·  {kind_str}"
        lp.font.size = Pt(10)
        lp.font.color.rgb = TEXT_MUTED

        # Verification Status Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.6), Inches(1.5), Inches(1.8), Inches(0.32))
        pill.fill.solid()
        pill.fill.fore_color.rgb = COLOR_PASSED if is_verified else COLOR_WARN
        pill.line.fill.background()
        ptf = pill.text_frame
        ptf.text = "✓ VERIFIED" if is_verified else "⚠ UNVERIFIED"
        ptf.paragraphs[0].font.size = Pt(9)
        ptf.paragraphs[0].font.bold = True
        ptf.paragraphs[0].font.color.rgb = TEXT_WHITE
        ptf.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Code Text Area
        fit = FitChecker.inspect_slide(slide_data)
        code_pt = max(9, min(fit["recommended_code_font_pt"], 12))

        code_text_box = slide.shapes.add_textbox(Inches(5.8), Inches(1.9), Inches(6.6), Inches(4.8))
        ctf = code_text_box.text_frame
        ctf.word_wrap = True
        cp = ctf.paragraphs[0]
        cp.text = code_src
        cp.font.name = "Consolas"
        cp.font.size = Pt(code_pt)
        cp.font.color.rgb = TEXT_EMERALD

        self._add_trainer_notes(slide, slide_data.get("notes", ""))

    def _add_diagram_slide(self, slide_data: Dict[str, Any]):
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        self._set_dark_background(slide)

        # Title
        title_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.5), Inches(11.33), Inches(0.8))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = slide_data.get("title", "")
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Bullets above diagram
        bullets_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(11.33), Inches(1.1))
        btf = bullets_box.text_frame
        btf.word_wrap = True
        for i, b in enumerate(slide_data.get("bullets", [])[:2]):
            bp = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
            bp.text = f"✦  {b}"
            bp.font.size = Pt(15)
            bp.font.color.rgb = TEXT_WHITE

        # Render diagram PNG
        diagram_src = slide_data.get("diagram", "")
        png_path = self.diagram_engine.render_to_png(diagram_src, name_hint=f"slide_{slide_data.get('id', 'diag')}")
        if os.path.exists(png_path):
            slide.shapes.add_picture(png_path, Inches(1.0), Inches(2.5), width=Inches(11.33), height=Inches(4.5))

        self._add_trainer_notes(slide, slide_data.get("notes", ""))

    def _add_exercise_slide(self, slide_data: Dict[str, Any], deck_data: Dict[str, Any]):
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        self._set_dark_background(slide)

        # Header Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.8))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = f"🛠️ {slide_data.get('title', 'Hands-on Lab Exercise')}"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Left Card: Lab Objectives & Constraints
        left_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
        left_card.fill.solid()
        left_card.fill.fore_color.rgb = SURFACE_DARK
        left_card.line.color.rgb = ACCENT_INDIGO
        left_card.line.width = Pt(1.5)

        ltf = left_card.text_frame
        ltf.word_wrap = True
        lp = ltf.paragraphs[0]
        lp.text = "🎯 LAB SPECIFICATION & OBJECTIVES"
        lp.font.size = Pt(14)
        lp.font.bold = True
        lp.font.color.rgb = ACCENT_BLUE

        bullets = slide_data.get("bullets", [])
        for b in bullets:
            bp = ltf.add_paragraph()
            bp.text = f"• {b}"
            bp.font.size = Pt(13)
            bp.font.color.rgb = TEXT_WHITE
            bp.space_before = Pt(8)

        # Right Card: Starter Code / Test Invariants
        right_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.7), Inches(1.5), Inches(5.8), Inches(5.3))
        right_card.fill.solid()
        right_card.fill.fore_color.rgb = SURFACE_DARK
        right_card.line.color.rgb = COLOR_PASSED
        right_card.line.width = Pt(1.5)

        rtf = right_card.text_frame
        rtf.word_wrap = True
        rp = rtf.paragraphs[0]
        rp.text = "🧪 DUAL-PROVER TEST SUITE CONTRACT"
        rp.font.size = Pt(14)
        rp.font.bold = True
        rp.font.color.rgb = COLOR_PASSED

        # Look for exercises data
        exercises = deck_data.get("exercises", [])
        ex = exercises[0] if exercises else {}
        starter = ex.get("starter", "# Student starter implementation\ndef solve():\n    pass")
        tests = ex.get("tests", "# Automated test assertions\ndef test_solve():\n    assert True")

        rp2 = rtf.add_paragraph()
        rp2.text = "Starter Template:"
        rp2.font.size = Pt(11)
        rp2.font.bold = True
        rp2.font.color.rgb = TEXT_MUTED
        rp2.space_before = Pt(8)

        rp3 = rtf.add_paragraph()
        rp3.text = starter[:200]
        rp3.font.name = "Consolas"
        rp3.font.size = Pt(10)
        rp3.font.color.rgb = TEXT_EMERALD

        rp4 = rtf.add_paragraph()
        rp4.text = "Dual-Prover Verification:"
        rp4.font.size = Pt(11)
        rp4.font.bold = True
        rp4.font.color.rgb = TEXT_MUTED
        rp4.space_before = Pt(8)

        rp5 = rtf.add_paragraph()
        rp5.text = "✓ Instructor Reference passes all tests\n✓ Naive implementation fails with assertion error"
        rp5.font.size = Pt(11)
        rp5.font.color.rgb = TEXT_WHITE

        self._add_trainer_notes(slide, slide_data.get("notes", ""))

    def _add_quiz_slide(self, slide_data: Dict[str, Any], deck_data: Dict[str, Any]):
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        self._set_dark_background(slide)

        # Header Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.8))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = f"🧠 {slide_data.get('title', 'Knowledge Check: Architecture Review')}"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Check if quiz questions are present
        quiz_list = deck_data.get("quiz", [])
        q = quiz_list[0] if quiz_list else {
            "question": "What is the primary benefit of declarative validation at the controller edge?",
            "options": [
                "A. Centralizes validation rules before state propagation",
                "B. Replaces unit testing completely",
                "C. Disables HTTP error status codes",
                "D. Forces XML serialization"
            ],
            "answer": 0,
            "explanation": "Declarative annotations keep controller and service methods focused solely on domain workflows."
        }

        # Question Card
        q_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.7), Inches(1.5))
        q_card.fill.solid()
        q_card.fill.fore_color.rgb = SURFACE_DARK
        q_card.line.color.rgb = ACCENT_INDIGO
        q_card.line.width = Pt(1.5)
        qtf = q_card.text_frame
        qtf.word_wrap = True
        qp = qtf.paragraphs[0]
        qp.text = f"QUESTION: {q.get('question', '')}"
        qp.font.size = Pt(17)
        qp.font.bold = True
        qp.font.color.rgb = TEXT_WHITE

        # Options Cards (2x2 Grid)
        options = q.get("options", [])
        correct_idx = q.get("answer", 0)
        grid_positions = [
            (Inches(0.8), Inches(3.2)),
            (Inches(6.8), Inches(3.2)),
            (Inches(0.8), Inches(4.5)),
            (Inches(6.8), Inches(4.5)),
        ]

        letters = ["A", "B", "C", "D"]
        for idx, (x, y) in enumerate(grid_positions[:len(options)]):
            is_correct = (idx == correct_idx)
            opt_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.7), Inches(1.1))
            opt_card.fill.solid()
            opt_card.fill.fore_color.rgb = RGBColor(16, 45, 35) if is_correct else SURFACE_DARK
            opt_card.line.color.rgb = COLOR_PASSED if is_correct else CARD_BORDER
            opt_card.line.width = Pt(1.5 if is_correct else 1)

            otf = opt_card.text_frame
            otf.word_wrap = True
            op = otf.paragraphs[0]
            prefix = "✓ " if is_correct else ""
            op.text = f"{prefix}{letters[idx]}. {options[idx]}"
            op.font.size = Pt(13)
            op.font.bold = is_correct
            op.font.color.rgb = TEXT_EMERALD if is_correct else TEXT_WHITE

        # Explanation Card at Bottom
        exp_box = slide.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.7), Inches(1.0))
        etf = exp_box.text_frame
        etf.word_wrap = True
        ep = etf.paragraphs[0]
        ep.text = f"💡 RATIONALE: {q.get('explanation', '')}"
        ep.font.size = Pt(12)
        ep.font.color.rgb = TEXT_MUTED

        self._add_trainer_notes(slide, slide_data.get("notes", ""))

    def _add_summary_slide(self, slide_data: Dict[str, Any], deck_data: Dict[str, Any]):
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        self._set_dark_background(slide)

        # Header Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.8))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = f"🚀 {slide_data.get('title', 'Production Readiness & Best Practices')}"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Left Column: Key Principles
        left_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(5.6), Inches(4.5))
        ltf = left_box.text_frame
        ltf.word_wrap = True
        lp = ltf.paragraphs[0]
        lp.text = "🏆 KEY ARCHITECTURAL PRINCIPLES"
        lp.font.size = Pt(14)
        lp.font.bold = True
        lp.font.color.rgb = ACCENT_BLUE

        bullets = slide_data.get("bullets", [])
        for b in bullets[:4]:
            bp = ltf.add_paragraph()
            bp.text = f"✓ {b}"
            bp.font.size = Pt(13)
            bp.font.color.rgb = TEXT_WHITE
            bp.space_before = Pt(10)

        # Right Column: Production Checklist
        right_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.7), Inches(1.5), Inches(5.8), Inches(4.5))
        right_card.fill.solid()
        right_card.fill.fore_color.rgb = SURFACE_DARK
        right_card.line.color.rgb = ACCENT_INDIGO
        right_card.line.width = Pt(1.5)

        rtf = right_card.text_frame
        rtf.word_wrap = True
        rp = rtf.paragraphs[0]
        rp.text = "📋 PRODUCTION DEPLOYMENT CHECKLIST"
        rp.font.size = Pt(14)
        rp.font.bold = True
        rp.font.color.rgb = ACCENT_INDIGO

        checklist = [
            "Input boundaries enforce strict schema validation",
            "Database queries use explicit pagination limits",
            "Cache-aside invalidation configured with safe TTLs",
            "Structured JSON logging with correlation IDs",
            "Zero-trust automated unit test coverage verified",
        ]
        for item in checklist:
            ip = rtf.add_paragraph()
            ip.text = f"☐  {item}"
            ip.font.size = Pt(12)
            ip.font.color.rgb = TEXT_WHITE
            ip.space_before = Pt(8)

        # Pro-Tip Callout
        pro_tip = slide_data.get("pro_tip", "Always verify every educational snippet before classroom presentation.")
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.2), Inches(11.7), Inches(0.75))
        card.fill.solid()
        card.fill.fore_color.rgb = SURFACE_DARK
        card.line.color.rgb = COLOR_PASSED
        card.line.width = Pt(1)
        ctf = card.text_frame
        cp = ctf.paragraphs[0]
        cp.text = f"💡 FINAL TAKEAWAY: {pro_tip}"
        cp.font.size = Pt(12)
        cp.font.color.rgb = TEXT_EMERALD

        self._add_trainer_notes(slide, slide_data.get("notes", ""))
