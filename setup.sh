sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get install -y python3-pip firefox
pip3 install -r requirements.txt
./geckodriver.sh
./chromedriver.sh
