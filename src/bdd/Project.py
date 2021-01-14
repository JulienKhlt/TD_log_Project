import datetime
import logging
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from src.bdd.bdd import Base, Session
from src.bdd.Config import Config
from src.bdd.Module import Module
from src.parser.tools import calculate, get_relative_path


class ProjectManager:
    class __ProjectManager:
        """A collection of tools to manage projects"""

        def __init__(self, sessionmaker):
            """sessionmaker is a function that enables sql alchemy
            session creation."""
            self.sessionmaker = sessionmaker
            self.session = self.sessionmaker()

        def exist(self, project_name):
            """Return True if a project with given name is already registered
            in BDD, False otherwise."""
            session = self.sessionmaker()

            # check if project exists.
            query_result = session.query(Project.path).filter_by(
                name=project_name).first()
            if query_result:
                session.close()
                return True
            session.close()
            return False

        def update_project(self, project_name, from_path):
            """Index new files in project, update bindings and
            external dependencies."""
            session = self.sessionmaker()

            # check if project exists.
            query_result = session.query(Project).filter_by(
                name=project_name).first()
            if not query_result:
                logging.info(f"{project_name} not found, skipping.")
                return

            if query_result.fully_indexed and query_result.external:
                logging.debug(
                    f"{project_name} already fully indexed, skipping.")
                return

            query_result.index(from_path)
            query_result.build()

            session.commit()
            session.close()

        def register_project(self, project_name, project_path, external=False,
                             fast=True, from_path=None):
            """Register a project with given path, return it afterward (might take a while async ?)."""
            if self.exist(project_name):
                if not external:
                    logging.info(f"{project_name} already registered!")
                else:
                    self.update_project(project_name, from_path)
                return
            # TODO -> venv support!
            project = Project(name=project_name, path=str(project_path), external=external,
                              config=Config(python_home="/usr/",
                                            fast=fast))

            self.session.add(project)
            self.session.commit()

            project.index(from_path)
            self.session.commit()

            project.build(from_path)
            self.session.commit()

            return project

        def is_workspace_registered(self, workspaceUri):
            """Return associatied Project if given workspace is registered, False otherwise.
            Doesn't close session if a project is found!"""
            workspaceUri = Path(workspaceUri)

            query_result = self.session.query(Project).filter_by(
                path=str(workspaceUri)).first()

            return query_result

        def lsp_add_workspace(self, workspacePath):
            """Called on LS initialization to either register current workspace if it's not already referenced
            or update it. Returns Project associated to workspacePath, None in case of failure."""

            # Let's use pathlib to assure cross-OS compatibility :
            workspacePath = Path(workspacePath)
            if not workspacePath.is_dir() or not workspacePath.exists():
                logging.error("Project root doesn't exist!")
                return None

            # Workspace exists, let's check if it's already referenced.
            project = self.is_workspace_registered(workspacePath)

            if project:
                logging.info("Workspace already registered, updating...")

                self.session.add(project)
                project.update()
                self.session.commit()
                project.build()
                self.session.commit()

                return project
            else:
                project = self.register_project(workspacePath.name, workspacePath)
                self.session.add(project)

                return project

        def drop_project(self, project_name):
            """Remove project and linked objects from BDD."""
            query_result = self.session.query(Project).filter_by(name=project_name).first()
            if not query_result:
                print(f"{project_name} doesn't not exist.")
                return

            self.session.delete(query_result)
            self.session.commit()



    instance = None

    @staticmethod
    def initialize(sessionmaker=Session):
        if not ProjectManager.instance:
            ProjectManager.instance = ProjectManager.__ProjectManager(sessionmaker)

    def __new__(cls):
        if not ProjectManager.instance:
            ProjectManager.initialize()
        return ProjectManager.instance


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)

    name = Column(String(50))
    path = Column(String(200))

    active = Column(Boolean)
    version = Column(String(20), default="TBD")
    external = Column(Boolean, default=False)
    fully_indexed = Column(Boolean, default=False)

    config = relationship("Config", uselist=False,
                          back_populates="project", cascade="all, delete, delete-orphan")
    module = relationship("Module", back_populates="project",
                          cascade="all, delete, delete-orphan")

    last_update = Column(DateTime, default=datetime.datetime.utcnow)

    def build(self, from_path=None):
        """Build the relationships between the project and its modules. Bind imports and external projects.
        Should be called once on project registration. Doesn't commit change to database.
        If FROM_PATH is not None, index only subproject beginning at FROM_PATH"""

        if from_path:
            logging.info(f"building project {self.name} from {from_path}")
        else:
            logging.info(f"building project {self.name}")

        if not self.external:
            self.bind_external_project()
            self.bind_imports()

    def index_modules_path(self, rec_path=None):
        """Returns a list of Path of all the files in a project."""

        next_path = Path(self.path)
        if rec_path:
            rec_path = Path(rec_path)
            if rec_path.is_file():
                return [rec_path]
            if rec_path.joinpath('__init__.py').exists():
                next_path = rec_path
            else:
                return []

        modules_path = list(next_path.glob('*.py'))

        for next_dir in next_path.iterdir():
            if next_dir.is_dir():
                modules_path += self.index_modules_path(next_dir)

        return modules_path

    def index(self, rec_path=None):
        """Add all .py files to the project and build them (in the module sense)."""

        if str(rec_path) == self.path or not rec_path:
            self.fully_indexed = True

        modules_path = self.index_modules_path(rec_path)

        for module_path in modules_path:
            self.add_module(module_path)

    def add_module(self, module_path):
        """Add module to project."""

        # Check if module is not in project.
        if module_path.stem == '__init__' or module_path.stem == '__main__':
            module = Module(path=str(module_path.parent),
                            name=module_path.stem)
        else:
            module = Module(path=str(module_path), name=module_path.stem)

        # Reference module
        module.build()

        # Add module
        self.module.append(module)

    def get_relative_path(self, fullpath):
        return get_relative_path(self.path, fullpath)

    def get_project_module_search_path(self):
        pass

    def is_module_in_project(self, module_name):
        """Return True if we can find the module in the project, False otherwise."""
        module_path = Path(self.path).joinpath(module_name).with_suffix('.py')
        for project_module in self.module:
            if project_module.path == str(module_path):
                return True
        return False

    def get_project_imports_name(self):
        """Return all imports (and imports_from) name within the project."""
        imports_name_list = []

        for project_module in self.module:
            imports_name_list += project_module.get_imports_name()

        return imports_name_list

    def get_project_unbound_imports_name(self):
        """Return all imports (and imports_from) name that are NOT bound within the project."""

        unbound_imports_name_list = []

        for module in self.module:
            unbound_imports_name_list += module.get_unbound_imports_name()

        return unbound_imports_name_list

    def get_module_path(self, module_name):
        """Return module Path from name if it exists in project modules dirs, None otherwise."""
        search_paths = self.config.get_python_module_search_path()
        for search_path in search_paths:
            full_path = search_path.joinpath(module_name)
            if full_path.is_dir() and full_path.exists() and full_path.joinpath('__init__.py').exists():
                return full_path
            full_path_py = full_path.with_suffix('.py')
            if full_path_py.exists():
                return full_path_py
        return None

    def get_python_module_path_from_system_path(self, system_path):
        """Return a Module valid Path from a system Path (if __init__.py/__main__.py return upper dir)."""

        # TODO (if import -> __init__.py, if ran -> __main__.py... I hate python!)
        return system_path

    def get_module(self, module_path):
        """Return Module object at module_path (Path) if in project, None otherwise."""

        module_path_string = str(module_path)
        for module in self.module:
            if module_path_string == module.path:
                return module
        return None

    def get_project_root(self, file_path):
        """Try to find the project's root for a given file path with the following rules:
            - if the directory containing the file has __init__.py we look in the up dir and we repeat the process.
            - if not we return the previous dir."""
        if file_path.is_dir():
            parent = file_path.parent
            if parent.joinpath('__init__.py').exists():
                return self.get_project_root(parent)
            else:
                return file_path
        else:
            return self.get_project_root(file_path.parent)

    def bind_external_project(self, for_modules=None):
        """Bind external projects to this project. Call this AFTER all modules have been indexed.
        Fast make that only necessary files are indexed, not everything. if FOR_MODULE is not None, search only in this
        list."""
        if not for_modules:
            imports_name = self.get_project_unbound_imports_name()
        else:
            imports_name = []
            for module in for_modules:
                imports_name += module.get_unbound_imports_name()

        for import_name in imports_name:
            if not self.is_module_in_project(import_name):
                module_path = self.get_module_path(import_name)
                if module_path:
                    project_root = self.get_project_root(module_path)
                    project_name = project_root.stem
                    from_path = None

                    if self.config.fast:
                        from_path = module_path
                    logging.info(f"Binding {imports_name} to {self.name}.")
                    ProjectManager().register_project(
                        project_name, str(project_root), True, True, from_path)

    def bind_imports(self, session=Session()):
        """Bind modules together via imports. Call this AFTER all modules have been indexed."""

        for project_module in self.module:
            for module_import in project_module.imports + project_module.imports_from:
                if module_import.module_to_id is not None:
                    continue
                paths = self.config.get_python_module_search_path()
                for string_path in paths:
                    path = Path(string_path, module_import.name)

                    result = session.query(Module.id).filter_by(
                        path=str(path)).first()
                    if not result:
                        path_py = path.with_suffix('.py')
                        result = session.query(Module.id).filter_by(
                            path=str(path_py)).first()
                    if result:
                        module_import.module_to_id = result[0]
                        break
                if not module_import.module_to_id:
                    logging.warning(f"Import not found: {module_import.name}")

    def update(self):
        """Check for new modules and/or modules modification.
        Operations are done in MEMORY! Commit to session to see modification in database."""
        modules_path = self.index_modules_path()

        # TODO : find a better matching algorithm (Nb_files ** 2 here)
        for module_path in modules_path:
            is_referenced = False
            for referenced_module in self.module:
                referenced_module_path = Path(referenced_module.path)
                if referenced_module_path == module_path:
                    is_referenced = True

                    # We check if it has been modified outside the Language Client
                    if referenced_module.visit_date < datetime.datetime.fromtimestamp(module_path.stat().st_mtime):
                        # We update this module
                        referenced_module.update()
                    break

            if not is_referenced:
                # Not referenced, we had it to the project.
                self.add_module(module_path)

        # Don't forget to rebuild the project afterward or imports won't be linked!

    def complete(self, to_complete, module_path):
        """Return a list of LSP::CompletionItem that corresponds to possible completion for TO_COMPLETE (CompletionParams) in file MODULE_PATH."""

        logging.info(f"Tring to complete {to_complete} in module {module_path}")

        for project_module in self.module:
            if project_module.path == module_path:
                return project_module.complete(to_complete)

        return []

    def complete_import(self, to_complete):
        """Return a list of string with possible completion."""
        paths = self.config.get_python_module_search_path()
        regex = re.compile(rf'^{to_complete}')

        completion_list = []

        for path in paths:
            if not path.exists():
                continue

            for directory in path.iterdir():
                match = regex.match(directory.name)

                if match and directory.joinpath('__init__.py').exists():
                    completion_list.append(directory.name)

            for file in list(path.glob('*.py')):
                if regex.match(file.stem) and file.suffix == '.py':
                    completion_list.append(file.stem)

        return completion_list






