from setting import PATH_OF_GITREF, PATH_OF_GITCLONE, PATH_OF_ERROR_GITCLONE
from tqdm import tqdm
import subprocess
import time
import os
import re



def getURL():
    with open(PATH_OF_GITREF) as f:
        gitrefs = f.readlines()

    return gitrefs


def getFolderName(gitref):
    if gitref[:5] == "http:":
        gitref = gitref.replace("http:", "https:")

    username_project = re.findall(r'https://github.com/([^/]*)/(.*)', gitref)

    if len(username_project) == 0:
        print(f"Error: Uneffective GitRef -> {gitref}")

        with open(PATH_OF_ERROR_GITCLONE, 'a+') as f:
            f.seek(0)
            if not gitref in f.read():
                f.write(f"Error: Uneffective GitRef -> {gitref}")

        return False
    
    return f"{username_project[0][0]}_{username_project[0][1]}"



def git_clone(gitref):
    repositories = os.listdir(path=PATH_OF_GITCLONE)
    folderName = getFolderName(gitref)

    if not folderName:
        return None
    if folderName in repositories:
        print("Already Exists!")
        return None

    cmd = f'git clone {gitref} {folderName}'
    clone = subprocess.run(list(cmd.split()), cwd=PATH_OF_GITCLONE, encoding='utf-8', stdout=subprocess.PIPE)

    # 連続アクセスを避ける
    time.sleep(5)

    return None



if __name__ == "__main__":
    gitrefs = getURL()

    for gitref in tqdm(gitrefs):
        git_clone(gitref)
