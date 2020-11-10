from setting import PATH_OF_UNIQUE_SATD_INFO, PATH_OF_ALLPROJECT_CSV, PATH_OF_GITCLONE
from tqdm import tqdm
import os
import re
import pandas as pd
from datetime import datetime
import subprocess
import hashlib

"""
必要になった情報はここでまとめていきます
"""

# docker/docker-ce と moby/moby が一致しているため削除
def delete_moby_moby(df):
    df = df[df["project"] != "moby\nmoby"]
    return df

def getTargetCSV():
    csvfiles = os.listdir(PATH_OF_UNIQUE_SATD_INFO)
    targetCsvfiles = []
    for csvfile in csvfiles:
        if csvfile == ".DS_Store":
            print("CSV file Error: .DS_Store")
            continue
        elif csvfile == "docker_docker.csv":
            print("docker/docker is same to moby")
            continue

        targetCsvfiles.append(csvfile)
    
    return targetCsvfiles


def ReadCSV_addGitPath(csvfile):
    df = pd.read_csv(f'{PATH_OF_UNIQUE_SATD_INFO}/{csvfile}', index_col=0)
    fileName = csvfile[:-4].split('_')
    accountName = fileName[0]
    projectName = '_'.join(fileName[1:])
    
    gitPath = f'https://github.com/{accountName}/{projectName}'

    df['project'] = f'{accountName}\n{projectName}'
    df["gitPath"] = gitPath

    return df


def convertDateTime(df):
    for col in df.columns:
        if not 'Date' in col:
            continue
        df[col] = pd.to_datetime(df[col], utc=True)
        df[col] = df[col].dt.tz_convert('Asia/Tokyo')
        df[col] = df[col].dt.strftime('%Y/%m/%d %H:%M')
    
    return df


def renameColumns(df):
    renameColumns = {
        'Date': 'CommitDate',
        'DeletedComment Date': 'DeleteComment',
        'FirstCommit Date': '(File) FirstCommit',
        'Deleted Date': '(File) Deleted',
    }

    df.rename(columns=renameColumns, inplace=True)
    return df


def addDateCalculatedInfo(df):
    listOfDateFromfirstCommit = []
    listOfDateToDeleteComment = []

    for index, row in df.iterrows():
        listOfDateFromfirstCommit.append((datetime.strptime(row['CommitDate'], '%Y/%m/%d %H:%M') - datetime.strptime(row['(File) FirstCommit'], '%Y/%m/%d %H:%M')))
        if str(row['DeleteComment']) == 'nan':
            listOfDateToDeleteComment.append('削除されていません')
        else:
            if row['DeleteComment'] == row['(File) Deleted']:
                listOfDateToDeleteComment.append('ファイル削除')
            else:
                listOfDateToDeleteComment.append((datetime.strptime(row['DeleteComment'], '%Y/%m/%d %H:%M') - datetime.strptime(row['CommitDate'], '%Y/%m/%d %H:%M')))

    df["firstCommitからコメント追加までの日数"] = listOfDateFromfirstCommit
    df["コメント追加からコメント削除までの日数"] = listOfDateToDeleteComment
    return df


def addBlob(df):
    df["追加時ファイル"] = df["gitPath"] + '/blob/' + df['CommitID'] + "/" + df["Dockerfile"]
    df["削除時ファイル"] = df["gitPath"] + '/blob/' + df['Deleted CommitID'] + "/" + df["LatestDockerfile"]
    return df


def addDiff(df):
    df["追加時ファイル"] = df["gitPath"] + '/commit/' + df['CommitID'] + "#diff-" + df["Dockerfile"].apply(lambda f: hashlib.md5(f.encode()).hexdigest())
    df["削除時ファイル"] = df["gitPath"] + '/commit/' + df['Deleted CommitID'] + "#diff-" + df["Deleted Filename"].apply(lambda f: hashlib.md5(f.encode()).hexdigest())
    return df

def addDiff_withLine(df):
    df = calculate_line(df, "added")
    df = calculate_line(df, "deleted")

    df["追加時ファイル"] = df["gitPath"] + '/commit/' + df['CommitID'] + "#diff-" + df["Dockerfile"].apply(lambda f: hashlib.sha256(f.encode()).hexdigest()) + df["added_line"]
    # deleted filter
    mask = df["Deleted CommitID"].apply(lambda s: str(s) != "nan")
    df.loc[mask, "削除時ファイル"] = df.loc[mask, "gitPath"] + '/commit/' + df.loc[mask, 'Deleted CommitID'] + "#diff-" + df.loc[mask, "Deleted Filename"].apply(lambda f: hashlib.sha256(f.encode()).hexdigest()) + df.loc[mask, "deleted_line"]
    return df


def calculate_line(df, add_delete):
    line_list = []

    for idx, row in df.iterrows():
        if add_delete == "added":
            plus_minus = "+"
            filename = row["Dockerfile"]
            commit_id = row["CommitID"]
        elif add_delete == "deleted":
            plus_minus = "-"
            filename = row["Deleted Filename"]
            commit_id = row["Deleted CommitID"]

        # 削除が存在していない場合
        if str(commit_id) == "nan":
            line_list.append(None)
            continue
        
        txtGitdiff = git_difference(commit_id, filename, row["project"])
        line = get_targetComment_line(txtGitdiff, row["Comment"], plus_minus)
        line_list.append(line)

    df[f"{add_delete}_line"] = line_list
    return df


def git_difference(commit_id, filename, project):
    repository = project.splitlines()[0] + "_" + project.splitlines()[1]

    # git dif
    command = f'git diff -U10000 {commit_id}^..{commit_id} -- {filename}'
    cwd = f'./{PATH_OF_GITCLONE}/{repository}/'

    # ignore utf-8 Error
    txtGitdiff = subprocess.run(command, cwd=cwd, encoding='utf-8', stdout=subprocess.PIPE, errors="ignore", shell=True)
    txtGitdiff = str(txtGitdiff.stdout)

    # 最初のコミットだった時
    if txtGitdiff == "":
        # git dif
        command = f'git diff -U10000 4b825dc642cb6eb9a060e54bf8d69288fbee4904..{commit_id} -- {filename}'
        cwd = f'./{PATH_OF_GITCLONE}/{repository}/'

        # ignore utf-8 Error
        txtGitdiff = subprocess.run(command, cwd=cwd, encoding='utf-8', stdout=subprocess.PIPE, errors="ignore", shell=True)
        txtGitdiff = str(txtGitdiff.stdout)

    return txtGitdiff

def get_targetComment_line(txtGitdiff, comment, plus_minus):
    global error
    start = False
    count = 0 # 過去のファイルの行数カウント
    comment = comment.lower()


    if plus_minus == "+":
        rev = "-"
        LR = "R"
    else:
        rev = "+"
        LR = "L"
    
    for diffrow in txtGitdiff.splitlines():
        if diffrow[0] == "@":
            start = True
            continue
        elif not start:
            continue

        if (diffrow[0] == rev):
            continue
        elif (diffrow[0] == plus_minus):
            count += 1
            if (diffrow[1:] == "#") or (diffrow[1:] == ""):
                continue
            elif (diffrow[1:].lower() in comment.splitlines()):
                return f"{LR}{count}"
        else:
            count += 1

    # SATD 自体が変更されずに　コメント削除になったもの
    targetCommentflg = False
    diffCommentflg = False
    start = False
    count = 0
    for diffrow in txtGitdiff.splitlines():
        if diffrow[0] == "@":
            start = True
            continue
        elif not start:
            continue

        if diffrow[1:] != "#" and diffrow[1:] != "" and (diffrow[1:].lower() in comment.splitlines()):
            count += 1
            targetCommentflg = True
            if diffCommentflg:
                return f"R{count}"

        elif diffrow[0] == "+":
            count += 1
            diffCommentflg = True
            if targetCommentflg:
                return f"R{count - 1}"

        elif diffrow[0] == "-":
            diffCommentflg = True
            if targetCommentflg:
                return f"R{count}"
        else:
            count += 1
            targetCommentflg = False
            diffCommentflg = False

    error = error.append({"type": plus_minus, "comment": comment, "diff": txtGitdiff}, ignore_index=True)
    return "Error"

def modifyColumnName(df):
    cols = [
        'project',
        'gitPath',
        'CommitID',
        'Deleted CommitID',
        'LatestDockerfile',
        'Comment',
        'CommitDate',
        'DeleteComment',
        '(File) FirstCommit',
        '(File) Deleted',
        'firstCommitからコメント追加までの日数',
        'コメント追加からコメント削除までの日数',
        '追加時ファイル',
        '削除時ファイル'
        ]
    
    return result[cols]
        

if __name__ == "__main__":
    csvfiles = getTargetCSV()
    error = pd.DataFrame(columns=["type", "comment", "diff"])

    for csvfile in csvfiles:
        df = ReadCSV_addGitPath(csvfile)
        try:
            result = pd.concat([result, df], ignore_index=True)
        except NameError:
            result = df.copy(deep=True)

    result = convertDateTime(result)
    result = renameColumns(result)
    result = addDateCalculatedInfo(result)
    result = addDiff_withLine(result)

    result = modifyColumnName(result)
    result = delete_moby_moby(result)

    result.to_csv(f'{PATH_OF_ALLPROJECT_CSV}/result.csv')
    error.to_csv(f'{PATH_OF_ALLPROJECT_CSV}/errorcomment.csv')
