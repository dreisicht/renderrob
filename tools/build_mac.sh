#!/bin/sh
rm -rf build dist renderrob.app renderrob.zip renderrob.dmg
uv run setup.py py2app

uv run tools/sign_all.py

source tools/py2appsigner_settings.sh
uv run py2appSign -p 3.11 -a renderrob --verbose zipsign
uv run py2appSign -p 3.11 -a renderrob --verbose appsign
uv run appNotarize -a renderrob --verbose
uv run appStaple -d renderrob -a renderrob --verbose
uv run appVerify -d renderrob -a renderrob

test -f renderrob.dmg && rm renderrob.dmg
create-dmg \
  --volname "Render Rob Installer" \
  --volicon "src/icon/icon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "Renderrob.app" 200 190 \
  --hide-extension "Renderrob.app" \
  --app-drop-link 600 185 \
  "renderrob.dmg" \
  "dist/renderrob.app/"

codesign -f --timestamp -s 5K24F4J2M5 renderrob.dmg
xcrun notarytool submit "renderrob.dmg" --keychain-profile "dev" --wait
xcrun stapler staple "renderrob.dmg"
xcrun stapler validate "renderrob.dmg"
