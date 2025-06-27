#!/usr/bin/env python3
"""
AWS WAF Event Analysis Tools
Provides command-line tools for analyzing WAF logs and generating security reports
"""

import boto3
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
import gzip
import sys
import os

# Optional imports for visualization
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

class WAFAnalyzer:
    def __init__(self, bucket_name, region='us-east-1'):
        """Initialize WAF Analyzer with S3 bucket and AWS region"""
        self.bucket_name = bucket_name
        self.region = region
        self.s3_client = boto3.client('s3', region_name=region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        
    def get_log_files(self, start_date, end_date):
        """Get list of WAF log files for date range"""
        log_files = []
        current_date = start_date
        
        while current_date <= end_date:
            prefix = f"year={current_date.year}/month={current_date.month:02d}/day={current_date.day:02d}/"
            
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        if obj['Key'].endswith('.gz'):
                            log_files.append(obj['Key'])
                            
            except Exception as e:
                print(f"Error listing objects for {prefix}: {e}")
                
            current_date += timedelta(days=1)
            
        return sorted(log_files)
    
    def download_and_parse_logs(self, log_files, max_files=None):
        """Download and parse WAF log files"""
        logs = []
        processed_files = 0
        
        for log_file in log_files:
            if max_files and processed_files >= max_files:
                break
                
            try:
                print(f"Processing {log_file}...")
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=log_file)
                
                # Decompress the gzipped content
                content = gzip.decompress(response['Body'].read()).decode('utf-8')
                
                # Parse each line as JSON
                for line in content.strip().split('\n'):
                    if line:
                        try:
                            log_entry = json.loads(line)
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue
                            
                processed_files += 1
                
            except Exception as e:
                print(f"Error processing {log_file}: {e}")
                continue
        
        print(f"Processed {processed_files} files, parsed {len(logs)} log entries")
        return logs
    
    def analyze_threat_patterns(self, logs):
        """Analyze threat patterns from WAF logs"""
        analysis = {
            'total_requests': len(logs),
            'blocked_requests': 0,
            'allowed_requests': 0,
            'blocked_by_rule': defaultdict(int),
            'blocked_by_country': defaultdict(int),
            'blocked_by_ip': defaultdict(int),
            'top_blocked_uris': defaultdict(int),
            'attack_methods': defaultdict(int),
            'hourly_distribution': defaultdict(int)
        }
        
        for log in logs:
            action = log.get('action', '')
            timestamp = datetime.fromtimestamp(log.get('timestamp', 0) / 1000)
            hour = timestamp.hour
            
            if action == 'BLOCK':
                analysis['blocked_requests'] += 1
                
                # Rule analysis
                rule_id = log.get('terminatingRuleId', 'Unknown')
                analysis['blocked_by_rule'][rule_id] += 1
                
                # Geographic analysis
                country = log.get('httpRequest', {}).get('country', 'Unknown')
                analysis['blocked_by_country'][country] += 1
                
                # IP analysis
                client_ip = log.get('httpRequest', {}).get('clientIP', 'Unknown')
                analysis['blocked_by_ip'][client_ip] += 1
                
                # URI analysis
                uri = log.get('httpRequest', {}).get('uri', 'Unknown')
                analysis['top_blocked_uris'][uri] += 1
                
                # Attack method detection
                http_method = log.get('httpRequest', {}).get('httpMethod', 'Unknown')
                user_agent = ''
                headers = log.get('httpRequest', {}).get('headers', [])
                for header in headers:
                    if header.get('name', '').lower() == 'user-agent':
                        user_agent = header.get('value', '')
                        break
                
                # Classify attack type
                if 'sql' in rule_id.lower() or 'sqli' in rule_id.lower():
                    analysis['attack_methods']['SQL Injection'] += 1
                elif 'xss' in rule_id.lower():
                    analysis['attack_methods']['Cross-Site Scripting'] += 1
                elif 'ratelimit' in rule_id.lower():
                    analysis['attack_methods']['Rate Limiting'] += 1
                elif 'geo' in rule_id.lower():
                    analysis['attack_methods']['Geographic Block'] += 1
                else:
                    analysis['attack_methods']['Other'] += 1
                    
            elif action == 'ALLOW':
                analysis['allowed_requests'] += 1
            
            # Hourly distribution
            analysis['hourly_distribution'][hour] += 1
        
        return analysis
    
    def generate_report(self, analysis, output_file=None):
        """Generate comprehensive security report"""
        report = []
        report.append("=" * 60)
        report.append("AWS WAF Security Analysis Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY STATISTICS")
        report.append("-" * 30)
        report.append(f"Total Requests: {analysis['total_requests']:,}")
        report.append(f"Blocked Requests: {analysis['blocked_requests']:,}")
        report.append(f"Allowed Requests: {analysis['allowed_requests']:,}")
        
        if analysis['total_requests'] > 0:
            block_rate = (analysis['blocked_requests'] / analysis['total_requests']) * 100
            report.append(f"Block Rate: {block_rate:.2f}%")
        
        report.append("")
        
        # Top blocked rules
        report.append("TOP TRIGGERED RULES")
        report.append("-" * 30)
        sorted_rules = sorted(analysis['blocked_by_rule'].items(), key=lambda x: x[1], reverse=True)
        for rule, count in sorted_rules[:10]:
            report.append(f"{rule}: {count:,} blocks")
        
        report.append("")
        
        # Top attacking countries
        report.append("TOP ATTACKING COUNTRIES")
        report.append("-" * 30)
        sorted_countries = sorted(analysis['blocked_by_country'].items(), key=lambda x: x[1], reverse=True)
        for country, count in sorted_countries[:10]:
            report.append(f"{country}: {count:,} blocks")
        
        report.append("")
        
        # Top attacking IPs
        report.append("TOP ATTACKING IP ADDRESSES")
        report.append("-" * 30)
        sorted_ips = sorted(analysis['blocked_by_ip'].items(), key=lambda x: x[1], reverse=True)
        for ip, count in sorted_ips[:10]:
            report.append(f"{ip}: {count:,} blocks")
        
        report.append("")
        
        # Attack methods
        report.append("ATTACK METHODS DISTRIBUTION")
        report.append("-" * 30)
        sorted_methods = sorted(analysis['attack_methods'].items(), key=lambda x: x[1], reverse=True)
        for method, count in sorted_methods:
            percentage = (count / analysis['blocked_requests']) * 100 if analysis['blocked_requests'] > 0 else 0
            report.append(f"{method}: {count:,} ({percentage:.1f}%)")
        
        report.append("")
        
        # Top blocked URIs
        report.append("TOP BLOCKED URIs")
        report.append("-" * 30)
        sorted_uris = sorted(analysis['top_blocked_uris'].items(), key=lambda x: x[1], reverse=True)
        for uri, count in sorted_uris[:10]:
            report.append(f"{uri}: {count:,} blocks")
        
        # Generate the report text
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Report saved to {output_file}")
        else:
            print(report_text)
        
        return report_text
    
    def create_visualizations(self, analysis, output_dir='./waf_charts'):
        """Create visualization charts for the analysis"""
        if not VISUALIZATION_AVAILABLE:
            print("Visualization libraries not available. Install with:")
            print("pip install matplotlib seaborn pandas")
            return
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Block vs Allow pie chart
        plt.figure(figsize=(10, 6))
        labels = ['Blocked', 'Allowed']
        sizes = [analysis['blocked_requests'], analysis['allowed_requests']]
        colors = ['#ff6b6b', '#4ecdc4']
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('WAF Request Distribution')
        plt.axis('equal')
        plt.savefig(f'{output_dir}/request_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Top blocked countries bar chart
        plt.figure(figsize=(12, 8))
        sorted_countries = sorted(analysis['blocked_by_country'].items(), key=lambda x: x[1], reverse=True)[:10]
        countries, counts = zip(*sorted_countries) if sorted_countries else ([], [])
        
        plt.bar(countries, counts, color='#ff6b6b')
        plt.title('Top 10 Attacking Countries')
        plt.xlabel('Country')
        plt.ylabel('Blocked Requests')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/top_countries.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Attack methods distribution
        plt.figure(figsize=(10, 8))
        methods = list(analysis['attack_methods'].keys())
        counts = list(analysis['attack_methods'].values())
        
        plt.pie(counts, labels=methods, autopct='%1.1f%%', startangle=90)
        plt.title('Attack Methods Distribution')
        plt.axis('equal')
        plt.savefig(f'{output_dir}/attack_methods.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Hourly distribution
        plt.figure(figsize=(12, 6))
        hours = list(range(24))
        hourly_counts = [analysis['hourly_distribution'].get(hour, 0) for hour in hours]
        
        plt.plot(hours, hourly_counts, marker='o', linewidth=2, markersize=6)
        plt.title('Hourly Request Distribution')
        plt.xlabel('Hour of Day')
        plt.ylabel('Number of Requests')
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 24, 2))
        plt.tight_layout()
        plt.savefig(f'{output_dir}/hourly_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 5. Top blocked rules
        plt.figure(figsize=(14, 8))
        sorted_rules = sorted(analysis['blocked_by_rule'].items(), key=lambda x: x[1], reverse=True)[:10]
        rules, counts = zip(*sorted_rules) if sorted_rules else ([], [])
        
        # Truncate rule names for better display
        truncated_rules = [rule[:30] + '...' if len(rule) > 30 else rule for rule in rules]
        
        plt.barh(truncated_rules, counts, color='#4ecdc4')
        plt.title('Top 10 Triggered WAF Rules')
        plt.xlabel('Number of Blocks')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig(f'{output_dir}/top_rules.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to {output_dir}/")

def main():
    parser = argparse.ArgumentParser(description='AWS WAF Event Analysis Tool')
    parser.add_argument('--bucket', required=True, help='S3 bucket name containing WAF logs')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--max-files', type=int, help='Maximum number of log files to process')
    parser.add_argument('--output-report', help='Output file for text report')
    parser.add_argument('--output-charts', default='./waf_charts', help='Output directory for charts')
    parser.add_argument('--no-charts', action='store_true', help='Skip chart generation')
    
    args = parser.parse_args()
    
    # Parse dates
    try:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError:
        print("Error: Date format should be YYYY-MM-DD")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = WAFAnalyzer(args.bucket, args.region)
    
    # Get log files
    print(f"Searching for log files from {args.start_date} to {args.end_date}...")
    log_files = analyzer.get_log_files(start_date, end_date)
    
    if not log_files:
        print("No log files found for the specified date range")
        sys.exit(1)
    
    print(f"Found {len(log_files)} log files")
    
    # Download and parse logs
    logs = analyzer.download_and_parse_logs(log_files, args.max_files)
    
    if not logs:
        print("No log entries found")
        sys.exit(1)
    
    # Analyze threat patterns
    print("Analyzing threat patterns...")
    analysis = analyzer.analyze_threat_patterns(logs)
    
    # Generate report
    print("Generating security report...")
    analyzer.generate_report(analysis, args.output_report)
    
    # Create visualizations
    if not args.no_charts:
        if VISUALIZATION_AVAILABLE:
            print("Creating visualizations...")
            analyzer.create_visualizations(analysis, args.output_charts)
        else:
            print("Warning: matplotlib/seaborn/pandas not installed. Skipping chart generation.")
            print("Install with: pip install matplotlib seaborn pandas")
    
    print("Analysis complete!")

if __name__ == '__main__':
    main()