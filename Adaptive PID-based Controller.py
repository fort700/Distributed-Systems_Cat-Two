class PIDController:
    def __init__(self, target_cpu=0.70):
        self.target = target_cpu
        self.integral = 0
        self.prev_error = 0

    def calculate_throttle_rate(self, current_cpu, current_locks):
        # Penalty for lock contention to prevent serialization bottleneck
        effective_load = current_cpu + (current_locks * 2.0)
        error = effective_load - self.target
        
        self.integral += error
        derivative = error - self.prev_error
        
        # Output is the adjustment to the Transaction Rate (TPS)
        adjustment = (Kp * error) + (Ki * self.integral) + (Kd * derivative)
        self.prev_error = error
        return max(0.1, 1.0 - adjustment) # Returns a multiplier for Ingress

def monitor_and_optimize():
    while True:
        metrics = get_node_metrics("Cloud1")
        # Compute health multiplier
        multiplier = controller.calculate_throttle_rate(metrics.cpu, metrics.locks)
        
        if metrics.cpu > 0.85 or metrics.memory_usage > 0.90:
            # Emergency Load Shedding
            drop_non_essential_tasks(priority < 3)
            trigger_backpressure_to_edge(multiplier * 0.5)
        else:
            # Gradual adjustment
            update_admission_control(multiplier)
        
        sleep(100ms) # Control loop frequency