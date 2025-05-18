# Docker Server

## 1. プロジェクト概要

- 目的：Flask + Docker + MySQL + HTTPS の構成を用いて、フルスタック Web アプリケーション開発と運用を体系的に学ぶ
- 対象：初中級エンジニア、教育演習、チーム内学習プロジェクト
- 特徴：
  - フロントとバックの基本的な連携（HTML フォーム → DB 保存 → 表示）
  - HTTPS 対応と Nginx による本番環境展開も視野に
  - Docker による環境分離と再現性の高い構成

## 2. 前提条件・環境構築（STEP 0）

### 必須ツールと導入方法

| ツール         | 推奨バージョン | 説明                       | リンク                                                 |
| -------------- | -------------- | -------------------------- | ------------------------------------------------------ |
| Python         | 3.11.x         | Flask アプリのローカル起動 | [公式](https://www.python.org/downloads/)              |
| Docker Desktop | 最新           | コンテナ環境の提供         | [公式](https://www.docker.com/products/docker-desktop) |
| Docker Compose | v2 系          | マルチサービス起動管理     | 同上                                                   |
| Git            | 任意           | バージョン管理             | [公式](https://git-scm.com/)                           |

### セットアップ手順（2 パターン）

#### Python ローカル環境で起動

★ macOS / Linux の場合

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python wsgi.py
```

★ Windows（コマンドプロンプト）の場合

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python wsgi.py

```

★ Windows（PowerShell）の場合

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python wsgi.py
```

#### Docker で起動（推奨）

```bash
docker-compose -f docker-compose.dev.yml up --build
```

## 3. 構成図とディレクトリ構成（具体版）

### サービス構成図（例）

```
┌────────┐       ┌────────────┐        ┌─────────────────┐
│ Browser│──────▶│ Nginx（任意）│──────▶│ Flask（Gunicorn）│
└────────┘       └────────────┘        └───────┬─────────┘
                                               │
                                     ┌─────────▼──────────┐
                                     │     MySQL（DB）     │
                                     └────────────────────┘
```

### ディレクトリツリー例（簡略）

```
.
├── app.py
├── wsgi.py
├── requirements.txt
├── Dockerfile
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── templates/
│   └── index.html
├── init/
│   └── init.sql
├── nginx/
│   └── nginx.conf
├── cert.pem
├── key.pem
```

### 各ディレクトリ・ファイルの役割

| パス                      | 内容と役割                           |
| ------------------------- | ------------------------------------ |
| `app.py`                  | Flask のルーティング、DB 操作のコア  |
| `wsgi.py`                 | 起動エントリーポイント（HTTPS 対応） |
| `templates/index.html`    | Jinja2 テンプレートで表示処理        |
| `requirements.txt`        | 必要ライブラリ一覧                   |
| `Dockerfile`              | Flask アプリのコンテナ定義           |
| `docker-compose.dev.yml`  | 開発用構成（Flask + MySQL）          |
| `docker-compose.prod.yml` | 本番用構成（Nginx + Gunicorn）       |
| `init/init.sql`           | DB 初期化スクリプト（テーブル定義）  |
| `nginx/nginx.conf`        | 本番用の SSL リバースプロキシ設定    |
| `cert.pem` / `key.pem`    | 自己署名証明書（HTTPS 用）           |

## 4. ステップ別構成と演習問題付き解説

### STEP 1: Flask アプリのコアロジック

【目的】
Flask のルーティングと MySQL との連携を通して、「表示」「登録」「削除」の基本的な Web 処理の流れを理解する。

【構成要素】
▶ `app.py`

- Flask アプリ本体
- `/` で DB からメッセージを取得
- `/submit` でフォームから文字列を登録
- `/delete_last` で最新レコードを削除

▶ `templates/index.html`

- `app.py` から渡された `messages` をループ表示
- HTML5 フォームで POST 発送
- JavaScript `confirm()` で削除前に確認ダイアログ

【ソースコード解説】

★ 表示

```python
@app.route('/')
def index():
    messages = get_messages()
    return render_template("index.html", messages=messages)
```

- `get_messages()` で DB からデータ取得
- Jinja2 で `{{ msg }}` を HTML 表示

★ 登録

```python
@app.route('/submit', methods=['POST'])
def submit():
    text = request.form['text']
    insert_message(text)
    return redirect('/')
```

- `request.form['text']`で input の値を取得
- SQL インジェクション対策のため `%s` プレースホルダ使用

★ 削除

```python
@app.route('/delete_last', methods=['POST'])
def delete_last():
    delete_last_message()
    return redirect('/')
```

- `DELETE` ではなく `POST` を利用してるのは HTML フォームでは GET/POST のみサポートされるため
- `delete_last_message()` 内で id DESC の LIMIT 1 を削除

【表示テンプレート index.html】

```html
<h1>
  {% for msg in messages %} {{ msg }}<br />
  {% endfor %}
</h1>
```

- Jinja2 のループ構文
- Flask から渡された `messages` を HTML 上に表示

### STEP 2: WSGI 起動ロジック & HTTPS

▶ `wsgi.py`

```python
from app import app

if __name__ == '__main__':
    app.run()
```

- Flask アプリの起動ファイル
- `__name__ == '__main__'`の条件により、コマンド立ち上げとしての実行のみを許可
- 開発時の試験起動に便利
- 本番環境では Gunicorn などから `import` されることを想定

【演習問題】
ChatGPT へ投げられる形式
△ 基本編
Flask の `wsgi.py` を利用する利点は何ですか？
`__name__ == '__main__'`の意味を教えてください。

△ 実践編
Flask の SSL 実行時に `ssl_context` に指定する要素は何ですか？
Flask の `app.run()`の `host` や `port` はどのように指定すると良いですか？

### STEP 3: HTTPS 対応と WSGI 起動

【目的】
Flask アプリを WSGI 経由で起動する際に、HTTPS による通信を実現する。このパートでは:

- Flask の WSGI 実装を使った起動フロー
- 自己署名証明書 (SSL/TLS) を用いた HTTPS 通信を理解する

【ソースコード】
▶ `wsgi.py`

```python
from app import app

if __name__ == '__main__':
    app.run()
```

- Flask アプリを `__main__` で起動
- 本来、WSGI サーバは Gunicorn などが使われるが、開発期は `app.run()` で単独起動も可

【HTTPS 化の説明】
Flask は `app.run()` の引数 `ssl_context` を指定することで HTTPS 対応可能
★ HTTPS 起動例

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, ssl_context=('cert.pem', 'key.pem'))
```

- `cert.pem` = 証明書 (Certificate)
- `key.pem` = 秘密鍵 (Private Key)

【自己署名証明書の作成手順】

1. 空のフォルダで作業
2. 以下の OpenSSL コマンドを実行

★ macOS / Linux（ターミナル）の場合

```bash
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes \
  -subj "/CN=localhost"
```

- `/CN=localhost `はテスト用の CommonName
- `.pem` ファイルを Flask や Nginx で利用

★ Windows（Git Bash / WSL 環境）の場合

```bash
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes \
  -subj "/CN=localhost"
```

- Git Bash または Windows Subsystem for Linux (WSL) を使用してください
- PowerShell や CMD では正常に動作しないことがあります

★ Windows（PowerShell / CMD 環境）※代替案
Windows 環境では OpenSSL が標準搭載されていないため、以下の方法でインストールしてください：

・OpenSSL for Windows を導入
https://slproweb.com/products/Win32OpenSSL.html

インストール後、cmd.exe または PowerShell にて openssl.exe を実行可能にします。

【推奨方式】

1. 開発期:
   - `app.run()` で HTTPS 確認 OK
2. 本番環境:
   - Gunicorn + Nginx の組み合わせでスケール

【演習問題】
ChatGPT へ投げられる形式
△ WSGI 関連
`wsgi.py` で `__name__ == '__main__'` で誰が起動されるか説明してください
Flask の `app.run()`の代わりに本番環境では何を使うべきですか？
△ HTTPS / 証明書
Flask で HTTPS を使用するためには、`app.run` にどのような引数を指定しますか？
自己署名証明書を使用する場合の利点と注意点を教えてください
`cert.pem` と `key.pem` は何を代表していますか？

### STEP 4: 依存ライブラリ管理 (`requirements.txt`)

【目的】
Flask アプリに必要なライブラリを `requirements.txt` に明示し、プロジェクトの現状を再現可能なようにする。

【ファイル内容】
▶ `requirements.txt`

```text
flask
mysql-connector-python
gunicorn
```

【各ライブラリの解説】
| ライブラリ | 用途 |
| ------------------------- | ----------------------- |
| `flask` | Web アプリケーションフレームワーク (コア) |
| `mysql-connector-python` | MySQL と Python を連携するためのドライバー |
| `gunicorn` | WSGI サーバー (Flask を本番環境で動作させる) |

【インストール手順】
★ バージョン指定なし (最新)

```bash
pip install -r requirements.txt
```

★ バージョンを固定したい場合

```text
flask==2.3.3
mysql-connector-python==8.3.0
gunicorn==21.2.0
```

- 確定したバージョンを持ち込むには `pip freeze > requirements.txt`

【使用シーン】

- Dockerfile の RUN pip install -r requirements.txt
- Python ローカル環境で venv 使用時

【演習問題】
ChatGPT へ投げられる形式
`requirements.txt` は何のために利用するファイルですか？
`pip freeze` で出力される一覧との違いは何ですか？
Flask を本番環境で動かす場合、`gunicorn` を入れる利点は何ですか？
`mysql-connector-python` はどのようなコードで使用されますか？

### STEP 5: Docker による環境構築

【目的】
Flask と MySQL を含むマルチサービスを Docker で構築し、環境構築の再現性と簡易性を高める。

【ファイル構成】
▶ `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# CMD は docker-compose 側で指定
```

- 軽量イメージ `python:3.11-slim` を使用
- `/app` をコンテナ内ルートパスとして指定
- `requirements.txt` を先に COPY してキャッシュ利用を最適化

▶ docker-compose.dev.yml

```YAML
version: "3.x"  # 最新のversionを確認。今回は3.8で起動
services:
  app:
    build: .
    ports:
      - "5001:5000"
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development
      - MYSQL_HOST=db
      - MYSQL_USER=root
      - MYSQL_PASSWORD=example
      - MYSQL_DATABASE=appdb
    command: flask run --host=0.0.0.0 --port=5000 --cert=cert.pem --key=key.pem --debug
    depends_on:
      - db

  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: example
    volumes:
      - dbdata:/var/lib/mysql
      - ./init:/docker-entrypoint-initdb.d

volumes:
  dbdata:
```

- `app` サービス: Flask アプリを起動
- `db` サービス: MySQL8 イメージを使用
- `depends_on`: DB が先に起動
- `volumes`:
  - `.:/app`: ホスト側のコードをコンテナ側にミラー
  - `./init`: 初期 SQL を MySQL コンテナにマウント

【開発コマンド】

```bash
docker-compose -f docker-compose.dev.yml up --build
```

- `--build`: Dockerfile から再構築
- Flask は `5001` 番ポート (ホスト) から接続

【ポイント】

- `command`:` flask run` は HTTPS 依存
- `volumes` は 開発時に便利 (ホットリロード)
- `depends_on` は DB 起動後に app を起動

【演習問題】
ChatGPT へ投げられる形式
`Dockerfile` で `COPY . .` を実行するとどのような動作をしますか？
Docker で「ボリューム」を利用する目的を教えてください
`docker-compose.yml` の `depends_on` は DB 起動を完全に待つ保証になりますか？
`compose` で command: `flask run` ... を設定する意味を教えてください

### STEP 6: MySQL 構造定義と初期化

【目的】
MySQL の初期起動時に、Docker コンテナ内で DB 構造を定義し、データを自動挿入する。

【ソース文一覧】
▶ `init/init.sql`

```SQL
CREATE DATABASE IF NOT EXISTS appdb;

USE appdb;

CREATE TABLE messages(
  id INT AUTO_INCREMENT PRIMARY KEY,
  text VARCHAR(255) NOT NULL
);

INSERT INTO messages (text) VALUES ('Hello World');
```

- データベース `appdb` がなければ作成
- `messages` テーブル
  - `id`: 固有の ID (AUTO_INCREMENT)
  - `text`: メッセージ本文
- 初期レコード: `Hello World`

【動作メカニズム】

- MySQL コンテナは `docker-compose.dev.yml` の中で:

★ macOS / Linux の場合

```YAML
volumes:
	- ./init:/docker-entrypoint-initdb.d
```

★ Windows（Git Bash / WSL / Docker Desktop 環境）の場合

```YAML
volumes:
  - ./init:/docker-entrypoint-initdb.d
```

- 基本的に macOS/Linux と同じ形式で動作します。
- ただし環境によっては `./` の解釈が不安定な場合があります。

★★ 安定性を高める方法（代替案）：もし windows でうまく動かない場合

```YAML
volumes:
  - ${PWD}/init:/docker-entrypoint-initdb.d
```

- `${PWD}` はカレントディレクトリの絶対パスに展開されるため、Windows 環境でもトラブルが少ないです。
- `env` ファイルで `PWD` を明示的に定義しても OK です。

★ Windows（PowerShell / CMD の場合の注意）

- PWD は展開されないため、以下のように絶対パスを明記する必要があります

```YAML
volumes:
  - C:/Users/yourname/project/init:/docker-entrypoint-initdb.d
```

- パスの区切りは必ずスラッシュ（/）で記述します。
- バックスラッシュ（\）は YAML 構文でエラーになります。

★★ 共通の挙動として

- 初回のコンテナ起動時に `/docker-entrypoint-initdb.d` 内の SQL が実行される
- 一度ボリュームに書き込まれると再実行されない

【よくある誤解】

- `init.sql` を修正しても、ボリューム (dbdata) が残っている場合、SQL は再実行されない

▶ 再初期化する方法

```bash
docker-compose down -v
```

- -v でボリュームも削除される
- 次回、`init.sql` の内容が有効化

【演習問題】
ChatGPT へ投げられる形式
`init.sql` は Docker のどの時点で実行されますか？
Docker で `init.sql` を再実行させるにはどうすればよいですか？
`AUTO_INCREMENT` の意味を説明してください
`CREATE DATABASE IF NOT EXISTS` を使う理由を教えてください

### STEP 7 (Optional): Nginx と本番構成 (SSL 終端処理)

【目的】
HTTPS の終端処理をアプリ側ではなく Nginx に委託する構成を学び、Flask + Gunicorn + Nginx の本番配置を理解する。

【構成概要】
▶ `docker-compose.prod.yml` (3 サービス)

- app: Gunicorn で Flask を起動 (ポート 8000)
- db: MySQL 8 + 初期 SQL
- nginx: HTTPS 終端処理とリバースプロキシ

▶ `nginx/nginx.conf`

```text
events {}

http {
  server {
    listen 80;
    return 301 https://$host$request_uri;
  }

  server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    location / {
      proxy_pass http://app:8000;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
  }
}
```

- ポート 80 は 443 にリダイレクト (301)
- `/etc/ssl/` は nginx コンテナ内の証明書パス
- 内部で `app:8000` (Gunicorn) にプロキシ配置
- `proxy_set_header` は Flask 側に本来のホスト/クライアント情報を渡す

【本番用 docker-compose.prod.yml】

```YAML
services:
  app:
    build: .
    expose:
      - "8000"
    environment:
      - MYSQL_HOST=db
      - MYSQL_USER=root
      - MYSQL_PASSWORD=example
      - MYSQL_DATABASE=appdb
    command: gunicorn --bind 0.0.0.0:8000 wsgi:app
    depends_on:
      - db

  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: example
    volumes:
      - dbdata:/var/lib/mysql
      - ./init:/docker-entrypoint-initdb.d

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./cert.pem:/etc/ssl/key.pem:ro
    depends_on:
      - app

volumes:
  dbdata:
```

【起動コマンド】

```bash
docker-compose -f docker-compose.prod.yml up --build
```

- Nginx: 80/443 公開
- app は `expose` のみ (Nginx のみから接続可)

【注意点】

- Nginx で HTTPS を実現
- Gunicorn は HTTP 8000 で待ち受け
- app のポートは `expose` で、外部には見せない

【演習問題】
ChatGPT へ投げられる形式
Nginx は HTTPS で受けたリクエストを Flask 側にどのように渡しますか？
`proxy_pass` や `proxy_set_header` の意味を教えてください
Flask を Gunicorn + Nginx で動かす利点は何ですか？
443 番ポートにリダイレクトするとき、HTTP ステータスコードになぜ 301 を使うのが良いのでしょう？

::: info
デバッグとトラブルシューティング
:::

- よくあるエラーと対処（DB 未接続、ポート競合）
- コンテナ・ログの確認コマンド一覧

::: info
発展・拡張ステップ（Next Step）
:::

- REST API 化、SPA 接続、CSRF 対策、CI/CD 導入案など

::: info
ライセンスとクレジット
:::

- MIT or チーム用ライセンス
- 作成者・履歴など

## LICENSE

This project is licensed under the [MIT License](./LICENSE).
