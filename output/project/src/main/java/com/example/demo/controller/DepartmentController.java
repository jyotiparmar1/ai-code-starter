package com.example.demo.controller;

import org.springframework.web.bind.annotation.*;
import java.util.List;
import com.example.demo.service.DepartmentService;
import com.example.demo.entity.Department;

@RestController
@RequestMapping("/api/departments")
public class DepartmentController {

    private final DepartmentService service;

    public DepartmentController(DepartmentService service) {
        this.service = service;
    }

    
    
    
    
    @PostMapping("/api/departments")
    public Department createDepartment(@RequestBody Department payload) {
        return service.createDepartment(payload);
    }

    
    
    
    
    
    @GetMapping("/api/departments")
    public List<Department> getAllDepartments() {
        return service.getAllDepartments();
    }

    
    
    
    
    
    @GetMapping("/api/departments/{id}")
    public Department getDepartmentById(@PathVariable Long id) {
        return service.getDepartmentById(id);
    }

    
    
    
    
    
    @PutMapping("/api/departments/{id}")
    public Department updateDepartment(@PathVariable Long id, @RequestBody Department payload) {
        return service.updateDepartment(id, payload);
    }

    
    
    
    
    
    @DeleteMapping("/api/departments/{id}")
    public void deleteDepartment(@PathVariable Long id) {
        service.deleteDepartment(id);
    }

    
    
}