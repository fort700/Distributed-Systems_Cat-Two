import java.util.*;
import java.util.concurrent.*;

// 1. Message Structure with Priority for Event Ordering
class Message {
    enum Type { RPC, PREPARE, COMMIT, DATA_SYNC, RECOVERY }
    String senderId;
    Type type;
    long timestamp;
    int priority; // Lower is higher priority
    Object payload;

    public Message(String senderId, Type type, int priority, Object payload) {
        this.senderId = senderId;
        this.type = type;
        this.timestamp = System.currentTimeMillis();
        this.priority = priority;
        this.payload = payload;
    }
}

// 2. Base Node Class modeling metrics and failure behavior
abstract class Node {
    String id;
    String layer;
    int latency; // ms
    double packetLoss;
    String failureType;
    boolean isRunning = true;

    public Node(String id, String layer, int latency, double packetLoss, String failureType) {
        this.id = id;
        this.layer = layer;
        this.latency = latency;
        this.packetLoss = packetLoss;
        this.failureType = failureType;
    }

    public abstract void handleMessage(Message msg);

    protected boolean shouldDropPacket() {
        return Math.random() < (packetLoss / 100.0);
    }

    protected void simulateByzantineBehavior(Message msg) {
        if ("Byzantine".equals(failureType)) {
            msg.payload = "CORRUPTED_DATA_" + new Random().nextInt(100);
        }
    }
}

// 3. Concrete Layer Implementations
class EdgeNode extends Node {
    private PriorityQueue<Message> eventQueue = new PriorityQueue<>(Comparator.comparingInt(m -> m.priority));

    public EdgeNode(String id, int latency, double loss, String fail) { super(id, "Edge", latency, loss, fail); }

    @Override
    public void handleMessage(Message msg) {
        if (!isRunning || (msg.type == Message.Type.RPC && "Omission".equals(failureType) && shouldDropPacket())) {
            System.out.println("[" + id + "] Message omitted or node crashed.");
            return;
        }
        eventQueue.add(msg);
        processEvents();
    }

    private void processEvents() {
        while (!eventQueue.isEmpty()) {
            Message m = eventQueue.poll();
            System.out.println("[" + id + "] Processing " + m.type + " with priority " + m.priority);
        }
    }
}

class CoreNode extends Node {
    public CoreNode(String id, int latency, double loss, String fail) { super(id, "Core", latency, loss, fail); }

    @Override
    public void handleMessage(Message msg) {
        if ("Crash".equals(failureType) && Math.random() > 0.8) {
            isRunning = false;
            System.out.println("[" + id + "] CRITICAL FAILURE: Node Crashed.");
            return;
        }
        
        simulateByzantineBehavior(msg);
        
        if (msg.type == Message.Type.PREPARE) {
            System.out.println("[" + id + "] 2PC Phase 1: Voted to Commit. Payload: " + msg.payload);
        }
    }
}

// 4. Network Simulator (Handles Asynchronous Delays)
class Network {
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(5);
    private final Map<String, Node> nodes = new HashMap<>();

    public void addNode(Node node) { nodes.put(node.id, node); }

    public void sendMessage(String targetId, Message msg) {
        Node target = nodes.get(targetId);
        if (target != null) {
            // Simulate Asynchronous Delay based on Node Latency
            scheduler.schedule(() -> target.handleMessage(msg), target.latency, TimeUnit.MILLISECONDS);
        }
    }
}

// 5. Execution Environment
public class DistributedSystemRunner {
    public static void main(String[] args) {
        Network network = new Network();

        // Initialize nodes using Dataset metrics
        EdgeNode edge1 = new EdgeNode("Edge1", 12, 0.2, "Crash");
        CoreNode core1 = new CoreNode("Core1", 8, 0.1, "Byzantine");
        CoreNode core2 = new CoreNode("Core2", 10, 0.2, "Crash");

        network.addNode(edge1);
        network.addNode(core1);
        network.addNode(core2);

        System.out.println("--- Starting Distributed Operations ---");

        // Simulate RPC from Edge to Core
        network.sendMessage("Edge1", new Message("User", Message.Type.RPC, 1, "Initial Request"));
        
        // Simulate Transaction Commit (2PC) at Core
        network.sendMessage("Core1", new Message("Edge1", Message.Type.PREPARE, 2, "Transaction_Data_001"));
        network.sendMessage("Core2", new Message("Edge1", Message.Type.PREPARE, 2, "Transaction_Data_001"));
    }
}
