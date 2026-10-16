from pydantic import BaseModel
from typing import List

class CodeBlock(BaseModel):
    language: str  # "java", "python", etc.
    framework: str  # "Spring Boot 3", "React 18", etc.
    code: str
    description: str

class Slide(BaseModel):
    slide_number: int
    title: str
    bullets: List[str]  # Main content points
    code_blocks: List[CodeBlock]  # Optional code examples
    diagram: str  # Optional Mermaid syntax
    trainer_notes: str  # What to say in class
    speaker_notes: str  # Hidden notes in PPTX

class Exercise(BaseModel):
    exercise_id: str
    title: str
    problem_statement: str
    reference_solution: CodeBlock  # Must pass tests
    naive_solution: CodeBlock  # Must fail tests
    test_code: str  # JUnit or similar
    expected_output: str  # What correct output looks like

class QuizQuestion(BaseModel):
    question_id: str
    question_text: str
    options: List[str]
    correct_option_index: int
    explanation: str

class Lesson(BaseModel):
    topic: str
    level: str  # "Beginner", "Intermediate", "Advanced"
    session_length_minutes: int
    framework: str  # "Spring Boot 3", etc.
    slides: List[Slide]
    exercises: List[Exercise]
    quiz: List[QuizQuestion]
    cheat_sheet: str  # Markdown, 1 page

class VerificationResult(BaseModel):
    code_block_id: str
    language: str
    passed: bool
    stdout: str
    stderr: str
    execution_time_seconds: float

class VerificationReport(BaseModel):
    lesson_topic: str
    total_code_blocks: int
    passed: int
    failed: int
    results: List[VerificationResult]
    timestamp: str