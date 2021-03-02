import os
import subprocess
from flask import Blueprint, request, render_template, json
from subprocess import Popen, PIPE

docker_compose_controller = Blueprint('docker_compose_controller', __name__, template_folder="templates")

MAIN_WORKING_DIRECTORY = os.getcwd() + '/web_dev/'


def populate_project_working_dirs():
    result = {}
    for working_dir in os.listdir(MAIN_WORKING_DIRECTORY):
        if os.path.isdir(os.path.join(MAIN_WORKING_DIRECTORY, working_dir)):
            result[working_dir] = MAIN_WORKING_DIRECTORY + working_dir
    return result


PROJECTS_WORKING_DIRS = populate_project_working_dirs()


def set_new_project_working_dir(git_repo):
    new_working_dir = git_repo.split("/")[-1].split(".")[0]
    PROJECTS_WORKING_DIRS[new_working_dir] = MAIN_WORKING_DIRECTORY + new_working_dir
    return PROJECTS_WORKING_DIRS[new_working_dir]


@docker_compose_controller.route('/', methods=['GET', 'POST'])
def process_request():
    if request.method == 'POST':
        response = process_post(request)
    response = process_get(request)
    if not response:
        return render_template("docker_compose.html")
    return render_template("docker_compose.html", docker_data=response)


def process_get(rq):
    if len(rq.args) == 0:
        return False
    git_repo = rq.args.get('git_repo')
    project_repository = get_project_repository(git_repo)
    docker_compose_result = run_docker_compose_up(project_repository)
    return docker_compose_result



def get_project_repository(git_repo):
    new_work_dir = set_new_project_working_dir(git_repo)
    git_clone_status = subprocess.run(["git", "clone", git_repo, new_work_dir])
    if git_clone_status.stderr is not None:
        return git_clone_status.stder

    return run_docker_compose_up(new_work_dir)


def run_docker_compose_up(working_dir):
    docker_arguments = ['docker-compose', 'up']
    docker_rmi_command = Popen(docker_arguments, stdout=PIPE, text=True, cwd=working_dir)
    stdout = docker_rmi_command.communicate()[0]
    result = cmd_result_to_dict(stdout)
    return result


def cmd_result_to_dict(cmd_result):
    all_rows = cmd_result.split('\n')
    status = False if all_rows.split(':')[0] == 'Error' else True
    msg = all_rows

    return {
        'status': status,
        'msg': msg
    }


def process_post(rq):
    return "nothing"
