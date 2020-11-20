from setting import PATH_OF_ALLPROJECT_CSV, PATH_OF_GITCLONE, PATH_OF_ALLPROJECT_CSV_UPDATE
from tqdm import tqdm
import os
import re
import pandas as pd
import numpy as np
from datetime import datetime
import subprocess


def judge_comment_change(df):
    tmp = df[df["コメント追加からコメント削除までの日数"].apply(lambda delete: False if delete in ["削除されていません", "ファイル削除"] else True)]
    target_idx = tmp.index.tolist()

    for idx in target_idx:
        target = df.loc[idx, :]
        

        #  === 条件
        # 1. 同一プロジェクト
        # 2. 最新Dockerfileが一致
        # 3. コメントの追加ID と 削除IDが一致
        # 4. Fileのコミット日が同じ

        # 使用方法は無視する
        if "# Usage:" in target["Comment"]:
            df.drop(index=idx, inplace=True)
            continue
    
        # エラーが発生したので処理
        # 内容：同じ内容のコミットが２回行われており、それぞれ異なるコミットIDだった。
        ## 上で弾いているので重複している処理
        if target["Deleted CommitID"] == "6863c4fe21e39c125f3a429e001c724bc37341b0":
            mask = (df["project"]==target["project"]) & (df["LatestDockerfile"]==target["LatestDockerfile"]) & (df["CommitID"]=="5e4f4153669d1dbd07f53a9267d5d8677c107b51") & (df["(File) FirstCommit"]==target["(File) FirstCommit"])
        elif target["Deleted CommitID"] == "6d420407caf533f89b60d78c54e0ddc2d307e942":
            mask = (df["project"]==target["project"]) & (df["LatestDockerfile"]==target["LatestDockerfile"]) & (df["CommitID"]=="31638ab2ad2a5380d447780f05f7aa078c9421f5") & (df["(File) FirstCommit"]==target["(File) FirstCommit"])
        else:
            mask = (df["project"]==target["project"]) & (df["LatestDockerfile"]==target["LatestDockerfile"]) & (df["CommitID"]==target["Deleted CommitID"]) & (df["(File) FirstCommit"]==target["(File) FirstCommit"])



        masked_df = df[mask]

        if len(masked_df) == 0:
            continue
        
        print('\n'*100)
        print(target)
        print(f"{idx}/{target_idx[-1]}")
        print("----- 元のコメント -----")
        print(target["Comment"])


        for i, t in masked_df.iterrows():
            print(f"\n--- index {i}/{len(masked_df)} ----------------- ")
            print(t["Comment"])


        while True:
            try:
                if len(masked_df) == 1:
                    judge = input("\n-----------> the same comment?: (0K: Enter , No: 0)   ")
                    if judge == 0:
                        break
                    else: # index -> i
                        selected = masked_df.loc[i, :]
                        df.loc[i, :] = combine_comment(target, selected)
                        df.drop(index=idx, inplace=True)
                else:
                    judge = int(input("\n===========> the same comment?: (input Index , No: 0)   "))

                    if judge == 0:
                        break
                    else:
                        selected = masked_df.loc[judge, :]
                        df.loc[judge, :] = combine_comment(target, selected)
                        df.drop(index=idx, inplace=True)
                break
            except Exception as e:
                print("例外:", e.args)
        

    df = df.sort_values('Comment')
    df.to_csv(f'{PATH_OF_ALLPROJECT_CSV_UPDATE}/result.csv')



"""
cols = [
    'project',
    'gitPath',
    'CommitID',
    'Deleted CommitID',
    'Dockerfile',
    'LatestDockerfile',
    'Comment',
    'CommitDate',
    'DeleteComment',
    '(File) FirstCommit',
    '(File) Deleted',
    'firstCommitからコメント追加までの日数',
    'コメント追加からコメント削除までの日数',
    '追加時ファイル',
    '削除時ファイル'
    ]
"""

def combine_comment(origin, after):

    after['CommitDate'] = origin['CommitDate']
    after["Author"] = origin["Author"]

    after['firstCommitからコメント追加までの日数'] = (datetime.strptime(after['CommitDate'], '%Y/%m/%d %H:%M') - datetime.strptime(after['(File) FirstCommit'], '%Y/%m/%d %H:%M'))

    if after["コメント追加からコメント削除までの日数"] in ["削除されていません", "ファイル削除"]:
        pass
    else:
        after['コメント追加からコメント削除までの日数'] = datetime.strptime(after['DeleteComment'], '%Y/%m/%d %H:%M') - datetime.strptime(after['CommitDate'], '%Y/%m/%d %H:%M')

    if str(after["(origin)SATD"]) == "nan":
        after["(origin)SATD"] = origin["Comment"]
        after["(origin)追加時ファイル"] = origin["追加時ファイル"]

    return after




if __name__ == "__main__":
    df = pd.read_csv(f"{PATH_OF_ALLPROJECT_CSV}/result.csv", index_col=0)
    df = df.sort_values('CommitDate')

    df["(origin)追加時ファイル"] = np.nan
    df["(origin)SATD"] = np.nan
    judge_comment_change(df)
