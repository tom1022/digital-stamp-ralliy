# デジタルスタンプラリー（digital-stamp-ralliy）

## 概要

Flaskを用いたデジタルスタンプラリーWebアプリケーションのバックエンドAPI
ユーザーは画像アップロードによるスタンプ獲得、スタンプコンプリート、管理者による景品付与などの機能を利用できます。

---

## 主な機能

- ユーザー登録・認証（UUIDによる）
- 画像アップロードによるスタンプ獲得
- スタンプの進捗確認・コンプリート判定
- 管理者用ダッシュボード・ログイン・景品付与

---

## ディレクトリ構成

```
app/
├── blueprints/         # Flask Blueprint（main, admin）
├── data/               # ランドマーク情報・モデルデータ
├── models/             # DBモデル
├── utils/              # 画像認識等のユーティリティ
├── test_api.py         # APIテストスクリプト
├── extensions.py       # DB等の拡張
├── requirements.txt    # Python依存パッケージ
├── .devcontainer/      # DevContainer設定
├── .env                # 環境変数
└── app.py              # アプリケーションエントリ
```

---

## セットアップ方法


`docker-compose.yml` の `app` および `nginx` サービス（productionプロファイル）を利用します。

### 必要要件

- Docker
- Docker Compose

### インストール

```sh
docker compose --profile production up -d --build
```

### .envファイルの作成

`/app/.env` を参考に、DB接続情報などを設定してください。

---

## 主なAPIエンドポイント

- `POST /` : ユーザー新規作成・取得
- `POST /upload` : 画像アップロード＆スタンプ判定
- `GET /final` : スタンプコンプリート判定
- `POST /admin/login` : 管理者ログイン
- `GET /admin/dashboard` : 管理ダッシュボード
- `POST /admin/prize` : 景品付与

---

## その他

- 画像認識モデル（YOLO等）は `/app/data/best.pt` に格納
- ランドマーク情報は `/app/data/landmarks.json` で管理

---

## ライセンス

MIT License
