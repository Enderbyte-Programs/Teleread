sudo apt install python3
sudo apt install python3-pip
sudo pip3 install pyinstaller
pyinstaller --onefile teleread.py
cp ./dist/teleread .
rm -rf ./build
rm -rf ./dist