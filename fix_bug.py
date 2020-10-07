"""
日付をまとめる際にSATDのみのファイルから日付を選択していた。
実際にコメントを全て消したようなファイルからは日付を取れていないのでコミット情報から取得する。
"""


"""
どこかにまとめる予定
"""

import pandas as pd
import numpy as np
import os


def getTargetDataFrame(repository):
    df = pd.read_csv(f"./2-gitlogsCSV/{repository}.csv", index_col=0)
    df = df.dropna(subset=['Dockerfile'])
    df = df[["CommitID", "Date", "Dockerfile", "Status"]]
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    return df


def getCommentDeleteDate(repository, filename, latestCommitDate):
    """
    File Delete は D でコミット日時を取れるので大丈夫
    """
    df = getTargetDataFrame(repository)
    df = df[df["Dockerfile"].apply(lambda files: filename in files)]
    # LatestCommit日(SATDが含まれる最終コミット日) よりあとのコミット情報を取得する。 
    df = df[ df["Date"] > latestCommitDate ]
    
    if len(df) == 0:
        return np.nan, np.nan
    else:
        return df.head(1).iloc[0, :]["Date"], df.head(1).iloc[0, :]["CommitID"]


if __name__ == "__main__":
    pass