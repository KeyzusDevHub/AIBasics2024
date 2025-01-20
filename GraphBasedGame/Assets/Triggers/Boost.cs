using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Boost : MonoBehaviour
{
    public float respawnTime = 5f;
    float time = 0f;
    bool collected = false;
    List<SpriteRenderer> sprites = new List<SpriteRenderer>();

    private void Awake() {
        sprites = new List<SpriteRenderer>(GetComponentsInChildren<SpriteRenderer>());
    }

    void Update()
    {
        if (time > 0f) {
            time -= Time.deltaTime;
        }
        else if (collected) {
            collected = false;
            foreach (var sprite in sprites) {
                sprite.enabled = true;
            }
        }
    }

    public bool IsCollected() {
        return collected;
    }

    public void Collect() {
        collected = true;
        time = respawnTime;
        foreach (var sprite in sprites) {
            sprite.enabled = false;
        }
    }
}
