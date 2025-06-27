#!/bin/bash

# AWS WAF Event Analysis Dashboard Deployment Script
# This script deploys the complete WAF infrastructure with event analysis capabilities

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
AWS_REGION="us-east-1"
STACK_NAME_PREFIX="waf-event-analysis"
DASHBOARD_STACK_PREFIX="waf-dashboard"
FORCE_DEPLOY=false
THREE_TIER_STACK_NAME=""

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Deploy AWS WAF Event Analysis Dashboard"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENVIRONMENT   Environment (dev/prod) [default: dev]"
    echo "  -r, --region REGION            AWS region [default: us-east-1]"
    echo "  -s, --stack-prefix PREFIX      Stack name prefix [default: waf-event-analysis]"
    echo "  -t, --three-tier-stack NAME    Name of the three-tier architecture stack"
    echo "  -f, --force                    Force deployment without confirmation"
    echo "  -h, --help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment dev --three-tier-stack my-three-tier-dev"
    echo "  $0 -e prod -t my-three-tier-prod -f"
}

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -s|--stack-prefix)
            STACK_NAME_PREFIX="$2"
            shift 2
            ;;
        -t|--three-tier-stack)
            THREE_TIER_STACK_NAME="$2"
            shift 2
            ;;
        -f|--force)
            FORCE_DEPLOY=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$THREE_TIER_STACK_NAME" ]; then
    log_error "Three-tier stack name is required. Use -t or --three-tier-stack option."
    usage
    exit 1
fi

# Set stack names
WAF_STACK_NAME="${STACK_NAME_PREFIX}-${ENVIRONMENT}"
DASHBOARD_STACK_NAME="${DASHBOARD_STACK_PREFIX}-${ENVIRONMENT}"

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    log_error "Environment must be 'dev' or 'prod'"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log "Starting WAF Event Analysis Dashboard deployment with the following configuration:"
log "Environment: $ENVIRONMENT"
log "AWS Region: $AWS_REGION"
log "WAF Stack Name: $WAF_STACK_NAME"
log "Dashboard Stack Name: $DASHBOARD_STACK_NAME"
log "Three-Tier Stack: $THREE_TIER_STACK_NAME"
log "Force Deploy: $FORCE_DEPLOY"
log ""

# Check if AWS CLI is configured
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    log_success "AWS CLI is configured and working"
}

# Get ALB ARN from three-tier stack
get_alb_arn() {
    log "Retrieving Application Load Balancer ARN from three-tier stack..."
    
    ALB_ARN=$(aws cloudformation describe-stacks \
        --stack-name "$THREE_TIER_STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApplicationLoadBalancerArn`].OutputValue' \
        --output text 2>/dev/null)
    
    if [ -z "$ALB_ARN" ] || [ "$ALB_ARN" = "None" ]; then
        # Try alternative output key
        ALB_ARN=$(aws cloudformation describe-stacks \
            --stack-name "$THREE_TIER_STACK_NAME" \
            --region "$AWS_REGION" \
            --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerArn`].OutputValue' \
            --output text 2>/dev/null)
    fi
    
    if [ -z "$ALB_ARN" ] || [ "$ALB_ARN" = "None" ]; then
        log_error "Could not retrieve ALB ARN from stack: $THREE_TIER_STACK_NAME"
        log_error "Please ensure the three-tier stack exists and has an ALB output."
        exit 1
    fi
    
    log_success "Retrieved ALB ARN: $ALB_ARN"
}

# Deploy WAF stack
deploy_waf_stack() {
    log "Deploying WAF Event Analysis stack..."
    
    # Create temporary parameter file with ALB ARN
    TEMP_PARAMS="/tmp/waf-${ENVIRONMENT}-parameters-$(date +%s).json"
    
    # Read the original parameter file and update ALB ARN
    jq --arg alb_arn "$ALB_ARN" '
        map(if .ParameterKey == "ApplicationLoadBalancerArn" then .ParameterValue = $alb_arn else . end)
    ' "$PROJECT_ROOT/parameters/waf-${ENVIRONMENT}-parameters.json" > "$TEMP_PARAMS"
    
    aws cloudformation deploy \
        --template-file "$PROJECT_ROOT/cloudformation/waf-event-analysis.yaml" \
        --stack-name "$WAF_STACK_NAME" \
        --parameter-overrides file://"$TEMP_PARAMS" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$AWS_REGION" \
        --no-fail-on-empty-changeset
    
    # Clean up temporary file
    rm -f "$TEMP_PARAMS"
    
    if [ $? -eq 0 ]; then
        log_success "WAF stack deployed successfully"
    else
        log_error "Failed to deploy WAF stack"
        exit 1
    fi
}

# Deploy Dashboard stack
deploy_dashboard_stack() {
    log "Deploying WAF Dashboard stack..."
    
    aws cloudformation deploy \
        --template-file "$PROJECT_ROOT/cloudformation/waf-dashboard.yaml" \
        --stack-name "$DASHBOARD_STACK_NAME" \
        --parameter-overrides file://"$PROJECT_ROOT/parameters/waf-dashboard-${ENVIRONMENT}-parameters.json" \
        --capabilities CAPABILITY_IAM \
        --region "$AWS_REGION" \
        --no-fail-on-empty-changeset
    
    if [ $? -eq 0 ]; then
        log_success "Dashboard stack deployed successfully"
    else
        log_error "Failed to deploy Dashboard stack"
        exit 1
    fi
}

# Get stack outputs
get_stack_outputs() {
    log "Retrieving stack outputs..."
    
    # WAF Stack outputs
    WAF_WEB_ACL_ARN=$(aws cloudformation describe-stacks \
        --stack-name "$WAF_STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`WAFWebACLArnALB`].OutputValue' \
        --output text)
    
    WAF_LOGS_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "$WAF_STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`WAFLogsBucketName`].OutputValue' \
        --output text)
    
    FIREHOSE_STREAM=$(aws cloudformation describe-stacks \
        --stack-name "$WAF_STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`FirehoseStreamName`].OutputValue' \
        --output text)
    
    THREAT_ALERT_TOPIC=$(aws cloudformation describe-stacks \
        --stack-name "$WAF_STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ThreatAlertTopicArn`].OutputValue' \
        --output text)
    
    # Dashboard Stack outputs
    DASHBOARD_URL=$(aws cloudformation describe-stacks \
        --stack-name "$DASHBOARD_STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`DashboardURL`].OutputValue' \
        --output text)
    
    log_success "Stack outputs retrieved successfully"
}

# Display deployment summary
display_summary() {
    echo ""
    log_success "=== WAF Event Analysis Dashboard Deployment Complete ==="
    echo ""
    log "WAF Configuration:"
    log "  WAF Web ACL ARN: $WAF_WEB_ACL_ARN"
    log "  Logs Bucket: $WAF_LOGS_BUCKET"
    log "  Firehose Stream: $FIREHOSE_STREAM"
    log "  Threat Alert Topic: $THREAT_ALERT_TOPIC"
    echo ""
    log "Dashboard Access:"
    log "  Dashboard URL: $DASHBOARD_URL"
    echo ""
    log "Next Steps:"
    log "  1. Configure SNS topic subscribers for threat alerts"
    log "  2. Wait 10-15 minutes for WAF logs to start flowing"
    log "  3. Access the CloudWatch dashboard to view analytics"
    log "  4. Test WAF rules by sending blocked requests"
    echo ""
    log_warning "Note: It may take several minutes for metrics to appear in the dashboard"
}

# Confirmation prompt
confirm_deployment() {
    if [ "$FORCE_DEPLOY" = false ]; then
        echo ""
        log_warning "This will deploy the following AWS resources:"
        log_warning "- WAF v2 Web ACL with managed rules"
        log_warning "- Kinesis Data Firehose stream"
        log_warning "- S3 bucket for WAF logs"
        log_warning "- Lambda function for log processing"
        log_warning "- SNS topic for threat alerts"
        log_warning "- CloudWatch dashboard and alarms"
        echo ""
        read -p "Are you sure you want to continue? (yes/no): " -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log "Deployment cancelled by user"
            exit 0
        fi
    fi
}

# Main deployment function
main() {
    # Pre-deployment checks
    check_aws_cli
    
    # Confirm deployment
    confirm_deployment
    
    # Get ALB ARN from three-tier stack
    get_alb_arn
    
    # Deploy stacks
    deploy_waf_stack
    deploy_dashboard_stack
    
    # Get outputs and display summary
    get_stack_outputs
    display_summary
    
    log_success "WAF Event Analysis Dashboard deployment completed successfully!"
}

# Script entry point
main "$@"