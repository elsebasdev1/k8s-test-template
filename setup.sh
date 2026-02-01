#!/bin/bash
# 1. Configurar entorno docker minikube
eval $(minikube docker-env)

# 2. Construir imágenes (Asumiendo que tienes Dockerfiles simples en cada carpeta)
docker build -t receiver:v1 ./apps/receiver
docker build -t processor:v1 ./apps/processor
docker build -t auditor:v1 ./apps/auditor

# 3. Limpiar y Aplicar K8s
kubectl delete all --all
kubectl apply -f k8s/

# 4. Esperar y Mostrar URL
echo "Esperando pods..."
kubectl wait --for=condition=ready pod --all --timeout=60s
minikube service receiver-svc