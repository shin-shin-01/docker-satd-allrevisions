## TODO
* 全リビジョンで同一コメント・同一ファイルをまとめる処理を行う。
* コメントがいつ削除されたかを追う作業を行う。
* 名称変更データを適用する。
* 日付データを適用する。
* 削除された日付を記載する。

## 1-git_clone.py
対象リポジトリをクローン
dockerhub 人気250イメージの github 260リポジトリ を元にクローン

対象: PATH_OF_GITREF
出力: PATH_OF_OUTPUT_GITCLONE
エラー内容: PATH_OF_ERROR_GITCLONE

## 2-git_log_extractDockerfile.py
```
git log --name-status
```
上記を実行し、コミット履歴を取得する。
Dockerfileが含まれる場合、Status とともに情報を取得する。

> コミットID・日付・Dockerfile・Status

`Status: A(dd) D(elete) M(odify) R(ename)`

## 3-getPastFile.py
2のファイルを元に過去のRevisionのDockerfileをテキスト形式で保存。
> Delete, Rename は無視。

## 4-getComments.py
3で取得したファイルを元にコメントを抽出し、
各リポジトリごとにCSVファイルで情報を保存。

> コミットID・Dockerfile・Comment
上記状態で、生のコメントを抽出しただけであり、重複を考慮していないので注意
