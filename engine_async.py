import os
import asyncio
import time
from typing import List
from dotenv import load_dotenv
from openai import AsyncOpenAI
from engine import ReviewAnalysisResult, mock_reviews

load_dotenv()

# Initialize the ASYNC client
async_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==========================================
# PRODUCTION-GRADE ASYNC WORKER
# ==========================================

async def analyze_batch_async(reviews: List[str], batch_id: int) -> ReviewAnalysisResult:
    """Worker that handles a single batch of reviews asynchronously."""
    formatted_reviews = "\n---\n".join([f"Review: {text}" for text in reviews])

    system_instruction = (
        "You are an expert Restaurant Operations Consultant. Analyze this batch of customer reviews, "
        "categorize the feedback objectively, and provide highly practical, operational advice."
    )

    print(f"📦 [Batch {batch_id}] Sending {len(reviews)} reviews to OpenAI...")

    # Using the async parsing method
    completion = await async_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": formatted_reviews}
        ],
        response_format=ReviewAnalysisResult,
    )

    print(f"✅ [Batch {batch_id}] Finished processing.")
    return completion.choices[0].message.parsed


async def process_large_review_pool(all_reviews: List[str], batch_size: int = 5):
    """Chunks the massive review list and processes them concurrently."""
    # 1. Chunking logic: Break the big list into lists of 'batch_size'
    chunks = [all_reviews[i:i + batch_size] for i in range(0, len(all_reviews), batch_size)]
    print(f"⚙️ Split {len(all_reviews)} reviews into {len(chunks)} concurrent batches.")

    # 2. Create an async task for each chunk
    tasks = []
    for index, chunk in enumerate(chunks):
        tasks.append(analyze_batch_async(chunk, batch_id=index + 1))

    # 3. Fire them all off at the exact same time and wait for them all to return
    start_time = time.time()
    results: List[ReviewAnalysisResult] = await asyncio.gather(*tasks)
    end_time = time.time()

    print(f"\n⏱️ Total Concurrency execution time: {end_time - start_time:.2f} seconds")
    return results

# ==========================================
# RUNNING THE SCALED PERFORMANCE TEST
# ==========================================
if __name__ == "__main__":
    # Let's multiply our mock reviews to simulate a heavy workload (30 reviews)
    large_scale_reviews = mock_reviews * 5

    print("🚀 Starting Production-Scale Async Engine Test...")

    # Run the main async loop
    batch_results = asyncio.run(process_large_review_pool(large_scale_reviews, batch_size=6))

    # Quick sanity check on the returned data structures
    print(f"\n📊 Successfully generated {len(batch_results)} independent batch analysis reports.")
    print(f"Sample Overall Sentiment from Batch 1: {batch_results[0].overall_sentiment}")
    print(batch_results)