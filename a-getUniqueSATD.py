import pandas as pd
import os
import re

from setting import PATH_OF_ALLPROJECT_CSV_UPDATE


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


if __name__ == "__main__":
    df = pd.read_csv(f'{PATH_OF_ALLPROJECT_CSV_UPDATE}/result.csv', index_col=0)
    get_unique_satd_toCSV(df)
    get_unique_satd_with_deleteInfo_toCSV(df)
