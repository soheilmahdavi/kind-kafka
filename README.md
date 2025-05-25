# ÖBB DevOps Assessment – Kafka Prototype

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
* Kubernetes ≥ 1.27 (e.g. **kind**)  
* Helm v3 *(only for the optional Kafka demo)*  

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
kubectl apply -f infra/k8s/
```

## Optional – Run a Broker in kind
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install kafka bitnami/kafka \
  --set replicaCount=1 \
  --set auth.enabled=false \
  --set zookeeper.enabled=true
```
## Clean-up
```bash
helm uninstall kafka                 # remove optional broker
kubectl delete -f infra/k8s/         # remove producer / consumer resources
```

## Image-Hardening Checklist

* Minimal base – distroless Debian 12.

* Non-root – USER nonroot; read-only root filesystem.

* Capability drop – capDrop: ["ALL"].

* Multi-stage build – compilers & pip cache stay in builder layer.

* Tag & digest pinning – prevents “latest” drift.

* SBOM + scan – CycloneDX + Trivy/Grype in CI.

* Sign & verify – cosign + admission policy.

* Runtime defence – Falco rules; Pod Security baseline or higher.

* CIS Benchmarks – automated with docker-bench, kube-bench.

## Monitoring & Observability

| Plane    | Stack                                    | Instrumentation                                                                                                  |
|----------|------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| Metrics  | **Prometheus Operator** + **Grafana**    | • Kafka via **JMX Exporter** / **Kafka Exporter** (lag, ISR, throughput)<br>• Micro-services expose `/metrics` with `prometheus_client` |
| Logs     | **Grafana Loki** (or EFK)                | JSON logs → **promtail** / **Fluent Bit**                                                                         |
| Traces   | **OpenTelemetry Collector** → **Tempo** (or Jaeger) | Auto-instrument Python; trace producer → broker → consumer spans                                                  |
| Alerts   | **Alertmanager**                         | Lag thresholds, under-replicated partitions, broker down, high 5xx error rate                                     |


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

### LOGs “Kubernetes Logging with Grafana Loki”
<h1 align="center">
<img src="https://raw.githubusercontent.com/soheilmahdavi/kind-kafka/main/docs/images/LOGs.jpg" width="600">
</h1><br>


What the diagram shows – 
* Cluster layout
At the left you see two “Worker Node” blocks.
Each node runs several application containers.

* Log collection on every node

A Promtail agent runs as a DaemonSet, so there is one Promtail pod per node.

Promtail tails each container’s stdout log file and attaches Kubernetes labels (namespace, pod, container, etc.).

* Shipping logs to Loki

Dashed red arrows show Promtail pushing log streams to Loki over HTTP.

A single Loki deployment receives, indexes and stores the logs.

* Loki Service

Kubernetes Service that fronts Loki. It exposes port 3100, which Promtail targets for ingestion and which Grafana uses for queries.

* Visualization with Grafana

Dashboards let operators search or filter the logs with LogQL, correlate them with metrics, and build panels/alerts.



## Quick Links

* Kind + local registry https://kind.sigs.k8s.io/docs/user/local-registry/

* Bitnami Kafka chart https://github.com/bitnami/charts/tree/master/bitnami/kafka

* Prometheus Operator https://github.com/prometheus-operator/prometheus-operator

* Loki Operator https://medium.com/@muppedaanvesh/a-hands-on-guide-to-kubernetes-logging-using-grafana-loki-%EF%B8%8F-b8d37ea4de13