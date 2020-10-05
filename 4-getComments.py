from setting import PATH_OF_PASTFILE, PATH_OF_COMMENTFILE
from tqdm import tqdm
import subprocess
import os
import re
import pandas as pd


def getTargetRepository():
    repositories = os.listdir(PATH_OF_PASTFILE)
    targetRepositories = []
    for repository in repositories:
        if f'{repository}.csv' in os.listdir(PATH_OF_COMMENTFILE):
            print("Already Exists!")
            continue
        if repository == ".DS_Store":
            print("Directory Error: .DS_Store")
            continue

        targetRepositories.append(repository)
    
    return targetRepositories

def commentDetect(txt):
    # テストコメント
    # txt = "# コメントですよ\n python app.py #コメント \n　python # 1コメント目\n # ２連続\n /*\n skommento\n*/\n ですよ"

    HashCommnets = re.findall(r'(([ \t\f\r]*\#[^\n]*\n*)+)', txt)
    HashCommnets = list(map(lambda tup: tup[0], HashCommnets))
    AstaCommnets = re.findall(r'(/\*[^/]*\*/)', txt)
    
    HashCommnets.extend(AstaCommnets)

    Comments = HashCommnets
    return Comments

def saveComentToResult(txtfile, result, comments):
    revision = txtfile[:40]
    filename = txtfile[40:-4].replace('___', '/')

    for comment in comments:
        result["CommitID"].append(revision)
        result["Dockerfile"].append(filename)
        result["Comment"].append(comment)

    return result


## 後できれいにまとめる予定
def main(repository):
    txtfiles = os.listdir(f'{PATH_OF_PASTFILE}/{repository}')

    result = { "CommitID":[], "Dockerfile":[], "Comment":[] }

    # 過去の全ての　Docker-file でfor文回してます
    for txtfile in txtfiles:
        if txtfile == ".DS_Store":
            print(f"File Error: .DS_Store")
            continue

        with open(f'{PATH_OF_PASTFILE}/{repository}/{txtfile}', 'r') as f:
            comments = commentDetect(f.read())
            
            saveComentToResult(txtfile, result, comments)

    result = pd.DataFrame.from_dict(result)
    result.to_csv(f'{PATH_OF_COMMENTFILE}/{repository}.csv')



if __name__ == "__main__":
    repositories = getTargetRepository()

    for repository in tqdm(repositories):
        main(repository)


