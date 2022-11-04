sudo apt install python3
sudo apt install python3-pip
sudo pip3 install pyinstaller
pip3 install urllib
pyinstaller --onefile teleread.py
cp ./dist/teleread .
rm -rf ./build
rm -rf ./dist
