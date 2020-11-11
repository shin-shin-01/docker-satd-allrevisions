from setting import PATH_OF_ALLPROJECT_CSV_UPDATE
import pandas as pd

# RQ1（仮） どれくらいのSATDが除去されているのか？

if __name__ == "__main__":
    df = pd.read_csv(f'{PATH_OF_ALLPROJECT_CSV_UPDATE}/result.csv', index_col=0)

    all_uniqueSATD = df["Comment"].unique()
    print(f"全てのユニークSATD \n →  {len(all_uniqueSATD)}")


    tmp = df[df["コメント追加からコメント削除までの日数"].apply(lambda delete: False if delete in ["削除されていません", "ファイル削除"] else True)]
    deleted_uniqueSATD = tmp["Comment"].unique()
    print(f"削除されたユニークSATD (コメント削除) \n →  {len(deleted_uniqueSATD)}")
