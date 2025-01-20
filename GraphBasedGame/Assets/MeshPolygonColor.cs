using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MeshPolygonColor : MonoBehaviour
{
    void Start() {
        MeshFilter filter = GetComponent<MeshFilter>();
        Mesh mesh = GetComponent<PolygonCollider2D>().CreateMesh(true, true);
        filter.mesh = mesh;
    }
}
