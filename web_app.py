from flask import Flask, request, render_template
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supekeyr'

@app.route('/')
def docker_file_form():
    return render_template('docker_setup.html')


@app.route('/', methods=['GET', 'POST'])
def docker_file_form_post():
    print("hey")
    print(request.method)
    print(request.form.get('image_name'))
    print(request.form.get('github_repo'))
    print(request.form.get('source_folder'))
    print(request.form.get('source_folder_image'))
    print(request.form.get('port'))
    if request.method == 'POST':
        image_name = request.form.get('image_name')
        github_repo = request.form.get('github_repo')
        source_folder = request.form.get('source_folder')
        source_folder_image = request.form.get('source_folder_image')
        port = request.form.get('port')
        # sync_files = request.form['sync_files']
        # sync_files_path = request.form['sync_files_path']

        os.system("git clone " + github_repo)
        os.system("cd " + github_repo.split("/")[-1].split(".")[0])
        os.system("touch Dockerfile")
        os.system("echo 'FROM: " + image_name + "' >> Dockerfile")
        os.system("echo 'CODE: " + source_folder + " " + source_folder_image + "' >> Dockerfile")
        os.system("echo 'EXPOSE: " + port + "' >> Dockerfile")
        return "thanks"
    else:
        return "no thanks"

if __name__ == "__main__":
    app.run()
