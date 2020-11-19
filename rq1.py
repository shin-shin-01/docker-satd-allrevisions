from setting import PATH_OF_ALLPROJECT_CSV_UPDATE
import pandas as pd
from tqdm import tqdm
import statistics
import math

# RQ1（仮） どれくらいのSATDが除去されているのか？
"""
ファイルごと削除されたSATDは ここでは無視している。
"""

if __name__ == "__main__":
    result_df = pd.read_csv(f'{PATH_OF_ALLPROJECT_CSV_UPDATE}/result.csv', index_col=0)
    not_deleted_df = pd.read_csv(f'a-extractComment/SATDnotDeletedWithInfo.csv', index_col=0)
    deleted_df = pd.read_csv(f'a-extractComment/SATDDeletedWithInfo.csv', index_col=0)
    file_deleted_df = pd.read_csv(f'a-extractComment/SATDfileDeletedWithInfo.csv', index_col=0)

    all_uniqueSATD = result_df["Comment"].unique()
    print(f"全てのユニークSATD \n →  {len(all_uniqueSATD)}")

    tmp = result_df[result_df["コメント追加からコメント削除までの日数"].apply(lambda delete: False if delete in ["削除されていません", "ファイル削除"] else True)]
    deleted_uniqueSATD = tmp["Comment"].unique()
    print(f"削除されたユニークSATD (コメント削除) \n →  {len(deleted_uniqueSATD)}")

    print(f"削除されたユニークSATD率 \n →  {len(deleted_uniqueSATD)/len(all_uniqueSATD) *100}")
    # print(f"削除されたSATD率 \n →  {len(deleted_df)/(len(deleted_df)+len(not_deleted_df)) *100}")

    print('-'*10)

    """
    各プロジェクトにおける 削除されたSATDの割合（全体 = 削除されたSATD + 削除されていないSATD）
    """
    percentages = []
    all_projects = result_df["project"].unique()
    for project in tqdm(all_projects):
        # 各プロジェクトごとの 削除されていないSATD(ユニーク) の件数
        unique_not_deleted_satd = len( not_deleted_df[ not_deleted_df["project"] == project ]["Comment"].unique() )
        # 各プロジェクトごとの 削除されたSATD(ユニーク) の件数
        unique_deleted_satd = len( deleted_df[ deleted_df["project"] == project ]["Comment"].unique() )
        # 各プロジェクトごとの ファイルごと削除されたSATD(ユニーク) の件数
        unique_file_deleted_satd = len( file_deleted_df[ file_deleted_df["project"] == project ]["Comment"].unique() )

        all_unique_satd = unique_not_deleted_satd + unique_deleted_satd + unique_file_deleted_satd

        if all_unique_satd == 0:
            continue

        percentage = ( unique_deleted_satd / all_unique_satd ) * 100

        percentages.append(percentage)
    
    percentages_mean = statistics.mean(percentages)
    percentages_median = statistics.median(percentages)

    print(f'mean(ユニーク): {percentages_mean}')
    print(f'median(ユニーク): {percentages_median}')

    percentages = []
    all_projects = result_df["project"].unique()
    for project in tqdm(all_projects):
        # 各プロジェクトごとの 削除されていないSATD の件数
        unique_not_deleted_satd = len( not_deleted_df[ not_deleted_df["project"] == project ]["Comment"] )
        # 各プロジェクトごとの 削除されたSATD の件数
        unique_deleted_satd = len( deleted_df[ deleted_df["project"] == project ]["Comment"] )
        # 各プロジェクトごとの ファイルごと削除されたSATD の件数
        unique_file_deleted_satd = len( file_deleted_df[ file_deleted_df["project"] == project ]["Comment"] )

        all_unique_satd = unique_not_deleted_satd + unique_deleted_satd + unique_file_deleted_satd

        if all_unique_satd == 0:
            continue

        percentage = ( unique_deleted_satd / all_unique_satd ) * 100

        percentages.append(percentage)
    
    percentages_mean = statistics.mean(percentages)
    percentages_median = statistics.median(percentages)

    print(f'mean: {percentages_mean}')
    print(f'median: {percentages_median}')
