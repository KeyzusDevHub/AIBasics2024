using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Node : MonoBehaviour
{
    List<Node> neighbours = new List<Node>();

    public void addNeighbour(Node node)
    {
        neighbours.Add(node);
    }

    public List<Node> getNeighbours()
    {
        return neighbours;
    }

    public override bool Equals(object obj)
    {
        if (obj == null || GetType() != obj.GetType())
            return false;

        Node other = (Node)obj;

        return transform.position == other.transform.position;
    }
    public override int GetHashCode()
    {
        return transform.GetHashCode();
    }
}
