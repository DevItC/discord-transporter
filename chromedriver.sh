#! /bin/sh

sudo apt-get install -yqq unzip
VERSION=$(wget http://chromedriver.storage.googleapis.com/LATEST_RELEASE -q -O -)
echo "[*] Fetching chromedriver version $VERSION."
wget -N -q http://chromedriver.storage.googleapis.com/$VERSION/chromedriver_linux64.zip
echo "[*] Installing chromedriver."
unzip -q chromedriver_linux64.zip
chmod +x chromedriver
sudo mv -f chromedriver /usr/local/share/chromedriver
sudo ln -s -f /usr/local/share/chromedriver /usr/local/bin/chromedriver
sudo ln -s -f /usr/local/share/chromedriver /usr/bin/chromedriver
rm chromedriver_linux64.zip
echo "[*] Chromedriver installed successfully!"
