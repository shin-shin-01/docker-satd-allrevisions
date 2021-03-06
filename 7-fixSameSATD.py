from setting import PATH_OF_SATD_COMMENTFILE_ADDINFO, PATH_OF_UNIQUE_SATD_INFO
from tqdm import tqdm
import os
import re
import pandas as pd
import numpy as np

from fix_bug import getCommentDeleteDate


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

"""
SATDで判断してるの良くない → 次のコミットがあるかどうかで判断する
Delete はそのままで良くて、削除されていないものは 次のコミットがあるかどうか確認。
"""
def removeSameSATDofSameFile(csvfile):
    df = pd.read_csv(f'{PATH_OF_SATD_COMMENTFILE_ADDINFO}/{csvfile}', index_col=0)
    repository = csvfile[:-4]
    df["Date"] = pd.to_datetime(df["Date"], utc=True)

    col = df.columns.tolist()
    col.append("DeletedComment Date")
    col.append("Deleted CommitID")

    result = pd.DataFrame(columns=col)

    uniqueLatestNameList = df["LatestDockerfile"].unique()

    for fileName in uniqueLatestNameList:
        df_Fileunique = df[ df["LatestDockerfile"] == fileName ]
        df_Fileunique = df_Fileunique.sort_values('Date') # 定期的にソートしておく
        # 小文字・大文字の変化も削除になってしまうため、全てを小文字に変換しておく
        tmpComment = df_Fileunique["Comment"].apply(lambda st: st.lower())
        uniqueCommentList = tmpComment.unique()

        # 同一ファイルのユニークコメントごとに処理を行う
        for comment in uniqueCommentList:
            # Dockerfile ごとのユニークなコメント
            df_FileCommentunique = df_Fileunique[ df_Fileunique["Comment"].apply(lambda st: st.lower() == comment) ]
            # 同一日付 は git log の index を元に判断する 
            df_FileCommentunique = df_FileCommentunique.sort_values(['Date', 'logIndex'], ascending=[True, False]) # 定期的にソートしておく

            firstCommitRow = df_FileCommentunique.head(1).iloc[0, :]
            LatestCommentRow = df_FileCommentunique.tail(1).iloc[0, :]

            # 同一Dockerfile のコミット履歴に対して、対象SATDの最終コミット日より後で直近の日付を '削除された日' として取得したい
            tmp_date = df_Fileunique[ df_Fileunique["Date"] > LatestCommentRow["Date"] ]

            deleted_date, commit_id, author, filename = getCommentDeleteDate(repository, LatestCommentRow["RenameList"], LatestCommentRow["Date"], LatestCommentRow["CommitID"], LatestCommentRow["logIndex"])

            # tmp_df (SATD のみのDataFrame) であるため、完全に削除されたあとは git log から コミット日時・ファイル名 を元に次のコミット日時 を取得
            if len(tmp_date) == 0:
                pass
            elif str(deleted_date) == "nan":
                deleted_date = tmp_date.head(1).iloc[0, :]["Date"]
                commit_id = tmp_date.head(1).iloc[0, :]["CommitID"]
                author = tmp_date.head(1).iloc[0, :]["Author"]
                filename = tmp_date.head(1).iloc[0, :]["Dockerfile"]
            elif tmp_date.head(1).iloc[0, :]["Date"] < deleted_date:
                deleted_date = tmp_date.head(1).iloc[0, :]["Date"]
                commit_id = tmp_date.head(1).iloc[0, :]["CommitID"]
                author = tmp_date.head(1).iloc[0, :]["Author"]
                filename = tmp_date.head(1).iloc[0, :]["Dockerfile"]     
            
            firstCommitRow["DeletedComment Date"] = deleted_date
            firstCommitRow["Deleted CommitID"] = commit_id
            firstCommitRow["Delete Author"] = author
            firstCommitRow["Deleted Filename"] = filename

            result = result.append(firstCommitRow)
    result.to_csv(f'{PATH_OF_UNIQUE_SATD_INFO}/{csvfile}')

        

if __name__ == "__main__":
    csvfiles = getTargetCSV()

    for csvfile in tqdm(csvfiles):
        removeSameSATDofSameFile(csvfile)
