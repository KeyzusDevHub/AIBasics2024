using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SteeringBehaviors : MonoBehaviour {
    [HideInInspector]
    public AStar aStar;
    [HideInInspector]
    public FloodingGraph floodingGraph;
    [HideInInspector]
    public List<Node> path = new List<Node>();
    [HideInInspector]
    public Agent steeredAgent;
    public float viewAngle = 45f;
    public float agentSpeed = 0.5f;
    public float agentRotation = 180f;
    public float attackCloseRange = 2f;
    float lastChasePath = 0f;
    float tolerance;
    Node currentNode;
    bool isHiding = false;
    Agent hidingFrom = null;

    public void initialize() {
        aStar = GetComponent<AStar>();
        aStar.f_graph = floodingGraph;
        steeredAgent = GetComponent<Agent>();
        path = aStar.FindPath(floodingGraph.FindNodeByPosition(transform.position), floodingGraph.GetRandomNode());
        currentNode = path[0];
        tolerance = floodingGraph.nodeRadius / 2f;
    }

    public bool isCloseTo(Vector3 pos) {
        return Vector3.Distance(pos, transform.position) <= tolerance;
    }

    public bool RotateTowards(Vector3 pos) {
        float step = agentRotation * Time.deltaTime;
        Vector3 targetDirection = pos - transform.position;

        float targetAngle = Mathf.Atan2(targetDirection.y, targetDirection.x) * Mathf.Rad2Deg - 90f;
        targetAngle = Mathf.Round(targetAngle);

        if (targetAngle < 0) {
            targetAngle = 360 + targetAngle;
        }

        float newAngle = Mathf.MoveTowardsAngle(transform.eulerAngles.z, targetAngle, step);
        transform.rotation = Quaternion.Euler(0, 0, newAngle);

        return Mathf.Abs(targetAngle - transform.eulerAngles.z) <= 30f;

    }

    public Vector3 Seek(Vector3 pos) {
        Vector3 direction = (pos - transform.position).normalized;
        if (direction == Vector3.zero) {
            Debug.Log("CRITICAL SEEK ERROR");
        }
        return direction;
    }

    public void Hide(List<Agent> visibleAgents) {
        List<Vector3> agentsPositions = new List<Vector3>();
        foreach (var agent in visibleAgents) {
            agentsPositions.Add(agent.transform.position);
        }
        if (isHiding && hidingFrom == visibleAgents[0]) {
            return;
        }
        path = aStar.FindPath(floodingGraph.FindNodeClosestTo(transform.position), floodingGraph.FindPointOnOtherSide(agentsPositions));
        isHiding = true;
        hidingFrom = visibleAgents[0];
    }

    public void Attack(List<Agent> visibleAgents) {
        Agent toAttack = visibleAgents[0];
        ColliderChecks cc = GetComponent<Agent>().colliderChecks;
        if (!cc.ObstaclesLineCollision(transform.position, toAttack.transform.position)) {
            currentNode = floodingGraph.FindNodeClosestTo(transform.position);
            path = new List<Node> { currentNode, currentNode };
            RotateTowards(toAttack.transform.position);
        }
        else if (lastChasePath > 1f || path.Count <= 2){
            path = aStar.FindPath(floodingGraph.FindNodeClosestTo(transform.position), floodingGraph.FindNodeClosestTo(toAttack.transform.position));
            currentNode = path[0];
            lastChasePath = 0.0f;
        }
        isHiding = false;
    }

    public void Heal() {
        if (floodingGraph.CheckBoostPosition(path[path.Count - 1].transform.position) == "Heal") {
            return;
        }
        path = aStar.FindPath(floodingGraph.FindNodeClosestTo(transform.position),
                              floodingGraph.FindBoostClosestTo("Heal", transform.position));
        currentNode = path[0];
        isHiding = false;
    }

    public void Armor() {
        if (floodingGraph.CheckBoostPosition(path[path.Count - 1].transform.position) == "Armor") {
            return;
        }
        path = aStar.FindPath(floodingGraph.FindNodeClosestTo(steeredAgent.transform.position), 
                              floodingGraph.FindBoostClosestTo("Armor", transform.position));
        currentNode = path[0];
        isHiding = false;
    }

    public void Ammo() {
        if (floodingGraph.CheckBoostPosition(path[path.Count - 1].transform.position) == "Ammo") {
            return;
        }
        path = aStar.FindPath(floodingGraph.FindNodeClosestTo(steeredAgent.transform.position), 
                              floodingGraph.FindBoostClosestTo("Ammo", transform.position));
        currentNode = path[0];
        isHiding = false;
    }

    public void RandomWalk() {
        if (currentNode == null) {
            path = aStar.FindPath(floodingGraph.FindNodeByPosition(steeredAgent.transform.position), floodingGraph.GetRandomNode());
        }
        else {
            path = aStar.FindPath(currentNode, floodingGraph.GetRandomNode());
        }
        currentNode = path[0];
        isHiding = false;
    }

    public void getNextPosition() {
        path.Remove(currentNode);
        if (floodingGraph.CheckBoostPositions(transform.position)) {
            steeredAgent.CollectBoost();
        }

        if (path.Count > 0) {
            currentNode = path[0];
        }
        else {
            currentNode = null;
            RandomWalk();
        }
    }

    public Vector3 getNewVelocity(State currentState) {
        if (currentNode == null) {
            Debug.Log("CRITICAL ERROR NULL!");
            return Vector3.zero;
        }
        if (!isCloseTo(currentNode.transform.position) && RotateTowards(currentNode.transform.position)) {
            return Seek(currentNode.transform.position) * agentSpeed;
        }
        else if (isCloseTo(currentNode.transform.position)) {
            getNextPosition();
        }
        return Vector3.zero;
    }

    void OnDrawGizmosSelected() {
        Gizmos.color = Color.red;
        Gizmos.DrawLine(transform.position, transform.position + transform.up * 1f);
        Gizmos.color = Color.magenta;
        Gizmos.DrawLine(transform.position, transform.position + Quaternion.AngleAxis(viewAngle, transform.forward) * transform.up * 10);
        Gizmos.DrawLine(transform.position, transform.position + Quaternion.AngleAxis(-viewAngle, transform.forward) * transform.up * 10);

        Gizmos.color = Color.green;
        foreach (Node node in path) {
            Gizmos.DrawSphere(node.transform.position, 0.05f);
        }
        for (int i = 0; i < path.Count - 1; i++) {
            Gizmos.DrawLine(path[i].transform.position, path[i + 1].transform.position);
        }
    }

    private void Update() {
        lastChasePath += Time.deltaTime;
    }

}
