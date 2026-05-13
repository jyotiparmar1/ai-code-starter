package com.example.demo.controller;

import org.springframework.web.bind.annotation.*;
import java.util.List;
import com.example.demo.service.ProjectService;
import com.example.demo.entity.Project;

@RestController
@RequestMapping("/api/projects")
public class ProjectController {

    private final ProjectService service;

    public ProjectController(ProjectService service) {
        this.service = service;
    }

    
    
    
    
    @PostMapping("")
    public Project createProject(@RequestBody Project payload) {
        return service.createProject(payload);
    }

    
    
    
    
    
    @GetMapping("")
    public List<Project> getAllProjects() {
        return service.getAllProjects();
    }

    
    
    
    
    
    @GetMapping("/{id}")
    public Project getProjectById(@PathVariable Long id) {
        return service.getProjectById(id);
    }

    
    
    
    
    
    @PutMapping("/{id}")
    public Project updateProject(@PathVariable Long id, @RequestBody Project payload) {
        return service.updateProject(id, payload);
    }

    
    
    
    
    
    @DeleteMapping("/{id}")
    public void deleteProject(@PathVariable Long id) {
        service.deleteProject(id);
    }

    
    
}