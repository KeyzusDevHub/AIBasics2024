using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public enum State {
    WANDER,
    ATTACK,
    HIDE,
    AMMO,
    ARMOR,
    HEAL
}

public class FSM : MonoBehaviour {
    State agentState = State.WANDER;
    FloodingGraph floodingGraph;

    private void Start() {
        floodingGraph = GetComponent<SteeringBehaviors>().floodingGraph;
    }

    public void StateSwitch(int health, int armor, int ammo, List<Agent> nearbyAgents) {
        if (agentState == State.WANDER) {
            ReactInWanderState(health, armor, ammo, nearbyAgents);
        }
        else if (agentState == State.ATTACK) {
            ReactInAttackState(health, armor, ammo, nearbyAgents);
        }
        else if (agentState == State.HIDE) {
            ReactInHideState(nearbyAgents);
        }
        else if (agentState == State.AMMO) {
            ReactInAmmoState(health, armor, ammo, nearbyAgents);
        }
        else if (agentState == State.ARMOR) {
            ReactInArmorState(health, armor, nearbyAgents);
        }
        else if (agentState == State.HEAL) {
            ReactInHealState(health, armor, nearbyAgents);
        }
    }

    public void ReactInWanderState(int health, int armor, int ammo, List<Agent> nearbyAgents) {
        if (health < 50 && floodingGraph.IsAnyBoostOnMap("Heal")) {
            agentState = State.HEAL;
        }
        else if (ammo == 0 && floodingGraph.IsAnyBoostOnMap("Ammo")) {
            agentState = State.AMMO;
        }
        else if (armor < 50 && floodingGraph.IsAnyBoostOnMap("Armor")) {
            agentState = State.ARMOR;
        }
        else if (health > 50 && armor > 50 && ammo > 0 && nearbyAgents.Count > 0) {
            agentState = State.ATTACK;
        }
        else if (health > 50 && health + armor > 100 && ammo > 0 && nearbyAgents.Count > 0) {
            agentState = State.ATTACK;
        }
        else {
            agentState = State.WANDER;
        }
    }

    public void ReactInAttackState(int health, int armor, int ammo, List<Agent> nearbyAgents) {
        if (health < 50 || health + armor < 100) {
            agentState = State.HIDE;
        }
        else if (ammo == 0 && floodingGraph.IsAnyBoostOnMap("Ammo")) {
            agentState = State.AMMO;
        }
        else if (ammo == 0 && !floodingGraph.IsAnyBoostOnMap("Ammo")) {
            agentState = State.WANDER;
        }
        else if (nearbyAgents.Count < 1) {
            agentState = State.WANDER;
        }
        else {
            agentState = State.ATTACK;
        }
    }

    public void ReactInHideState(List<Agent> nearbyAgents) {
        if (nearbyAgents.Count == 0) {
            agentState = State.WANDER;
        }
        else {
            agentState = State.HIDE;
        }
    }

    public void ReactInAmmoState(int health, int armor, int ammo, List<Agent> nearbyAgents) {
        if (nearbyAgents.Count > 0 && (health < 50 || health + armor < 100)) {
            agentState = State.HIDE;
        }
        else if (ammo > 0) {
            agentState = State.WANDER;
        }
        else if (!floodingGraph.IsAnyBoostOnMap("Ammo")) {
            agentState = State.WANDER;
        }
        else {
            agentState = State.AMMO;
        }
    }

    public void ReactInArmorState(int health, int armor, List<Agent> nearbyAgents) {
        if (nearbyAgents.Count > 0 && (health < 50 || health + armor < 100)) {
            agentState = State.HIDE;
        }
        else if (armor == 100) {
            agentState = State.WANDER;
        }
        else if (!floodingGraph.IsAnyBoostOnMap("Armor")) {
            agentState = State.WANDER;
        }
        else {
            agentState = State.ARMOR;
        }
    }

    public void ReactInHealState(int health, int armor, List<Agent> nearbyAgents) {
        if (nearbyAgents.Count > 0 && (health < 50 || health + armor < 100)) {
            agentState = State.HIDE;
        }
        else if (!floodingGraph.IsAnyBoostOnMap("Heal")) {
            agentState = State.WANDER;
        }
        else if (health == 100) {
            agentState = State.WANDER;
        }
        else {
            agentState = State.HEAL;
        }
    }

    public State getState() { 
        return agentState;
    }
}
