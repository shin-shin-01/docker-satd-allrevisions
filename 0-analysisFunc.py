import pandas as pd
import os
import re

from setting import PATH_OF_ALLPROJECT_CSV, PATH_OF_COMMENTFILE, PATH_OF_PASTFILE, PATH_OF_SATD_COMMENTFILE


def countAllModifiedRevisionOfDockerfile():
    """
    全リビジョンでの Dockerfile の　'Modified commit'の数
    """
    countAllModifiedRevisions = 0 
    projects = os.listdir(f'{PATH_OF_PASTFILE}')

    for project in projects:
        if project == ".DS_Store":
            continue
        revisionDockerfiles = os.listdir(f'{PATH_OF_PASTFILE}/{project}')
        try:
            revisionDockerfiles.remove('.DS_Store')
        except ValueError:
            pass

        countAllModifiedRevisions += len(revisionDockerfiles)

    print(f"from 3-pastfiles  全Dockerfile の全プロジェクト全リビジョンでの変更されたコミット数  \n→{countAllModifiedRevisions}")



def countUniqueComment():
    csvfiles = os.listdir(f'{PATH_OF_COMMENTFILE}')
    for csvfile in csvfiles:
        if csvfile == ".DS_Store":
            continue
        try:
            df = pd.concat([df, pd.read_csv(f'{PATH_OF_COMMENTFILE}/{csvfile}', index_col=0)], ignore_index=True)
        except UnboundLocalError:
            df = pd.read_csv(f'{PATH_OF_COMMENTFILE}/{csvfile}', index_col=0)

    comments = df["Comments"]
    print(f"リビジョン統合前全コメント数 \n→{len(comments)}")

    uniqueComment = df["Comments"].unique()
    print(f"UniqueComments from 4-rowComments (全プロジェクト全リビジョンでのユニークコメント検出)   \n→{len(uniqueComment)}")


def countSATDbeforeRevisionMerge():
    countSATD = 0 
    csvfiles = os.listdir(f'{PATH_OF_SATD_COMMENTFILE}')
    for csvfile in csvfiles:
        if csvfiles == ".DS_Store":
            continue
        df = pd.read_csv(f'{PATH_OF_SATD_COMMENTFILE}/{csvfile}', index_col=0)
        countSATD += len(df)

    print(f"UniqueComments from 5-SATDComments (全プロジェクト全リビジョンでのSATD検出)   \n→{countSATD}")




def countUniqueSATD():
    df = pd.read_csv(f'{PATH_OF_ALLPROJECT_CSV}/result.csv', index_col=0)
    
    SATD = df["Comments"]
    print(f"SATD from 8-result.csv (全プロジェクト全リビジョンでのSATD検出(Fileが異なる物は異なるものとしてカウント -> file ごとにコメントマージ)) \n→{len(SATD)}")

    uniqueSATD = df["Comments"].unique()
    print(f"UniqueSATD from 8-result.csv (全プロジェクト全リビジョンでのユニークSATD検出) \n→{len(uniqueSATD)}")



def countDeletedSATD():
    df = pd.read_csv(f'{PATH_OF_ALLPROJECT_CSV}/result.csv', index_col=0)
    df = df[df["コメント追加からコメント削除までの日数"] != "削除されていません"]
    uniqueSATD = df["Comments"].unique()
    print(f"削除されたユニークSATD  \n→{len(uniqueSATD)}")
    


if __name__ == "__main__":
    countAllModifiedRevisionOfDockerfile()
    countUniqueComment()
    countSATDbeforeRevisionMerge()
    countUniqueSATD()
    countDeletedSATD()
