variable "region" {
  description = "AWS region. af-south-1 is closest to Lagos but must be enabled in the account first."
  type        = string
  default     = "eu-west-1"
}

variable "name" {
  type    = string
  default = "todo-app"
}

variable "kubernetes_version" {
  description = <<-EOT
    No default on purpose: versions leave standard support after ~14 months and are then billed at 6x.
    List current ones with:
      aws eks describe-cluster-versions --query "clusterVersions[?status=='STANDARD_SUPPORT'].[clusterVersion,endOfStandardSupportDate]" --output table
    and pick the newest.
  EOT
  type        = string
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "admin_cidrs" {
  description = "CIDRs allowed to reach the Kubernetes API (kubectl/Terraform). Use your own IP, e.g. [\"203.0.113.7/32\"]."
  type        = list(string)
}

variable "ingress_cidrs" {
  description = "CIDRs allowed to reach the load balancer. Open to the internet by default; narrow it while testing."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "node_instance_type" {
  type    = string
  default = "t3.medium"
}

variable "node_desired_size" {
  description = "Worker nodes (spread over 2 AZs). "
  type        = number
  default     = 2
}

variable "use_spot" {
  description = "Spot nodes are ~65% cheaper but can be reclaimed"
  type        = bool
  default     = false
}

variable "k8s_namespace" {
  type    = string
  default = "todo"
}

variable "container_port" {
  description = "Port the Spring Boot container listens on"
  type        = number
  default     = 8080
}

variable "db_name" {
  type    = string
  default = "todo"
}

variable "db_username" {
  type    = string
  default = "todo"
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "db_multi_az" {
  description = "Standby replica in the second AZ"
  type        = bool
  default     = false
}

variable "protect_database" {
  description = "true = deletion protection + final snapshot on destroy. Leave false while experimenting, set true for real data."
  type        = bool
  default     = false
}

variable "enable_waf" {
  description = "Create a WAFv2 web ACL (AWS managed common rules) to attach to the ALB"
  type        = bool
  default     = false
}

variable "node_count" {
  description = "App servers. 2 = survives one data centre failing; 1 = ~$33/month cheaper."
  type        = number
  default     = 2
}
