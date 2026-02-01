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

# 4. Frontend (Interfaz Web)
docker build -t frontend:v1 ./apps/frontend
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

---

## 🪟 INSTALACIÓN EN WINDOWS (MODO GRÁFICO – SIN WSL)

Esta opción es para usuarios que **NO quieren usar WSL ni terminal Linux**.  
Todo se instala mediante **instaladores `.exe`** en Windows.

---

### 1. Instalar Docker Desktop (Incluye Kubernetes)

Docker Desktop para Windows **ya incluye Kubernetes**, por lo que **no necesitas Minikube** en este modo.

#### Pasos:

1. Descarga Docker Desktop desde el sitio oficial:  
   https://www.docker.com/products/docker-desktop/

2. Ejecuta el instalador `.exe`

3. Durante la instalación:
   - ✅ Deja activada la opción **"Use WSL 2 instead of Hyper-V"** (recomendado)
   - (Si no tienes WSL, Docker Desktop lo instalará automáticamente)

4. Reinicia Windows si el instalador lo solicita

5. Abre **Docker Desktop** y espera a que esté en estado **Running**

---

### 2. Activar Kubernetes en Docker Desktop

1. Abre **Docker Desktop**
2. Ve a **Settings**
3. En el menú lateral, selecciona **Kubernetes**
4. Marca la opción:
   - ✅ **Enable Kubernetes**
5. Haz clic en **Apply & Restart**
6. Espera a que el clúster esté listo (puede tardar varios minutos)

Cuando termine, verás el estado:
> Kubernetes is running

---

### 3. Instalar kubectl (Windows .exe)

Docker Desktop **puede instalar kubectl automáticamente**, pero si no:

1. Descarga kubectl para Windows desde:  
   https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/

2. Descarga el archivo:
   - `kubectl.exe`

3. Copia `kubectl.exe` en una carpeta incluida en tu `PATH`, por ejemplo:
   - `C:\Windows\System32`
   - o `C:\Program Files\kubectl\` (agregando al PATH)

4. Verifica instalación abriendo **PowerShell** o **CMD**:

```powershell
kubectl version --client
```

---

### 4. Verificar acceso al clúster Kubernetes

Docker Desktop configura automáticamente el contexto.

Verifica con:

```powershell
kubectl get nodes
```

Resultado esperado:
- 1 nodo en estado **Ready**
- Nombre similar a `docker-desktop`

---

### 5. Construcción de imágenes (Docker Desktop)

En este modo **NO necesitas** `minikube docker-env`.

Docker Desktop ya expone su Docker Engine al sistema.

Desde **PowerShell**, en la raíz del proyecto:

```powershell
docker build -t receiver:v1 ./apps/receiver
docker build -t processor:v1 ./apps/processor
docker build -t auditor:v1 ./apps/auditor
```

---

### 6. Despliegue en Kubernetes (Docker Desktop)

Aplica los manifiestos normalmente:

```powershell
kubectl apply -f k8s/
kubectl get pods -w
```

---

### 📝 Notas importantes para Windows GUI

- ✅ **No se usa Minikube**
- ✅ **No se usa WSL manualmente**
- ✅ Kubernetes corre dentro de Docker Desktop
- ⚠️ `minikube service` **NO aplica** aquí
- Para exponer servicios, usa:
  - `kubectl port-forward`
  - o `Service type: NodePort / LoadBalancer`
**Solución:**  
Revisar `k8s/01-config.yaml` y `k8s/02-services.yaml`.

## ⚡ GUÍA DE EJECUCIÓN (EL DÍA DEL EXAMEN)

Abre 3 pestañas de tu terminal WSL (Ubuntu) y sigue estos pasos.

==============================
🖥️ TERMINAL 1: EL DESPLIEGUE (SETUP)
==============================
Esta terminal se encarga de construir las imágenes y levantar Kubernetes.

# 1. Inicia Minikube (Solo si no está corriendo)
minikube start --driver=docker

# 2. Ejecuta el script de instalación (Sin permisos previos)
# Usamos 'bash' directamente para evitar el error de permisos en Windows
bash setup.sh

# 3. Verifica que los 4 pods estén en estado "Running"
kubectl get pods


==============================
🖥️ TERMINAL 2: EL ACCESO (PORT FORWARD)
==============================
Aquí abrimos los túneles para conectar Windows con el clúster.
Si el comando con & te da problemas, abre una 4ta pestaña y ejecuta uno en cada una.

# Exponemos el Frontend (Puerto 8000) y el Backend (Puerto 8080) a la vez
kubectl port-forward service/frontend-svc 8000:80 &
kubectl port-forward service/receiver-svc 8080:8080

(Mantén esta terminal abierta y no la cierres.
Si necesitas cancelarlo, usa Ctrl + C)


==============================
🖥️ TERMINAL 3: EVIDENCIA (LOGS)
==============================
Esta terminal es para mostrarle al profesor que el sistema funciona.

# Dejamos corriendo los logs del Auditor (el último nodo del anillo)
kubectl logs -f -l app=auditor


==============================
🏁 CÓMO PRESENTAR LA PRUEBA
==============================

Abre tu navegador en Windows:
http://localhost:8000

Formulario:
ID: ExamenFinal
Valor: 10 (Si es par, se multiplica. Si es impar, suma 1)

Ejecutar:
Clic en "Iniciar Ciclo"

Verificar:
- Navegador: JSON final con el array audit lleno
- Terminal 3: CICLO COMPLETADO: {...}
