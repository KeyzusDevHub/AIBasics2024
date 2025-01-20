using JetBrains.Annotations;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor.Experimental.GraphView;
using UnityEngine;

public class FloodingGraph : MonoBehaviour {
    [Header("Prefabs")]
    public Node nodePrefab;
    public Agent agentPrefab;
    public GameObject healPrefab;
    public GameObject ammoPrefab;
    public GameObject armorPrefab;
    [Header("GraphData")]
    public Node startingPoint;
    public float nodeSpacing = 0.2f;
    public float nodeRadius = 0.1f;
    public int boostSpawnLimit = 2;
    public float minimalBoostDistance = 3f;
    public ColliderChecks colliderChecks;
    public GameObject boostAreas;
    public GameObject spawnAreas;

    [HideInInspector]
    public List<Node> nodes = new List<Node>();
    [HideInInspector]
    public List<Boost> armorPoints = new List<Boost>();
    [HideInInspector]
    public List<Boost> healPoints = new List<Boost>();
    [HideInInspector]
    public List<Boost> ammoPoints = new List<Boost>();
    [HideInInspector]
    public List<Node> spawnPoints = new List<Node>();

    List<BoxCollider2D> boostSpawnAreas = new List<BoxCollider2D>();
    List<BoxCollider2D> agentSpawnAreas = new List<BoxCollider2D>();

    List<Agent> spawnedAgents = new List<Agent>();

    // Start is called before the first frame update
    void Start() {
        boostSpawnAreas = new List<BoxCollider2D>(boostAreas.GetComponentsInChildren<BoxCollider2D>());
        agentSpawnAreas = new List<BoxCollider2D>(spawnAreas.GetComponentsInChildren<BoxCollider2D>());
        nodes.Add(startingPoint);
        List<Node> createdNodes = FloodGraph(startingPoint);
        while (createdNodes.Count != 0) {
            List<Node> newNodes = new List<Node>();
            foreach (Node node in createdNodes) {
                newNodes.AddRange(FloodGraph(node));
            }
            createdNodes = newNodes;
        }
        GenerateBoosts();
        GenerateSpawnPoints();
        SpawnAgents();
    }

    private void OnDrawGizmosSelected() {
        Gizmos.color = Color.yellow;
        foreach (Node node in nodes) {
            Gizmos.DrawSphere(node.transform.position, 0.05f);
            foreach (Node neighbour in node.getNeighbours()) {
                Gizmos.DrawLine(node.transform.position, neighbour.transform.position);
            }
        }
    }

    Node CreateNode(Vector3 position) {
        Node newNode = Instantiate(nodePrefab, transform);
        newNode.transform.localPosition = position;
        nodes.Add(newNode);
        return newNode;
    }

    public Node FindNodeByPosition(Vector3 position) {
        foreach (Node node in nodes) {
            Vector3 existingPosition = node.transform.position;
            if (Vector3.Distance(position, existingPosition) <= nodeRadius) {
                return node;
            }
        }
        return null;
    }

    public Node GetRandomNode() {
        if (nodes.Count > 0) {
            return nodes[Random.Range(0, nodes.Count)];
        }
        return null;
    }

    public List<Node> GetAllNodes() {
        return nodes;
    }

    public List<Agent> GetAgentsExcept(Agent agent) {
        List<Agent> list = new List<Agent>();
        foreach (Agent a in spawnedAgents) {
            if (!agent.Equals(a)) {
                list.Add(a);
            }
        }
        return list;
    }

    List<Node> FloodGraph(Node node) {
        Vector3 startPosition = node.transform.localPosition;
        List<Node> createdNodes = new List<Node>();

        Vector3[] directions = new Vector3[]
        {
            Vector3.up * nodeSpacing,
            Vector3.down * nodeSpacing,
            Vector3.left * nodeSpacing,
            Vector3.right * nodeSpacing,
            (Vector3.left + Vector3.down) * nodeSpacing,
            (Vector3.right + Vector3.down) * nodeSpacing,
            (Vector3.left + Vector3.up) * nodeSpacing,
            (Vector3.right + Vector3.up) * nodeSpacing
        };

        foreach (Vector3 direction in directions) {
            Vector3 newPosition = startPosition + direction;

            if (!IsObstaclePresent(newPosition) && !IsWithinRange(newPosition)) {
                Node newNode = CreateNode(newPosition);
                newNode.addNeighbour(node);
                node.addNeighbour(newNode);
                createdNodes.Add(newNode);
            }
            else if (IsWithinRange(newPosition)) {
                Node newNode = FindNodeByPosition(newPosition);
                newNode.addNeighbour(node);
                node.addNeighbour(newNode);
            }
        }
        return createdNodes;
    }

    public Node FindBoostClosestTo(string boostName, Vector3 position) {
        List<Boost> boosts = null;
        if (boostName == "Heal") {
            boosts = healPoints;
        }
        else if (boostName == "Ammo") {
            boosts = ammoPoints;
        }
        else if (boostName == "Armor") {
            boosts = armorPoints;
        }
        Boost closest = boosts[0];
        float closestDist = float.MaxValue;
        foreach (Boost boost in boosts) {
            if (boost.IsCollected()) {
                continue;
            }
            float dist = Vector3.Distance(boost.transform.position, position);
            if (dist < closestDist) {
                closest = boost;
                closestDist = dist;
            }
        }

        return FindNodeClosestTo(closest.transform.position);
    }

    public Node FindNodeClosestTo(Vector3 position) {
        Node closest = null;
        float closestDist = float.MaxValue;
        foreach (Node node in nodes) {
            float dist = Vector3.Distance(position, node.transform.position);
            if (dist < closestDist) {
                closest = node;
                closestDist = dist;
            }
        }
        return closest;
    }

    public Node FindPointFurthestTo(List<Vector3> positions) {
        Node furthest = null;
        float furthestDist = 0;
        foreach (Node node in nodes) {
            float dist = 0;
            foreach (Vector3 position in positions) {
                dist += Vector3.Distance(position, node.transform.position);
            }
            if (dist > furthestDist) {
                furthest = node;
                furthestDist = dist;
            }
        }
        return furthest;
    }

    public Node FindPointOnOtherSide(List<Vector3> positions) {
        Vector3 closestEnemy = positions.OrderBy(n => Mathf.Min(Vector3.Distance(n, transform.position))).First();
        if (closestEnemy == Vector3.zero) {
            return FindPointFurthestTo(positions);
        }
        float x = 0;
        float y = 0;
        if (Mathf.Sign(transform.position.x) == Mathf.Sign(closestEnemy.x) || Mathf.Sign(transform.position.y) == Mathf.Sign(closestEnemy.y)) {
            x = Mathf.Sign(closestEnemy.x);
            y = -Mathf.Sign(closestEnemy.y);
        }
        else {
            x = -Mathf.Sign(closestEnemy.x);
            y = -Mathf.Sign(closestEnemy.y);
        }
        Node furthest = null;
        float furthestDist = 0;
        foreach (Node node in nodes) {
            if (Mathf.Sign(node.transform.position.x) != x && Mathf.Sign(node.transform.position.y) != y) {
                continue;
            }
            float dist = 0;
            foreach (Vector3 position in positions) {
                dist += Vector3.Distance(position, node.transform.position);
            }
            if (dist > furthestDist) {
                furthest = node;
                furthestDist = dist;
            }
        }
        return furthest;
    }

    public void RespawnAgent(Agent agent) {
        spawnedAgents.Remove(agent);
        Node safestNode = null;
        float furthestDist = 0;
        foreach (Node node in spawnPoints) {
            float dist = 0;
            foreach (Agent enemy in spawnedAgents) {
                dist += Vector3.Distance(enemy.transform.position, node.transform.position);
            }
            if (dist > furthestDist) {
                furthestDist = dist;
                safestNode = node;
            }
        }
        Agent newAgent = Instantiate(agentPrefab, safestNode.transform.position, Quaternion.identity);
        newAgent.GetComponent<SteeringBehaviors>().floodingGraph = this;
        newAgent.GetComponent<SteeringBehaviors>().aStar = GetComponent<AStar>();
        newAgent.colliderChecks = colliderChecks;
        newAgent.GetComponent<SteeringBehaviors>().initialize();
        spawnedAgents.Add(newAgent);

    }

    public void PropagateShot(Agent agent) {
        foreach (Agent a in spawnedAgents) {
            if (a != null && !a.Equals(agent)) {
                a.ReactToShot(agent);
            }
        }
    }

    public bool CheckBoostPositions(Vector3 position) {
        List<Boost> allBoosts = new List<Boost>();
        allBoosts.AddRange(healPoints);
        allBoosts.AddRange(ammoPoints);
        allBoosts.AddRange(armorPoints);
        foreach (Boost b in allBoosts) {
            if (Vector3.Distance(b.transform.position, position) > nodeRadius && !b.IsCollected()) {
                return true;
            }
        }
        return false;
    }

    public bool IsAnyBoostOnMap(string boostName) {
        List<Boost> boosts = new List<Boost>();
        if (boostName == "Ammo") {
            boosts = ammoPoints;
        }
        else if (boostName == "Heal") {
            boosts = healPoints;
        }
        else if (boostName == "Armor") {
            boosts = armorPoints;
        }

        foreach (Boost b in boosts) {
            if (!b.IsCollected()) {
                return true;
            }
        }
        return false;
    }

    public string CollectBoost(Vector3 position) {
        foreach (Boost b in healPoints) {
            if (Vector3.Distance(b.transform.position, position) <= nodeRadius && !b.IsCollected()) {
                b.Collect();
                return "Heal";
            }
        }
        foreach (Boost b in armorPoints) {
            if (Vector3.Distance(b.transform.position, position) <= nodeRadius && !b.IsCollected()) {
                b.Collect();
                return "Armor";
            }
        }
        foreach (Boost b in ammoPoints) {
            if (Vector3.Distance(b.transform.position, position) <= nodeRadius && !b.IsCollected()) {
                b.Collect();
                return "Ammo";
            }
        }
        return "None";
    }

    public string CheckBoostPosition(Vector3 position) {
        foreach (Boost b in healPoints) {
            if (Vector3.Distance(b.transform.position, position) <= nodeRadius && !b.IsCollected()) {
                return "Heal";
            }
        }
        foreach (Boost b in armorPoints) {
            if (Vector3.Distance(b.transform.position, position) <= nodeRadius && !b.IsCollected()) {
                return "Armor";
            }
        }
        foreach (Boost b in ammoPoints) {
            if (Vector3.Distance(b.transform.position, position) <= nodeRadius && !b.IsCollected()) {
                return "Ammo";
            }
        }
        return "None";
    }

    bool IsObstaclePresent(Vector3 position) {
        return colliderChecks.ObstaclesCircleCollision(position, nodeRadius);
    }

    bool IsWithinRange(Vector3 newPosition) {
        foreach (Node node in nodes) {
            Vector3 existingPosition = node.transform.position;

            if (Vector3.Distance(newPosition, existingPosition) <= nodeRadius) {
                return true;
            }
        }

        return false;
    }

    void GenerateBoosts() {
        List<string> boostNames = new List<string> { "Armor", "Heal", "Ammo" };
        List<string> allSpawnedBoosts = new List<string>();
        foreach (BoxCollider2D area in boostSpawnAreas) {
            List<string> spawnedBoosts = new List<string>();
            List<Node> spawnedPosition = new List<Node>();
            List<Node> nodes = PointsInArea(area);
            while (spawnedBoosts.Count != 2) {
                List<Node> leftPositions = nodes.Except(spawnedPosition).ToList();
                Node randomNode = GetRandomElementFromList(nodes);
                if (IsBoostInRange(randomNode)) {
                    continue;
                }
                List<string> leftToSpawn = boostNames.Except(spawnedBoosts).ToList();
                string randomBoost = GetRandomElementFromList(leftToSpawn);
                GameObject b = InstantiateNewBoost(randomNode, randomBoost);
                b.transform.SetParent(area.transform, true);
                AddBoostToList(randomBoost, b);
                spawnedBoosts.Add(randomBoost);
                spawnedPosition.Add(randomNode);
                allSpawnedBoosts.Add(randomBoost);
                boostNames = UpdateBoostNames(allSpawnedBoosts);
            }
        }

    }

    void AddBoostToList(string boostName, GameObject boost) {
        Boost b = boost.GetComponent<Boost>();
        if (boostName == "Ammo") {
            ammoPoints.Add(b);
        }
        else if (boostName == "Armor") {
            armorPoints.Add(b);
        }
        else if (boostName == "Heal") {
            healPoints.Add(b);
        }
    }

    bool IsBoostInRange(Node node) {
        Vector3 position = node.transform.position;
        List<Boost> allBoosts = new List<Boost>();
        allBoosts.AddRange(healPoints);
        allBoosts.AddRange(ammoPoints);
        allBoosts.AddRange(armorPoints);

        foreach (Boost b in allBoosts) {
            Vector3 boostPosition = b.transform.position;
            if (Vector3.Distance(position, boostPosition) < minimalBoostDistance) {
                return true;
            }
        }
        return false;
    }

    List<string> UpdateBoostNames(List<string> allSpawnedBoosts) {
        List<string> updatedBoostNames = new List<string>();
        int ammoCount = allSpawnedBoosts.Count(x => x == "Ammo");
        int healCount = allSpawnedBoosts.Count(x => x == "Heal");
        int armorCount = allSpawnedBoosts.Count(x => x == "Armor");

        if (ammoCount + healCount + armorCount == 3) {
            if (ammoCount == 0) {
                updatedBoostNames.Add("Ammo");
            }
            else if (healCount == 0) {
                updatedBoostNames.Add("Heal");
            }
            else if (armorCount == 0) {
                updatedBoostNames.Add("Armor");
            }
            if (updatedBoostNames.Count > 0) { 
                return updatedBoostNames;
            }
        }

        if (ammoCount < boostSpawnLimit) {
            updatedBoostNames.Add("Ammo");
        }
        if (healCount < boostSpawnLimit) {
            updatedBoostNames.Add("Heal");
        }
        if (armorCount < boostSpawnLimit) {
            updatedBoostNames.Add("Armor");
        }
        return updatedBoostNames;
    }

    GameObject InstantiateNewBoost(Node randomNode, string randomBoost) {
        GameObject spawnedBoost = null;
        Vector3 position = randomNode.transform.position;

        if (randomBoost == "Armor") {
            spawnedBoost = Instantiate(armorPrefab, position, Quaternion.identity);
            armorPoints.Add(spawnedBoost.GetComponent<Boost>());
        }
        else if (randomBoost == "Heal") {
            spawnedBoost = Instantiate(healPrefab, position, Quaternion.identity);
            healPoints.Add(spawnedBoost.GetComponent<Boost>());
        }
        else if (randomBoost == "Ammo") {
            spawnedBoost = Instantiate(ammoPrefab, position, Quaternion.identity);
            ammoPoints.Add(spawnedBoost.GetComponent<Boost>());
        }
        return spawnedBoost;
    }

    T GetRandomElementFromList<T>(List<T> list) {
        int randomIndex = Random.Range(0, list.Count);
        return list[randomIndex];
    }

    void GenerateSpawnPoints() {
        foreach (BoxCollider2D area in agentSpawnAreas) {
            List<Node> nodes = PointsInArea(area);
            Node randomNode = GetRandomElementFromList(nodes);
            spawnPoints.Add(randomNode);
        }
    }

    void SpawnAgents() {
        foreach (Node node in spawnPoints) {
            Agent agent = Instantiate(agentPrefab, node.transform.position, Quaternion.identity);
            agent.GetComponent<SteeringBehaviors>().floodingGraph = this;
            agent.GetComponent<SteeringBehaviors>().aStar = GetComponent<AStar>();
            agent.colliderChecks = colliderChecks;
            agent.GetComponent<SteeringBehaviors>().initialize();
            spawnedAgents.Add(agent);
        }
    }

    List<Node> PointsInArea(BoxCollider2D area) {
        List<Node> points = new List<Node>();
        foreach (Node node in nodes) {
            if (PointInArea(area, node.transform.position)) {
                points.Add(node);
            }
        }
        return points;
    }
    
    bool PointInArea(BoxCollider2D area, Vector3 point) {
        Vector3 corner1 = area.bounds.min;
        Vector3 corner2 = area.bounds.max;

        float minX = Mathf.Min(corner1.x, corner2.x);
        float maxX = Mathf.Max(corner1.x, corner2.x);
        float minY = Mathf.Min(corner1.y, corner2.y);
        float maxY = Mathf.Max(corner1.y, corner2.y);

        return point.x >= minX && point.x <= maxX && point.y >= minY && point.y <= maxY;
    }
}

