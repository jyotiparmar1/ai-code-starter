from tools.parser import parse
from tools.analyzer import analyze
from tools.generator import generate
from tools.mcp_server import validate_entity_design

def run_pipeline(file_path):
    text = parse(file_path)
    structured_data = analyze(text)

    # Validate entities using MCP
    if "entities" in structured_data:
        for entity in structured_data["entities"]:
            validation = validate_entity_design(entity)
            if not validation.get("valid", True):
                print(f"Warning: Entity validation issues for {entity.get('name', 'Unknown')}: {validation.get('issues', [])}")
            if validation.get("suggestions"):
                print(f"Suggestions for {entity.get('name', 'Unknown')}: {validation.get('suggestions', [])}")

    zip_path = generate(structured_data)

    return zip_path