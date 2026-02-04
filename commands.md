1.
minikube start --driver=docker
kubectl delete all --all
#### opcional para borrar bd -> kubectl delete pvc postgres-pvc

2.
cd k8s-test-template

3.
.\setup.ps1

4.
kubectl get pods

5.
# Pestaña 1
kubectl port-forward service/frontend-svc 8000:80
# Pestaña 2
kubectl port-forward service/receiver-svc 8080:8080
# Pestaña 3 (Logs)
kubectl logs -f -l app=auditor

6.
http://localhost:8000


---

En caso de guardar en archivos de texto

# 1. Obtén el nombre del pod del auditor
kubectl get pods

# 2. Lee el archivo dentro del pod (reemplaza auditor-xxxx con el nombre real)
# Para el Síncrono:
kubectl exec auditor-5f88d8b9c-xyz -- cat auditor_logs.txt

# Para el Asíncrono:
kubectl exec auditor-5f88d8b9c-xyz -- cat worker_logs.txt