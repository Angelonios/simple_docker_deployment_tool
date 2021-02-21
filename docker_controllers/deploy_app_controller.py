from flask import Blueprint, render_template, request
import subprocess

deploy_app_controller = Blueprint('deploy_app_controller', __name__, template_folder="templates")


@deploy_app_controller.route('/', methods=['GET', 'POST'])
def docker_file_form():
    if request.method == 'POST':
        github_repo = request.form.get('github_repo')
        image_name = request.form.get('image_name')
        image_version = request.form.get('image_version')
        host_port = request.form.get('host_port')
        container_port = request.form.get('container_port')
        dockerfile_content = request.form.get('dockerfile')

        # path where deployment app is
        dev_path = "/home/ubuntu/dev_enviroment/simple_docker_deployment_tool/"

        # path of folder containing src & dockerfile
        service_path = dev_path + github_repo.split("/")[-1].split(".")[0]

        # path of dockerfile
        dockerfile_path = service_path + "/dockerfile"

        # clones users application from remote repository
        git_clone_status = subprocess.run(["git", "clone", github_repo, service_path])

        # opens a file and writes the dockerfile into it
        create_docker_file(dockerfile_path, dockerfile_content)

        # run docker build
        docker_build_status = subprocess.run(
            ["docker", "build", "-t", image_name + ":" + image_version, service_path])

        # run docker run
        docker_run_status = subprocess.run(
            ["docker", "run", "-it", "-d", "-p", host_port + ":" + container_port, image_name])

        return 'Ok'

    return render_template('deploy_app.html')


def create_docker_file(dockerfile_path, dockerfile_content):
    try:
        dockerfile = open(dockerfile_path, "w")
        dockerfile.writelines(dockerfile_content)
    except Exception as err:
        print("This exception occured: {0}".format(err))
    finally:
        dockerfile.close()
