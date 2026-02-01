# 🚀 K8S EXAM MASTER KIT: Arquitectura Distribuida

Este repositorio despliega una arquitectura de **3 Nodos (Microservicios)** conectados secuencialmente (Topología de Anillo/Lineal) sobre Kubernetes.

---

## 🛠️ FASE 0: INSTALACIÓN EN WINDOWS (WSL 2)

*Ejecuta estos comandos DENTRO de tu terminal WSL (Ubuntu/Debian).*

### 1. Preparar dependencias (Vital para WSL)

Minikube en WSL necesita `conntrack` para gestionar la red, o fallará al arrancar.

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg conntrack
```

### 2. Instalar Docker Engine (En WSL)

**Nota:**  
Si ya tienes **Docker Desktop** instalado en Windows, puedes **saltar este paso** y solo asegurar que la opción  
**"Use WSL 2 based engine"** esté activa en los settings de Docker Desktop.

Si no tienes Docker Desktop, instálalo nativo en WSL:

```bash
# Instalar script oficial
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Dar permisos al usuario actual
sudo usermod -aG docker $USER
newgrp docker

# ⚠️ EN WSL EL SERVICIO NO ARRANCA SOLO:
sudo service docker start
```

### 3. Instalar Kubectl & Minikube (Binarios Linux)

Aunque estás en Windows, tu terminal WSL usa binarios de Linux.

```bash
# Kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

---

## ⚡ FASE 1: ARRANQUE Y ENTORNO

### 1. Iniciar el Clúster

En WSL, a veces es necesario forzar el driver de Docker explícitamente y asegurar permisos si hay problemas de cgroups.

```bash
# Asegúrate que el demonio de docker corre
sudo service docker status
# Si dice "not running", ejecuta:
sudo service docker start

# Iniciar Minikube
minikube start --driver=docker
```

### 2. Conectar Shell (CRÍTICO)

Este paso es igual que en Linux puro, pero **fundamental**.

```bash
eval $(minikube docker-env)
```

### 📝 Resumen de cambios hechos para WSL

1. **Dependencia `conntrack`:**  
   Agregada. Sin esto, Minikube en WSL falla por red.

2. **Servicio Docker:**  
   Uso de `sudo service docker start` en lugar de `systemctl`, más compatible con WSL.

3. **Nota Docker Desktop:**  
   Se aclara que si se usa Docker Desktop con WSL 2, se puede omitir la instalación de Docker en WSL.


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
