# AWS WAF Event Analysis Dashboard - Complete Implementation Guide

## Overview

This implementation provides a comprehensive **AWS WAF (Web Application Firewall) v2** solution with real-time event analysis capabilities, designed to protect web applications and provide detailed security insights through an interactive dashboard.

## 🚀 Key Features

### 1. Advanced WAF Protection
- ✅ AWS Managed Rule Groups (Common, SQL Injection, Known Bad Inputs)
- ✅ Custom rate limiting rules (2000 requests per 5 minutes per IP)
- ✅ Geographic blocking capabilities
- ✅ Real-time threat detection and blocking
- ✅ Support for both ALB and CloudFront protection

### 2. Event Analysis Pipeline
- ✅ Kinesis Data Firehose for real-time log streaming
- ✅ Lambda-based log processing with threat intelligence
- ✅ S3 storage with partitioned data for analytics
- ✅ Custom CloudWatch metrics for security insights
- ✅ SNS notifications for immediate threat alerts

### 3. Interactive Dashboard
- ✅ Real-time CloudWatch dashboard with 12+ widgets
- ✅ Geographic attack visualization
- ✅ Rule performance analytics
- ✅ Top attackers and threat patterns
- ✅ Custom log queries and insights

### 4. Monitoring and Alerting
- ✅ CloudWatch alarms for security events
- ✅ SNS topic for threat notifications
- ✅ Automated response capabilities
- ✅ Historical trend analysis

## 🏗️ Architecture Components

### Core Infrastructure
```
Internet → AWS WAF → ALB → EC2 Instances → RDS
              ↓
         Event Analysis Pipeline
              ↓
    Kinesis → Lambda → S3 + CloudWatch
              ↓
         SNS Alerts + Dashboard
```

### Security Rule Set
1. **AWS Managed Rules Common Rule Set**: Protection against OWASP Top 10
2. **Known Bad Inputs Rule Set**: Protection against known malicious inputs
3. **SQL Injection Rule Set**: Advanced SQLi protection
4. **Rate Limiting**: IP-based request throttling
5. **Geographic Blocking**: Country-specific access control

## 📊 Resource Summary

The WAF Event Analysis deployment creates **25+ AWS resources**:

- **1** WAF v2 Web ACL with 5 rules
- **1** Kinesis Data Firehose delivery stream
- **1** S3 bucket for log storage with lifecycle policies
- **1** Lambda function for log processing (300+ lines of code)
- **1** SNS topic for threat alerts
- **1** CloudWatch dashboard with 12 widgets
- **3** CloudWatch alarms for security monitoring
- **Multiple** IAM roles and policies for secure operations

## 🔧 Technical Specifications

### WAF Configuration
```yaml
Rules:
  - Common Rule Set (Priority 1)
  - Known Bad Inputs (Priority 2) 
  - SQL Injection Protection (Priority 3)
  - Rate Limiting: 2000 req/5min (Priority 4)
  - Geographic Blocking: CN, RU, KP (Priority 5)

Logging:
  - All blocked requests
  - Sampled allowed requests
  - Real-time streaming to Kinesis
```

### Event Processing
```yaml
Kinesis Firehose:
  - Buffer Size: 5 MB
  - Buffer Interval: 5 minutes
  - Compression: GZIP
  - Error Handling: Separate S3 prefix

Lambda Processing:
  - Runtime: Python 3.9
  - Memory: 512 MB
  - Timeout: 5 minutes
  - Custom metrics generation
```

### Storage and Retention
```yaml
S3 Storage:
  - Partitioned by year/month/day/hour
  - Lifecycle policies for cost optimization
  - Encryption at rest (AES-256)
  - Cross-region replication ready

Log Retention:
  - Development: 7 days
  - Production: 30 days
  - Customizable per environment
```

## 🚀 Quick Start Deployment

### Prerequisites
1. **AWS CLI** configured with appropriate permissions
2. **Existing three-tier architecture** deployed
3. **jq** installed for JSON processing
4. **IAM permissions** for WAF, Kinesis, Lambda, S3, CloudWatch, SNS

### Deployment Steps

1. **Clone the repository**:
```bash
git clone https://github.com/mitel-networks-test/test.git
cd test/aws-infrastructure
```

2. **Deploy WAF Event Analysis**:
```bash
# For development environment
./scripts/deploy-waf.sh --environment dev --three-tier-stack my-three-tier-dev

# For production environment
./scripts/deploy-waf.sh --environment prod --three-tier-stack my-three-tier-prod --force
```

3. **Access the dashboard**:
```bash
# The deployment script will output the dashboard URL
# Example: https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=WAFEventAnalysis-dev-WAF-Event-Analysis-Dashboard
```

### Manual Deployment (Alternative)

1. **Deploy WAF Infrastructure**:
```bash
aws cloudformation deploy \
  --template-file cloudformation/waf-event-analysis.yaml \
  --stack-name waf-event-analysis-dev \
  --parameter-overrides file://parameters/waf-dev-parameters.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

2. **Deploy Dashboard**:
```bash
aws cloudformation deploy \
  --template-file cloudformation/waf-dashboard.yaml \
  --stack-name waf-dashboard-dev \
  --parameter-overrides file://parameters/waf-dashboard-dev-parameters.json \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

## 📈 Dashboard Features

### Real-time Metrics Widgets

1. **WAF Request Overview**
   - Allowed vs Blocked requests over time
   - Success rate percentage
   - Total request volume

2. **Rule Performance Analysis**
   - Blocked requests by rule type
   - Rule trigger frequency
   - Most effective rules

3. **Geographic Threat Map**
   - Requests by country
   - Blocked traffic visualization
   - Attack origin analysis

4. **Top Threats Display**
   - Most blocked IP addresses
   - Attack pattern identification
   - Threat severity scoring

### Advanced Log Queries

The dashboard includes pre-built log queries for:

```sql
-- Recent blocked requests
SOURCE '/aws/kinesisfirehose/WAFEventAnalysis-dev-waf-logs'
| fields @timestamp, action, httpRequest.clientIP, httpRequest.country, terminatingRuleId, httpRequest.uri
| filter action = "BLOCK"
| sort @timestamp desc
| limit 100

-- Top blocked IP addresses
SOURCE '/aws/kinesisfirehose/WAFEventAnalysis-dev-waf-logs'
| fields httpRequest.clientIP
| filter action = "BLOCK"
| stats count() as blocked_requests by httpRequest.clientIP
| sort blocked_requests desc
| limit 10

-- Most triggered rules
SOURCE '/aws/kinesisfirehose/WAFEventAnalysis-dev-waf-logs'
| fields terminatingRuleId
| filter action = "BLOCK"
| stats count() as triggers by terminatingRuleId
| sort triggers desc
| limit 10
```

## 🔔 Alerting Configuration

### Automated Alerts

1. **High Block Rate Alarm**
   - Threshold: 100 blocked requests in 15 minutes
   - Evaluation: 3 consecutive periods
   - Action: SNS notification

2. **SQL Injection Detection**
   - Threshold: 5 SQLi attempts in 5 minutes
   - Evaluation: 1 period
   - Action: Immediate SNS alert

3. **Rate Limit Triggers**
   - Threshold: 50 rate-limited requests in 10 minutes
   - Evaluation: 2 consecutive periods
   - Action: SNS notification + custom metric

### SNS Topic Configuration

Configure SNS subscriptions for threat alerts:

```bash
# Email notifications
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:WAFEventAnalysis-dev-threat-alerts \
  --protocol email \
  --notification-endpoint security-team@company.com

# SMS alerts for critical threats
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:WAFEventAnalysis-dev-threat-alerts \
  --protocol sms \
  --notification-endpoint +1234567890

# Slack integration via webhook
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:WAFEventAnalysis-dev-threat-alerts \
  --protocol https \
  --notification-endpoint https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

## 🧪 Testing the WAF

### Simulate Attacks for Testing

1. **SQL Injection Test**:
```bash
# This should be blocked by the SQLi rule
curl -X POST "https://your-alb-domain.com/search" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query='; DROP TABLE users; --"
```

2. **Rate Limiting Test**:
```bash
# Send rapid requests to trigger rate limiting
for i in {1..2500}; do
  curl -s "https://your-alb-domain.com/" > /dev/null &
done
```

3. **Geographic Blocking Test**:
```bash
# Test from blocked countries (use VPN/proxy)
curl -H "CF-IPCountry: CN" "https://your-alb-domain.com/"
```

### Verify Protection

1. **Check WAF Logs**:
```bash
aws logs start-query \
  --log-group-name "/aws/kinesisfirehose/WAFEventAnalysis-dev-waf-logs" \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, action, httpRequest.clientIP | filter action = "BLOCK"'
```

2. **View Metrics**:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/WAFV2 \
  --metric-name BlockedRequests \
  --dimensions Name=WebACL,Value=WAFEventAnalysis-dev-alb-web-acl Name=Region,Value=us-east-1 Name=Rule,Value=ALL \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Sum
```

## 🔧 Customization Options

### Adding Custom Rules

Add custom WAF rules by modifying the CloudFormation template:

```yaml
- Name: CustomIPBlockRule
  Priority: 6
  Action:
    Block: {}
  Statement:
    IPSetReferenceStatement:
      ARN: !GetAtt CustomIPSet.Arn
  VisibilityConfig:
    SampledRequestsEnabled: true
    CloudWatchMetricsEnabled: true
    MetricName: CustomIPBlockMetric
```

### Custom Lambda Processing

Extend the Lambda function to add custom threat detection:

```python
def detect_custom_threats(log_data):
    """Add custom threat detection logic"""
    user_agent = log_data.get('httpRequest', {}).get('headers', [])
    
    # Detect suspicious user agents
    for header in user_agent:
        if header.get('name', '').lower() == 'user-agent':
            ua_value = header.get('value', '').lower()
            if any(bot in ua_value for bot in ['sqlmap', 'nikto', 'nmap']):
                send_custom_alert('Suspicious User Agent Detected', log_data)
                return True
    
    return False
```

### Additional Dashboard Widgets

Add custom widgets to the CloudWatch dashboard:

```json
{
  "type": "metric",
  "x": 0,
  "y": 30,
  "width": 12,
  "height": 6,
  "properties": {
    "metrics": [
      [ "WAF/EventAnalysis", "SuspiciousUserAgents" ],
      [ ".", "CustomThreatDetected" ],
      [ ".", "APIAbuse" ]
    ],
    "view": "timeSeries",
    "stacked": false,
    "region": "${AWS::Region}",
    "title": "Custom Threat Metrics",
    "period": 300,
    "stat": "Sum"
  }
}
```

## 🧹 Cleanup and Maintenance

### Automated Cleanup

Use the provided cleanup script:

```bash
# Clean up development environment
./scripts/cleanup-waf.sh --environment dev

# Clean up production environment with force flag
./scripts/cleanup-waf.sh --environment prod --force
```

### Manual Cleanup

1. **Delete CloudFormation Stacks**:
```bash
# Delete dashboard first (has dependencies)
aws cloudformation delete-stack --stack-name waf-dashboard-dev

# Wait for completion, then delete WAF stack
aws cloudformation delete-stack --stack-name waf-event-analysis-dev
```

2. **Clean S3 Bucket** (if needed):
```bash
aws s3 rm s3://wafeventanalysis-dev-waf-logs-123456789012-us-east-1 --recursive
```

### Cost Optimization

1. **Adjust Log Retention**: Modify retention periods based on compliance needs
2. **S3 Lifecycle Policies**: Configure intelligent tiering for cost savings
3. **CloudWatch Log Retention**: Set appropriate retention for Lambda logs
4. **Kinesis Buffer Settings**: Optimize buffer size and interval for costs

## 📚 Additional Resources

### AWS Documentation
- [AWS WAF v2 Developer Guide](https://docs.aws.amazon.com/waf/latest/developerguide/)
- [Kinesis Data Firehose Documentation](https://docs.aws.amazon.com/firehose/)
- [CloudWatch Dashboards User Guide](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Dashboards.html)

### Security Best Practices
- [AWS WAF Security Best Practices](https://docs.aws.amazon.com/waf/latest/developerguide/waf-best-practices.html)
- [OWASP Top 10 Web Application Security Risks](https://owasp.org/www-project-top-ten/)
- [AWS Security Blog - WAF](https://aws.amazon.com/blogs/security/tag/aws-waf/)

### Monitoring and Troubleshooting
- [WAF Monitoring and Logging](https://docs.aws.amazon.com/waf/latest/developerguide/monitoring-cloudwatch.html)
- [Kinesis Data Firehose Troubleshooting](https://docs.aws.amazon.com/firehose/latest/dev/troubleshooting.html)
- [Lambda Monitoring Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-functions.html)

## 🎉 Summary

This WAF Event Analysis Dashboard implementation provides:

- **Enterprise-grade Security**: Multi-layered protection with AWS managed rules
- **Real-time Visibility**: Comprehensive dashboard with threat analytics
- **Automated Response**: Immediate alerting and custom threat detection
- **Scalable Architecture**: Handles high-volume traffic and log processing
- **Cost-effective**: Optimized for both security and operational costs
- **Easy Deployment**: Automated scripts and comprehensive documentation

The solution is production-ready and can serve as a foundation for advanced security monitoring and threat response capabilities in AWS environments.

## 📞 Support and Contributions

For issues, feature requests, or contributions:
1. Review the architecture documentation
2. Check CloudWatch logs for troubleshooting
3. Test with the provided examples
4. Follow AWS security best practices
5. Monitor costs and optimize as needed

This implementation demonstrates enterprise-grade security architecture with comprehensive event analysis capabilities, providing both protection and deep visibility into web application security threats.