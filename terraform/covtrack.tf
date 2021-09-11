provider "aws" {
  #region = "us-east-1"
  region = var.aws_region
  default_tags {
    tags = var.common_tags
  } 
}

resource "aws_vpc" "covtrack_vpc" {
  cidr_block           = "10.11.0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name = "covtrack_vpc"
    # Owner = var.Owner
  }

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

resource "aws_subnet" "covtrack_subnet0" {
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
  subnet_id   = aws_subnet.covtrack_subnet0.id
  private_ips = ["10.11.0.10"]
  security_groups = [aws_security_group.covtrack_sg.id]

  tags = {
    Name = "primary_network_interface"
  }
}


resource "aws_key_pair" "covtrack_key" {
  key_name   = "covtrack_key"
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


resource "aws_instance" "covtrack_ec2" {
  ami = var.ec2_ami
  instance_type = var.ec2_instance_type

  tags = {
    Name = "ec2_covtrack"
    Project = "Covid Tracker"
    # Owner = var.Owner
  }

  key_name = aws_key_pair.covtrack_key.id #"rhel8"
  # security_groups = ["covtrack"]
  # vpc_security_group_ids = [aws_security_group.covtrack_sg.id]

  network_interface {
    network_interface_id = aws_network_interface.covtrack_ip.id
    device_index         = 0
  }

  user_data = <<-EOF
    #!/bin/bash
    set -ex
    sudo apt update && sudo apt install -y docker docker.io docker-compose
    sudo service docker start
    # sudo usermod -a -G docker ec2-user
    # sudo curl -L https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
    # sudo chmod +x /usr/local/bin/docker-compose
  EOF

  depends_on = [aws_db_instance.covtrack_db]
}


resource "aws_db_instance" "covtrack_db" {
  allocated_storage    = 5
  engine               = "MariaDB"
  engine_version       = "10.4"
  identifier           = "covtrack-db"
  instance_class       = var.db_instance_class
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
  subnet_ids = [aws_subnet.covtrack_subnet0.id, 
                aws_subnet.covtrack_subnet1.id, 
                aws_subnet.covtrack_subnet2.id]

  tags = {
    Name = "covtrack_subnet_gr"
  }
}


output "ec2_ip" {
  value = aws_instance.covtrack_ec2.public_ip
}