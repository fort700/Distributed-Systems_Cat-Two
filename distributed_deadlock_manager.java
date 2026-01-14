import java.util.*;
import java.util.concurrent.*;

class Transaction {
    String id;
    long timestamp;
    int priority; // Higher weight nodes get higher priority

    public Transaction(String id, int priority) {
        this.id = id;
        this.timestamp = System.currentTimeMillis();
        this.priority = priority;
    }
}

class DeadlockDetector {
    // Maps Transaction ID -> Transaction it is waiting for
    private final Map<String, String> waitForGraph = new ConcurrentHashMap<>();
    private final long timeoutMillis = 2000; 

    public void requestResource(Transaction requester, String holderId) {
        if (holderId == null) return;

        System.out.println("[Detector] " + requester.id + " is waiting for " + holderId);
        waitForGraph.put(requester.id, holderId);

        // Initiate Probe (Edge Chasing)
        if (detectCycle(requester.id, holderId, new HashSet<>())) {
            resolveDeadlock(requester, holderId);
        }
    }

    private boolean detectCycle(String startId, String currentId, Set<String> visited) {
        if (startId.equals(currentId)) return true;
        if (currentId == null || !visited.add(currentId)) return false;

        return detectCycle(startId, waitForGraph.get(currentId), visited);
    }

    private void resolveDeadlock(Transaction requester, String holderId) {
        System.out.println("!!! DEADLOCK DETECTED involving " + requester.id + " !!!");
        
        // Resolution Strategy: Wait-Die (Preserves Consistency)
        // If requester is "older" (higher priority/lower timestamp), it waits.
        // If requester is "younger", it dies (aborts) to break the cycle.
        if (requester.priority < 5) { // Simulation logic: lower priority nodes abort
            System.out.println("[Recovery] Aborting Transaction " + requester.id + " to release Core1 locks.");
            waitForGraph.remove(requester.id);
            // Trigger protocol recovery from (l)
        } else {
            System.out.println("[Recovery] Requester high priority. Forcing timeout on holder " + holderId);
        }
    }
}

public class DistributedSystemSim {
    public static void main(String[] args) {
        DeadlockDetector detector = new DeadlockDetector();

        // Simulate Transactions on identified bottleneck nodes (k)
        Transaction txCore1 = new Transaction("TX_CORE1", 8); // High priority
        Transaction txEdge2 = new Transaction("TX_EDGE2", 2); // Low priority (0.5% loss)

        // Simulate Cyclic Dependency: 
        // TX_CORE1 waits for TX_EDGE2 (consensus)
        // TX_EDGE2 waits for TX_CORE1 (lock on data)
        System.out.println("--- Simulating Cyclic Dependency between Core and Edge ---");
        
        detector.requestResource(txCore1, "TX_EDGE2");
        detector.requestResource(txEdge2, "TX_CORE1"); // This triggers detection
    }
}
