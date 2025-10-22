rm -rf build dist renderrob.app renderrob.zip
uv run setup.py py2app

uv run tools/sign_all.py

source tools/py2appsigner_settings.sh
uv run py2appSign -p 3.11 -a renderrob --verbose zipsign
uv run py2appSign -p 3.11 -a renderrob --verbose appsign
uv run appNotarize -a renderrob --verbose
uv run appStaple -d renderrob -a renderrob --verbose
uv run appVerify -d renderrob -a renderrob

# ditto -c -k --keepParent "dist/renderrob.app" "renderrob.zip"

hdiutil create -fs HFS+ -srcfolder "dist/renderrob.app" -volname "Renderrob Installer" "Renderrob.dmg"
