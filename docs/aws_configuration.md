# AWS Configuration Guide

This guide provides comprehensive instructions for configuring AWS services and credentials for the Bedrock Agent application.

## AWS Account Setup

### Step 1: Create AWS Account
1. Visit https://aws.amazon.com
2. Create a new account or sign in to existing account
3. Complete account verification process

### Step 2: Enable Bedrock Service
1. Navigate to AWS Bedrock console
2. Request access to foundation models
3. Wait for approval (typically 1-2 business days)

## Credential Configuration

### Method 1: AWS CLI Configuration
```bash
aws configure
```
Provide:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region (e.g., us-east-1)
- Output format (json)

### Method 2: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Method 3: IAM Roles (EC2/Lambda)
For applications running on AWS infrastructure, use IAM roles instead of hardcoded credentials.

## Required Permissions

Create an IAM policy with the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

## Supported Regions

AWS Bedrock is available in the following regions:
- us-east-1 (N. Virginia)
- us-west-2 (Oregon)
- eu-west-1 (Ireland)
- ap-southeast-1 (Singapore)

Choose the region closest to your users for optimal performance.

## Model Selection

### Available Foundation Models

1. **Anthropic Claude 3 Sonnet** (Recommended)
   - Model ID: `anthropic.claude-3-sonnet-20240229-v1:0`
   - Best for: General purpose Q&A and summarization
   - Context window: 200k tokens

2. **Amazon Titan Text**
   - Model ID: `amazon.titan-text-express-v1`
   - Best for: Text generation and completion
   - Context window: 8k tokens

3. **AI21 Jurassic**
   - Model ID: `ai21.j2-ultra-v1`
   - Best for: Creative writing and analysis
   - Context window: 8k tokens

## Cost Optimization

### Tips to Reduce Costs
1. Use appropriate model sizes for your use case
2. Implement caching for frequently asked questions
3. Set reasonable token limits
4. Monitor usage through AWS Cost Explorer

### Pricing Factors
- Model type and size
- Number of input/output tokens
- Request frequency
- Region selection

## Security Best Practices

1. **Never commit credentials to source code**
2. **Use IAM roles when possible**
3. **Rotate access keys regularly**
4. **Enable CloudTrail for audit logging**
5. **Implement least privilege access**

## Troubleshooting

### Common Configuration Issues

1. **Credentials not found**
   - Verify AWS CLI configuration
   - Check environment variables
   - Ensure credentials file exists

2. **Access denied errors**
   - Verify IAM permissions
   - Check model access requests
   - Confirm region availability

3. **Model not available**
   - Request access to specific models
   - Check regional availability
   - Verify model ID spelling

### Debug Commands

Test your configuration:
```bash
# Test AWS connection
aws sts get-caller-identity

# List available Bedrock models
aws bedrock list-foundation-models --region us-east-1

# Test agent status
python3 bedrock_agent.py status
```