from flask import Flask, request, render_template
import subprocess

app= Flask(__name__)

@app.route('/docker_images')
def docker_images_table():
    return render_template('docker_images_table.html')

@app.route('/docker_imgaes', ['GET', 'POST'])
def docker_images_info():
    name_tag = request.form.get('name_tag')
    all_option = request.form.get('all_option')
    digest_option = request.form.get('digest_option')
    
    filter_option = request.form.get('filter_option')
    filter_rule = filter_option ? request.form.get('filter_rule') : ''

    format_option = request.form.get('format_option')
    format_rule = format_option ? request.form.get('format_rule') : ''

    no_trunc_option = request.form.get('no_trunc_option')
    
    docker_images_result = docker_images(
            name_tag, 
            all_option, 
            digest_option, 
            filter_option, 
            filter_rule,
            format_option,
            format_rule,
            no_trunc_option)
    
    docker_images_info = format_docker_images_result(docker_images_result)

    return render_template('docker_images_table.html')

def docker_images(
        name_tag='', 
        all_option=False, 
        digest_option=False,
        filter_option=False,
        filter_rule='',
        format_option=False,
        format_rule='',
        no_trunc_option=False):
    return subprocess.run(
            ['docker', 'images',
                name_tag,
                all_option?'-a':'',
                digest_option?'--digests':'',
                filter_option?'--filter':'',
                filter_option?filter_rule:'',
                format_option?'--format':'',
                format_option?format_rule:'',
                no_trunc_option?'--no-trunc':''],
            capture_output=True
            text=True)

@app.route('/deploy_app')
def docker_file_form():
    return render_template('docker_setup.html')


@app.route('/deploy_app', methods=['GET', 'POST'])
def docker_file_form_post():
    if request.method == 'POST':   
        github_repo         = request.form.get('github_repo')
        image_name          = request.form.get('image_name')
        image_version       = request.form.get('image_version')
        host_port           = request.form.get('host_port')
        container_port      = request.form.get('container_port')
        dockerfile_content  = request.form.get('dockerfile')

        #path where deployment app is
        dev_path = "/home/ubuntu/dev_enviroment/simple_docker_deployment_tool/"
   
        #path of folder containing src & dockerfile
        service_path = dev_path + github_repo.split("/")[-1].split(".")[0]
   
        #path of dockerfile
        dockerfile_path = service_path + "/dockerfile"
    
        # clones users application from remote repository        
        git_clone_status = subprocess.run(["git", "clone", github_repo, service_path])
        
        # opens a file and writes the dockerfile into it
        create_docker_file(dockerfile_path, dockerfile_content)
        
        # run docker build
        docker_build_status = subprocess.run(["docker", "build", "-t", image_name + ":" + image_version, service_path])
        
        # run docker run
        docker_run_status = subprocess.run(["docker", "run", "-it", "-d", "-p", host_port + ":" + container_port, image_name])
        
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
