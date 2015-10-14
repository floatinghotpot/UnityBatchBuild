
#if UNITY_EDITOR

using UnityEngine;
using System.Collections;
using UnityEditor;
using System;

public class BatchBuild : MonoBehaviour {
	[MenuItem("Tools/Build/Test")]
	public static void Test() {
		Debug.Log ("BatchBuildTest");
	}

	// Use this for initialization
	void Start () {
	
	}
	
	// Update is called once per frame
	void Update () {
	
	}
}

#endif
