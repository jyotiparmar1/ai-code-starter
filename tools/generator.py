import os
import shutil
import zipfile
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))

BASE_PACKAGE = "com.example.demo"

def generate(data):

    base_path = "output/project"

    clean_output(base_path)

    create_project_structure(base_path)

    generate_main_application(base_path)
    generate_properties(base_path)
    generate_pom(base_path)

    for entity in data["entities"]:
        generate_entity(entity, base_path)
        generate_repository(entity, base_path)
        generate_service(entity, base_path)
        generate_controller(entity, base_path)

    zip_path = "output/project.zip"

    zip_project(base_path, zip_path)

    return zip_path


def clean_output(path):

    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path)


def create_project_structure(base_path):

    folders = [
        "entity",
        "controller",
        "service",
        "repository"
    ]

    for folder in folders:
        os.makedirs(f"{base_path}/{folder}", exist_ok=True)


def write_file(path, content):

    with open(path, "w") as f:
        f.write(content)


def generate_entity(entity, base_path):

    template = env.get_template("entity.java.j2")

    code = template.render(
        entity=entity,
        package=BASE_PACKAGE
    )

    write_file(
        f"{base_path}/entity/{entity['name']}.java",
        code
    )


def generate_repository(entity, base_path):

    template = env.get_template("repository.java.j2")

    code = template.render(
        entity=entity,
        package=BASE_PACKAGE
    )

    write_file(
        f"{base_path}/repository/{entity['name']}Repository.java",
        code
    )


def generate_service(entity, base_path):

    template = env.get_template("service.java.j2")

    code = template.render(
        entity=entity,
        package=BASE_PACKAGE
    )

    write_file(
        f"{base_path}/service/{entity['name']}Service.java",
        code
    )


def generate_controller(entity, base_path):

    template = env.get_template("controller.java.j2")

    code = template.render(
        entity=entity,
        package=BASE_PACKAGE
    )

    write_file(
        f"{base_path}/controller/{entity['name']}Controller.java",
        code
    )


def generate_main_application(base_path):

    template = env.get_template("application.java.j2")

    code = template.render(package=BASE_PACKAGE)

    write_file(
        f"{base_path}/Application.java",
        code
    )


def generate_properties(base_path):

    template = env.get_template("application.properties.j2")

    code = template.render()

    write_file(
        f"{base_path}/application.properties",
        code
    )


def generate_pom(base_path):

    template = env.get_template("pom.xml.j2")

    code = template.render()

    write_file(
        f"{base_path}/pom.xml",
        code
    )


def zip_project(folder_path, zip_path):

    with zipfile.ZipFile(zip_path, 'w') as zipf:

        for root, dirs, files in os.walk(folder_path):

            for file in files:

                full_path = os.path.join(root, file)

                zipf.write(
                    full_path,
                    os.path.relpath(full_path, folder_path)
                )