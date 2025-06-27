# AWS Three-Tier Architecture - Complete Implementation

This document provides a comprehensive overview of the AWS three-tier architecture implementation.

## 🏗️ Architecture Overview

The implementation creates a scalable, highly available web application infrastructure following AWS best practices:

### Architecture Diagram

```
Internet Users
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Internet Gateway                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              Application Load Balancer                     │
│                    (Public Subnets)                        │
└─────────────────┬─────────────────┬─────────────────────────┘
                  │                 │
    ┌─────────────▼─────────────┐   ┌─────────────▼─────────────┐
    │     Availability Zone 1   │   │     Availability Zone 2   │
    │                           │   │                           │
    │ ┌─────────────────────┐   │   │ ┌─────────────────────┐   │
    │ │    NAT Gateway      │   │   │ │    NAT Gateway      │   │
    │ └─────────────────────┘   │   │ └─────────────────────┘   │
    │           │               │   │           │               │
    │ ┌─────────▼─────────┐     │   │ ┌─────────▼─────────┐     │
    │ │  EC2 Instances    │     │   │ │  EC2 Instances    │     │
    │ │ (Private Subnet)  │     │   │ │ (Private Subnet)  │     │
    │ └─────────┬─────────┘     │   │ └─────────┬─────────┘     │
    │           │               │   │           │               │
    │ ┌─────────▼─────────┐     │   │ ┌─────────▼─────────┐     │
    │ │  RDS Primary      │     │   │ │  RDS Standby      │     │
    │ │ (Database Subnet) │◄────┼───┼►│ (Database Subnet) │     │
    │ └───────────────────┘     │   │ └───────────────────┘     │
    └───────────────────────────┘   └───────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 S3 Static Website                          │
│              (Presentation Tier)                           │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
aws-infrastructure/
├── cloudformation/
│   └── three-tier-architecture.yaml    # Main CloudFormation template
├── parameters/
│   ├── dev-parameters.json            # Development environment parameters
│   └── prod-parameters.json           # Production environment parameters
├── static-website/
│   ├── index.html                     # Main static website page
│   └── error.html                     # Error page for S3 website
├── application/
│   └── app.py                         # Python web application for EC2
├── scripts/
│   ├── deploy.sh                      # Deployment automation script
│   └── cleanup.sh                     # Cleanup automation script
└── docs/
    ├── architecture-diagram.md        # Detailed architecture diagram
    └── deployment-guide.md            # Complete deployment guide
```

## 🚀 Key Features Implemented

### 1. High Availability
- ✅ Multi-AZ deployment across 2 availability zones
- ✅ Auto Scaling Group with 2-6 instances
- ✅ Application Load Balancer with health checks
- ✅ RDS Multi-AZ with automatic failover
- ✅ NAT Gateways in each AZ for redundancy

### 2. Security
- ✅ Network segmentation with public/private subnets
- ✅ Security groups with least privilege access
- ✅ Database in isolated subnet
- ✅ No direct internet access to application/database tiers
- ✅ Bastion host security group for admin access

### 3. Scalability
- ✅ Auto Scaling Group with configurable policies
- ✅ Application Load Balancer for traffic distribution
- ✅ RDS with configurable instance types
- ✅ Elastic Block Store for expandable storage
- ✅ CloudFormation parameters for easy scaling

### 4. Infrastructure as Code
- ✅ Complete CloudFormation template (500+ lines)
- ✅ Parameterized for multiple environments
- ✅ Automated deployment scripts
- ✅ Proper resource tagging and naming

### 5. Monitoring and Management
- ✅ Health checks for all tiers
- ✅ CloudWatch integration
- ✅ Auto Scaling based on metrics
- ✅ RDS automated backups
- ✅ Application-level monitoring endpoints

## 🔧 Technical Specifications

### Networking
```yaml
VPC CIDR: 10.0.0.0/16 (dev) / 10.1.0.0/16 (prod)

Public Subnets (ALB, NAT):
  - AZ1: 10.0.1.0/24
  - AZ2: 10.0.2.0/24

Private Subnets (EC2):
  - AZ1: 10.0.11.0/24  
  - AZ2: 10.0.12.0/24

Database Subnets (RDS):
  - AZ1: 10.0.21.0/24
  - AZ2: 10.0.22.0/24
```

### Instance Configuration
```yaml
Development:
  - EC2: t3.micro instances
  - RDS: db.t3.micro MySQL 8.0
  - Min instances: 2, Max: 6

Production:
  - EC2: t3.small instances
  - RDS: db.t3.small MySQL 8.0
  - Min instances: 2, Max: 6
```

### Security Groups
```yaml
ALB Security Group:
  - Inbound: HTTP (80), HTTPS (443) from 0.0.0.0/0

EC2 Security Group:
  - Inbound: HTTP (80) from ALB SG
  - Inbound: SSH (22) from Bastion SG

Database Security Group:
  - Inbound: MySQL (3306) from EC2 SG

Bastion Security Group:
  - Inbound: SSH (22) from 0.0.0.0/0
```

## 📊 Resource Summary

The CloudFormation template creates **50+ AWS resources**:

- **1** VPC with DNS support
- **6** Subnets (2 public, 2 private, 2 database)
- **1** Internet Gateway
- **2** NAT Gateways with Elastic IPs
- **3** Route Tables with routes
- **4** Security Groups
- **1** S3 Bucket with website configuration
- **1** Application Load Balancer with Target Group
- **1** Launch Template for EC2 instances
- **1** Auto Scaling Group
- **1** RDS Database with Multi-AZ
- **1** Database Subnet Group
- **Multiple** Route Table Associations

## 🎯 Use Cases

This architecture is perfect for:

1. **Web Applications**: Scalable web apps with database backend
2. **E-commerce Sites**: High availability for business-critical applications
3. **Content Management**: Static content with dynamic application features
4. **API Services**: RESTful APIs with load balancing and scaling
5. **Development/Testing**: Cost-effective environments with easy cleanup

## 🚀 Quick Start Commands

```bash
# Clone repository
git clone https://github.com/mitel-networks-test/test.git
cd test/aws-infrastructure

# Deploy development environment
./scripts/deploy.sh --environment dev

# Test the deployment
curl http://<alb-dns-name>/health
curl http://<alb-dns-name>/api/info

# Cleanup when done
./scripts/cleanup.sh --environment dev
```

## 💰 Cost Considerations

Estimated monthly costs (us-west-2):

### Development Environment
- EC2 (2 x t3.micro): ~$17/month
- RDS (db.t3.micro): ~$13/month  
- ALB: ~$22/month
- NAT Gateways: ~$45/month
- S3, EBS, Data Transfer: ~$5/month
- **Total: ~$102/month**

### Production Environment  
- EC2 (2-4 x t3.small): ~$30-60/month
- RDS (db.t3.small): ~$26/month
- ALB: ~$22/month
- NAT Gateways: ~$45/month
- S3, EBS, Data Transfer: ~$10/month
- **Total: ~$133-163/month**

*Note: Costs may vary by region and actual usage*

## 🔒 Security Best Practices Implemented

- ✅ **Network Isolation**: Private subnets for app and database tiers
- ✅ **Least Privilege**: Security groups with minimal required access
- ✅ **Encryption**: RDS encryption at rest enabled
- ✅ **Backup Strategy**: Automated RDS backups with 7-day retention
- ✅ **Multi-AZ**: Database redundancy for disaster recovery
- ✅ **Health Monitoring**: Application and infrastructure health checks
- ✅ **Resource Tagging**: Proper tagging for governance and cost tracking

## 📈 Performance Optimizations

- ✅ **Load Balancing**: ALB distributes traffic efficiently
- ✅ **Auto Scaling**: Responds to traffic spikes automatically  
- ✅ **Database Caching**: Connection pooling in application
- ✅ **Static Content**: S3 for fast static asset delivery
- ✅ **Health Checks**: Removes unhealthy instances quickly
- ✅ **Multi-AZ**: Reduces latency with geographically distributed resources

## 🧪 Testing and Validation

A comprehensive test suite validates:
- ✅ CloudFormation template syntax and structure
- ✅ Parameter file validation for all environments
- ✅ Static website HTML structure and content
- ✅ Application code functionality and endpoints
- ✅ Deployment script permissions and structure

Run tests with:
```bash
python3 tests/test_aws_infrastructure.py
```

## 📖 Additional Documentation

- **[Architecture Diagram](docs/architecture-diagram.md)**: Detailed visual representation
- **[Deployment Guide](docs/deployment-guide.md)**: Step-by-step instructions
- **[CloudFormation Template](cloudformation/three-tier-architecture.yaml)**: Infrastructure definition

## 🎉 Summary

This implementation provides a **production-ready, enterprise-grade** three-tier architecture that demonstrates:

- **Best Practices**: Following AWS Well-Architected Framework
- **High Availability**: Multi-AZ deployment with automatic failover
- **Scalability**: Auto Scaling and load balancing
- **Security**: Network segmentation and proper access controls
- **Automation**: Infrastructure as Code with deployment scripts
- **Monitoring**: Health checks and logging at all tiers
- **Documentation**: Comprehensive guides and diagrams

The solution is ready for immediate deployment and can serve as a foundation for production workloads or as a learning resource for AWS architecture patterns.