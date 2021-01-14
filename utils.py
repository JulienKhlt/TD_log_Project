import argparse
import shutil
import subprocess
from time import sleep


def run():
    """Build container if necessary and run them."""
    # Run container
    bash_command = "docker-compose -f docker/docker-compose.yml up -d db adminer"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    process.communicate()

    print("To visualize data please visit: http://localhost:8888")
    print("Username: tdlog")
    print("Password: tdlog")


def install():
    """Install Python virtualenv with pipenv, build docker images."""
    docker = shutil.which('docker')
    docker_compose = shutil.which('docker-compose')
    pipenv = shutil.which('pipenv')

    if not docker or not docker_compose:
        print("Please install docker and docker-compose.")
        return

    if not pipenv:
        print("Please install pipenv (pip install pipenv).")

    # Install python requirements
    bash_command = "pipenv sync"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    process.communicate()

    # Build docker container
    bash_command = "docker-compose -f docker/docker-compose.yml build"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    process.communicate()

    print("Please init and migrate before using Ponthon.")


def init():
    """Init Project BDD. This should be done before migrating"""
    bash_command = "docker-compose -f docker/docker-compose.yml up -d db_init"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    process.communicate()

    print("If there is no error, it should have worked. Please run migration now.")


def migrate():
    """Run migration. You can use Ponthon after this."""

    # We launch the container. (We never know)
    bash_command = "docker-compose -f docker/docker-compose.yml up -d db"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    process.communicate()

    # TO avoid connection issues...
    sleep(1.)

    bash_command = "pipenv run migrate"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    process.communicate()

    print("You're good to go! You can now run Ponthon with the run command.")


def remove():
    """Stop and remove all containers."""
    print("It will remove all files and container from Ponthon, are you sure ? (y/N)")
    answer = input()

    if answer == 'y' or answer == 'yes' or answer == 'Y' or answer == 'YES' or answer == 'Yes':
        bash_command = "docker-compose -f docker/docker-compose.yml down"
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        process.communicate()
    else:
        print("Doing nothing, bye.")


def cli(command):
    """Run CLI in correct environment."""
    command = ' '.join(command)
    bash_command = f"pipenv run cli {command}"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    process.communicate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Install/Run BDD for development purpose.")
    parser.add_argument('action', choices=['install', 'run', 'cli', 'init', 'migrate', 'remove'],
                        help="What should I do ?")
    parser.add_argument('command', nargs='*', default=None)
    args = parser.parse_args()

    if args.action == 'run':
        run()
    elif args.action == 'install':
        install()
    elif args.action == 'init':
        init()
    elif args.action == 'migrate':
        migrate()
    elif args.action == 'cli':
        cli(args.command)
    elif args.action == 'remove':
        remove()
