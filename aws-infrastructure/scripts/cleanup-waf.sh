#!/bin/bash

# AWS WAF Event Analysis Dashboard Cleanup Script
# This script removes all WAF infrastructure and related resources

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
FORCE_DELETE=false

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Cleanup AWS WAF Event Analysis Dashboard resources"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENVIRONMENT   Environment (dev/prod) [default: dev]"
    echo "  -r, --region REGION            AWS region [default: us-east-1]"
    echo "  -s, --stack-prefix PREFIX      Stack name prefix [default: waf-event-analysis]"
    echo "  -f, --force                    Force deletion without confirmation"
    echo "  -h, --help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --environment dev"
    echo "  $0 -e prod -f"
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
        -f|--force)
            FORCE_DELETE=true
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

# Set stack names
WAF_STACK_NAME="${STACK_NAME_PREFIX}-${ENVIRONMENT}"
DASHBOARD_STACK_NAME="${DASHBOARD_STACK_PREFIX}-${ENVIRONMENT}"

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    log_error "Environment must be 'dev' or 'prod'"
    exit 1
fi

log "Starting WAF Event Analysis Dashboard cleanup with the following configuration:"
log "Environment: $ENVIRONMENT"
log "AWS Region: $AWS_REGION"
log "WAF Stack Name: $WAF_STACK_NAME"
log "Dashboard Stack Name: $DASHBOARD_STACK_NAME"
log "Force Delete: $FORCE_DELETE"
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

# Confirmation prompt
confirm_deletion() {
    if [ "$FORCE_DELETE" = false ]; then
        echo ""
        log_warning "WARNING: This will delete the following resources:"
        log_warning "- WAF Web ACL and all associated rules"
        log_warning "- Kinesis Data Firehose stream"
        log_warning "- S3 bucket and all WAF logs"
        log_warning "- Lambda function for log processing"
        log_warning "- SNS topic for threat alerts"
        log_warning "- CloudWatch dashboard and alarms"
        log_warning "- All custom metrics and log data"
        echo ""
        read -p "Are you sure you want to continue? (yes/no): " -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log "Deletion cancelled by user"
            exit 0
        fi
    fi
}

# Empty S3 bucket before deletion
empty_s3_bucket() {
    log "Checking for S3 bucket to empty..."
    
    # Get S3 bucket name from WAF stack outputs
    BUCKET_NAME=$(aws cloudformation describe-stacks \
        --stack-name "$WAF_STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`WAFLogsBucketName`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$BUCKET_NAME" ] && [ "$BUCKET_NAME" != "None" ]; then
        log "Emptying S3 bucket: $BUCKET_NAME"
        
        # Check if bucket exists
        if aws s3api head-bucket --bucket "$BUCKET_NAME" --region "$AWS_REGION" 2>/dev/null; then
            # Delete all objects and versions
            aws s3 rm "s3://$BUCKET_NAME" --recursive --region "$AWS_REGION" || true
            
            # Delete all object versions if versioning is enabled
            aws s3api list-object-versions \
                --bucket "$BUCKET_NAME" \
                --region "$AWS_REGION" \
                --output json \
                --query 'Versions[].{Key:Key,VersionId:VersionId}' 2>/dev/null | \
                jq -r '.[] | "--key " + .Key + " --version-id " + .VersionId' | \
                while read -r args; do
                    aws s3api delete-object --bucket "$BUCKET_NAME" --region "$AWS_REGION" $args || true
                done
            
            # Delete all delete markers
            aws s3api list-object-versions \
                --bucket "$BUCKET_NAME" \
                --region "$AWS_REGION" \
                --output json \
                --query 'DeleteMarkers[].{Key:Key,VersionId:VersionId}' 2>/dev/null | \
                jq -r '.[] | "--key " + .Key + " --version-id " + .VersionId' | \
                while read -r args; do
                    aws s3api delete-object --bucket "$BUCKET_NAME" --region "$AWS_REGION" $args || true
                done
            
            log_success "S3 bucket emptied successfully"
        else
            log_warning "S3 bucket does not exist or is not accessible"
        fi
    else
        log_warning "Could not determine S3 bucket name from stack outputs"
    fi
}

# Delete WAF associations before stack deletion
remove_waf_associations() {
    log "Removing WAF associations..."
    
    # Get WAF Web ACL ARN
    WAF_ACL_ARN=$(aws cloudformation describe-stacks \
        --stack-name "$WAF_STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`WAFWebACLArnALB`].OutputValue' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$WAF_ACL_ARN" ] && [ "$WAF_ACL_ARN" != "None" ]; then
        # List all associations for this Web ACL
        ASSOCIATIONS=$(aws wafv2 list-resources-for-web-acl \
            --web-acl-arn "$WAF_ACL_ARN" \
            --region "$AWS_REGION" \
            --scope REGIONAL \
            --query 'ResourceArns[]' \
            --output text 2>/dev/null || echo "")
        
        if [ -n "$ASSOCIATIONS" ]; then
            for RESOURCE_ARN in $ASSOCIATIONS; do
                log "Disassociating WAF from resource: $RESOURCE_ARN"
                aws wafv2 disassociate-web-acl \
                    --resource-arn "$RESOURCE_ARN" \
                    --region "$AWS_REGION" || true
            done
            log_success "WAF associations removed"
        else
            log "No WAF associations found"
        fi
    else
        log_warning "Could not determine WAF Web ACL ARN"
    fi
}

# Delete CloudFormation stacks
delete_stacks() {
    log "Deleting CloudFormation stacks..."
    
    # Delete Dashboard stack first (has dependencies on WAF stack)
    if aws cloudformation describe-stacks --stack-name "$DASHBOARD_STACK_NAME" --region "$AWS_REGION" &>/dev/null; then
        log "Deleting Dashboard stack: $DASHBOARD_STACK_NAME"
        aws cloudformation delete-stack \
            --stack-name "$DASHBOARD_STACK_NAME" \
            --region "$AWS_REGION"
        
        log "Waiting for Dashboard stack deletion to complete..."
        aws cloudformation wait stack-delete-complete \
            --stack-name "$DASHBOARD_STACK_NAME" \
            --region "$AWS_REGION" || {
            log_warning "Dashboard stack deletion may have timed out or failed"
        }
        log_success "Dashboard stack deleted"
    else
        log_warning "Dashboard stack not found: $DASHBOARD_STACK_NAME"
    fi
    
    # Delete WAF stack
    if aws cloudformation describe-stacks --stack-name "$WAF_STACK_NAME" --region "$AWS_REGION" &>/dev/null; then
        log "Deleting WAF stack: $WAF_STACK_NAME"
        aws cloudformation delete-stack \
            --stack-name "$WAF_STACK_NAME" \
            --region "$AWS_REGION"
        
        log "Waiting for WAF stack deletion to complete..."
        aws cloudformation wait stack-delete-complete \
            --stack-name "$WAF_STACK_NAME" \
            --region "$AWS_REGION" || {
            log_warning "WAF stack deletion may have timed out or failed"
        }
        log_success "WAF stack deleted"
    else
        log_warning "WAF stack not found: $WAF_STACK_NAME"
    fi
}

# Clean up orphaned resources
cleanup_orphaned_resources() {
    log "Checking for orphaned resources..."
    
    # Clean up CloudWatch Log Groups that might not be deleted by CloudFormation
    LOG_GROUPS=$(aws logs describe-log-groups \
        --region "$AWS_REGION" \
        --log-group-name-prefix "/aws/lambda/${STACK_NAME_PREFIX}" \
        --query 'logGroups[].logGroupName' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$LOG_GROUPS" ]; then
        for LOG_GROUP in $LOG_GROUPS; do
            log "Deleting orphaned log group: $LOG_GROUP"
            aws logs delete-log-group \
                --log-group-name "$LOG_GROUP" \
                --region "$AWS_REGION" || true
        done
    fi
    
    # Clean up Firehose log groups
    FIREHOSE_LOG_GROUPS=$(aws logs describe-log-groups \
        --region "$AWS_REGION" \
        --log-group-name-prefix "/aws/kinesisfirehose/${STACK_NAME_PREFIX}" \
        --query 'logGroups[].logGroupName' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$FIREHOSE_LOG_GROUPS" ]; then
        for LOG_GROUP in $FIREHOSE_LOG_GROUPS; do
            log "Deleting orphaned Firehose log group: $LOG_GROUP"
            aws logs delete-log-group \
                --log-group-name "$LOG_GROUP" \
                --region "$AWS_REGION" || true
        done
    fi
    
    log_success "Orphaned resources cleanup completed"
}

# Main cleanup function
main() {
    # Pre-cleanup checks
    check_aws_cli
    
    # Confirm deletion
    confirm_deletion
    
    # Remove WAF associations first
    remove_waf_associations
    
    # Empty S3 bucket
    empty_s3_bucket
    
    # Delete CloudFormation stacks
    delete_stacks
    
    # Clean up orphaned resources
    cleanup_orphaned_resources
    
    log_success "WAF Event Analysis Dashboard cleanup completed successfully!"
    echo ""
    log "All WAF resources have been removed from your AWS account."
    log "Please verify in the AWS Console that all resources have been deleted."
}

# Script entry point
main "$@"