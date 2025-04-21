import sys
import os

def alter_sys_paths_mac():
  if sys.platform != "darwin":
    return
  print(__file__)
  bundle_dir = os.path.dirname(os.path.abspath(__file__))
  frameworks = os.path.join(bundle_dir, '..', 'Frameworks')
  lib_dynload = os.path.join(frameworks, 'lib', 'python3.x', 'lib-dynload')
  sys.path.append(lib_dynload)
  sys.path.append(frameworks)
  print(sys.path)

alter_sys_paths_mac()
