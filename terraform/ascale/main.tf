provider "aws" {
  region = var.aws_region
  default_tags {
    tags = var.common_tags
  } 
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "${var.name_prefix}-ssh-key"
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "aws_launch_configuration" "launch_conf" {
  # name_prefix = "${var.name_prefix}-"
  name            = "${var.name_prefix}-launch_conf"
  image_id        = var.ec2_ami
  instance_type   = var.ec2_instance_type
  key_name        = aws_key_pair.ssh_key.id
  security_groups = [ aws_security_group.ec2_sg.id ]
  associate_public_ip_address = true

  user_data = templatefile("ec2_init.tpl", {
      rdb_address     = aws_db_instance.rdb.address,
      db_name         = var.db_name,
      db_user         = var.db_user,
      db_password     = var.db_password,
      docker_img_name = var.docker_img_name
  })

  # user_data = <<-USER_DATA
  #   #!/bin/bash
  #   apt update
  #   apt -y install net-tools stress-ng docker docker.io # nfs-common docker-compose
  #   systemctl start docker
  #   docker run -dit -p 80:5000 \
  #     -e MYSQL_HOST="${aws_db_instance.rdb.address}" \
  #     -e MYSQL_DATABASE="${var.db_name}" \
  #     -e MYSQL_USER="${var.db_user}" \
  #     -e MYSQL_PASSWORD="${var.db_password}" \
  #     --restart always --name covtrack ${var.docker_img_name}
  #   # curl http://169.254.169.254/latest/meta-data/local-ipv4 > /efs/wordpress/index.html
  # USER_DATA

  # lifecycle {
  #   create_before_destroy = true
  # }
}

resource "aws_vpc" "vpc" {
  # cidr_block           = var.vpc_cidr
  cidr_block           = "${var.vpc_net_prefix}0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name = "${var.name_prefix}-vpc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
}

resource "aws_route" "route0" {
  route_table_id          = aws_vpc.vpc.default_route_table_id
  destination_cidr_block  = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.igw.id
}

data "aws_availability_zones" "available" {}

resource "aws_subnet" "subnets" {
  vpc_id            = aws_vpc.vpc.id
  count = "${length(data.aws_availability_zones.available.names)}"
  # cidr_block        = var.cidr_blocks[count.index]
  cidr_block        = "${var.vpc_net_prefix}${count.index}.0/24"
  availability_zone = "${data.aws_availability_zones.available.names[count.index]}"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.name_prefix}-subnet${count.index}"
  }
}

