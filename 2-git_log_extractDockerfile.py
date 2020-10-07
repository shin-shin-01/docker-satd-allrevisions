from setting import PATH_OF_GITCLONE, PATH_OF_GITLOGTXT, PATH_OF_ERROR_GITLOG, PATH_OF_GITLOGCSV, PATH_OF_GITSHOWLIST
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

    # -mオプションは、マージコミットを通常のコミットと同じように扱うオプション。
    command = f'git log --name-status -m'
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
> Author
> Date
> Dockerfiles
> Status
"""

def appendToResult(result, tmp, status, dockerfile):
    result["CommitID"].append(tmp["CommitID"])
    result["Author"].append(tmp["Author"])
    result["Date"].append(tmp["Date"])
    result["Dockerfile"].append(dockerfile)
    result["Status"].append(status)

    return result

def appendRevisionFile(revisionFileList, commitid, filename):
    revisionFile = f"{commitid}:{filename}"
    if revisionFile in revisionFileList:
        return revisionFileList
    else:
        revisionFileList.append(revisionFile)
        return revisionFileList


def saveRevisonFileToShow(revisionFileList, repository):
    txt = '\n'.join(revisionFileList)
    with open(f"./{PATH_OF_GITSHOWLIST}/{repository}.txt", "w") as f:
        f.write(txt)


def RevisionsHaveDocker(repository, txtGitFileStatus):
    result = { "CommitID":[], "Author":[], "Date":[], "Dockerfile":[], "Status":[] }
    tmp = { "CommitID":"", "Author":"", "Date":"" }
    revisionFileList = []

    for i, txt in enumerate(txtGitFileStatus.splitlines()):
        if txt[:6] == "commit":
            tmp["CommitID"] = txt[7:47]

        elif txt[:7] == "Author:":
            tmp["Author"] = txt[8:]

        elif txt[:5] == "Date:":
            tmp["Date"] = txt[8:]

        elif ("Dockerfile" == txt[-10:]) or ("dockerfile" == txt[-10:]):

            if txt[0] != " ":
                if txt[0] == "R":
                    status = f"{txt[0]}"
                    dockerfile = f"{txt.split()[1]}  {txt.split()[2]}"
                    result = appendToResult(result, tmp, status, dockerfile)
                    # いつ削除されたかを明確にするため、R100 でも取得する
                    revisionFileList = appendRevisionFile(revisionFileList, tmp["CommitID"], txt.split()[2])
                else:
                    status = f"{txt[0]}"
                    dockerfile = f"{txt.split()[1]}"
                    result = appendToResult(result, tmp, status, dockerfile)
                    if txt[0] != "D":
                        revisionFileList = appendRevisionFile(revisionFileList, tmp["CommitID"], txt.split()[1])

    result = pd.DataFrame.from_dict(result)
    result.to_csv(f"./{PATH_OF_GITLOGCSV}/{repository}.csv")

    saveRevisonFileToShow(revisionFileList, repository)




if __name__ == "__main__":
    repositories = os.listdir(PATH_OF_GITCLONE)
    count = 0

    for repository in tqdm(repositories):

        if not isTargetRepository(repository):
            continue

        txtGitFileStatus = GitlogFileStatus(repository)
        if not txtGitFileStatus:
            continue

        RevisionsHaveDocker(repository, txtGitFileStatus)


