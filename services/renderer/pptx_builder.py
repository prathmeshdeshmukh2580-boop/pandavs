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
BG_DARK = RGBColor(15, 23, 42)       # Slate 900
SURFACE_DARK = RGBColor(30, 41, 59)  # Slate 800
ACCENT_BLUE = RGBColor(59, 130, 246) # Blue 500
ACCENT_INDIGO = RGBColor(99, 102, 241)# Indigo 500
TEXT_WHITE = RGBColor(248, 250, 252) # Slate 50
TEXT_MUTED = RGBColor(148, 163, 184) # Slate 400
CODE_BG = RGBColor(15, 23, 42)       # Slate 950
COLOR_PASSED = RGBColor(16, 185, 129)# Emerald 500
COLOR_WARN = RGBColor(245, 158, 11)  # Amber 500

class PPTXBuilder:
    """
    Builds branded 16:9 widescreen PowerPoint decks from verified Deck JSON.
    Applies typography rules, code block syntax panels, diagram engine output,
    and embeds trainer notes directly into PPTX speaker notes.
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
            else:
                self._add_content_slide(slide_data)

        # Ensure output directory exists
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(out))
        return str(out)

    def _set_dark_background(self, slide):
        # Create full bleed background rectangle
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
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.2), Inches(3.2), Inches(0.45))
        badge.fill.solid()
        badge.fill.fore_color.rgb = ACCENT_INDIGO
        badge.line.fill.background()
        btf = badge.text_frame
        btf.text = "VERIFIED COURSE STUDIO"
        btf.paragraphs[0].font.size = Pt(11)
        btf.paragraphs[0].font.bold = True
        btf.paragraphs[0].font.color.rgb = TEXT_WHITE
        btf.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Main Title Box
        title_box = slide.shapes.add_textbox(Inches(1.2), Inches(1.9), Inches(11.0), Inches(2.2))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = slide_data.get("title", deck_data.get("topic", "Course Presentation"))
        p.font.size = Pt(40)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Subtitle / Bullets
        bullets = slide_data.get("bullets", [])
        if bullets:
            for b in bullets:
                bp = tf.add_paragraph()
                bp.text = f"•  {b}"
                bp.font.size = Pt(18)
                bp.font.color.rgb = TEXT_MUTED

        # Footer Meta (Stack, Duration, Level)
        meta_box = slide.shapes.add_textbox(Inches(1.2), Inches(5.8), Inches(11.0), Inches(0.8))
        mtf = meta_box.text_frame
        mp = mtf.paragraphs[0]
        stack_str = ", ".join([f"{k}: {v}" for k, v in deck_data.get("stack", {}).items()]) or "Java 21, Spring Boot 3"
        mp.text = f"Audience: {deck_data.get('level', 'Beginner').capitalize()}  |  Duration: {deck_data.get('minutes', 90)} mins  |  Stack: {stack_str}"
        mp.font.size = Pt(13)
        mp.font.color.rgb = ACCENT_BLUE

        self._add_trainer_notes(slide, slide_data.get("notes", ""))

    def _add_content_slide(self, slide_data: Dict[str, Any]):
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        self._set_dark_background(slide)

        # Header Title
        title_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.33), Inches(1.0))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = slide_data.get("title", "")
        p.font.size = Pt(30)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Accent Line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.85), Inches(11.33), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = ACCENT_INDIGO
        line.line.fill.background()

        # Bullets
        fit = FitChecker.inspect_slide(slide_data)
        font_pt = fit["recommended_bullet_font_pt"]

        bullets_box = slide.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.9), Inches(4.5))
        btf = bullets_box.text_frame
        btf.word_wrap = True

        bullets = slide_data.get("bullets", [])
        for i, bullet in enumerate(bullets):
            bp = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
            bp.text = f"✦  {bullet}"
            bp.font.size = Pt(font_pt)
            bp.font.color.rgb = TEXT_WHITE
            bp.space_before = Pt(14)

        self._add_trainer_notes(slide, slide_data.get("notes", ""))

    def _add_code_slide(self, slide_data: Dict[str, Any]):
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        self._set_dark_background(slide)

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.9))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = slide_data.get("title", "")
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Left Column: Teaching Points
        left_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.2))
        ltf = left_box.text_frame
        ltf.word_wrap = True
        for i, bullet in enumerate(slide_data.get("bullets", [])):
            bp = ltf.paragraphs[0] if i == 0 else ltf.add_paragraph()
            bp.text = f"•  {bullet}"
            bp.font.size = Pt(15)
            bp.font.color.rgb = TEXT_WHITE
            bp.space_before = Pt(12)

        # Right Column: Code Card Container
        code_blocks = slide_data.get("code", [])
        code_data = code_blocks[0] if code_blocks else {}
        code_src = code_data.get("source", "// No code provided")
        is_verified = code_data.get("verified", "unverified") == "passed"

        # Code Background Card
        code_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.6), Inches(1.6), Inches(6.9), Inches(5.2))
        code_card.fill.solid()
        code_card.fill.fore_color.rgb = SURFACE_DARK
        code_card.line.color.rgb = ACCENT_INDIGO
        code_card.line.width = Pt(1.5)

        # Verification Status Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.2), Inches(1.8), Inches(2.1), Inches(0.35))
        pill.fill.solid()
        pill.fill.fore_color.rgb = COLOR_PASSED if is_verified else COLOR_WARN
        pill.line.fill.background()
        ptf = pill.text_frame
        ptf.text = "✓ VERIFIED" if is_verified else "⚠ UNVERIFIED"
        ptf.paragraphs[0].font.size = Pt(10)
        ptf.paragraphs[0].font.bold = True
        ptf.paragraphs[0].font.color.rgb = TEXT_WHITE
        ptf.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Code Text Area
        fit = FitChecker.inspect_slide(slide_data)
        code_pt = fit["recommended_code_font_pt"]

        code_text_box = slide.shapes.add_textbox(Inches(5.8), Inches(2.2), Inches(6.5), Inches(4.4))
        ctf = code_text_box.text_frame
        ctf.word_wrap = True
        cp = ctf.paragraphs[0]
        cp.text = code_src
        cp.font.name = "Consolas"
        cp.font.size = Pt(code_pt)
        cp.font.color.rgb = RGBColor(167, 243, 208)  # Emerald 200 monospace

        self._add_trainer_notes(slide, slide_data.get("notes", ""))

    def _add_diagram_slide(self, slide_data: Dict[str, Any]):
        blank_layout = self.prs.slide_layouts[6]
        slide = self.prs.slides.add_slide(blank_layout)
        self._set_dark_background(slide)

        # Title
        title_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.6), Inches(11.33), Inches(0.9))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = slide_data.get("title", "")
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

        # Bullets above diagram
        bullets_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.33), Inches(1.2))
        btf = bullets_box.text_frame
        btf.word_wrap = True
        for i, b in enumerate(slide_data.get("bullets", [])[:2]):
            bp = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
            bp.text = f"✦  {b}"
            bp.font.size = Pt(16)
            bp.font.color.rgb = TEXT_WHITE

        # Render diagram PNG
        diagram_src = slide_data.get("diagram", "")
        png_path = self.diagram_engine.render_to_png(diagram_src, name_hint=f"slide_{slide_data.get('id', 'diag')}")
        if os.path.exists(png_path):
            slide.shapes.add_picture(png_path, Inches(1.0), Inches(2.8), width=Inches(11.33), height=Inches(4.1))

        self._add_trainer_notes(slide, slide_data.get("notes", ""))
