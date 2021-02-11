from flask import Flask, request, render_template
import subprocess
from subprocess import Popen, PIPE

app = Flask(__name__)

# Docker images option arguments
ALL_OPTION = 'all_option'
DIGEST_OPTION = 'digest_option'
FILTER_OPTION = 'filter_option'
FORMAT_OPTION = 'format_option'
NO_TRUNC_OPTION = 'no_trunc_option'

# Docker images parameter arguments
NAME_TAG = 'name_tag'
FILTER_RULE = 'filter_rule'
FORMAT_RULE = 'format_rule'

# Docker images option argument tokens
DOCKER_IMAGES_ARGS = {
    ALL_OPTION: '--all',
    DIGEST_OPTION: '--digests',
    FILTER_OPTION: '--filter',
    FORMAT_OPTION: '--format',
    NO_TRUNC_OPTION: '--no-trunc'
}

@app.route('/docker_images')
def docker_images_info():
    if request.args.__len__() == 0:
        return render_template('docker_images.html')
    if request.method == 'GET':
        images_request = {
            NAME_TAG: param_request(request, NAME_TAG),
            ALL_OPTION: option_request(request, ALL_OPTION),
            DIGEST_OPTION: option_request(request, DIGEST_OPTION),
            FILTER_OPTION: option_request(request, FILTER_OPTION),
            FILTER_RULE: param_request(request, FILTER_RULE),
            FORMAT_OPTION: option_request(request, FORMAT_OPTION),
            FORMAT_RULE: param_request(request, FORMAT_RULE),
            NO_TRUNC_OPTION: option_request(request, NO_TRUNC_OPTION),
        }

        docker_images_result = docker_images(images_request)
        docker_images_formatted = format_docker_images_result(docker_images_result)

    return render_template('docker_images.html', docker_info=docker_images_formatted)


def option_request(rq, arg):
    return True if rq.args.get(arg) is not None else False


def param_request(rq, arg):
    return rq.args.get(arg) if rq.args.get(arg) is not None else False


def docker_images(images_request):
    docker_arguments = ['docker', 'images']

    for arg_key in images_request:
        arg = images_request[arg_key]
        if type(arg) is str and arg != '':
            docker_arguments.append(arg)
            continue
        if arg:
            docker_arguments.append(DOCKER_IMAGES_ARGS[arg_key])

    awk_arguments = ['mawk', '-F', '[[:space:]][[:space:]]+']
    if images_request[DIGEST_OPTION]:
        awk_arguments.append(
            'NR>1{print PREV} {PREV=$1 "," $2 "," $3 "," $4 "," $5 "," $6} END{printf("%s",$1 "," $2 "," $3 "," $4 "," $5 "," $6)}'
        )
    else:
        awk_arguments.append(
            'NR>1{print PREV} {PREV=$1 "," $2 "," $3 "," $4 "," $5} END{printf("%s",$1 "," $2 "," $3 "," $4 "," $5)}'
        )

    docker_images_command = Popen(docker_arguments, stdout=PIPE)
    #docker_images_return_code = docker_images_command.wait()


    awk_format = Popen(awk_arguments, stdin=docker_images_command.stdout, stdout=PIPE, text=True)
    docker_images_command.stdout.close()
    #awk_format_return_code = awk_format.wait()

    result = awk_format.communicate()[0]

    return result


def format_docker_images_result(docker_images_result):
    all_rows = docker_images_result.split('\n')
    header = all_rows[0].split(',')
    rows = [i.split(',') for i in all_rows[1:]]

    result = {
        "header": header,
        "rows": rows
    }

    return result


@app.route('/deploy_app')
def docker_file_form():
    return render_template('docker_setup.html')


@app.route('/deploy_app', methods=['GET', 'POST'])
def docker_file_form_post():
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
    else:
        return "NotOk"


def create_docker_file(dockerfile_path, dockerfile_content):
    try:
        dockerfile = open(dockerfile_path, "w")
        dockerfile.writelines(dockerfile_content)
    except Exception as err:
        print("This exception occured: {0}".format(err))
    finally:
        dockerfile.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0')
