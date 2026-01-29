cat > README.md << 'EOF'
# LearningSteps API - Cloud-Native DevOps Capstone

A production-ready FastAPI application deployed on Azure Kubernetes Service (AKS) with complete CI/CD automation, Infrastructure as Code, and security best practices.

🌐 **Live Demo:** https://api.learningsteps.cloud/docs

---

## 🏗️ Architecture
```
Internet (HTTPS)
    ↓
api.learningsteps.cloud
    ↓
NGINX Ingress + Let's Encrypt
    ↓
Kubernetes Service (ClusterIP)
    ↓
API Pods (2 replicas + Auto-scaling)
    ↓
PostgreSQL Flexible Server (Private Network)
```

---

## 🚀 Features

- ✅ **Containerization** - Multi-stage Docker builds for production
- ✅ **Infrastructure as Code** - Complete Azure infrastructure managed by Terraform
- ✅ **Kubernetes Orchestration** - Deployment, auto-scaling, health checks
- ✅ **CI/CD Pipeline** - Automated testing, security scanning, deployment
- ✅ **HTTPS/SSL** - Automatic certificate management with Let's Encrypt
- ✅ **Secret Management** - Azure Key Vault integration
- ✅ **Private Networking** - Database isolated in private subnet
- ✅ **Security Scanning** - Container vulnerabilities (Trivy), secrets (TruffleHog)

---

## 📦 Tech Stack

**Application:**
- FastAPI (Python 3.11)
- PostgreSQL 15
- JWT Authentication
- AsyncPG

**Infrastructure:**
- Azure Kubernetes Service (AKS)
- Azure Container Registry (ACR)
- Azure PostgreSQL Flexible Server
- Azure Key Vault
- Azure Virtual Network

**DevOps:**
- Terraform (Infrastructure as Code)
- GitHub Actions (CI/CD)
- Docker (Containerization)
- Kubernetes (Orchestration)
- NGINX Ingress Controller
- cert-manager (SSL certificates)

---

## 🚦 Getting Started

### Prerequisites
- Azure CLI
- Terraform >= 1.0
- kubectl
- Docker

### 1. Infrastructure Setup
```bash
cd infra-terraform
terraform init
terraform apply
```

See [infra-terraform/README.md](infra-terraform/README.md) for detailed setup.

### 2. Deploy to Kubernetes
```bash
cd k8s-manifests

# Create secrets from Key Vault
# See SECRET-SETUP.md for instructions

# Deploy application
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

# Setup HTTPS
kubectl apply -f cluster-issuer.yaml
kubectl apply -f ingress.yaml

# Initialize database
kubectl apply -f db-init-job.yaml
```

See [k8s-manifests/README.md](k8s-manifests/README.md) for detailed deployment steps.

---

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline automatically:

1. **Tests** - Lints Python code, runs tests
2. **Scans** - Checks for secrets and vulnerabilities
3. **Builds** - Creates Docker image for AMD64
4. **Pushes** - Uploads to Azure Container Registry
5. **Deploys** - Updates Kubernetes deployment
6. **Verifies** - Health checks after deployment

**Trigger:** Push to `main` branch

---

## 🔐 Security

- Private database with no public access
- Network Security Groups restrict traffic
- Secrets stored in Azure Key Vault
- No hardcoded credentials in code
- Automated vulnerability scanning
- HTTPS enforced with valid SSL certificates

---

## 📊 API Endpoints

**Health Check:**
```bash
GET /health
```

**Authentication:**
```bash
POST /auth/login?username=admin&password=admin
```

**Entries:**
```bash
GET    /v1/entries       # List all entries
GET    /v1/entries/{id}  # Get specific entry
POST   /v1/entries       # Create entry (auth required)
PATCH  /v1/entries/{id}  # Update entry (auth required)
DELETE /v1/entries/{id}  # Delete entry (auth required)
```

**Documentation:**
- Swagger UI: https://api.learningsteps.cloud/docs
- ReDoc: https://api.learningsteps.cloud/redoc

---

## 🧪 Testing
```bash
# Health check
curl https://api.learningsteps.cloud/health

# Get token
TOKEN=$(curl -s -X POST "https://api.learningsteps.cloud/auth/login?username=admin&password=admin" | jq -r '.access_token')

# Create entry
curl -X POST https://api.learningsteps.cloud/v1/entries \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"work": "test", "struggle": "none", "intention": "learn"}'
```

---

## 📝 Project Structure
```
learningsteps/
├── .github/workflows/    # CI/CD pipelines
├── api/                  # FastAPI application code
├── infra-terraform/      # Terraform infrastructure
├── k8s-manifests/        # Kubernetes manifests
├── Dockerfile            # Container definition
└── requirements.txt      # Python dependencies
```

---

## 🎓 Capstone Requirements Met

- ✅ Containerization with production-grade Dockerfile
- ✅ Infrastructure as Code (Terraform)
- ✅ DevSecOps with security scanning in pipeline
- ✅ CI/CD with GitHub Actions
- ✅ Kubernetes orchestration on AKS
- ✅ Horizontal Pod Autoscaling
- ✅ HTTPS with automatic certificate management
- ✅ Private database networking
- ✅ Secret management with Azure Key Vault

---

## 🧹 Cleanup

To destroy all infrastructure:
```bash
cd infra-terraform
terraform destroy
```

**Warning:** This will delete all resources including the database!

---

## 📚 Documentation

- [Terraform Setup Guide](infra-terraform/README.md)
- [Kubernetes Deployment Guide](k8s-manifests/README.md)
- [Secret Management](k8s-manifests/SECRET-SETUP.md)

---

## 👨‍💻 Author

Stanislav Safaniuk

---

## 📜 License

MIT License