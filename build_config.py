#!/usr/bin/env python
# coding=UTF-8

#from Foundation import NSMutableDictionary

# See: https://github.com/kronenthaler/mod-pbxproj
#from mod_pbxproj import XcodeProject

UNITY_SMCS = {
    "common":"-define:LMGAME",
    "debug":"-define:DEV_VERSION;EnableChinese;", 
    "release":"-define:DISTRIBUTION_VERSION;EnableChinese;CODESTRIPPER;"
}

IOS_PROVISION_CERT = {
    "debug": {
        "id": "com.uniq.LMDemo", 
        "provision": "420a97b6-99ea-48f9-ac2b-5c5032e0ea66",
        "cert": "iPhone Developer: Liming Xie (GA52LZZ6A5)"
    },
    "release": {
        "id": "com.uniq.LMDemo", 
        "provision": "420a97b6-99ea-48f9-ac2b-5c5032e0ea66",
        "cert": "iPhone Distribution: Liming Xie (GA52LZZ6A5)"
    }
}

APP_MAJOR_VERSION = "v0.1"; # build number from svn revision

# icons put under APP_ICON_DIR/<target>, like ./Res/Icons/360/Icon-57.png"
APP_ICON_DIR = "/Res/Icons"

# actual target will be "/Target/<target>", like ./Target/ios, /Target/360, etc.
TARGET_DIR = "/Target"

# build package for every publish channels

TARGET_PACKAGES = {
    "ios" : { # apple app store
        "enabled": True,
        "platform": "ios",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo"
    },
    "android" : { # google play
        "enabled": True,
        "platform": "android",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo"
    },
    "360" : { # qihu 360
        "enabled": False,
        "platform": "android",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo.app360",
        "msmcs": "-define:FOR_360"
    },
    "xiaomi" : { # xiao mi
        "enabled": False,
        "platform": "android",
        "name" : "LMDemo",
        "id" : "com.uniq.LMDemo.mi",
        "msmcs": "-define:FOR_XIAOMI"
    }
}

# TODO: put all 3pp SDK appid/appkey here

SDK_3PP_IOS = {
    "QQ" : {
        "enabled" : False,
        "appid" : "tencent100703379",
        "appkey" : "4578e54fb3a1bd18e0681bc1c734514e"
    },
    "weixin" : {
        "enabled" : False,
        "appid" : "wx5923bbc6094cc763",
        "appkey" : "eea65831dbb5eb81439bcc2e1adb3dbc"
    },
    "tencentopenapi" : {
        "enabled" : False,
        "appid" : "QQ0600678E",
        "appkey" : ""
    },
    "dengta" : {
        "enabled" : False,
        "appid" : "1001",
        "appkey" : "0I4007GJN70PS0PW"
    }
}

SDK_3PP_ANDROID = {
    "QQ" : {
        "enabled" : False,
        "appid" : "tencent100703379",
        "appkey" : "4578e54fb3a1bd18e0681bc1c734514e"
    },
    "weixin" : {
        "enabled" : False,
        "appid" : "wx5923bbc6094cc763",
        "appkey" : "eea65831dbb5eb81439bcc2e1adb3dbc"
    }
}

# ----------------------------------------------
def PatchXcodeProject( project, buildMode ):
    # add System Framework
    project.add_file('System/Library/Frameworks/CoreTelephony.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/SystemConfiguration.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/UIKit.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/Foundation.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/CoreGraphics.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/CFNetwork.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/StoreKit.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/MobileCoreServices.framework', tree='SDKROOT')
    project.add_file('System/Library/Frameworks/AdSupport.framework', tree='SDKROOT',weak=True)
    
    project.add_file('usr/lib/libz.dylib', tree='SDKROOT')
    
    # modify other link flag, some SDK use auto reference counting but some project not, this link flag will cause duplicated error
    project.remove_other_ldflags('-all_load');
    
    # -fembed-bitcode is not supported on versions of iOS prior to 6.0
    # it's required by iWatch APP but optional for iOS
    project.remove_other_ldflags('-fembed-bitcode');

    return

# ----------------------------------------------
def PatchPlist( plist, buildMode ):
    # --- Allow HTTP ---
	# Apple made a radical decision with iOS 9, disabling all unsecured HTTP traffic from iOS apps, as a part of App Transport Security.
    plist['NSAppTransportSecurity'] = { 'NSAllowsArbitraryLoads':True }

    url_types = []
    
    # --- QQ ---
    QQ = SDK_3PP_IOS['QQ']
    if QQ != None and QQ['enabled']:
        need_msdk = True
        plist['QQAppID'] = QQ['appid'][7:]
        plist['QQAppKey'] = QQ['appkey']
        url_types.append({
                'CFBundleTypeRole':'Editor',
                'CFBundleURLName':'QQ',
                'CFBundleURLSchemes':[ QQ['appid'] ]})
    
    # -- QQ --
    weixin = SDK_3PP_IOS['weixin']
    if weixin != None and weixin['enabled']:
        need_msdk = True
        plist['WXAppID'] = weixin['appid']
        plist['WXAppKey'] = weixin['appkey']
        url_types.append({
                'CFBundleTypeRole':'Editor',
                'CFBundleURLName':'weixin',
                'CFBundleURLSchemes':[ weixin['appid'] ]})
    
    # -- Tencent MSDK ---
    tencentopenapi = build_config.SDK_3PP_IOS['tencentopenapi']
    dengta = SDK_3PP_IOS['dengta']
    if tencentopenapi != None and tencentopenapi['enabled']:
        need_msdk = True
        plist['CHANNEL_DENGTA'] = dengta['appid']
        plist['APPKEY_DENGTA'] = dengta['appkey']
        url_types.append({
                'CFBundleTypeRole':'Editor',
                'CFBundleURLName':'tencentopenapi',
                'CFBundleURLSchemes':[ tencentopenapi['appid'] ]})

    if need_msdk:
        if buildMode != "distribution":
            plist['MSDK_URL'] = "http://msdktest.qq.com"
        else:
            plist['MSDK_URL'] = "http://msdk.qq.com"

    # TODO: --- add more SDK content here ---
            
    if len(url_types) > 0:
        plist['CFBundleURLTypes'] = url_types
    
    return










