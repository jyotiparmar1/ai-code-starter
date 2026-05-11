# Research: PRD CRUD Inference

## Decision

Use the existing parser → analyzer → generator pipeline. The analyzer will be responsible for extracting domain entities, fields, and CRUD intent from natural-language PRD text. The generator will translate that structured result into Spring Boot starter code via Jinja2 templates.

## Rationale

- The repository already has a clean pipeline architecture, so extending it preserves the constitution's modularity requirement.
- AI-based PRD analysis is a strong fit for ambiguous requirements and maps naturally to the existing OpenRouter integration.
- Embedding inferred CRUD behavior into templates delivers the user-visible value the spec asks for: runnable starter code from a PRD upload.

## Alternatives Considered

- Local heuristic parsing of PRD text without AI: rejected because this project is explicitly AI-driven and the existing analyzer already uses OpenRouter.
- Generate only entity scaffolding without CRUD operations: rejected because the user request specifically requires CRUD intent extraction.
- Add a dedicated rules engine for CRUD inference: deferred for later phases; immediate MVP should leverage AI prompts.

## Outcome

Use the analyzer to produce JSON with:
- `project_name`
- `entities` including fields and inferred CRUD operations
- `apis` describing endpoints and methods
- optional `inference_notes` documenting ambiguous assumptions

Embed inference documentation in generated output so users can review what was inferred from the PRD.
