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


def removeSameSATDofSameFile(csvfile):
    df = pd.read_csv(f'{PATH_OF_SATD_COMMENTFILE_ADDINFO}/{csvfile}', index_col=0)

    col = df.columns.tolist()
    col.append("DeletedComment Date")

    result = pd.DataFrame(columns=col)

    uniqueLatestNameList = df["LatestDockerfile"].unique()

    for fileName in uniqueLatestNameList:
        df_File = df[ df["LatestDockerfile"] == fileName ]
        uniqueCommentList = df_File["Comments"].unique()

        for comment in uniqueCommentList:
            # Dockerfile ごとのユニークなコメント
            df_FileComment = df_File[ df_File["Comments"] == comment ]

            firstCommitRow = df_FileComment.iloc[-1, :].copy(deep=True)
            LatestCommentDate = df_FileComment.iloc[0, :]["Date"]

            # 同一Dockerfile のコミット履歴に対して、対象SATDの最終コミット日より後で直近の日付を '削除された日' として取得したい
            tmp_date = df_File[ df_File["Date"] > LatestCommentDate ]
            if len(tmp_date) == 0:
                # 削除されていたらその日付 されていなければ Nan
                firstCommitRow["DeletedComment Date"] = firstCommitRow["Deleted Date"]
            else:
                firstCommitRow["DeletedComment Date"] = tmp_date.iloc[-1, :]["Date"]

            result = result.append(firstCommitRow)
    
    result.to_csv(f'{PATH_OF_UNIQUE_SATD_INFO}/{csvfile}')

        

if __name__ == "__main__":
    csvfiles = getTargetCSV()

    for csvfile in tqdm(csvfiles):
        removeSameSATDofSameFile(csvfile)



