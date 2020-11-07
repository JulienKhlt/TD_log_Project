import logging
import re
from pathlib import Path

from sqlalchemy.orm import sessionmaker

from src.bdd.Config import Config
from src.bdd.Project import Project, ProjectManager
from src.bdd.bdd import engine, Session

from src.bdd.Module import Module
from src.bdd.Import import Import


def index(project_dir, ensure_package=False, onedir=False):
    """Return a list that contains all the .py files
    part of the project (ie all subdirectory)

        :param project_dir: The root directory of the project.
    """

    if ensure_package and not project_dir.joinpath('__init__.py').exists():
        return []

    path_list = []

    for child in project_dir.iterdir():
        if child.suffix == '.py':
            path_list.append(child)
        if child.is_dir() and not onedir:
            path_list += index(child, True)

    return path_list


IGNORE_DIRS = ['site-packages', '__pycache__']


def create_project(project):
    session = Session()

    # check if project exists.
    query_result = session.query(Project.path).filter_by(name=project.name).first()
    if query_result:
        print(f"{project.name} already exists at {query_result[0]}")
        return

    project_path = Path(project.path).resolve()

    # index external modules as project
    # Way too heavy, we are gonna change that!
    if not project.external:
        search_paths = project.config.get_python_module_search_path()
        for string_path in search_paths:
            path = Path(string_path).resolve()
            match1, match2 = re.search(str(path), str(project_path)), re.search(str(project_path), str(path))
            if match1 or match2:
                continue

            if path.is_dir():
                results = list(path.glob('*.py'))
                if results:
                    print(f"Indexing {path.name} as single directory.")
                    create_project(Project(name=path.name,
                                           path=str(path.resolve()),
                                           external=True,
                                           onedir=True,
                                           config=Config(python_home=project.config.python_home)))
                for child in path.iterdir():
                    if child.joinpath('__init__.py').exists():
                        version = project.config.get_version(child)
                        create_project(Project(name=child.name,
                                               path=str(child.resolve()),
                                               external=True,
                                               version=version,
                                               config=Config(python_home=project.config.python_home)))

    # index files

    # index modules
    print(f"Indexing project {project.name}...")
    modules_path = index(Path(project.path), onedir=project.onedir)

    if not modules_path:
        print(f"{project.name} is not a python project.")
        return

    session.add(project)

    for module_path in modules_path:
        project.add_module(module_path)

    # Update imports
    project.bind_imports(session)

    # add project to database
    session.commit()


def remove_project(project_name):

    session = Session()

    # check if project exists.
    query_result = session.query(Project).filter_by(name=project_name).first()
    if not query_result:
        print(f"{project_name} doesn't not exist.")
        return

    session.delete(query_result)
    session.commit()

def purge():
    """Empty database. CAN'T BE UNDONE!"""

    print("Do you really want to purge? (y/n)")
    answer = input()

    if answer == 'y':
        print("Purging...")
        session = Session()

        query_results = session.query(Project).all()

        for project in query_results:
            print(f"Removing {project.name}")
            session.delete(project)

        session.commit()

def bind_import(project_name):

    session = Session()

    # check if project exists.
    query_result = session.query(Project).filter_by(name=project_name).first()
    if not query_result:
        print(f"{project_name} doesn't not exist.")
        return

    query_result.bind_imports(session)

if __name__ == '__main__':
    purge()
    # create_project(Project(name="AutoComplete", path="/home/pglandon/PycharmProjects/AutoComplete/src",
    #                        config=Config(python_home="/home/pglandon/PycharmProjects/AutoComplete/venv")))
    # bind_import("AutoComplete")

    logging.basicConfig(level=logging.INFO)
    ProjectManager.initialize(Session)

    logging.basicConfig(level=logging.DEBUG)
    remove_project('AutoComplete')

    ProjectManager().register_project('AutoComplete', "/home/pglandon/PycharmProjects/AutoComplete/",
                                      external=False, fast=True,
                                      from_path="/home/pglandon/PycharmProjects/AutoComplete/src")

