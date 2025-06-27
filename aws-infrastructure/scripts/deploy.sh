#!/bin/bash

# AWS Three-Tier Architecture Deployment Script
# This script deploys the CloudFormation stack for the three-tier architecture

set -e

# Configuration
STACK_NAME=""
ENVIRONMENT=""
AWS_REGION="us-west-2"
TEMPLATE_FILE="../cloudformation/three-tier-architecture.yaml"
PARAMETERS_FILE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Environment (dev|prod) [required]"
    echo "  -s, --stack-name NAME    CloudFormation stack name [optional]"
    echo "  -r, --region REGION      AWS region [default: us-west-2]"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment dev"
    echo "  $0 --environment prod --stack-name my-three-tier-stack"
    echo "  $0 -e dev -r us-east-1"
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

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check if template file exists
    if [ ! -f "$TEMPLATE_FILE" ]; then
        log_error "CloudFormation template not found: $TEMPLATE_FILE"
        exit 1
    fi
    
    # Check if parameters file exists
    if [ ! -f "$PARAMETERS_FILE" ]; then
        log_error "Parameters file not found: $PARAMETERS_FILE"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

validate_template() {
    log "Validating CloudFormation template..."
    
    if aws cloudformation validate-template --template-body file://$TEMPLATE_FILE --region $AWS_REGION > /dev/null; then
        log_success "Template validation successful"
    else
        log_error "Template validation failed"
        exit 1
    fi
}

deploy_stack() {
    log "Deploying CloudFormation stack: $STACK_NAME"
    
    # Check if stack already exists
    if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION &> /dev/null; then
        log_warning "Stack $STACK_NAME already exists. Updating..."
        OPERATION="update-stack"
    else
        log "Stack $STACK_NAME does not exist. Creating..."
        OPERATION="create-stack"
    fi
    
    # Deploy the stack
    aws cloudformation $OPERATION \\
        --stack-name $STACK_NAME \\
        --template-body file://$TEMPLATE_FILE \\
        --parameters file://$PARAMETERS_FILE \\
        --capabilities CAPABILITY_IAM \\
        --region $AWS_REGION \\
        --tags Key=Environment,Value=$ENVIRONMENT Key=Project,Value=ThreeTierArchitecture
    
    log "Stack deployment initiated. Waiting for completion..."
    
    # Wait for stack operation to complete
    if [ "$OPERATION" = "create-stack" ]; then
        aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $AWS_REGION
    else
        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $AWS_REGION
    fi
    
    log_success "Stack deployment completed successfully"
}

get_outputs() {
    log "Retrieving stack outputs..."
    
    aws cloudformation describe-stacks \\
        --stack-name $STACK_NAME \\
        --region $AWS_REGION \\
        --query 'Stacks[0].Outputs' \\
        --output table
}

upload_static_content() {
    log "Uploading static website content to S3..."
    
    # Get S3 bucket name from stack outputs
    BUCKET_NAME=$(aws cloudformation describe-stacks \\
        --stack-name $STACK_NAME \\
        --region $AWS_REGION \\
        --query 'Stacks[0].Outputs[?OutputKey==\`StaticWebsiteURL\`].OutputValue' \\
        --output text | sed 's|http://||' | sed 's|\\.s3-website.*||')
    
    if [ -n "$BUCKET_NAME" ]; then
        aws s3 sync ../static-website/ s3://$BUCKET_NAME/ --region $AWS_REGION
        log_success "Static content uploaded to S3 bucket: $BUCKET_NAME"
    else
        log_warning "Could not determine S3 bucket name. Please upload static content manually."
    fi
}

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -s|--stack-name)
                STACK_NAME="$2"
                shift 2
                ;;
            -r|--region)
                AWS_REGION="$2"
                shift 2
                ;;
            -h|--help)
                print_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
    
    # Validate required parameters
    if [ -z "$ENVIRONMENT" ]; then
        log_error "Environment is required. Use --environment or -e"
        print_usage
        exit 1
    fi
    
    if [ "$ENVIRONMENT" != "dev" ] && [ "$ENVIRONMENT" != "prod" ]; then
        log_error "Environment must be 'dev' or 'prod'"
        exit 1
    fi
    
    # Set default stack name if not provided
    if [ -z "$STACK_NAME" ]; then
        STACK_NAME="three-tier-architecture-$ENVIRONMENT"
    fi
    
    # Set parameters file based on environment
    PARAMETERS_FILE="../parameters/$ENVIRONMENT-parameters.json"
    
    log "Starting deployment with the following configuration:"
    log "Environment: $ENVIRONMENT"
    log "Stack Name: $STACK_NAME"
    log "AWS Region: $AWS_REGION"
    log "Parameters File: $PARAMETERS_FILE"
    log ""
    
    # Execute deployment steps
    check_prerequisites
    validate_template
    deploy_stack
    upload_static_content
    get_outputs
    
    log_success "Deployment completed successfully!"
    log ""
    log "Next steps:"
    log "1. Access the static website using the StaticWebsiteURL output"
    log "2. Access the application tier using the ApplicationLoadBalancerURL output"
    log "3. Monitor the resources in the AWS console"
}

# Script entry point
main "$@"