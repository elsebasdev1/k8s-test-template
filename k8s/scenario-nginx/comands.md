Paso 1. Desplegar
### Aplicar el archivo base
kubectl apply -f k8s/scenario-nginx/base.yaml

### Verificar que está corriendo (Captura de pantalla 1)
kubectl get all

---

Paso 2: Validar ClusterIP y Cambiar a NodePort
# Validar acceso interno (ClusterIP)
# Creamos un pod temporal "curl" para probar la IP interna
kubectl run test-curl --image=curlimages/curl -i --tty -- sh
# (Dentro del pod): curl http://nginx-service
# (Sales con exit)

# --- CAMBIAR A NODEPORT ---
# Opción A (Fácil): Parchear el servicio
kubectl patch service nginx-service -p '{"spec": {"type": "NodePort"}}'

# Opción B (Manual): Editar el archivo YAML en vivo
kubectl edit service nginx-service
# (Cambias type: ClusterIP por type: NodePort y guardas)

# Validar acceso externo (Captura de pantalla 2)
minikube service nginx-service --url
# (Copias esa URL y haces curl o la abres en navegador)

---

Paso 3: Escalado a 4 Réplicas
# Comando imperativo para escalar
kubectl scale deployment nginx-exam --replicas=4

# Verificar (Captura de pantalla 3)
kubectl get pods -w
# (Espera a que los 4 digan Running)

---

Paso 4: Actualización de Imagen (Rolling Update)
# Cambiar la imagen de nginxdemos/hello a nginx:alpine
kubectl set image deployment/nginx-exam nginx-container=nginx:alpine

# Observar el proceso de actualización (Captura de pantalla 4)
kubectl rollout status deployment/nginx-exam

# Verificar la nueva versión
kubectl get pods
# (Verás que los pods viejos mueren y nacen nuevos)

---

## 🔵 ESCENARIO: PRUEBA DE INFRAESTRUCTURA (NGINX)
*Usar si el examen pide "nginxdemos/hello", "escalar pods" o "actualizar imagen".*

### 1. Iniciar Limpio
```bash
minikube start --driver=docker
kubectl delete all --all  # Borra cualquier rastro de la app anterior
```

### 2. Despliegue Base
Bash
```bash
kubectl apply -f k8s/scenario-nginx/base.yaml
kubectl get pods
```

### 3. Exposición y Cambio a NodePort
Bash
```bash
# 1. Verificar que existe como ClusterIP
kubectl get svc

# 2. Cambiar a NodePort (Requerido por el examen)
kubectl patch service nginx-service -p '{"spec": {"type": "NodePort"}}'

# 3. Obtener URL para captura de pantalla
minikube service nginx-service
```

### 4. Escalar a 4 Réplicas
Bash
```bash
kubectl scale deployment nginx-exam --replicas=4
# Tomar captura cuando todos estén en "Running"
kubectl get pods
```

### 5. Actualizar Imagen (Update)
Bash
```bash
# Cambiar imagen
kubectl set image deployment/nginx-exam nginx-container=nginx:alpine

# Verificar el cambio
kubectl rollout status deployment/nginx-exam
kubectl describe pod <nombre-de-un-pod-nuevo> | grep Image
```
