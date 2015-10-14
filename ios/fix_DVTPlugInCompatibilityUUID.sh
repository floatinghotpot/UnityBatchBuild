#!/bin/bash

#
# when call Xcodebuild command line, sometimes it will report following error.
# this script will fix the error.
#
# xcodebuild[42968:11009294] [MT] PluginLoading: Required plug-in compatibility UUID 0420B86A-AA43-4792-9ED0-6FE0F2B16A13 for plug-in at path '~/Library/Application Support/Developer/Shared/Xcode/Plug-ins/Unity4XC.xcplugin' not present in DVTPlugInCompatibilityUUIDs
#

XCODEUUID=`defaults read /Applications/Xcode.app/Contents/Info DVTPlugInCompatibilityUUID`

for f in ~/Library/Application\ Support/Developer/Shared/Xcode/Plug-ins/*; 
  do defaults write "$f/Contents/Info" DVTPlugInCompatibilityUUIDs -array-add $XCODEUUID; 
done
