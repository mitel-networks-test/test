# AWS WAF CloudWatch Insights Queries
# These queries can be used in CloudWatch Logs Insights for real-time WAF log analysis

# Replace 'LOG_GROUP_NAME' with your actual Kinesis Firehose log group name
# Example: /aws/kinesisfirehose/WAFEventAnalysis-dev-waf-logs

## 1. Recent Blocked Requests
```
fields @timestamp, action, httpRequest.clientIP, httpRequest.country, terminatingRuleId, httpRequest.uri
| filter action = "BLOCK"
| sort @timestamp desc
| limit 100
```

## 2. Top Blocked IP Addresses (Last 24 Hours)
```
fields httpRequest.clientIP
| filter action = "BLOCK"
| stats count() as blocked_requests by httpRequest.clientIP
| sort blocked_requests desc
| limit 20
```

## 3. Most Triggered WAF Rules
```
fields terminatingRuleId
| filter action = "BLOCK"
| stats count() as triggers by terminatingRuleId
| sort triggers desc
| limit 15
```

## 4. Blocked Requests by Country
```
fields httpRequest.country
| filter action = "BLOCK"
| stats count() as blocked_count by httpRequest.country
| sort blocked_count desc
| limit 20
```

## 5. SQL Injection Attempts
```
fields @timestamp, httpRequest.clientIP, httpRequest.uri, httpRequest.args
| filter action = "BLOCK" and terminatingRuleId like /AWSManagedRulesSQLiRuleSet/
| sort @timestamp desc
| limit 50
```

## 6. Rate Limited Requests
```
fields @timestamp, httpRequest.clientIP, httpRequest.country
| filter action = "BLOCK" and terminatingRuleId like /RateLimitRule/
| stats count() as rate_limited_requests by httpRequest.clientIP, httpRequest.country
| sort rate_limited_requests desc
| limit 20
```

## 7. Geographic Blocking Activity
```
fields @timestamp, httpRequest.clientIP, httpRequest.country, httpRequest.uri
| filter action = "BLOCK" and terminatingRuleId like /GeoBlockRule/
| sort @timestamp desc
| limit 50
```

## 8. Blocked Requests with User Agent Analysis
```
fields @timestamp, httpRequest.clientIP, httpRequest.headers
| filter action = "BLOCK"
| sort @timestamp desc
| limit 30
```

## 9. Request Volume by Hour
```
fields @timestamp
| stats count() as request_count by bin(5m)
| sort @timestamp desc
```

## 10. Top Blocked URIs
```
fields httpRequest.uri
| filter action = "BLOCK"
| stats count() as blocked_count by httpRequest.uri
| sort blocked_count desc
| limit 25
```

## 11. Detailed Attack Analysis
```
fields @timestamp, action, httpRequest.clientIP, httpRequest.country, httpRequest.uri, httpRequest.httpMethod, terminatingRuleId
| filter action = "BLOCK"
| sort @timestamp desc
| limit 100
```

## 12. Cross-Site Scripting (XSS) Attempts
```
fields @timestamp, httpRequest.clientIP, httpRequest.uri, httpRequest.args
| filter action = "BLOCK" and (terminatingRuleId like /XSS/ or httpRequest.uri like /%3Cscript/ or httpRequest.args like /%3Cscript/)
| sort @timestamp desc
| limit 30
```

## 13. Unusual HTTP Methods
```
fields @timestamp, httpRequest.clientIP, httpRequest.httpMethod, httpRequest.uri
| filter httpRequest.httpMethod not in ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
| sort @timestamp desc
| limit 50
```

## 14. Requests with Multiple Rule Triggers
```
fields @timestamp, httpRequest.clientIP, httpRequest.uri, terminatingRuleId, nonTerminatingMatchingRules
| filter action = "BLOCK" and nonTerminatingMatchingRules.0.ruleId exists
| sort @timestamp desc
| limit 30
```

## 15. Error Rate Analysis (5xx responses)
```
fields @timestamp, httpRequest.clientIP, httpRequest.uri, httpResponse.responseCode
| filter httpResponse.responseCode >= 500
| stats count() as error_count by httpResponse.responseCode, httpRequest.uri
| sort error_count desc
| limit 20
```

## 16. Large Request Body Analysis
```
fields @timestamp, httpRequest.clientIP, httpRequest.uri, httpRequest.requestId
| filter httpRequest.size > 10000
| sort httpRequest.size desc
| limit 30
```

## 17. Suspicious User Agents
```
fields @timestamp, httpRequest.clientIP, httpRequest.headers
| filter action = "BLOCK"
| sort @timestamp desc
| limit 50
```

## 18. Weekly Attack Trend
```
fields @timestamp
| filter action = "BLOCK"
| stats count() as blocked_requests by bin(1h)
| sort @timestamp
```

## 19. Top Attacking ASNs (if available)
```
fields httpRequest.clientIP, httpRequest.country
| filter action = "BLOCK"
| stats count() as attacks by httpRequest.clientIP, httpRequest.country
| sort attacks desc
| limit 25
```

## 20. Request Pattern Analysis
```
fields @timestamp, httpRequest.clientIP, httpRequest.uri, httpRequest.httpMethod
| filter action = "ALLOW"
| stats count() as request_count by httpRequest.uri, httpRequest.httpMethod
| sort request_count desc
| limit 30
```

## Advanced Queries for Security Teams

### Real-time Threat Hunting
```
# Look for potential coordinated attacks
fields @timestamp, httpRequest.clientIP, httpRequest.uri, terminatingRuleId
| filter action = "BLOCK"
| stats count() as attack_count by httpRequest.clientIP
| filter attack_count > 50
| sort attack_count desc
```

### Compliance Reporting
```
# Generate compliance report data
fields @timestamp, action, httpRequest.clientIP, httpRequest.country, terminatingRuleId
| stats 
    count() as total_requests,
    count(action = "BLOCK") as blocked_requests,
    count(action = "ALLOW") as allowed_requests
| eval block_rate = (blocked_requests / total_requests) * 100
```

### Performance Impact Analysis
```
# Analyze WAF performance impact
fields @timestamp, httpRequest.clientIP, httpRequest.uri, responseTimestamp
| filter action = "ALLOW"
| eval response_time = responseTimestamp - timestamp
| stats avg(response_time) as avg_response_time by httpRequest.uri
| sort avg_response_time desc
```

## Usage Notes:

1. **Replace LOG_GROUP_NAME**: Update the log group name in your CloudWatch Logs Insights queries
2. **Time Range**: Adjust the time range in CloudWatch console for your analysis period
3. **Limits**: Increase or decrease the `limit` values based on your needs
4. **Filters**: Modify filters to focus on specific IP ranges, countries, or attack types
5. **Aggregation**: Use different time bins (1m, 5m, 1h, 1d) for trend analysis

## Tips for Effective Analysis:

- Start with broad queries and narrow down based on findings
- Use multiple queries in sequence to build a complete picture
- Export results to CSV for further analysis in Excel or other tools
- Set up CloudWatch alarms based on query results
- Create custom dashboards with these queries as widgets
- Schedule regular analysis using these queries for proactive security monitoring