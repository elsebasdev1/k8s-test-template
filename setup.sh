#!/bin/bash

# 1. Configurar entorno docker minikube (Detecta automáticamente la shell)
eval $(minikube docker-env)

echo "🏗️  Construyendo imágenes..."
# 2. Construir imágenes (Incluyendo el Frontend que faltaba)
docker build -t receiver:v1 ./apps/receiver
docker build -t processor:v1 ./apps/processor
docker build -t auditor:v1 ./apps/auditor
docker build -t frontend:v1 ./apps/frontend

echo "🧹 Limpiando cluster anterior..."
# 3. Limpiar y Aplicar K8s
kubectl delete all --all
kubectl apply -f k8s/

echo "⏳ Esperando a que los pods estén listos..."
# 4. Esperar a que todo esté en Running
kubectl wait --for=condition=ready pod --all --timeout=120s

echo "✅ ¡Despliegue completado!"
echo "👉 Ve a la Terminal 2 para activar el acceso."