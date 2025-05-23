[app]

# title of your application
title = RenderRob

# project directory. the general assumption is that project_dir is the parent directory
# of input_file
project_dir = .

# source file path
input_file = /Users/peterbaintner/repos/renderrob/renderrob.py

# directory where exec is stored
exec_directory = .

# path to .pyproject project file
# project_file = 
icon = icons/icon-256.png

[python]

# python path
python_path = /opt/homebrew/opt/python@3.11/bin/python3.11

# python packages to install
# ordered-set = increase compile time performance of nuitka packaging
# zstandard = provides final executable size optimization
packages = nuitka,ordered_set,zstandard

# buildozer = for deploying Android application
android_packages = buildozer,cython

[qt]

# comma separated path to qml files required
# normally all the qml files are added automatically
qml_files = 

# excluded qml plugin binaries
excluded_qml_plugins = 

# path to pyside wheel
wheel_pyside = 

# path to shiboken wheel
wheel_shiboken = 
modules = DBus,Widgets,OpenGL,OpenGLWidgets,Core,UiTools,Gui
plugins = accessiblebridge,platformthemes,generic,styles,xcbglintegrations,platforminputcontexts,iconengines,egldeviceintegrations,imageformats,platforms/darwin,platforms

[nuitka]

# (str) specify any extra nuitka arguments
# eg = extra_args = --show-modules --follow-stdlib
extra_args = --disable-console --macos-create-app-bundle
macos.permissions = 

[buildozer]

# build mode
# possible options = [release, debug]
# release creates an aab, while debug creates an apk
mode = debug

# contrains path to pyside6 and shiboken6 recipe dir
recipe_dir = 

# path to extra qt android jars to be loaded by the application
jars_dir = 

# if empty uses default ndk path downloaded by buildozer
ndk_path = 

# if empty uses default sdk path downloaded by buildozer
sdk_path = 

# modules used. comma separated
modules = 

# other libraries to be loaded. comma separated.
local_libs = plugins_platforms_qtforandroid

# architecture of deployed platform
# possible values = ["aarch64", "armv7a", "i686", "x86_64"]
arch = 

