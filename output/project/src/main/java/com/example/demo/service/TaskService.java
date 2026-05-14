package com.example.demo.service;

import java.util.List;
import org.springframework.stereotype.Service;
import com.example.demo.entity.Task;
import com.example.demo.repository.TaskRepository;

@Service
public class TaskService {

    private final TaskRepository repository;

    public TaskService(TaskRepository repository) {
        this.repository = repository;
    }

    
    public Task createTask(Task payload) {
        
        return repository.save(payload);
        
    }

    
    public List<Task> getAllTasks() {
        
        return repository.findAll();
        
    }

    
    public Task getTaskById(Long id) {
        
        return repository.findById(id).orElse(null);
        
    }

    
    public Task updateTask(Long id, Task payload) {
        
        payload.setId(id);
        return repository.save(payload);
        
    }

    
    public void deleteTask(Long id) {
        
        repository.deleteById(id);
        
    }

    
}