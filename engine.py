import os
from typing import List, Literal
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==========================================
# 1. DEFINE THE DATA SCHEMAS (Pydantic)
# ==========================================

class CategoryInsight(BaseModel):
    category_name: Literal["Service", "Food Quality", "Cleanliness", "Pricing", "Atmosphere/Ambiance"] = Field(
        ..., description="The high-level category this insight belongs to."
    )
    sentiment_score: float = Field(
        ..., description="A score from -1.0 (highly negative) to 1.0 (highly positive) representing this specific category."
    )
    top_issues: List[str] = Field(
        ..., description="List of specific complaints or recurring negative points found for this category. Empty list if none."
    )
    positive_mentions: List[str] = Field(
        ..., description="List of specific compliments, highlights, or praise. Empty list if none."
    )

class ActionableRecommendation(BaseModel):
    priority: Literal["High", "Medium", "Low"] = Field(
        ..., description="How urgently the restaurant owner needs to address this issue based on volume and impact."
    )
    detected_issue: str = Field(
        ..., description="The problem identified from the reviews (e.g., 'Cold delivery pizzas')."
    )
    operational_action_plan: str = Field(
        ..., description="A concrete, realistic operational step the owner can take in the kitchen or front-of-house to fix it."
    )

class ReviewAnalysisResult(BaseModel):
    overall_sentiment: Literal["Positive", "Mixed", "Negative"] = Field(
        ..., description="The general sentiment across all analyzed reviews combined."
    )
    total_reviews_analyzed: int = Field(
        ..., description="Count of the reviews processed."
    )
    categories: List[CategoryInsight] = Field(
        ..., description="Detailed breakdown of performance per restaurant category."
    )
    actionable_recommendations: List[ActionableRecommendation] = Field(
        ..., description="Top 2-3 highest impact steps the owner should take right now."
    )

# ==========================================
# 2. MOCK DATA & AI EXECUTION ENGINE
# ==========================================

# Simulating messy reviews scraped from platforms like Google and delivery apps
mock_reviews = [
    "The pizza was actually delicious, but we waited almost an hour just to get our drinks! The waiter looked completely overwhelmed.",
    "Ordered delivery from here last night. The burger arrived freezing cold and the fries were soggy. Terrible experience for €25.",
    "Super clean restaurant and beautiful interior. However, the receptionist was incredibly rude when we checked in for our reservation.",
    "Always love coming here! Sarah provided excellent service, she was so attentive. The pasta was superb.",
    "Food is okay but way too expensive for the tiny portions you get. Also, the bathroom floor was sticky.",
    "We waited 45 minutes for our table even though we booked in advance. Nobody offered us a complimentary drink or even apologized."
]

def analyze_restaurant_reviews(reviews: List[str]) -> ReviewAnalysisResult:
    # Format the reviews into a single readable batch string for the LLM
    formatted_reviews = "\n---\n".join([f"Review {i+1}: {text}" for i, text in enumerate(reviews)])

    system_instruction = (
        "You are an expert Restaurant Operations Consultant and Data Analyst. "
        "Your job is to analyze a batch of customer reviews, categorize the feedback objectively, "
        "and provide highly practical, operational advice to the owner. Do not give generic advice."
    )

    # Utilizing OpenAI's beta feature for strict structured schema enforcement
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",  # Highly cost-effective model for text classification
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Analyze these reviews:\n\n{formatted_reviews}"}
        ],
        response_format=ReviewAnalysisResult, # This enforces the Pydantic schema
    )

    return completion.choices[0].message.parsed

# ==========================================
# 3. RUN THE ENGINE
# ==========================================
if __name__ == "__main__":
    print("🚀 Running ReviewChef Extraction Engine...")

    try:
        insights = analyze_restaurant_reviews(mock_reviews)

        # Print the structured JSON output directly from the validated Pydantic model
        print("\n✨ Structured AI Output Validated Successfully:")
        print(insights.model_dump_json(indent=2))

    except Exception as e:
        print(f"❌ An error occurred: {e}")