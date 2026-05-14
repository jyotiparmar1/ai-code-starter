package com.example.demo.service;

import java.util.List;
import org.springframework.stereotype.Service;
import com.example.demo.entity.Project;
import com.example.demo.repository.ProjectRepository;

@Service
public class ProjectService {

    private final ProjectRepository repository;

    public ProjectService(ProjectRepository repository) {
        this.repository = repository;
    }

    
    public Project createProject(Project payload) {
        
        return repository.save(payload);
        
    }

    
    public List<Project> getAllProjects() {
        
        return repository.findAll();
        
    }

    
    public Project getProjectById(Long id) {
        
        return repository.findById(id).orElse(null);
        
    }

    
    public Project updateProject(Long id, Project payload) {
        
        payload.setId(id);
        return repository.save(payload);
        
    }

    
    public void deleteProject(Long id) {
        
        repository.deleteById(id);
        
    }

    
}