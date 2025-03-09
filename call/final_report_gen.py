import json
import openai
from django.conf import settings
from .models import EvaluationResult

def generate_final_report(evaluation_result, job_description):
    """
    Generate a comprehensive evaluation report using stored scores and job context.
    
    Args:
        evaluation_result (EvaluationResult): The evaluation result instance.
        job_description (str): The job description for the position.
    
    Returns:
        dict: Structured final report in JSON format.
    """
    verbal_scores = evaluation_result.verbal_scores
    
    # Convert string scores to floats
    if isinstance(verbal_scores, dict):
        try:
            flat_scores = {q: float(v) for q, v in verbal_scores.items()}  # Convert all values to float
        except ValueError:
            raise ValueError("One or more scores in verbal_scores cannot be converted to a number.")
    else:
        flat_scores = {}  # Default to an empty dictionary if verbal_scores is not a dict
    
    total_questions = len(flat_scores)
    
    average_score = sum(flat_scores.values()) / total_questions if total_questions > 0 else 0
    max_score = max(flat_scores.values(), default=0)
    min_score = min(flat_scores.values(), default=0)

    # Identify strengths and improvement areas dynamically
    strengths, improvement_areas = _identify_patterns(flat_scores, job_description)

    # Construct summary table data dynamically
    summary_table = {
        "Overall Score": f"{average_score:.2f}/{total_questions}",
        "Strengths": ", ".join(strengths) if strengths else "None identified",
        "Key Skill Gaps": ", ".join(improvement_areas) if improvement_areas else "None identified",
        "Communication Skills": "Decent articulation; lacks job specificity",  # Placeholder; adjust as needed
        "Recommendation": "Do not progress"  # Placeholder; adjust as needed
    }

    return summary_table

def _identify_patterns(scores, job_desc):
    """Identify strengths/weaknesses based on score patterns."""
    client = openai.OpenAI(api_key=settings.OPEN_AI_KEY)
    
    prompt = f"""
    Analyze these interview scores for a {job_desc} role:
    {json.dumps(scores, indent=2)}
    
    Identify 3 key strengths and 2 improvement areas based on:
    1. Consistency across technical questions
    2. Job requirement alignment
    3. Communication skill progression
    
    Format as JSON:
    {{
        "strengths": [],
        "improvement_areas": []
    }}
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    analysis = json.loads(response.choices[0].message.content)
    return analysis["strengths"], analysis["improvement_areas"]
