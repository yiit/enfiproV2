#!/bin/bash

# Hata olursa scripti durdur
set -e

echo "🚀 EnfiproV2 Kurulumu Başlıyor..."
read -p "Devam etmek için ENTER'a basın..."

### 1. GEREKLİ LINUX PAKETLERİ ###
echo "📦 Gerekli Linux paketleri kuruluyor..."
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y wget git build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev curl libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev \
    flex bison gnupg2 lsb-release gpg samba samba-common-bin
read -p "Devam etmek için ENTER'a basın..."

### 2. ENFIPROV2 KLASÖRÜ VE GITHUB KLON ###
echo "📁 ~/enfiproV2 klasörü hazırlanıyor ve GitHub'dan proje indiriliyor..."
mkdir -p ~/enfiproV2
cd ~/enfiproV2
git clone https://github.com/yiit/enfiproV2.git
cd enfiproV2
read -p "Devam etmek için ENTER'a basın..."

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
read -p "Devam etmek için ENTER'a basın..."

### 4. PYTHON VENV OLUŞTUR ###
echo "🔧 Python venv oluşturuluyor..."
~/enfiproV2/python3.13/bin/python3.13 -m venv ~/enfiproV2/venv
read -p "Devam etmek için ENTER'a basın..."

### 5. PIP GÜNCELLEME ###
echo "⬆️ pip güncelleniyor..."
~/enfiproV2/venv/bin/pip install --upgrade pip
read -p "Devam etmek için ENTER'a basın..."

### 6. NODEENV ve NODE.JS KURULUMU ###
echo "🟢 nodeenv kuruluyor ve Node.js kuruluyor..."
~/enfiproV2/venv/bin/pip install nodeenv
~/enfiproV2/venv/bin/nodeenv -p
export PATH="$HOME/enfiproV2/venv/bin:$PATH"
~/enfiproV2/venv/bin/npm install -g npm@11.3.0
~/enfiproV2/venv/bin/npm install express serialport @serialport/parser-readline cors
read -p "Devam etmek için ENTER'a basın..."

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
read -p "Devam etmek için ENTER'a basın..."

### 8. POSTGRESQL DATA DİZİNİ OLUŞTUR ###
echo "📂 PostgreSQL data dizini hazırlanıyor..."
mkdir -p ~/enfiproV2/pgsql14_data
~/enfiproV2/pgsql14/bin/initdb -D ~/enfiproV2/pgsql14_data
read -p "Devam etmek için ENTER'a basın..."

### 9. POSTGRESQL SERVER BAŞLAT ###
echo "🚀 PostgreSQL server başlatılıyor..."
~/enfiproV2/pgsql14/bin/pg_ctl -D ~/enfiproV2/pgsql14_data -l ~/enfiproV2/pgsql14_data/logfile start
sleep 5
read -p "Devam etmek için ENTER'a basın..."

### 10. POSTGRESQL DATABASE VE USER OLUŞTUR ###
echo "🛠 Django için PostgreSQL kullanıcı ve veritabanı oluşturuluyor..."
~/enfiproV2/pgsql14/bin/psql -h localhost -d postgres -c "CREATE ROLE django_user WITH LOGIN PASSWORD '1';"
~/enfiproV2/pgsql14/bin/psql -h localhost -d postgres -c "CREATE DATABASE django_db OWNER django_user;"
~/enfiproV2/pgsql14/bin/psql -h localhost -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE django_db TO django_user;"
read -p "Devam etmek için ENTER'a basın..."

### 11. PYTHON GEREKLİ PIP KÜTÜPHANELERİ ###
echo "📦 Django ve gerekli pip kütüphaneleri yükleniyor..."
~/enfiproV2/venv/bin/pip install Django psycopg2-binary
~/enfiproV2/venv/bin/pip install -r requirements.txt
read -p "Devam etmek için ENTER'a basın..."

### 12. DJANGO MIGRATIONS VE SUPERUSER ###
echo "🛠 Django makemigrations ve migrate çalıştırılıyor..."
cd ~/enfiproV2/enfiproV2
~/enfiproV2/venv/bin/python manage.py makemigrations
~/enfiproV2/venv/bin/python manage.py migrate
echo "🛠 Django superuser (pi / 1) oluşturuluyor..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('pi', 'pi@example.com', '1')" | ~/enfiproV2/venv/bin/python manage.py shell
read -p "Devam etmek için ENTER'a basın..."

### 13. SYSTEMD SERVİSLERİ OLUŞTURULUYOR ###
echo "🛠 PostgreSQL, Django ve SerialJS systemd servisleri yazılıyor..."
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

sudo systemctl daemon-reload
sudo systemctl enable postgresql-enfipro
sudo systemctl enable django-enfipro
sudo systemctl enable serialjs-enfipro
sudo systemctl start postgresql-enfipro
sudo systemctl start django-enfipro
sudo systemctl start serialjs-enfipro
read -p "Devam etmek için ENTER'a basın..."

### 14. USB YAZICI & SERIAL PORT AYARLARI ###
echo "🔧 USB yazıcı ve serial port izinleri ayarlanıyor..."
sudo tee /etc/udev/rules.d/99-usblp.rules > /dev/null <<EOL
SUBSYSTEM=="usb", ATTR{idVendor}=="0fe6", ATTR{idProduct}=="8800", MODE="0666", GROUP="lp"
EOL

sudo tee /etc/udev/rules.d/99-serial-permissions.rules > /dev/null <<EOL
KERNEL=="ttyS0", MODE="0666"
KERNEL=="ttyS1", MODE="0666"
EOL

sudo udevadm control --reload-rules
sudo udevadm trigger
sudo usermod -aG lp $USER
sudo chmod 666 /dev/ttyS0
sudo chmod 666 /dev/ttyS1
read -p "Devam etmek için ENTER'a basın..."

### 15. SAMBA SHARE ###
echo "🔧 Samba kuruluyor ve enfiproV2 klasörü paylaşılıyor..."
sudo tee -a /etc/samba/smb.conf > /dev/null <<EOL

[enfiproV2]
comment = enfiproV2 Share
path = /home/pi/enfiproV2
browseable = yes
writeable = yes
guest ok = yes
force user = pi
create mask = 0777
directory mask = 0777
EOL

sudo systemctl restart smbd
read -p "Devam etmek için ENTER'a basın..."

### 16. GOOGLE CHROME KURULUMU ###
echo "🌐 Google Chrome kuruluyor..."
wget -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome.deb || sudo apt --fix-broken install -y
sudo apt --fix-broken install -y
sudo apt remove -y chromium --purge
sudo apt autoremove -y
read -p "Devam etmek için ENTER'a basın..."

### 17. LXDE AUTOSTART ###
echo "🖥 LXDE autostart dosyası hazırlanıyor..."
mkdir -p /home/pi/.config/lxsession/LXDE-pi
sudo tee /home/pi/.config/lxsession/LXDE-pi/autostart > /dev/null <<EOL
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@/usr/bin/google-chrome --kiosk --no-first-run --force-device-scale-factor=0.65 http://localhost:8000
EOL
sudo chown pi:pi /home/pi/.config/lxsession/LXDE-pi/autostart
read -p "Devam etmek için ENTER'a basın..."

### 18. BİTİRME ###
echo ""
echo "🔔 İlk açılışta Virtual_Keyboard uzantısını elle yüklemeyi unutmayın!"
echo "✅ Kurulum tamamlandı!"
echo "♻️ 10 saniye içinde sistem yeniden başlayacak..."
sleep 10
sudo reboot
