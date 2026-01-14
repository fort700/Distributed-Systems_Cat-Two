def allocate_task(task_type, current_load_map):
    # Sort nodes by the specific resource the task needs
    if task_type == "ANALYTICS":
        target_nodes = sort_by_memory_and_throughput(nodes)
    elif task_type == "TRANSACTION":
        target_nodes = sort_by_latency_and_tps(nodes)

    for node in target_nodes:
        # Check if adding this task violates the 85% CPU safety margin
        if node.predicted_cpu(task) < 0.85 and node.lock_risk < 0.12:
            return node.dispatch(task)
    
    # If no node is safe, initiate "Load Shedding"
    return load_shedding_queue.push(task)
