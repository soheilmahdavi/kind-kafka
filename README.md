# ÖBB DevOps Assessment – Kafka Prototype

Two Python micro-services illustrate how internal applications will publish to
and consume from ÖBB’s Kafka integration platform.

| Path | Purpose |
|------|---------|
| `kafka-producer/` | One-shot job that publishes *N* demo messages. |
| `kafka-consumer/` | Deployment that streams messages to `stdout`. |
| `infra/k8s/`      | Kubernetes YAML: shared `ConfigMap`, producer `Job`, consumer `Deployment`. |
| `requirements.txt`| Common Python deps (`kafka-python`, `python-dotenv`). |

> **No Kafka broker is required** for the practical part of the assignment.
> Containers log a graceful “cannot connect” message if no broker is present.
> A Helm snippet is provided for reviewers who want an end-to-end demo.

---

## 📑 Table of Contents

1. [Prerequisites](#1-prerequisites)  
2. [Build & Push Images](#2-build--push-images)  
3. [Deploy to Kubernetes](#3-deploy-to-kubernetes)  
4. [Optional – Run a Broker in _kind_](#4-optional--run-a-broker-in-kind)  
5. [Clean-up](#5-clean-up)  
6. [Monitoring & Observability](#6-monitoring--observability)  
7. [Image-Hardening Checklist](#7-image-hardening-checklist)  
8. [Quick Links](#quick-links)

---

## 1  Prerequisites

* Docker 24 + BuildKit  
* Kubernetes ≥ 1.27 (tested with **kind**)  
* Helm v3 (if you want the optional broker test)

---

## 2  Build & Push Images

```bash
# build
docker build -t localhost:5000/kafka-producer:1.0.0 -f kafka-producer/Dockerfile .
docker build -t localhost:5000/kafka-consumer:1.0.0 -f kafka-consumer/Dockerfile .

# push to local registry (kind-registry on port 5000)
docker push localhost:5000/kafka-producer:1.0.0
docker push localhost:5000/kafka-consumer:1.0.0
