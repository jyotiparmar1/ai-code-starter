# Implementation Plan: PRD CRUD Inference

**Branch**: `001-crud-from-prd` | **Date**: 2026-05-11 | **Spec**: specs/001-crud-from-prd/spec.md
**Input**: Feature specification from `/specs/001-crud-from-prd/spec.md`

## Summary

Extend the existing parser → analyzer → generator pipeline so uploaded PRD files are analyzed for domain entities, fields, and CRUD intent. The analyzer will infer create/read/update/delete operations from natural-language PRD content and the generator will embed those operations into Spring Boot template scaffolding. Additionally, integrate AI-driven feature extraction to automatically identify technology stack requirements (JWT, databases, etc.) from PRD text. The output remains a runnable Spring Boot starter project packaged as a ZIP archive with standardized `/api/` REST endpoints and clean entity definitions.

## Technical Context

**Language/Version**: Python 3.x
**Primary Dependencies**: FastAPI, requests, Jinja2, zipfile, python-docx, OpenRouter API
**Storage**: Temporary local files for upload processing and output generation
**Testing**: No automated test cases required for this phase; validation is limited to generated artifact structure and runnability
**Target Platform**: Local development server; HTTP API for file uploads
**Project Type**: Web service / code generation pipeline
**Performance Goals**: Generate one Spring Boot project per PRD upload with acceptable latency for an AI-backed service (target: < 30 seconds, dependent on OpenRouter)
**Constraints**: MVP must support PRD-only input; Jira/Test cases/MCP integrations are deferred to later phases; must not require additional user tests in this phase
**Scale/Scope**: Single PRD upload per request, one generated Spring Boot starter ZIP per request

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Must follow AI-driven, template-based generation. ✔
- Must preserve parser → analyzer → generator architecture. ✔
- Must generate runnable Spring Boot artifacts using Jinja2 templates. ✔
- Must produce downloadable ZIP output. ✔
- Must remain extensible for future MCP/JIRA/Test case integration. ✔
- Must use AI for feature extraction from PRD text. ✔
- Must generate standardized `/api/` REST endpoints. ✔
- Must prevent duplicate field generation in entities. ✔

## Project Structure

### Documentation (this feature)

```text
specs/001-crud-from-prd/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.md
└── spec.md
```

### Source Code (repository root)

```text
main.py
orchestrator.py
tools/parser.py
tools/analyzer.py
tools/generator.py
templates/
```

## Implementation Approach

1. Enhance `tools/parser.py` to support `.docx` PRD uploads and extract text for analysis.
2. Enhance `tools/analyzer.py` to infer CRUD operations and generate a richer JSON contract from PRD text.
3. Update `tools/generator.py` to consume inferred operations and render them into `controller.java.j2`, `service.java.j2`, and other templates.
4. Integrate AI-driven feature extraction using LLM in `tools/features.py` for automated technology stack inference.
5. Fix template issues: update controller base paths to `/api/`, prevent duplicate `id` fields, enhance operation normalization for custom endpoints.
6. Add output metadata documentation for ambiguous inferences, e.g. `inference-summary.txt` in the generated ZIP.
7. Keep `main.py` and `orchestrator.py` as the pipeline entrypoints.
8. Maintain the current ZIP packaging flow in `tools/generator.py`.

## Dependencies & Notes

- This phase depends on the OpenRouter API for PRD interpretation.
- The parser also depends on `python-docx` to support `.docx` uploads.
- No additional persistence layer is required.
- Because no tests are required, the focus is on end-to-end artifact completeness rather than automated coverage.

## Risks

- AI inference may misinterpret domain operations, so generated scaffold must be conservative and clearly documented.
- Lack of explicit tests increases risk of broken generated output; manual verification of sample PRD flows will be important.
