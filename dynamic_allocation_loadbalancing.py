import random
import time
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Node:
    name: str
    layer: str
    cpu_usage: float  # Percentage
    memory_gb: float
    latency_ms: int
    is_active: bool = True
    task_queue: List[str] = field(default_factory=list)

class DistributedSystemSim:
    def __init__(self, nodes: List[Node]):
        self.nodes = {n.name: n for n in nodes}
        self.network_delay_factor = 1.0 # Multiplier for jitter

    def inject_failure(self, node_name: str):
        """Simulates Crash or Omission failure."""
        if node_name in self.nodes:
            self.nodes[node_name].is_active = False
            print(f"!!! FAILURE INJECTED: {node_name} is DOWN !!!")

    def adaptive_migrate(self, task: str, source_node: Node):
        """Finds the next best node based on layer hierarchy and current CPU."""
        print(f"Searching migration target for {task} from {source_node.name}...")
        
        # Filter active nodes that aren't the source
        candidates = [n for n in self.nodes.values() if n.is_active and n.name != source_node.name]
        
        # Selection Logic: Prioritize same layer, then lowest CPU usage
        candidates.sort(key=lambda x: (x.layer != source_node.layer, x.cpu_usage))
        
        if candidates:
            target = candidates[0]
            target.task_queue.append(task)
            print(f"SUCCESS: Migrated {task} to {target.name} (CPU: {target.cpu_usage}%)")
        else:
            print(f"CRITICAL: No available nodes for migration of {task}")

    def process_workload(self, workload: Dict[str, str]):
        """
        Simulates task execution with network delays and dynamic balancing.
        workload: {task_id: target_node_name}
        """
        for task, node_name in workload.items():
            node = self.nodes[node_name]
            
            # 1. Simulate Network Delay
            delay = (node.latency_ms / 1000) * random.uniform(0.8, 1.5)
            time.sleep(delay)
            
            # 2. Check for node health or Overload (Threshold > 85%)
            if not node.is_active or node.cpu_usage > 85.0:
                print(f"Node {node_name} unavailable or overloaded. Triggering migration...")
                self.adaptive_migrate(task, node)
            else:
                node.task_queue.append(task)
                print(f"Task {task} processed by {node_name} in {delay:.3f}s")

# --- Initialize Dataset from Image ---
nodes_list = [
    Node("Edge1", "Edge", 45.0, 4.0, 12),
    Node("Edge2", "Edge", 50.0, 4.5, 15),
    Node("Core1", "Core", 65.0, 8.0, 8),
    Node("Cloud1", "Cloud", 72.0, 16.0, 22)
]

sim = DistributedSystemSim(nodes_list)

# --- Execution Simulation ---
print("--- Starting Simulation ---")
current_tasks = {"Task_A": "Edge1", "Task_B": "Edge2", "Task_C": "Core1"}

# Inject a failure mid-process
sim.inject_failure("Edge1")

# Process tasks
sim.process_workload(current_tasks)
