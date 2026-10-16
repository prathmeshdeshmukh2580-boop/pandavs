from typing import Dict, Any, List

class FitChecker:
    """
    Validates and adjusts slide text density according to studio rules:
    - Bullets: max ~5 per slide, ~12 words each
    - Code: max ~14 lines per slide
    - Adjusts font sizing dynamically to prevent slide overflow.
    """
    MAX_BULLETS = 6
    MAX_WORDS_PER_BULLET = 16
    MAX_CODE_LINES = 16

    @classmethod
    def inspect_slide(cls, slide_data: Dict[str, Any]) -> Dict[str, Any]:
        warnings = []
        bullets = slide_data.get("bullets", [])
        code_blocks = slide_data.get("code", [])

        # Check bullets
        if len(bullets) > cls.MAX_BULLETS:
            warnings.append(f"Too many bullets ({len(bullets)} > {cls.MAX_BULLETS}). Recommend splitting slide.")
        
        for idx, bullet in enumerate(bullets):
            word_count = len(bullet.split())
            if word_count > cls.MAX_WORDS_PER_BULLET:
                warnings.append(f"Bullet {idx+1} is verbose ({word_count} words > {cls.MAX_WORDS_PER_BULLET}).")

        # Check code lines
        code_font_size = 13
        for block in code_blocks:
            lines = block.get("source", "").splitlines()
            if len(lines) > cls.MAX_CODE_LINES:
                warnings.append(f"Code block '{block.get('id')}' has {len(lines)} lines (exceeds {cls.MAX_CODE_LINES}). Font scaled down.")
                code_font_size = 10
            elif len(lines) > 10:
                code_font_size = 11

        return {
            "slide_id": slide_data.get("id"),
            "fits": len(warnings) == 0,
            "warnings": warnings,
            "recommended_code_font_pt": code_font_size,
            "recommended_bullet_font_pt": 18 if len(bullets) <= 4 else 15
        }
