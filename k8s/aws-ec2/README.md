# Manifiestos Kubernetes para AWS (3 EC2)

Estos manifiestos despliegan:

- `frontend`
- `messages`
- `files`
- `presence`

> Nota: el frontend tambien consume otros endpoints (`/auth`, `/users`, `/conversations`, etc.). Si quieres operar toda la app completa, debes desplegar los demas microservicios y agregar sus rutas al `Ingress`.

## Prerrequisitos recomendados

1. Cluster Kubernetes en tus 3 EC2 (kubeadm o k3s).
2. Ingress Controller instalado (por ejemplo `ingress-nginx`).
3. DNS del host (ejemplo `chat.example.com`) apuntando al entrypoint del Ingress.
4. MongoDB, Redis y PostgreSQL accesibles desde el cluster (gestionados en AWS o dentro del cluster).

## Archivos

- `00-namespace.yaml`: namespace `mandmandm`.
- `01-configmap.yaml`: variables no sensibles.
- `02-secret.example.yaml`: plantilla de secretos (debes copiarla a `02-secret.yaml` y reemplazar valores).
- `10-deployments.yaml`: deployments de frontend/messages/files/presence.
- `11-services.yaml`: services internos (`ClusterIP`).
- `12-ingress.yaml`: exposicion HTTP por rutas.

## Pasos de despliegue

1. Crea el secret real:

```bash
cp k8s/aws-ec2/02-secret.example.yaml k8s/aws-ec2/02-secret.yaml
```

2. Edita `k8s/aws-ec2/02-secret.yaml` con valores reales (`MONGO_URI`, `REDIS_URI`, `DATABASE_URL`).

3. Ajusta `chat.example.com` en:

- `k8s/aws-ec2/01-configmap.yaml` (`FRONTEND_PUBLIC_BASE_URL`, `FRONTEND_API_BASE_URL`)
- `k8s/aws-ec2/12-ingress.yaml` (campo `host`)

4. Aplica:

```bash
kubectl apply -f k8s/aws-ec2/00-namespace.yaml
kubectl apply -f k8s/aws-ec2/01-configmap.yaml
kubectl apply -f k8s/aws-ec2/02-secret.yaml
kubectl apply -f k8s/aws-ec2/10-deployments.yaml
kubectl apply -f k8s/aws-ec2/11-services.yaml
kubectl apply -f k8s/aws-ec2/12-ingress.yaml
```

5. Verifica:

```bash
kubectl get pods,svc,ing -n mandmandm
kubectl describe ing mandmandm-ingress -n mandmandm
```

## Recomendaciones para produccion

- Usa tags inmutables de imagen (evita `latest`).
- Mueve secretos a un gestor (AWS Secrets Manager + External Secrets).
- Agrega TLS con `cert-manager`.
- Define `HorizontalPodAutoscaler` y `PodDisruptionBudget`.
