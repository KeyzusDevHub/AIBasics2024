using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class ColliderChecks : MonoBehaviour
{
    List<PolygonCollider2D> colliders;

    private void Awake() {
        colliders = new List<PolygonCollider2D>(GetComponentsInChildren<PolygonCollider2D>());
    }
    public bool ObstaclesCircleCollision(Vector3 circleCenter, float circleRadius) {
        foreach (var collider in colliders) {
            if (PolygonCircleCollision(collider, circleCenter, circleRadius)) {
                return true;
            }
        }
        return false;
    }

    public bool ObstaclesLineCollision(Vector3 lineStart, Vector3 lineEnd) {
        foreach (var collider in colliders) {
            if (PolygonLineCollision(collider, lineStart, lineEnd)) {
                return true;
            }
        }
        return false;
    }

    public Vector3 ObstaclesLineCollisionPoint(Vector3 lineStart, Vector3 lineEnd) {
        List<Vector3> points = new List<Vector3>();
        foreach (var collider in colliders) {
            Vector3 point = PolygonLineCollisionPoint(collider, lineStart, lineEnd);
            if (point != Vector3.negativeInfinity) {
                points.Add(point);
            }
        }
        if (points.Count == 0) {
            Debug.Log("OLCP ERROR");
        }
        return points.OrderBy(x => Vector3.Distance(lineStart, x)).First();
    }

    public bool PolygonLineCollision(PolygonCollider2D collider, Vector3 lineStart, Vector3 lineEnd, bool isMoveable = false) {

        List<Vector2> polygonPoints = new List<Vector2>(collider.points);

        for (int i = 0; i < collider.pathCount; i++) {
            polygonPoints.AddRange(collider.GetPath(i));
        }

        if (isMoveable) {
            List<Vector2> newPolyPoints = new List<Vector2>();
            Vector2 scale = (Vector2)collider.transform.localScale;
            foreach (Vector2 point in polygonPoints) {
                newPolyPoints.Add((Vector2)collider.transform.position + Vector2.Scale(point, scale));
            }
            polygonPoints = newPolyPoints;
        }

        int next = 0;
        for (int curr = 0; curr < polygonPoints.Count; curr++) {

            next = curr + 1;
            if (next == polygonPoints.Count) {
                next = 0;
            }

            Vector2 polyLineStart = polygonPoints[curr];
            Vector2 polyLineEnd = polygonPoints[next];

            if (LineLineCollision(lineStart, lineEnd, polyLineStart, polyLineEnd)) {
                return true;
            }
        }

        return false;
    }

    public Vector3 PolygonLineCollisionPoint(PolygonCollider2D collider, Vector3 lineStart, Vector3 lineEnd, bool isMoveable = false) {

        List<Vector2> polygonPoints = new List<Vector2>(collider.points);
        List<Vector3> collisionPoints = new List<Vector3>();

        for (int i = 0; i < collider.pathCount; i++) {
            polygonPoints.AddRange(collider.GetPath(i));
        }

        if (isMoveable) {
            List<Vector2> newPolyPoints = new List<Vector2>();
            Vector2 scale = (Vector2)collider.transform.localScale;
            foreach (Vector2 point in polygonPoints) {
                newPolyPoints.Add((Vector2)collider.transform.position + Vector2.Scale(point, scale));
            }
            polygonPoints = newPolyPoints;
        }

        int next = 0;
        for (int curr = 0; curr < polygonPoints.Count; curr++) {

            next = curr + 1;
            if (next == polygonPoints.Count) {
                next = 0;
            }

            Vector2 polyLineStart = polygonPoints[curr];
            Vector2 polyLineEnd = polygonPoints[next];
            Vector3 point = LineLineCollisionPoint(lineStart, lineEnd, polyLineStart, polyLineEnd);

            if (point != Vector3.negativeInfinity) {
                collisionPoints.Add(point);
            }
        }
        if (collisionPoints.Count > 0) {
            return collisionPoints.OrderBy(p => Vector3.Distance(p, lineStart)).First();
        }

        return Vector3.zero;
    }

    private bool LineLineCollision(Vector2 lineStart, Vector2 lineEnd, Vector2 otherLineStart, Vector2 otherLineEnd) {
        float x1 = lineStart.x;
        float y1 = lineStart.y;
        float x2 = lineEnd.x;
        float y2 = lineEnd.y;
        float x3 = otherLineStart.x;
        float y3 = otherLineStart.y;
        float x4 = otherLineEnd.x;
        float y4 = otherLineEnd.y;

        float uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1));
        float uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1));

        return uA >= 0f && uA <= 1f && uB >= 0f && uB <= 1f;
    }

    private Vector3 LineLineCollisionPoint(Vector2 lineStart, Vector2 lineEnd, Vector2 otherLineStart, Vector2 otherLineEnd) {
        float x1 = lineStart.x;
        float y1 = lineStart.y;
        float x2 = lineEnd.x;
        float y2 = lineEnd.y;
        float x3 = otherLineStart.x;
        float y3 = otherLineStart.y;
        float x4 = otherLineEnd.x;
        float y4 = otherLineEnd.y;

        float uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1));
        float uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1));

        if (uA >= 0f && uA <= 1f && uB >= 0f && uB <= 1f) {
            float intersectionX = x1 + (uA * (x2 - x1));
            float intersectionY = y1 + (uA * (y2 - y1));
            return new Vector3(intersectionX, intersectionY, 0);
        }

        return Vector3.negativeInfinity; 
    }

    private bool PolygonCircleCollision(PolygonCollider2D collider, Vector3 circleCenter, float circleRadius) {
        List<Vector2> polygonPoints = new List<Vector2>(collider.points);

        for (int i = 0; i < collider.pathCount; i++) {
            polygonPoints.AddRange(collider.GetPath(i));
        }

        if (collider.pathCount > 1) {
            List<Vector2> outsideCollider = new List<Vector2>(collider.GetPath(1));
            List<Vector2> insideCollider = new List<Vector2>(collider.GetPath(0));
            if (PolygonPointCollision(outsideCollider, circleCenter) && !PolygonPointCollision(insideCollider, circleCenter)) {
                return true;
            }
        }
        else {
            if (PolygonPointCollision(polygonPoints, circleCenter)) {
                return true;
            }
        }


        int next = 0;
        for (int curr = 0; curr < polygonPoints.Count; curr++) {

            next = curr + 1;
            if (next == polygonPoints.Count) {
                next = 0;
            }

            Vector2 vc = polygonPoints[curr];
            Vector2 vn = polygonPoints[next];

            bool collision = CircleLineCollision(circleCenter, circleRadius, vc, vn);
            if (collision) {
                return true;
            }
        }

        return false;
    }

    private bool PolygonPointCollision(List<Vector2> polygonPoints, Vector3 point) {
        int next = 0;
        int windingNumber = 0;
        for (int curr = 0; curr < polygonPoints.Count; curr++) {

            next = curr + 1;

            if (next == polygonPoints.Count) {
                next = 0;
            }

            Vector2 vc = polygonPoints[curr];
            Vector2 vn = polygonPoints[next];

            if (vc.y <= point.y) {
                if (vn.y > point.y && IsLeft(vc, vn, point) > 0)
                    windingNumber++;
            }
            else {
                if (vn.y <= point.y && IsLeft(vc, vn, point) < 0)
                    windingNumber--;
            }
        }
        return windingNumber != 0;
    }

    private float IsLeft(Vector2 p0, Vector2 p1, Vector2 p2) {
        return (p1.x - p0.x) * (p2.y - p0.y) - (p1.y - p0.y) * (p2.x - p0.x);
    }

    private bool CircleLineCollision(Vector3 circleCenter, float radius, Vector3 lineStart, Vector3 lineEnd) {

        bool inside1 = PointCircleCollision(lineStart, circleCenter, radius);
        bool inside2 = PointCircleCollision(lineEnd, circleCenter, radius);
        
        if (inside1 || inside2) {
            return true;
        }

        Vector3 line = (lineEnd - lineStart);
        Vector3 lineCircle = (circleCenter - lineStart);
        float len = line.magnitude;

        float dot = Vector3.Dot(line, lineCircle) / Mathf.Pow(len, 2);

        Vector3 closest = lineStart + (dot * line);

        bool onSegment = LinePointCollision(lineStart, lineEnd, closest);
        if (!onSegment) {
            return false;
        }

        float distance = (closest - circleCenter).magnitude;

        return distance <= radius;
    }

    private bool LinePointCollision(Vector3 lineStart, Vector3 lineEnd, Vector3 point) {

        float d1 = (point - lineStart).magnitude;
        float d2 = (point - lineEnd).magnitude;

        float lineLen = (lineEnd - lineStart).magnitude;

        float buffer = 0.01f;

        return (d1 + d2 >= lineLen - buffer && d1 + d2 <= lineLen + buffer);
    }

    private bool PointCircleCollision(Vector3 point, Vector3 circleCenter, float radius) {

        float distance = (point - circleCenter).magnitude;

        return distance <= radius;
    }
}
