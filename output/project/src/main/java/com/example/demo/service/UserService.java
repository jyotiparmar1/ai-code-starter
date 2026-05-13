package com.example.demo.service;

import java.util.List;
import org.springframework.stereotype.Service;
import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;

@Service
public class UserService {

    private final UserRepository repository;

    public UserService(UserRepository repository) {
        this.repository = repository;
    }

    
    public User createUser(User payload) {
        
        return repository.save(payload);
        
    }

    
    public List<User> getAllUsers() {
        
        return repository.findAll();
        
    }

    
    public User getUserById(Long id) {
        
        return repository.findById(id).orElse(null);
        
    }

    
    public User updateUser(Long id, User payload) {
        
        payload.setId(id);
        return repository.save(payload);
        
    }

    
    public void deleteUser(Long id) {
        
        repository.deleteById(id);
        
    }

    
}