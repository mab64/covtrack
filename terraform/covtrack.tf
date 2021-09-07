provider "aws" {
  #region = "us-east-1"
  region = var.aws_region
}

resource "aws_vpc" "covtrack_vpc" {
  cidr_block           = "10.11.0.0/16"
  enable_dns_hostnames = true
}

resource "aws_internet_gateway" "covtrack_gw" {
  vpc_id = aws_vpc.covtrack_vpc.id
}

resource "aws_route" "covtrack_r" {
  route_table_id            = aws_vpc.covtrack_vpc.default_route_table_id
  destination_cidr_block    = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.covtrack_gw.id
  
  # vpc_peering_connection_id = "pcx-45ff3dc1"
  # depends_on                = [aws_route_table.testing]
}

resource "aws_subnet" "covtrack_subnet" {
  vpc_id            = aws_vpc.covtrack_vpc.id
  cidr_block        = "10.11.0.0/24"
  availability_zone = "eu-central-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "covtrack_subnet0"
  }
}

resource "aws_subnet" "covtrack_subnet1" {
  vpc_id            = aws_vpc.covtrack_vpc.id
  cidr_block        = "10.11.1.0/24"
  availability_zone = "eu-central-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "covtrack_subnet1"
  }
}

resource "aws_subnet" "covtrack_subnet2" {
  vpc_id            = aws_vpc.covtrack_vpc.id
  cidr_block        = "10.11.2.0/24"
  availability_zone = "eu-central-1c"
  map_public_ip_on_launch = true

  tags = {
    Name = "covtrack_subnet2"
  }
}

resource "aws_network_interface" "covtrack_ip" {
  subnet_id   = aws_subnet.covtrack_subnet.id
  private_ips = ["10.11.0.10"]
  security_groups = [aws_security_group.covtrack_sg.id]

  tags = {
    Name = "primary_network_interface"
  }
}

resource "aws_instance" "ec2_debian_10" {
  ami = "ami-0245697ee3e07e755"
  instance_type = "t2.micro"

  tags = {
    Name = "ec2_covtrack"
    Project = "Covid Tracker"
  }

  key_name = aws_key_pair.covtrack_key.id #"rhel8"
  # security_groups = ["covtrack"]
  # vpc_security_group_ids = [aws_security_group.covtrack_sg.id]

  network_interface {
    network_interface_id = aws_network_interface.covtrack_ip.id
    device_index         = 0
  }

}

resource "aws_key_pair" "covtrack_key" {
  key_name   = "covtrack_key"
  # public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD3F6tyPEFEzV0LX3X8BsXdMsQz1x2cEikKDEY0aIj41qgxMCP/iteneqXSIFZBp5vizPvaoIR3Um9xK7PGoW8giupGn+EPuxIA4cDM4vzOqOkiMPhz5XK0whEjkVzTo4+S0puvDZuwIsdiW9mxhJc7tgBNL0cYlWSYVkz4G/fslNfRPW5mYAM49f4fhtxPb5ok4Q2Lg9dPKVHO/Bgeu5woMc7RY0p1ej6D4CKFE6lymSDJpW0YHX/wqE9+cfEauh7xZcG0q9t2ta6F6fmX0agvpFyZo8aFbXeUBr7osSCJNgvavWbM/06niWrOvYX2xwWdhXmXSrbX8ZbabVohBK41 email@example.com"
  public_key = file("~/.ssh/ansible_key.pub")
}

resource "aws_security_group" "covtrack_sg" {
  name        = "covtrack_sg"
  description = "Cov traffic"
  vpc_id      = aws_vpc.covtrack_vpc.id

  tags = {
    Name = "covtrack_sg"
  }

  # ingress = [
  #   {
  #     description      = "SSH traffic"
  #     from_port        = 22
  #     to_port          = 22
  #     protocol         = "tcp"
  #     cidr_blocks      = ["0.0.0.0/0"]
  #     ipv6_cidr_blocks = ["::/0"]
  #     # cidr_blocks      = [aws_vpc.main.cidr_block]
  #     # ipv6_cidr_blocks = [aws_vpc.main.ipv6_cidr_block]
  #     prefix_list_ids = []
  #     security_groups = []
  #     self = null
  #   }
  # ]

  dynamic "ingress" {
    for_each = ["22", "80", "443", "3306", "5000", "5001"]
    content {
      from_port        = ingress.value
      to_port          = ingress.value
      protocol         = "tcp"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
      # cidr_blocks      = [aws_vpc.main.cidr_block]
      # ipv6_cidr_blocks = [aws_vpc.main.ipv6_cidr_block]
      prefix_list_ids = []
      security_groups = []
      self = null
    }
  }

  egress = [
    {
      description      = "All traffic"
      from_port        = 0
      to_port          = 0
      protocol         = "-1"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
      prefix_list_ids = []
      security_groups = []
      self = null
    }
  ]

}

resource "aws_db_instance" "covtrack_db" {
  allocated_storage    = 5
  engine               = "MariaDB"
  engine_version       = "10.4"
  identifier           = "covtrack-db"
  instance_class       = "db.t2.micro"
  name                 = "covtrack_db"
  username             = "covtrack_user"
  password             = var.db_password
  # parameter_group_name = "default.mysql5.7"
  skip_final_snapshot  = true
  db_subnet_group_name = aws_db_subnet_group.covtrack_subnet_gr.name
  vpc_security_group_ids = [aws_security_group.covtrack_sg.id]
   
}

resource "aws_db_subnet_group" "covtrack_subnet_gr" {
  name       = "covtrack_subnet_gr"
  subnet_ids = [aws_subnet.covtrack_subnet.id, 
                aws_subnet.covtrack_subnet1.id, 
                aws_subnet.covtrack_subnet2.id]

  tags = {
    Name = "covtrack_subnet_gr"
  }
}

## Variables
variable "aws_region" {
  type = string
  default = "eu-central-1"
}

variable "db_password" {
  type = string
}
