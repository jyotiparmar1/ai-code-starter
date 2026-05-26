"""MCP Server for Spring Boot Code Generation.

This module uses FastMCP to define MCP tools with standard decorator-based registration.
"""

import asyncio
from typing import Any, Dict, List

from fastmcp.server.server import FastMCP

from tools.parser import parse
from tools.analyzer import analyze
from tools.generator import generate
from tools.jira_client import JiraClient

mcp_app = FastMCP(
    name="spring_boot_mcp_server",
    instructions="FastMCP server exposing Spring Boot code generation tools.",
    version="1.0",
)


def _extract_tool_output(tool_result: Any) -> Any:
    if hasattr(tool_result, "structured_content") and tool_result.structured_content is not None:
        return tool_result.structured_content
    return getattr(tool_result, "content", tool_result)


async def _call_tool_async(tool_name: str, **kwargs: Any) -> Any:
    tool_result = await mcp_app.call_tool(tool_name, kwargs)
    return _extract_tool_output(tool_result)


async def _list_registered_tools() -> List[Dict[str, Any]]:
    return await mcp_app._local_provider.list_tools()


@mcp_app.tool(
    name="parse_prd",
    title="Parse PRD",
    description="Parse a PRD file (markdown, docx, or txt) and extract text content.",
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "content": {"type": "string"},
            "file_path": {"type": "string"},
            "length": {"type": "integer"},
            "error": {"type": "string"},
        },
        "required": ["success", "file_path"],
        "additionalProperties": False,
    },
)
def parse_prd(file_path: str) -> Dict[str, Any]:
    try:
        content = parse(file_path)
        return {
            "success": True,
            "content": content,
            "file_path": file_path,
            "length": len(content),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
        }


@mcp_app.tool(
    name="analyze_prd",
    title="Analyze PRD",
    description="Analyze parsed PRD text to extract entities, CRUD operations, and features.",
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "analysis": {"type": "object", "additionalProperties": True},
            "error": {"type": "string"},
        },
        "required": ["success"],
        "additionalProperties": False,
    },
)
def analyze_prd(prd_text: str, project_name: str) -> Dict[str, Any]:
    try:
        analysis = analyze(prd_text, project_name)
        return {
            "success": True,
            "analysis": analysis,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@mcp_app.tool(
    name="generate_project",
    title="Generate Project",
    description="Generate a Spring Boot project from analyzed PRD data.",
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "zip_path": {"type": "string"},
            "message": {"type": "string"},
            "error": {"type": "string"},
        },
        "required": ["success"],
        "additionalProperties": False,
    },
)
def generate_project(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        zip_path = generate(analysis_data)
        return {
            "success": True,
            "zip_path": zip_path,
            "message": f"Project generated successfully at {zip_path}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@mcp_app.tool(
    name="get_api_best_practices",
    title="Get API Best Practices",
    description="Return Spring Boot API design best practices.",
    output_schema={
        "type": "object",
        "properties": {"result": {"type": "string"}},
        "required": ["result"],
        "additionalProperties": False,
    },
)
def _get_api_best_practices_tool() -> Dict[str, str]:
    return {"result": """
Spring Boot REST API Best Practices:

1. URL Design:
- Use nouns, not verbs (GET /users, not GET /getUsers)
- Use plural nouns for collections
- Use kebab-case for multi-word resources
- Use query parameters for filtering/sorting

2. HTTP Methods:
- GET: Retrieve resources
- POST: Create new resources
- PUT: Update entire resource
- PATCH: Partial updates
- DELETE: Remove resources

3. Status Codes:
- 200: Success
- 201: Created
- 204: No Content (for deletes)
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

4. Response Format:
- Use consistent JSON structure
- Include pagination info for lists
- Use meaningful error messages

5. Error Handling:
- Use @ControllerAdvice for global exception handling
- Return consistent error response format
- Log errors appropriately
    """}


def get_api_best_practices() -> str:
    return _get_api_best_practices_tool()["result"]


@mcp_app.tool(
    name="get_spring_boot_context",
    title="Get Spring Boot Context",
    description="Return Spring Boot context guidance for given requirements.",
    output_schema={
        "type": "object",
        "properties": {"result": {"type": "string"}},
        "required": ["result"],
        "additionalProperties": False,
    },
)
def _get_spring_boot_context_tool(requirements: str) -> Dict[str, str]:
    if not requirements or not isinstance(requirements, str):
        return {"result": get_api_best_practices()}

    summary = requirements.strip()
    if len(summary) > 300:
        summary = summary[:300] + "..."

    return {
        "result": (
            f"Spring Boot generation context for requirements:\n{summary}\n\n"
            "Use standard Spring Boot REST patterns, JPA entity modeling, and service/controller separation."
        )
    }


def get_spring_boot_context(requirements: str) -> str:
    return _get_spring_boot_context_tool(requirements=requirements)["result"]


@mcp_app.tool(
    name="get_project_structure",
    title="Get Project Structure",
    description="Generate recommended Spring Boot project structure.",
    output_schema={"type": "object", "additionalProperties": True},
)
def generate_code_structure(project_name: str) -> Dict[str, Any]:
    return {
        "project_name": project_name,
        "structure": {
            "src/main/java/com/example": {
                "controller": ["MainController.java"],
                "entity": ["User.java", "Product.java"],
                "repository": ["UserRepository.java", "ProductRepository.java"],
                "service": ["UserService.java", "ProductService.java"],
                "config": ["SecurityConfig.java", "WebConfig.java"],
            },
            "src/main/resources": {
                "application.properties": "Spring configuration",
                "templates": ["index.html"],
                "static": ["css", "js", "images"],
            },
            "src/test/java": {
                "controller": ["MainControllerTest.java"],
                "service": ["UserServiceTest.java"],
            },
        },
        "dependencies": [
            "spring-boot-starter-web",
            "spring-boot-starter-data-jpa",
            "spring-boot-starter-security",
            "spring-boot-starter-validation",
            "spring-boot-starter-thymeleaf",
            "h2",
        ],
    }


@mcp_app.tool(
    name="validate_entity_design",
    title="Validate Entity Design",
    description="Validate entity metadata for Spring Boot generation.",
    output_schema={"type": "object", "additionalProperties": True},
)
def validate_entity_design(entity_data: Dict[str, Any]) -> Dict[str, Any]:
    validation_results = {
        "valid": True,
        "issues": [],
        "suggestions": [],
    }

    if not isinstance(entity_data, dict):
        return {
            "valid": False,
            "issues": ["Entity data must be a dictionary"],
            "suggestions": [],
        }

    if "name" not in entity_data:
        validation_results["valid"] = False
        validation_results["issues"].append("Entity missing 'name' field")

    if "fields" not in entity_data:
        validation_results["valid"] = False
        validation_results["issues"].append("Entity missing 'fields' array")
    else:
        for field in entity_data["fields"]:
            if not isinstance(field, dict):
                validation_results["valid"] = False
                validation_results["issues"].append(
                    f"Field entry must be a dictionary: {field}"
                )
                continue
            if "name" not in field:
                validation_results["valid"] = False
                validation_results["issues"].append(f"Field missing 'name': {field}")
            if "type" not in field:
                validation_results["valid"] = False
                validation_results["issues"].append(f"Field missing 'type': {field}")

    if validation_results["valid"]:
        validation_results["suggestions"].extend(
            [
                "Consider adding @Entity annotation",
                "Add @Id field for primary key",
                "Consider using Lombok annotations",
            ]
        )

    return validation_results


@mcp_app.tool(
    name="validate_database_schema",
    title="Validate Database Schema",
    description="Validate relational database design, normalization, and indexing.",
    output_schema={"type": "object", "additionalProperties": True},
)
def validate_database_schema(entities: Dict[str, Any]) -> Dict[str, Any]:
    validation_results = {
        "valid": True,
        "issues": [],
        "suggestions": [],
        "indexes": [],
        "relationships": [],
    }

    if "entities" not in entities:
        validation_results["valid"] = False
        validation_results["issues"].append("No entities found for database validation")
        return validation_results

    entity_list = entities["entities"]
    entity_names = [e.get("name", "").lower() for e in entity_list]

    for entity in entity_list:
        name = entity.get("name", "Unknown")
        fields = entity.get("fields", [])

        has_id = any(
            f.get("name", "").lower() in ["id", "entityid", f"{name.lower()}id"]
            for f in fields
        )
        if not has_id:
            validation_results["issues"].append(
                f"Entity '{name}' missing primary key field"
            )
            validation_results["suggestions"].append(
                f"Add @Id field to {name} entity"
            )

        for field in fields:
            field_name = field.get("name", "").lower()
            if "id" in field_name and field_name != "id":
                related_entity = field_name.replace("id", "")
                if related_entity in entity_names:
                    validation_results["relationships"].append(
                        {
                            "from_entity": name,
                            "to_entity": related_entity.capitalize(),
                            "field": field_name,
                            "type": "ManyToOne",
                        }
                    )

    for entity in entity_list:
        name = entity.get("name", "")
        fields = entity.get("fields", [])
        for field in fields:
            field_name = field.get("name", "").lower()
            if any(keyword in field_name for keyword in ["name", "email", "username", "status", "type"]):
                validation_results["indexes"].append(
                    {
                        "entity": name,
                        "field": field_name,
                        "reason": "Commonly queried field",
                    }
                )

    if len(entity_list) > 1:
        validation_results["suggestions"].append(
            "Consider normalizing entities to reduce data redundancy"
        )
        validation_results["suggestions"].append(
            "Review one-to-many relationships for proper foreign key setup"
        )

    return validation_results


@mcp_app.tool(
    name="suggest_dependencies",
    title="Suggest Dependencies",
    description="Recommend Maven dependencies based on detected features.",
    output_schema={"type": "object", "additionalProperties": True},
)
def suggest_dependencies(features: Dict[str, Any]) -> Dict[str, Any]:
    dependencies = {
        "core": [
            "org.springframework.boot:spring-boot-starter-web",
            "org.springframework.boot:spring-boot-starter-data-jpa",
            "org.springframework.boot:spring-boot-starter-validation",
        ],
        "database": [],
        "security": [],
        "caching": [],
        "messaging": [],
        "monitoring": [],
        "testing": [
            "org.springframework.boot:spring-boot-starter-test",
            "org.junit.jupiter:junit-jupiter",
            "org.mockito:mockito-core",
        ],
        "documentation": [],
        "utilities": [],
    }

    requirements_text = features.get("requirements", "").lower()
    entities = features.get("entities", [])

    if "mysql" in requirements_text:
        dependencies["database"].extend(
            [
                "mysql:mysql-connector-java",
                "org.springframework.boot:spring-boot-starter-data-jpa",
            ]
        )
    elif "postgresql" in requirements_text:
        dependencies["database"].extend(
            [
                "org.postgresql:postgresql",
                "org.springframework.boot:spring-boot-starter-data-jpa",
            ]
        )
    elif "mongodb" in requirements_text:
        dependencies["database"].extend(
            ["org.springframework.boot:spring-boot-starter-data-mongodb"]
        )
    else:
        dependencies["database"].append("com.h2database:h2")

    if any(keyword in requirements_text for keyword in ["login", "auth", "security", "user", "password"]):
        dependencies["security"].extend(
            [
                "org.springframework.boot:spring-boot-starter-security",
                "io.jsonwebtoken:jjwt-api:0.11.5",
                "io.jsonwebtoken:jjwt-impl:0.11.5",
                "io.jsonwebtoken:jjwt-jackson:0.11.5",
            ]
        )

    if any(keyword in requirements_text for keyword in ["cache", "performance", "redis"]):
        dependencies["caching"].extend(
            [
                "org.springframework.boot:spring-boot-starter-cache",
                "org.springframework.boot:spring-boot-starter-data-redis",
            ]
        )

    if any(keyword in requirements_text for keyword in ["message", "queue", "kafka", "rabbitmq"]):
        if "kafka" in requirements_text:
            dependencies["messaging"].append("org.springframework.kafka:spring-kafka")
        elif "rabbitmq" in requirements_text:
            dependencies["messaging"].append(
                "org.springframework.boot:spring-boot-starter-amqp"
            )

    if any(keyword in requirements_text for keyword in ["monitor", "health", "metrics"]):
        dependencies["monitoring"].extend(
            [
                "org.springframework.boot:spring-boot-starter-actuator",
                "io.micrometer:micrometer-registry-prometheus",
            ]
        )

    dependencies["documentation"].extend(
        ["org.springdoc:springdoc-openapi-starter-webmvc-ui:2.2.0"]
    )

    has_dates = any(
        any("date" in str(field).lower() or "time" in str(field).lower()
            for field in entity.get("fields", []))
        for entity in entities
    )
    if has_dates:
        dependencies["utilities"].append(
            "org.springframework.boot:spring-boot-starter-validation"
        )

    dependencies = {k: v for k, v in dependencies.items() if v}

    return {
        "dependencies": dependencies,
        "pom_xml_snippet": _generate_pom_xml(dependencies),
        "explanations": {
            "core": "Essential Spring Boot starters for web and data",
            "database": "Database connectivity and JPA support",
            "security": "Authentication and authorization",
            "caching": "Performance optimization with caching",
            "messaging": "Asynchronous messaging support",
            "monitoring": "Application monitoring and metrics",
            "testing": "Unit and integration testing",
            "documentation": "API documentation generation",
            "utilities": "Additional utility libraries",
        },
    }


def _generate_pom_xml(dependencies: Dict[str, List[str]]) -> str:
    xml_parts = ["    <dependencies>"]
    for category, deps in dependencies.items():
        xml_parts.append(f"        <!-- {category.title()} Dependencies -->")
        for dep in deps:
            if ":" in dep:
                parts = dep.split(":")
                if len(parts) == 3:
                    group_id, artifact_id, version = parts
                    xml_parts.append("        <dependency>")
                    xml_parts.append(f"            <groupId>{group_id}</groupId>")
                    xml_parts.append(f"            <artifactId>{artifact_id}</artifactId>")
                    xml_parts.append(f"            <version>{version}</version>")
                    xml_parts.append("        </dependency>")
                elif len(parts) == 2:
                    group_id, artifact_id = parts
                    xml_parts.append("        <dependency>")
                    xml_parts.append(f"            <groupId>{group_id}</groupId>")
                    xml_parts.append(f"            <artifactId>{artifact_id}</artifactId>")
                    xml_parts.append("        </dependency>")
        xml_parts.append("")
    xml_parts.append("    </dependencies>")
    return "\n".join(xml_parts)


@mcp_app.tool(
    name="fetch_jira_issue",
    title="Fetch JIRA Issue",
    description="Fetch a JIRA issue by key and extract its content for use as PRD input.",
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "issue_key": {"type": "string"},
            "summary": {"type": "string"},
            "issue_type": {"type": "string"},
            "status": {"type": "string"},
            "project_key": {"type": "string"},
            "content": {"type": "string"},
            "length": {"type": "integer"},
            "error": {"type": "string"},
        },
        "required": ["success"],
        "additionalProperties": False,
    },
)
def fetch_jira_issue(
    issue_key: str,
    jira_url: str = None,
    jira_email: str = None,
    jira_token: str = None,
) -> Dict[str, Any]:
    try:
        client = JiraClient(base_url=jira_url, email=jira_email, api_token=jira_token)
        issue = client.get_issue(issue_key)
        fields = issue.get("fields", {})
        content = client.extract_text_from_issue(issue)
        return {
            "success": True,
            "issue_key": issue_key,
            "summary": fields.get("summary", ""),
            "issue_type": fields.get("issuetype", {}).get("name", ""),
            "status": fields.get("status", {}).get("name", ""),
            "project_key": fields.get("project", {}).get("key", ""),
            "content": content,
            "length": len(content),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "issue_key": issue_key}


@mcp_app.tool(
    name="fetch_jira_project_context",
    title="Fetch JIRA Project Context",
    description="Fetch JIRA project metadata and open-sprint issues for context.",
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "project_name": {"type": "string"},
            "project_key": {"type": "string"},
            "description": {"type": "string"},
            "sprint_issues": {"type": "array", "items": {"type": "object"}},
            "error": {"type": "string"},
        },
        "required": ["success"],
        "additionalProperties": False,
    },
)
def fetch_jira_project_context(
    project_key: str,
    jira_url: str = None,
    jira_email: str = None,
    jira_token: str = None,
) -> Dict[str, Any]:
    try:
        client = JiraClient(base_url=jira_url, email=jira_email, api_token=jira_token)
        project = client.get_project(project_key)
        sprint_issues = client.search_issues(
            jql=f"project = {project_key} AND sprint in openSprints() ORDER BY created DESC",
            max_results=20,
        )
        return {
            "success": True,
            "project_name": project.get("name", ""),
            "project_key": project_key,
            "description": project.get("description") or "",
            "sprint_issues": [
                {
                    "key": i["key"],
                    "summary": i["fields"]["summary"],
                    "type": i["fields"]["issuetype"]["name"],
                    "status": i["fields"]["status"]["name"],
                }
                for i in sprint_issues
            ],
        }
    except Exception as e:
        return {"success": False, "error": str(e), "project_key": project_key}


@mcp_app.tool(
    name="generate_jira_comment_summary",
    title="Generate JIRA Comment Summary",
    description="Use LLM to write a contextual comment summary for a JIRA ticket based on its description and what was generated.",
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "summary": {"type": "string"},
            "error": {"type": "string"},
        },
        "required": ["success"],
        "additionalProperties": False,
    },
)
def generate_jira_comment_summary(
    issue_summary: str,
    issue_content: str,
    entities: List[Dict[str, Any]],
) -> Dict[str, Any]:
    import os as _os
    import requests as _req

    api_key = _os.getenv(
        "OPENROUTER_API_KEY",
        "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",
    )

    entity_lines = []
    for e in entities:
        name = e.get("name", "Unknown")
        ops = [o.get("type", "") for o in e.get("operations", []) if o.get("type")]
        op_str = f" ({', '.join(ops)})" if ops else ""
        entity_lines.append(f"- {name}{op_str}")
    entity_desc = "\n".join(entity_lines) if entity_lines else "- No entities detected"

    prompt = f"""You are a software architect reviewing a completed code generation task.

A Spring Boot project was generated from the following JIRA ticket.

Ticket Title: {issue_summary}

Ticket Description:
{issue_content[:2000]}

What was generated:
{entity_desc}

Write a concise 2-4 sentence comment to post on this JIRA ticket that:
- Explains what was generated and how it directly addresses the ticket requirements
- References specific requirements or acceptance criteria mentioned in the ticket description
- Connects the generated entities to the business needs described
- Uses professional language suitable for a development team

Return only the comment text. No markdown formatting, no bullet points, no headers."""

    try:
        response = _req.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost",
                "X-Title": "Code Generator",
            },
            json={
                "model": "poolside/laguna-m.1:free",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=45,
        )
        response.raise_for_status()
        summary = response.json()["choices"][0]["message"]["content"].strip()
        return {"success": True, "summary": summary}
    except Exception as e:
        # Graceful fallback — still post a comment, just without LLM prose
        fallback = f"Spring Boot project was generated based on the requirements in this ticket: {issue_summary}."
        return {"success": False, "error": str(e), "summary": fallback}


@mcp_app.tool(
    name="post_jira_comment",
    title="Post JIRA Comment",
    description="Post a generation summary comment to a JIRA issue.",
    output_schema={
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "comment_id": {"type": "string"},
            "issue_key": {"type": "string"},
            "error": {"type": "string"},
        },
        "required": ["success"],
        "additionalProperties": False,
    },
)
def post_jira_comment(
    issue_key: str,
    project_name: str,
    entities: List[Dict[str, Any]],
    issue_summary: str = "",
    all_issue_keys: List[str] = None,
    llm_summary: str = "",
    jira_url: str = None,
    jira_email: str = None,
    jira_token: str = None,
) -> Dict[str, Any]:
    try:
        client = JiraClient(base_url=jira_url, email=jira_email, api_token=jira_token)
        adf_body = JiraClient.build_comment_adf(
            project_name=project_name,
            entities=entities,
            issue_key=issue_key,
            issue_summary=issue_summary,
            all_issue_keys=all_issue_keys,
            llm_summary=llm_summary,
        )
        result = client.add_comment(issue_key, adf_body)
        return {
            "success": True,
            "comment_id": result.get("id", ""),
            "issue_key": issue_key,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "issue_key": issue_key}


class MCPServer:
    """Wrapper around the FastMCP App for synchronous and asynchronous use."""

    def __init__(self):
        self.server = mcp_app

    async def call_tool_async(self, tool_name: str, **kwargs: Any) -> Any:
        return await _call_tool_async(tool_name, **kwargs)

    def call_tool(self, tool_name: str, **kwargs: Any) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.call_tool_async(tool_name, **kwargs))
        raise RuntimeError(
            "call_tool() cannot be used from a running event loop. Use call_tool_async() instead."
        )

    async def get_tool_info_async(self) -> Dict[str, Any]:
        tools = await _list_registered_tools()
        tool_info: Dict[str, Any] = {}
        for tool in tools:
            tool_info[tool.name] = {
                "description": tool.description,
                "inputSchema": tool.parameters,
                "outputSchema": tool.output_schema,
                "tags": list(tool.tags) if getattr(tool, "tags", None) else [],
            }
        return tool_info

    def get_tool_info(self) -> Dict[str, Any]:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.get_tool_info_async())
        raise RuntimeError(
            "get_tool_info() cannot be used from a running event loop. Use get_tool_info_async() instead."
        )


server = MCPServer()
