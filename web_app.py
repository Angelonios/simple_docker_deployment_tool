from flask import Flask, request, render_template
import os
import asyncio

app = Flask(__name__)

@app.route('/')
def docker_file_form():
    return render_template('docker_setup.html')


@app.route('/', methods=['GET', 'POST'])
def docker_file_form_post():
    github_repo = request.form.get('github_repo')
    image_name = request.form.get('image_name')
    image_version = request.form.get('image_version')
    host_port = request.form.get('host_port')
    container_port = request.form.get('container_port')
    dockerfile_content = request.form.get('dockerfile')

    #path where deployment app is
    dev_path = "/home/ubuntu/dev_enviroment/simple_docker_deployment_tool/"
    #path of folder containing src & dockerfile
    service_path = dev_path + github_repo.split("/")[-1].split(".")[0]
    #path of dockerfile
    dockerfile_path = service_path + "/dockerfile"
    
    if request.method == 'POST':
        os.system("git clone " + github_repo + " " + service_path)
        os.system("touch " + dockerfile_path)
        dockerfile = open(dockerfile_path, "w")
        dockerfile.writelines(dockerfile_content)
        os.system("docker build -t " + image_name + ":" + image_version + " " + service_path)
        os.system("docker build -t " + image_name + ":" + image_version + " " + service_path)
        os.system("docker run -it -d -p " + host_port + ":" + container_port + " " + image_name)
        return "thanks"
    else:
        return "no thanks"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
