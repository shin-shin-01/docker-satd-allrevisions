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
from setting import PATH_OF_GITLOGCSV


def getTargetDataFrame(repository):
    df = pd.read_csv(f"./{PATH_OF_GITLOGCSV}/{repository}.csv", index_col=0)
    df["logIndex"] = df.index
    df = df. dropna(subset=['Dockerfile'])
    df = df[["CommitID", "Date", "Dockerfile", "Status", "logIndex"]]
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    return df


def getCommentDeleteDate(repository, renameList, latestCommitDate, latestCommitID, latestLogIndex):
    """
    File Delete は D でコミット日時を取れるので大丈夫
    → 複数回 Delete されていたら最初の Delete を取得するが
    → ファイルdeleteとして記載しているのは 最後の Delete である
    → よって D の場合は最後をとるように変更する
    """
    df = getTargetDataFrame(repository)

    for filename in renameList.splitlines():
        df = df[df["Dockerfile"].apply(lambda file: filename == file)]
        # LatestCommit日(SATDが含まれる最終コミット日) よりあとのコミット情報を取得する。 
        df = df[ (df["logIndex"] < latestLogIndex) & (df["CommitID"] != latestCommitID) & (df["Date"] >= latestCommitDate) ]

        if len(df) > 0: # 存在していたらその時点で renamelist 終了
            break

    if len(df) == 0: # 存在していなかったら削除されていない
        return np.nan, np.nan, np.nan

    # 削除に関しては 最後を残して全て削除
    delete_index = df[df["Status"] == "D"].index.tolist()
    df.drop(index=delete_index[:-1], inplace=True)

    return df.head(1).iloc[0, :]["Date"], df.head(1).iloc[0, :]["CommitID"], filename


if __name__ == "__main__":
    pass