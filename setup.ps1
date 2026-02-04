# 1. Conectar la terminal al Docker de Minikube (Comando mágico de Windows)
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

Write-Host "🏗️  Construyendo imágenes..." -ForegroundColor Cyan

# 2. Construir imágenes
docker build -t receiver:v1 ./apps/receiver
docker build -t processor:v1 ./apps/processor
docker build -t auditor:v1 ./apps/auditor
docker build -t frontend:v1 ./apps/frontend

# 3. Limpiar y Aplicar K8s
Write-Host "🧹 Limpiando cluster anterior..." -ForegroundColor Yellow
kubectl delete all --all
kubectl apply -f k8s/

# 4. Esperar a que todo esté listo
Write-Host "⏳ Esperando a que los pods estén listos..." -ForegroundColor Cyan
kubectl wait --for=condition=ready pod --all --timeout=120s

Write-Host "✅ ¡Despliegue completado!" -ForegroundColor Green
Write-Host "👉 Ve a la siguiente terminal para activar el acceso." -ForegroundColor White