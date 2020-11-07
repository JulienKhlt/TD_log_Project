from unittest import TestCase

from src.bdd.Config import Config
from src.bdd.Project import Project

class TestProject(TestCase):
    def test_add_module(self):
        self.fail()

    def test_get_relative_path(self):
        self.fail()

    def test_get_project_module_search_path(self):
        self.fail()

    def test_is_module_in_project(self):
        self.fail()

    def test_get_project_imports_name(self):
        self.fail()

    def test_get_module_path(self):
        project = Project(name="TestProject")
        project.config = Config(python_home="/usr")

        print(project.get_module_path('toml/decoder'))

        self.fail()

    def test_get_project_root(self):
        project = Project(name="TestProject")
        project.config = Config(python_home="/usr")

        file_path = project.get_module_path('bdd/File')

        print(project.get_project_root(file_path))

        self.assertTrue(True, True)

    def test_index_modules_path(self):
        project = Project(name="TestProject", path='/home/pglandon/PycharmProjects/AutoComplete/src/')
        res = project.index_modules_path('/home/pglandon/PycharmProjects/AutoComplete/src/bdd/Config.py')

        for r in res:
            print(r)
        self.assertTrue(True, True)

    def test_bind_external_project(self):
        self.fail()

    def test_bind_imports(self):
        self.fail()
