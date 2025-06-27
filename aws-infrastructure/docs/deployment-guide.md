# AWS Three-Tier Architecture Deployment Guide

## Overview

This document provides comprehensive instructions for deploying a highly available three-tier web application architecture on AWS using CloudFormation.

## Prerequisites

Before deploying the infrastructure, ensure you have the following:

### 1. AWS Account Setup
- AWS account with appropriate permissions
- AWS CLI installed and configured
- Sufficient service limits for the resources being deployed

### 2. Required Permissions
Your AWS user/role needs the following permissions:
- CloudFormation: Full access
- EC2: Full access
- RDS: Full access
- S3: Full access
- VPC: Full access
- IAM: Limited access for role creation
- ELB: Full access
- Auto Scaling: Full access

### 3. Software Requirements
```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
```

## Architecture Components

### Presentation Tier
- **Amazon S3**: Hosts static website content
- **CloudFront** (Optional): Global CDN for improved performance

### Application Tier
- **Application Load Balancer**: Distributes incoming requests
- **Auto Scaling Group**: Manages EC2 instances across multiple AZs
- **EC2 Instances**: Run the web application in private subnets

### Database Tier
- **Amazon RDS**: Multi-AZ MySQL database for data persistence
- **Database Subnet Group**: Isolates database in private subnets

## Deployment Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/mitel-networks-test/test.git
cd test/aws-infrastructure
```

### Step 2: Review and Customize Parameters

Edit the parameter files to match your requirements:

**For Development Environment:**
```bash
vi parameters/dev-parameters.json
```

**For Production Environment:**
```bash
vi parameters/prod-parameters.json
```

Key parameters to review:
- `EnvironmentName`: Prefix for all resources
- Network CIDR blocks
- Instance types (t3.micro for dev, t3.small+ for prod)
- Database credentials (change default passwords!)

### Step 3: Deploy the Infrastructure

**Development Environment:**
```bash
cd scripts
./deploy.sh --environment dev
```

**Production Environment:**
```bash
cd scripts
./deploy.sh --environment prod
```

**Custom Deployment:**
```bash
./deploy.sh --environment dev --stack-name my-custom-stack --region us-east-1
```

### Step 4: Verify Deployment

After deployment completes, you'll see output URLs:

```
ApplicationLoadBalancerURL: http://dev-threetier-alb-123456789.us-west-2.elb.amazonaws.com
StaticWebsiteURL: http://dev-threetier-static-website-123456789.s3-website-us-west-2.amazonaws.com
DatabaseEndpoint: dev-threetier-database.abc123def456.us-west-2.rds.amazonaws.com
```

### Step 5: Test the Application

1. **Test Static Website**: Open the StaticWebsiteURL in your browser
2. **Test Application Tier**: Open the ApplicationLoadBalancerURL in your browser
3. **Test Health Check**: Access `<ALB-URL>/health`
4. **Test API Endpoints**: 
   - `<ALB-URL>/api/info`
   - `<ALB-URL>/api/database`

## Post-Deployment Configuration

### 1. Database Setup

Connect to your RDS instance and create application databases:

```sql
-- Connect using RDS endpoint
mysql -h dev-threetier-database.abc123def456.us-west-2.rds.amazonaws.com -u admin -p

-- Create application database
CREATE DATABASE app_db;
CREATE USER 'app_user'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON app_db.* TO 'app_user'@'%';
FLUSH PRIVILEGES;
```

### 2. SSL/TLS Configuration (Production)

For production deployments, configure SSL/TLS:

1. **Request SSL Certificate**:
```bash
aws acm request-certificate \\
  --domain-name yourdomain.com \\
  --validation-method DNS \\
  --region us-west-2
```

2. **Update ALB Listener** to use HTTPS (443) with the certificate

### 3. Domain Configuration

1. **Route 53 Setup**:
```bash
# Create hosted zone
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)

# Create A record pointing to ALB
aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch file://route53-change.json
```

### 4. Monitoring Setup

Enable CloudWatch monitoring:

1. **Custom Metrics**: Configure application to send custom metrics
2. **Alarms**: Set up CloudWatch alarms for key metrics
3. **Dashboards**: Create monitoring dashboards

## Scaling Configuration

### Auto Scaling Policies

The deployment includes basic auto scaling. To customize:

```bash
# Update Auto Scaling Group
aws autoscaling update-auto-scaling-group \\
  --auto-scaling-group-name dev-threetier-asg \\
  --min-size 2 \\
  --max-size 10 \\
  --desired-capacity 4

# Create scaling policies
aws autoscaling put-scaling-policy \\
  --auto-scaling-group-name dev-threetier-asg \\
  --policy-name scale-up \\
  --scaling-adjustment 2 \\
  --adjustment-type ChangeInCapacity
```

### Database Scaling

For database scaling:

1. **Vertical Scaling**: Modify instance class
2. **Read Replicas**: Add read replicas for read-heavy workloads
3. **Storage Scaling**: Increase storage size as needed

## Backup and Disaster Recovery

### RDS Backups

The deployment configures automated backups:
- **Backup Retention**: 7 days
- **Backup Window**: Automatic
- **Multi-AZ**: Enabled for automatic failover

### Application Backups

1. **AMI Creation**: Create regular AMIs of EC2 instances
2. **S3 Versioning**: Enable versioning for static content
3. **Cross-Region Backup**: Consider cross-region backup for critical data

## Security Best Practices

### 1. Security Groups
- Principle of least privilege
- Regular review and audit
- Use specific ports and protocols

### 2. IAM Roles
- Instance profiles for EC2 instances
- Service-specific roles
- Regular role review

### 3. Network Security
- Private subnets for application and database tiers
- NACLs for additional security
- VPC Flow Logs enabled

### 4. Data Encryption
- RDS encryption at rest
- EBS volume encryption
- S3 bucket encryption

## Troubleshooting

### Common Issues

1. **Deployment Failures**:
   - Check CloudFormation events
   - Verify IAM permissions
   - Ensure service limits

2. **Application Not Accessible**:
   - Check security group rules
   - Verify ALB target health
   - Check EC2 instance status

3. **Database Connection Issues**:
   - Verify security group rules
   - Check database status
   - Validate connection strings

### Debugging Commands

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name dev-threetier-architecture

# Check ALB target health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:...

# Check Auto Scaling Group
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names dev-threetier-asg

# Check RDS status
aws rds describe-db-instances --db-instance-identifier dev-threetier-database
```

## Cost Optimization

### 1. Instance Types
- Use appropriate instance types for workload
- Consider Reserved Instances for predictable workloads
- Use Spot Instances for non-critical workloads

### 2. Storage Optimization
- Use GP3 instead of GP2 for better price/performance
- Regular cleanup of old snapshots
- S3 lifecycle policies for static content

### 3. Monitoring Costs
- AWS Cost Explorer
- AWS Budgets and alerts
- Regular cost reviews

## Cleanup

To remove all resources:

```bash
cd scripts
./cleanup.sh --environment dev
```

For forced cleanup (no confirmation):
```bash
./cleanup.sh --environment dev --force
```

## Support and Documentation

### Additional Resources
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [AWS Application Load Balancer Guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)

### Getting Help
- AWS Support (if you have a support plan)
- AWS Forums
- Stack Overflow with `aws` and `cloudformation` tags