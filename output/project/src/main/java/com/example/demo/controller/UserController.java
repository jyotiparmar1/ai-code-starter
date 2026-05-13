package com.example.demo.controller;

import org.springframework.web.bind.annotation.*;
import java.util.List;
import com.example.demo.service.UserService;
import com.example.demo.entity.User;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService service;

    public UserController(UserService service) {
        this.service = service;
    }

    
    
    
    
    @PostMapping("")
    public User createUser(@RequestBody User payload) {
        return service.createUser(payload);
    }

    
    
    
    
    
    @GetMapping("")
    public List<User> getAllUsers() {
        return service.getAllUsers();
    }

    
    
    
    
    
    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) {
        return service.getUserById(id);
    }

    
    
    
    
    
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody User payload) {
        return service.updateUser(id, payload);
    }

    
    
    
    
    
    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) {
        service.deleteUser(id);
    }

    
    
}