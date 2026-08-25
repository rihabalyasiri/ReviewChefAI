# analysis-service (planned)

Will wrap the existing sentiment/insight logic in `engine.py` / `engine_async.py` as a standalone service:
reads a batch of reviews (initially from Redis, written there by `review-fetcher-service`) and produces a
`ReviewAnalysisResult` per the schema defined in `engine.py`.

Not implemented yet — this is a placeholder marking where that service will live once the review-fetcher
and analysis pipelines are wired together.
