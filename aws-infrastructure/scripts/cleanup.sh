#!/bin/bash

# AWS Three-Tier Architecture Cleanup Script
# This script removes the CloudFormation stack and associated resources

set -e

# Configuration
STACK_NAME=""
ENVIRONMENT=""
AWS_REGION="us-west-2"
FORCE_DELETE=false

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
    echo "  -f, --force              Force deletion without confirmation"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment dev"
    echo "  $0 --environment prod --force"
    echo "  $0 -e dev -s my-three-tier-stack"
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

confirm_deletion() {
    if [ "$FORCE_DELETE" = false ]; then
        echo ""
        log_warning "WARNING: This will delete the following resources:"
        log_warning "- CloudFormation stack: $STACK_NAME"
        log_warning "- All EC2 instances"
        log_warning "- Application Load Balancer"
        log_warning "- RDS database (with final snapshot)"
        log_warning "- S3 bucket and static content"
        log_warning "- VPC and all networking components"
        echo ""
        read -p "Are you sure you want to continue? (yes/no): " -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log "Deletion cancelled by user"
            exit 0
        fi
    fi
}

empty_s3_bucket() {
    log "Emptying S3 bucket before stack deletion..."
    
    # Get S3 bucket name from stack outputs
    BUCKET_NAME=$(aws cloudformation describe-stacks \\
        --stack-name $STACK_NAME \\
        --region $AWS_REGION \\
        --query 'Stacks[0].Outputs[?OutputKey==\`StaticWebsiteURL\`].OutputValue' \\
        --output text 2>/dev/null | sed 's|http://||' | sed 's|\\.s3-website.*||' || echo "")
    
    if [ -n "$BUCKET_NAME" ]; then
        log "Found S3 bucket: $BUCKET_NAME"
        aws s3 rm s3://$BUCKET_NAME --recursive --region $AWS_REGION 2>/dev/null || true
        log_success "S3 bucket emptied"
    else
        log_warning "Could not determine S3 bucket name"
    fi
}

delete_stack() {
    log "Checking if stack $STACK_NAME exists..."
    
    # Check if stack exists
    if ! aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION &> /dev/null; then
        log_warning "Stack $STACK_NAME does not exist in region $AWS_REGION"
        return 0
    fi
    
    log "Deleting CloudFormation stack: $STACK_NAME"
    
    # Empty S3 bucket first to avoid deletion issues
    empty_s3_bucket
    
    # Delete the stack
    aws cloudformation delete-stack \\
        --stack-name $STACK_NAME \\
        --region $AWS_REGION
    
    log "Stack deletion initiated. Waiting for completion..."
    
    # Wait for stack deletion to complete
    aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $AWS_REGION
    
    log_success "Stack deletion completed successfully"
}

cleanup_orphaned_resources() {
    log "Checking for orphaned resources..."
    
    # Note: In a production environment, you might want to add additional
    # cleanup for resources that might not be properly deleted by CloudFormation
    
    log_warning "Manual cleanup may be required for:"
    log_warning "- Elastic IPs not automatically released"
    log_warning "- Security groups with dependencies"
    log_warning "- Key pairs created manually"
    log_warning "- IAM roles/policies if created outside the stack"
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
            -f|--force)
                FORCE_DELETE=true
                shift
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
    
    # Check if AWS CLI is installed and configured
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    log "Starting cleanup with the following configuration:"
    log "Environment: $ENVIRONMENT"
    log "Stack Name: $STACK_NAME"
    log "AWS Region: $AWS_REGION"
    log "Force Delete: $FORCE_DELETE"
    log ""
    
    # Confirm deletion
    confirm_deletion
    
    # Execute cleanup
    delete_stack
    cleanup_orphaned_resources
    
    log_success "Cleanup completed successfully!"
}

# Script entry point
main "$@"