# Kubernetes Manifests

## Overview
Kubernetes manifests for deploying LearningSteps API to Azure Kubernetes Service.

## Files

- `namespace.yaml` - Production namespace
- `configmap.yaml` - Non-sensitive configuration
- `deployment.yaml` - API deployment with 2 replicas
- `service.yaml` - LoadBalancer service (or ClusterIP with Ingress)
- `hpa.yaml` - Horizontal Pod Autoscaler
- `ingress.yaml` - HTTPS ingress with TLS
- `cluster-issuer.yaml` - Let's Encrypt certificate issuer

## Prerequisites

- AKS cluster running and kubectl configured
- Container image pushed to ACR
- Secrets created (see SECRET-SETUP.md)

## Deployment Steps

### 1. Create namespace and config
```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
```

### 2. Create secrets
Follow instructions in `SECRET-SETUP.md`

### 3. Deploy application
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
```

### 4. Setup HTTPS (optional)
Requires cert-manager and nginx-ingress installed:
```bash
kubectl apply -f cluster-issuer.yaml
kubectl apply -f ingress.yaml
```

## Verify Deployment
```bash
# Check all resources
kubectl get all -n production

# Check pods
kubectl get pods -n production

# Check logs
kubectl logs -l app=learningsteps-api -n production --tail=50

# Get external IP (if using LoadBalancer)
kubectl get service learningsteps-api -n production
```

## Update Deployment

After pushing new image:
```bash
kubectl rollout restart deployment/learningsteps-api -n production
kubectl rollout status deployment/learningsteps-api -n production
```

## Troubleshooting

### Image pull errors
```bash
# Check ACR integration
az aks check-acr \
  --resource-group learningsteps-rg \
  --name learningsteps-aks \
  --acr learningstepsacr.azurecr.io
```

### Pod issues
```bash
kubectl describe pod <pod-name> -n production
kubectl logs <pod-name> -n production
```
