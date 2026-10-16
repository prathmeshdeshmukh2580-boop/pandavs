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

class CodeBlock(BaseModel):
    id: str
    lang: str
    version: str
    kind: str
    source: str
    expected_output: Optional[str] = None
    verified: str = "unverified"
    attempts: int = 1
    error_message: Optional[str] = None

class Slide(BaseModel):
    id: str
    type: str
    title: str
    bullets: List[str]
    code: Optional[List[CodeBlock]] = None
    diagram: Optional[str] = None
    notes: str

class ExerciseProof(BaseModel):
    reference_passes: bool
    naive_fails: bool

class Exercise(BaseModel):
    id: str
    title: Optional[str] = "Exercise"
    description: Optional[str] = ""
    starter: str
    tests: str
    reference: str
    naive: str
    proof: ExerciseProof

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: int
    explanation: str

class DeckModel(BaseModel):
    deck_id: str
    topic: str
    level: str
    minutes: int
    stack: Dict[str, str]
    slides: List[Slide]
    exercises: List[Exercise]
    quiz: List[QuizQuestion]
    cheat_sheet: str
