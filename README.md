# OFRAA（管理者機能：ログイン・ログアウト・スポット登録）

Flask + JavaScript で作った、OFRAA の最初の3機能です。

## 動かし方（Windows）
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py        # データベースを作る（初回だけ。再実行するとデータが消えます）
python app.py            # http://127.0.0.1:5000 を開く
```
ログイン：ID `admin` ／ パスワード `admin1234`（開発用。本番では必ず変更する）

## テスト
```
python -m pytest -q
```

## フォルダ構成（クラス図に合わせています）
| フォルダ・ファイル | 役割 | クラス図 |
|---|---|---|
| actions/ | 画面ごとの処理（Flask Blueprint） | Action |
| templates/ , static/ | 画面（HTML・CSS・JavaScript） | JSP |
| dao/ | DBの読み書き | DAO |
| beans/ | データを持つクラス | Bean |
| db.py , schema.sql , init_db.py | DB接続・テーブル定義・初期データ | DBManager |
| utils/ | ログイン確認、写真のチェックと保存 | 共通 |

## 画面と機能
| 画面ID | 画面 | URL |
|---|---|---|
| LOGI001 | ログイン | /login |
| MMNU001 | メインメニュー | /menu |
| LOGO001 | ログアウト（確認画面） | /logout |
| FCSM001 | スポット一覧（編集・削除は未実装） | /spots/ |
| FCSR001 | スポット登録 | /spots/register |
| FCSR002 | スポット登録完了 | /spots/register/done/<id> |
| ERR001 | エラー画面 | （エラー時に自動表示） |

## 注意点
- フロアマップ登録機能ができるまでは、仮の地図（static/img/no_map.svg）を表示します。
- クラス図の `AdminDAO.findByLoginIdAndPassword` は、パスワードをハッシュで保存するため
  `find_by_login_id`（IDで探して、パスワードは Bean 側で照合）に変えています。
- 本番では環境変数 `OFRAA_SECRET_KEY` を必ず設定してください。
