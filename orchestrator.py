from tools.parser import parse
from tools.analyzer import analyze
from tools.generator import generate

def run_pipeline(file_path):
    text = parse(file_path)
    structured_data = analyze(text)
    zip_path = generate(structured_data)

    return zip_path