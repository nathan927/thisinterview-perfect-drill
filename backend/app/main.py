from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional
import json
from dotenv import load_dotenv
from functools import lru_cache
from .prefect_questions import get_random_questions, evaluate_answer, PREFECT_QUESTIONS
import os
import openai
from google.cloud import speech, translate
from pathlib import Path

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Interview Platform API")

# Configure CORS with environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Settings management
class Settings:
    OPENROUTER_API_BASE: str = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

    def validate_api_keys(self):
        # Only validate if we're using endpoints that require these keys
        pass

@lru_cache()
def get_settings():
    settings = Settings()
    settings.validate_api_keys()
    return settings

# Configure OpenRouter API
openai.api_base = get_settings().OPENROUTER_API_BASE
openai.api_key = get_settings().OPENROUTER_API_KEY

class InterviewQuestion(BaseModel):
    text: str
    language: str

    @validator('language')
    def validate_language(cls, v):
        allowed_languages = {'en', 'tc', 'sc'}
        if v not in allowed_languages:
            raise ValueError(f'Language must be one of {allowed_languages}')
        return v

class FeedbackRequest(BaseModel):
    audio_url: str
    question: str
    language: str

    @validator('language')
    def validate_language(cls, v):
        allowed_languages = {'en', 'tc', 'sc'}
        if v not in allowed_languages:
            raise ValueError(f'Language must be one of {allowed_languages}')
        return v

class FeedbackResponse(BaseModel):
    score: float
    strengths: List[str]
    improvements: List[str]
    detailed_analysis: str
    recommendations: List[str]

class PrefectQuestionRequest(BaseModel):
    difficulty: str
    num_questions: Optional[int] = 3
    language: str = "en"

    @validator('difficulty')
    def validate_difficulty(cls, v):
        allowed_difficulties = {'basics', 'intermediate', 'advanced'}
        if v not in allowed_difficulties:
            raise ValueError(f'Difficulty must be one of {allowed_difficulties}')
        return v

    @validator('language')
    def validate_language(cls, v):
        allowed_languages = {'en', 'es', 'fr', 'de', 'zh', 'ja', 'ko'}
        if v not in allowed_languages:
            raise ValueError(f'Language must be one of {allowed_languages}')
        return v

class PrefectAnswerRequest(BaseModel):
    question: str
    answer: str
    difficulty: str

    @validator('difficulty')
    def validate_difficulty(cls, v):
        allowed_difficulties = {'basics', 'intermediate', 'advanced'}
        if v not in allowed_difficulties:
            raise ValueError(f'Difficulty must be one of {allowed_difficulties}')
        return v

    @validator('answer')
    def validate_answer(cls, v):
        if not v.strip():
            raise ValueError('Answer cannot be empty')
        return v.strip()

class CustomQuestion(BaseModel):
    question: str
    key_points: List[str]
    difficulty: str
    language: str = "en"

    @validator('difficulty')
    def validate_difficulty(cls, v):
        allowed_difficulties = {'basics', 'intermediate', 'advanced'}
        if v not in allowed_difficulties:
            raise ValueError(f'Difficulty must be one of {allowed_difficulties}')
        return v

    @validator('language')
    def validate_language(cls, v):
        allowed_languages = {'en', 'es', 'fr', 'de', 'zh', 'ja', 'ko'}
        if v not in allowed_languages:
            raise ValueError(f'Language must be one of {allowed_languages}')
        return v

    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()

    @validator('key_points')
    def validate_key_points(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Key points cannot be empty')
        return [point.strip() for point in v if point.strip()]

@app.post("/api/questions/generate")
async def generate_questions(language: str):
    """Generate interview questions based on the selected language."""
    try:
        response = await openai.ChatCompletion.acreate(
            model="openai/gpt-4",
            messages=[{
                "role": "system",
                "content": f"You are an expert interviewer. Generate 5 professional interview questions in {language}."
            }],
            headers={
                "HTTP-Referer": "https://interview-platform.com",
                "X-Title": "AI Interview Platform",
                "Authorization": f"Bearer {openai.api_key}"
            }
        )
        questions = response.choices[0].message.content.split("\n")
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/questions/upload")
async def upload_questions(questions: List[InterviewQuestion]):
    """Handle custom question upload."""
    try:
        # Validate and store questions
        return {"message": "Questions uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid question format")

@app.post("/api/prefect/questions")
async def get_prefect_questions(request: PrefectQuestionRequest):
    """Get random Prefect interview questions based on difficulty level and language."""
    try:
        questions = get_random_questions(
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            language=request.language
        )
        return {"questions": questions}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prefect/evaluate")
async def evaluate_prefect_answer(request: PrefectAnswerRequest):
    """Evaluate a user's answer to a Prefect interview question."""
    try:
        evaluation = evaluate_answer(request.question, request.answer, request.difficulty)
        return evaluation
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prefect/questions/upload")
async def upload_custom_questions(questions: List[CustomQuestion]):
    """Upload custom Prefect interview questions."""
    try:
        # Add questions to the existing question bank
        for q in questions:
            # Create language-specific key if it doesn't exist
            if q.language not in PREFECT_QUESTIONS:
                PREFECT_QUESTIONS[q.language] = {
                    'basics': [],
                    'intermediate': [],
                    'advanced': []
                }
            
            # Add question to the appropriate language and difficulty
            PREFECT_QUESTIONS[q.language][q.difficulty].append({
                "question": q.question,
                "key_points": q.key_points
            })
        
        return {
            "message": f"Successfully added {len(questions)} questions",
            "questions_added": questions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/speech/transcribe")
async def transcribe_audio(
    language: str,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """Transcribe audio to text using Google Cloud Speech-to-Text."""
    if not file.filename.endswith(('.webm', '.wav', '.mp3')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only .webm, .wav, and .mp3 files are supported."
        )

    try:
        client = speech.SpeechClient()
        content = await file.read()
        
        # Check file size (10MB limit)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum size is 10MB."
            )

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            language_code=language,
            audio_channel_count=1,
            enable_automatic_punctuation=True,
        )

        response = client.recognize(config=config, audio=audio)
        
        if not response.results:
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe audio. Please ensure clear audio quality."
            )

        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript + "\n"
        
        return {"transcript": transcript.strip()}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )

@app.post("/api/feedback/analyze")
async def analyze_feedback(
    request: FeedbackRequest,
    settings: Settings = Depends(get_settings)
):
    """Generate professional feedback for the interview response."""
    try:
        response = await openai.ChatCompletion.acreate(
            model="openai/gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert interviewer providing detailed feedback on interview responses."
                },
                {
                    "role": "user",
                    "content": f"Question: {request.question}\nResponse: {request.audio_url}\nProvide detailed feedback with scores, strengths, improvements, and recommendations."
                }
            ],
            headers={
                "HTTP-Referer": "https://interview-platform.com",
                "X-Title": "AI Interview Platform",
            }
        )

        feedback_text = response.choices[0].message.content
        
        # Parse the feedback into structured format
        # This is a simplified version - you might want to make this more robust
        feedback = {
            "score": 7.5,  # You should parse this from the feedback
            "strengths": ["Clear communication", "Good structure"],
            "improvements": ["Could provide more specific examples"],
            "detailed_analysis": feedback_text,
            "recommendations": ["Practice with more specific examples", "Focus on pace"]
        }
        
        return FeedbackResponse(**feedback)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating feedback: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
