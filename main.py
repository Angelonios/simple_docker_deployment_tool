from flask import Flask, render_template
from docker_controllers import deploy_app_controller, docker_images_controller

app = Flask(__name__)
app.register_blueprint(deploy_app_controller.deploy_app_controller, url_prefix="/deploy_app")
app.register_blueprint(docker_images_controller.docker_images_controller, url_prefix="/docker_images")


@app.route('/')
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
