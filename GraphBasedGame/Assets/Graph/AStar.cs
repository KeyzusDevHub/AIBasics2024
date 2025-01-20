using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using static UnityEngine.RuleTile.TilingRuleOutput;

public class AStar : MonoBehaviour {
    [HideInInspector]
    public FloodingGraph f_graph;
    Dictionary<Node, Node> pathConnections = new Dictionary<Node, Node>();

    public List<Node> FindPath(Node startNode, Node endNode) {
        Dictionary<Node, float> gCosts = new Dictionary<Node, float>();
        Dictionary<Node, float> hCosts = new Dictionary<Node, float>();
        Dictionary<Node, float> fCosts = new Dictionary<Node, float>();
        Vector3 destPos = endNode.transform.position;

        pathConnections.Clear();

        foreach (Node node in f_graph.GetAllNodes()) {
            gCosts[node] = float.MaxValue;
            hCosts[node] = float.MaxValue;
        }

        List<Node> openSet = new List<Node>();
        HashSet<Node> closedSet = new HashSet<Node>();
        gCosts[startNode] = 0;
        Vector3 sNodePos = startNode.transform.position;
        hCosts[startNode] = Mathf.Abs(sNodePos.x - destPos.x) - Mathf.Abs(sNodePos.y - destPos.y); ;
        openSet.Add(startNode);

        while (openSet.Count > 0) {
            Node currentNode = openSet.OrderBy(n => Mathf.Max(gCosts[n], hCosts[n], gCosts[n] + hCosts[n])).First();
            openSet.Remove(currentNode);
            closedSet.Add(currentNode);

            if (currentNode.Equals(endNode)) {
                return RetracePath(startNode, endNode);
            }

            foreach (Node neighbor in GetNeighbors(currentNode)) {
                if (closedSet.Contains(neighbor))
                    continue;

                float newCostToNeighbor = gCosts[currentNode] + Vector3.Distance(currentNode.transform.position,
                                                                                    neighbor.transform.position);

                if (newCostToNeighbor < gCosts[neighbor]) {
                    gCosts[neighbor] = newCostToNeighbor;
                    Vector3 neighPos = neighbor.transform.position;
                    hCosts[neighbor] = Mathf.Abs(neighPos.x - destPos.x) - Mathf.Abs(neighPos.y - destPos.y);
                    pathConnections[neighbor] = currentNode;

                    if (!openSet.Contains(neighbor)) {
                        openSet.Add(neighbor);
                    }
                }
            }
        }
        Debug.Log("CRITICAL ERROR NO PATH!");
        return new List<Node>();
    }

    List<Node> RetracePath(Node startNode, Node endNode) {
        List<Node> path = new List<Node>();
        Node currentNode = endNode;

        while (currentNode != startNode) {
            path.Add(currentNode);
            currentNode = pathConnections[currentNode];
        }
        path.Reverse();
        if (path.Count <= 1) {
            Debug.Log("CRITICAL ERROR EMPTY REVERSE!");
        }
        return path;
    }

    List<Node> GetNeighbors(Node node) {
        return node.getNeighbours();
    }
}

