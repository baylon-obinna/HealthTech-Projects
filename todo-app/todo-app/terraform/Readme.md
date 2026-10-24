# Todo App: AWS Infrastructure (Terraform)

Terraform for hosting the todo-app on **Amazon EKS** with a **PostgreSQL (RDS)** database behind an **Application Load Balancer**, inside a hardened VPC.

This is a cost-conscious, single-environment setup.

## Architecture

```
Internet
   │  HTTP :80
   ▼
┌─ PUBLIC SUBNETS (2 AZs) ─────────────────────────────────┐
│  Application Load Balancer   (created by the AWS Load    │
│          │                    Balancer Controller from   │
│          ▼                    a Kubernetes Ingress)      │
│  EKS worker nodes ── todo-app pods (Spring Boot, :8080)  │
└──────────────────────────────┬───────────────────────────┘
                               │ PostgreSQL :5432 (SSL only)
┌─ PRIVATE SUBNETS (2 AZs) ────▼───────────────────────────┐
│  RDS PostgreSQL 16  (no route to the internet)           │
└──────────────────────────────────────────────────────────┘
```

- **One VPC, four subnets:** two public (load balancer + app servers), two private (database), spread over two availability zones.
- **No NAT gateway**. Worker nodes get public IPs so they can pull images, but their security group only accepts traffic from the load balancer.
- **Traffic is chained by security groups:** internet → load balancer (80/443) → nodes (app port only) → database (5432 only).

## Files

| File | What it contains |
|---|---|
| `main.tf` | Terraform and provider setup, and how Terraform logs in to AWS and Kubernetes. |
| `network.tf` | VPC, the four subnets, flow logs, and the load balancer and database security groups. |
| `cluster.tf` | ECR image registry, EKS cluster and node group, Kubernetes namespace, and the AWS Load Balancer Controller. |
| `database.tf` | RDS PostgreSQL, a generated password, and the `db-credentials` Kubernetes secret used by the app. |
| `variables.tf` | All settings you can change (table below). |
| `outputs.tf` | Values printed after `apply`. |

## What gets created

- VPC with 2 public + 2 isolated database subnets, default security group locked down, VPC flow logs to CloudWatch (14-day retention)
- ECR repository with scan-on-push
- EKS cluster and one managed node group (Amazon Linux 2023, IMDSv2 only), with the Kubernetes API restricted to your IP
- Kubernetes namespace (`todo` by default) and a `db-credentials` secret holding the JDBC URL, username and password
- AWS Load Balancer Controller (Helm chart) with its own least-privilege IAM role
- RDS PostgreSQL 16 in the private subnets: encrypted at rest, SSL enforced, 7-day backups, random 32-character password

## Prerequisites

- Terraform `>= 1.5`
- AWS CLI, logged in to the target account (`aws sts get-caller-identity` should print your account)
- `kubectl`, and Docker (for building and pushing the image)
- IAM permissions to create VPC, EKS, RDS, IAM, KMS, ECR and CloudWatch resources

## Variables

| Variable | Default | Notes |
|---|---|---|
| `kubernetes_version` | *none, required* | Pick the newest version in standard support (command below). Versions past standard support are billed at about 6× the control-plane price. |
| `admin_cidrs` | *none, required* | Your public IP(s) for `kubectl` access, e.g. `["203.0.113.7/32"]`. |
| `region` | `eu-west-1` | `af-south-1` . |
| `name` | `todo-app` | Prefix for resource names. |
| `vpc_cidr` | `10.0.0.0/16` | |
| `node_instance_type` | `t3.medium` | `t3.small` . |
| `node_count` | `2` | Use `1` while testing . |
| `use_spot` | `false` |  Testing only. |
| `k8s_namespace` | `todo` | |
| `container_port` | `8080` | Must match the port in your Kubernetes manifest. |
| `db_name` / `db_username` | `todo` / `todo` | |
| `db_instance_class` | `db.t4g.micro` | |
| `protect_database` | `false` | `true` = deletion protection and a final snapshot on destroy. Set it once real data exists. |

Find the newest supported Kubernetes version:

```bash
aws eks describe-cluster-versions \
  --query "clusterVersions[?status=='STANDARD_SUPPORT'].[clusterVersion,endOfStandardSupportDate]" \
  --output table
```

## Quick start

```bash
cd terraform

cat > terraform.tfvars <<EOF
kubernetes_version = "<newest version from the command above>"
admin_cidrs        = ["$(curl -4 -s https://checkip.amazonaws.com)/32"]
node_count         = 1
EOF

terraform init
terraform plan
terraform apply          # about 15 minutes

$(terraform output -raw configure_kubectl)
kubectl get nodes        # should show Ready
```

## Outputs

| Output | Use |
|---|---|
| `configure_kubectl` | Command that points `kubectl` at the cluster. |
| `ecr_repository_url` | Where to push the Docker image. |
| `alb_security_group_id` | Goes into the Ingress annotation `alb.ingress.kubernetes.io/security-groups`. |

## Deploying the app

Terraform builds the platform. The app itself is deployed with the manifest in `k8s/eks/` (Deployment, Service and Ingress).

```bash
cd ..    # project root, where the Dockerfile is
REGION=eu-west-1
REPO=$(terraform -chdir=terraform output -raw ecr_repository_url)
ALB_SG=$(terraform -chdir=terraform output -raw alb_security_group_id)

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin ${REPO%%/*}
docker build --platform linux/amd64 -t $REPO:v1 .
docker push $REPO:v1

sed "s|<ECR_URL>:<TAG>|$REPO:v1|; s|<ALB_SG_ID>|$ALB_SG|" k8s/eks/todo-app.yaml | kubectl apply -f -

kubectl get pods -n todo -w
kubectl get ingress -n todo      # the ADDRESS column is the public URL (2-3 minutes)
```

The app receives its database settings through the `db-credentials` secret, which the Deployment loads with `envFrom` (`SPRING_DATASOURCE_URL`, `SPRING_DATASOURCE_USERNAME`, `SPRING_DATASOURCE_PASSWORD`).


## Tearing down

**Order matters.** The load balancer is created by Kubernetes, not Terraform, so Terraform doesn't know about it. If it still exists, it blocks the VPC from being deleted.

```bash
kubectl delete -f k8s/eks/todo-app.yaml   # 1. removes the ALB
sleep 60                                  #    let AWS finish deleting it
cd terraform && terraform destroy         # 2. removes everything else
```

## Security notes

- The Kubernetes API accepts only the IPs in `admin_cidrs`.
- Worker nodes accept the app port only from the load balancer. The database accepts 5432 only from the worker nodes, and SSL is required.
- IMDSv2 only, hop limit 1: pods can't read the node's IAM credentials.
- Kubernetes secrets are envelope-encrypted with KMS (EKS module default), the database is encrypted at rest, and the ECR repo scans images on push.
- The `kubernetes_version` setting has no default, and the cluster is pinned to standard support, so it can't silently roll into extended-support pricing.

## .gitignore

```
terraform/.terraform/
terraform/*.tfstate*
terraform/terraform.tfvars
```

Commit `terraform/.terraform.lock.hcl`.