# Where Docker image is stored for the app. The ECR repository is created here, but the image is built and pushed in the GitHub Actions workflow.
resource "aws_ecr_repository" "app" {
  name         = var.name
  force_delete = true # remove for production

  image_scanning_configuration {
    scan_on_push = true
  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.31"

  cluster_name    = var.name
  cluster_version = var.kubernetes_version

  cluster_upgrade_policy = { support_type = "STANDARD" }

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnets

  # kubectl only works from your IP
  cluster_endpoint_public_access           = true
  cluster_endpoint_public_access_cidrs     = var.admin_cidrs
  enable_cluster_creator_admin_permissions = true

  cluster_addons = {
    coredns    = {}
    kube-proxy = {}
    vpc-cni    = {}
  }

  eks_managed_node_groups = {
    app = {
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = [var.node_instance_type]
      capacity_type  = var.use_spot ? "SPOT" : "ON_DEMAND"
      min_size       = 1
      max_size       = var.node_count + 1
      desired_size   = var.node_count

      # Pods cannot read the server's IAM credentials (IMDSv2 only, hop limit 1)
      metadata_options = {
        http_endpoint               = "enabled"
        http_tokens                 = "required"
        http_put_response_hop_limit = 1
      }
    }
  }

  # App servers accept the app port from the load balancer, nothing else from outside
  node_security_group_additional_rules = {
    from_alb = {
      description              = "App port from the load balancer"
      type                     = "ingress"
      protocol                 = "tcp"
      from_port                = var.container_port
      to_port                  = var.container_port
      source_security_group_id = aws_security_group.alb.id
    }
  }
}

resource "kubernetes_namespace" "app" {
  metadata {
    name = var.k8s_namespace
  }

  depends_on = [module.eks]
}

# The load balancer controller watches for Ingress objects and builds the ALB.
# The IAM role below gives it only the AWS permissions it needs.
module "lb_controller_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name                              = "${var.name}-lb-controller"
  attach_load_balancer_controller_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }
}

resource "helm_release" "lb_controller" {
  name       = "aws-load-balancer-controller"
  namespace  = "kube-system"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  version    = "1.8.1"

  set {
    name  = "clusterName"
    value = module.eks.cluster_name
  }
  set {
    name  = "region"
    value = var.region
  }
  set {
    name  = "vpcId"
    value = module.vpc.vpc_id
  }
  set {
    name  = "serviceAccount.name"
    value = "aws-load-balancer-controller"
  }
  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = module.lb_controller_role.iam_role_arn
  }

  depends_on = [module.eks]
}
