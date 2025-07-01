package com.example.threetier.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.net.InetAddress;
import java.net.UnknownHostException;

@RestController
@CrossOrigin(origins = "*")
public class ThreeTierController {

    @GetMapping("/")
    public ResponseEntity<String> home() {
        return ResponseEntity.ok(getMainPageHtml());
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> healthStatus = new HashMap<>();
        healthStatus.put("status", "healthy");
        healthStatus.put("timestamp", LocalDateTime.now());
        healthStatus.put("service", "Three-Tier Backend");
        healthStatus.put("version", "1.0.0");
        return ResponseEntity.ok(healthStatus);
    }

    @GetMapping("/api/info")
    public ResponseEntity<Map<String, Object>> instanceInfo() {
        Map<String, Object> info = new HashMap<>();
        try {
            InetAddress localhost = InetAddress.getLocalHost();
            info.put("hostname", localhost.getHostName());
            info.put("ip_address", localhost.getHostAddress());
        } catch (UnknownHostException e) {
            info.put("hostname", "unknown");
            info.put("ip_address", "unknown");
        }
        
        info.put("service", "Java Spring Boot Backend");
        info.put("version", "1.0.0");
        info.put("java_version", System.getProperty("java.version"));
        info.put("spring_boot_version", "3.2.0");
        info.put("timestamp", LocalDateTime.now());
        info.put("uptime_seconds", getUptimeSeconds());
        info.put("memory_usage", getMemoryUsage());
        
        return ResponseEntity.ok(info);
    }

    @GetMapping("/api/database")
    public ResponseEntity<Map<String, Object>> databaseInfo() {
        Map<String, Object> dbInfo = new HashMap<>();
        // This would normally connect to RDS, but for demo purposes we'll simulate
        dbInfo.put("status", "connected");
        dbInfo.put("type", "MySQL RDS");
        dbInfo.put("multi_az", true);
        dbInfo.put("backup_retention", "7 days");
        dbInfo.put("engine_version", "8.0.35");
        dbInfo.put("storage_type", "gp2");
        dbInfo.put("allocated_storage", "20 GB");
        dbInfo.put("connection_count", 5);
        dbInfo.put("last_backup", LocalDateTime.now().withHour(2).withMinute(0).withSecond(0));
        dbInfo.put("timestamp", LocalDateTime.now());
        
        return ResponseEntity.ok(dbInfo);
    }

    private String getMainPageHtml() {
        return "<!DOCTYPE html>" +
                "<html><head><title>Three-Tier Backend API</title>" +
                "<style>body{font-family:Arial,sans-serif;padding:20px;background:#f5f5f5;}" +
                ".container{max-width:800px;margin:0 auto;background:white;padding:30px;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1);}" +
                "h1{color:#333;text-align:center;}" +
                ".endpoint{background:#f8f9fa;padding:15px;margin:10px 0;border-radius:5px;border-left:4px solid #007bff;}" +
                ".method{background:#28a745;color:white;padding:5px 10px;border-radius:3px;font-weight:bold;margin-right:10px;}" +
                "</style></head><body>" +
                "<div class='container'>" +
                "<h1>🚀 Three-Tier Architecture - Java Backend API</h1>" +
                "<p>Welcome to the Java Spring Boot backend service for the AWS Three-Tier Architecture.</p>" +
                "<h2>Available Endpoints:</h2>" +
                "<div class='endpoint'><span class='method'>GET</span>/health - Health check endpoint</div>" +
                "<div class='endpoint'><span class='method'>GET</span>/api/info - Instance information</div>" +
                "<div class='endpoint'><span class='method'>GET</span>/api/database - Database status</div>" +
                "<h2>Service Information:</h2>" +
                "<ul>" +
                "<li><strong>Service:</strong> Java Spring Boot Backend</li>" +
                "<li><strong>Version:</strong> 1.0.0</li>" +
                "<li><strong>Java Version:</strong> " + System.getProperty("java.version") + "</li>" +
                "<li><strong>Timestamp:</strong> " + LocalDateTime.now() + "</li>" +
                "</ul>" +
                "</div></body></html>";
    }

    private long getUptimeSeconds() {
        return java.lang.management.ManagementFactory.getRuntimeMXBean().getUptime() / 1000;
    }

    private Map<String, Object> getMemoryUsage() {
        Runtime runtime = Runtime.getRuntime();
        Map<String, Object> memory = new HashMap<>();
        memory.put("max_memory_mb", runtime.maxMemory() / (1024 * 1024));
        memory.put("total_memory_mb", runtime.totalMemory() / (1024 * 1024));
        memory.put("free_memory_mb", runtime.freeMemory() / (1024 * 1024));
        memory.put("used_memory_mb", (runtime.totalMemory() - runtime.freeMemory()) / (1024 * 1024));
        return memory;
    }
}