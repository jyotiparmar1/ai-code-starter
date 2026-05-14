package com.example.demo.service;

import java.util.List;
import org.springframework.stereotype.Service;
import com.example.demo.entity.Department;
import com.example.demo.repository.DepartmentRepository;

@Service
public class DepartmentService {

    private final DepartmentRepository repository;

    public DepartmentService(DepartmentRepository repository) {
        this.repository = repository;
    }

    
    public Department createDepartment(Department payload) {
        
        return repository.save(payload);
        
    }

    
    public List<Department> getAllDepartments() {
        
        return repository.findAll();
        
    }

    
    public Department getDepartmentById(Long id) {
        
        return repository.findById(id).orElse(null);
        
    }

    
    public Department updateDepartment(Long id, Department payload) {
        
        payload.setId(id);
        return repository.save(payload);
        
    }

    
    public void deleteDepartment(Long id) {
        
        repository.deleteById(id);
        
    }

    
}