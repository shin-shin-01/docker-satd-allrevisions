from setting import PATH_OF_SATD_COMMENTFILE_ADDINFO, PATH_OF_UNIQUE_SATD_INFO
from tqdm import tqdm
import os
import re
import pandas as pd



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

    result = pd.DataFrame(columns=col)

    uniqueLatestNameList = df["LatestDockerfile"].unique()

    for fileName in uniqueLatestNameList:
        df_File = df[ df["LatestDockerfile"] == fileName ]
        df_File = df_File.sort_values('Date') # 定期的にソートしておく
        uniqueCommentList = df_File["Comment"].unique()

        for comment in uniqueCommentList:
            # Dockerfile ごとのユニークなコメント
            df_FileComment = df_File[ df_File["Comment"] == comment ]
            df_FileComment = df_FileComment.sort_values('Date') # 定期的にソートしておく

            firstCommitRow = df_FileComment.head(1).iloc[0, :]
            LatestCommentDate = df_FileComment.tail(1).iloc[0, :]["Date"]

            # 同一Dockerfile のコミット履歴に対して、対象SATDの最終コミット日より後で直近の日付を '削除された日' として取得したい
            tmp_date = df_File[ df_File["Date"] > LatestCommentDate ]

            if comment in tmp_date["Comment"].tolist():
                # 同一ファイル
                print("Error: 対象SATDの最終コミット日よりあとのデータに対象SATDが含まれています．\n === コードを修正してください。===")
                exit()

            if len(tmp_date) == 0:
                # 削除されていたらその日付 されていなければ Nan
                firstCommitRow["DeletedComment Date"] = firstCommitRow["Deleted Date"]
            else:
                firstCommitRow["DeletedComment Date"] = tmp_date.head(1).iloc[0, :]["Date"]

            result = result.append(firstCommitRow)
    result.to_csv(f'{PATH_OF_UNIQUE_SATD_INFO}/{csvfile}')

        

if __name__ == "__main__":
    csvfiles = getTargetCSV()

    for csvfile in tqdm(csvfiles):
        removeSameSATDofSameFile(csvfile)



