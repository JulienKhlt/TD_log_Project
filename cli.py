import argparse
from src.bdd.Project import ProjectManager


def drop(project_name):
    """Drop PROJECT_NAME named project."""

    ProjectManager().drop_project(project_name)


def add(project_path):
    """Add project at PROJECT_PATH to Reference Server."""

    project_manager = ProjectManager()
    project_manager.lsp_add_workspace(project_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Perform command on Projects.")
    parser.add_argument('action', choices=['drop', 'add'], help="What should I do ?")
    parser.add_argument('project_name', nargs='?', default=None)

    args = parser.parse_args()

    if args.action == 'drop':
        drop(args.project_name)
    elif args.action == 'add':
        add(args.project_name)
