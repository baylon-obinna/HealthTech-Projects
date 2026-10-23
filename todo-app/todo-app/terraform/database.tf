# A private, encrypted PostgreSQL database.

resource "random_password" "db" {
  length  = 32
  special = false
}

# Reject any connection that isn't encrypted
resource "aws_db_parameter_group" "pg" {
  name_prefix = "${var.name}-"
  family      = "postgres16"

  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }

  lifecycle { create_before_destroy = true }
}

resource "aws_db_instance" "db" {
  identifier        = "${var.name}-db"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = var.db_instance_class
  allocated_storage = 20
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = var.db_name
  username = var.db_username
  password = random_password.db.result

  db_subnet_group_name   = module.vpc.database_subnet_group_name # the private subnets
  vpc_security_group_ids = [aws_security_group.db.id]
  parameter_group_name   = aws_db_parameter_group.pg.name
  publicly_accessible    = false

  backup_retention_period   = 7
  deletion_protection       = var.protect_database
  skip_final_snapshot       = !var.protect_database
  final_snapshot_identifier = var.protect_database ? "${var.name}-final" : null
}

# Hands the connection details to your app as environment variables.
resource "kubernetes_secret" "db" {
  metadata {
    name      = "db-credentials"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    SPRING_DATASOURCE_URL      = "jdbc:postgresql://${aws_db_instance.db.address}:5432/${var.db_name}?sslmode=require"
    SPRING_DATASOURCE_USERNAME = var.db_username
    SPRING_DATASOURCE_PASSWORD = random_password.db.result
  }
}
