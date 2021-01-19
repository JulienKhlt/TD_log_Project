import argparse
import logging
from src.bdd.Project import ProjectManager
from src.bdd.Config import Config

def drop(project_name):
    """Drop PROJECT_NAME named project."""

    ProjectManager().drop_project(project_name)


def add(project_path):
    """Add project at PROJECT_PATH to Reference Server."""

    project_manager = ProjectManager()
    project_manager.lsp_add_workspace(project_path)

def scan():
    """Look for all modules and add them to the RS in system python path.
    Might take a while! Use this to avoid crash while importing big library
    in a project."""

    config = Config(python_home="/usr/")
    project_manager = ProjectManager()

    paths = config.get_python_module_search_path()

    with open("cli.log", "w") as file:
        for path in paths:
            file.write(str(path.absolute()))
            file.write('\n')

    for path in paths:
        if path.exists() and path.is_dir():
            py_files = list(path.glob("*.py"))
            if len(py_files) > 0:
                project_manager.register_project(path.name, str(path.absolute()), external=True)

            for file in path.iterdir():
                if file.is_dir():
                    if file.joinpath('__init__.py').exists():
                        project_manager.register_project(file.name, str(file.absolute()), external=True)
    # project_manager.register_project("python3", "/usr/lib/python3.9", external=True)
    # project_manager.register_project("yaml", "/usr/lib/python3.9/site-packages/yaml", external=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Perform command on Projects.")
    parser.add_argument('action', choices=['drop', 'add', 'scan'], help="What should I do ?")
    parser.add_argument('project_name', nargs='?', default=None)

    args = parser.parse_args()

    if args.action == 'drop':
        drop(args.project_name)
    elif args.action == 'add':
        add(args.project_name)
    elif args.action == 'scan':
        scan()
