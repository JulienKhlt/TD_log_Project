#!/home/pl/miniconda3/bin/python
# When executed, create a .project directory
# if none is found in any parent directories

from pathlib import Path

path = Path().resolve()
parents = path.parents


def start():
    """Start the script"""
    print('script started')
    return


def create_project():
    """Create a project in the current directory"""
    print(f'No parents found, creating .project in {path}')
    curr_path = path / '.project'
    curr_path.mkdir()
    return


def extend_project(curr_dir, project_dir):
    """Extend current project to all subdirectory"""
    for child in curr_dir.iterdir():
        if (child / '.project').is_dir():
            merge_project(project_dir, child)
        if '.' in child.stem:
            continue
        elif child.is_dir():
            file = child / '.project'
            with file.open(mode='w') as f:
                f.write(str(project_dir))
                extend_project(child, project_dir)
    return


def merge_project(project_dir, child_dir):
    """Ask the user wether or not he wants to merge the current project with one found in a subdirectory, if yes the
    subproject will be remove and all data will be lost """

    if (child_dir / '.project').is_dir() and (project_dir / '.project').is_dir():
        is_fuse = input(f"Do you want to merge project in {child_dir} with "
                        f"the project you are about to create in {project_dir} ? (y/n)")
        while True:
            if is_fuse == 'y':
                for file in (child_dir / '.project').iterdir():
                    file.unlink()
                (child_dir / '.project').rmdir()
                extend_project(child_dir, project_dir)
                break
            elif is_fuse == 'n':
                break
            else:
                is_fuse = input("Please enter y (yes) or n (no)")
    return


def clear_project(curr_dir):
    """Clear all subdirectory from .project file"""
    for child in curr_dir.iterdir():
        if (child / '.project').is_file():
            (child / '.project').unlink()
            clear_project(child)
    print("Project cleared")
    return


def init_project():
    """Initialize a project inside the current directory, it will look for an existing project in a parent directory,
    if none is found, it will create one, if not, it will extend the project to all subdirectory """
    curr_path = path / '.project'
    project_dir = path
    if curr_path.is_dir():
        extend_project(path,path)
        start()
    else:
        print("Directory not found, looking for parent")
        for k, parent in enumerate(parents):
            print(f'{k},{parent.name}')
            if parent.name == Path.home().name:
                create_project()
                extend_project(path, path)
                start()
                project_dir = path
                break
            else:
                curr_path = parent / '.project'
                if curr_path.is_dir():
                    project_dir = parent
                    print(f'Found a parent project in {project_dir}, copying')
                    extend_project(curr_dir=project_dir, project_dir=project_dir)
                    start()
                    break
    return project_dir


def indexing(project_dir):
    """Create an index file in .project directory in the root folder of the project, it contains all the .py files
    part of the project (ie all subdirectory) """

    print('Indexing project')
    path_list = list(project_dir.glob('**/*.py'))
    curr_path = project_dir / '.project'
    if curr_path.is_dir():
        file = curr_path / 'index'
        with file.open(mode='w') as f:
            for elem in path_list:
                f.write(f'{elem.resolve()}\n')
    else:
        print('Project not initialized, consider initialazing it first')


if __name__ == '__main__':
    root_dir = init_project()
    indexing(root_dir)
