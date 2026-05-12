"""
MCP Server for Spring Boot Code Generation
Provides tools and context for enhanced Spring Boot development
Simplified implementation without external MCP dependencies
"""

from typing import Dict, Any
import json

class MCPServer:
    """Simplified MCP Server implementation"""

    def __init__(self):
        self.tools = {
            "get_spring_boot_context": self.get_spring_boot_context,
            "validate_entity_design": self.validate_entity_design,
            "get_api_best_practices": self.get_api_best_practices,
            "generate_code_structure": self.generate_code_structure
        }

    def get_spring_boot_context(self, requirements: str) -> str:
        """
        Get Spring Boot specific context and best practices based on requirements.

        Args:
            requirements: The business requirements text

        Returns:
            Enhanced context for Spring Boot development
        """
        context = """
        Spring Boot Best Practices Context:

        1. Entity Design:
        - Use JPA annotations (@Entity, @Id, @GeneratedValue)
        - Implement proper validation with Bean Validation
        - Use Lombok for boilerplate reduction
        - Follow naming conventions (PascalCase for classes)

        2. Repository Layer:
        - Extend JpaRepository for CRUD operations
        - Use @Query for custom queries
        - Implement pagination and sorting

        3. Service Layer:
        - Use @Service annotation
        - Implement business logic
        - Handle transactions with @Transactional

        4. Controller Layer:
        - Use @RestController for REST APIs
        - Implement proper HTTP status codes
        - Use @Valid for request validation
        - Implement error handling

        5. Security:
        - Use Spring Security for authentication/authorization
        - Implement JWT tokens for stateless auth
        - Configure CORS properly

        6. Configuration:
        - Use application.properties/application.yml
        - Externalize configuration
        - Use profiles for different environments

        7. Testing:
        - Use @SpringBootTest for integration tests
        - Use @MockBean for mocking dependencies
        - Implement unit tests with JUnit and Mockito
        """

        # Analyze requirements for specific patterns
        if "user" in requirements.lower() or "login" in requirements.lower():
            context += "\n\nUser Management Specific:\n"
            context += "- Implement User entity with roles\n"
            context += "- Use BCrypt for password hashing\n"
            context += "- Add authentication endpoints\n"

        if "product" in requirements.lower() or "inventory" in requirements.lower():
            context += "\n\nProduct Management Specific:\n"
            context += "- Implement Product entity with categories\n"
            context += "- Add inventory tracking\n"
            context += "- Implement search and filtering\n"

        return context

    def validate_entity_design(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate entity design against Spring Boot best practices.

        Args:
            entity_data: Entity structure to validate

        Returns:
            Validation results with suggestions
        """
        validation_results = {
            "valid": True,
            "issues": [],
            "suggestions": []
        }

        # Check entity structure
        if "name" not in entity_data:
            validation_results["valid"] = False
            validation_results["issues"].append("Entity missing 'name' field")

        if "fields" not in entity_data:
            validation_results["valid"] = False
            validation_results["issues"].append("Entity missing 'fields' array")
        else:
            # Validate fields
            for field in entity_data["fields"]:
                if "name" not in field:
                    validation_results["issues"].append(f"Field missing 'name': {field}")
                if "type" not in field:
                    validation_results["issues"].append(f"Field missing 'type': {field}")

        # Add suggestions
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

    def call_tool(self, tool_name: str, **kwargs):
        """Call a tool by name"""
        if tool_name in self.tools:
            return self.tools[tool_name](**kwargs)
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