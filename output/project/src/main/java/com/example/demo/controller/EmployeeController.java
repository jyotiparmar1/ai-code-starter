package com.example.demo.controller;

import org.springframework.web.bind.annotation.*;
import java.util.List;
import com.example.demo.service.EmployeeService;
import com.example.demo.entity.Employee;

@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    private final EmployeeService service;

    public EmployeeController(EmployeeService service) {
        this.service = service;
    }

    
    
    
    
    @PostMapping("/api/employees")
    public Employee createEmployee(@RequestBody Employee payload) {
        return service.createEmployee(payload);
    }

    
    
    
    
    
    @GetMapping("/api/employees")
    public List<Employee> getAllEmployees() {
        return service.getAllEmployees();
    }

    
    
    
    
    
    @GetMapping("/api/employees/{id}")
    public Employee getEmployeeById(@PathVariable Long id) {
        return service.getEmployeeById(id);
    }

    
    
    
    
    
    @PutMapping("/api/employees/{id}")
    public Employee updateEmployee(@PathVariable Long id, @RequestBody Employee payload) {
        return service.updateEmployee(id, payload);
    }

    
    
    
    
    
    @DeleteMapping("/api/employees/{id}")
    public void deleteEmployee(@PathVariable Long id) {
        service.deleteEmployee(id);
    }

    
    
}