using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;

public class Bullet : MonoBehaviour
{
    [HideInInspector]
    public ColliderChecks checks = null;
    [HideInInspector]
    public FloodingGraph floodingGraph = null;
    private List<Agent> agents = new List<Agent>();
    private float liveTime = 1.0f;

    public void initialize(Agent shooter, Vector3 dir) {
        agents = floodingGraph.GetAgentsExcept(shooter);
        bool hit = false;
        Vector3 startPoint = shooter.transform.position;
        Vector3 endPoint = Vector3.zero;
        foreach (Agent agent in agents) {
            if (agent != null && agent.WasHit(startPoint, dir)) {
                agent.Hit();
                endPoint = checks.PolygonLineCollisionPoint(agent.GetComponent<PolygonCollider2D>(), startPoint, startPoint + dir * 20f, true);
                hit = true;
                break;
            }
        }
        if (!hit) {
            endPoint = checks.ObstaclesLineCollisionPoint(startPoint, startPoint + dir * 20f);
        }
        Vector3 meshScale = new Vector3(0.03f, 0.03f, 0f);
        Vector3 perpVec = new Vector3(dir.y, -dir.x, 0f);
        Vector3 meshTranslate = new Vector3((meshScale.x * perpVec.x) / 2f, (meshScale.y * perpVec.y) / 2f, 0f);
        Mesh mesh = new Mesh();
        Vector3[] vertices = new Vector3[] {startPoint - meshTranslate, startPoint + meshTranslate, endPoint + meshTranslate,  endPoint - meshTranslate };
        int[] triangles = new int[] { 0, 1, 2, 0, 2, 3 };
        mesh.vertices = vertices;
        mesh.triangles = triangles;
        GetComponent<MeshFilter>().mesh = mesh;
    }
    void Update()
    {
        liveTime -= Time.deltaTime;
        if (liveTime < 0) { 
            Destroy(gameObject);
        }
    }

}
