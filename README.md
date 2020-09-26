## TODO
* コメントのマージ
→ SATDの追加や削除についての分析なのでしなくていいかも..
* 全体の検出件数をわかりやすく計算する
* Renameについて

## 考えなくてはいけない点
* ファイル名変更にて、Dockerfile などの名前が複数回定義されたときにエラーが発生する
```
例）
→ 202001にDockerfileを作成し, 202002に/ver2/Dockerfile に名前を変更
→ 202007にDockerfileを作成し, 202008に/ver3/Dockerfile に名前を変更
→ Dockerfileと最初に定義されたものは全て /ver3/Dockerfile に置き換わる
```

* 削除された日付や追加された日付が複数存在する時がある
→ 同じファイルが何度も追加削除されたとき

* <s>ファイル削除とコメント削除の違いをわかりやすくしないと。</s>

## 0-analysisFunc.py
下記で出力したデータに対して分析（細かい数字の計算）を行うための関数

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

> コミットID・Dockerfiles・Comments
上記状態で、生のコメントを抽出しただけであり、重複を考慮していないので注意

## 5-detecctSATD.py
4で取得したファイルとキーワード64個をもとにSATDの検出・抽出作業。
> コミットID・Dockerfiles・Comments・isSATD

#### us-ascii を変換したつもりであるが、ファイルによってはエンコーディングエラーがあり検出できていないかも...？？

## 6-addDateRenameInfo.py
5で取得したファイルに以下の情報を追加
> コミットID・Dockerfiles・LatestDockerfile・Comments・Date・FirstCommit Date・Deleted Date・isSATD

1. LatestDockerfile Name: 最新バージョンのファイル名
2. Date: コミットIDに基づいたコミット日時
3. FirstCommit Date: 最新ファイル名に置き換えたもので、そのファイルがいつ追加(A)されたかの日時
4. Delete Date: 最新ファイル名であると仮定し、そのファイルがいつ削除(D)されたかの日時　（今の存在するファイル名の中でこの名前が使用されているかも）

#### 1.3.4 に課題あり。

## 7-fixSameSATD.py
6で取得したファイルに対して以下の処理を実行
以下の流れで同一ファイルの重複コメントの削除、コメント追加日・削除日情報を取得する。

* 同じDockerfile(LatestDokcerfile)ごとに分ける
* さらに同じコメントごとに分ける
* コメントの中で一番最初のコミットの情報のみ取得する。
* コメントの中で一番最後のコミットの日付を取得する。
* 同じDockerfileごとのデータに戻り、取得した日付よりあとの日付でコミットされたデータを取得
　その中で一番古い日付を「上記対象コメントが削除された日付」として保存。存在しない場合はファイルの削除日を保存する。

## 8-createAllProjectCSV.py
7で取得したファイルを１つにまとめて"最強データ"を作成するためのCSVファイルを作成。
データをまとめる際に、分析に必要な結果を追加してます。

> project・gitPath・CommitID・Dockerfiles・LatestDockerfile・Comments・CommitDate・DeleteComment・(File) FirstCommit・(File) Deleted・isSATD・firstCommitからコメント追加までの日数・コメント追加からコメント削除までの日数
