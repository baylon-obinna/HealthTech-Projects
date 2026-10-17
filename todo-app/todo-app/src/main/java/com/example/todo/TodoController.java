package com.example.todo;

import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@RestController
@RequestMapping("/api/todos")
public class TodoController {

    private final TodoRepository repository;

    public TodoController(TodoRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public List<Todo> list(@RequestParam(required = false) Boolean completed) {
        return completed == null ? repository.findAll() : repository.findByCompleted(completed);
    }

    @GetMapping("/{id}")
    public Todo get(@PathVariable Long id) {
        return find(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Todo create(@Valid @RequestBody Todo todo) {
        return repository.save(todo);
    }

    @PutMapping("/{id}")
    public Todo update(@PathVariable Long id, @Valid @RequestBody Todo input) {
        Todo todo = find(id);
        todo.setTitle(input.getTitle());
        todo.setDescription(input.getDescription());
        todo.setCompleted(input.isCompleted());
        return repository.save(todo);
    }

    @PatchMapping("/{id}/toggle")
    public Todo toggle(@PathVariable Long id) {
        Todo todo = find(id);
        todo.setCompleted(!todo.isCompleted());
        return repository.save(todo);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        repository.delete(find(id));
    }

    private Todo find(Long id) {
        return repository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Todo " + id + " not found"));
    }
}
