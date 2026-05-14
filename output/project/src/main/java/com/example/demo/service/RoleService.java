package com.example.demo.service;

import java.util.List;
import org.springframework.stereotype.Service;
import com.example.demo.entity.Role;
import com.example.demo.repository.RoleRepository;

@Service
public class RoleService {

    private final RoleRepository repository;

    public RoleService(RoleRepository repository) {
        this.repository = repository;
    }

    
    public Role createRole(Role payload) {
        
        return repository.save(payload);
        
    }

    
    public List<Role> getAllRoles() {
        
        return repository.findAll();
        
    }

    
    public Role getRoleById(Long id) {
        
        return repository.findById(id).orElse(null);
        
    }

    
    public Role updateRole(Long id, Role payload) {
        
        payload.setId(id);
        return repository.save(payload);
        
    }

    
    public void deleteRole(Long id) {
        
        repository.deleteById(id);
        
    }

    
}