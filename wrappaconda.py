#!/usr/bin/env python
# Author: Nick Zwart
# Date: 2015oct31 

from __future__ import print_function

import os
import sys
import stat
import errno
import shutil
import optparse
import traceback
import subprocess

wrappaconda_name_string = 'Wr[App]-A-Conda'

class AppAtizer(object):

    def __init__(self):

        # tmp paths
        self._downloads_prefix = os.path.expanduser('~/Downloads')
        if not os.path.isdir(self._downloads_prefix):
            self._downloads_prefix = './' # use cwd

        # try for wget or curl
        self._get = self._getDownloaderCommand()

        # cli input
        self._parseUserInput()

        # .app paths
        self._apppath = '/Applications/'+self._name+'.app'
        self._contents_prefix = self._apppath + "/Contents"
        self._resource_prefix = self._contents_prefix + "/Resources"
        self._info_plist_path = self._contents_prefix + "/Info.plist"
        self._pkg_info_path = self._contents_prefix + "/PkgInfo"
        self._macos_prefix = self._contents_prefix + "/MacOS"
        self._cfbundle_icon_filename = 'app.icns'

        # Wr[App]-A-Conda paths
        self._id_file_path = self._resource_prefix + "/wrappaconda"

        # miniconda paths
        self._miniconda_prefix = self._resource_prefix + "/miniconda"
        self._python_path = self._miniconda_prefix + "/bin/python"
        self._conda_path = self._miniconda_prefix + "/bin/conda"


    def _parseUserInput(self):
        # get user input
        parser = optparse.OptionParser()
        parser.add_option("-n", "--name", dest='name', help="[REQUIRED] The name of this app.")
        parser.add_option("-t", "--target", dest='target', help="[REQUIRED] The binary or script found in Anaconda\'s $PREFIX/bin.")
        parser.add_option("-v", "--version", dest='version', help="The version of this app.", default='0.1')
        parser.add_option("-i", "--icon", dest='icon_file', help="Icon file to be used in the bundle.")
        parser.add_option("-c", "--channel", dest='channel', help="The Anaconda.org package channel(s), or url(s) separated by commas (e.g. nckz,https://conda.anaconda.org/gpi/channel/rc) (defaults to \'defaults\')", default='defaults')
        parser.add_option("-p", "--package", dest='package', help="The package name(s) separated by commas (e.g. scipy=0.15.0,curl=7.26.0,pip).")
        parser.add_option("-r", "--rootenv", dest='rootenv', help="A root environment file (created using: \'conda list --export\').")
        parser.add_option("--py", dest='py_ver', help="Choose the distro python version using the major and minor version numbers (defaults to 3.5).", default='3.5')
        parser.add_option("-o", "--overwrite", action="store_true", dest='overwrite', help="Overwrite an existing app with the same \'name\'. Use caution!!!")
        options, args = parser.parse_args()

        try:
            # check for input errors
            assert options.name is not None
            assert options.target is not None
            if options.icon_file is not None:
                assert os.path.isfile(options.icon_file)
                assert options.icon_file.endswith(".icns")
            if options.rootenv is not None:
                assert os.path.isfile(options.rootenv)
        except:
            parser.print_help()
            raise

        self._name = options.name
        self._version = options.version
        self._target = options.target
        self._icon_file = options.icon_file
        self._channel = options.channel
        self._package = options.package
        self._root_env = options.rootenv
        self._py_ver = options.py_ver
        self._overwrite = options.overwrite

    def _getDownloaderCommand(self):
        # check for installed utilities
        try:
            subprocess.check_output('command -v wget >/dev/null 2>&1;', shell=True)
            return 'wget --directory-prefix ' + self._downloads_prefix + ' -c {}'
        except:
            try:
                subprocess.check_output('command -v curl >/dev/null 2>&1;', shell=True)
                return 'cd '+self._downloads_prefix+' && curl --fail -O -C - {} '
            except:
                print("This script requires \'wget\' or \'curl\' and neither were found.")
                raise

    def appPath(self):
        return self._apppath

    def deleteExistingApp(self):
        if os.path.exists(self._apppath):
            if self._overwrite:
                print("Removing existing path: "+self._apppath)
                try:
                    with open(self._id_file_path, 'r') as f:
                        assert f.read().count(wrappaconda_name_string) > 0
                    shutil.rmtree(self._apppath)
                except:
                    print("The app \'"+self._apppath+"\' cannot be verified for deletion. You may have to remove it manually. Skipping...")
            else:
                print("The app \'"+self._apppath+"\' already exists, exiting...")

    def buildAppSkeleton(self):
        # build the .app directory and supporting files
        try:
            os.mkdir(self._apppath)
            os.mkdir(self._contents_prefix)
            os.mkdir(self._macos_prefix)
            os.mkdir(self._resource_prefix)
        except OSError as e:
            if e.errno == errno.EPERM:
                print("You must have root permissions to write to /Applications.")
            raise

    def copyIconFile(self):
        if self._icon_file is not None:
            shutil.copy(self._icon_file, self._resource_prefix + '/' + self._cfbundle_icon_filename)

    def writeInfoPList(self):
        # http://stackoverflow.com/questions/7404792/how-to-create-mac-application-bundle-for-python-script-via-python
        CFBundleName = self._name
        CFBundleVersion = self._version
        CFBundleIconFile = self._cfbundle_icon_filename
        CFBundleGetInfoString = CFBundleName + " " + CFBundleVersion
        CFBundleShortVersionString = CFBundleGetInfoString
        CFBundleIdentifier = "com.gpilab."+CFBundleName
        CFBundleExecutable = self._target

        info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleExecutable</key>
    <string>%s</string>
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
        with open(self._info_plist_path, "w") as f:
            f.write(info_plist % (CFBundleExecutable, CFBundleGetInfoString, CFBundleIconFile, CFBundleIdentifier, CFBundleName, CFBundleShortVersionString, CFBundleVersion))

    def writePkgInfo(self):
        with open(self._pkg_info_path, "w") as f:
            f.write("APPL????")

    def writeWrappacondaIDFile(self):
        with open(self._id_file_path, "w") as f:
            f.write("This app was generated by " + wrappaconda_name_string)

    def setupMiniconda(self):
        # anaconda website and miniconda package info
        #   -python 3 is the default miniconda
        MINICONDA_NAME='Miniconda3'
        if float(self._py_ver) < 3:
            MINICONDA_NAME='Miniconda'
        MINICONDA_WEB='https://repo.continuum.io/miniconda/'
        MINICONDA_OSX=MINICONDA_NAME+'-latest-MacOSX-x86_64.sh'

        # download miniconda
        try:
            cmd = self._get.format(MINICONDA_WEB+MINICONDA_OSX)
            print(cmd)
            subprocess.check_output(cmd, shell=True)
        except:
            print("Failed to download miniconda.")

        # install miniconda
        try:
            os.chmod(self._downloads_prefix+'/'+MINICONDA_OSX, 0o777)
            cmd = self._downloads_prefix+'/'+MINICONDA_OSX+' -b -p '+self._miniconda_prefix
            print(cmd)
            subprocess.check_output(cmd, shell=True)
        except:
            print("Failed to run miniconda.")

        # install central conda package
        if self._package:
            try:
                python = ' python=='+self._py_ver+' '
                conda_cmd = self._conda_path+' install -y -c '+' -c '.join(self._channel.split(','))+' '+' '.join(self._package.split(',')) + python
                if self._root_env:
                    conda_cmd += ' --file '+self._root_env
                print(conda_cmd)
                subprocess.check_output(conda_cmd, shell=True)
                subprocess.check_output(self._conda_path+' clean -t -i -p -l -y', shell=True)
            except:
                print("Failed to run conda.")
                raise

    def linkTarget(self):
        # check for the existence of the target
        try:
            assert os.path.isfile(self._miniconda_prefix + '/bin/' + self._target)
            os.link(self._miniconda_prefix + '/bin/' + self._target, self._macos_prefix + '/' + self._target)
        except:
            print(self._target, ' doesn\'t exist in Miniconda bin.')
            raise 

def main():
    make = AppAtizer()
    make.deleteExistingApp()
    make.buildAppSkeleton()
    make.writeWrappacondaIDFile()
    make.copyIconFile()
    make.setupMiniconda()
    make.linkTarget()
    make.writeInfoPList()
    make.writePkgInfo()
    print(make.appPath() + " has been created.")

if __name__ == '__main__':
    main()
