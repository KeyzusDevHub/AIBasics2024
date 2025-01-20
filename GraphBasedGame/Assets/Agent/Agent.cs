using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;


public class Agent : MonoBehaviour {
    const int MAX_AMMO = 10;
    const int MAX_HEALTH = 100;
    const int MAX_ARMOR = 100;

    int health;
    int armor;
    int ammo;
    public Bullet bulletPrefab;
    float shootTime = 0;
    float attackAngle = 1f;
    List<Agent> agentsInView = new List<Agent>();
    Dictionary<Agent, float> agentsLastSeen = new Dictionary<Agent, float>();
    GameObject healthBar;
    GameObject armorBar;
    Vector3 healthNominalScale;
    Vector3 armorNominalScale;
    Vector3 healthNominalPosition;
    Vector3 armorNominalPosition;
    [HideInInspector]
    public ColliderChecks colliderChecks;
    public float shootRecoil = 5f;
    SteeringBehaviors sb;
    FSM stateMachine;
    float lastChanged = 0.0f;
    float walkTimer = 0.0f;

    private void Start() {
        health = MAX_HEALTH;
        armor = MAX_ARMOR;
        ammo = MAX_AMMO;
        sb = GetComponent<SteeringBehaviors>();
        stateMachine = GetComponent<FSM>();
        healthBar = transform.Find("Health").gameObject;
        armorBar = transform.Find("Armor").gameObject;
        healthNominalScale = healthBar.transform.localScale;
        armorNominalScale = armorBar.transform.localScale;
        healthNominalPosition = healthBar.transform.localPosition;
        armorNominalPosition = armorBar.transform.localPosition;
    }

    public void ReactToShot(Agent shooter) {
        Vector3 shotPosition = shooter.transform.position;
        if (!colliderChecks.ObstaclesLineCollision(transform.position, shotPosition)) {
            if (!agentsInView.Contains(shooter)) {
                agentsInView.Add(shooter);
                agentsInView = agentsInView.OrderBy(x => Vector3.Distance(x.transform.position, transform.position)).ToList();
            }
            if (!agentsLastSeen.ContainsKey(shooter)) {
                agentsLastSeen.Add(shooter, 0.0f);
            }
            else {
                agentsLastSeen[shooter] = 0.0f;
            }
        }
    }

    private void Shoot() {
        if (shootTime >= 1 && ammo > 0) {
            float randomAngle = Random.Range(-shootRecoil, shootRecoil);
            Vector3 direction = Quaternion.AngleAxis(randomAngle, transform.forward) * transform.up;
            Bullet bullet = Instantiate(bulletPrefab, new Vector3(0f, 0f, 0f), Quaternion.Euler(0f, 0f, 0f));
            bullet.floodingGraph = sb.floodingGraph;
            bullet.checks = colliderChecks;
            bullet.initialize(this, direction);
            shootTime = 0;
            ammo--;
        }
        sb.floodingGraph.PropagateShot(this);
    }

    private void FindEnemiesInSight() {
        List<Agent> enemies = sb.floodingGraph.GetAgentsExcept(this);
        foreach (Agent agent in enemies) {
            if (Vector3.Angle(transform.up, agent.transform.position - transform.position) < sb.viewAngle
                && !colliderChecks.ObstaclesLineCollision(transform.position, agent.transform.position)) {
                if (!agentsInView.Contains(agent)) {
                    agentsInView.Add(agent);
                    agentsInView = agentsInView.OrderBy(x => Vector3.Distance(x.transform.position, transform.position)).ToList();
                }
                if (!agentsLastSeen.ContainsKey(agent)) {
                    agentsLastSeen.Add(agent, 0.0f);
                }
                else {
                    agentsLastSeen[agent] = 0.0f;
                }
            }
        }
    }

    private void ResetEnemiesInSight() {
        List<Agent> newAgentsInView = new List<Agent>();
        foreach(Agent agent in agentsInView) {
            if (agent != null && agentsLastSeen[agent] < 3f) {
                newAgentsInView.Add(agent);
            }
        }
        agentsInView = newAgentsInView;
    }

    private bool ShouldShoot(Agent target) {
        return Vector3.Angle(transform.up, target.transform.position - transform.position) < attackAngle;
    }

    public bool WasHit(Vector3 startPoint, Vector3 dir) {
        return colliderChecks.PolygonLineCollision(GetComponent<PolygonCollider2D>(), startPoint, startPoint + dir * 20f, true);
    }

    public void CollectBoost() {
        string collectedBoost = sb.floodingGraph.CollectBoost(transform.position);
        if (collectedBoost == "Ammo") {
            ammo = MAX_AMMO;
        }
        else if (collectedBoost == "Armor") {
            armor = MAX_ARMOR;
            UpdateBars();
        }
        else if (collectedBoost == "Heal") {
            health = MAX_HEALTH;
            UpdateBars();
        }
    }

    public void Hit() {
        if (armor >- 20) {
            armor -= 20;
            health -= 10;
        }
        else if (armor < 20 && armor != 0) {
            health -= 30 - armor;
            armor = 0;
        }
        else {
            health -= 30;
        }
        UpdateBars();
    }

    private void OnDrawGizmosSelected() {
        if (agentsInView.Count > 0) {
            Gizmos.color = Color.yellow;
            Gizmos.DrawLine(transform.position, agentsInView[0].transform.position);
        }
    }

    private void UpdateBars() {
        Vector3 healthNewScale = healthNominalScale;
        healthNewScale.x *= health / 100f;
        Vector3 armorNewScale = armorNominalScale;
        armorNewScale.x *= armor / 100f;
        healthBar.transform.localScale = healthNewScale;
        armorBar.transform.localScale = armorNewScale;
    }

    private void PreserveBarsPosition() {
        Vector3 healthScaledPosition = new Vector3(healthNominalPosition.x * transform.localScale.x, healthNominalPosition.y * transform.localScale.y, 0f);
        Vector3 armorScaledPosition = new Vector3(armorNominalPosition.x * transform.localScale.x, armorNominalPosition.y * transform.localScale.y, 0f);
        healthBar.transform.position = transform.position + healthScaledPosition;
        armorBar.transform.position = transform.position + armorScaledPosition;
        healthBar.transform.rotation = Quaternion.Euler(0f, 0f, 0f);
        armorBar.transform.rotation = Quaternion.Euler(0f, 0f, 0f);
    }

    private void ReactToStateChange(State newState) {

        if (lastChanged < 0.1f) {
            return;
        }
        if (newState == State.AMMO) {
            sb.Ammo();
        }
        else if (newState == State.ARMOR) {
            sb.Armor();
        }
        else if (newState == State.HEAL) {
            sb.Heal();
        }
        else if (newState == State.HIDE) {
            sb.Hide(agentsInView);
        }
        lastChanged = 0f;
    }

    void Update() {

        ResetEnemiesInSight();
        FindEnemiesInSight();

        stateMachine.StateSwitch(health, armor, ammo, agentsInView);

        ReactToStateChange(stateMachine.getState());

        if (stateMachine.getState() == State.WANDER && walkTimer > 2f) {
            float selected = Random.value;
            if (selected * 100f < 25f) {
                sb.RandomWalk();
            }
            walkTimer = 0f;
        }
        

        if (stateMachine.getState() == State.ATTACK) {
            sb.Attack(agentsInView);
            if (ShouldShoot(agentsInView[0])) {
                Shoot();
            }
        }

        transform.position += sb.getNewVelocity(stateMachine.getState()) * Time.deltaTime;

        shootTime += Time.deltaTime;
        lastChanged += Time.deltaTime;
        walkTimer += Time.deltaTime;

        Dictionary<Agent, float> newAgentsLastSeen = new Dictionary<Agent, float>();
        foreach (Agent agent in agentsLastSeen.Keys) {
            if (agent != null) {
                newAgentsLastSeen.Add(agent, agentsLastSeen[agent] + Time.deltaTime);
            }
        }
        agentsLastSeen = newAgentsLastSeen;
        
        if (health <= 0) {
            sb.floodingGraph.RespawnAgent(this);
            Destroy(gameObject);
        }
        PreserveBarsPosition();
    }
}
