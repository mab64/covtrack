resource "aws_autoscaling_group" "asg" {
  name = "${var.name_prefix}-asg"
  launch_configuration = aws_launch_configuration.launch_conf.name

  min_size             = 1
  desired_capacity     = 1
  max_size             = 3
  health_check_type    = "ELB"
  # health_check_grace_period = 300
  
  # load_balancers = [ aws_elb.elb.id ]
  target_group_arns = [ aws_lb_target_group.alb_tg.arn ]

  vpc_zone_identifier  = aws_subnet.subnets.*.id

  tag {
    key                 = "Name"
    value               = "${var.name_prefix}-asg-ec2"
    propagate_at_launch = true
  }

  depends_on = [ aws_db_instance.rdb ]
}

resource "aws_autoscaling_policy" "scale_up" {
  name = "${var.name_prefix}-scale-policy-up"
  scaling_adjustment = 1
  adjustment_type = "ChangeInCapacity"
  cooldown = 180
  autoscaling_group_name = aws_autoscaling_group.asg.name
}

resource "aws_cloudwatch_metric_alarm" "alarm_cpu_high" {
  alarm_name = "alarm-cpu-high"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  period = "60"
  evaluation_periods = "2"
  metric_name = "CPUUtilization"
  namespace = "AWS/EC2"
  statistic = "Average"
  threshold = "80"

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.asg.name
  }

  alarm_description = "Monitors EC2 instance high CPU utilization"
  alarm_actions = [ aws_autoscaling_policy.scale_up.arn ]
}

resource "aws_autoscaling_policy" "scale_down" {
  name = "${var.name_prefix}-scale-policy-down"
  scaling_adjustment = -1
  adjustment_type = "ChangeInCapacity"
  cooldown = 180
  autoscaling_group_name = aws_autoscaling_group.asg.name
}

resource "aws_cloudwatch_metric_alarm" "alarm_cpu_low" {
  alarm_name = "alarm-cpu-low"
  comparison_operator = "LessThanOrEqualToThreshold"
  period = "60"
  evaluation_periods = "2"
  metric_name = "CPUUtilization"
  namespace = "AWS/EC2"
  statistic = "Average"
  threshold = "30"

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.asg.name
  }

  alarm_description = "Monitors EC2 instance low CPU utilization"
  alarm_actions = [ aws_autoscaling_policy.scale_down.arn ]
}

resource "aws_security_group" "ec2_sg" {
  name        = "${var.name_prefix}-ec2-sg"
  vpc_id      = aws_vpc.vpc.id

  tags = {
    Name = "${var.name_prefix}-ec2-sg"
  }

  dynamic "ingress" {
    for_each = ["22", "80", "443", "5000"]
    content {
      from_port         = ingress.value
      to_port           = ingress.value
      protocol          = "tcp"
      cidr_blocks       = ["0.0.0.0/0"]
      ipv6_cidr_blocks  = ["::/0"]
      prefix_list_ids   = []
      security_groups   = []
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

