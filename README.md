# ReviewChefAI

A prototype engine that turns a batch of restaurant customer reviews into structured, actionable insights
using OpenAI's structured-output API. Given raw review text, it produces a validated `ReviewAnalysisResult`:
overall sentiment, a per-category breakdown (Service, Food Quality, Cleanliness, Pricing, Atmosphere), and
prioritized operational recommendations for the restaurant owner.

## Setup

Requires `openai`, `pydantic`, and `python-dotenv`.

```bash
pip install openai pydantic python-dotenv
cp example.env .env   # then fill in your OPENAI_API_KEY
```

## Usage

```bash
python engine.py        # synchronous: analyzes the sample review set in one request
python engine_async.py  # async: chunks a larger review pool into concurrent batched requests
```

`engine.py` prints the validated analysis as pretty JSON. `engine_async.py` simulates a heavier workload
by processing multiple batches concurrently and reports total execution time.

## How it works

- `engine.py` defines the output schema (`CategoryInsight`, `ActionableRecommendation`,
  `ReviewAnalysisResult`) as Pydantic models and enforces it on the OpenAI response via
  `client.beta.chat.completions.parse(..., response_format=ReviewAnalysisResult)`, using `gpt-4o-mini`.
- `engine_async.py` reuses that same schema and sample data, but splits a large list of reviews into
  batches and processes them concurrently with `asyncio.gather` for better throughput.

Both scripts currently run against a hardcoded `mock_reviews` sample list rather than real scraped data.
