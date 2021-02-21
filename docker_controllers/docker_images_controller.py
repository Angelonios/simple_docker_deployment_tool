from flask import Blueprint, request, render_template, json
from subprocess import Popen, PIPE

docker_images_controller = Blueprint('docker_images_controller', __name__, template_folder="templates")

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
DELETE_IMAGE_ACTION = 'delete'

# Docker images option argument tokens
DOCKER_IMAGES_ARGS = {
    ALL_OPTION: '--all',
    DIGEST_OPTION: '--digests',
    FILTER_OPTION: '--filter',
    FORMAT_OPTION: '--format',
    NO_TRUNC_OPTION: '--no-trunc'
}

DOCKER_RMI_ARGS = {

}


@docker_images_controller.route('/')
def list_images():
    if request.method == 'GET':
        if len(request.args) == 0:
            return render_template('docker_images.html')
        else:
            images_request = parse_images_request(request)
            docker_info = exec_docker_images(images_request)
            return render_template('docker_images.html', docker_info=docker_info)


def parse_images_request(rq):
    return {
            NAME_TAG: param_request(rq, NAME_TAG),
            ALL_OPTION: option_request(rq, ALL_OPTION),
            DIGEST_OPTION: option_request(rq, DIGEST_OPTION),
            FILTER_OPTION: option_request(rq, FILTER_OPTION),
            FILTER_RULE: param_request(rq, FILTER_RULE),
            FORMAT_OPTION: option_request(rq, FORMAT_OPTION),
            FORMAT_RULE: param_request(rq, FORMAT_RULE),
            NO_TRUNC_OPTION: option_request(rq, NO_TRUNC_OPTION),
        }


def option_request(rq, arg):
    return rq.args.get(arg, False) == 'on'


def param_request(rq, arg):
    return rq.args.get(arg, False)


def exec_docker_images(images_request):
    # first two cmd tokens
    docker_arguments = ['docker', 'images']
    # add rest of cmd tokens from request
    docker_arguments = append_requested_args(docker_arguments, images_request)
    # prepare awk cmd tokens for formatting docker images result
    awk_arguments = prepare_awk_arguments(images_request[DIGEST_OPTION])
    # run docker images with requested args and set stdout to PIPE
    docker_images_command = Popen(docker_arguments, stdout=PIPE)
    # docker_images_return_code = docker_images_command.wait()

    # accept docker images stdout as stdin to awk cmd
    awk_format = Popen(awk_arguments, stdin=docker_images_command.stdout, stdout=PIPE, text=True)
    # handle docker images cmd closure
    docker_images_command.stdout.close()
    # awk_format_return_code = awk_format.wait()

    # get output of the command line pipe
    cmd_result = awk_format.communicate()[0]

    # convert string output to dictionary
    result = cmd_table_to_dict(cmd_result)

    return result


def append_requested_args(args, requested_args):
    docker_args = args
    for arg_key in requested_args:
        arg = requested_args[arg_key]
        if type(arg) is str:
            docker_args.append(arg)
            continue
        if arg:
            docker_args.append(DOCKER_IMAGES_ARGS[arg_key])
    return docker_args


def prepare_awk_arguments(digest_option):
    awk_arguments = ['mawk', '-F', '[[:space:]][[:space:]]+']
    if digest_option:
        awk_arguments.append(
            'NR>1{print PREV} {PREV=$1 "," $2 "," $3 "," $4 "," $5 "," $6} END{printf("%s",$1 "," $2 "," $3 "," $4 "," $5 "," $6)}'
        )
    else:
        awk_arguments.append(
            'NR>1{print PREV} {PREV=$1 "," $2 "," $3 "," $4 "," $5} END{printf("%s",$1 "," $2 "," $3 "," $4 "," $5)}'
        )
    return awk_arguments


def cmd_table_to_dict(cmd_result):
    all_rows = cmd_result.split('\n')
    header = all_rows[0].split(',')
    rows = [i.split(',') for i in all_rows[1:]]

    return {
        "header": header,
        "rows": rows
    }


@docker_images_controller.route('/docker_images', methods=['GET', 'POST'])
def docker_image_action():
    if request.method == 'POST':
        data = json.loads(request.data)
        image_name = data["image_name"]
        image_version = data["image_version"]
        image_action = data["action"]

        if image_action == DELETE_IMAGE_ACTION:
            return json.dumps(exec_docker_rmi(image_name, image_version))

        result = 'not implemented'
        return result


def exec_docker_rmi(image_name, image_version):
    docker_arguments = ['docker', 'rmi', image_name + ':' + image_version]
    docker_rmi_command = Popen(docker_arguments, stdout=PIPE, text=True)
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

