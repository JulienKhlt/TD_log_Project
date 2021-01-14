import argparse
from src.bdd.Project import ProjectManager


def drop(project_name):
    """Drop PROJECT_NAME named project."""

    ProjectManager().drop_project(project_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Perform command on Projects.")
    parser.add_argument('action', choices=['drop'], help="What should I do ?")
    parser.add_argument('project_name', nargs='?', default=None)
    args = parser.parse_args()

    if args.action == 'drop':
        drop(args.project_name)