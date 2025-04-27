#!/bin/bash

# Hata olursa scripti durdur
set -e

echo "🚀 EnfiproV2 Kurulumu Başlıyor..."

### 1. GEREKLİ LINUX PAKETLERİ ###
echo "📦 Gerekli Linux paketleri kuruluyor..."
sudo apt update
sudo apt install -y wget git build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev curl libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev \
    flex bison gnupg2 lsb-release

### 2. ENFIPROV2 KLASÖRÜ VE GITHUB KLON ###
echo "📁 ~/enfiproV2 klasörü hazırlanıyor ve GitHub'dan proje indiriliyor..."
mkdir -p ~/enfiproV2
cd ~/enfiproV2

git clone https://github.com/yiit/enfiproV2.git
cd enfiproV2

### 3. PYTHON 3.13.1 KURULUMU ###
echo "🐍 Python 3.13.1 kuruluyor..."
wget https://www.python.org/ftp/python/3.13.1/Python-3.13.1.tar.xz
rm -rf Python-3.13.1
tar -xf Python-3.13.1.tar.xz
cd Python-3.13.1
./configure --enable-optimizations --prefix=$HOME/enfiproV2/python3.13
make -j$(nproc)
make install
cd ..

### 4. PYTHON VENV OLUŞTUR ###
echo "🔧 Python venv oluşturuluyor..."
~/enfiproV2/python3.13/bin/python3.13 -m venv venv
source ~/enfiproV2/venv/bin/activate

### 5. PIP GÜNCELLEME ###
echo "⬆️ pip güncelleniyor..."
pip install --upgrade pip

### 6. NODEENV ve NODE.JS KURULUMU ###
echo "🟢 nodeenv kuruluyor ve Node.js kuruluyor..."
pip install nodeenv
nodeenv -p

echo "⬆️ npm en son sürüme güncelleniyor (npm@11.3.0)..."
npm install -g npm@11.3.0

echo "📦 Gerekli npm paketleri kuruluyor..."
npm install express serialport @serialport/parser-readline cors

### 7. POSTGRESQL 14 KURULUMU ###
echo "🐘 PostgreSQL 14 kuruluyor..."
wget https://ftp.postgresql.org/pub/source/v14.11/postgresql-14.11.tar.gz
rm -rf postgresql-14.11
tar -xzf postgresql-14.11.tar.gz
cd postgresql-14.11
./configure --prefix=$HOME/enfiproV2/pgsql14
make -j$(nproc)
make install
cd ..

### 8. POSTGRESQL DATA DİZİNİ OLUŞTUR ###
echo "📂 PostgreSQL data dizini hazırlanıyor..."
mkdir -p ~/enfiproV2/pgsql14_data
~/enfiproV2/pgsql14/bin/initdb -D ~/enfiproV2/pgsql14_data

### 9. PYTHON GEREKLİ PIP KÜTÜPHANELERİ ###
echo "📦 Django ve gerekli pip kütüphaneleri yükleniyor..."
pip install Django psycopg2-binary

### 10. SYSTEMD SERVİSLERİ OLUŞTURULUYOR ###

echo "🛠 PostgreSQL systemd servisi yazılıyor..."
sudo tee /etc/systemd/system/postgresql-enfipro.service > /dev/null <<EOL
[Unit]
Description=PostgreSQL 14 (enfiproV2) manual instance
After=network.target

[Service]
Type=forking
User=pi
ExecStart=/home/pi/enfiproV2/pgsql14/bin/pg_ctl -D /home/pi/enfiproV2/pgsql14_data -l /home/pi/enfiproV2/pgsql14_data/logfile start
ExecStop=/home/pi/enfiproV2/pgsql14/bin/pg_ctl -D /home/pi/enfiproV2/pgsql14_data stop
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

echo "🛠 Django systemd servisi yazılıyor..."
sudo tee /etc/systemd/system/django-enfipro.service > /dev/null <<EOL
[Unit]
Description=Django Server for EnfiproV2
After=network.target postgresql-enfipro.service

[Service]
User=pi
WorkingDirectory=/home/pi/enfiproV2/enfiproV2
Environment="PATH=/home/pi/enfiproV2/venv/bin"
ExecStart=/home/pi/enfiproV2/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

echo "🛠 Serial.js Node.js systemd servisi yazılıyor..."
sudo tee /etc/systemd/system/serialjs-enfipro.service > /dev/null <<EOL
[Unit]
Description=Node.js Serial.js Service for EnfiproV2
After=network.target postgresql-enfipro.service

[Service]
User=pi
WorkingDirectory=/home/pi/enfiproV2/enfiproV2
ExecStart=/home/pi/enfiproV2/venv/bin/node serial.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

### 11. SERVİSLERİ ETKİNLEŞTİR VE BAŞLAT ###
echo "🔄 Systemd reload ediliyor..."
sudo systemctl daemon-reload

echo "🚀 Servisler enable yapılıyor ve başlatılıyor..."
sudo systemctl enable postgresql-enfipro
sudo systemctl enable django-enfipro
sudo systemctl enable serialjs-enfipro

sudo systemctl start postgresql-enfipro
sudo systemctl start django-enfipro
sudo systemctl start serialjs-enfipro

### 12. ANYDESK KURULUMU ###
echo "🖥 AnyDesk kuruluyor..."
wget -qO - https://keys.anydesk.com/repos/DEB-GPG-KEY | sudo apt-key add -
echo "deb http://deb.anydesk.com/ all main" | sudo tee /etc/apt/sources.list.d/anydesk.list
sudo apt update
sudo apt install -y anydesk

### 13. SİSTEMİ GÜNCELLE ###
echo "🛠 Sistem güncelleniyor..."
sudo apt update
sudo apt upgrade -y
sudo apt full-upgrade -y
sudo apt autoremove --purge -y

### 14. KERNEL ve LINUX-IMAGE BİLGİSİ ###
echo "🛠 Kernel ve Linux image durumu:"
uname -r
dpkg --list | grep linux-image

### TAMAMLANDI ###
echo ""
echo "🎯 Tüm kurulum başarıyla tamamlandı!"
echo "🌍 Django Server: http://<Raspberry-IP>:8000/"
echo "🐘 PostgreSQL çalışıyor"
echo "🟢 Serial.js çalışıyor"
echo "🖥 AnyDesk kurulumu tamamlandı"
echo ""
echo "🚀 Artık sistem otomatik başlıyor!"
