### Demo of init script

## How to test ?

Three differents demo are available, each one having different scenario of project creation

#Demo 1

No project is already created, so the script will create one in the **current directory** (where the code is launched). In each subfolders (except hidden one), a .project file will be created containing the (absolute) path to the .project directory in the **root directory**.

#Demo 2

A project already exist in a parent directory, so the script will extend this projject to the one you are about to create. It will result in .project files being created in all subdirectory of the **root directory**.

#Demo 3

A project already exists in a subdirectory, so when you are about to create one in a parent directory, two options will be given to you :

* Merge project: The .project file in the **child directory** will be deleted, the subdirectory of the **child directory** will be appended to the the project in the **root directory**.

* Do not merge: The **child directory** will be ignored by the extending process of the project in the **root directory** so that both can be considered independants.