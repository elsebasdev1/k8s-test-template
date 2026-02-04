Parte práctica

1.
minikube start --driver=docker

2.
kubectl delete all --all

3. crear carpeta de proyecto (github)
crear base.yaml

4.

kubectl apply -f k8s/scenario-nginx/base.yaml

5. Tomar captura

kubectl get pods

kubectl get deployments

6. Verificar ClusterIP

kubectl get service nginx-service

7. Cambiar a nodeport

kubectl edit service nginx-service

cambiar type: ClusterIP por type: NodePort

8. Tomar captura

minikube service nginx-service

9. Replicas

kubectl scale deployment nginx-exam --replicas=4

10. Tomar captura

kubectl get pods -w

11. Cambiar la imagen de nginxdemos/hello a nginx:alpine

kubectl set image deployment/nginx-exam nginx-container=nginx:alpine

12. Tomar captura

kubectl rollout status deployment/nginx-exam

kubectl describe pod -l app=nginx-exam | sls Image

13. Volver a ejecutar para ver cambios
minikube service nginx-service

14. Borrar todo
kubectl delete all --all
