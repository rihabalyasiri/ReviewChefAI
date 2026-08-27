# review-fetcher-service

Fetches a restaurant's Google reviews and stores the ones that fall within a given calendar month in Redis.

## Known limitation

The Google **Places API** (used here) only ever exposes up to 5 reviews per place — the most relevant, or
with `reviews_sort=newest` the most recent — and has no server-side date filtering or pagination. This
service fetches whatever the API currently returns and filters it down to the requested month client-side,
so requesting a month further back than the 5 most recent reviews will usually return zero results. Real
historical, paginated access requires the **Google Business Profile API** instead (OAuth as the verified
business owner), which is a larger integration than this prototype covers.

## Architecture

Each layer depends only on an abstraction of the layer below it (dependency inversion), so the Google
Places API or Redis can each be swapped out independently:

- `app/providers/` — `ReviewsProvider` abstract base + `GooglePlacesReviewsProvider` implementation.
- `app/repositories/` — `ReviewsRepository` abstract base + `RedisReviewsRepository` implementation.
- `app/services/review_fetch_service.py` — `ReviewFetchService`, the use case that fetches, filters by
  month, and persists — wired to a provider and repository via constructor injection.
- `app/main.py` — FastAPI HTTP layer that wires concrete implementations together and exposes the API.
- `app/date_utils.py` — pure functions for computing a month's date range and filtering reviews by it.

## API

- `GET /health` — liveness check.
- `POST /reviews/fetch` — body `{"place_id": "...", "year": 2024, "month": 3}`. Fetches reviews for the
  place, keeps only those from the given month, saves them to Redis under key
  `reviews:{place_id}:{year}-{month}` (zero-padded month), and returns the stored reviews.

## Setup

```bash
pip install -r requirements-dev.txt
cp example.env .env   # then fill in GOOGLE_PLACES_API_KEY
```

## Running

```bash
uvicorn app.main:app --reload
```

Requires a Redis instance reachable via `REDIS_HOST`/`REDIS_PORT`/`REDIS_DB` (see `docker-compose.yml` at
the repo root to run one locally alongside this service).

## Testing

```bash
GOOGLE_PLACES_API_KEY=test-key pytest
```
