rm -rf RenderRob.app
pyside6-deploy -c build/pysidedeploy_mac.spec
mv RenderRob.app/Contents/MacOS/ RenderRob.app/Contents/Frameworks
mkdir RenderRob.app/Contents/MacOS
mv RenderRob.app/Contents/Frameworks/renderrob RenderRob.app/Contents/MacOS/renderrob
install_name_tool -change "@executable_path/Python" "@executable_path/../Frameworks/Python" RenderRob.app/Contents/MacOS/renderrob
codesign -s "Peter Baintner" --keychain "dev" RenderRob.app -f

