# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

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

## Core Engineering Principles

Always prioritize the following, in this order:

Correctness
Data integrity
Security and privacy
Maintainability
Testability
Performance
Developer experience
Minimal complexity

Do not optimize prematurely.

Do not introduce a framework, library, abstraction, design pattern, database technology, or architectural layer unless there is a concrete reason for it.

When modifying existing code, prefer the smallest safe change that solves the problem.

Do not rewrite working code simply because a different implementation looks cleaner.

**IMPORTANT**: Whenever you write code, it MUST follow SOLID design principles. Never write code that violates these principles. If you do, you will be asked to refactor it.

## Repository Exploration

Use repository search aggressively before creating new code.

Prefer:

Searching for existing implementations.
Reusing existing components.
Reusing existing validation.
Reusing existing error handling.
Reusing existing API clients.
Reusing existing types/models.
Reusing existing formatting utilities.

Avoid creating duplicate:

Components
Services
Utility functions
Validation logic
API clients
Types
Database queries
Formatting functions

If similar functionality already exists, extend it instead of creating a parallel implementation.

## Error Handling

Errors should be handled intentionally.

Do not use broad catch blocks that hide failures.

Avoid:

catch (error) {
    // ignore
}

unless there is a documented reason.

Errors should:

Be actionable for developers.
Be understandable for users where appropriate.
Preserve useful debugging information.
Avoid leaking sensitive implementation details.

Do not expose raw database errors to end users.

## Test Quality

Do not write brittle tests that depend unnecessarily on:

Implementation details
Exact internal function calls
Unstable DOM structure
Timing
Random values
Current date/time

Prefer behavior-focused assertions.

A good test should communicate what behavior is required.

## Dependencies

Before adding a dependency, ask:

Does the project already have something that solves this?
Is the dependency actively maintained?
Is it necessary?
What is its bundle/runtime cost?
Does it introduce security concerns?
Does it significantly increase complexity?

Do not add a dependency for trivial functionality that can reasonably be implemented using existing platform capabilities.

## Code Style

Follow the existing formatter and linter.

Do not manually fight automated formatting.

Before finishing a change, run the project's relevant:

formatter
linter
type checker
unit tests
integration tests
build

Use the actual commands defined by the repository rather than assuming standard commands.

## Type Safety

Prefer explicit and meaningful types.

Avoid unnecessary:

any
unknown
type assertions
non-null assertions

when safer alternatives exist.

Do not weaken type safety merely to make compilation succeed.

If an external API returns untrusted data, validate it at the boundary.

## Naming

Use names that describe intent.

Prefer:

calculateMonthlyExpenses()
getExpensesByCategory()
createExpense()
validateExpense()

over vague names such as:

process()
handle()
doStuff()
data()

Names should follow the existing project's language and conventions.

Do not rename unrelated code during feature work.

## Comments

Write comments to explain why, not obvious what.

Bad:

// Add expense to list
expenses.push(expense)

Good:

// Keep the locally created expense visible immediately while the
// background synchronization completes.

Remove outdated comments when changing the corresponding implementation.

Never leave comments that describe behavior the code no longer has.

## Refactoring

Refactor when it clearly improves:

Correctness
Maintainability
Reusability
Testability
Performance

Avoid unrelated refactoring during feature work.

A feature PR should not unexpectedly modify dozens of unrelated files.

If a refactor is necessary, keep it logically separated where possible.

## Performance

Do not optimize based on assumptions.

Measure first when performance matters.

Watch for:

N+1 database queries
Loading all expenses unnecessarily
Excessive frontend re-renders
Expensive calculations repeated unnecessarily
Large API payloads
Missing database indexes
Unbounded queries

For large expense datasets, prefer server-side filtering, pagination, and aggregation where appropriate.

Do not sacrifice correctness for premature performance optimization.

## Responsive Design

The expense tracker should work well across:

Desktop
Tablet
Mobile

Do not assume a large screen.

Expense entry should remain practical on mobile devices.

Avoid horizontal scrolling unless it is genuinely necessary.

## Claude Code Behavior

When working on this repository, Claude should:

Inspect before editing.
Search before creating.
Reuse before duplicating.
Test before claiming success.
Explain assumptions when they matter.
Keep changes focused.
Protect financial data.
Preserve existing architecture unless there is a strong reason to change it.

Claude should not:

Invent APIs.
Invent database schemas without inspecting the existing schema.
Assume dependencies are installed.
Assume environment variables exist.
Remove functionality without authorization.
Disable tests to make them pass.
Ignore lint/type errors without justification.
Hide errors.
Commit secrets.
Perform destructive database operations without explicit authorization.

## Definition of Done

A change is not complete merely because the code compiles.

Before considering a task complete, verify as applicable:

Requirements are implemented.

Existing behavior is preserved.

Input validation is correct.

Financial calculations are exact.

Authorization/privacy requirements are respected.

Error handling is appropriate.

Tests are added or updated.

Existing tests pass.

Linting passes.

Type checking passes.

Formatting passes.

Build succeeds.

No secrets were introduced.

No unrelated files were modified.

Git diff was reviewed.

Documentation was updated if behavior/configuration changed.

## Development Workflow
1. Before making any changes, create and checkout a feature branch named `feature-[brief-description]`
2. Write comprehensive tests for all new functionality
3. Compile code and run all tests before committing
4. Write detailed commit messages explaining the changes and rationale
5. Commit all changes to the feature branch
