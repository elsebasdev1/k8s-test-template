2. Cómo activar el "Modo Pánico" en el Examen
Si el DNS falla, sigue esta secuencia rápida:

Paso A: Abre los túneles (Terminal 2) Ejecuta los comandos que mencionaste para exponer todo a Windows:

Bash
# Exponer TODOS los servicios a tu localhost
kubectl port-forward svc/receiver-svc 8080:5000 &
kubectl port-forward svc/processor-svc 8081:5000 &
kubectl port-forward svc/auditor-svc 8082:5000 &
Paso B: Aplica la configuración de emergencia (Terminal 1) Sobrescribe la configuración normal con la de pánico y reinicia los pods para que tomen el cambio.

Bash
# 1. Aplica el ConfigMap de emergencia
kubectl apply -f k8s/01-config-panic.yaml

# 2. Reinicia los despliegues para que lean la nueva variable
kubectl rollout restart deployment receiver
kubectl rollout restart deployment processor

3. ¿Necesito cambiar el código Python?
NO. Esa es la belleza de usar variables de entorno. Tu código Python (app.py) ya tiene esta línea:

Python
NEXT_HOP = os.getenv("NEXT_SERVICE_URL", "http://valor-por-defecto...")
Cuando aplicas el nuevo ConfigMap y reinicias, Kubernetes inyecta la nueva URL (http://host.minikube.internal:8081) automáticamente. El código simplemente la usa sin saber que hubo un cambio.

Resumen del Flujo en "Modo Pánico":
Receiver (Pod) recibe el request.

Intenta llamar a NEXT_HOP.

Kubernetes le dice: "Tu NEXT_HOP es http://host.minikube.internal:8081".

El request viaja del Pod -> Tu Windows (Puerto 8081).

En tu Windows, el kubectl port-forward atrapa el tráfico.

Lo reenvía -> Processor (Pod).