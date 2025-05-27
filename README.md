# TASK 2: high-level architectural design
<h1 align="center">
<img src="https://raw.githubusercontent.com/soheilmahdavi/kind-kafka/main/docs/images/highlevel-architecture.svg" width="1000">
</h1><br>


## Explanation of Components:

### 1. Data Collection & Storage

* Role: Storage and versioning of raw image data.

* Instruments: AWS S3, Azure Blob Storage, MinIO.

* Rationale: scalable, reliable, affordable storage devices and services are now available, ideal for storing image and versions on.

### 2. Preprocessing of Data and Features Extraction

* Role: Cleanse, resize, normalize and extract features from raw image data.

* Tools: AWS Glue, Apache Airflow, Kubeflow Pipelines.

* Rationale: Workflow automation, being able to reproduce the preprocessing and use it as part of ML workflows.

### 3. Model Training

* Role: Training and validation of ML models with automated standardized workflows.

* Tools: Kubeflow, Amazon SageMaker, MLflow.

* Explanation: Kubeflow and SageMaker support scalable training infrastructure, A/B testing, and are well-suited for Kubernetes-based cloud-native solutions. MLflow makes it simple to manage the complete lifecycle of your model.

### 4. Model Registry

* Role: Serve as a central place to store pre-trained models as well as managing these files and versioning and their associated metadata.

* Tools: MLflow Model Registry, Amazon SageMaker Model Registry.

* Comment: The single source of truth for model version and model metadata makes deployment management.

### 5. CI/CD Pipelines & Model Deployment Managing:

* Responsibility: Automate deployment, testing and version roll out of models.

* Techstack: We currently use GitLab CI, ArgoCD and Jenkins.

* Rationale: GitLab CI - integration into source control is seamless. ArgoCD-as-a-service for continuous delivery on Kubernetes, for repeatable and auditable deployments.

### 6. Production Deployments and Monitoring

* Primary function: Deploy models, serve predictions, and monitor performance.

* Thou shalt leverage the following tools and platforms: Kubernetes (for deployed scalable deployments), Prometheus (for monitoring & metrics), Grafana (for visualization).

* Rationale: Kubernetes smoothes out reliable scale and deployment. Prometheus and Grafana are the observability tools for the model’s health.

### 7. User/Application Access

* Role: Providing external systems and users easy and secure access to predictions.

* Tools: API Gateway, REST APIs (e.g., AWS API Gateway, Kong, Ambassador).

* Justification: Simplifies integration with applications, provides secure, standardized interfaces

---
# Tasks 1
1. Containerization
  - [x] Create a Dockerfile for each microservice.
  - [x] Choose an appropriate base image and install the necessary dependencies.  
2. Kubernetes Manifests 
  - [x] Write the required Kubernetes manifest files (e.g., deployment, job) for each micro service to deploy them 
        to a Kubernetes cluster.  

3. Bonus Questions  

  - [x] Discuss Monitoring: Kafka and the connected applications need to be monitored for health and performance.  
        What monitoring technology stack would you recommend collecting, store and visualize observability data 
        (metrics, logs, traces)? 
  - [ ] Briefly explain how you would implement observability for Kafka and the micro services.  
        
  - [ ] Discuss Image Hardening: To minimize the attack vector on our applications, we apply "image hardening" when 
        building our Docker images.  
  - [ ] What aspects would you consider?


#  DevOps Assessment – Kafka Prototype

Two Python micro-services illustrate how internal applications can publish to, and consume from, ÖBB’s Kafka integration platform.

| Path | Purpose |
|------|---------|
| `kafka-producer/`   | One-shot **Job** that publishes *N* demo messages and exits. |
| `kafka-consumer/`   | Long-running **Deployment** that logs every message on a topic. |
| `infra/k8s/`        | Kubernetes YAML: shared `ConfigMap`, producer `Job`, consumer `Deployment`. |
| `requirements.txt`  | Shared Python dependencies (`kafka-python`, `python-dotenv`). |

---

## Table of Contents
1. [Prerequisites](##Prerequisites)  
2. [Build & Push Images](#build--push-images)  
3. [Deploy to Kubernetes](#deploy-to-kubernetes)  
4. [Optional – Run a Broker in kind](#optional--run-a-broker-in-kind)  
5. [Clean-up](#clean-up)  
6. [Monitoring & Observability](#monitoring--observability)  
7. [Image-Hardening Checklist](#image-hardening-checklist)  
8. [Quick Links](#quick-links)

---

## Prerequisites
* Docker 24 ( BuildKit enabled )  
* Kubernetes ≥ 1.27 (e.g. I use **kind**)  
* Helm v3 *(only for the optional Kafka demo)*  

---
## Option 1: Create Kubernetes Cluster and registry
```bash
chmod 777 create-cluster.sh
./create-cluster.sh
```

## Option 2:  Run a Broker in kind
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install kafka bitnami/kafka \
  --set replicaCount=1 \
  --set auth.enabled=false \
  --set zookeeper.enabled=true
```
---

## Build & Push Images
```bash
# build
docker build -t localhost:5000/kafka-producer:1.0.0 -f kafka-producer/Dockerfile .
docker build -t localhost:5000/kafka-consumer:1.0.0 -f kafka-consumer/Dockerfile .

# push to your local registry (kind-registry on :5000)
docker push localhost:5000/kafka-producer:1.0.0
docker push localhost:5000/kafka-consumer:1.0.0
```

## deploy-to-kubernetes
```bash
kubectl apply -f kafka-consumer/deploy/
kubectl apply -f kafka-producer/deploy/
```



## Image-Hardening Checklist

* Minimal base – distroless Debian 12.

* Non-root – USER nonroot; read-only root filesystem.

* Capability drop – capDrop: ["ALL"].

* Multi-stage build – compilers & pip cache stay in builder layer.

* Tag & digest pinning – prevents “latest” drift.

* SBOM + scan – CycloneDX + Trivy/Grype in CI.

* CIS Benchmarks – automated with [docker-bench](https://www.cisecurity.org/benchmark/docker), kube-bench.

## Monitoring & Observability

| Plane    | Stack                                    | Instrumentation                                                                                                  |
|----------|------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| Metrics  | **Prometheus Operator** + **Grafana**    | • Kafka via **JMX Exporter** / **Kafka Exporter** (lag, ISR, throughput)<br>• Micro-services expose `/metrics` with `prometheus_client` |
| Logs     | **Grafana Loki** (or EFK)                | JSON logs → **promtail** / **Fluent Bit**                                                                         |
| Traces   | **OpenTelemetry Collector** → **Tempo** (or Jaeger) | Auto-instrument Python; trace producer → broker → consumer spans                                                  |
| Alerts   | **Alertmanager**                         | Prometheus and Grafana                                     |

---
### Metrics
Here’s a visual of the metrics pipeline inside Kubernetes, your micro-service pods, and the Prometheus → Grafana / Alertmanager stack:

<!-- Local / relative path -->
![Brief alt text](images/Metrics.png)
<h1 align="center">
<img src="https://raw.githubusercontent.com/soheilmahdavi/kind-kafka/main/docs/images/metrics.png" width="600">
</h1><br>

* Kafka pod – jvm metrics are exported via jmx exporter.

* Consumer / Producer – Python metrics on /metrics exposed by prometheus_client

* ServiceMonitor – This is a custom resource created by Prometheus Operator in order to auto-scrape the Service endpoints.

* Prometheus → Alertmanager → Slack – send alerts to a slack channel for on-call notification

* Dashboards feed into Grafana for real time visualisation

---
### LOGs “Kubernetes Logging with Grafana Loki”
<h1 align="center">
<img src="https://raw.githubusercontent.com/soheilmahdavi/kind-kafka/main/docs/images/LOGs.jpg" width="600">
</h1><br>


* Cluster layout

  On the left, you have two “Worker Node” blocks. Each node has multiple application containers running.

* Gathering logs from each node

  A Prometheus server runs as a StatefulSet, while a Promtail agent runs as a DaemonSet, so there’s exactly one Promtail pod per node.

  Promtail tails the stdout log file of each container, and labels it with the name of the container as well as Kubernetes labels (namespace, pod, container, etc).

* Shipping logs to Loki

  Promtail pushing log streams to Loki via HTTP.

* Loki Service

  Kubernetes Service that fronts Loki. It exposes port 3100, which Promtail targets for ingestion and which Grafana uses for queries.

* Visualization with Grafana

  Dashboards let operators search or filter the logs with LogQL, correlate them with metrics, and build panels/alerts.


---
### Tracing: OpenTelemetry + Tempo + Grafana

<h1 align="center">
<img src="https://raw.githubusercontent.com/soheilmahdavi/kind-kafka/main/docs/images/Trace.jpg" width="600">
</h1><br>

* OpenTelemetry SDK / auto-instrumentation

    creates spans for every request, Kafka publish/consume, DB call, etc.


* OpenTelemetry Collector (cluster service)

    receives OTLP spans from all pods, adds Kubernetes labels, batches & samples.

    exports the processed spans to the tracing backend.

* Grafana Tempo (tracing backend)

    ingests the spans, compresses them, stores them in storage.


* Grafana (UI)

    is configured with a Tempo datasource → can search traces by service / latency / errors.


---

## Quick Links

* Kind + local registry https://kind.sigs.k8s.io/docs/user/local-registry/

* Bitnami Kafka chart https://github.com/bitnami/charts/tree/master/bitnami/kafka

* Prometheus Operator https://github.com/prometheus-operator/prometheus-operator

* Loki Operator https://medium.com/@muppedaanvesh/a-hands-on-guide-to-kubernetes-logging-using-grafana-loki-%EF%B8%8F-b8d37ea4de13

* Docker Image Hardning https://owasp.org/www-project-devsecops-guideline/latest/02f-Container-Vulnerability-Scanning