from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class CreateDeckRequest(BaseModel):
    topic: str = Field(..., json_schema_extra={"example": "Spring Boot 3 REST APIs"})
    level: str = Field("beginner", json_schema_extra={"example": "beginner"})
    minutes: int = Field(90, json_schema_extra={"example": 90})
    stack: Dict[str, str] = Field(
        default_factory=lambda: {"java": "21", "spring_boot": "3.3"},
        json_schema_extra={"example": {"java": "21", "spring_boot": "3.3"}}
    )


class VerifyRequest(BaseModel):
    language: str = Field(..., json_schema_extra={"example": "java"})
    version: str = Field("21", json_schema_extra={"example": "21"})
    code: str = Field(..., json_schema_extra={"example": "public class Main{public static void main(String[] a){System.out.println(42);}}"})
    kind: Optional[str] = Field("spring-fragment", json_schema_extra={"example": "spring-fragment"})
    expected_output: Optional[str] = None


class VerifyResponse(BaseModel):
    status: str
    stdout: str
    stderr: str
    duration_ms: float
    cached: bool = False
    returncode: Optional[int] = None


class RegenerateSlideRequest(BaseModel):
    prompt_hint: Optional[str] = Field(None, json_schema_extra={"example": "Add more emphasis on response status codes"})


class UpgradeFrameworkRequest(BaseModel):
    target_stack: Dict[str, str] = Field(..., json_schema_extra={"example": {"spring_boot": "3.3", "java": "21"}})
    source_stack: Optional[Dict[str, str]] = None


# ---------- Deck sub-models (aligned with deck.schema.json) ----------

class CodeBlock(BaseModel):
    """Matches $defs/code_block in deck.schema.json."""
    id: str
    lang: str
    version: str
    kind: str = "plain"
    source: str
    expected_output: Optional[str] = None
    verified: str = "unverified"
    attempts: int = 0


class Diagram(BaseModel):
    """Matches $defs/diagram in deck.schema.json."""
    id: str
    kind: str = "mermaid"
    source: str


class Slide(BaseModel):
    """Matches $defs/slide in deck.schema.json."""
    id: str
    type: str
    title: str
    bullets: List[str] = []
    code: List[CodeBlock] = []
    diagram: Optional[Diagram] = None
    notes: str = ""


class ExerciseProof(BaseModel):
    """Matches exercise.proof in deck.schema.json."""
    reference_passes: Optional[bool] = None
    naive_fails: Optional[bool] = None


class Exercise(BaseModel):
    """Matches $defs/exercise in deck.schema.json."""
    id: str
    title: str
    lang: str
    version: str
    prompt: str
    starter: str = ""
    tests: str
    reference: str
    naive: str
    proof: ExerciseProof = Field(default_factory=ExerciseProof)


class QuizItem(BaseModel):
    """Matches $defs/quiz_item in deck.schema.json."""
    id: str
    question: str
    options: List[str]
    answer_index: int
    explanation: str = ""


class DeckModel(BaseModel):
    """Top-level deck model matching deck.schema.json."""
    deck_id: str
    topic: str
    level: str
    minutes: int
    stack: Dict[str, str] = {}
    slides: List[Slide] = []
    exercises: List[Exercise] = []
    quiz: List[QuizItem] = []
    cheat_sheet: str = ""
    meta: Optional[Dict[str, Any]] = None


# ---------- Self-Healing Theater Models ----------

class StartSelfHealRequest(BaseModel):
    example_id: Optional[str] = Field("python_add", json_schema_extra={"example": "python_add"})


class AddToDeckRequest(BaseModel):
    deck_id: Optional[str] = Field(None, json_schema_extra={"example": "d_001"})
