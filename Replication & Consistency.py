import threading
import time

class ConsistencyManager:
    def __init__(self, replicas):
        self.replicas = replicas  # List of Node objects
        self.lock = threading.Lock()
        self.global_state = {}

    def execute_transaction(self, tx_id, key, value):
        """
        Simulates a Strong Consistency write (Synchronous Replication).
        Ensures all active replicas acknowledge before commit.
        """
        with self.lock:
            print(f"\n[TX {tx_id}] Initiating Transaction: {key} -> {value}")
            
            # Phase 1: Prepare/Propose
            acks = 0
            for node in self.replicas:
                if node.is_active:
                    # Simulate network delay for replication
                    time.sleep(node.latency_ms / 1000)
                    acks += 1
            
            # Phase 2: Commit (Requires Quorum)
            quorum = (len(self.replicas) // 2) + 1
            if acks >= quorum:
                self.global_state[key] = value
                print(f"[TX {tx_id}] SUCCESS: Quorum reached ({acks}/{len(self.replicas)}).")
                return True
            else:
                print(f"[TX {tx_id}] ABORTED: Insufficient replicas available.")
                return False

# Example Usage with your Dataset Nodes
core_nodes = [nodes_list[2], nodes_list[3]] # Core1 and Cloud1 as replicas
consistency_engine = ConsistencyManager(core_nodes)

# Simulate concurrent transactions
t1 = threading.Thread(target=consistency_engine.execute_transaction, args=("001", "balance", 500))
t2 = threading.Thread(target=consistency_engine.execute_transaction, args=("002", "balance", 600))

t1.start()
t2.start()
t1.join()
t2.join()