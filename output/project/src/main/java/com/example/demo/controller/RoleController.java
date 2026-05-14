package com.example.demo.controller;

import org.springframework.web.bind.annotation.*;
import java.util.List;
import com.example.demo.service.RoleService;
import com.example.demo.entity.Role;

@RestController
@RequestMapping("/api/roles")
public class RoleController {

    private final RoleService service;

    public RoleController(RoleService service) {
        this.service = service;
    }

    
    
    
    
    @PostMapping("/api/roles")
    public Role createRole(@RequestBody Role payload) {
        return service.createRole(payload);
    }

    
    
    
    
    
    @GetMapping("/api/roles")
    public List<Role> getAllRoles() {
        return service.getAllRoles();
    }

    
    
    
    
    
    @GetMapping("/api/roles/{id}")
    public Role getRoleById(@PathVariable Long id) {
        return service.getRoleById(id);
    }

    
    
    
    
    
    @PutMapping("/api/roles/{id}")
    public Role updateRole(@PathVariable Long id, @RequestBody Role payload) {
        return service.updateRole(id, payload);
    }

    
    
    
    
    
    @DeleteMapping("/api/roles/{id}")
    public void deleteRole(@PathVariable Long id) {
        service.deleteRole(id);
    }

    
    
}