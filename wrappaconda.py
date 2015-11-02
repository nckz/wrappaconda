#!/usr/bin/env python
# Author: Nick Zwart
# Date: 2015oct31 
# Adapted from SO: http://stackoverflow.com/questions/7404792/how-to-create-mac-application-bundle-for-python-script-via-python

import os
import sys
import stat
import shutil
import optparse

parser = optparse.OptionParser()
parser.add_option("-n", "--name", dest='name', help="The name of this app.")
parser.add_option("-v", "--version", dest='version', help="The version of this app.", default='0.1')
parser.add_option("-i", "--icon", dest='icon_file', help="Icon file to be used in the bundle.")
options, args = parser.parse_args()

if options.icon_file is not None:
    if not os.path.isfile(options.icon_file):
        print "The supplied icon path doesn\'t point to a valid file."
        parser.print_help()
        sys.exit(1)
    if os.path.splitext(options.icon_file)[1] != ".icns":
        print "The supplied icon path must point to an .icns file."
        parser.print_help()
        sys.exit(1)
if options.name == '' or options.name is None:
    print "The app name is a required input."
    parser.print_help()
    sys.exit(1)

CFBundleVersion = options.version
CFBundleName = options.name
CFBundleGetInfoString = CFBundleName + " " + CFBundleVersion
CFBundleShortVersionString = CFBundleGetInfoString
CFBundleIdentifier = "com.gpilab."+CFBundleName
CFBundleIconFile = 'app.icns'

apppath = './'+CFBundleName+'.app'

os.mkdir(apppath)
os.mkdir(apppath + "/Contents")
os.mkdir(apppath + "/Contents/MacOS")
os.mkdir(apppath + "/Contents/Resources")

if options.icon_file is not None:
    shutil.copy(options.icon_file, apppath + "/Contents/Resources/" + CFBundleIconFile)

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
    <string>%s</string>
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
    f.write(info_plist % (CFBundleGetInfoString, CFBundleIconFile, CFBundleIdentifier, CFBundleName, CFBundleShortVersionString, CFBundleVersion))

with open(apppath + "/Contents/PkgInfo", "w") as f:
    f.write("APPL????")

with open(apppath + "/Contents/MacOS/main.py", "w") as f:
    f.write(main_py)

oldmode = os.stat(apppath + "/Contents/MacOS/main.py").st_mode
os.chmod(apppath + "/Contents/MacOS/main.py", oldmode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
