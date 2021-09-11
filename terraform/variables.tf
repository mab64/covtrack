variable "aws_region" {
  type = string
  default = "eu-central-1"
}

variable "db_password" {
  type = string
}

variable "db_instance_class" {
  default = "db.t2.micro"
}

variable "ec2_instance_type" {
  default = "t2.micro"
}
variable "ec2_ami" {
  default = "ami-0245697ee3e07e755" # debian 10
}

# locals {
#   common_tags = {
#     Environment = "Test"
#     Owner       = "MA"
#     Project     = "Covid Tracker"
#   }
# }

variable "common_tags" {
  default = {
    Environment = "Test"
    Owner       = "MA"
    Project     = "Covid Tracker"
  }
}