# KeepUp Inventory Management System

A full-stack CRUD application built with **React**, **FastAPI**, and **PostgreSQL**, containerized with **Docker**, deployed on **AWS EC2** through a **GitHub Actions** CD pipeline, and hosted with the React frontend on **Netlify**.

### 🌐 Live Demo

**Frontend:** https://keepupinventory.netlify.app/

This project was built primarily to understand and demonstrate practical **Docker, container networking, cloud deployment, environment variables, and frontend/backend deployment**.

---

## 🚀 Project Overview

The application provides a simple interface for managing product inventory:

- Create a product
- View all products
- View a product by ID
- Update a product
- Delete a product

### Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Containerization | Docker + Docker Compose |
| Backend Hosting | AWS EC2 |
| Frontend Hosting | Netlify |
| Version Control | Git + GitHub |
| CI/CD | GitHub Actions (backend), Netlify auto-deploy (frontend) |

---

## 🏗️ Architecture

```
                         Internet
                            |
                 +----------+----------+
                 |                     |
                 v                     v
          Netlify (React)       AWS EC2 Server
                                      |
                                      v
                              FastAPI Container
                                      |
                                      v
                             PostgreSQL Container
```

### Request Flow

```
User
  |
  v
React Frontend (Netlify)
  |
  | HTTP API Request
  v
FastAPI API (AWS EC2 :8000)
  |
  v
PostgreSQL (Docker)
```

The React application communicates with the FastAPI backend through the backend's API URL.

Inside Docker Compose, FastAPI communicates with PostgreSQL using the PostgreSQL service name (`postgres-db`) rather than `localhost`.

---

## 📁 Project Structure

```
project-root/
│
├── .github/
│   └── workflows/
│       └── deploy.yml
│
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   └── ...
│   ├── public/
│   ├── package.json
│   ├── .env.development
│   ├── .env.production
│   └── ...
│
├── main.py
├── database.py
├── database_module.py
├── module.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Backend

The backend is implemented using FastAPI.

Example API endpoints:

```
GET    /products
POST   /products
GET    /products/{id}
PUT    /products/{id}
DELETE /products/{id}
```

FastAPI provides the REST API, while SQLAlchemy is used to interact with PostgreSQL.

---

## 🗄️ Database

The project uses PostgreSQL.

When running locally without Docker, the database can be accessed through `localhost`.

When FastAPI and PostgreSQL are running in Docker Compose, the backend connects to PostgreSQL through the Docker Compose service name:

```
postgres-db
```

Example Docker database URL:

```
postgresql://postgres:<PASSWORD>@postgres-db:5432/postgres
```

The application reads the database connection string from an environment variable:

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL")
```

This keeps database configuration outside the application code.

---

## 🐳 Docker

The backend and PostgreSQL database are containerized.

### Build and start the application

```bash
docker compose up --build
```

### Start existing images

```bash
docker compose up -d
```

### Check running containers

```bash
docker ps
```

### Stop the containers

```bash
docker compose down
```

### View logs

```bash
docker compose logs
```

For the FastAPI service:

```bash
docker compose logs fastapi
```

---

## 🔌 Docker Networking

One important Docker concept used in this project is **service-to-service communication**.

The FastAPI container does **not** use `localhost` to reach PostgreSQL.

Instead, Docker Compose provides internal DNS, so the PostgreSQL service can be reached using `postgres-db`:

```
FastAPI Container
       |
       | DATABASE_URL
       v
postgres-db:5432
```

This is different from accessing PostgreSQL from the host machine, where `localhost:5432` may be used.

---

## 💻 Running Locally

### 1. Start PostgreSQL and FastAPI

From the project root:

```bash
docker compose up --build
```

The FastAPI API is available at: `http://localhost:8000`

FastAPI's interactive API documentation is available at: `http://localhost:8000/docs`

### 2. Start the React frontend

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm start
```

If port `3000` is already occupied, React can run on another port such as `http://localhost:3001`.

---

## 🌐 Frontend Environment Variables

The frontend uses an environment variable to determine where the backend API is hosted.

### Development

`.env.development`

```
REACT_APP_API_URL=http://127.0.0.1:8000
```

### Production

`.env.production`

```
REACT_APP_API_URL=http://<EC2_PUBLIC_IP>:8000
```

The React application accesses it using:

```javascript
process.env.REACT_APP_API_URL
```

This allows the same frontend codebase to communicate with different backend environments.

---

## ☁️ AWS EC2 Deployment

The FastAPI backend was deployed to an **AWS EC2** instance.

The deployment flow was:

```
Local Project
     |
     v
GitHub
     |
     v
AWS EC2
     |
     v
Docker
     |
     +------ FastAPI Container
     |
     +------ PostgreSQL Container
```

### EC2 Setup

The EC2 server runs Docker and Docker Compose.

After connecting to the server:

```bash
docker ps
```

The FastAPI application is exposed on port `8000`.

The API can then be accessed through the EC2 public IP:

```
http://<EC2_PUBLIC_IP>:8000
```

FastAPI documentation:

```
http://<EC2_PUBLIC_IP>:8000/docs
```

> Replace `<EC2_PUBLIC_IP>` with the current public IP of your EC2 instance. Avoid committing a changing EC2 IP directly into source code.

---

## 🔐 AWS Security Group

The EC2 security group needs to allow the required inbound traffic.

Typical development configuration:

| Protocol | Port | Purpose |
|---|---|---|
| SSH | 22 | Server administration |
| TCP | 8000 | FastAPI API |

For a production deployment, access rules should be restricted appropriately rather than exposing development ports publicly.

---

## 🌍 Netlify Frontend Deployment

The React frontend was deployed using **Netlify**.

Netlify configuration:

| Setting | Value |
|---|---|
| Branch | `main` |
| Base directory | `frontend` |
| Build command | `npm run build` |
| Publish directory | `build` |

The production frontend uses the EC2 backend URL through:

```
REACT_APP_API_URL=http://<EC2_PUBLIC_IP>:8000
```

After the frontend is deployed, the user accesses the React application through the production Netlify URL:

**Live Application:** https://keepupinventory.netlify.app/

---

## 🔄 Complete Deployment Flow

```
                 GitHub Repository
                         |
              +----------+----------+
              |                     |
              v                     v
          Netlify                 AWS EC2
        React Build             Docker Compose
              |                     |
              |                     +--> FastAPI
              |                     |
              |                     +--> PostgreSQL
              |                     |
              +-------- HTTP -------+
```

The deployed architecture separates the frontend and backend:

- **Frontend:** React application hosted on **Netlify**
- **Backend:** FastAPI application running in a Docker container on **AWS EC2**
- **Database:** PostgreSQL running in Docker on the EC2 server
- **Communication:** React frontend communicates with the FastAPI backend over HTTP

A typical user request looks like:

```
Browser
   |
   v
React App on Netlify
   |
   | GET /products
   v
FastAPI on EC2
   |
   v
PostgreSQL Container
   |
   v
Products Data
   |
   v
FastAPI Response
   |
   v
React UI
```

---

## 🔁 CI/CD Pipeline

Deployments are automated, so no manual steps on the server are needed after a push.

| Part | Tool | Trigger |
|---|---|---|
| Backend | GitHub Actions workflow: **Deploy to EC2** | Push to `main` |
| Frontend | Netlify continuous deployment | Push to `main` |

```
Developer pushes to main
          |
          +----------------------------+
          |                            |
          v                            v
  GitHub Actions                   Netlify
  "Deploy to EC2"              builds React app
          |                            |
          v                            v
  AWS EC2 (Docker Compose)      Live frontend updated
  FastAPI + PostgreSQL
```

The workflow is defined in `.github/workflows/`, and run history is visible in the repository's **Actions** tab.

---

## 🧪 Testing the Backend

You can verify that FastAPI is running with:

```bash
curl http://localhost:8000/products
```

You can also open `/docs` to use FastAPI's Swagger UI and test the API interactively.

---

## 🛠️ Troubleshooting

### CORS Error

If the React frontend is running on a different origin, FastAPI needs to allow the frontend origin.

For example:

```
Frontend: http://localhost:3001
Backend:  http://localhost:8000
```

These are different origins, so CORS must be configured appropriately in FastAPI.

### PostgreSQL Connection Error

Inside Docker, make sure the database hostname is `postgres-db` and not `localhost`.

For example:

```
DATABASE_URL=postgresql://postgres:<PASSWORD>@postgres-db:5432/postgres
```

### Port Already in Use

If port `3000` is already occupied, React may ask to use another port such as `3001`.

For FastAPI, check whether port `8000` is already being used:

```bash
docker ps
```

---

## 📌 Key Concepts Demonstrated

This project demonstrates practical experience with:

- React frontend development
- REST API development with FastAPI
- PostgreSQL database integration
- SQLAlchemy
- CRUD operations
- Environment variables
- CORS
- Dockerfiles
- Docker Compose
- Docker networking
- Containerized PostgreSQL
- AWS EC2 deployment
- Linux server basics
- Netlify frontend deployment
- Git/GitHub-based workflow
- CI/CD with GitHub Actions
- Debugging deployed applications

---

## 🎯 Learning Objective

The main goal of this project was not to build a complex business application, but to understand how a modern application moves from local development to a cloud-hosted environment.

The progression was:

```
Application Development
        ↓
React + FastAPI + PostgreSQL
        ↓
Docker
        ↓
Docker Compose
        ↓
AWS EC2
        ↓
Netlify
        ↓
CI/CD with GitHub Actions
        ↓
Deployed Full-Stack Application
```

This provides a foundation for adding more advanced DevOps practices later, such as automated tests in the pipeline, container registries, infrastructure as code, monitoring, and Kubernetes.
