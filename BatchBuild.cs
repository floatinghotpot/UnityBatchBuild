﻿
#if UNITY_EDITOR

using UnityEngine;
using UnityEditor;
using System.Collections;
using System.Collections.Generic;
using System;
using System.IO;

public class BatchBuild : MonoBehaviour {
	
	// Use this for initialization
	void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
		
	}

	public static void Build(string appName, string packageId, string version, BuildTarget target, BuildOptions options) {
		string target_dir = null;
		string locationPath = null;
		BuildTargetGroup targetGroup = BuildTargetGroup.Unknown;

		if (target == BuildTarget.Android) {
			target_dir = BatchBuildConfig.TARGET_PATH_ANDROID;
			locationPath = target_dir + "/" + appName + ".apk";
			targetGroup = BuildTargetGroup.Android;

		} else if (target == BuildTarget.iOS) {
			target_dir = BatchBuildConfig.TARGET_PATH_IOS; 
			locationPath = target_dir;
			targetGroup = BuildTargetGroup.iOS;

		} else if (target == BuildTarget.WP8Player) {
			target_dir = BatchBuildConfig.TARGET_PATH_WP8;
			locationPath = target_dir;
			targetGroup = BuildTargetGroup.WP8;

		} else {
			Debug.LogError("No plan to support this platform yet.");
			return;
		}
		
		PlayerSettings.bundleIdentifier = packageId;
		PlayerSettings.bundleVersion = version;
		PlayerSettings.SetScriptingDefineSymbolsForGroup(targetGroup, BatchBuildConfig.SCRIPT_DEFINE_SYMBOL);
		
		// Clean previous build
		try {
			if (Directory.Exists(target_dir)) {
				Directory.Delete(target_dir, true);
			}

			if(! Directory.Exists(BatchBuildConfig.TARGET_PATH)) {
				Directory.CreateDirectory(BatchBuildConfig.TARGET_PATH);
			}
			
			Directory.CreateDirectory(target_dir); 
			
		} catch (Exception ex) {
			Debug.LogError(ex.Message);
		}
		
		// switch active build target
		string strTarget = EditorUserBuildSettings.activeBuildTarget.ToString();
		if(! strTarget.Equals(target.ToString())) {
			EditorUserBuildSettings.SwitchActiveBuildTarget(target); 
		}
		
		// build pipeline
		string res = BuildPipeline.BuildPlayer(BatchBuildConfig.SCENES, locationPath, target, options);   
		if (res.Length > 0)  {
			throw new Exception("BuildPlayer failure: " + res);
			return;
		}
		
		#if UNITY_EDITOR_OSX
		if (target == BuildTarget.iOS) {
			XcodeBuild.PatchAndBuild(target, locationPath);
		}
		#endif
	}
}

#endif
