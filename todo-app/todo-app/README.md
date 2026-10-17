# To-Do App (Spring Boot + PostgreSQL)

A full-stack to-do app: REST API + a small web UI served by Spring Boot.
Open **http://localhost:8080** after starting the app.

## Run
```bash
docker compose up -d        # starts PostgreSQL on :5432
./mvnw spring-boot:run      # or: mvn clean spring-boot:run
```
Requires Java 17+. The `todos` table is created automatically on startup.
Override DB settings with env vars: `DB_URL`, `DB_USER`, `DB_PASSWORD`.

## Endpoints
| Method | Path                      | Description                          |
|--------|---------------------------|--------------------------------------|
| GET    | /api/todos                | List all (`?completed=true|false`)   |
| GET    | /api/todos/{id}           | Get one                              |
| POST   | /api/todos                | Create                               |
| PUT    | /api/todos/{id}           | Update                               |
| PATCH  | /api/todos/{id}/toggle    | Flip completed                       |
| DELETE | /api/todos/{id}           | Delete                               |

## Try it
```bash
curl -X POST localhost:8080/api/todos -H "Content-Type: application/json" \
  -d '{"title":"Write report","description":"Q4 numbers"}'
curl localhost:8080/api/todos
curl -X PATCH localhost:8080/api/todos/1/toggle
curl -X DELETE localhost:8080/api/todos/1
```
