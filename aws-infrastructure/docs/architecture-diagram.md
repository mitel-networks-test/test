# AWS Three-Tier Architecture Diagram

## High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                AWS CLOUD                                        │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                            PRESENTATION TIER                             │  │
│  │  ┌─────────────────┐                    ┌─────────────────────────────┐   │  │
│  │  │   CloudFront    │◄──────────────────►│       Amazon S3            │   │  │
│  │  │   (Optional)    │                    │   Static Website Hosting   │   │  │
│  │  │   Global CDN    │                    │   - index.html             │   │  │
│  │  └─────────────────┘                    │   - error.html             │   │  │
│  │           │                             │   - CSS/JS assets          │   │  │
│  │           │                             └─────────────────────────────┘   │  │
│  └───────────┼─────────────────────────────────────────────────────────────┐ │  │
│              │                                                           │ │  │
│              │                  INTERNET USERS                          │ │  │
│              │                       │                                   │ │  │
│              └───────────────────────┼───────────────────────────────────┘ │  │
│                                      │                                     │  │
│  ┌───────────────────────────────────┼─────────────────────────────────────┐ │  │
│  │                                   │         APPLICATION TIER            │ │  │
│  │                                   │                                     │ │  │
│  │  ┌─────────────────────────────────▼──────────────────────────────────┐  │ │  │
│  │  │                     Internet Gateway                             │  │ │  │
│  │  └─────────────────────────────────┬──────────────────────────────────┘  │ │  │
│  │                                    │                                     │ │  │
│  │  ┌──────────────────────────────────▼──────────────────────────────────┐  │ │  │
│  │  │                  Application Load Balancer                        │  │ │  │
│  │  │                       (Multi-AZ)                                  │  │ │  │
│  │  └──────────────┬─────────────────────────────┬─────────────────────────┘  │ │  │
│  │                 │                             │                            │ │  │
│  │    ┌────────────▼──────────────┐   ┌─────────▼──────────────┐             │ │  │
│  │    │     Public Subnet 1       │   │     Public Subnet 2    │             │ │  │
│  │    │     (AZ-1)                │   │     (AZ-2)             │             │ │  │
│  │    │  ┌─────────────────────┐   │   │  ┌─────────────────────┐│             │ │  │
│  │    │  │    NAT Gateway 1    │   │   │  │    NAT Gateway 2    ││             │ │  │
│  │    │  └─────────────────────┘   │   │  └─────────────────────┘│             │ │  │
│  │    └──────────────┬──────────────┘   └─────────┬───────────────┘             │ │  │
│  │                   │                           │                             │ │  │
│  │    ┌──────────────▼──────────────┐   ┌─────────▼──────────────┐             │ │  │
│  │    │     Private Subnet 1        │   │     Private Subnet 2   │             │ │  │
│  │    │     (AZ-1)                  │   │     (AZ-2)             │             │ │  │
│  │    │  ┌─────────────────────┐    │   │  ┌─────────────────────┐│             │ │  │
│  │    │  │   EC2 Instance 1    │    │   │  │   EC2 Instance 2    ││             │ │  │
│  │    │  │   (Auto Scaling)    │    │   │  │   (Auto Scaling)    ││             │ │  │
│  │    │  └─────────────────────┘    │   │  └─────────────────────┘│             │ │  │
│  │    │  ┌─────────────────────┐    │   │  ┌─────────────────────┐│             │ │  │
│  │    │  │   EC2 Instance 3    │    │   │  │   EC2 Instance 4    ││             │ │  │
│  │    │  │   (Auto Scaling)    │    │   │  │   (Auto Scaling)    ││             │ │  │
│  │    │  └─────────────────────┘    │   │  └─────────────────────┘│             │ │  │
│  │    └─────────────────────────────┘   └────────────────────────┘             │ │  │
│  └─────────────────────────────────────────────────────────────────────────────┘ │  │
│                                      │                                           │  │
│  ┌───────────────────────────────────┼─────────────────────────────────────────┐ │  │
│  │                                   │           DATABASE TIER                 │ │  │
│  │                                   │                                         │ │  │
│  │    ┌──────────────────────────────▼──────────────────────────────────────┐  │ │  │
│  │    │                    Database Subnet Group                           │  │ │  │
│  │    │                                                                    │  │ │  │
│  │    │  ┌────────────────────────┐      ┌─────────────────────────────┐   │  │ │  │
│  │    │  │   Database Subnet 1    │      │    Database Subnet 2        │   │  │ │  │
│  │    │  │       (AZ-1)           │      │        (AZ-2)               │   │  │ │  │
│  │    │  │                        │      │                             │   │  │ │  │
│  │    │  │  ┌──────────────────┐  │      │  ┌──────────────────────┐   │   │  │ │  │
│  │    │  │  │  RDS Primary     │  │      │  │   RDS Standby        │   │   │  │ │  │
│  │    │  │  │   (Master)       │  │◄────►│  │   (Multi-AZ)         │   │   │  │ │  │
│  │    │  │  │   MySQL 8.0      │  │      │  │   (Automatic         │   │   │  │ │  │
│  │    │  │  └──────────────────┘  │      │  │    Failover)         │   │   │  │ │  │
│  │    │  └────────────────────────┘      │  └──────────────────────┘   │   │  │ │  │
│  │    │                                  └─────────────────────────────┘   │  │ │  │
│  │    └──────────────────────────────────────────────────────────────────┘  │ │  │
│  └─────────────────────────────────────────────────────────────────────────────┘ │  │
└─────────────────────────────────────────────────────────────────────────────────┘  │
                                                                                     │
  ┌─────────────────────────────────────────────────────────────────────────────────┘
  │                              SECURITY GROUPS
  │
  │  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  │  ALB Security Group: HTTP/HTTPS from Internet (0.0.0.0/0:80,443)            │
  │  └─────────────────────────────────────────────────────────────────────────────┘
  │
  │  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  │  WebServer Security Group: HTTP from ALB SG + SSH from Bastion SG           │
  │  └─────────────────────────────────────────────────────────────────────────────┘
  │
  │  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  │  Database Security Group: MySQL from WebServer SG (3306)                    │
  │  └─────────────────────────────────────────────────────────────────────────────┘
  │
  │  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  │  Bastion Security Group: SSH from Internet (0.0.0.0/0:22)                   │
  │  └─────────────────────────────────────────────────────────────────────────────┘
  └─────────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Presentation Tier
- **Amazon S3**: Static website hosting for HTML, CSS, JavaScript files
- **CloudFront** (Optional): Global content delivery network for low latency
- **Features**: Cost-effective, scalable, highly available static content delivery

### Application Tier
- **Application Load Balancer**: Distributes traffic across multiple EC2 instances
- **Auto Scaling Group**: Automatically scales EC2 instances based on demand
- **EC2 Instances**: Run the application code in private subnets
- **Multiple Availability Zones**: Ensures high availability
- **NAT Gateways**: Provide internet access for private subnet instances

### Database Tier
- **Amazon RDS**: Managed relational database service
- **Multi-AZ Deployment**: Automatic failover to standby instance
- **Database Subnet Group**: Isolates database in private subnets
- **Automated Backups**: Point-in-time recovery and snapshots

## Network Architecture

### VPC Configuration
- **CIDR Block**: 10.0.0.0/16 (dev) / 10.1.0.0/16 (prod)
- **Availability Zones**: 2 AZs for high availability

### Subnet Design
```
Public Subnets (ALB, NAT Gateways):
├── Public Subnet 1 (AZ-1): 10.0.1.0/24
└── Public Subnet 2 (AZ-2): 10.0.2.0/24

Private Subnets (EC2 Application Servers):
├── Private Subnet 1 (AZ-1): 10.0.11.0/24
└── Private Subnet 2 (AZ-2): 10.0.12.0/24

Database Subnets (RDS):
├── Database Subnet 1 (AZ-1): 10.0.21.0/24
└── Database Subnet 2 (AZ-2): 10.0.22.0/24
```

## Traffic Flow

### User Request Flow
1. **User** → Internet Gateway → Application Load Balancer
2. **ALB** → Private Subnet EC2 Instances (Round Robin)
3. **EC2** → Database Subnet RDS Instance
4. **Response** flows back through the same path

### Static Content Flow
1. **User** → S3 Static Website (or CloudFront if configured)
2. **Direct S3 access** for static assets

## High Availability Features

1. **Multi-AZ Deployment**: All tiers span multiple availability zones
2. **Auto Scaling**: EC2 instances automatically scale based on demand
3. **Load Balancing**: ALB distributes traffic across healthy instances
4. **Database Failover**: RDS Multi-AZ provides automatic failover
5. **NAT Gateway Redundancy**: One NAT Gateway per AZ for outbound internet access

## Security Features

1. **Network Segmentation**: Separate subnets for each tier
2. **Security Groups**: Restrictive firewall rules between tiers
3. **Private Subnets**: Application and database tiers not directly accessible from internet
4. **IAM Roles**: Proper permissions for EC2 instances and services
5. **Encryption**: RDS encryption at rest and in transit

## Scalability Features

1. **Horizontal Scaling**: Auto Scaling Group can add/remove EC2 instances
2. **Database Scaling**: RDS supports read replicas and instance size changes
3. **Load Distribution**: ALB handles increasing traffic loads
4. **Storage Scaling**: EBS volumes and RDS storage can be expanded

## Monitoring and Logging

1. **CloudWatch Metrics**: Monitor all AWS resources
2. **ALB Access Logs**: Track all load balancer requests
3. **VPC Flow Logs**: Monitor network traffic
4. **Application Logs**: EC2 instances log application events
5. **Database Logs**: RDS provides query and error logs