from setting import PATH_OF_SATD_COMMENTFILE_ADDINFO, PATH_OF_UNIQUE_SATD_INFO
from tqdm import tqdm
import os
import re
import pandas as pd
import numpy as np



def getTargetCSV():
    csvfiles = os.listdir(PATH_OF_SATD_COMMENTFILE_ADDINFO)
    targetCsvfiles = []
    for csvfile in csvfiles:
        if csvfile in os.listdir(PATH_OF_UNIQUE_SATD_INFO):
            print(f"Already Exists! {csvfile}")
            continue
        if csvfile == ".DS_Store":
            print("CSV file Error: .DS_Store")
            continue

        targetCsvfiles.append(csvfile)
    
    return targetCsvfiles


"""
日付がソートされていなかった。
iloc[0, :], iloc[-1, :] でDataFrameの最初・最後の要素を取得できていなかったため head(1), tails(1) を使用
"""

def removeSameSATDofSameFile(csvfile):
    df = pd.read_csv(f'{PATH_OF_SATD_COMMENTFILE_ADDINFO}/{csvfile}', index_col=0)
    df["Date"] = pd.to_datetime(df["Date"], utc=True)

    col = df.columns.tolist()
    col.append("DeletedComment Date")
    col.append("Deleted CommitID")

    result = pd.DataFrame(columns=col)

    uniqueLatestNameList = df["LatestDockerfile"].unique()

    for fileName in uniqueLatestNameList:
        df_Fileunique = df[ df["LatestDockerfile"] == fileName ]
        df_Fileunique = df_Fileunique.sort_values('Date') # 定期的にソートしておく
        uniqueCommentList = df_Fileunique["Comment"].unique()

        # 同一ファイルのユニークコメントごとに処理を行う
        for comment in uniqueCommentList:
            # Dockerfile ごとのユニークなコメント
            df_FileCommentunique = df_Fileunique[ df_Fileunique["Comment"] == comment ]
            df_FileCommentunique = df_FileCommentunique.sort_values('Date') # 定期的にソートしておく

            firstCommitRow = df_FileCommentunique.head(1).iloc[0, :]
            LatestCommentRow = df_FileCommentunique.tail(1).iloc[0, :]

            # 同一Dockerfile のコミット履歴に対して、対象SATDの最終コミット日より後で直近の日付を '削除された日' として取得したい
            tmp_date = df_Fileunique[ df_Fileunique["Date"] > LatestCommentRow["Date"] ]

            if comment in tmp_date["Comment"].tolist():
                # 同一ファイル
                print("Error: 対象SATDの最終コミット日よりあとのデータに対象SATDが含まれています．\n === コードを修正してください。===")
                exit()

            if len(tmp_date) == 0:
                # 'コメントが削除された日' が存在しない場合に (File) Deleted Date　を適用 -> 日付もしくはNan
                firstCommitRow["DeletedComment Date"] = firstCommitRow["Deleted Date"]
                firstCommitRow["Deleted CommitID"] = np.nan

            else:
                # コメントが削除された日
                firstCommitRow["DeletedComment Date"] = tmp_date.head(1).iloc[0, :]["Date"]
                firstCommitRow["Deleted CommitID"] = tmp_date.head(1).iloc[0, :]["CommitID"]


            result = result.append(firstCommitRow)
    result.to_csv(f'{PATH_OF_UNIQUE_SATD_INFO}/{csvfile}')

        

if __name__ == "__main__":
    csvfiles = getTargetCSV()

    for csvfile in tqdm(csvfiles):
        removeSameSATDofSameFile(csvfile)



