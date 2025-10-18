rm -rf build dist renderrob.app
uv run setup.py py2app

rm -rf dist/renderrob.app/Contents/Resources/lib/python3.11/PySide6/Linguist.app
rm -rf dist/renderrob.app/Contents/Resources/lib/python3.11/PySide6/Designer.app
rm -rf dist/renderrob.app/Contents/Resources/lib/python3.11/PySide6/Assistant.app

source tools/py2appsigner_settings.sh
uv run py2appSign -p 3.11 -a renderrob --verbose zipsign
uv run py2appSign -p 3.11 -a renderrob --verbose appsign
uv run appNotarize -a renderrob --verbose
