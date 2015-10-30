#if UNITY_EDITOR

using UnityEngine;
using UnityEditor;
using System.Collections;
using System.Collections.Generic;
using System;
using System.IO;

public class BatchBuild : MonoBehaviour {
	// --- common constants ---
	
	#if (UNITY_4_6 || UNITY_4_7 || UNITY_4_8)
	public static BuildTarget BuildTarget_iOS = BuildTarget.iPhone;
	public static BuildTargetGroup BuildTargetGroup_iOS = BuildTargetGroup.iPhone;
	#else
	public static BuildTarget BuildTarget_iOS = BuildTarget.iOS;
	public static BuildTargetGroup BuildTargetGroup_iOS = BuildTargetGroup.iOS;
	#endif

	public static void Build(string appName, string packageId, string version, BuildTarget target, BuildOptions options) {
		string ProjPath = Application.dataPath.Replace("/Assets", "");
		string target_dir = ProjPath + BatchBuildConfig.TARGET_DIR;

		string locationPath = null;
		BuildTargetGroup targetGroup = BuildTargetGroup.Unknown;

		if (target == BuildTarget.Android) {
			locationPath = target_dir + "/" + appName + ".apk";
			targetGroup = BuildTargetGroup.Android;

		} else if (target == BatchBuild.BuildTarget_iOS) {
			locationPath = target_dir;
			targetGroup = BatchBuild.BuildTargetGroup_iOS;

		} else if (target == BuildTarget.WP8Player) {
			locationPath = target_dir;
			targetGroup = BuildTargetGroup.WP8;

		} else {
			Debug.LogError("No plan to support this platform yet.");
			return;
		}
		
		PlayerSettings.bundleIdentifier = packageId;
		PlayerSettings.bundleVersion = version;
		for(int i=0; i<BatchBuildConfig.DEFINE_MACRO.Length; i++) {
			PlayerSettings.SetScriptingDefineSymbolsForGroup(targetGroup, BatchBuildConfig.DEFINE_MACRO);
		}
		
		// Clean previous build
		try {
			if (Directory.Exists(target_dir)) {
				Directory.Delete(target_dir, true);
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
		string res = BuildPipeline.BuildPlayer(BatchBuildMenu.SCENES, locationPath, target, options);   
		if (res.Length > 0)  {
			throw new Exception("BuildPlayer failure: " + res);
			return;
		}
	}
}

#endif
