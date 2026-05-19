import os
import re
import shutil
import zipfile
from jinja2 import Environment, FileSystemLoader
from tools.features import infer_features_from_prd, get_feature_config

env = Environment(loader=FileSystemLoader("templates"))

BASE_PACKAGE = "com.example.demo"


def generate(data):
    """
    Generate Spring Boot project with dynamically selected features based on PRD analysis.
    
    Args:
        data: Dictionary with entities, project_name, raw_analysis (from analyzer)
    
    Returns:
        Path to generated project.zip
    """
    base_path = "output/project"
    clean_output(base_path)
    source_root, resources_root = create_project_structure(base_path)

    # Infer features from PRD analysis
    features_info = infer_features_from_prd(data)
    feature_config = get_feature_config(features_info["enabled"])
    
    # Generate core components
    generate_main_application(source_root)
    generate_properties(resources_root, feature_config)
    generate_pom(base_path, feature_config)
    generate_feature_configs(source_root, resources_root, feature_config)
    generate_inference_summary(base_path, data, features_info)

    # Generate entity-specific components
    for entity in data.get("entities", []):
        normalize_entity(entity)
        generate_entity(entity, source_root)
        generate_repository(entity, source_root)
        generate_service(entity, source_root)
        generate_controller(entity, source_root)

    zip_path = "output/project.zip"
    zip_project(base_path, zip_path)
    return zip_path


def clean_output(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def create_project_structure(base_path):
    package_path = os.path.join(base_path, "src", "main", "java", *BASE_PACKAGE.split("."))
    resources_path = os.path.join(base_path, "src", "main", "resources")

    for path in [package_path, resources_path]:
        os.makedirs(path, exist_ok=True)

    # Create folders for all component types
    for folder in ["entity", "controller", "service", "repository", "config", "security", "exception"]:
        os.makedirs(os.path.join(package_path, folder), exist_ok=True)

    return package_path, resources_path


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def normalize_entity(entity: dict):
    entity["name"] = normalize_java_name(entity.get("name", "GeneratedEntity"))
    entity["table_name"] = entity.get("table_name", default_table_name(entity["name"]))
    entity["fields"] = entity.get("fields", []) or [{"name": "name", "type": "String"}]
    for field in entity["fields"]:
        field["name"] = sanitize_field_name(field.get("name", "field"))
        field["type"] = field.get("type", "String")
        field["method_name"] = field["name"][0].upper() + field["name"][1:]
    entity["fields"] = [field for field in entity["fields"] if field["name"] != "id"]
    if not entity["fields"]:
        entity["fields"] = [{"name": "name", "type": "String", "method_name": "Name"}]
    operations = entity.get("operations")
    if not isinstance(operations, list):
        operations = []
    entity["operations"] = [normalize_operation(op, entity["name"]) for op in operations]
    if not entity["operations"]:
        entity["operations"] = default_crud_operations(entity["name"])


def normalize_java_name(value: str) -> str:
    if not value or not isinstance(value, str):
        return "GeneratedEntity"
    parts = [part for part in re.split(r"[^A-Za-z0-9]", value) if part]
    if not parts:
        return "GeneratedEntity"
    normalized = "".join(part.capitalize() for part in parts)
    if normalized[0].isdigit():
        normalized = "Entity" + normalized
    return normalized


def sanitize_field_name(name: str) -> str:
    if not name or not isinstance(name, str):
        return "field"
    parts = [part for part in re.split(r"[^A-Za-z0-9]", name) if part]
    if not parts:
        return "field"
    sanitized = parts[0][0].lower() + parts[0][1:] if parts[0] else ""
    sanitized += "".join(part[0].upper() + part[1:] if part else "" for part in parts[1:])
    if sanitized and sanitized[0].isdigit():
        sanitized = "field" + sanitized
    return sanitized


def default_table_name(entity_name: str) -> str:
    name = entity_name.lower()
    if name.endswith("s"):
        return name
    return f"{name}s"


def normalize_operation(operation: dict, entity_name: str) -> dict:
    op_type = str(operation.get("type", "READ")).upper()
    method = str(operation.get("method", "")).upper().strip()
    endpoint = str(operation.get("endpoint", "")).strip()
    description = str(operation.get("description", "")).strip()
    base = f"/{entity_name.lower()}s"
    if op_type not in {"CREATE", "READ", "UPDATE", "DELETE"}:
        op_type = "READ"
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        method = default_http_method(op_type)
    if not endpoint:
        endpoint = default_endpoint(entity_name, op_type)
    relative_path = endpoint
    if endpoint.startswith(base):
        relative_path = endpoint[len(base):]
        if relative_path == "":
            relative_path = "/"

    path_vars = re.findall(r"\{([^}]+)\}", endpoint)
    params = []
    for var in path_vars:
        param_name = sanitize_field_name(var)
        params.append({
            "annotation": "@PathVariable",
            "type": "Long",
            "name": param_name,
            "path_variable_name": var,
        })

    if op_type == "CREATE":
        method_name = f"create{entity_name}"
        params = [{"annotation": "@RequestBody", "type": entity_name, "name": "payload"}]
        return_type = entity_name
    elif op_type == "READ":
        if path_vars:
            first_var = path_vars[0]
            if first_var.lower() == "id":
                method_name = f"get{entity_name}ById"
                return_type = entity_name
            else:
                suffix = "".join(part[0].upper() + part[1:] if part else "" for part in re.split(r"[^A-Za-z0-9]", first_var) if part)
                method_name = f"get{entity_name}sBy{suffix or 'Criteria'}"
                return_type = f"List<{entity_name}>"
        else:
            method_name = f"getAll{entity_name}s"
            return_type = f"List<{entity_name}>"
    elif op_type == "UPDATE":
        method_name = f"update{entity_name}"
        params = [
            {"annotation": "@PathVariable", "type": "Long", "name": "id", "path_variable_name": "id"},
            {"annotation": "@RequestBody", "type": entity_name, "name": "payload"},
        ]
        return_type = entity_name
    else:
        method_name = f"delete{entity_name}"
        params = [{"annotation": "@PathVariable", "type": "Long", "name": "id", "path_variable_name": "id"}]
        return_type = "void"

    repository_method = None
    repository_param = None
    if op_type == "READ" and path_vars and path_vars[0].lower() != "id":
        suffix = "".join(part[0].upper() + part[1:] if part else "" for part in re.split(r"[^A-Za-z0-9]", path_vars[0]) if part)
        repository_method = f"findAllBy{suffix or 'Criteria'}"
        repository_param = params[0] if params else None

    return {
        "type": op_type,
        "method": method,
        "endpoint": endpoint,
        "relative_path": relative_path,
        "description": description,
        "defaulted": False,
        "path_vars": path_vars,
        "params": params,
        "method_name": method_name,
        "return_type": return_type,
        "repository_method": repository_method,
        "repository_param": repository_param,
    }


def default_http_method(operation_type: str) -> str:
    return {
        "CREATE": "POST",
        "READ": "GET",
        "UPDATE": "PUT",
        "DELETE": "DELETE",
    }.get(operation_type, "GET")


def default_endpoint(entity_name: str, operation_type: str) -> str:
    base = f"/{entity_name.lower()}s"
    if operation_type == "UPDATE" or operation_type == "DELETE":
        return f"{base}/{{id}}"
    if operation_type == "READ":
        return base
    return base


def default_crud_operations(entity_name: str) -> list:
    return [
        {"type": "CREATE", "method": "POST", "endpoint": default_endpoint(entity_name, "CREATE"), "description": "Create a new %s." % entity_name, "defaulted": True},
        {"type": "READ", "method": "GET", "endpoint": default_endpoint(entity_name, "READ"), "description": "List all %s." % entity_name.lower(), "defaulted": True},
        {"type": "READ", "method": "GET", "endpoint": default_endpoint(entity_name, "READ") + "/{id}", "description": "Get a single %s by ID." % entity_name.lower(), "defaulted": True},
        {"type": "UPDATE", "method": "PUT", "endpoint": default_endpoint(entity_name, "UPDATE"), "description": "Update an existing %s." % entity_name.lower(), "defaulted": True},
        {"type": "DELETE", "method": "DELETE", "endpoint": default_endpoint(entity_name, "DELETE"), "description": "Delete an existing %s." % entity_name.lower(), "defaulted": True},
    ]


def generate_entity(entity, source_root):
    template = env.get_template("entity.java.j2")
    code = template.render(entity=entity, package=BASE_PACKAGE)
    write_file(os.path.join(source_root, "entity", f"{entity['name']}.java"), code)


def generate_repository(entity, source_root):
    template = env.get_template("repository.java.j2")
    code = template.render(entity=entity, package=BASE_PACKAGE)
    write_file(os.path.join(source_root, "repository", f"{entity['name']}Repository.java"), code)


def generate_service(entity, source_root):
    template = env.get_template("service.java.j2")
    code = template.render(entity=entity, package=BASE_PACKAGE)
    write_file(os.path.join(source_root, "service", f"{entity['name']}Service.java"), code)


def generate_controller(entity, source_root):
    template = env.get_template("controller.java.j2")
    code = template.render(entity=entity, package=BASE_PACKAGE)
    write_file(os.path.join(source_root, "controller", f"{entity['name']}Controller.java"), code)


def generate_main_application(source_root):
    template = env.get_template("application.java.j2")
    code = template.render(package=BASE_PACKAGE)
    write_file(os.path.join(source_root, "Application.java"), code)


def generate_properties(resources_root, feature_config=None):
    """Generate application.properties with feature-specific configuration."""
    if feature_config is None:
        feature_config = {"config_keys": {}}
    
    template = env.get_template("application.properties.j2")
    code = template.render(config_keys=feature_config.get("config_keys", {}))
    write_file(os.path.join(resources_root, "application.properties"), code)


def generate_pom(base_path, feature_config=None):
    """Generate pom.xml with feature-specific dependencies."""
    if feature_config is None:
        feature_config = {"dependencies": []}
    
    template = env.get_template("pom.xml.j2")
    code = template.render(dependencies=feature_config.get("dependencies", []))
    write_file(os.path.join(base_path, "pom.xml"), code)


def resolve_template_name(template_name):
    if template_name.endswith(".j2"):
        return template_name
    candidate = template_name + ".j2"
    if os.path.exists(os.path.join("templates", candidate)):
        return candidate
    return template_name


def determine_output_subdir(template_name: str) -> str:
    name = template_name.replace(".j2", "")
    if name.endswith(".java"):
        name = name[: -len(".java")]
    if name in {"JwtTokenProvider", "JwtAuthenticationFilter"}:
        return "security"
    if name in {"SecurityConfig", "SwaggerConfig", "OAuth2Config", "CacheConfig"}:
        return "config"
    if name == "GlobalExceptionHandler":
        return "exception"
    if name in {"Role", "Permission"}:
        return "entity"
    if name == "RoleRepository":
        return "repository"
    return "config"


def generate_feature_configs(source_root, resources_root, feature_config):
    """Generate configuration files for enabled features."""
    if not feature_config:
        return
    
    enabled_templates = feature_config.get("templates", [])
    
    for template_name in enabled_templates:
        full_template_name = resolve_template_name(template_name)
        try:
            template = env.get_template(full_template_name)
            
            if full_template_name.endswith(".java.j2"):
                subdir = determine_output_subdir(full_template_name)
                code = template.render(package=BASE_PACKAGE)
                output_path = os.path.join(source_root, subdir, full_template_name.replace(".j2", ""))
                write_file(output_path, code)
            elif full_template_name.endswith(".yml.j2") or full_template_name.endswith(".yaml.j2"):
                code = template.render()
                output_name = full_template_name.replace(".j2", "")
                output_path = os.path.join(resources_root, output_name)
                write_file(output_path, code)
            elif full_template_name.endswith(".xml.j2"):
                code = template.render()
                output_path = os.path.join(resources_root, full_template_name.replace(".j2", ""))
                write_file(output_path, code)
            else:
                code = template.render(package=BASE_PACKAGE)
                output_path = os.path.join(source_root, "config", full_template_name.replace(".j2", ""))
                write_file(output_path, code)
        except Exception as e:
            print(f"Warning: Could not generate {template_name}: {str(e)}")


def generate_inference_summary(base_path, data, features_info=None):
    """Generate inference summary including features detected from PRD."""
    lines = [f"Project: {data.get('project_name', 'GeneratedProject')}", ""]
    
    if features_info:
        lines.append("=== DETECTED FEATURES ===")
        lines.extend(features_info.get("inferred_reason", []))
        lines.append("")
        lines.append("Enabled Features:")
        for feature in features_info.get("enabled", []):
            lines.append(f"  - {feature}")
        lines.append("")
    
    lines.append("=== INFERRED ENTITIES AND OPERATIONS ===")
    for entity in data.get("entities", []):
        lines.append(f"- Entity: {entity['name']}")
        lines.append(f"  Fields: {', '.join(field['name'] + ':' + field['type'] for field in entity.get('fields', []))}")
        for op in entity.get("operations", []):
            defaulted = " (defaulted)" if op.get("defaulted") else ""
            lines.append(f"  - {op['type']} {op['method']} {op['endpoint']}{defaulted}: {op.get('description', '')}")
        lines.append("")
    
    for note in data.get("inference_notes", []):
        lines.append(f"* {note}")
    lines.append("")
    
    write_file(os.path.join(base_path, "inference-summary.txt"), "\n".join(lines))


def zip_project(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                zipf.write(full_path, os.path.relpath(full_path, folder_path))