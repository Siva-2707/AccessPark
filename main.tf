# AWS Configurations
provider "aws" {
  region = "us-east-1"
  # access_key = #ACCESS_KEY
  # secret_key = #SECRET_KEY
  # token = #TOKEN
}

#Variable for region to use it later. 
variable "region" {
  default = "us-east-1"
}

#Defining VPC
resource "aws_vpc" "ap_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "ap_vpc"
    Group = "ap"
  }
}

#Defining IGW
resource "aws_internet_gateway" "ap_vpc_igw" {
  vpc_id = aws_vpc.ap_vpc.id
  tags = {
    Name = "ap_vpc_igw"
    Group = "ap"
  }
}

#Creating required subnets
resource "aws_subnet" "ap_public_subnet" {
  vpc_id = aws_vpc.ap_vpc.id
  cidr_block = "10.0.1.0/24"
  tags = {
    Name = "ap_public_subnet"
    Group = "ap"
  }
}

resource "aws_subnet" "ap_private_subnet" {
  vpc_id = aws_vpc.ap_vpc.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "us-east-1a"
  tags = {
    Name = "ap_private_subnet"
    Group = "ap"
  }
}

resource "aws_subnet" "ap_private_subnet_bck" {
  vpc_id = aws_vpc.ap_vpc.id
  cidr_block = "10.0.3.0/24"
  availability_zone = "us-east-1b"
  tags = {
    Name = "ap_private_subnet_bck"
    Group = "ap"
  }
}

#Creating Route tables (Public)
resource "aws_route_table" "ap_public_rt" {
  vpc_id = aws_vpc.ap_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.ap_vpc_igw.id
  }

  tags = {
    Name = "ap_public_rt"
    Group = "ap"
  }
}

#Creating association with Public RT and Public SN
resource "aws_route_table_association" "ap_public_rt_association" {
  subnet_id      = aws_subnet.ap_public_subnet.id
  route_table_id = aws_route_table.ap_public_rt.id
}

# Creating an Elastic IP for the NAT Gateway
resource "aws_eip" "nat_eip" {
  domain = "vpc"
}

#Creating NAT Gateway in a public subnet
resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.ap_public_subnet.id
  tags = {
    Name = "nat-gateway"
  }
}

#Creating Route tables (Private)
resource "aws_route_table" "ap_private_rt" {
  vpc_id = aws_vpc.ap_vpc.id

  route{
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }

  tags = {
    Name = "ap_private_rt"
    Group = "ap"
  }
}

#Creating association with Private RT and Private SNs
resource "aws_route_table_association" "ap_private_rt_associations" {
  for_each      = {
    primary = aws_subnet.ap_private_subnet.id
    backup  = aws_subnet.ap_private_subnet_bck.id
  }
  subnet_id      = each.value
  route_table_id = aws_route_table.ap_private_rt.id
}


# S3 Bucket to store Lambda code
resource "aws_s3_bucket" "lambda_bucket" {
  bucket = "lambda-code-bucket-${random_id.bucket_id.hex}"
  force_destroy = true
}

#Creating random id for bucket, making it unique. 
resource "random_id" "bucket_id" {
  byte_length = 4
}

#Local zipping of lambda executable and uploading it into the S3 bucket.
resource "null_resource" "zip_and_upload" {
  provisioner "local-exec" {
    command = <<EOT
      cd ingestor
      pip install -r requirements.txt -t package/
      pip install \
      --platform manylinux2014_x86_64 \
      --target=package \
      --implementation cp \
      --python-version 3.13 \
      --only-binary=:all: --upgrade \
      numpy
      pip install \
      --platform manylinux2014_x86_64 \
      --target=package \
      --implementation cp \
      --python-version 3.13 \
      --only-binary=:all: --upgrade \
      pandas
      cd package && zip -r9 ../ingestor.zip . && cd ..
      zip -g ingestor.zip -r ./*.py
      aws s3 cp ingestor.zip s3://${aws_s3_bucket.lambda_bucket.bucket}/ingestor.zip
      # aws s3 cp ingestor.zip s3://accessparktest/ingestor.zip
    EOT
  }
  depends_on = [aws_s3_bucket.lambda_bucket]
}

# Security Group for MySQL
resource "aws_security_group" "mysql_sg" {
  name        = "mysql-sg"
  description = "Allow MySQL access"
  ingress { 
    from_port = 3306
    to_port = 3306
    protocol = "tcp"
    security_groups = [aws_security_group.lambda_sg.id]
    cidr_blocks = ["0.0.0.0/0"] 
  }
  egress{
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  vpc_id = aws_vpc.ap_vpc.id
}

# Subnet group for RDS
resource "aws_db_subnet_group" "ap_rds_sng" {
  name        = "mysql-subnet-group"
  subnet_ids  = [aws_subnet.ap_private_subnet.id, aws_subnet.ap_private_subnet_bck.id]
  tags = {
    Name = "mysql-subnet-group"
  }
}

# RDS MySQL DB with security group attached. 
resource "aws_db_instance" "mysql_db" {
  identifier         = "myapp-db"
  allocated_storage  = 20
  engine             = "mysql"
  engine_version     = "8.0"
  instance_class     = "db.t3.micro"
  db_subnet_group_name = aws_db_subnet_group.ap_rds_sng.name
  multi_az = false
  username           = var.db_username
  password           = var.db_password
  db_name            = var.db_name
  publicly_accessible = false
  skip_final_snapshot = true
  vpc_security_group_ids = [aws_security_group.mysql_sg.id]
}

# Using existing IAM role for lambda.
data "aws_iam_role" "lambda_exec_role" {
  name = "LabRole"
}

# IAM role profile to attach it to resources.
resource "aws_iam_instance_profile" "lab_role_profile" {
  name = "LabRoleProfile"
  role = data.aws_iam_role.lambda_exec_role.name
}

# Security group for lambda
resource "aws_security_group" "lambda_sg" {
  name        = "lambda-sg"
  description = "Allow Lambda to connect to RDS and receive EventBridge triggers"
  vpc_id      = aws_vpc.ap_vpc.id

  #Only outbound rules to connect to RDS and opensource data. 
  egress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }

  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

    egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "lambda-sg"
  }
}

# Lambda Function
resource "aws_lambda_function" "ingestor" {
  function_name = "ingestorLambda"
  s3_bucket     = aws_s3_bucket.lambda_bucket.bucket
  s3_key        = "ingestor.zip"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.13"
  role          = data.aws_iam_role.lambda_exec_role.arn
  timeout       = 150
  memory_size   = 512
  
  ephemeral_storage {
    size = 1028
  }

  vpc_config {
    subnet_ids         = [aws_subnet.ap_private_subnet.id, aws_subnet.ap_private_subnet_bck.id]
    security_group_ids = [aws_security_group.lambda_sg.id]
  }

  environment {
    variables = {
      DB_HOST     = aws_db_instance.mysql_db.address
      DB_PORT     = aws_db_instance.mysql_db.port
      DB_NAME     = var.db_name
      DB_USER = var.db_username
      DB_PASSWORD = var.db_password
    }
  }
  depends_on = [null_resource.zip_and_upload, aws_db_instance.mysql_db]
}

#Invoking lambda once for initial load.
resource "null_resource" "invoke_lambda_once" {
  provisioner "local-exec" {
    command = <<EOT
      aws lambda invoke \
        --function-name ${aws_lambda_function.ingestor.function_name} \
        --payload '{}' \
        response.json
    EOT
  }

  triggers = {
    lambda_version = aws_lambda_function.ingestor.version
  }

  depends_on = [aws_lambda_function.ingestor]
}

# EventBridge rule to trigger Lambda weekly
resource "aws_cloudwatch_event_rule" "weekly" {
  name                = "weekly-lambda-trigger"
  schedule_expression = "rate(7 days)"
}

# Setting target for EventBridge.
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.weekly.name
  target_id = "lambda-ingestor"
  arn       = aws_lambda_function.ingestor.arn
}

# Allowing necessary permission for lambda.
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingestor.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly.arn
}

# Security Group for EC2
resource "aws_security_group" "ec2_sg" {
  name        = "ec2-sg"
  description = "Allow HTTP and SSH"
  ingress{ 
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }
  ingress { 
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  vpc_id = aws_vpc.ap_vpc.id
}

# EC2 Instance
resource "aws_instance" "fastapi_instance" {
  ami           = "ami-0c7217cdde317cfec" # Ubuntu 22.04 in us-east-1
  instance_type = "t2.micro"
  subnet_id = aws_subnet.ap_public_subnet.id
  security_groups = [aws_security_group.ec2_sg.id]
  associate_public_ip_address = true
  iam_instance_profile = aws_iam_instance_profile.lab_role_profile.name

  user_data = <<-EOF
              #!/bin/bash
              apt update -y
              apt install -y python3-pip git
              git clone https://github.com/Siva-2707/AccessPark.git
              cd AccessPark/backend
              touch .env
              echo "DB_USERNAME=${var.db_username}" >> .env
              echo "DB_PASSWORD=${var.db_password}" >> .env
              echo "DB_HOST=${aws_db_instance.mysql_db.address}" >> .env
              echo "DB_PORT=${aws_db_instance.mysql_db.port}" >> .env
              echo "DB_NAME=${var.db_name}" >> .env
              pip3 install -r requirements.txt
              nohup uvicorn main:app --host 0.0.0.0 --port 80 &
              EOF
}

# Output Public IP
output "ec2_public_ip" {
  value = aws_instance.fastapi_instance.public_ip
}

# Variables
variable "db_username" {
  default = "admin"
  description = "Database username"
}
variable "db_password" {
  default = "password"
  description = "Database password"
  sensitive = true
  type = string
}
variable "db_name" {
  default = "parking"
  description = "Database name"
  type = string
}
