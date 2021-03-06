import pandas as pd
import os
import re

from setting import PATH_OF_ALLPROJECT_CSV_UPDATE, PATH_OF_COMMENTFILE, PATH_OF_PASTFILE, PATH_OF_SATD_COMMENTFILE


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

    comments = df["Comment"]
    print(f"リビジョン統合前全コメント数 \n→{len(comments)}")

    uniqueComment = df["Comment"].unique()
    print(f"UniqueComments from 4-rowComments (全プロジェクト全リビジョンでのユニークコメント検出)   \n→{len(uniqueComment)}")


def countSATDbeforeRevisionMerge():
    countSATD = 0 
    csvfiles = os.listdir(f'{PATH_OF_SATD_COMMENTFILE}')
    for csvfile in csvfiles:
        if csvfile == ".DS_Store":
            continue
        df = pd.read_csv(f'{PATH_OF_SATD_COMMENTFILE}/{csvfile}', index_col=0)
        countSATD += len(df)

    print(f"Comments from 5-SATDComments (全プロジェクト全リビジョンでのSATD検出)   \n→{countSATD}")




def countUniqueSATD():
    df = pd.read_csv(f'{PATH_OF_ALLPROJECT_CSV_UPDATE}/result.csv', index_col=0)
    
    SATD = df["Comment"]
    print(f"SATD from 8-result.csv (全プロジェクト全リビジョンでのSATD検出(Fileが異なる物は異なるものとしてカウント -> file ごとにコメントマージ)) \n→{len(SATD)}")

    uniqueSATD = df["Comment"].unique()
    print(f"UniqueSATD from 8-result.csv (全プロジェクト全リビジョンでのユニークSATD検出) \n→{len(uniqueSATD)}")



def countDeletedSATD():
    df = pd.read_csv(f'{PATH_OF_ALLPROJECT_CSV_UPDATE}/result.csv', index_col=0)
    tmp = df[df["コメント追加からコメント削除までの日数"] != "削除されていません"]
    uniqueSATD = tmp["Comment"].unique()
    print(f"削除されたユニークSATD (ファイル削除・コメント削除) \n→{len(uniqueSATD)}")

    tmp = df[df["コメント追加からコメント削除までの日数"].apply(lambda delete: True if delete == "ファイル削除" else False)]
    uniqueSATD = tmp["Comment"].unique()
    print(f"削除されたユニークSATD (ファイル削除) \n→{len(uniqueSATD)}")

    tmp = df[df["コメント追加からコメント削除までの日数"].apply(lambda delete: False if delete in ["削除されていません", "ファイル削除"] else True)]
    uniqueSATD = tmp["Comment"].unique()
    print(f"削除されたユニークSATD (コメント削除)\n→{len(uniqueSATD)}")

    tmp = df[df["コメント追加からコメント削除までの日数"].apply(lambda delete: True if delete == "削除されていません" else False)]
    uniqueSATD = tmp["Comment"].unique()
    print(f"削除されていないユニークSATD \n→{len(uniqueSATD)}")
    
    """
    同一コメントでも削除された物と存在しているものが複数のファイル（プロジェクト）にまたがって存在しているため数が合わなくなっている
    """



if __name__ == "__main__":
    countAllModifiedRevisionOfDockerfile()
    countUniqueComment()
    countSATDbeforeRevisionMerge()
    countUniqueSATD()
    countDeletedSATD()
