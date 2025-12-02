# Oracle Linux 8をベースイメージとして使用
FROM oraclelinux:8

# Python 3.11、pip、Oracle Instant Client、ビルドツール、tzdata をインストール
RUN yum -y update && \
    yum -y install oracle-epel-release-el8 && \
    yum -y install python3.11 python3.11-pip python3.11-devel gcc tzdata && \
    yum -y install oracle-instantclient-release-el8 && \
    yum -y install oracle-instantclient-basic && \
    rm -rf /var/cache/yum

# python3.11 をデフォルトの python に設定し、pip のシンボリックリンクを作成
RUN alternatives --set python /usr/bin/python3.11 && \
    ln -s /usr/bin/pip3.11 /usr/bin/pip

# タイムゾーンを JST に設定
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    echo "Asia/Tokyo" > /etc/timezone

# 作業ディレクトリを設定
WORKDIR /app

# requirements.txtをコピーし、Pythonパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポートを公開
EXPOSE 5000

# アプリケーションの起動コマンド
CMD ["python", "app.py"]
