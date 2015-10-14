#if UNITY_EDITOR

using UnityEngine;
using System.Collections;
using UnityEditor;

public class BatchBuildConfig {

	public static string[] SCENES = {
		// add your scene here
	};
	
	public static string XCODEBUILD_CLI = "/usr/bin/Xcodebuild";
	
	public static string PROJECT_PATH = Application.dataPath.Replace("/Assets", "");

	public static string TARGET_PATH = PROJECT_PATH + "/Target";
	public static string TARGET_PATH_ANDROID = TARGET_PATH + "/android";
	public static string TARGET_PATH_IOS = TARGET_PATH + "/ios";
	public static string TARGET_PATH_WP8 = TARGET_PATH + "/wp8";

	public static string SCRIPT_DEFINE_SYMBOL = "LM";
	
	public static string[] SMCS_MODES = {
		"-define:DEV_VERSION;EnableChinese;",    // debug
	    "-define:RELEASE_VERSION;EnableChinese;",   //release or daily
		"-define:DISTRIBUTION_VERSION;EnableChinese;CODESTRIPPER;" //distribution
	};

	public static string[] PROVISION_CER = {
		// change to your own provisioning file and certificate
		"com.company.app",
		"420a97b6-99ea-48f9-ac2b-5c5032e0ea66",
		"iPhone Developer: Your Name (GA52LZZ6A3)"
	};

}

#endif
