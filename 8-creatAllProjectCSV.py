from setting import PATH_OF_UNIQUE_SATD_INFO, PATH_OF_ALLPROJECT_CSV
from tqdm import tqdm
import os
import re
import pandas as pd
from datetime import datetime
import hashlib

"""
必要になった情報はここでまとめていきます
"""

def getTargetCSV():
    csvfiles = os.listdir(PATH_OF_UNIQUE_SATD_INFO)
    targetCsvfiles = []
    for csvfile in csvfiles:
        if csvfile == ".DS_Store":
            print("CSV file Error: .DS_Store")
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


def modifyColumnName():
    Columns = [
        'project',
        'gitPath',
        'CommitID',
        'Deleted CommitID',
        'Dockerfile',
        'LatestDockerfile',
        'Comment',
        'Date',
        'DeletedComment Date',
        'FirstCommit Date',
        'Deleted Date',
        'isSATD'
        ]

    df = pd.DataFrame(columns=Columns)
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
    df["削除時ファイル"] = df["gitPath"] + '/commit/' + df['Deleted CommitID'] + "#diff-" + df["LatestDockerfile"].apply(lambda f: hashlib.md5(f.encode()).hexdigest())
    return df
        

if __name__ == "__main__":
    csvfiles = getTargetCSV()
    result = modifyColumnName()

    for csvfile in tqdm(csvfiles):
        df = ReadCSV_addGitPath(csvfile)
        result = pd.concat([result, df], ignore_index=True)


    result = convertDateTime(result)
    result = renameColumns(result)
    result = addDateCalculatedInfo(result)
    result = addDiff(result)

    result.to_csv(f'{PATH_OF_ALLPROJECT_CSV}/result.csv')




