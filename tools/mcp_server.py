"""
MCP Server for Spring Boot Code Generation
Wraps parser, analyzer, generator tools as MCP server tools.
Designed to be called by an MCP client (orchestrator).
"""

import json
import sys
from typing import Dict, Any, List, Optional
from tools.parser import parse
from tools.analyzer import analyze
from tools.generator import generate


class MCPServer:
    """MCP Server that exposes code generation tools"""

    def __init__(self):
        self.tools = {
            "parse_prd": {
                "description": "Parse a PRD file (markdown, docx, or txt) and extract text content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the PRD file to parse"
                        }
                    },
                    "required": ["file_path"]
                },
                "handler": self.parse_prd
            },
            "analyze_prd": {
                "description": "Analyze parsed PRD text to extract entities, CRUD operations, and features",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prd_text": {
                            "type": "string",
                            "description": "The PRD text content to analyze"
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Project name for the generated code"
                        }
                    },
                    "required": ["prd_text", "project_name"]
                },
                "handler": self.analyze_prd
            },
            "generate_project": {
                "description": "Generate a Spring Boot project from analyzed PRD data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "analysis_data": {
                            "type": "object",
                            "description": "The output from analyze_prd containing entities and operations"
                        }
                    },
                    "required": ["analysis_data"]
                },
                "handler": self.generate_project
            },
            "get_api_best_practices": {
                "description": "Return Spring Boot API design best practices",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                },
                "handler": self.get_api_best_practices
            },
            "get_spring_boot_context": {
                "description": "Return Spring Boot context guidance for given requirements",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "requirements": {
                            "type": "string",
                            "description": "The requirements text to analyze for Spring Boot context"
                        }
                    },
                    "required": ["requirements"]
                },
                "handler": self.get_spring_boot_context
            },
            "get_project_structure": {
                "description": "Generate recommended Spring Boot project structure",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Project name for the structure guide"
                        }
                    },
                    "required": ["project_name"]
                },
                "handler": self.generate_code_structure
            },
            "validate_entity_design": {
                "description": "Validate entity design and fields for Spring Boot generation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity_data": {
                            "type": "object",
                            "description": "Entity metadata to validate"
                        }
                    },
                    "required": ["entity_data"]
                },
                "handler": self.validate_entity_design
            },
            "validate_database_schema": {
                "description": "Validate relational database design, normalization, and indexing",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "object",
                            "description": "Dictionary containing entities and their relationships"
                        }
                    },
                    "required": ["entities"]
                },
                "handler": self.validate_database_schema
            },
            "suggest_dependencies": {
                "description": "Recommend Maven dependencies based on detected features",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "features": {
                            "type": "object",
                            "description": "Dictionary containing detected features and requirements"
                        }
                    },
                    "required": ["features"]
                },
                "handler": self.suggest_dependencies
            }
        }

    def parse_prd(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a PRD file and extract text content.
        
        Args:
            file_path: Path to the PRD file
            
        Returns:
            Dictionary with parsed content and metadata
        """
        try:
            content = parse(file_path)
            return {
                "success": True,
                "content": content,
                "file_path": file_path,
                "length": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

    def analyze_prd(self, prd_text: str, project_name: str) -> Dict[str, Any]:
        """
        Analyze PRD text to extract entities and CRUD operations.
        
        Args:
            prd_text: The PRD text content
            project_name: Project name for generated code
            
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis = analyze(prd_text, project_name)
            return {
                "success": True,
                "analysis": analysis
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_project(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a Spring Boot project from analysis data.
        
        Args:
            analysis_data: Output from analyze_prd
            
        Returns:
            Dictionary with generation results and output path
        """
        try:
            zip_path = generate(analysis_data)
            return {
                "success": True,
                "zip_path": zip_path,
                "message": f"Project generated successfully at {zip_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def validate_entity_design(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate entity design and fields for Spring Boot generation.

        Args:
            entity_data: Entity metadata to validate

        Returns:
            Validation results with issue list and suggestions
        """
        validation_results = {
            "valid": True,
            "issues": [],
            "suggestions": []
        }

        if not isinstance(entity_data, dict):
            return {
                "valid": False,
                "issues": ["Entity data must be a dictionary"],
                "suggestions": []
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
                    validation_results["issues"].append(f"Field entry must be a dictionary: {field}")
                    continue
                if "name" not in field:
                    validation_results["valid"] = False
                    validation_results["issues"].append(f"Field missing 'name': {field}")
                if "type" not in field:
                    validation_results["valid"] = False
                    validation_results["issues"].append(f"Field missing 'type': {field}")

        if validation_results["valid"]:
            validation_results["suggestions"].append("Consider adding @Entity annotation")
            validation_results["suggestions"].append("Add @Id field for primary key")
            validation_results["suggestions"].append("Consider using Lombok annotations")

        return validation_results

    def get_api_best_practices(self) -> str:
        """
        Get REST API design best practices for Spring Boot.

        Returns:
            API design guidelines
        """
        return """
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
        - Include HATEOAS links when appropriate

        5. Error Handling:
        - Use @ControllerAdvice for global exception handling
        - Return consistent error response format
        - Log errors appropriately
        """

    def get_spring_boot_context(self, requirements: str) -> str:
        """
        Generate Spring Boot context guidance from requirements.

        Args:
            requirements: A short description of application requirements

        Returns:
            A context string to guide code generation
        """
        if not requirements or not isinstance(requirements, str):
            return self.get_api_best_practices()

        summary = requirements.strip()
        if len(summary) > 300:
            summary = summary[:300] + "..."

        return (
            f"Spring Boot generation context for requirements:\n{summary}\n\n"
            "Use standard Spring Boot REST patterns, JPA entity modeling, and service/controller separation."
        )

    def generate_code_structure(self, project_name: str) -> Dict[str, Any]:
        """
        Generate recommended Spring Boot project structure.

        Args:
            project_name: Name of the project

        Returns:
            Project structure recommendation
        """
        return {
            "project_name": project_name,
            "structure": {
                "src/main/java/com/example": {
                    "controller": ["MainController.java"],
                    "entity": ["User.java", "Product.java"],
                    "repository": ["UserRepository.java", "ProductRepository.java"],
                    "service": ["UserService.java", "ProductService.java"],
                    "config": ["SecurityConfig.java", "WebConfig.java"]
                },
                "src/main/resources": {
                    "application.properties": "Spring configuration",
                    "templates": ["index.html"],
                    "static": ["css", "js", "images"]
                },
                "src/test/java": {
                    "controller": ["MainControllerTest.java"],
                    "service": ["UserServiceTest.java"]
                }
            },
            "dependencies": [
                "spring-boot-starter-web",
                "spring-boot-starter-data-jpa",
                "spring-boot-starter-security",
                "spring-boot-starter-validation",
                "spring-boot-starter-thymeleaf",
                "h2"  # For development
            ]
        }

    def validate_database_schema(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate relational database design, normalization, and indexing.

        Args:
            entities: Dictionary containing entities and their relationships

        Returns:
            Validation results with suggestions for database optimization
        """
        validation_results = {
            "valid": True,
            "issues": [],
            "suggestions": [],
            "indexes": [],
            "relationships": []
        }

        if "entities" not in entities:
            validation_results["valid"] = False
            validation_results["issues"].append("No entities found for database validation")
            return validation_results

        entity_list = entities["entities"]
        entity_names = [e.get("name", "").lower() for e in entity_list]

        # Check for primary keys
        for entity in entity_list:
            name = entity.get("name", "Unknown")
            fields = entity.get("fields", [])

            # Check for ID field
            has_id = any(f.get("name", "").lower() in ["id", "entityid", f"{name.lower()}id"] for f in fields)
            if not has_id:
                validation_results["issues"].append(f"Entity '{name}' missing primary key field")
                validation_results["suggestions"].append(f"Add @Id field to {name} entity")

            # Check for foreign key relationships
            for field in fields:
                field_name = field.get("name", "").lower()
                field_type = field.get("type", "").lower()

                # Detect potential foreign keys
                if "id" in field_name and field_name != "id":
                    related_entity = field_name.replace("id", "")
                    if related_entity in entity_names:
                        validation_results["relationships"].append({
                            "from_entity": name,
                            "to_entity": related_entity.capitalize(),
                            "field": field_name,
                            "type": "ManyToOne"
                        })

        # Suggest indexes for common query patterns
        for entity in entity_list:
            name = entity.get("name", "")
            fields = entity.get("fields", [])

            # Index on commonly queried fields
            for field in fields:
                field_name = field.get("name", "").lower()
                if any(keyword in field_name for keyword in ["name", "email", "username", "status", "type"]):
                    validation_results["indexes"].append({
                        "entity": name,
                        "field": field_name,
                        "reason": "Commonly queried field"
                    })

        # Normalization checks
        if len(entity_list) > 1:
            validation_results["suggestions"].append("Consider normalizing entities to reduce data redundancy")
            validation_results["suggestions"].append("Review one-to-many relationships for proper foreign key setup")

        return validation_results

    def suggest_dependencies(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend Maven dependencies based on detected features.

        Args:
            features: Dictionary containing detected features and requirements

        Returns:
            Dictionary with categorized dependencies and explanations
        """
        dependencies = {
            "core": [
                "org.springframework.boot:spring-boot-starter-web",
                "org.springframework.boot:spring-boot-starter-data-jpa",
                "org.springframework.boot:spring-boot-starter-validation"
            ],
            "database": [],
            "security": [],
            "caching": [],
            "messaging": [],
            "monitoring": [],
            "testing": [
                "org.springframework.boot:spring-boot-starter-test",
                "org.junit.jupiter:junit-jupiter",
                "org.mockito:mockito-core"
            ],
            "documentation": [],
            "utilities": []
        }

        requirements_text = features.get("requirements", "").lower()
        entities = features.get("entities", [])

        # Database dependencies
        if "mysql" in requirements_text:
            dependencies["database"].extend([
                "mysql:mysql-connector-java",
                "org.springframework.boot:spring-boot-starter-data-jpa"
            ])
        elif "postgresql" in requirements_text:
            dependencies["database"].extend([
                "org.postgresql:postgresql",
                "org.springframework.boot:spring-boot-starter-data-jpa"
            ])
        elif "mongodb" in requirements_text:
            dependencies["database"].extend([
                "org.springframework.boot:spring-boot-starter-data-mongodb"
            ])
        else:
            # Default to H2 for development
            dependencies["database"].append("com.h2database:h2")

        # Security dependencies
        if any(keyword in requirements_text for keyword in ["login", "auth", "security", "user", "password"]):
            dependencies["security"].extend([
                "org.springframework.boot:spring-boot-starter-security",
                "io.jsonwebtoken:jjwt-api:0.11.5",
                "io.jsonwebtoken:jjwt-impl:0.11.5",
                "io.jsonwebtoken:jjwt-jackson:0.11.5"
            ])

        # Caching dependencies
        if any(keyword in requirements_text for keyword in ["cache", "performance", "redis"]):
            dependencies["caching"].extend([
                "org.springframework.boot:spring-boot-starter-cache",
                "org.springframework.boot:spring-boot-starter-data-redis"
            ])

        # Messaging dependencies
        if any(keyword in requirements_text for keyword in ["message", "queue", "kafka", "rabbitmq"]):
            if "kafka" in requirements_text:
                dependencies["messaging"].extend([
                    "org.springframework.kafka:spring-kafka"
                ])
            elif "rabbitmq" in requirements_text:
                dependencies["messaging"].extend([
                    "org.springframework.boot:spring-boot-starter-amqp"
                ])

        # Monitoring dependencies
        if any(keyword in requirements_text for keyword in ["monitor", "health", "metrics"]):
            dependencies["monitoring"].extend([
                "org.springframework.boot:spring-boot-starter-actuator",
                "io.micrometer:micrometer-registry-prometheus"
            ])

        # Documentation dependencies
        dependencies["documentation"].extend([
            "org.springdoc:springdoc-openapi-starter-webmvc-ui:2.2.0"
        ])

        # Utility dependencies based on entity analysis
        has_dates = any(
            any("date" in str(field).lower() or "time" in str(field).lower()
                for field in entity.get("fields", []))
            for entity in entities
        )
        if has_dates:
            dependencies["utilities"].append("org.springframework.boot:spring-boot-starter-validation")

        # Remove empty categories
        dependencies = {k: v for k, v in dependencies.items() if v}

        return {
            "dependencies": dependencies,
            "pom_xml_snippet": self._generate_pom_xml(dependencies),
            "explanations": {
                "core": "Essential Spring Boot starters for web and data",
                "database": "Database connectivity and JPA support",
                "security": "Authentication and authorization",
                "caching": "Performance optimization with caching",
                "messaging": "Asynchronous messaging support",
                "monitoring": "Application monitoring and metrics",
                "testing": "Unit and integration testing",
                "documentation": "API documentation generation",
                "utilities": "Additional utility libraries"
            }
        }

    def _generate_pom_xml(self, dependencies: Dict[str, List[str]]) -> str:
        """Generate a sample pom.xml dependencies section"""
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

    def call_tool(self, tool_name: str, **kwargs):
        """Call a tool by name"""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            return tool["handler"](**kwargs)
        else:
            raise ValueError(f"Tool '{tool_name}' not found")

# Create server instance
server = MCPServer()

# Convenience functions for direct access
def get_spring_boot_context(requirements: str) -> str:
    return server.get_spring_boot_context(requirements)

def validate_entity_design(entity_data: Dict[str, Any]) -> Dict[str, Any]:
    return server.validate_entity_design(entity_data)

def get_api_best_practices() -> str:
    return server.get_api_best_practices()

def generate_code_structure(project_name: str) -> Dict[str, Any]:
    return server.generate_code_structure(project_name)

def validate_database_schema(entities: Dict[str, Any]) -> Dict[str, Any]:
    return server.validate_database_schema(entities)

def suggest_dependencies(features: Dict[str, Any]) -> Dict[str, Any]:
    return server.suggest_dependencies(features)