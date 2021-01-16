# Ponthon: ENPC's Python Language Server

## About Ponthon

The work of a lifetime.\
Please donate at https://www.paypal.com/paypalme/Ponthon.

## Requirements

You need the following dependencies to make it work:
- docker
- docker-compose
- pipenv

**For Debian users, please install pipenv with pip and not with apt/apt-get or it won't work!**

`pip install --user pipenv` should do the trick.

Other dependencies will be automatically installed. For future release, we plan on
removing those dependencies, but for development it's just easier.
We didn't test it on Windows, but it should work the same way.

**Please check that you are in the docker group! It won't work otherwise.**

To check please type `docker run hello-world` (without sudo). If it exits with an error, add yourself to the docker group with `sudo usermod -aG docker yourUsername` 
and reload the system permission (rebooting works).

*Please check that docker's daemon is running!* type `sudo systemctl enable docker --now` to start it automatically on reboot. `sudo systemctl start docker` to start it this one time.

## Installation

In the root of the project, you'll find a CLI `utils` that will help you to install, run and test the project. Please use 
`python utils.py --help` for further information.
To install the project, run the following commands:
- `python utils.py install`
- `python utils.py init`
- `python utils.py migrate`
- `python utils.py cli scan` to add library to the reference server before hand -> avoid timeout in client (no async yet) | OPTIONAL AND MIGHT TAKE WHILE (APPROX 3 MIN on my computer).
- If the last command fail, please run `cd docker` then `docker-compose up db_init` and do migration again.

## Usage

In this dev version, you have to make sure that the container is running for Ponthon to work.
To do so, you can use `python utils.py run`. \
Once the container is started, you can find extensions for your favourite editor in the `extensions` folder.\
See `extensions/Readme.md` for further instruction.\
`**Trello** :
https://trello.com/b/hZRqQjoj/projet-tdlog

## Licence

Whatever

## Issues

- Do NOT use import in VSCode projects.... The indexing takes too long and make LS crash -> need async but complicated with SQL Alchemy... Fix this by adding your project by command line first! or library scanning on install.

## TODOs

- TODO Write Tests
- INPROGRESS Add a CLI -> What do you need PL ?
- TODO Write type inference
- DONE Write dot completion
- DONE Change bdd size for everything (problem with numpy today)
- TODO better completion type detection (i.e. better regex)
- DROPPED add dynamic completion (No computation on EACH change)
- DONE write heritage completion
- DONE write import completion
- TODO write import/from completion
- DROPPED -> Client modification needed... add virtualenv/pipenv support
- DONE: commit session only on file save
- DONE: add a new file to project
- DROPPED How to handle external files ?
- TODO upgrade semantic completion -> 3 loops when 1 is required!
- DONE fix "index out of range" on finding good scope
- TODO clean up logger
- TODO write separate logs for ls, rs, pygls
- TODO add import aware completion
- DONE: better vscode extension deployment
- TODO -> IMPORTANT add chained import completion
- DONE: add builtins completion (print, etc)
- DONE Fix heritage
- TODO Add async file parsing for external files -> or else it will crash
- DROPPED write async file referencing
- TODO add library scanning and referencing on install
