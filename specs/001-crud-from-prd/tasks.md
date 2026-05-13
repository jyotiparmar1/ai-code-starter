---

description: "Task list for implementing PRD CRUD inference and runnable Spring Boot ZIP generation"
---

# Tasks: PRD CRUD Inference

**Input**: Design documents from `/specs/001-crud-from-prd/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the feature structure, validate the repository pipeline, and confirm template coverage.

- [ ] T001 Create `specs/001-crud-from-prd/tasks.md` to document feature implementation work
- [ ] T002 Review `main.py`, `orchestrator.py`, and `tools/` to confirm the parser → analyzer → generator pipeline structure
- [ ] T003 Confirm Spring Boot code templates exist in `templates/` and cover `Application.java`, `pom.xml`, `application.properties`, entity, repository, service, and controller artifacts
- [ ] T004 Add `.docx` PRD support to `tools/parser.py` using `python-docx`, while preserving plain text parsing behavior

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared implementation foundation needed by all user stories.

- [ ] T004 Implement PRD CRUD inference schema support in `tools/analyzer.py` to output entities, fields, and inferred CRUD operations
- [ ] T005 Update `tools/generator.py` to consume entity CRUD metadata and generate output files for each entity
- [ ] T006 Extend `templates/controller.java.j2` and `templates/service.java.j2` to render inferred CRUD methods from `entity.operations`
- [ ] T007 Add generation of an inference metadata file in `tools/generator.py`, such as `inference-summary.txt`, into `output/project/`
- [ ] T008 Ensure `tools/generator.py` still writes `Application.java`, `application.properties`, `pom.xml`, and packages `output/project.zip`

---

## Phase 2.5: AI Enhancement & Template Fixes

**Purpose**: Integrate AI-driven feature extraction and fix template issues for better automation.

- [X] T027 Integrate LLM for automated feature extraction from PRD text in `tools/features.py`
- [X] T028 Update controller templates to use `/api/` base path for REST endpoints
- [X] T029 Fix duplicate `id` field generation in entity templates
- [X] T030 Enhance operation normalization for custom endpoints with path variables
- [X] T031 Update service/repository templates for dynamic operation rendering

---

## Phase 3: User Story 1 - Generate runnable CRUD starter code from PRD (Priority: P1) 🎯 MVP

**Goal**: Extract entity definitions and CRUD intent from a PRD and generate a runnable Spring Boot starter ZIP.

**Independent Test**: Upload a PRD text file with one entity and CRUD action descriptions, then verify `output/project.zip` contains Spring Boot starter files plus inferred CRUD scaffolding.

- [ ] T009 [US1] Enhance `tools/analyzer.py` prompt and output format to infer CRUD operations and entity fields from PRD text
- [ ] T010 [US1] Update `tools/generator.py` to generate `entity/{Entity}.java`, `repository/{Entity}Repository.java`, `service/{Entity}Service.java`, and `controller/{Entity}Controller.java` for each inferred entity
- [ ] T011 [US1] Implement CRUD method rendering in `templates/controller.java.j2` for generated endpoints and HTTP methods
- [ ] T012 [US1] Implement CRUD service scaffolding in `templates/service.java.j2` based on inferred create/read/update/delete actions
- [ ] T013 [US1] Generate `inference-summary.txt` in `output/project/` documenting inferred operations and ambiguity resolution
- [ ] T014 [US1] Validate the generated ZIP contains compiled source structure and `inference-summary.txt`

---

## Phase 4: User Story 2 - Extract multiple entities and operations from a single PRD (Priority: P2)

**Goal**: Support PRDs with multiple entities and generate separate scaffolding for each.

**Independent Test**: Upload a PRD describing two or more entities and confirm the generated ZIP contains distinct controller/service/repository groups for each entity.

- [ ] T015 [US2] Update `tools/analyzer.py` to recognize and return multiple entities from a single PRD document
- [ ] T016 [US2] Ensure `tools/generator.py` iterates over all inferred entities and creates separate files in `output/project/entity/`, `output/project/repository/`, `output/project/service/`, and `output/project/controller/`
- [ ] T017 [US2] Validate file naming and package consistency for multiple entity outputs

---

## Phase 5: User Story 3 - Handle ambiguous or incomplete CRUD instructions gracefully (Priority: P3)

**Goal**: Generate default scaffolding for vague PRD content and document inferred behavior.

**Independent Test**: Upload a PRD with partial CRUD descriptions and verify the output still includes starter scaffolding and a note of inferred assumptions.

- [ ] T018 [US3] Add fallback inference logic in `tools/analyzer.py` for entities with missing or ambiguous CRUD actions
- [ ] T019 [US3] Update `tools/generator.py` to render default CRUD placeholders when input operations are incomplete
- [ ] T020 [US3] Document ambiguous assumptions in `inference-summary.txt` or generated README notes
- [ ] T021 [US3] Confirm the generator does not fail on partially specified PRDs and still produces a ZIP archive

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Finalize the feature with documentation, cleanup, and user guidance.

- [ ] T022 [P] Update `specs/001-crud-from-prd/quickstart.md` with any new usage details for the `/generate` endpoint and ZIP output
- [ ] T023 [P] Clean up generator code in `tools/generator.py` and remove any hard-coded test values
- [ ] T024 [P] Review and polish `templates/controller.java.j2` and `templates/service.java.j2` for readable generated code
- [ ] T025 [P] Add or update inline comments in `tools/analyzer.py` to explain the CRUD inference contract
- [ ] T026 [P] Confirm `output/project.zip` contains only the generated Spring Boot starter project files and no temporary upload artifacts

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies, can begin immediately
- **Phase 2: Foundational**: Blocks all user stories until complete
- **Phase 3+: User Stories**: Depend on Phase 2 completion
- **Final Phase**: Depends on user story implementation completion

### Story Dependencies

- **US1**: Independent after foundational phase completes
- **US2**: Independent after foundational phase completes, but requires multi-entity support in analyzer and generator
- **US3**: Independent after foundational phase completes, but requires fallback behavior for ambiguity

## Parallel Execution Examples

- [P] tasks in Phase 1 and Phase 2 can be executed in parallel when they touch different files
- `T009 [US1]` and `T015 [US2]` can be worked in parallel if one engineer focuses on analyzer extraction and another on generator output structure
- `T011 [US1]` and `T012 [US1]` can be implemented in parallel because controller and service templates are separate files

## Implementation Strategy

- Focus first on the MVP path: `T009` through `T014`
- Once the core PRD-to-ZIP flow works, add multi-entity support (`T015`–`T017`)
- Finally, add ambiguity handling and inference documentation (`T018`–`T021`)
- Polish with documentation, cleanup, and ZIP verification tasks
