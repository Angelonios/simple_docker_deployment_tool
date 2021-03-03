import subprocess
from flask import Blueprint, request, render_template, Response
from subprocess import Popen, PIPE, STDOUT
from helpers import file_helper

docker_compose_controller = Blueprint('docker_compose_controller', __name__, template_folder="templates")


@docker_compose_controller.route('/', methods=['GET', 'POST'])
def remote_docker_compose():
    if request.method == 'POST':
        git_repo = request.form.get('git_repo')
        new_work_dir = file_helper.set_new_project_working_dir(git_repo)
        git_clone_status = subprocess.run(["git", "clone", git_repo, new_work_dir])
        if git_clone_status.stderr is not None:
            return render_template("docker_compose.html", docker_error=format_std_output(git_clone_status.stder))

        return Response(run_docker_compose_up(new_work_dir), mimetype="text/plain", content_type="text/event-stream")
    else:
        return render_template("docker_compose.html")




def run_docker_compose_up(working_dir):
    docker_arguments = ['docker-compose', 'up']
    docker_compose_command = Popen(docker_arguments, stdout=PIPE, stderr=STDOUT, text=True, cwd=working_dir)

    for line in iter(docker_compose_command.stdout.readline, b''):
        msg = line.rstrip() + "\n"
        print(msg)
        yield msg


def format_std_output(std_output):
    return std_output.split('\n')

