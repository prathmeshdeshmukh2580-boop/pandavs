import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

class DiagramEngine:
    """
    Renders Mermaid or architectural diagrams to PNG images for embedding into slides.
    Supports mmdc (Mermaid CLI) when available, and falls back to a high-quality native
    Pillow vector-box renderer.
    """
    def __init__(self, output_dir: Optional[str] = None):
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).resolve().parent.parent.parent / "data" / "diagrams"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.mmdc_path = shutil.which("mmdc")

    def render_to_png(self, diagram_src: str, name_hint: str = "diagram") -> str:
        """
        Renders diagram source to a PNG file and returns the absolute file path.
        """
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name_hint)
        output_path = self.output_dir / f"{clean_name}.png"

        # Try Mermaid CLI if available
        if self.mmdc_path:
            try:
                with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False) as f:
                    f.write(diagram_src)
                    f_name = f.name
                cmd = [self.mmdc_path, "-i", f_name, "-o", str(output_path), "-b", "transparent", "-w", "1200"]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
                os.remove(f_name)
                if res.returncode == 0 and output_path.exists():
                    return str(output_path)
            except Exception:
                pass

        # Fallback native Pillow diagram renderer
        self._render_pillow_diagram(diagram_src, str(output_path))
        return str(output_path)

    def _render_pillow_diagram(self, src: str, output_path: str) -> None:
        """
        Draws a clean modern architecture diagram from diagram text or Mermaid flow.
        """
        # Parse basic node labels from src
        labels = []
        for line in src.splitlines():
            line = line.strip()
            if not line or line.startswith("graph ") or line.startswith("flowchart "):
                continue
            # match [Label]
            matches = re.findall(r'\[(.*?)\]', line)
            for m in matches:
                clean_m = m.replace('"', '').strip()
                if clean_m and clean_m not in labels:
                    labels.append(clean_m)

        if not labels:
            labels = ["Client Request", "FastAPI Orchestrator", "Docker Sandbox", "Verified PPTX Output"]

        # Canvas Dimensions
        width = 1000
        height = 360
        img = Image.new("RGBA", (width, height), (15, 23, 42, 255)) # Dark slate bg
        draw = ImageDraw.Draw(img)

        # Draw Title
        draw.text((40, 25), "ARCHITECTURE WORKFLOW", fill=(148, 163, 184, 255))

        # Layout horizontal sequence of boxes
        num_boxes = len(labels[:4])
        box_width = 190
        box_height = 90
        total_boxes_w = num_boxes * box_width
        gap = (width - 100 - total_boxes_w) // max(1, num_boxes - 1)
        start_x = 50
        y = 120

        colors = [
            ((99, 102, 241), (224, 231, 255)),  # Indigo
            ((16, 185, 129), (209, 250, 229)),  # Emerald
            ((14, 165, 233), (224, 242, 254)),  # Sky
            ((168, 85, 247), (243, 232, 255)),  # Purple
        ]

        for i, label in enumerate(labels[:4]):
            bx = start_x + i * (box_width + gap)
            border_col, text_col = colors[i % len(colors)]
            
            # Box shadow / background
            draw.rounded_rectangle([bx, y, bx + box_width, y + box_height], radius=10, fill=(30, 41, 59, 255), outline=border_col, width=2)
            
            # Box pill header
            draw.rounded_rectangle([bx + 10, y + 10, bx + 70, y + 26], radius=4, fill=border_col)
            draw.text((bx + 18, y + 12), f"STEP {i+1}", fill=(255, 255, 255, 255))

            # Box Label text (wrapped if needed)
            words = label.split()
            line1 = " ".join(words[:2]) if len(words) > 2 else label
            line2 = " ".join(words[2:]) if len(words) > 2 else ""

            draw.text((bx + 14, y + 36), line1, fill=text_col)
            if line2:
                draw.text((bx + 14, y + 56), line2, fill=text_col)

            # Draw arrow to next box
            if i < num_boxes - 1:
                arrow_start = bx + box_width + 8
                arrow_end = arrow_start + gap - 16
                arrow_y = y + (box_height // 2)
                draw.line([(arrow_start, arrow_y), (arrow_end, arrow_y)], fill=(100, 116, 139, 255), width=3)
                # Arrow head
                draw.polygon([
                    (arrow_end, arrow_y),
                    (arrow_end - 8, arrow_y - 6),
                    (arrow_end - 8, arrow_y + 6)
                ], fill=(100, 116, 139, 255))

        img.save(output_path, "PNG")
