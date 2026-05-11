# Quickstart: PRD CRUD Inference

## Setup

1. Activate the Python virtual environment:
   ```powershell
   d:\ai-code-starter\venv\Scripts\Activate.ps1
   ```

2. Install required Python dependencies if not already installed:
   ```powershell
   pip install fastapi uvicorn requests jinja2
   ```

## Run the API

Start the FastAPI server:

```powershell
uvicorn main:app --reload
```

The API will be available at:

- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Use the feature

1. Open the Swagger UI at `http://localhost:8000/docs`.
2. Use the `POST /generate` endpoint.
3. Upload a PRD text file.
4. The response will return a ZIP file path such as `output/project.zip`.

## Output

The generated ZIP contains a runnable Spring Boot starter project with:

- `Application.java`
- `application.properties`
- `pom.xml`
- `entity/` classes
- `repository/` interfaces
- `service/` classes
- `controller/` classes
- `inference-summary.txt` or generated inference notes (planned)

## Notes

- This MVP targets PRD-only generation. Jira and test case integrations are deferred to later phases.
- The system currently relies on OpenRouter for PRD interpretation.
