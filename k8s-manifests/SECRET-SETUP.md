# Kubernetes Secrets Setup

## ⚠️ Important
Secrets are **NOT stored in Git**. They must be created manually from Azure Key Vault values.

---

## 🔐 Create Secrets from Azure Key Vault

### Prerequisites
- Terraform infrastructure deployed
- Azure CLI logged in
- kubectl configured for AKS cluster

---

## Step-by-Step Instructions

### 1. Navigate to Terraform Directory
```bash
cd ~/learningsteps/learningsteps/infra-terraform
```

### 2. Get Database Connection String

The database URL needs proper URL encoding to handle special characters in the password:
```bash
# Get database details
DB_HOST=$(az postgres flexible-server show \
  --resource-group learningsteps-rg \
  --name learningsteps-postgres \
  --query fullyQualifiedDomainName -o tsv)

DB_USER=$(az postgres flexible-server show \
  --resource-group learningsteps-rg \
  --name learningsteps-postgres \
  --query administratorLogin -o tsv)

# Get password from Key Vault
DB_PASS=$(az keyvault secret show \
  --vault-name learningsteps-kv \
  --name database-password \
  --query value -o tsv)

DB_NAME="learningsteps"

# URL encode the password (handles special characters)
DB_PASS_ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$DB_PASS', safe=''))")

# Create properly formatted connection string
DATABASE_URL="postgresql://${DB_USER}:${DB_PASS_ENCODED}@${DB_HOST}:5432/${DB_NAME}?sslmode=require"

# Verify it's not empty
echo "DATABASE_URL length: ${#DATABASE_URL}"
```

### 3. Get JWT Secret
```bash
JWT_SECRET=$(az keyvault secret show \
  --vault-name learningsteps-kv \
  --name jwt-secret-key \
  --query value -o tsv)

# Verify it's not empty
echo "JWT_SECRET length: ${#JWT_SECRET}"
```

### 4. Create Kubernetes Namespace (if not exists)
```bash
cd ../k8s-manifests
kubectl apply -f namespace.yaml
```

### 5. Create the Secret
```bash
kubectl create secret generic learningsteps-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=JWT_SECRET_KEY="$JWT_SECRET" \
  --namespace=production
```

Expected output:
```
secret/learningsteps-secrets created
```

---

## ✅ Verify Secret Creation
```bash
# Check secret exists
kubectl get secret learningsteps-secrets -n production

# Describe secret (doesn't show values)
kubectl describe secret learningsteps-secrets -n production

# View secret keys (not values)
kubectl get secret learningsteps-secrets -n production -o jsonpath='{.data}' | jq 'keys'
```

---

## 🔄 Update Existing Secrets

If you need to update secrets:
```bash
# Delete existing secret
kubectl delete secret learningsteps-secrets -n production

# Recreate with new values (follow steps above)
kubectl create secret generic learningsteps-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=JWT_SECRET_KEY="$JWT_SECRET" \
  --namespace=production

# Restart pods to pick up new secret
kubectl rollout restart deployment/learningsteps-api -n production
```

---

## 🐛 Troubleshooting

### Error: "Invalid IPv6 URL"
This means the password has special characters that aren't URL-encoded.

**Solution:** Make sure you're using the URL-encoded version (step 2 above with `urllib.parse.quote`)

### Error: Secret already exists
```bash
# Delete and recreate
kubectl delete secret learningsteps-secrets -n production
# Then create again
```

### Pods show "degraded" database status
```bash
# Restart pods to pick up new secret
kubectl rollout restart deployment/learningsteps-api -n production

# Check pod logs
kubectl logs -l app=learningsteps-api -n production --tail=50
```

### Can't connect to Key Vault
```bash
# Check you're logged in
az account show

# Check Key Vault exists
az keyvault show --name learningsteps-kv

# List secrets (verify they exist)
az keyvault secret list --vault-name learningsteps-kv --output table
```

---

## 🔑 Secret Contents

The `learningsteps-secrets` secret contains:

| Key | Description | Source |
|-----|-------------|--------|
| `DATABASE_URL` | PostgreSQL connection string | Generated from Key Vault components |
| `JWT_SECRET_KEY` | JWT signing secret | Azure Key Vault: `jwt-secret-key` |

---

## 🔒 Security Best Practices

1. **Never commit secrets to Git**
2. **Always use Key Vault as source of truth**
3. **URL-encode passwords** to avoid parsing issues
4. **Rotate secrets regularly**
5. **Limit access to Key Vault** using RBAC
6. **Restart pods** after updating secrets

---

## 📝 Alternative: Using Azure Key Vault CSI Driver (Advanced)

For production, consider using the Azure Key Vault CSI driver to mount secrets directly:
```bash
# Install CSI driver
helm repo add csi-secrets-store-provider-azure https://azure.github.io/secrets-store-csi-driver-provider-azure/charts
helm install csi csi-secrets-store-provider-azure/csi-secrets-store-provider-azure \
  --namespace kube-system
```

This allows automatic secret rotation without pod restarts.

---

## 🔗 Related Documentation

- [Kubernetes Deployment Guide](README.md)
- [Terraform Infrastructure](../infra-terraform/README.md)
- [Azure Key Vault Documentation](https://docs.microsoft.com/en-us/azure/key-vault/)
