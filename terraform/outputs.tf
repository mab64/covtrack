
output "RDS_DNS_Name" {
  value = aws_db_instance.rdb.address
}

output "Subnets" {
  value = aws_subnet.subnets.*.cidr_block
}

output "ALB_DNS_Name" {
  value = aws_lb.alb.dns_name
}

