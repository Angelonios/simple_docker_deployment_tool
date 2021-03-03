import os


def populate_project_working_dirs():
    result = {}
    for working_dir in os.listdir(MAIN_WORKING_DIRECTORY):
        if os.path.isdir(os.path.join(MAIN_WORKING_DIRECTORY, working_dir)):
            result[working_dir] = MAIN_WORKING_DIRECTORY + working_dir
    return result


def set_new_project_working_dir(git_repo):
    new_working_dir = git_repo.split("/")[-1].split(".")[0]
    PROJECTS_WORKING_DIRS[new_working_dir] = MAIN_WORKING_DIRECTORY + new_working_dir
    return PROJECTS_WORKING_DIRS[new_working_dir]


MAIN_WORKING_DIRECTORY = os.getcwd() + '/web_dev/'
PROJECTS_WORKING_DIRS = populate_project_working_dirs()

