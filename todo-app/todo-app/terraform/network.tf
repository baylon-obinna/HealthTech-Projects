# One VPC, four subnets, two security groups.
#
#   public subnets  (2) -> load balancer + app servers
#   private subnets (2) -> database only, no route to the internet
#
# Two of each, in two different data centres (availability zones).

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = var.name
  cidr = var.vpc_cidr
  azs  = slice(data.aws_availability_zones.available.names, 0, 2)

  public_subnets   = [cidrsubnet(var.vpc_cidr, 8, 0), cidrsubnet(var.vpc_cidr, 8, 1)]
  database_subnets = [cidrsubnet(var.vpc_cidr, 8, 10), cidrsubnet(var.vpc_cidr, 8, 11)]

  create_database_subnet_group       = true
  create_database_subnet_route_table = true # its own route table: no way out to the internet

  enable_nat_gateway      = false 
  enable_dns_hostnames    = true
  map_public_ip_on_launch = true # app servers need a public IP to pull images (no NAT)

  # Tag so the load balancer controller knows where to place the ALB
  public_subnet_tags = { "kubernetes.io/role/elb" = 1 }

  # Lock the VPC's default security group (nothing allowed in or out)
  manage_default_security_group  = true
  default_security_group_ingress = []
  default_security_group_egress  = []

  # Flow logs
  enable_flow_log                                 = true
  create_flow_log_cloudwatch_log_group            = true
  create_flow_log_cloudwatch_iam_role             = true
  flow_log_cloudwatch_log_group_retention_in_days = 14
}

# Load balancer: open to the internet on web ports
resource "aws_security_group" "alb" {
  name_prefix = "${var.name}-alb-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "To the app, inside the VPC only"
    from_port   = var.container_port
    to_port     = var.container_port
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  lifecycle { create_before_destroy = true }
}

# Database: only the app servers may connect, only on the Postgres port
resource "aws_security_group" "db" {
  name_prefix = "${var.name}-db-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "Postgres from app servers"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  lifecycle { create_before_destroy = true }
}
