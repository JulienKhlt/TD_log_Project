from pathlib import Path

from sqlalchemy.orm import sessionmaker

from bdd.Project import Project
from bdd.bdd import engine, Session

from bdd.Module import Module
from bdd.Import import Import

def index(project_dir):
    """Return a list that contains all the .py files
    part of the project (ie all subdirectory)

        :param project_dir: The root directory of the project.
    """

    print('Indexing project')
    path_list = list(project_dir.glob('**/*.py'))
    return path_list

def create_project(project):
    session = Session()

    # check if project exists.
    query_result = session.query(Project.path).filter_by(name=project.name).first()
    if query_result:
        print(f"{project.name} already exists at {query_result[0]}")
        return
    session.add(project)
    # index files

    # index modules
    modules_path = index(Path(project.path))
    for module_path in modules_path:
        project.add_module(module_path)

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

if __name__ == '__main__':
    create_project(Project(name="AutoComplete", path="/home/pglandon/PycharmProjects/AutoComplete/src"))
    # remove_project("AutoComplete")