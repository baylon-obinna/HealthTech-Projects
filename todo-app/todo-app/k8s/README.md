# Run on minikube

```bash
minikube start --driver=docker
minikube image build -t todo-app:local .          # run from the project root (Dockerfile) 
# if you're using wsl then enable kubernetes in docker destop to avoid API and DNS issues with minikube setup {docker build -t todo-app:local .}

kubectl apply -f k8s/00-namespace.yaml
kubectl create secret generic todo-db --from-env-file=.env -n todo
kubectl apply -f k8s/10-postgres.yaml -f k8s/20-app.yaml

kubectl get pods -n todo -w
kubectl port-forward -n todo svc/todo-app 8080:8080   # then open http://localhost:8080
```
