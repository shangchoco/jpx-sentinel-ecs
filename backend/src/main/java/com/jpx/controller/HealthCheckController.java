package com.jpx.controller;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;

@RestController
public class HealthCheckController {
    @GetMapping("/health")
    public String health() {
        return "I am alive!";
    }
}