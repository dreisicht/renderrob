from PyInstaller.utils.hooks import copy_metadata
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files
hiddenimports = collect_submodules('google-api-python-client')
datas = copy_metadata('google-api-python-client')

