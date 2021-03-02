from flask import Blueprint, request, render_template, json
from subprocess import Popen, PIPE

docker_container_controller = Blueprint('docker_container_controller', __name__, template_folder="templates")


def parse_container_request(request):
    return {
        # NAME_TAG: param_request(rq, NAME_TAG),
        # ALL_OPTION: option_request(rq, ALL_OPTION),
        # DIGEST_OPTION: option_request(rq, DIGEST_OPTION),
        # FILTER_OPTION: option_request(rq, FILTER_OPTION),
        # FILTER_RULE: param_request(rq, FILTER_RULE),
        # FORMAT_OPTION: option_request(rq, FORMAT_OPTION),
        # FORMAT_RULE: param_request(rq, FORMAT_RULE),
        # NO_TRUNC_OPTION: option_request(rq, NO_TRUNC_OPTION),
    }


def exec_container_images(container_request):
    pass


@docker_container_controller.route('/', methods=['GET', 'POST'])
def list_images():
    if request.method == 'POST':
        container_request = parse_container_request(request)
        # docker_info = exec_container_images(container_request)
        # return render_template('docker_images.html', docker_info=docker_info)
        return "To be implemented."
