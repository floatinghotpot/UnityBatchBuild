#if UNITY_EDITOR

using UnityEngine;
using System.Collections;
using UnityEditor;

public class BatchBuildMenu {
	
	public static string[] SCENES = {
		// TODO: add your scene here

	};
	
	[MenuItem ("Tools/Build Android")]
	public static void BuildAndroid () {
		// TODO: Build streaming assets for Android

		BatchBuild.Build (
		                  BatchBuildConfig.APP_NAME, 
		                  BatchBuildConfig.APP_ID, 
		                  BatchBuildConfig.APP_VERSION, 
		                  BuildTarget.Android, 
		                  BuildOptions.Development | BuildOptions.ConnectWithProfiler);
	} 
	
	[MenuItem ("Tools/Build IOS")]
	public static void BuildIOS () {
		// TODO: Build streaming assets for iOS

		BatchBuild.Build (
		                  BatchBuildConfig.APP_NAME, 
		                  BatchBuildConfig.APP_ID, 
		                  BatchBuildConfig.APP_VERSION, 
		                  BatchBuild.BuildTarget_iOS, 
		                  BuildOptions.Development | BuildOptions.ConnectWithProfiler);
	}
	
	[MenuItem ("Tools/Build WP8")]
	public static void BuildWP8() {
		// TODO: Build streaming assets for WP8

		BatchBuild.Build (
		                  BatchBuildConfig.APP_NAME, 
		                  BatchBuildConfig.APP_ID, 
		                  BatchBuildConfig.APP_VERSION, 
		                  BuildTarget.WP8Player, 
		                  BuildOptions.Development | BuildOptions.ConnectWithProfiler);
	}

	[MenuItem ("Tools/Build Current Configured")]
	public static void BuildConfig() {
		switch (BatchBuildConfig.PLATFORM) {
		case "ios":
			BuildIOS();
			break;
		case "android":
			BuildAndroid();
			break;
		case "wp8":
			BuildWP8();
			break;
		default:
			break;
		}
	}
}

#endif
