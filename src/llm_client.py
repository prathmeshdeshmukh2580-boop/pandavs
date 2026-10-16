import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from schema import Lesson

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_model():
    """Get Gemini model (2.0-flash is free, fast, and good for JSON)"""
    return genai.GenerativeModel(
        model_name=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,  # Balance between creativity and consistency
            top_p=0.9,
            top_k=40,
        )
    )

def call_llm(prompt: str, system_prompt: str = "") -> str:
    """
    Call Gemini with a prompt and get back the response.
    
    Args:
        prompt: What you ask Gemini
        system_prompt: The "instructions" for Gemini
    
    Returns:
        Gemini's response as text
    """
    model = get_model()
    
    # Combine system prompt and user prompt
    full_prompt = system_prompt + "\n\n" + prompt if system_prompt else prompt
    
    print(f"   💬 Sending request to Gemini...", end="", flush=True)
    
    try:
        response = model.generate_content(full_prompt)
        text = response.text
        
        print(f" ✓")
        return text
        
    except Exception as e:
        print(f" ✗ Error: {e}")
        raise


def generate_lesson(topic: str, level: str, length_minutes: int) -> Lesson:
    """
    Generate a complete lesson by asking Gemini.
    
    Args:
        topic: What to teach (e.g., "Spring Boot REST APIs")
        level: Difficulty (e.g., "Beginner")
        length_minutes: How long (e.g., 90)
    
    Returns:
        A Lesson object (structured JSON)
    """
    from prompts import SYSTEM_PROMPT_LESSON_GENERATOR
    
    # Build the prompt (what we ask Gemini)
    prompt = f"""
    Generate a lesson plan for:
    Topic: {topic}
    Level: {level}
    Duration: {length_minutes} minutes
    Framework: Spring Boot 3.1
    
    Include:
    - 5-7 slides with code examples
    - 2-3 exercises with reference and naive solutions
    - 5 quiz questions with explanations
    - 1 page cheat sheet
    
    Respond ONLY with JSON, no other text.
    """
    
    print(f"\n📝 Asking Gemini to generate a lesson...")
    print(f"   Topic: {topic}")
    print(f"   Level: {level}")
    print(f"   Duration: {length_minutes} min")
    
    # Call Gemini
    response_text = call_llm(prompt, SYSTEM_PROMPT_LESSON_GENERATOR)
    
    print(f"✓ Gemini responded ({len(response_text)} characters)")
    
    # Parse the JSON response
    try:
        # Sometimes Gemini wraps JSON in markdown code blocks, so clean it
        if response_text.startswith("```"):
            # Remove markdown code blocks
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        json_data = json.loads(response_text)
        lesson = Lesson(**json_data)
        print(f"✓ Generated lesson with {len(lesson.slides)} slides, {len(lesson.exercises)} exercises")
        return lesson
        
    except json.JSONDecodeError as e:
        print(f"✗ ERROR: Gemini's response wasn't valid JSON")
        print(f"   Error: {e}")
        print(f"   First 200 chars: {response_text[:200]}")
        raise
    except Exception as e:
        print(f"✗ ERROR: {e}")
        raise


def fix_broken_code(code: str, error_message: str, language: str) -> str:
    """
    Ask Gemini to fix broken code.
    
    Args:
        code: The broken code
        error_message: The error message
        language: Programming language (e.g., "java")
    
    Returns:
        Fixed code
    """
    from prompts import SYSTEM_PROMPT_FIX_CODE
    
    prompt = f"""
    Language: {language}
    
    BROKEN CODE:
    {code}
    
    ERROR MESSAGE:
    {error_message}
    
    Fix the code to make it work.
    """
    
    print(f"   🔧 Asking Gemini to fix code...", end="", flush=True)
    
    fixed_code = call_llm(prompt, SYSTEM_PROMPT_FIX_CODE)
    
    print(f" ✓")
    
    return fixed_code


# TEST: Run this to see if it works
if __name__ == "__main__":
    try:
        # Test 1: Can we call Gemini?
        print("\n=== TEST 1: Calling Gemini ===")
        response = call_llm("Say 'Hello' in one word")
        print(f"Gemini said: {response}")
        
        # Test 2: Can we generate a lesson?
        print("\n=== TEST 2: Generating a lesson ===")
        lesson = generate_lesson(
            topic="Spring Boot REST APIs",
            level="Beginner",
            length_minutes=90
        )
        print(f"Generated lesson with {len(lesson.slides)} slides!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nMake sure:")
        print("  1. You have a .env file with GEMINI_API_KEY")
        print("  2. The API key is valid (from https://ai.google.dev/)")
        print("  3. You have installed: pip install google-generativeai python-dotenv pydantic")
def generate_lesson_with_retry(topic: str, level: str, length_minutes: int, max_retries: int = 3) -> Lesson:
    """
    Generate a lesson, retry if JSON parsing fails.
    
    Args:
        topic: What to teach
        level: Difficulty
        length_minutes: How long
        max_retries: How many times to try (default 3)
    
    Returns:
        A Lesson object
    """
    from prompts import SYSTEM_PROMPT_LESSON_GENERATOR
    
    for attempt in range(max_retries):
        try:
            print(f"\n📝 Attempt {attempt + 1}/{max_retries}")
            
            prompt = f"""
            Generate a lesson plan for:
            Topic: {topic}
            Level: {level}
            Duration: {length_minutes} minutes
            Framework: Spring Boot 3.1
            
            Include:
            - 5-7 slides with code examples
            - 2-3 exercises with reference and naive solutions
            - 5 quiz questions with explanations
            - 1 page cheat sheet
            
            Respond ONLY with valid JSON, no markdown, no explanation.
            """
            
            response_text = call_llm(prompt, SYSTEM_PROMPT_LESSON_GENERATOR)
            
            # Clean markdown if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            json_data = json.loads(response_text)
            lesson = Lesson(**json_data)
            
            print(f"✓ Success!")
            return lesson
            
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print(f"   ✗ JSON parsing failed: {str(e)[:80]}")
                print(f"   🔄 Retrying...")
            else:
                print(f"   ✗ Failed after {max_retries} attempts")
                raise
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"   ✗ Error: {str(e)[:80]}")
                print(f"   🔄 Retrying...")
            else:
                print(f"   ✗ Failed after {max_retries} attempts")
                raise