# インターンシップ LangChain 解説資料

LangChain を使った AI チャットアプリの解説資料です。  
Streamlit で UI を構築し、Amazon Bedrock 上の Claude を LLM として利用します。

## 使用技術

- **Python** — プログラミング言語
- **Streamlit** — Web UI フレームワーク
- **LangChain** — LLM を扱うためのフレームワーク
- **Amazon Bedrock** — AWS の生成 AI サービス（Claude を利用）
- **boto3** — AWS の Python SDK

## 事前準備

### 1. Python のバージョン確認

**Mac / Linux**
```bash
python3 --version
```

**Windows**
```bash
python --version
```

`Python 3.14.5` と表示されれば OK です。

### 2. ファイルの解凍

配布された ZIP ファイルを解凍してください。

### 3. ライブラリのインストール

解凍したフォルダに移動し、以下を実行してください。

**Mac / Linux**
```bash
pip3 install -r requirements.txt
```

**Windows**
```bash
pip install -r requirements.txt
```

## 実行方法

**Mac / Linux**
```bash
python3 -m streamlit run main.py --server.port 8501
```

**Windows**
```bash
python -m streamlit run main.py --server.port 8501
```

ブラウザで以下の URL を開いてください。

http://localhost:8501

真っ白な画面が表示されれば準備完了です。
