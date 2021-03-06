from setting import PATH_OF_GITLOGCSV, PATH_OF_SATD_COMMENTFILE, PATH_OF_SATD_COMMENTFILE_ADDINFO, PATH_OF_ERROR_ADDINFO
from tqdm import tqdm
import os
import re
import pandas as pd
import numpy as np


def getTargetSatdCSV():
    csvfiles = os.listdir(PATH_OF_SATD_COMMENTFILE)
    targetCsvfiles = []

    for csvfile in csvfiles:
        if csvfile[-4:] != ".csv":
            print(f"File Error: invalid file -> {csvfile}")
            continue
        if csvfile in os.listdir(PATH_OF_SATD_COMMENTFILE_ADDINFO):
            print(f"AlreadyExists : {csvfile}")
            continue

        targetCsvfiles.append(csvfile)
    
    return targetCsvfiles


def getDataFrame(csvfile):
    df = pd.read_csv(f'{PATH_OF_SATD_COMMENTFILE}/{csvfile}', index_col=0, encoding='utf-8-sig')
    gitlog = pd.read_csv(f'{PATH_OF_GITLOGCSV}/{csvfile}', encoding='utf-8-sig')

    try:
        df["Dockerfile"] = df["Dockerfile"].apply(lambda fileName: fileName[1:] if fileName[0] == "/" else fileName)
        gitlog["Dockerfile"] = gitlog["Dockerfile"].apply(
            lambda fileNames: '\n'.join(
                list(map(lambda fileName: fileName[1:] if fileName[0] == "/" else fileName, str(fileNames).splitlines() ))
            ))
    except KeyError: # [Dockerfile] カラムが存在してない（中身がない）
        pass

    return df, gitlog


# コミットIDとコミット日の紐付け
def addCommitDate(df, gitlog):
    gitlog = gitlog[["CommitID", "Date"]]
    gitlog["logIndex"] = gitlog.index
    gitlog = gitlog.drop_duplicates(["CommitID", "Date"]) # 重複削除
    df = pd.merge(df, gitlog, on=["CommitID"])
    return df

# コミットIDとコミット者の紐付け
def addCommiter(df, gitlog):
    gitlog = gitlog[["Author"]]
    gitlog["logIndex"] = gitlog.index
    gitlog["Author"] =  gitlog["Author"].apply(lambda a: a.lstrip())
    df = pd.merge(df, gitlog, on=["logIndex"])
    return df


def modifyInformation(df, gitlog):
    """
    === 処理内容 ===
    ・rename 処理
    ・FirstCommit日 追加
    ・ファイル削除日 追加
    """

    df["LatestDockerfile"] = df["Dockerfile"]
    df["Deleted Date"] = np.nan
    df["FirstCommit Date"] = np.nan
    df["Date"] = pd.to_datetime(df["Date"])
    df["RenameList"] = df["Dockerfile"]
 
    dateStatusDataFrame = extractChangeInfo(gitlog)
    # 日付変換
    dateStatusDataFrame["Date"] = pd.to_datetime(dateStatusDataFrame["Date"])

    rename_delete_df = dateStatusDataFrame[dateStatusDataFrame["Status"].apply(lambda st: st in ["R", "D"])].iloc[::-1] # 逆順
    # 逆順にしないことで最過去の日時を追加された日時とすることができる
    added_df = dateStatusDataFrame[dateStatusDataFrame["Status"] == "A"]

    # 複数回追加されたものでも初期追加されたときの日時を利用する
    # added_df = added_df.drop_duplicates(keep='first', subset=['filename'])

    for idx, row in rename_delete_df.iterrows():
        # rename のときは 変更前名称をとる
        before_filename = row["filename"].split()[0]

        """ rename / delete [条件]
        1. ファイル名が一致している
        2. コミット日が rename/delete コミット日より前
        3. まだ削除されていない
        """
        # RenameList -> そのファイルが将来どう変更されるか？のリスト [現在のファイル名 + ... rename]
        if row["Status"] == "R":
            new_filename = row["filename"].split()[1]
            # 最新ファイルネームがどんどん新しく変更されている → renameリストに 将来の名前をどんどん追加している (最も古いファイルはすべての変更名を含む)
            renamed_logs_idx = df[(df["LatestDockerfile"] == before_filename) & (df["Date"] <= row["Date"]) & (str(df["Deleted Date"]) != "nan")].index
            for idx in renamed_logs_idx:
                df.loc[idx, "LatestDockerfile"] = new_filename
                df.loc[idx, "RenameList"] += f'\n{new_filename}'
        elif row["Status"] == "D":
            df.loc[(df["LatestDockerfile"] == before_filename) & (df["Date"] <= row["Date"]) & (str(df["Deleted Date"]) != "nan"), "Deleted Date"] = row["Date"]

        """ add
        最初に追加された時間を追加するために LatestDockerfile で名前を判断する
        → dockerfile名を rename後の LatestDockerfile で統一する作業をしている
        """
        if row["Status"] == "R":
            renamefiles = row["filename"].split()
            before_name = renamefiles[0]
            after_name = renamefiles[1]
            """ ここでちょっとエラーがでる
             rename されたファイルは rename された時刻より前に存在しているはずなのに
             rename されたあとに add されているファイルが存在している。

             ここを正確に日付入れてやろうとしている理由は
             ファイルが削除されたあとに異なる同名ファイルが作成されていたら、
             新しいはずのファイルも同様に rename してしまうから。
            """
            added_df.loc[(added_df["filename"] == before_name) & (added_df["Date"] <= row["Date"]), "filename"] = after_name

            # 全ファイル変更
            # added_df.loc[ added_df["filename"] == renamefiles[0], "filename"] = renamefiles[1]


    # TODO: ここ正しい値にはなっていない（暫定で判断している）
    # 最初に追加された日付を追加している処理 (逆順にしないことで)
    for idx, row in added_df.iterrows():
        df.loc[df["LatestDockerfile"] == row["filename"], "FirstCommit Date"] = row["Date"]

    return df


def extractChangeInfo(gitlog):
    """ === 処理内容 ===
    git log から Add Rename Delete の情報（ファイル名・日付・ステータス）を取得
    """

    df = gitlog.copy(deep=True)
     # isDockerFile
    df = df.dropna(subset=['Dockerfile'])
    df = df[ df["Status"].apply(lambda st: ("A" == str(st)) or ("D" == str(st)) or ("R" == str(st)))]

    dateStatusDict = {
        "filename": [],
        "Date": [],
        "Status": []
    }
    
    # get Rename
    for index, row in df.iterrows():
        dateStatusDict["filename"].append(row["Dockerfile"])
        dateStatusDict["Date"].append(row["Date"])
        dateStatusDict["Status"].append(row["Status"])

    dateStatusDataFrame = pd.DataFrame.from_dict(dateStatusDict)

    return dateStatusDataFrame


def writeError(log):
    with open(PATH_OF_ERROR_ADDINFO, "a+") as f:
        f.seek(0)
        if not log in f.read():
            f.write(f"{log}\n")


if __name__ == "__main__":
    csvfiles = getTargetSatdCSV()

    for csvfile in tqdm(csvfiles):
        df, gitlog = getDataFrame(csvfile)

        length = len(df)
        if length == 0:
            errorlog = f"FileData Error: {csvfile} : CSVファイルの中身が無いです。"
            writeError(errorlog)
            continue

        df = addCommitDate(df, gitlog)
        df = addCommiter(df, gitlog)
        
        if len(df) != length:
            errorlog = f"[Error] Merged commit Date:  {csvfile} :最終的な出力結果数が変わっています。{length} -> {len(df)}"
            print(errorlog)
            writeError(errorlog)

        df = modifyInformation(df, gitlog)
        if len(df) != length:
            errorlog = f"[Error] add Information:  {csvfile} :最終的な出力結果数が変わっています。{length} -> {len(df)}"
            print(errorlog)
            writeError(errorlog)

        df = df.reindex(columns=['CommitID', 'Author', 'Dockerfile', 'LatestDockerfile', 'Comment', 'Date', 'FirstCommit Date', 'Deleted Date', 'RenameList', "logIndex"])
        df.to_csv(f'{PATH_OF_SATD_COMMENTFILE_ADDINFO}/{csvfile}')
