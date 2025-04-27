#!/bin/bash

# Hata durumunda scripti durdur
set -e

### 1. GEREKLİ PAKETLER ###
echo "\U0001F449 Gerekli Linux paketleri kuruluyor..."
sudo apt update
sudo apt install -y wget build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev curl libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev \
    flex bison libreadline-dev zlib1g-dev

### 2. ENFIPROV2 KLASÖRÜ ###
echo "\U0001F449 ~/enfiproV2 klasörü oluşturuluyor..."
mkdir -p ~/enfiproV2
cd ~/enfiproV2

### 3. PYTHON 3.13.1 KURULUMU ###
echo "\U0001F449 Python 3.13.1 indiriliyor ve kuruluyor..."
wget https://www.python.org/ftp/python/3.13.1/Python-3.13.1.tar.xz
rm -rf Python-3.13.1

# Çıkart ve derle
 tar -xf Python-3.13.1.tar.xz
cd Python-3.13.1
./configure --enable-optimizations --prefix=$HOME/enfiproV2/python3.13
make -j$(nproc)
make install

# Ana dizine geri dön
cd ~/enfiproV2

### 4. PYTHON VENV OLUŞTUR ###
echo "\U0001F449 Python venv oluşturuluyor..."
~/enfiproV2/python3.13/bin/python3.13 -m venv venv
source ~/enfiproV2/venv/bin/activate

### 5. PIP GÜNCELLEME ###
echo "\U0001F449 pip güncelleniyor..."
pip install --upgrade pip

### 6. NODEENV KURULUMU ve NODE.JS ###
echo "\U0001F449 nodeenv kuruluyor ve Node.js kuruluyor..."
pip install nodeenv
nodeenv -p

### 7. POSTGRESQL 14 KURULUMU ###
echo "\U0001F449 PostgreSQL 14 indiriliyor ve kuruluyor..."
wget https://ftp.postgresql.org/pub/source/v14.11/postgresql-14.11.tar.gz
rm -rf postgresql-14.11

tar -xzf postgresql-14.11.tar.gz
cd postgresql-14.11
./configure --prefix=$HOME/enfiproV2/pgsql14
make -j$(nproc)
make install

# Ana dizine geri dön
cd ~/enfiproV2

### 8. POSTGRESQL DATA DİZİNİ HAZIRLA ###
echo "\U0001F449 PostgreSQL veritabanı init yapılıyor..."
mkdir -p ~/enfiproV2/pgsql14_data
~/enfiproV2/pgsql14/bin/initdb -D ~/enfiproV2/pgsql14_data

### 9. PYTHON GEREKLİ KÜTÜPHANELER ###
echo "\U0001F449 Django ve gerekli kütüphaneler yükleniyor..."
pip install Django psycopg2-binary

### 10. BİLGİLENDİRME ###
echo ""
echo "\U0001F389 Tum kurulum tamamlandı!"
echo ""
echo "Kullanım icin:"
echo "1. Ortamı aktif etmek icin: source ~/enfiproV2/venv/bin/activate"
echo "2. PostgreSQL'i başlatmak icin: ~/enfiproV2/pgsql14/bin/pg_ctl -D ~/enfiproV2/pgsql14_data -l ~/enfiproV2/pgsql14_data/logfile start"
echo "3. Django projeni başlatabilirsin!"
echo ""
echo "\U0001F680 Iyi calışmalar!"
