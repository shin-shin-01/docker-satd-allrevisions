from setting import PATH_OF_GITLOGCSV, PATH_OF_PASTFILE, PATH_OF_GITCLONE, PATH_OF_ERROR_NOT_EXISTS_PASTFILE
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
def getTargetCSV(csvfile):
    if csvfile[-4:] != ".csv":
        print("Error: Not CSV file")
        return False

    return True
    
def getDf(csvfile):
    df = pd.read_csv(f'./{PATH_OF_GITLOGCSV}/{csvfile}')
    df = df.dropna(subset=['Dockerfiles'])

    return df


def createSaveFileName(revision, filename):
    """
        保存名が難しいので注意！！！
    """
    filename = filename.replace("/", "___")
    return f"{revision}___{filename}.txt"


def notAlreadyExist(savefilename, savePath):
    try:
        if savefilename in os.listdir(savePath):
            print("Already Exists!")
            return False
    except FileNotFoundError:
        cwd = "./"
        command = f"mkdir {savePath}"
        tmp = subprocess.run(list(command.split()), cwd=cwd, encoding='utf-8', stdout=subprocess.PIPE, errors="ignore")

    return True


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


def CheckoutSaveTXT(row, csvfile):
    revision = row["CommitID"]

    statuses = str(row["Status"]).splitlines()
    filenames = str(row["Dockerfiles"]).splitlines()
    cloneDirName = csvfile[:-4]

    for i in range(len(filenames)):
        status = statuses[i]
        filename = filenames[i]

        if status == "D" or status == "R":
            continue
        
        savefilename = createSaveFileName(revision, filename)
        savePath = f"./{ PATH_OF_PASTFILE}/{cloneDirName}"

        if not notAlreadyExist(savefilename, savePath):
            continue

        txt = ShowPastFile(revision, cloneDirName, filename)

        if not txt:
            continue

        with open(f"{savePath}/{savefilename}", "w") as f:
            f.write(txt)





if __name__ == "__main__":
    csvfiles = os.listdir(PATH_OF_GITLOGCSV)

    for csvfile in tqdm(csvfiles):
        if not getTargetCSV(csvfile):
            continue

        df = getDf(csvfile)
        for index, row in df.iterrows():
            CheckoutSaveTXT(row, csvfile)
