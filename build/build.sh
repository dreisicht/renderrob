sudo apt-get update
sudo apt-get -y install python3
sudo apt-get -y install python3-pip
pip3 install xlrd
pip3 install gspread
pip3 install oauth2client
pip3 install sty
pip3 install https://github.com/pyinstaller/pyinstaller/archive/develop.zip

sudo apt install libxi6 libxrender1 libgl1-mesa-glx
curl -o blender.tar.xz https://builder.blender.org/download/blender-2.83-e5ace51295b9-linux64.tar.xz
tar -xvf blender.tar.xz

python3 -m PyInstaller --onefile --icon /home/ubuntu/RenderRob/img/renderrob_icon.ico /home/ubuntu/RenderRob/src/rr_master.py


