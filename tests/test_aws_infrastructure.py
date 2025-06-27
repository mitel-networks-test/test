#!/usr/bin/env python3
"""
Test script for AWS Three-Tier Architecture CloudFormation template
"""

import json
import yaml
import os
import sys
from pathlib import Path

def test_cloudformation_template():
    """Test CloudFormation template syntax and structure"""
    print("Testing CloudFormation template...")
    
    template_path = Path("aws-infrastructure/cloudformation/three-tier-architecture.yaml")
    
    if not template_path.exists():
        print(f"❌ Template file not found: {template_path}")
        return False
    
    try:
        # Read the file content for basic validation
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check for required sections in the file content
        required_sections = ['AWSTemplateFormatVersion:', 'Description:', 'Parameters:', 'Resources:', 'Outputs:']
        for section in required_sections:
            if section not in content:
                print(f"❌ Missing required section: {section}")
                return False
        
        print(f"✅ Template structure is valid")
        
        # Count sections by looking for YAML patterns
        param_count = content.count('    Type: String') + content.count('    Type: AWS::')
        print(f"✅ Template contains parameters and resources")
        
        # Validate key resources exist in content
        required_resources = [
            'VPC:', 'InternetGateway:', 'PublicSubnet1:', 'PublicSubnet2:',
            'PrivateSubnet1:', 'PrivateSubnet2:', 'DatabaseSubnet1:', 'DatabaseSubnet2:',
            'ApplicationLoadBalancer:', 'AutoScalingGroup:', 'DatabaseCluster:',
            'StaticWebsiteBucket:'
        ]
        
        for resource in required_resources:
            if resource not in content:
                print(f"❌ Missing required resource: {resource}")
                return False
        
        # Check for CloudFormation intrinsic functions
        cf_functions = ['!Ref', '!GetAtt', '!Sub', '!Select', '!GetAZs']
        functions_found = sum(1 for func in cf_functions if func in content)
        
        if functions_found < 3:
            print(f"❌ Template should use CloudFormation intrinsic functions")
            return False
        
        print(f"✅ All required resources are present")
        print(f"✅ Template uses CloudFormation intrinsic functions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing template: {e}")
        return False

def test_parameter_files():
    """Test parameter files"""
    print("\\nTesting parameter files...")
    
    param_files = [
        "aws-infrastructure/parameters/dev-parameters.json",
        "aws-infrastructure/parameters/prod-parameters.json"
    ]
    
    for param_file in param_files:
        param_path = Path(param_file)
        
        if not param_path.exists():
            print(f"❌ Parameter file not found: {param_path}")
            return False
        
        try:
            with open(param_path, 'r') as f:
                params = json.load(f)
            
            if not isinstance(params, list):
                print(f"❌ Parameter file should contain a list: {param_file}")
                return False
            
            # Check required parameters
            required_params = ['EnvironmentName', 'VpcCIDR', 'DBUsername', 'DBPassword']
            param_keys = [p.get('ParameterKey') for p in params]
            
            for req_param in required_params:
                if req_param not in param_keys:
                    print(f"❌ Missing required parameter {req_param} in {param_file}")
                    return False
            
            print(f"✅ Parameter file valid: {param_file}")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error in {param_file}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error testing parameter file {param_file}: {e}")
            return False
    
    return True

def test_static_website():
    """Test static website files"""
    print("\\nTesting static website files...")
    
    website_files = [
        "aws-infrastructure/static-website/index.html",
        "aws-infrastructure/static-website/error.html"
    ]
    
    for website_file in website_files:
        file_path = Path(website_file)
        
        if not file_path.exists():
            print(f"❌ Website file not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic HTML validation
            if not content.strip().startswith('<!DOCTYPE html>'):
                print(f"❌ Invalid HTML structure in {website_file}")
                return False
            
            if '<html' not in content or '</html>' not in content:
                print(f"❌ Missing HTML tags in {website_file}")
                return False
            
            print(f"✅ Website file valid: {website_file}")
            
        except Exception as e:
            print(f"❌ Error testing website file {website_file}: {e}")
            return False
    
    return True

def test_application_code():
    """Test application code"""
    print("\\nTesting application code...")
    
    app_file = Path("aws-infrastructure/application/app.py")
    
    if not app_file.exists():
        print(f"❌ Application file not found: {app_file}")
        return False
    
    try:
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Check for required components
        required_components = [
            'class ThreeTierAppHandler',
            'def serve_health_check',
            'def serve_instance_info',
            'def serve_database_info',
            'if __name__ == \'__main__\':'
        ]
        
        for component in required_components:
            if component not in content:
                print(f"❌ Missing component in application: {component}")
                return False
        
        print(f"✅ Application code structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error testing application code: {e}")
        return False

def test_deployment_scripts():
    """Test deployment scripts"""
    print("\\nTesting deployment scripts...")
    
    scripts = [
        "aws-infrastructure/scripts/deploy.sh",
        "aws-infrastructure/scripts/cleanup.sh"
    ]
    
    for script in scripts:
        script_path = Path(script)
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False
        
        # Check if script is executable
        if not os.access(script_path, os.X_OK):
            print(f"❌ Script not executable: {script_path}")
            return False
        
        try:
            with open(script_path, 'r') as f:
                content = f.read()
            
            # Basic script validation
            if not content.startswith('#!/bin/bash'):
                print(f"❌ Script missing shebang: {script_path}")
                return False
            
            print(f"✅ Script valid: {script_path}")
            
        except Exception as e:
            print(f"❌ Error testing script {script_path}: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Running AWS Three-Tier Architecture Tests\\n")
    
    tests = [
        test_cloudformation_template,
        test_parameter_files,
        test_static_website,
        test_application_code,
        test_deployment_scripts
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("❌ Test failed!")
    
    print(f"\\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())