# Kubernetes Manifests

## Overview
Kubernetes manifests for deploying the LearningSteps API to Azure Kubernetes Service (AKS).

---

## 📁 Files

| File | Purpose |
|------|---------|
| `namespace.yaml` | Production namespace |
| `configmap.yaml` | Non-sensitive configuration |
| `deployment.yaml` | API deployment with 2 replicas |
| `service.yaml` | ClusterIP service |
| `hpa.yaml` | Horizontal Pod Autoscaler |
| `ingress.yaml` | HTTPS ingress with TLS |
| `cluster-issuer.yaml` | Let's Encrypt certificate issuer |
| `db-init-job.yaml` | Database initialization job |
| `SECRET-SETUP.md` | Instructions for creating secrets |

---

## 🚀 Deployment Steps

### Prerequisites

1. **AKS cluster running** and `kubectl` configured
```bash
   az aks get-credentials \
     --resource-group learningsteps-rg \
     --name learningsteps-aks
```

2. **Container image pushed to ACR**
```bash
   az acr login --name learningstepsacr
   docker buildx build --platform linux/amd64 \
     -t learningstepsacr.azurecr.io/learningsteps-api:latest \
     --push .
```

3. **Secrets created from Key Vault**  
   See [SECRET-SETUP.md](SECRET-SETUP.md) for detailed instructions

---

### Step 1: Create Namespace and ConfigMap
```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
```

---

### Step 2: Create Secrets

Follow the instructions in [SECRET-SETUP.md](SECRET-SETUP.md) to create secrets from Azure Key Vault.

Quick version:
```bash
# Get secrets from Key Vault
cd ../infra-terraform
DATABASE_URL=$(terraform output -raw database_connection_string)
JWT_SECRET=$(az keyvault secret show \
  --vault-name learningsteps-kv \
  --name jwt-secret-key \
  --query value -o tsv)

# Create Kubernetes secret
cd ../k8s-manifests
kubectl create secret generic learningsteps-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=JWT_SECRET_KEY="$JWT_SECRET" \
  --namespace=production
```

---

### Step 3: Deploy Application
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
```

Watch deployment:
```bash
kubectl get pods -n production -w
```

---

### Step 4: Initialize Database
```bash
kubectl apply -f db-init-job.yaml

# Watch job complete
kubectl get jobs -n production -w

# Check logs
kubectl logs -l job-name=db-init-job -n production

# Clean up job after success
kubectl delete job db-init-job -n production
```

---

### Step 5: Setup HTTPS (Optional)

Requires cert-manager and nginx-ingress-controller installed:
```bash
# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.crds.yaml
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.13.3

# Apply ingress and certificate issuer
kubectl apply -f cluster-issuer.yaml
kubectl apply -f ingress.yaml

# Wait for certificate
kubectl get certificate -n production -w
```

---

## ✅ Verify Deployment

### Check Resources
```bash
# All resources in production namespace
kubectl get all -n production

# Pods status
kubectl get pods -n production

# Service and external IP
kubectl get service -n production

# Ingress and certificate
kubectl get ingress,certificate -n production

# HPA status
kubectl get hpa -n production
```

### Check Logs
```bash
# All pod logs
kubectl logs -l app=learningsteps-api -n production --tail=50

# Follow logs in real-time
kubectl logs -l app=learningsteps-api -n production -f

# Specific pod
kubectl logs <pod-name> -n production
```

### Test API
```bash
# Health check (via LoadBalancer)
EXTERNAL_IP=$(kubectl get service learningsteps-api -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$EXTERNAL_IP/health

# Or via domain (if ingress configured)
curl https://api.learningsteps.cloud/health
```

---

## 🔄 Update Deployment

### After Pushing New Image
```bash
# Update image
kubectl set image deployment/learningsteps-api \
  api=learningstepsacr.azurecr.io/learningsteps-api:latest \
  -n production

# Or restart deployment to pull latest
kubectl rollout restart deployment/learningsteps-api -n production

# Watch rollout
kubectl rollout status deployment/learningsteps-api -n production

# Verify new pods
kubectl get pods -n production
```

---

## 🐛 Troubleshooting

### Pods Not Starting

**ImagePullBackOff:**
```bash
# Check ACR integration
az aks check-acr \
  --resource-group learningsteps-rg \
  --name learningsteps-aks \
  --acr learningstepsacr.azurecr.io

# Re-attach ACR if needed
az aks update \
  --resource-group learningsteps-rg \
  --name learningsteps-aks \
  --attach-acr learningstepsacr
```

**CrashLoopBackOff:**
```bash
# Check pod logs
kubectl logs <pod-name> -n production

# Check previous container logs
kubectl logs <pod-name> -n production --previous

# Describe pod for events
kubectl describe pod <pod-name> -n production
```

### Database Connection Issues
```bash
# Check if secret exists
kubectl get secret learningsteps-secrets -n production

# Verify secret values (careful with credentials!)
kubectl get secret learningsteps-secrets -n production -o jsonpath='{.data.DATABASE_URL}' | base64 -d
echo ""

# Test database from pod
POD=$(kubectl get pods -n production -l app=learningsteps-api -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD -n production -- env | grep DATABASE
```

### Certificate Not Issuing
```bash
# Check certificate status
kubectl describe certificate learningsteps-tls -n production

# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager

# Check certificate request
kubectl get certificaterequest -n production

# Check challenge (if http01)
kubectl get challenge -n production
```

### Service Not Accessible
```bash
# Check service endpoints
kubectl get endpoints learningsteps-api -n production

# Check if pods are ready
kubectl get pods -n production

# Describe service
kubectl describe service learningsteps-api -n production

# Check ingress
kubectl describe ingress learningsteps-ingress -n production
```

---

## 🧹 Cleanup

### Delete Application
```bash
kubectl delete -f deployment.yaml
kubectl delete -f service.yaml
kubectl delete -f hpa.yaml
kubectl delete -f ingress.yaml
```

### Delete Namespace (removes everything)
```bash
kubectl delete namespace production
```

---

## 📊 Monitoring

### Resource Usage
```bash
# Pod resource usage
kubectl top pods -n production

# Node resource usage
kubectl top nodes
```

### Events
```bash
# Recent events
kubectl get events -n production --sort-by='.lastTimestamp'

# Watch events
kubectl get events -n production -w
```

### HPA Scaling
```bash
# Watch HPA
kubectl get hpa -n production -w

# Generate load to test scaling
kubectl run -it --rm load-generator \
  --image=busybox \
  --restart=Never \
  -- /bin/sh -c "while true; do wget -q -O- http://learningsteps-api.production/health; done"
```

---

## 📝 Notes

- **Secrets are NOT stored in Git** - Always create them from Key Vault
- **Database is private** - Only accessible from within the VNET
- **Images must be AMD64** - Build with `--platform linux/amd64`
- **HPA requires metrics-server** - Should be enabled by default in AKS
- **Ingress requires ingress controller** - NGINX ingress recommended

---

## 🔗 Related Documentation

- [Secret Setup Instructions](SECRET-SETUP.md)
- [Terraform Infrastructure](../infra-terraform/README.md)
- [Main Project README](../README.md)
