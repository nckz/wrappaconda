#!/usr/bin/env python
# Author: Nick Zwart
# Date: 2015oct31 
# Adapted from SO: http://stackoverflow.com/questions/7404792/how-to-create-mac-application-bundle-for-python-script-via-python

import os
import sys
import stat
import errno
import shutil
import optparse
import subprocess

# check for installed utilities
try:
    subprocess.check_output('command -v wget >/dev/null 2>&1;', shell=True)
    get_cmd = 'wget -c '
except:
    try:
        subprocess.check_output('command -v curl >/dev/null 2>&1;', shell=True)
        get_cmd = 'curl -O -C - '
    except:
        print "This script requires \'wget\' or \'curl\' and neither were found."
        raise

# get user input
parser = optparse.OptionParser()
parser.add_option("-n", "--name", dest='name', help="The name of this app.")
parser.add_option("-v", "--version", dest='version', help="The version of this app.", default='0.1')
parser.add_option("-i", "--icon", dest='icon_file', help="Icon file to be used in the bundle.")
parser.add_option("-t", "--target", dest='target', help="The python script to be executed by the app.")
parser.add_option("-c", "--channel", dest='channel', help="The Anaconda.org package channel.", default='defaults')
parser.add_option("-p", "--package", dest='package', help="The package name.")
parser.add_option("--py2", action="store_true", dest='py2', help="Icon file to be used in the bundle.")
parser.add_option("-o", "--over-write", action="store_true", dest='overwrite', help="Overwrite existing apps. Use caution!!!")
options, args = parser.parse_args()

# check for input errors
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
if options.target == '' or options.target is None:
    print "The app target is a required input."
    parser.print_help()
    sys.exit(1)
if options.package == '' or options.package is None:
    print "An app package is a required input."
    parser.print_help()
    sys.exit(1)

# anaconda website and miniconda package info
#   -python 3 is the default miniconda
MINICONDA_NAME='Miniconda3'
if options.py2:
    MINICONDA_NAME='Miniconda'
MINICONDA_WEB='https://repo.continuum.io/miniconda/'
MINICONDA_OSX=MINICONDA_NAME+'-latest-MacOSX-x86_64.sh'

# setup the CFBundle variables for the Info.plist
CFBundleVersion = options.version
CFBundleName = options.name
CFBundleGetInfoString = CFBundleName + " " + CFBundleVersion
CFBundleShortVersionString = CFBundleGetInfoString
CFBundleIdentifier = "com.gpilab."+CFBundleName
CFBundleIconFile = 'app.icns'
AppTarget = options.target

apppath = '/Applications/'+CFBundleName+'.app'
id_file_path = apppath + "/Contents/Resources/wrappaconda"
python_path = apppath + "/Contents/Resources/miniconda/bin/python"
conda_path = apppath + "/Contents/Resources/miniconda/bin/conda"

if os.path.exists(apppath):
    if options.overwrite:
        print "Removing existing path: "+apppath
        try:
            with open(id_file_path, 'r') as f:
                assert f.read().count('Wr[App]-A-Conda') > 0
            shutil.rmtree(apppath)
        except:
            print "The app \'"+apppath+"\' cannot be verified for deletion, exiting..."
    else:
        print "The app \'"+apppath+"\' already exists, exiting..."

# build the .app directory and supporting files
try:
    os.mkdir(apppath)
    os.mkdir(apppath + "/Contents")
    os.mkdir(apppath + "/Contents/MacOS")
    os.mkdir(apppath + "/Contents/Resources")
except OSError as e:
    if (e[0] == errno.EPERM):
        print "You must have root permissions to write to /Applications."
    sys.exit(1)

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

with open(apppath + "/Contents/Info.plist", "w") as f:
    f.write(info_plist % (CFBundleGetInfoString, CFBundleIconFile, CFBundleIdentifier, CFBundleName, CFBundleShortVersionString, CFBundleVersion))

with open(apppath + "/Contents/PkgInfo", "w") as f:
    f.write("APPL????")

with open(apppath + "/Contents/MacOS/main.py", "w") as f, open(AppTarget, "r") as t:
    hdr_shebang = "#!"+ python_path + "\n"
    f.write(hdr_shebang + t.read())

with open(id_file_path, "w") as f:
    id_file = """This app was generated by Wr[App]-A-Conda."""
    f.write(id_file)

oldmode = os.stat(apppath + "/Contents/MacOS/main.py").st_mode
os.chmod(apppath + "/Contents/MacOS/main.py", oldmode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

# download miniconda
try:
    subprocess.check_output(get_cmd+MINICONDA_WEB+MINICONDA_OSX, shell=True)
except:
    print "Failed to download miniconda."

# install miniconda
try:
    os.chmod('./'+MINICONDA_OSX, 0o777)
    subprocess.check_output('./'+MINICONDA_OSX+' -b -p '+apppath+"/Contents/Resources/miniconda", shell=True)
except:
    print "Failed to run miniconda."

# install central conda package
try:
    subprocess.check_output(conda_path+' install -y -c '+options.channel+' '+options.package, shell=True)
    subprocess.check_output(conda_path+' -t -i -p -l -y', shell=True)
except:
    print "Failed to run conda."
    raise

print apppath + " has been created."
