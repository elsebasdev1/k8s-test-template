# 🛑 FASE 0: PREPARACIÓN DE LA MÁQUINA (Windows)

> Usar **Windows + Docker Desktop + Minikube**.  
> Instalación pensada para laboratorio rápido y sin configuración compleja.

---

## 1️⃣ Instalar Docker Desktop (Windows)

Descarga oficial (.exe):  
https://www.docker.com/products/docker-desktop/

### Pasos
1. Ejecutar el instalador
2. Durante la instalación, **si aparece la opción**, marcar:
   - `Use WSL 2 instead of Hyper-V`
3. Finalizar la instalación
4. Reiniciar Windows
5. Abrir **Docker Desktop** y esperar a que diga **Docker is running**

---

## 2️⃣ Instalar kubectl (Windows)

Descarga directa (.exe):  
https://dl.k8s.io/release/v1.30.0/bin/windows/amd64/kubectl.exe

### Instalación
1. Crear carpeta:
C:\Program Files\kubectl\

2. Copiar `kubectl.exe` dentro
3. Agregar esa carpeta al **PATH** de Windows

### Verificación
```powershell
kubectl version --client
3️⃣ Instalar Minikube (Windows)
Descarga oficial (.exe):
https://storage.googleapis.com/minikube/releases/latest/minikube-installer.exe

Verificación
minikube version
4️⃣ Iniciar Kubernetes local
En PowerShell o Windows Terminal:

minikube start --driver=docker
Verificación
kubectl get nodes
Salida esperada:

minikube   Ready   control-plane


🟢 FASE 1: EL DESPLIEGUE ESTÁNDAR (Síncrono)
Esto es lo primero que haces al sentarte. Muestra que el sistema base funciona.

Paso 1: Encender Motores
En tu Terminal 1:

```
minikube start --driver=docker
eval $(minikube docker-env)  # <--- SI OLVIDAS ESTO, FALLARÁ TODO
```

Paso 2: Ejecutar el Script Maestro
bash setup.sh

(Esto construirá las imágenes, borrará lo viejo y desplegará lo nuevo).

Paso 3: Abrir Accesos (Terminal 2)
Deja esta terminal abierta y no la toques.

```
# Exponer Frontend (8000) y Backend (8080)
kubectl port-forward service/frontend-svc 8000:80 & \
kubectl port-forward service/receiver-svc 8080:8080
```

Paso 4: Verificar (Terminal 3)
kubectl logs -f -l app=auditor

Ve al navegador: http://localhost:8000 -> Click "Iniciar Ciclo". Si ves el JSON y el log: YA TIENES EL 70% DE LA NOTA.

🟡 FASE 2: ADAPTACIÓN (Lo que pida el Profesor)
Caso A: "Cambien la lógica matemática"
Pedido: "Quiero que si el número es par reste 5, y si es impar multiplique por 10".

Edita apps/processor/app.py.

Busca la función process():

```
# CAMBIA ESTO:
if val % 2 == 0:
    data['value'] = val - 5  # <--- Nueva lógica
else:
    data['value'] = val * 10 # <--- Nueva lógica
```

Terminal 1: Ejecuta bash setup.sh.

Listo. Prueba en el navegador.

Caso B: "Quiero Arquitectura Asíncrona / Colas / Workers"
Pedido: "El servicio B debe encolar el mensaje y el C debe procesarlo después sin bloquear".

Intercambio de Archivos:

Ve a apps/processor/. Copia todo el contenido de app-async.py y pégalo dentro de app.py (sobrescribir).

Ve a apps/auditor/. Copia todo el contenido de app-async.py y pégalo dentro de app.py (sobrescribir).

Reconstruir:

Terminal 1: Ejecuta bash setup.sh.

Verificar:

Dale al botón en el Frontend.

Verás una respuesta inmediata: status: QUEUED.

En la Terminal 3 verás: 👷 [WORKER] Procesando....

Caso C: "Sistema de Mensajería / Chat"
Pedido: "El usuario manda un mensaje y se guarda en un historial".

Esto es igual al Caso B (Asíncrono).

Aplica el Caso B (Swap de archivos a async).

En el Frontend, en vez de enviar un número, escribe texto en el campo ID o crea un campo nuevo si te da tiempo (sino, usa el ID como mensaje).

El Auditor (que ahora es Worker) lo guardará en Postgres automáticamente.

Caso D: "Guardar en Archivo de Texto (No en BD)"
Pedido: "El auditor debe escribir en un archivo log.txt dentro del pod".

Edita apps/auditor/app.py.

Busca la parte donde guarda en DB y cámbiala por:

```
# Nueva lógica de persistencia en archivo
with open("/tmp/log.txt", "a") as f:
    f.write(f"Registro: {data}\n")
print(f"Guardado en archivo: {data}", flush=True)
```

Terminal 1: Ejecuta bash setup.sh.

Demostrar: Entra al pod para ver el archivo:
kubectl exec -it <nombre-pod-auditor> -- cat /tmp/log.txt


🔴 FASE 3: MODO PÁNICO (Si falla la Red/DNS)
Síntoma: Los pods están "Running" pero el Frontend da "Error Connection Refused" o el Receiver no puede contactar al Processor.

Solución: Usar tu Windows como puente.

Terminal 2: Asegúrate de tener 3 túneles abiertos (no solo 2):

```
kubectl port-forward service/receiver-svc 8080:5000 & \
kubectl port-forward service/processor-svc 8081:5000 & \
kubectl port-forward service/auditor-svc 8082:5000
```

Terminal 1: Aplica la configuración de emergencia:
kubectl apply -f k8s/01-config-panic.yaml

Reiniciar Pods:
kubectl rollout restart deployment receiver processor

Ahora el tráfico fluye: Pod A -> Tu Windows -> Pod B.

Acción,Comando
Verificar Pods,kubectl get pods
Ver Logs de un Pod,kubectl logs -f <nombre-del-pod>
Entrar a un Pod,kubectl exec -it <nombre-del-pod> -- sh
Verificar DB Redis,kubectl exec -it <pod-redis> -- redis-cli monitor
Reiniciar un servicio,kubectl rollout restart deployment <nombre>
Borrar todo,kubectl delete all --all

MENTALIDAD PARA EL EXAMEN
No pienses, ejecuta. Sigue los pasos de la Fase 1.

Si piden cambios: Busca el "Caso" correspondiente en la Fase 2 y aplica el cambio de código.

Usa bash setup.sh: Cada vez que toques una línea de Python, corre el script. No intentes hacerlo manual.

Tú tienes el control. Tu arquitectura es modular. Si algo falla, se reinicia solo. Muestra eso con orgullo.