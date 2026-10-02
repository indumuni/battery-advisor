# Battery Advisor project instructions

## Purpose and current state

This is a Python battery pack advisor for customers in Melbourne, Australia.
It collects structured requirements, searches a local catalog, and calculates
compatibility, runtime, and approximate solar charging performance.

The models, clarification loop, catalog, and deterministic tools are implemented.
RAG, MCP, UI, configuration loading, evaluation, and the project skill documents
are largely scaffolded. Inspect the code before assuming a roadmap component
works; the README's statement that the catalog and tests are empty is outdated.

## Project map

- `src/battery_advisor/models/`: Pydantic v2 `BatteryPack` and `Requirements` models.
- `src/battery_advisor/agent/`: requirement state, deterministic readiness checks,
  and the Anthropic conversation loop.
- `src/battery_advisor/tools/`: catalog search, compatibility, runtime, solar
  estimates, and the tool registry with Pydantic input schemas.
- `data/catalog/catalog.json`: local sample battery specifications and prices.
- `data/knowledge/`: guides, manufacturer PDFs, and generated catalog summaries.
- `configs/prompts/`: system and clarification prompts.
- `configs/settings.yaml`: intended model, locale, and RAG settings; configuration
  loading is still a placeholder. The conversation loop currently hardcodes its
  model separately, so do not assume editing YAML changes runtime behavior.
- `scripts/`: catalog validation, datasheet generation, tool examples, and the
  placeholder index builder.
- `tests/unit/`: catalog, clarification, and tool tests.
- `skills/`: placeholder battery-sizing and recommendation-report methodology.

## Development commands

Use Python 3.12 or newer and `uv`; dependencies and Ruff/pytest settings are in
`pyproject.toml`, with resolved dependencies in `uv.lock`. Run from the repo root.

```sh
uv sync --group dev
uv run pytest
uv run pytest tests/unit/test_tools.py -q
uv run ruff check .
uv run ruff format --check .
uv run python scripts/validate_catalog.py
uv run python scripts/make_datasheets.py
uv run --env-file .env python -m battery_advisor.agent.loop
```

The live agent needs `ANTHROPIC_API_KEY` in a local `.env`; `.env.example` documents
the variable. Unit tests run locally without an API key or network calls.
`uv run make test` runs pytest. The ingest, evaluation, MCP, and UI Make targets
refer to scaffolded components; they are not established working workflows.

## Implementation conventions

- Follow existing module boundaries and keep changes focused on the request.
- Use type hints and Pydantic v2 APIs such as `model_validate`, `model_dump`,
  `model_copy`, and `model_json_schema`. Ruff targets Python 3.12 and a 100-character
  line length. Avoid formatting unrelated files.
- Keep numerical calculations and constraint checks deterministic in the tools.
  The language model should collect requirements and explain computed results.
- Document public functions with their purpose, units, return values, and any
  approximation or important error behavior.
- When adding or changing a tool, update its input model and `REGISTRY` entry in
  `tools/registry.py` so the exposed schema and callable stay consistent.
  `call_tool` validates arguments and returns failures as `{"error": ...}`.
  Requirements-dependent tools receive the requirements object from the caller.
- Add or update focused tests for behavior changes. Run relevant tests and report
  the result; documentation-only edits do not require new tests.
- Use pack IDs that actually exist in the catalog. Search returns price-ordered
  matches and only the three cheapest near misses that fail exactly one check;
  account for this limit when constructing test scenarios.

## Battery domain rules

- Use metric units: W, Wh, V, A, Ah, kg, mm, and degrees Celsius. Prices and budgets
  are AUD. Local dates and solar times use `Australia/Melbourne`, including DST.
- Never invent specifications or certifications. Distinguish catalog data,
  manufacturer documents, user-provided requirements, and planning assumptions.
- Required clarification inputs are application, nominal voltage, peak load,
  and either explicit energy or continuous load plus runtime. Readiness also
  checks consistency warnings. Preserve the conversation's confirmation step
  before finalizing requirements, and disclose optional assumptions.
- Explicit required Wh takes precedence over load multiplied by runtime.
  Usable energy applies chemistry-specific depth of discharge and cold derating;
  reuse `runtime_calc.py` instead of duplicating these formulas.
- Compatibility currently allows 15% nominal-voltage deviation, permits rotation
  when checking dimensions, and evaluates supplied constraints. It does not
  currently check every `Requirements` field, including maximum charge time.
- Runtime excludes inverter losses. Solar charging uses approximate Melbourne
  monthly peak sun hours and 75% efficiency. Keep those assumptions visible and
  do not present the estimates as measured performance or safety certification.

## Data and generated files

- Validate catalog edits with `scripts/validate_catalog.py`; it checks schema,
  unique IDs, physical constraints, and approximate Wh consistency with V × Ah.
- `scripts/make_datasheets.py` writes or overwrites one `<pack_id>.md` file per
  catalog pack in `data/knowledge/datasheets/`. Change the generator when changing
  the generated document format. Its outputs are catalog summaries, not original
  manufacturer datasheets; lifetime cost uses usable energy and rated cycle life.
- Catalog loading is cached. Tests that replace catalog contents should clear
  `load_catalog.cache_clear()` before and after using their temporary data.
- Preserve source PDFs and existing knowledge documents when regenerating
  summaries. Generated vector indexes belong in the ignored `data/vectorstore/`.
- Keep API keys, `.env` contents, virtual environments, caches, and build artifacts
  out of commits. Add dependencies through `uv` so metadata and lockfile agree.
