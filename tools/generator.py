import os
import zipfile
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))

BASE_PACKAGE = "com.example.demo"

def generate(data: dict) -> str:
    base_path = "output/project"
    clean_dir(base_path)

    for entity in data["entities"]:
        generate_entity(entity, base_path)
        generate_repository(entity, base_path)
        generate_service(entity, base_path)
        generate_controller(entity, base_path)

    generate_main_app(base_path)
    generate_pom(base_path)

    zip_path = "output/project.zip"
    zip_folder(base_path, zip_path)

    return zip_path


def clean_dir(path):
    if os.path.exists(path):
        import shutil
        shutil.rmtree(path)
    os.makedirs(path)


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def generate_entity(entity, base_path):
    template = env.get_template("entity.java.j2")
    code = template.render(entity=entity, package=BASE_PACKAGE)
    write_file(f"{base_path}/entity/{entity['name']}.java", code)


def generate_repository(entity, base_path):
    template = env.get_template("repository.java.j2")
    code = template.render(entity=entity, package=BASE_PACKAGE)
    write_file(f"{base_path}/repository/{entity['name']}Repository.java", code)


def generate_service(entity, base_path):
    template = env.get_template("service.java.j2")
    code = template.render(entity=entity, package=BASE_PACKAGE)
    write_file(f"{base_path}/service/{entity['name']}Service.java", code)


def generate_controller(entity, base_path):
    template = env.get_template("controller.java.j2")
    code = template.render(entity=entity, package=BASE_PACKAGE)
    write_file(f"{base_path}/controller/{entity['name']}Controller.java", code)


def generate_main_app(base_path):
    template = env.get_template("main_app.java.j2")
    code = template.render(package=BASE_PACKAGE)
    write_file(f"{base_path}/Application.java", code)


def generate_pom(base_path):
    template = env.get_template("pom.xml.j2")
    code = template.render()
    write_file(f"{base_path}/pom.xml", code)


def zip_folder(folder, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for root, dirs, files in os.walk(folder):
            for file in files:
                path = os.path.join(root, file)
                zipf.write(path, os.path.relpath(path, folder))