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

def appendToResult(result, tmp):
    result["CommitID"].append(tmp["CommitID"])
    result["Author"].append(tmp["Author"])
    result["Date"].append(tmp["Date"])
    result["Dockerfiles"].append(tmp["Dockerfiles"])
    result["Status"].append(tmp["Status"])

    return result, { "CommitID":"", "Author": "", "Date":"", "Dockerfiles":"", "Status":"" }


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


def RevisonsHaveDocker(repository, txtGitFileStatus):
    result = { "CommitID":[], "Author":[], "Date":[], "Dockerfiles":[], "Status":[] }
    tmp = { "CommitID":"", "Author":"", "Date":"", "Dockerfiles":"", "Status":"" }
    revisionFileList = []

    for i, txt in enumerate(txtGitFileStatus.splitlines()):
        if txt[:6] == "commit":
            if not i == 0:
                result, tmp = appendToResult(result, tmp)
            tmp["CommitID"] = txt[7:47]

        elif txt[:7] == "Author:":
            tmp["Author"] = txt[8:]

        elif txt[:5] == "Date:":
            tmp["Date"] = txt[8:]

        elif ("Dockerfile" in txt) or ("dockerfile" in txt):
            ## 例外ファイル
            if txt[-3:] == ".go":
                continue
            elif txt[-4:] == ".tgz":
                continue
            elif txt[-10:] == ".installer":
                continue
            elif txt[-3:] == ".sh":
                continue


            if txt[0] != " ":
                if txt[0] == "R":
                    tmp["Status"] += f"{txt[0]}\n"
                    tmp["Dockerfiles"] += f"{txt.split()[1]}  {txt.split()[2]}\n"
                    if txt[0:4] != "R100": # 完全一致のRenameじゃないなら git show 
                        revisionFileList = appendRevisionFile(revisionFileList, tmp["CommitID"], txt.split()[2])
                else:
                    tmp["Status"] += f"{txt[0]}\n"
                    tmp["Dockerfiles"] += f"{txt.split()[1]}\n"
                    if txt[0] != "D":
                        revisionFileList = appendRevisionFile(revisionFileList, tmp["CommitID"], txt.split()[1])

    result, tmp = appendToResult(result, tmp)
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

        RevisonsHaveDocker(repository, txtGitFileStatus)


