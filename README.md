# Distributed-Systems_Cat-Two

**Distributed Computing & Applications: Edge-Core-Cloud Telecom System**

**Project Overview**

This repository contains the design, implementation, and multi-dimensional analysis of a carrier-grade distributed telecommunications system. The project follows a strictly sequential task-flow, evolving from a raw performance dataset into a fully integrated, fault-tolerant orchestrator capable of handling heterogeneous workloads with strong consistency.

**System Architecture**

The architecture is designed as a three-tier continuum to optimize for the competing requirements of latency and throughput.

*Edge Layer: Optimized for ultra-low latency and local event ordering
*Core Layer: The transactional engine handling consensus and deadlock detection with high throughput 
*Cloud Layer: A high-capacity resource pool for analytics and distributed shared memory.

**Key Features**

*Weighted-Quorum Paxos (Consensus): A custom protocol designed to maximize throughput under asymmetric failure probabilities and network jitter.
*Adaptive Migration: Python-based simulation of dynamic process allocation to balance CPU and memory loads across nodes.
*Distributed Deadlock Management: Java implementation of edge-chasing algorithms and "Wait-Die" resolution to maintain system liveness.
*Byzantine Fault Tolerance: Integrated mechanisms to detect and fence corrupted nodes, specifically addressing the risks associated with the Core layer.

**Data-Driven Insights**

The project utilizes a specific dataset of five nodes (Edge1, Edge2, Core1, Core2, Cloud1) to justify all design decisions:

*Primary Bottleneck: Identified as Core1 due to a $12\%$ lock contention rate and Byzantine failure potential.
*Latency Anchor: Cloud1 contributes the highest end-to-end latency, necessitating the weighted quorum bypass strategy.
*Reliability Score: Systemic risk is mitigated through a multi-dimensional strategy that improves throughput.

**Getting Started**

*Simulation: Run python and java codes to observe system behavior during simultaneous multi-node responses and failures.
*Analysis: Review task (t) for a critical analysis of trade-offs between reliability, scalability, and maintainability.
