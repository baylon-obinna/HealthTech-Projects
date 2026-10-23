output "configure_kubectl" {
  description = "Run this to point kubectl at the new cluster"
  value       = "aws eks update-kubeconfig --region ${var.region} --name ${module.eks.cluster_name}"
}

output "ecr_repository_url" {
  description = "Push your Docker image here"
  value       = aws_ecr_repository.app.repository_url
}

output "alb_security_group_id" {
  description = "Goes in your Ingress as: alb.ingress.kubernetes.io/security-groups"
  value       = aws_security_group.alb.id
}
