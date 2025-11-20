
# HW 2 Docker&PG

## Docker hub link       
https://hub.docker.com/repositories/rsnhk

## Structure

- `db/` – контейнер с PostgreSQL
- `app/` – Python + Flask, точка входа

## How it starts 

```docker compose build -up```

## How it works 

```
curl http://localhost:8000/
curl http://localhost:8000/items
```