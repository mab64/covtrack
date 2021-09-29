variable "aws_region" {
  default = "eu-central-1"
}

variable "common_tags" {
  default = {
    Environment = "Test"
    Owner       = "MA"
    Project     = "Covid Tracker"
  }
}

variable "name_prefix" {
  default = "cov"
}

variable "vpc_net_prefix" {
  default = "10.11."
}

variable "ec2_ami" {
  default = "ami-0245697ee3e07e755" # debian 10
}
variable "ec2_instance_type" {
  default = "t2.micro"
}
variable "ec2_username" {
  default = "admin"
}

variable "docker_img_name" {
  default = "mual/covtrack"
}
variable "docker_container_name" {
  default = "covtrack"
}

variable "db_instance_class" {
  default = "db.t2.micro"
}

variable "db_name" {}
variable "db_user" {}
variable "db_password" {}

