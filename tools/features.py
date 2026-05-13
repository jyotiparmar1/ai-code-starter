"""
Feature Registry and Feature Inference System

This module defines the feature flags and their configurations,
including dependencies, template selections, and configuration needs.
"""

import json
import os
import requests
import re

# OpenRouter API configuration, with environment override.
OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "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"
)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "poolside/laguna-m.1:free"


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


def infer_features_with_llm(raw_text: str) -> list:
    """
    Use LLM to infer enabled features from PRD text.
    
    Args:
        raw_text: The raw PRD analysis text
    
    Returns:
        List of enabled feature keys
    """
    feature_keys = list(FEATURE_REGISTRY.keys())
    prompt = f"""
You are a senior Spring Boot architect.
Analyze the PRD text and identify which features from the following list are required or implied.
Return STRICT JSON ONLY with no explanatory text.

Available features: {', '.join(feature_keys)}

PRD Text:
{raw_text}

JSON FORMAT:
{{
  "enabled_features": ["jwt_auth", "database_mysql"],
  "reasoning": "Brief explanation for each feature"
}}
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Feature Extractor"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        data = extract_json_from_response(content)
        return data.get("enabled_features", [])
    except Exception as e:
        # Fallback to manual inference if LLM fails
        print(f"LLM feature inference failed: {e}. Falling back to manual.")
        return infer_features_manually(raw_text)


def infer_features_manually(raw_text: str) -> list:
    """Manual keyword-based feature inference as fallback."""
    raw_lower = raw_text.lower()
    enabled = []
    if any(term in raw_lower for term in ["jwt", "token", "authentication", "login"]):
        enabled.append("jwt_auth")
    if any(term in raw_lower for term in ["oauth", "google auth"]):
        enabled.append("oauth2")
    if any(term in raw_lower for term in ["role", "permission", "rbac"]):
        enabled.append("role_based_access")
    if any(term in raw_lower for term in ["mysql"]):
        enabled.append("database_mysql")
    elif any(term in raw_lower for term in ["postgres", "postgresql"]):
        enabled.append("database_postgresql")
    elif any(term in raw_lower for term in ["mongodb"]):
        enabled.append("database_mongodb")
    if any(term in raw_lower for term in ["log", "logging"]):
        enabled.append("logging")
    if any(term in raw_lower for term in ["cache", "redis"]):
        enabled.append("caching")
    if any(term in raw_lower for term in ["validation"]):
        enabled.append("validation")
    if any(term in raw_lower for term in ["error", "exception"]):
        enabled.append("error_handling")
    if any(term in raw_lower for term in ["swagger", "openapi"]):
        enabled.append("api_documentation")
    if any(term in raw_lower for term in ["health", "actuator"]):
        enabled.append("actuator")
    return enabled

# Feature Definitions: Maps feature flags to their configurations
FEATURE_REGISTRY = {
    "jwt_auth": {
        "name": "JWT Authentication",
        "description": "JWT token-based authentication",
        "dependencies": [
            "org.springframework.boot:spring-boot-starter-security",
            "io.jsonwebtoken:jjwt-api:0.11.5",
            "io.jsonwebtoken:jjwt-impl:0.11.5",
            "io.jsonwebtoken:jjwt-jackson:0.11.5",
        ],
        "templates": ["JwtTokenProvider.java", "JwtAuthenticationFilter.java", "SecurityConfig.java"],
        "config_keys": {"jwt.secret": "your-secret-key-change-in-production", "jwt.expiration": "86400000"},
    },
    "oauth2": {
        "name": "OAuth 2.0",
        "description": "OAuth 2.0 authentication",
        "dependencies": [
            "org.springframework.boot:spring-boot-starter-oauth2-client",
            "org.springframework.boot:spring-boot-starter-oauth2-resource-server",
        ],
        "templates": ["OAuth2Config.java"],
        "config_keys": {"spring.security.oauth2.client.registration.google.client-id": "your-client-id"},
    },
    "role_based_access": {
        "name": "Role-Based Access Control",
        "description": "RBAC with roles and permissions",
        "dependencies": [
            "org.springframework.boot:spring-boot-starter-security",
        ],
        "templates": ["Role.java", "Permission.java", "RoleRepository.java", "SecurityConfig.java"],
        "config_keys": {},
    },
    "database_mysql": {
        "name": "MySQL Database",
        "description": "MySQL connectivity and configuration",
        "dependencies": [
            "org.springframework.boot:spring-boot-starter-data-jpa",
            "mysql:mysql-connector-java:8.0.33",
        ],
        "templates": ["application-mysql.yml"],
        "config_keys": {
            "spring.datasource.url": "jdbc:mysql://localhost:3306/demo_db",
            "spring.datasource.username": "root",
            "spring.datasource.password": "password",
            "spring.jpa.hibernate.ddl-auto": "update",
            "spring.jpa.show-sql": "true",
        },
    },
    "database_postgresql": {
        "name": "PostgreSQL Database",
        "description": "PostgreSQL connectivity and configuration",
        "dependencies": [
            "org.springframework.boot:spring-boot-starter-data-jpa",
            "org.postgresql:postgresql:42.5.4",
        ],
        "templates": ["application-postgres.yml"],
        "config_keys": {
            "spring.datasource.url": "jdbc:postgresql://localhost:5432/demo_db",
            "spring.datasource.username": "postgres",
            "spring.datasource.password": "password",
            "spring.jpa.database-platform": "org.hibernate.dialect.PostgreSQLDialect",
            "spring.jpa.hibernate.ddl-auto": "update",
        },
    },
    "database_mongodb": {
        "name": "MongoDB Database",
        "description": "MongoDB connectivity and configuration",
        "dependencies": [
            "org.springframework.boot:spring-boot-starter-data-mongodb",
        ],
        "templates": ["application-mongodb.yml"],
        "config_keys": {
            "spring.data.mongodb.uri": "mongodb://localhost:27017/demo_db",
        },
    },
    "logging": {
        "name": "Structured Logging",
        "description": "SLF4J and Logback logging",
        "dependencies": [
            "org.springframework.boot:spring-boot-starter-logging",
        ],
        "templates": ["logback-spring.xml"],
        "config_keys": {"logging.level.root": "INFO"},
    },
    "caching": {
        "name": "Caching",
        "description": "Redis caching support",
        "dependencies": [
            "org.springframework.boot:spring-boot-starter-data-redis",
            "redis.clients:jedis",
        ],
        "templates": ["CacheConfig.java"],
        "config_keys": {"spring.redis.host": "localhost", "spring.redis.port": "6379"},
    },
    "validation": {
        "name": "Input Validation",
        "description": "Bean validation and annotations",
        "dependencies": [
            "org.springframework.boot:spring-boot-starter-validation",
        ],
        "templates": [],
        "config_keys": {},
    },
    "error_handling": {
        "name": "Global Error Handling",
        "description": "Centralized exception handling",
        "dependencies": [],
        "templates": ["GlobalExceptionHandler.java"],
        "config_keys": {},
    },
    "api_documentation": {
        "name": "API Documentation (Swagger/OpenAPI)",
        "description": "Swagger/OpenAPI documentation",
        "dependencies": [
            "org.springdoc:springdoc-openapi-starter-webmvc-ui:2.0.2",
        ],
        "templates": ["SwaggerConfig.java"],
        "config_keys": {
            "springdoc.swagger-ui.path": "/swagger-ui.html",
            "springdoc.api-docs.path": "/v3/api-docs",
        },
    },
    "actuator": {
        "name": "Spring Boot Actuator",
        "description": "Health checks and metrics",
        "dependencies": [
            "org.springframework.boot:spring-boot-starter-actuator",
        ],
        "templates": ["application-actuator.yml"],
        "config_keys": {
            "management.endpoints.web.exposure.include": "health,metrics",
            "management.endpoint.health.show-details": "always",
        },
    },
}


def infer_features_from_prd(analysis_data: dict) -> dict:
    """
    Infer feature flags from PRD analysis results using LLM.
    
    Args:
        analysis_data: Dictionary with 'raw_analysis' and 'entities' keys
    
    Returns:
        Dictionary with 'features' (enabled feature list) and 'config' keys
    """
    raw_text = analysis_data.get("raw_analysis", "")
    
    # Use LLM for feature inference
    enabled_features = infer_features_with_llm(raw_text)
    
    features = {
        "enabled": enabled_features,
        "config": {},
        "inferred_reason": [f"LLM identified: {', '.join(enabled_features)}"],
    }

    return features


def get_feature_config(features_list: list) -> dict:
    """
    Build combined configuration for enabled features.
    
    Args:
        features_list: List of enabled feature keys
    
    Returns:
        Combined configuration dictionary
    """
    config = {
        "dependencies": [],
        "templates": [],
        "config_keys": {},
        "enabled_features": [],
    }

    for feature in features_list:
        if feature in FEATURE_REGISTRY:
            registry = FEATURE_REGISTRY[feature]
            config["enabled_features"].append(registry["name"])
            config["dependencies"].extend(registry["dependencies"])
            config["templates"].extend(registry["templates"])
            config["config_keys"].update(registry["config_keys"])

    # Remove duplicate dependencies
    config["dependencies"] = list(set(config["dependencies"]))

    return config
