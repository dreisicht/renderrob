rm -rf build dist renderrob.app
python3.11 tools/py2app_setup.py py2app

source tools/py2appsigner_settings.sh
py2appSign -p 3.11 -d "" -a renderrob --verbose zipsign
py2appSign -p 3.11 -d "" -a renderrob --verbose appsign
