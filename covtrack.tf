provider "aws" {
  #region = "us-east-1"
  region = "eu-central-1"

}

resource "aws_vpc" "covtrack_vpc" {
  cidr_block           = "10.11.0.0/16"
  enable_dns_hostnames = true
  
}

resource "aws_internet_gateway" "covtrack_gw" {
  vpc_id = aws_vpc.covtrack_vpc.id
}

# resource "aws_default_route_table"

resource "aws_route" "covtrack_r" {
  route_table_id            = aws_vpc.covtrack_vpc.default_route_table_id
  destination_cidr_block    = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.covtrack_gw.id
  
  # vpc_peering_connection_id = "pcx-45ff3dc1"
  # depends_on                = [aws_route_table.testing]
}

# module "covtrack_sg" {
#   source = "terraform-aws-modules/security-group/aws"

#   name = "covtrack_sg"
#   description = "Security group for CovTrack application"
#   vpc_id      = aws_vpc.covtrack_vpc.id
  

# }

resource "aws_subnet" "covtrack_subnet" {
  vpc_id            = aws_vpc.covtrack_vpc.id
  cidr_block        = "10.11.0.0/24"
  # availability_zone = "us-west-2a"
  map_public_ip_on_launch = true

  tags = {
    Name = "covtrack_subnet"
  }
}

resource "aws_network_interface" "covtrack_ip" {
  subnet_id   = aws_subnet.covtrack_subnet.id
  # subnet_id   = "subnet-0c701777f60dc6228"
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

  key_name = "rhel8"
  # security_groups = ["covtrack"]
  # vpc_security_group_ids = [aws_security_group.covtrack_sg.id]

  network_interface {
    network_interface_id = aws_network_interface.covtrack_ip.id
    device_index         = 0
  }

}

resource "aws_security_group" "covtrack_sg" {
  name        = "covtrack_sg"
  description = "Cov traffic"
  vpc_id      = aws_vpc.covtrack_vpc.id

  tags = {
    Name = "covtrack_sg"
  }

  ingress = [
    {
      description      = "SSH traffic"
      from_port        = 22
      to_port          = 22
      protocol         = "tcp"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
      # cidr_blocks      = [aws_vpc.main.cidr_block]
      # ipv6_cidr_blocks = [aws_vpc.main.ipv6_cidr_block]
      prefix_list_ids = []
      security_groups = []
      self = null
    }
  ]

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

