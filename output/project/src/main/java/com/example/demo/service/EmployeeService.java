package com.example.demo.service;

import java.util.List;
import org.springframework.stereotype.Service;
import com.example.demo.entity.Employee;
import com.example.demo.repository.EmployeeRepository;

@Service
public class EmployeeService {

    private final EmployeeRepository repository;

    public EmployeeService(EmployeeRepository repository) {
        this.repository = repository;
    }

    
    public Employee createEmployee(Employee payload) {
        
        return repository.save(payload);
        
    }

    
    public List<Employee> getAllEmployees() {
        
        return repository.findAll();
        
    }

    
    public Employee getEmployeeById(Long id) {
        
        return repository.findById(id).orElse(null);
        
    }

    
    public Employee updateEmployee(Long id, Employee payload) {
        
        payload.setId(id);
        return repository.save(payload);
        
    }

    
    public void deleteEmployee(Long id) {
        
        repository.deleteById(id);
        
    }

    
}