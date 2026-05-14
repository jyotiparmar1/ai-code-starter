package com.example.demo.controller;

import org.springframework.web.bind.annotation.*;
import java.util.List;
import com.example.demo.service.TaskService;
import com.example.demo.entity.Task;

@RestController
@RequestMapping("/api/tasks")
public class TaskController {

    private final TaskService service;

    public TaskController(TaskService service) {
        this.service = service;
    }

    
    
    
    
    @PostMapping("")
    public Task createTask(@RequestBody Task payload) {
        return service.createTask(payload);
    }

    
    
    
    
    
    @GetMapping("")
    public List<Task> getAllTasks() {
        return service.getAllTasks();
    }

    
    
    
    
    
    @GetMapping("/{id}")
    public Task getTaskById(@PathVariable Long id) {
        return service.getTaskById(id);
    }

    
    
    
    
    
    @PutMapping("/{id}")
    public Task updateTask(@PathVariable Long id, @RequestBody Task payload) {
        return service.updateTask(id, payload);
    }

    
    
    
    
    
    @DeleteMapping("/{id}")
    public void deleteTask(@PathVariable Long id) {
        service.deleteTask(id);
    }

    
    
}