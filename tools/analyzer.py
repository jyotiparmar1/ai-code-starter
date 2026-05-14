import json
import re
import os
import requests

# OpenRouter API configuration, with environment override.
OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "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"
)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "poolside/laguna-m.1:free"
OPENROUTER_TIMEOUT = int(os.getenv("OPENROUTER_TIMEOUT", "45"))

def extract_json_from_response(content: str) -> dict:
    """Extract JSON from response, handling markdown code blocks."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    json_match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from response. Content: {content[:200]}")


def normalize_name(value: str) -> str:
    if not value or not isinstance(value, str):
        return "GeneratedEntity"
    parts = re.findall(r"[A-Za-z0-9]+", value)
    if not parts:
        return "GeneratedEntity"
    normalized = "".join(part.capitalize() for part in parts)
    if normalized and normalized[0].isdigit():
        normalized = "Entity" + normalized
    return normalized


def normalize_field_type(type_value: str) -> str:
    if not type_value or not isinstance(type_value, str):
        return "String"
    normalized = type_value.strip().lower()
    if normalized in {"long", "int", "integer", "bigint"}:
        return "Long"
    if normalized in {"double", "float", "decimal", "number"}:
        return "Double"
    if normalized in {"bool", "boolean"}:
        return "Boolean"
    return "String"


def sanitize_field_name(name: str) -> str:
    if not name or not isinstance(name, str):
        return "field"
    parts = re.findall(r"[A-Za-z0-9]+", name)
    if not parts:
        return "field"
    sanitized = parts[0].lower() + "".join(part.capitalize() for part in parts[1:])
    if sanitized[0].isdigit():
        sanitized = "field" + sanitized
    return sanitized


def extract_operations_from_entity(entity: dict) -> list:
    operations = []
    raw_ops = entity.get("operations")
    if isinstance(raw_ops, list):
        for op in raw_ops:
            if not isinstance(op, dict):
                continue
            op_type = str(op.get("type", "READ")).strip().upper()
            endpoint = str(op.get("endpoint", "")).strip()
            method = str(op.get("method", "")).strip().upper()
            description = str(op.get("description", "")).strip()
            if op_type not in {"CREATE", "READ", "UPDATE", "DELETE"}:
                op_type = "READ"
            if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                method = "GET"
            operations.append({
                "type": op_type,
                "method": method,
                "endpoint": endpoint,
                "description": description,
            })
    return operations


def ensure_entity_defaults(entity: dict) -> dict:
    name = normalize_name(entity.get("name"))
    fields = []
    for raw_field in entity.get("fields") or []:
        if not isinstance(raw_field, dict):
            continue
        field_name = sanitize_field_name(raw_field.get("name"))
        field_type = normalize_field_type(raw_field.get("type"))
        fields.append({"name": field_name, "type": field_type})
    if not fields:
        fields = [{"name": "name", "type": "String"}]

    operations = extract_operations_from_entity(entity)
    return {
        "name": name,
        "fields": fields,
        "operations": operations,
    }


def clean_analyzer_output(data: dict, raw_prd_text: str = "") -> dict:
    if not isinstance(data, dict):
        data = {}

    project_name = data.get("project_name")
    if not project_name or not isinstance(project_name, str):
        project_name = "GeneratedProject"

    entities = []
    raw_entities = data.get("entities")
    if isinstance(raw_entities, list):
        for raw in raw_entities:
            if not isinstance(raw, dict):
                continue
            entities.append(ensure_entity_defaults(raw))

    if not entities:
        entities.append(ensure_entity_defaults({}))

    inference_notes = data.get("inference_notes")
    if not isinstance(inference_notes, list):
        inference_notes = []

    return {
        "project_name": project_name,
        "entities": entities,
        "inference_notes": inference_notes,
        "raw_analysis": raw_prd_text,
    }


def analyze(text: str, project_name: str = None) -> dict:
    # Get enhanced context from MCP server
    try:
        from .mcp_server import get_spring_boot_context
        mcp_context = get_spring_boot_context(text)
        context_info = f"\nAdditional Context from MCP:\n{mcp_context}\n"
    except Exception:
        # Fallback if MCP server is not available
        context_info = "\nUsing standard Spring Boot best practices.\n"

    if project_name and isinstance(project_name, str):
        project_prompt = f"Project name: {project_name}\n"
    else:
        project_prompt = ""
    
    prompt = f"""
You are a senior Spring Boot architect.
Analyze the PRD for domain entities, fields, and CRUD operations.
Return STRICT JSON ONLY with no explanatory text.

PRD:
{project_prompt}{text}

{context_info}

JSON FORMAT:
{{
  "project_name": "EmployeeManagement",
  "entities": [
    {{
      "name": "Employee",
      "fields": [
        {{"name": "name", "type": "String"}},
        {{"name": "department", "type": "String"}}
      ],
      "operations": [
        {{"type": "CREATE", "method": "POST", "endpoint": "/employees", "description": "Create a new employee"}},
        {{"type": "READ", "method": "GET", "endpoint": "/employees", "description": "List all employees"}},
        {{"type": "READ", "method": "GET", "endpoint": "/employees/{{id}}", "description": "Get employee by ID"}},
        {{"type": "UPDATE", "method": "PUT", "endpoint": "/employees/{{id}}", "description": "Update employee details"}},
        {{"type": "DELETE", "method": "DELETE", "endpoint": "/employees/{{id}}", "description": "Remove an employee"}}
      ]
    }}
  ]
}}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Code Generator"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    if not text.strip():
        raise ValueError("Cannot generate JSON from empty requirement text.")

    try:
        response = requests.post(
            OPENROUTER_BASE_URL,
            headers=headers,
            json=payload,
            timeout=OPENROUTER_TIMEOUT
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        data = {
            "inference_notes": [
                f"OpenRouter request timed out after {OPENROUTER_TIMEOUT} seconds. Falling back to default entity extraction."
            ]
        }
    except requests.exceptions.RequestException as exc:
        data = {
            "inference_notes": [
                f"OpenRouter request failed: {str(exc)}. Falling back to default entity extraction."
            ]
        }
    else:
        content = response.json()["choices"][0]["message"]["content"]
        try:
            data = extract_json_from_response(content)
        except ValueError as exc:
            data = {
                "inference_notes": [
                    f"OpenRouter returned invalid JSON: {str(exc)}. Falling back to default entity extraction."
                ]
            }

    if project_name and isinstance(project_name, str):
        data["project_name"] = project_name
    return clean_analyzer_output(data, raw_prd_text=text)