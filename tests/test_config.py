import unittest

from bdd.Project import Config


class MyTestCase(unittest.TestCase):
    def test_python_path(self):
        config = Config(python_home='/usr')
        python_exec = config.get_python_exec()

        self.assertTrue(python_exec.samefile( "/usr/bin/python"))

        config = Config(python_home='/home/pglandon/PycharmProjects/AutoComplete/venv')
        python_exec = config.get_python_exec()

        self.assertTrue(python_exec.samefile('/home/pglandon/PycharmProjects/AutoComplete/venv/bin/python'))

    def test_module_search_path(self):
        config = Config(python_home='/home/pglandon/PycharmProjects/AutoComplete/venv')
        search_path = config.get_python_module_search_path()

        print(search_path)


if __name__ == '__main__':
    unittest.main()
