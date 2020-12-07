from src.bdd.bdd import Session

class ProjectManager:
    class __ProjectManager:
        def __init__(self, session):
            self.session = session

    __instance = None
    def __new__(cls, *args, **kwargs):
        if not ProjectManager.__instance:
            ProjectManager.__instance = ProjectManager.__ProjectManager(Session)
        return ProjectManager.__instance
