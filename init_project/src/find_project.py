#!/home/pl/miniconda3/bin/python
# When executed, create a .project directory
# if none is found in any parent directories

from pathlib import Path


def start():
    """Start the script"""
    print('script started')
    return


def create_project(path):
    """Create a project in the current directory"""
    print(f'No parents found, creating .project in {path}')
    curr_path = path / '.project'
    curr_path.mkdir()
    return


def extend_project(curr_dir, project_dir):
    """Extend current project to all subdirectory

        :param curr_dir: The directory in which we look for every directory that need a .project file.
        :param project_dir: The directory where the .project folder is.
    """
    for child in curr_dir.iterdir():
        if '.' in child.stem:
            continue
        elif (child / '.project').is_dir():
            merge_project(project_dir, child)
        elif child.is_dir():
            file = child / '.project'
            with file.open(mode='w') as f:
                f.write(str(project_dir))
                extend_project(child, project_dir)
    return


def merge_project(project_dir, child_dir):
    """Ask the user wether or not he wants to merge the current project with one found in a subdirectory, if yes the
    subproject will be remove and all data will be lost

        :param project_dir: A parent directory of ``child_dir`` which contains a .project folder.
        :param child_dir: A subdirectory of ``project_dir`̀ whicj also contains a .project folder.
     """

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


def clear_project(curr_dir=Path().resolve()):
    """Clear all subdirectory from .project file and curr_dir from .project folder

        :param curr_dir: The directory from which the cleaning process starts.
    """
    if (curr_dir / '.project').is_dir():
        for child in (curr_dir / '.project').iterdir():
            try:
                child.unlink()
            except:
                pass
        try:
            (curr_dir / '.project').rmdir()
        except:
            pass
    for child in curr_dir.iterdir():
        if (child / '.project').is_file():
            (child / '.project').unlink()
        elif child.is_dir():
            clear_project(child)
    return


def init_project(anchor=Path.home(), path=Path().resolve()):
    """Initialize a project inside the current directory, it will look for an existing project in a parent directory,
    if none is found, it will create one, if not, it will extend the project to all subdirectory

        :param anchor: The directory upon which the search process stops, set to /home/usr by default.
        :param path: Path were the project is intended to be created first, set to '.' by default.
    """
    parents = path.parents
    curr_path = path / '.project'
    project_dir = path
    if curr_path.is_dir():
        extend_project(path, path)
        start()
    else:
        print("Directory not found, looking for parent")
        for k, parent in enumerate(parents):
            print(f'{k},{parent.name}')
            if parent.name == anchor.name:
                create_project(path)
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
    part of the project (ie all subdirectory)

        :param project_dir: The directory containing the .project folder.
    """

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
