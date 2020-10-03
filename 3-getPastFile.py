from setting import PATH_OF_REVISIONFILE_TXT, PATH_OF_PASTFILE, PATH_OF_GITCLONE, PATH_OF_ERROR_NOT_EXISTS_PASTFILE
from tqdm import tqdm
import subprocess
import os
import re
import pandas as pd



"""
outputCSV
> CommitID
> Date
> Dockerfiles
> Status
"""

## いずれ対象を絞るかもしれない
def getTargetTXT(txtfile):
    if txtfile[-4:] != ".txt":
        print(f"Error: Not TXT file -> {txtfile}")
        return False

    return True


def createSaveFileName(revision, filename):
    """
        保存名が難しいので注意！！！
    """
    filename = filename.replace("/", "___")
    return f"{revision}___{filename}.txt"


def ShowPastFile(revision, cloneDirName, filename):
    cwd = f"{PATH_OF_GITCLONE}/{cloneDirName}"
    command = f"git show {revision}:{filename}"

    # show revision
    tmp = subprocess.run(list(command.split()), cwd=cwd, encoding='utf-8', stdout=subprocess.PIPE, errors="ignore")

    if tmp.stdout == "":
        with open(PATH_OF_ERROR_NOT_EXISTS_PASTFILE, 'a+') as f:
            msg = f"fatal: Path '{filename}' does not exist in '{revision}'"
            f.seek(0)
            if not msg in f.read():
                f.write(f"{msg}\n")

            return False
        
    return tmp.stdout


def CheckoutSaveTXT(revisionFileList, cloneDirName):
    # save されているファイル一覧を取得
    savePath = f"./{ PATH_OF_PASTFILE}/{cloneDirName}"
    try:
        savedFile = os.listdir(savePath)
    except FileNotFoundError:
        cwd = "./"
        command = f"mkdir {savePath}"
        tmp = subprocess.run(list(command.split()), cwd=cwd, encoding='utf-8', stdout=subprocess.PIPE, errors="ignore")
        savedFile = []

    for revisionFile in revisionFileList:
        revision = revisionFile.split(':')[0]
        filename = revisionFile.split(':')[1].replace('\n', '')
        
        savefilename = createSaveFileName(revision, filename)
        if savefilename in savedFile:
            continue

        txt = ShowPastFile(revision, cloneDirName, filename)

        if not txt: #過去ファイルを取得できなかった場合
            continue

        with open(f"{savePath}/{savefilename}", "w") as f:
            f.write(txt)



if __name__ == "__main__":
    txtfiles = os.listdir(f'{PATH_OF_REVISIONFILE_TXT}')

    for txtfile in tqdm(txtfiles):
        if not getTargetTXT(txtfile):
            continue
        
        with open(f'{PATH_OF_REVISIONFILE_TXT}/{txtfile}', "r") as f:
            revisionFileList = f.readlines()

            cloneDirName = txtfile[:-4]
            CheckoutSaveTXT(revisionFileList, cloneDirName)
