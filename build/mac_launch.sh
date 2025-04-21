export DYLD_LIBRARY_PATH=/Users/peterbaintner/repos/renderrob/RenderRob.app/Contents/Frameworks:$DYLD_LIBRARY_PATH
./RenderRob.app/Contents/MacOS/renderrob

Maybe go in a loop through all .so files in the MacOS directory, and then for every file call the install_name_tool?
