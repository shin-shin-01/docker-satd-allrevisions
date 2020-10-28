import pandas as pd
import os
import re

from setting import PATH_OF_ALLPROJECT_CSV



def get_unique_satd_toCSV(df):
    df[["Comment"]].drop_duplicates().to_csv("./a-extractComment/uniqueALLSATD.csv")


def get_unique_satd_with_deleteInfo_toCSV(df):
    tmp = df[df["コメント追加からコメント削除までの日数"] == "削除されていません"]
    tmp.to_csv("./a-extractComment/SATDnotDeletedWithInfo.csv")
    tmp = tmp[["Comment"]].drop_duplicates().to_csv("./a-extractComment/SATDnotDeleted.csv")

    tmp = df[df["コメント追加からコメント削除までの日数"] == "ファイル削除"]
    tmp.to_csv("./a-extractComment/SATDfileDeletedWithInfo.csv")
    tmp = tmp[["Comment"]].drop_duplicates().to_csv("./a-extractComment/SATDfileDeleted.csv")

    tmp = df[df["コメント追加からコメント削除までの日数"].apply(lambda delete: False if delete in ["削除されていません", "ファイル削除"] else True)]
    tmp.to_csv("./a-extractComment/SATDDeletedWithInfo.csv")
    tmp = tmp[["Comment"]].drop_duplicates().to_csv("./a-extractComment/SATDDeleted.csv")


def get_azuma_count(df):
    """
    プロジェクトごとに SATD　のユニークを取得している
    """
    df = df[df["コメント追加からコメント削除までの日数"] == "削除されていません"]
    df = df[df["LatestDockerfile"].apply(lambda filename: filename[-10:] == "Dockerfile")]

    print("東さんのデータに合わせた整形→行数 : ", len(df[["project", "Comment"]].drop_duplicates()))

if __name__ == "__main__":
    # df = pd.read_csv(f'{PATH_OF_ALLPROJECT_CSV}/result.csv', index_col=0)
    df = pd.read_csv(f'test.csv', index_col=0)
    get_unique_satd_toCSV(df)
    get_unique_satd_with_deleteInfo_toCSV(df)
    get_azuma_count(df)