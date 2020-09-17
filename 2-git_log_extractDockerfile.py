from setting import PATH_OF_GITCLONE, PATH_OF_GITLOGTXT, PATH_OF_ERROR_GITLOG, PATH_OF_GITLOGCSV
from tqdm import tqdm
import subprocess
import os
import re
import pandas as pd


"""
1. git log -p -w を実行
2. Dockerfileを変更に含む commitID(revision)を取り出す
3. CSV ファイルに書き出す
"""

def isTargetRepository(repository):
    outputs = os.listdir(PATH_OF_GITLOGTXT)

    if repository == ".DS_Store":
        pass
    elif f'{repository}.txt' in outputs:
        print("Already Exists!")
    else:
        return True

    return False


def GitlogFileStatus(repository):
    """
    file status
    - M : Modified
    - D : Deleted
    - A : Added
    """

    command = f'git log --name-status'
    cwd = f'./{PATH_OF_GITCLONE}/{repository}/'

    # ignore utf-8 Error
    txtGitFileStatus = subprocess.run(list(command.split()), cwd=cwd, encoding='utf-8', stdout=subprocess.PIPE, errors="ignore")
    txtGitFileStatus = str(txtGitFileStatus.stdout)

    with open(f'{PATH_OF_GITLOGTXT}/{repository}.txt', 'w') as f:
        f.write(txtGitFileStatus)
    
    # エラー処理
    if txtGitFileStatus == "":
        with open(PATH_OF_ERROR_GITLOG, 'a+') as f:
            f.seek(0)
            if not repository in f.read():
                f.write(f"fatal: your current branch 'master' does not have any commits yet -> {repository}\n")

        return False

    return txtGitFileStatus

"""
outputCSV
> CommitID
> Date
> Dockerfiles
> Status
"""

def appendToResult(result, tmp):
    result["CommitID"].append(tmp["CommitID"])
    result["Date"].append(tmp["Date"])
    result["Dockerfiles"].append(tmp["Dockerfiles"])
    result["Status"].append(tmp["Status"])

    return result, { "CommitID":"", "Date":"", "Dockerfiles":"", "Status":"" }


def RevisonsHaveDocker(trepository, txtGitFileStatus):
    result = { "CommitID":[], "Date":[], "Dockerfiles":[], "Status":[] }
    tmp = { "CommitID":"", "Date":"", "Dockerfiles":"", "Status":"" }

    for i, txt in enumerate(txtGitFileStatus.splitlines()):
        if txt[:6] == "commit":
            if not i == 0:
                result, tmp = appendToResult(result, tmp)
            tmp["CommitID"] = txt[7:47]

        elif txt[:5] == "Date:":
            tmp["Date"] = txt.split()[1]

        elif ("Dockerfile" in txt) or ("dockerfile" in txt):
            if txt[0] != " ":
                tmp["Status"] += f"{txt[0]}\n"
                tmp["Dockerfiles"] += f"{txt.split()[1]}\n"

    result, tmp = appendToResult(result, tmp)
    result = pd.DataFrame.from_dict(result)
    result.to_csv(f"./{PATH_OF_GITLOGCSV}/{repository}.csv")





if __name__ == "__main__":
    repositories = os.listdir(PATH_OF_GITCLONE)
    count = 0

    for repository in tqdm(repositories):

        if not isTargetRepository(repository):
            continue

        txtGitFileStatus = GitlogFileStatus(repository)
        if not txtGitFileStatus:
            continue

        RevisonsHaveDocker(repository, txtGitFileStatus)


