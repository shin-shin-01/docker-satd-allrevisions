from setting import PATH_OF_GITLOGCSV, PATH_OF_SATD_COMMENTFILE, PATH_OF_SATD_COMMENTFILE_ADDINFO, PATH_OF_ERROR_ADDINFO
from tqdm import tqdm
import os
import re
import pandas as pd


def getTargetSatdCSV():
    csvfiles = os.listdir(PATH_OF_SATD_COMMENTFILE)
    targetCsvfiles = []

    for csvfile in csvfiles:
        if csvfile[-4:] != ".csv":
            print(f"File Error: invalid file -> {csvfile}")
            continue
        if csvfile in os.listdir(PATH_OF_SATD_COMMENTFILE_ADDINFO):
            print(f"AlreadyExists : {csvfile}")
            continue

        targetCsvfiles.append(csvfile)
    
    print("\n ===== 要素数が０のファイルは保存されずに実行されます =====\n")
    return targetCsvfiles


def getDataFrame(csvfile):
    df = pd.read_csv(f'{PATH_OF_SATD_COMMENTFILE}/{csvfile}', index_col=0, encoding='utf-8-sig')
    gitlog = pd.read_csv(f'{PATH_OF_GITLOGCSV}/{csvfile}', index_col=0, encoding='utf-8-sig')


    try:
        df["Dockerfiles"] = df["Dockerfiles"].apply(lambda fileName: fileName[1:] if fileName[0] == "/" else fileName)
        gitlog["Dockerfiles"] = gitlog["Dockerfiles"].apply(
            lambda fileNames: '\n'.join(
                list(map(lambda fileName: fileName[1:] if fileName[0] == "/" else fileName, str(fileNames).splitlines() ))
            ))
    except KeyError: #Dockerfiles
        pass

    return df, gitlog


def getRenamePairListFromGitLog(gitlog):
    df = gitlog.copy(deep=True)
     # isDockerFile
    df = df.dropna(subset=['Dockerfiles'])
    # isRename
    df = df[ df["Status"].apply(lambda st: "R" in str(st)) ]

    renameDict = {
        "count": 0,
        "beforeName": [],
        "afterName": []
    }
    
    # get Rename
    for index, row in df.iterrows():
        dockerfiles = row["Dockerfiles"].splitlines()
        statuses = row["Status"].splitlines()
        for i in range(len(dockerfiles)):
            if statuses[i] == "R":
                dockerfile = dockerfiles[i].split()
                renameDict["count"] += 1
                renameDict["beforeName"].append(dockerfile[0])
                renameDict["afterName"].append(dockerfile[1])

    renameDict["beforeName"] = renameDict["beforeName"][::-1]
    renameDict["afterName"] = renameDict["afterName"][::-1]

    return renameDict


def renameFile(fileName, renameDict):
    for i in range(renameDict["count"]):
        if fileName == renameDict["beforeName"][i]:
            fileName = renameDict["afterName"][i]
        
    return fileName


def renameFileToLatest(df, gitlog):
    renameDict = getRenamePairListFromGitLog(gitlog)

    df["LatestDockerfile"] = df["Dockerfiles"]
    
    df["LatestDockerfile"] = df["LatestDockerfile"].apply(lambda fileName: renameFile(fileName, renameDict))

    return df, renameDict
 

def addCommitDate(df, gitlog):
    gitlog = gitlog[["CommitID", "Date"]]
    df = pd.merge(df, gitlog, on=["CommitID"])
    return df


def getFirstDateOfDockerfileFromGitLog(gitlog):
    df = gitlog.copy(deep=True)
     # isDockerFile
    df = df.dropna(subset=['Dockerfiles'])
    # isAdded
    df = df[ df["Status"].apply(lambda st: "A" in str(st)) ]

    firstCommitDateDict = {
        "filename": [],
        "FirstCommit Date": []
    }
    
    # get Rename
    for index, row in df.iterrows():
        dockerfiles = row["Dockerfiles"].splitlines()
        statuses = row["Status"].splitlines()
        for i in range(len(dockerfiles)):
            if statuses[i] == "A":
                firstCommitDateDict["filename"].append(dockerfiles[i])
                firstCommitDateDict["FirstCommit Date"].append(row["Date"])

    firstCommitDateDataFrame = pd.DataFrame.from_dict(firstCommitDateDict)

    return firstCommitDateDataFrame


def addFirstCommitDate(df, gitlog):
    global renameDict
    firstCommitDateDataFrame = getFirstDateOfDockerfileFromGitLog(gitlog)
    firstCommitDateDataFrame["filename"] = firstCommitDateDataFrame["filename"].apply(lambda fileName: renameFile(fileName, renameDict))

    # 互いに最新ファイルで比較
    df = pd.merge(df, firstCommitDateDataFrame, left_on=['LatestDockerfile'], right_on=['filename'], how='left')
    return df
    

def getDeletedDateOfDockerfileFromGitLog(gitlog):
    df = gitlog.copy(deep=True)
     # isDockerFile
    df = df.dropna(subset=['Dockerfiles'])
    # isAdded
    df = df[ df["Status"].apply(lambda st: "D" in str(st)) ]

    deleteCommitDateDict = {
        "filename": [],
        "Deleted Date": []
    }
    
    # get Rename
    for index, row in df.iterrows():
        dockerfiles = row["Dockerfiles"].splitlines()
        statuses = row["Status"].splitlines()
        for i in range(len(dockerfiles)):
            if statuses[i] == "D":
                deleteCommitDateDict["filename"].append(dockerfiles[i])
                deleteCommitDateDict["Deleted Date"].append(row["Date"])

    deleteCommitDateDataFrame = pd.DataFrame.from_dict(deleteCommitDateDict)

    return deleteCommitDateDataFrame


def addDeletedCommitDate(df, gitlog):
    deleteCommitDateDataFrame = getDeletedDateOfDockerfileFromGitLog(gitlog)

    # 互いに最新ファイルで比較
    df = pd.merge(df, deleteCommitDateDataFrame, left_on=['LatestDockerfile'], right_on=['filename'], how='left')
    return df

def writeError(log):
    with open(PATH_OF_ERROR_ADDINFO, "a+") as f:
        f.seek(0)
        if not log in f.read():
            f.write(f"{log}\n")


if __name__ == "__main__":
    """
    ・ファイル名変更にて、Dockerfile などの名前が複数回定義されたときにエラーが発生する
    例）
    → 202001にDockerfileを作成し, 202002に/ver2/Dockerfile に名前を変更
    → 202007にDockerfileを作成し, 202008に/ver3/Dockerfile に名前を変更

    ・削除された日付や追加された日付が複数存在する時がある
    → 同じファイルが何度も追加削除されたとき
    """

    csvfiles = getTargetSatdCSV()

    for csvfile in tqdm(csvfiles):
        df, gitlog = getDataFrame(csvfile)

        length = len(df)
        if length == 0:
            errorlog = f"FileData Error: {csvfile} : CSVファイルの中身が無いです。"
            writeError(errorlog)
            continue

        df, renameDict = renameFileToLatest(df, gitlog)
        if len(df) != length:
            errorlog = f"RENAME Error: {csvfile} :最終的な出力結果数が変わっています。{length} -> {len(df)}"
            print(errorlog)
            writeError(errorlog)

        df = addCommitDate(df, gitlog)
        if len(df) != length:
            errorlog = f"DATE Error: {csvfile} :最終的な出力結果数が変わっています。{length} -> {len(df)}"
            print(errorlog)
            writeError(errorlog)

        df = addFirstCommitDate(df, gitlog)
        if len(df) != length:
            errorlog = f"FIRSTDATE Error: {csvfile} :最終的な出力結果数が変わっています。{length} -> {len(df)}"
            print(errorlog)
            writeError(errorlog)

        df = addDeletedCommitDate(df, gitlog)
        if len(df) != length:
            errorlog = f"DELETE DATE Error: {csvfile} :最終的な出力結果数が変わっています。{length} -> {len(df)}"
            print(errorlog)
            writeError(errorlog)

        df = df.reindex(columns=['CommitID', 'Dockerfiles', 'LatestDockerfile', 'Comments', 'Date', 'FirstCommit Date', 'Deleted Date', 'isSATD'])
        df.to_csv(f'{PATH_OF_SATD_COMMENTFILE_ADDINFO}/{csvfile}')
