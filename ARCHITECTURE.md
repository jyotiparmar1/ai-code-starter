# Dynamic Feature-Driven Generation Architecture

## Overview

This solution replaces the fixed template approach with a **dynamic, feature-driven system** that:

1. **Analyzes the PRD** to understand requirements
2. **Infers features** from the PRD text (authentication, database, logging, caching, etc.)
3. **Dynamically selects templates and configurations** based on inferred features
4. **Generates all necessary project files** - not just CRUD, but also auth, security, database configs, etc.

## Architecture Components

### 1. Feature Registry (`tools/features.py`)

**Purpose**: Central configuration for all available features and how they map to code generation.

**Key Components**:

- `FEATURE_REGISTRY`: Defines each feature with:
  - Name and description
  - Maven dependencies needed
  - Template files to generate
  - Configuration keys (for application.properties)

- `infer_features_from_prd(analysis_data)`: Analyzes PRD text and infers which features are needed
  - Detects: JWT, OAuth2, RBAC, database types, logging, caching, validation, error handling, API docs, monitoring

- `get_feature_config(features_list)`: Builds combined configuration for enabled features
  - Aggregates dependencies, templates, and configs

**Supported Features**:
- JWT Authentication
- OAuth 2.0
- Role-Based Access Control
- Database (MySQL, PostgreSQL, MongoDB)
- Logging
- Caching (Redis)
- Input Validation
- Error Handling
- API Documentation (Swagger)
- Spring Actuator (Monitoring)

### 2. Enhanced Analyzer (`tools/analyzer.py`)

**Changes**:
- Now returns `raw_analysis` field containing original PRD text
- This text is used by the feature inference system to detect required features

### 3. Dynamic Generator (`tools/generator.py`)

**Changes**:
- Calls `infer_features_from_prd()` to determine enabled features
- Calls `get_feature_config()` to gather all needed dependencies and templates
- Generates feature-specific configurations:
  - `generate_pom()`: Includes feature dependencies
  - `generate_properties()`: Includes feature configurations
  - `generate_feature_configs()`: Creates authentication, security, error handling, database config files
- Enhanced `generate_inference_summary()`: Shows which features were detected and why

**Generated Files**:
- Standard: Entity, Repository, Service, Controller
- Feature-Dependent (dynamic):
  - `JwtTokenProvider.java` (if JWT detected)
  - `JwtAuthenticationFilter.java` (if JWT detected)
  - `SecurityConfig.java` (if auth detected)
  - `GlobalExceptionHandler.java` (if error handling detected)
  - `CacheConfig.java` (if caching detected)
  - `SwaggerConfig.java` (if API docs detected)
  - `application-mysql.yml`, `application-postgres.yml`, `application-mongodb.yml` (if DB detected)
  - `logback-spring.xml` (if logging detected)
  - And more...

### 4. New Templates

Added templates for commonly needed features:
- `SecurityConfig.java.j2` - Spring Security configuration
- `JwtTokenProvider.java.j2` - JWT token generation and validation
- `JwtAuthenticationFilter.java.j2` - JWT authentication filter
- `GlobalExceptionHandler.java.j2` - Centralized exception handling
- `SwaggerConfig.java.j2` - Swagger/OpenAPI configuration
- `CacheConfig.java.j2` - Redis caching configuration
- `application-mysql.yml.j2` - MySQL database config
- `application-postgres.yml.j2` - PostgreSQL database config
- `application-mongodb.yml.j2` - MongoDB database config
- `application-actuator.yml.j2` - Spring Actuator monitoring config

## How It Works

### Example: PRD mentions "user authentication", "database", and "API documentation"

```
PRD: "Users should login with JWT tokens. Data stored in PostgreSQL. API documented with Swagger."
```

**Processing Flow**:

1. **Analyzer** extracts entities (User) and CRUD operations
   - Also returns raw PRD text

2. **Feature Inferrer** analyzes raw text and detects:
   - ✓ "JWT tokens" → `jwt_auth` feature enabled
   - ✓ "PostgreSQL" → `database_postgresql` feature enabled
   - ✓ "Swagger" → `api_documentation` feature enabled

3. **Feature Config** builds combined configuration:
   - Dependencies: jjwt libraries, postgresql driver, springdoc-openapi
   - Templates: JwtTokenProvider, JwtAuthenticationFilter, SecurityConfig, SwaggerConfig, application-postgres.yml
   - Config keys: jwt.secret, jwt.expiration, database connection strings, swagger paths

4. **Generator** creates project with:
   - `src/main/java/com/example/demo/entity/User.java`
   - `src/main/java/com/example/demo/controller/UserController.java`
   - `src/main/java/com/example/demo/service/UserService.java`
   - `src/main/java/com/example/demo/repository/UserRepository.java`
   - `src/main/java/com/example/demo/security/JwtTokenProvider.java` ← NEW
   - `src/main/java/com/example/demo/security/JwtAuthenticationFilter.java` ← NEW
   - `src/main/java/com/example/demo/config/SecurityConfig.java` ← NEW
   - `src/main/java/com/example/demo/config/SwaggerConfig.java` ← NEW
   - `pom.xml` (includes JWT, PostgreSQL, Swagger dependencies) ← DYNAMIC
   - `application.properties` (includes database and JWT configs) ← DYNAMIC
   - `application-postgres.yml` ← NEW
   - `inference-summary.txt` (explains detected features)

5. **Output ZIP** contains complete, runnable Spring Boot project with:
   - Authentication fully configured
   - Database ready for connection
   - API documentation ready at `/swagger-ui.html`

## Extensibility

Adding new features is simple:

1. Add entry to `FEATURE_REGISTRY` in `tools/features.py`:
   ```python
   "rabbitmq_messaging": {
       "name": "RabbitMQ Messaging",
       "dependencies": ["org.springframework.boot:spring-boot-starter-amqp"],
       "templates": ["RabbitMqConfig.java"],
       "config_keys": {"spring.rabbitmq.host": "localhost"},
   }
   ```

2. Add detection keyword in `infer_features_from_prd()`:
   ```python
   if any(term in raw_text for term in ["rabbitmq", "message queue", "async"]):
       features["enabled"].append("rabbitmq_messaging")
   ```

3. Create template `templates/RabbitMqConfig.java.j2`

## Benefits

✓ **No Template Constraints** - Dynamically generates any project configuration needed
✓ **Smart Detection** - AI-powered feature inference from PRD text
✓ **Extensible** - Easy to add new features and templates
✓ **Complete Runnable Code** - Not just scaffolding, but working implementations
✓ **Configuration Management** - All feature configs bundled together
✓ **Clear Documentation** - inference-summary.txt explains all detected features

## Next Steps

To use this new system:

1. Upload a PRD that mentions desired features (auth, database, caching, etc.)
2. System automatically detects and generates complete project with those features
3. Generated ZIP is immediately runnable with proper configurations

Example PRD text that will work well:
- "Users authenticate using JWT"
- "Use PostgreSQL for data persistence"
- "Implement caching with Redis"
- "Document API with Swagger"
- "Implement role-based access control"
