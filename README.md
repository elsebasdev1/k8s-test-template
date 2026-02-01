# 🚀 K8S EXAM MASTER KIT: Arquitectura Distribuida

Este repositorio despliega una arquitectura de **3 Nodos (Microservicios)** conectados secuencialmente (Topología de Anillo/Lineal) sobre Kubernetes.

---

## 🛠️ FASE 0: INSTALACIÓN DE HERRAMIENTAS (Máquina de Laboratorio)

Si la máquina está vacía, ejecuta estos bloques paso a paso.  
*Nota: Se asume entorno Linux (Ubuntu/Debian/CentOS). Requiere permisos `sudo`.*

### 1. Instalar Docker

```bash
# Actualizar e instalar básicos
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Instalar Docker Engine (Script oficial rápido)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Dar permisos al usuario (Vital para no usar sudo con docker)
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Instalar Kubectl (El control remoto)

```bash
# Descargar binario
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Instalar
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verificar
kubectl version --client
```

### 3. Instalar Minikube (El Clúster Local)

```bash
# Descargar e instalar
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Arrancar el clúster con driver Docker
minikube start --driver=docker
```

---

## ⚡ FASE 1: PREPARACIÓN DEL ENTORNO

⚠️ **PASO CRÍTICO**  
Debemos conectar nuestra terminal al Docker que vive **DENTRO** de Minikube.  
Si no haces esto, Kubernetes no encontrará las imágenes que construyas.

```bash
eval $(minikube docker-env)
```

(Si usas otra shell como Fish: `minikube docker-env | source`)

---

## 🏗️ FASE 2: CONSTRUCCIÓN (BUILD)

Construimos las imágenes de los 3 nodos usando los Dockerfile locales.  
Asegúrate de estar en la raíz del proyecto.

```bash
# 1. Nodo A (Receptor HTTP)
docker build -t receiver:v1 ./apps/receiver

# 2. Nodo B (Lógica de Negocio/Matemática)
docker build -t processor:v1 ./apps/processor

# 3. Nodo C (Auditor/Log)
docker build -t auditor:v1 ./apps/auditor
```

Verificación:

```bash
docker images
```

Debes ver `receiver`, `processor` y `auditor`.

---

## 🚀 FASE 3: DESPLIEGUE (DEPLOY)

Aplicamos los manifiestos de Kubernetes.

```bash
# Limpiar cualquier rastro anterior
kubectl delete all --all

# Aplicar toda la carpeta k8s
kubectl apply -f k8s/
```

Monitorear Pods:

```bash
kubectl get pods -w
```

---

## 🌐 FASE 4: ACCESO Y PRUEBA FINAL

### 1. Exponer el servicio

```bash
# Opción A: URL directa
minikube service receiver-svc

# Opción B: Port Forward
kubectl port-forward service/receiver-svc 8080:5000
```

### 2. Disparar la prueba

```bash
curl -X POST http://localhost:8080/start \
  -H "Content-Type: application/json" \
  -d '{
        "id": "test-01",
        "value": 50,
        "audit": []
      }'
```

### 3. Resultado esperado

```json
{
  "id": "test-01",
  "value": 100,
  "audit": [
    "Multiplied by 2 (Even)",
    "Audit Completed"
  ],
  "status": "FINISHED"
}
```

---

## 🚑 SOLUCIÓN DE PROBLEMAS

### ImagePullBackOff / ErrImagePull

**Causa:**  
No usaste `eval $(minikube docker-env)`.

**Solución:**  
Repite FASE 1 y FASE 2.

---

### CrashLoopBackOff

```bash
kubectl logs <nombre-del-pod>
```

---

### Nodo A no conecta con Nodo B

**Causa:**  
Nombre incorrecto del Service en ConfigMap.

**Solución:**  
Revisar `k8s/01-config.yaml` y `k8s/02-services.yaml`.
