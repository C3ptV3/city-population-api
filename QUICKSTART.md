# City Population API - Quick Start Guide

## 🚀 Quick Local Development

1. **Clone and navigate to the project:**
   ```bash
   cd city-population-api/
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Test the API:**
   ```bash
   # Make the test script executable
   chmod +x test_api.sh
   
   # Run tests
   ./test_api.sh
   ```

## 🎯 Quick Kubernetes Deployment

1. **Build and push Docker image:**
   ```bash
   # Build
   docker build -t yourusername/city-population-api:latest .
   
   # Push to Docker Hub
   docker push yourusername/city-population-api:latest
   ```

2. **Deploy with Helm:**
   ```bash
   # Add Elastic repo
   helm repo add elastic https://helm.elastic.co
   helm repo update
   
   # Install
   helm install city-api ./helm/city-population-api \
     --set image.repository=yourusername/city-population-api
   ```

3. **Access the API:**
   ```bash
   # Port forward
   kubectl port-forward service/city-api-city-population-api 5000:80
   
   # Test
   curl http://localhost:5000/health
   ```

## 📚 API Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/health` | Health check | `curl http://localhost:5000/health` |
| POST | `/city` | Insert/Update city | `curl -X POST http://localhost:5000/city -H "Content-Type: application/json" -d '{"city": "Paris", "population": 2161000}'` |
| GET | `/city/{name}` | Get city population | `curl http://localhost:5000/city/Paris` |
| GET | `/cities` | List all cities | `curl http://localhost:5000/cities` |


## 📋 Project Structure

```
city-population-api/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container definition
├── docker-compose.yaml    # Local development
├── helm/                 # Kubernetes deployment
│   └── city-population-api/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
└── QUICKSTART.md             # Full documentation
```

## 🔧 Common Operations

### Update a city's population:
```bash
curl -X PUT http://localhost:5000/city \
  -H "Content-Type: application/json" \
  -d '{"city": "Paris", "population": 2200000}'
```

### Check Elasticsearch directly:
```bash
# Port forward to Elasticsearch
kubectl port-forward service/city-api-elasticsearch-master 9200:9200

# Query Elasticsearch
curl http://localhost:9200/cities/_search
```

### Scale the application:
```bash
# Manual scaling
kubectl scale deployment city-api-city-population-api --replicas=3

# Or use Helm
helm upgrade city-api ./helm/city-population-api --set replicaCount=3
```

## 🐛 Troubleshooting

1. **Pods not starting?**
   ```bash
   kubectl describe pod <pod-name>
   kubectl logs <pod-name>
   ```

2. **Elasticsearch connection issues?**
   ```bash
   # Check Elasticsearch pods
   kubectl get pods -l app=elasticsearch-master
   kubectl logs -l app=elasticsearch-master
   ```

3. **API not responding?**
   ```bash
   # Check service endpoints
   kubectl get endpoints
   kubectl get svc
   ```

