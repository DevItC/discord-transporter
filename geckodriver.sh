#! /bin/sh

VERSION=$(wget -q -O - "https://api.github.com/repos/mozilla/geckodriver/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
FILENAME=geckodriver-$VERSION-linux64.tar.gz
echo "[*] Fetching geckodriver $VERSION."
wget -q https://github.com/mozilla/geckodriver/releases/download/$VERSION/$FILENAME -O $FILENAME
echo "[*] Installing geckodriver."
tar -xzf $FILENAME
chmod +x geckodriver
sudo mv -f geckodriver /usr/local/share/geckodriver
sudo ln -s -f /usr/local/share/geckodriver /usr/local/bin/geckodriver
sudo ln -s -f /usr/local/share/geckodriver /usr/bin/geckodriver
rm $FILENAME
echo "[*] Geckodriver installed successfully!"
