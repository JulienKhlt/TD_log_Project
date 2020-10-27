#!/home/pl/miniconda3/bin/python
# When exucuted, create a .project file
# if none is found in any parent directories

from pathlib import Path 

path = Path().resolve()
parents = path.parents

def start():
	print('script started')
	return

def create_project():
	print(f'No parents found, creating .project in {path}')
	curr_path = path / '.project'
	curr_path.mkdir()
	start()
	return

def extend_project(root_num, root_dir, parents):
	print(f'Found a parent project in {parents[root_num]}, copying')
	curr_path = path / '.project'
	with curr_path.open(mode='w') as f:
		f.write(str(root_dir))
	for fold_num in range(root_num):
		curr_path = parents[fold_num] / '.project'
		with curr_path.open(mode='w') as f:
			f.write(str(root_dir))
	return

def init_project():
	curr_path = path / '.project'
	if curr_path.is_dir():
		start()
		root_dir=path
	else:
		print("Directory not found, looking for parent")
		for k,parent in enumerate(parents):
			print(f'{k},{parent.name}')
			if parent.name == Path.home().name:
				create_project()
				start()
				root_dir=path
				break
			else:
				curr_path = parent / '.project'
				if curr_path.is_dir():
					root_dir = parent
					extend_project(root_num=k, root_dir=curr_path, parents=parents)
					start()
					break
	return root_dir

def indexing(root_dir):
	print('Indexing project')
	path_list = list(root_dir.glob('**/*.py'))
	curr_path = root_dir / '.project'
	if curr_path.is_dir():
		file = curr_path / '.index'
		with file.open(mode='w') as f:
			for elem in path_list:
				f.write(f'{elem.resolve()}\n')
	else:
		print('Project not initialized, consider initialazing it first')

if __name__ == '__main__':
	root_dir = init_project()
	indexing(root_dir)