from typing import List, Dict
import random

# Initialize questions with language support
PREFECT_QUESTIONS = {
    'en': {  # English questions
        'basics': [
            {
                'question': 'What is a Prefect Flow?',
                'key_points': [
                    'A Flow is a container for workflow logic',
                    'Flows are Python functions decorated with @flow',
                    'Flows can contain tasks and other flows'
                ]
            },
            {
                "question": "What is Prefect and how does it differ from other workflow management tools?",
                "key_points": [
                    "Modern workflow orchestration tool",
                    "Python-native framework",
                    "Dynamic DAG creation",
                    "Hybrid execution model",
                    "Built-in failure handling"
                ]
            },
            {
                "question": "Explain the concept of Tasks and Flows in Prefect.",
                "key_points": [
                    "Tasks are individual units of work",
                    "Flows are collections of tasks with dependencies",
                    "Decorators @task and @flow",
                    "State handling",
                    "Task retries and caching"
                ]
            },
            {
                "question": "How does Prefect handle task dependencies?",
                "key_points": [
                    "Automatic dependency inference",
                    "Explicit dependencies using upstream/downstream",
                    "Task results as inputs",
                    "Parallel execution",
                    "Dynamic task generation"
                ]
            }
        ],
        'intermediate': [
            {
                "question": "Explain Prefect's execution model and deployment options.",
                "key_points": [
                    "Local vs distributed execution",
                    "Prefect agents and work queues",
                    "Docker containers",
                    "Kubernetes integration",
                    "Infrastructure blocks"
                ]
            },
            {
                "question": "How do you handle errors and retries in Prefect?",
                "key_points": [
                    "Retry policies",
                    "Task state handlers",
                    "Flow-level error handling",
                    "Custom retry logic",
                    "State change notifications"
                ]
            }
        ],
        'advanced': [
            {
                "question": "Describe Prefect's storage options and how to configure them.",
                "key_points": [
                    "Local storage",
                    "S3/GCS/Azure storage blocks",
                    "Result persistence",
                    "Flow storage configuration",
                    "Remote storage best practices"
                ]
            },
            {
                "question": "How would you implement a complex ETL pipeline using Prefect?",
                "key_points": [
                    "Subflow composition",
                    "Parallel task execution",
                    "Data validation tasks",
                    "Error handling strategies",
                    "Monitoring and logging"
                ]
            }
        ]
    },
    'es': {  # Spanish questions
        'basics': [],
        'intermediate': [],
        'advanced': []
    },
    'fr': {  # French questions
        'basics': [],
        'intermediate': [],
        'advanced': []
    },
    'de': {  # German questions
        'basics': [],
        'intermediate': [],
        'advanced': []
    },
    'zh': {  # Chinese questions
        'basics': [],
        'intermediate': [],
        'advanced': []
    },
    'ja': {  # Japanese questions
        'basics': [],
        'intermediate': [],
        'advanced': []
    },
    'ko': {  # Korean questions
        'basics': [],
        'intermediate': [],
        'advanced': []
    }
}

def get_random_questions(difficulty: str, num_questions: int = 3, language: str = 'en') -> List[Dict]:
    """Get random questions from the specified difficulty level and language."""
    if language not in PREFECT_QUESTIONS:
        raise ValueError(f'Language {language} not supported')
    
    if difficulty not in PREFECT_QUESTIONS[language]:
        raise ValueError(f'Difficulty {difficulty} not found')
    
    questions = PREFECT_QUESTIONS[language][difficulty]
    if not questions:
        raise ValueError(f'No questions available for {difficulty} difficulty in {language}')
    
    # Return random questions, or all if num_questions > available questions
    return random.sample(questions, min(num_questions, len(questions)))

def evaluate_answer(question: str, answer: str, difficulty: str, language: str = 'en') -> Dict:
    """Evaluate a user's answer to a Prefect interview question."""
    if language not in PREFECT_QUESTIONS:
        raise ValueError(f'Language {language} not supported')
    
    # Find the matching question and key points
    matching_question = None
    for q in PREFECT_QUESTIONS[language][difficulty]:
        if q["question"].strip() == question.strip():
            matching_question = q
            break
    
    if not matching_question:
        raise ValueError(f'Question not found in {difficulty} difficulty level for {language}')
    
    # Create evaluation criteria
    evaluation = {
        "covered_points": [],
        "missed_points": [],
        "score": 0.0,
        "feedback": ""
    }
    
    try:
        # Check for key points in the answer
        answer_lower = answer.lower()
        for point in matching_question["key_points"]:
            # More flexible matching by checking if the key concepts are present
            key_terms = point.lower().split()
            if any(all(term in answer_lower for term in key_terms) for term in key_terms):
                evaluation["covered_points"].append(point)
            else:
                evaluation["missed_points"].append(point)
        
        # Calculate score
        total_points = len(matching_question["key_points"])
        covered_points = len(evaluation["covered_points"])
        evaluation["score"] = (covered_points / total_points * 100) if total_points > 0 else 0
        
        # Generate feedback based on language
        if evaluation["score"] >= 80:
            evaluation["feedback"] = get_feedback_text("excellent", language)
            if evaluation["missed_points"]:
                evaluation["feedback"] += " " + get_feedback_text("consider", language) + ": " + ", ".join(evaluation["missed_points"])
        elif evaluation["score"] >= 60:
            evaluation["feedback"] = get_feedback_text("good", language) + ": " + ", ".join(evaluation["missed_points"])
        else:
            evaluation["feedback"] = get_feedback_text("review", language) + ": " + ", ".join(evaluation["missed_points"])
        
        return evaluation
    except Exception as e:
        raise ValueError(f"Error evaluating answer: {str(e)}")

def get_feedback_text(feedback_type: str, language: str) -> str:
    """Get feedback text in the specified language."""
    feedback_texts = {
        'en': {
            'excellent': 'Excellent answer! You demonstrated strong understanding of the concepts.',
            'good': 'Good answer showing basic understanding. To improve, elaborate on',
            'review': 'Review these key concepts',
            'consider': 'Consider mentioning'
        },
        'es': {
            'excellent': '¡Excelente respuesta! Demostraste una sólida comprensión de los conceptos.',
            'good': 'Buena respuesta que muestra comprensión básica. Para mejorar, elabora sobre',
            'review': 'Revisa estos conceptos clave',
            'consider': 'Considera mencionar'
        },
        # Add more languages as needed
    }
    
    # Default to English if language not supported
    return feedback_texts.get(language, feedback_texts['en']).get(feedback_type, feedback_texts['en'][feedback_type])
