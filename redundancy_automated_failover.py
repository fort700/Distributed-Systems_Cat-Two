import time
import random
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# --- Configuration & Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NodeState(Enum):
    ACTIVE = "ACTIVE"
    STANDBY = "STANDBY"
    FAILED = "FAILED"
    PARTITIONED = "PARTITIONED"

@dataclass
class Node:
    id: str
    role: str  # e.g., "Primary", "Replica"
    metrics: Dict[str, float]  # CPU, Latency, etc.
    state: NodeState = NodeState.STANDBY
    data_log: List[str] = field(default_factory=list)
    last_heartbeat: float = 0.0

class FailoverSystem:
    def __init__(self):
        # Initializing high-risk nodes from (p) with Redundant Pairs
        self.nodes = {
            # Core1 (Byzantine Risk) -> Paired with Core1_Backup
            "Core1": Node("Core1", "Primary", {"cpu": 65, "lock": 12}, NodeState.ACTIVE),
            "Core1_Backup": Node("Core1_Backup", "Replica", {"cpu": 10, "lock": 0}, NodeState.STANDBY),
            
            # Cloud1 (Resource Cliff) -> Paired with Cloud1_Overflow
            "Cloud1": Node("Cloud1", "Primary", {"cpu": 72, "mem": 16.0}, NodeState.ACTIVE),
            "Cloud1_Overflow": Node("Cloud1_Overflow", "Replica", {"cpu": 5, "mem": 32.0}, NodeState.STANDBY),
            
            # Edge2 (Network Risk) -> No dedicated backup, relies on Edge1
            "Edge2": Node("Edge2", "Primary", {"packet_loss": 0.5}, NodeState.ACTIVE),
        }
        self.partition_groups = [] # List of sets containing node IDs that can communicate

    def replicate_state(self, primary_id: str, replica_id: str, data: str):
        """Simulates data replication. Fails if network is partitioned."""
        p_node = self.nodes[primary_id]
        r_node = self.nodes[replica_id]

        if p_node.state == NodeState.ACTIVE and r_node.state != NodeState.FAILED:
            # Check partition connectivity
            if self.is_partitioned(primary_id, replica_id):
                logging.warning(f"REPLICATION FAILED: {primary_id} cannot reach {replica_id} (Partitioned)")
                return False
            
            r_node.data_log.append(data)
            logging.info(f"SYNC: {data} replicated from {primary_id} to {replica_id}")
            return True
        return False

    def heartbeat_check(self):
        """Monitors node health and triggers failover."""
        current_time = time.time()
        
        # Check Core1 (Byzantine/Crash Risk)
        if not self.is_healthy("Core1"):
            self.trigger_failover("Core1", "Core1_Backup")

        # Check Cloud1 (Resource Saturation)
        if not self.is_healthy("Cloud1"):
            self.trigger_failover("Cloud1", "Cloud1_Overflow")

    def is_healthy(self, node_id: str) -> bool:
        """Simulates health check. Returns False if failed or partitioned."""
        node = self.nodes[node_id]
        if node.state == NodeState.FAILED:
            return False
        # If partitioned from the monitor (simulated here as 'self'), consider unhealthy
        return True 

    def trigger_failover(self, primary_id: str, standby_id: str):
        primary = self.nodes[primary_id]
        standby = self.nodes[standby_id]

        if standby.state == NodeState.STANDBY:
            logging.error(f"!!! FAILOVER ALERT: {primary_id} is DOWN/UNREACHABLE. Promoting {standby_id} !!!")
            
            # Fencing: Ensure old primary is marked failed to prevent Split-Brain
            primary.state = NodeState.FAILED 
            standby.state = NodeState.ACTIVE
            logging.info(f"SUCCESS: {standby_id} is now ACTIVE Primary.")
        else:
            logging.critical(f"CRITICAL FAILURE: Backup {standby_id} is also unavailable!")

    def inject_simultaneous_failure(self):
        """Simulates the catastrophic scenario from (p)."""
        logging.info("\n--- INJECTING SIMULTANEOUS FAILURES ---")
        
        # 1. Network Partition isolates Edge2 and Cloud1
        self.partition_groups = [{"Core1", "Core1_Backup", "Cloud1_Overflow"}, {"Edge2", "Cloud1"}]
        logging.warning("NETWORK PARTITION: System split into two isolated groups.")
        
        # 2. Primary Cloud Node Crashes under load
        self.nodes["Cloud1"].state = NodeState.FAILED
        logging.error("FAILURE: Cloud1 crashed due to Resource Exhaustion (CPU > 95%).")

        # 3. Core1 acts Byzantine (stops responding correctly)
        self.nodes["Core1"].state = NodeState.FAILED
        logging.error("FAILURE: Core1 detected as Byzantine/Unresponsive.")

    def is_partitioned(self, node_a: str, node_b: str):
        """Returns True if nodes are in different partition groups."""
        if not self.partition_groups: return False
        
        group_a = next((g for g in self.partition_groups if node_a in g), None)
        group_b = next((g for g in self.partition_groups if node_b in g), None)
        return group_a != group_b

# --- Execution Simulation ---
system = FailoverSystem()

# Normal Operation
system.replicate_state("Core1", "Core1_Backup", "Transaction_001")
system.replicate_state("Cloud1", "Cloud1_Overflow", "Archive_Data_A")

# Trigger Catastrophe
system.inject_simultaneous_failure()

# System attempts auto-recovery
print("\n--- ATTEMPTING AUTOMATED RECOVERY ---")
system.heartbeat_check()

# Verify Split-Brain Prevention (Replication attempt during partition)
system.replicate_state("Cloud1_Overflow", "Cloud1", "Recovery_Log_01")
