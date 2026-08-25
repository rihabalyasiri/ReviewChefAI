# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ReviewChefAI is a small prototype engine that uses OpenAI's structured-output API to turn a batch of
restaurant customer reviews into a validated `ReviewAnalysisResult` (Pydantic model): per-category
sentiment/issues/praise, an overall sentiment, and prioritized operational recommendations for the
restaurant owner. There is no CLI, web server, or test suite yet — each file is run directly as a script.

## Setup

No dependency manifest exists yet (no `requirements.txt`/`pyproject.toml`). Required packages, inferred
from imports: `openai`, `pydantic`, `python-dotenv`.

```bash
pip install openai pydantic python-dotenv
cp example.env .env   # then fill in OPENAI_API_KEY
```

Both entry points call `load_dotenv()` and read `OPENAI_API_KEY` from the environment.

## Running

```bash
python engine.py        # synchronous: analyzes the mock_reviews list in one request
python engine_async.py  # async: chunks a larger review pool into concurrent batched requests
```

Both scripts are meant to be run directly (`if __name__ == "__main__":`) and print results to stdout —
`engine.py` prints the validated result as pretty JSON via `model_dump_json`; `engine_async.py` prints
timing/progress plus the list of per-batch results.

## Architecture

- **`engine.py`** is the source of truth for the data schema and sync analysis logic:
  - `CategoryInsight`, `ActionableRecommendation`, `ReviewAnalysisResult` — the Pydantic models that
    define the strict JSON schema enforced on the model's output via
    `client.beta.chat.completions.parse(..., response_format=ReviewAnalysisResult)`.
  - `analyze_restaurant_reviews(reviews)` — formats a list of review strings into one prompt and makes a
    single blocking OpenAI call (`gpt-4o-mini`) returning a parsed `ReviewAnalysisResult`.
  - `mock_reviews` — the sample review data used by both scripts.
- **`engine_async.py`** builds on top of `engine.py` (imports `ReviewAnalysisResult` and `mock_reviews`
  from it rather than redefining them) to demonstrate scaling the same schema-enforced analysis across
  many reviews:
  - `analyze_batch_async(reviews, batch_id)` — the async equivalent of `analyze_restaurant_reviews` for
    one chunk, using `AsyncOpenAI`.
  - `process_large_review_pool(all_reviews, batch_size)` — splits the full review list into chunks and
    fires all batch requests concurrently with `asyncio.gather`, reporting total wall-clock time.

When extending this project (e.g., replacing mock data with real scraped reviews, adding a CLI/API layer,
or persisting results), keep the Pydantic schema in `engine.py` as the single definition that both the
sync and async paths import — don't fork a second copy of the models.

## Workflow

Every code change must happen on a feature branch, never directly on `main`. Before editing any files,
create (or switch to) a feature branch off `main`, then commit and open a PR from there.
