#!/usr/bin/env python
# Adapted from SO: http://stackoverflow.com/questions/7404792/how-to-create-mac-application-bundle-for-python-script-via-python

import stat
import sys
import os, os.path

assert len(sys.argv) > 1
apppath = sys.argv[1]
assert os.path.splitext(apppath)[1] == ".app"

os.mkdir(apppath)
os.mkdir(apppath + "/Contents")
os.mkdir(apppath + "/Contents/MacOS")

CFBundleVersion = "1.0.0"
CFBundleName = "Test"
CFBundleGetInfoString = CFBundleName + " " + CFBundleVersion
CFBundleShortVersionString = CFBundleGetInfoString
CFBundleIdentifier = "com.gpilab.test"

info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleExecutable</key>
    <string>main.py</string>
    <key>CFBundleGetInfoString</key>
    <string>%s</string>
    <key>CFBundleIconFile</key>
    <string>app.icns</string>
    <key>CFBundleIdentifier</key>
    <string>%s</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>%s</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>%s</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleVersion</key>
    <string>%s</string>
    <key>NSAppleScriptEnabled</key>
    <string>YES</string>
    <key>NSMainNibFile</key>
    <string>MainMenu</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
"""

main_py = """#!/usr/bin/env python
import sys
from PyQt4 import QtGui

def main():
    
    app = QtGui.QApplication(sys.argv)

    w = QtGui.QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Simple')
    w.show()
    w.raise_()
    
    sys.exit(app.exec_())

main()
"""

with open(apppath + "/Contents/Info.plist", "w") as f:
    f.write(info_plist % (CFBundleGetInfoString, CFBundleIdentifier, CFBundleName, CFBundleShortVersionString, CFBundleVersion))

with open(apppath + "/Contents/PkgInfo", "w") as f:
    f.write("APPL????")

with open(apppath + "/Contents/MacOS/main.py", "w") as f:
    f.write(main_py)

oldmode = os.stat(apppath + "/Contents/MacOS/main.py").st_mode
os.chmod(apppath + "/Contents/MacOS/main.py", oldmode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
