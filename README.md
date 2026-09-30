# Battery Pack Recommender: Roadmap

Each AI concept has its own job in this project:

| Concept | Role in the project |
| --- | --- |
| Clarifying loop | Keeps a structured requirements object and asks about whatever is missing or ambiguous. |
| Tools | Actions with exact answers: search the catalog, calculate runtime, and check compatibility. |
| RAG | Knowledge lookup: datasheets, chemistry guides, and safety and shipping standards. |
| MCP | Exposes the tools and data as a standard server, so any MCP client can use them. |
| Skills | Packaged expertise (`SKILL.md`): the sizing methodology and recommendation report format. |

## Steps

1. **Domain model:** Define the requirements schema and a sample battery catalog.
2. **Clarifying-question loop:** The agent fills the schema by asking follow-up questions.
3. **Tools:** Build catalog search, a runtime and energy calculator, and a compatibility checker.
4. **RAG:** Index datasheets and guides, and retrieve them to justify recommendations.
5. **MCP:** Move the tools and RAG into an MCP server.
6. **Skills:** Package the sizing and recommendation procedure.
7. **Integration, evaluation, UI:** Run end-to-end tests with sample user personas, then build a simple chat interface.

## Project Scaffold

The folder structure is ready for the roadmap above. Python modules and skill
documents are placeholders, the catalog is empty, and tests are yet to be added.
The ingest, evaluation, MCP, and UI entry points report that implementation is pending.

Install the project and development tools with `uv sync --group dev`, then copy
`.env.example` to `.env` and provide your API key. Run Make targets in the project
environment, for example `uv run make test`.

Available targets: `make ingest`, `make test`, `make eval`, `make serve-mcp`,
and `make run`. Generated indexes in `data/vectorstore/` are ignored by Git.

## Development
```uv run pytest tests/unit                       # tests
uv run ruff check . && uv run ruff format .    # lint + format
uv run --env-file .env python -m battery_advisor.agent.loop   # try Step 2
uv add <package>                               # add a dependency later (chromadb, mcp, ...)
```

```
test:
	uv run pytest
lint:
	uv run ruff check .
run:
	uv run --env-file .env python -m battery_advisor.agent.loop
```
