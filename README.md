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
  | HTTPS API Request (/api/...)
  v
Netlify Edge Proxy
  |
  | HTTP (server-side)
  v
FastAPI API (AWS EC2 :8000)
  |
  v
PostgreSQL (Docker)
```

The React application calls the API at the relative path `/api`, which Netlify's edge proxies to the FastAPI backend on EC2. See [How the Frontend–Backend Connection Evolved](#-how-the-frontendbackend-connection-evolved).

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
REACT_APP_API_URL=/api
```

For why production uses a relative path proxied by Netlify rather than the EC2 address, see [How the Frontend–Backend Connection Evolved](#-how-the-frontendbackend-connection-evolved).

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

> Replace `<EC2_PUBLIC_IP>` with the current public IP of your EC2 instance. With an Elastic IP attached, the address is stable, so committing it in `frontend/public/_redirects` is safe. Without one, the address changes on every stop and start, and the proxy rule silently breaks.

---

## 🔐 AWS Security Group

The EC2 security group needs to allow the required inbound traffic.

Inbound rules:

| Protocol | Port | Purpose |
|---|---|---|
| SSH | 22 | Server administration |
| TCP | 8000 | FastAPI API — must be open to `0.0.0.0/0` for the Netlify proxy |

Port `8000` is open to `0.0.0.0/0` because the proxy requires it, not as a development shortcut: Netlify's edge connects inbound from a changing pool of addresses, so the port cannot be restricted by IP. See [What this approach gives up](#what-this-approach-gives-up) for the consequences.

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

The production frontend calls the backend through the relative path:

```
REACT_APP_API_URL=/api
```

`frontend/public/_redirects` wires the proxy: Netlify forwards `/api/*` to the EC2 backend at `http://<EC2_PUBLIC_IP>:8000`.

After the frontend is deployed, the user accesses the React application through the production Netlify URL:

**Live Application:** https://keepupinventory.netlify.app/

---

## 🧭 How the Frontend–Backend Connection Evolved

Connecting the Netlify frontend to the EC2 backend took four attempts. Each
failed for a different reason, and the reasons are the most useful part of this
project, so they are recorded here rather than quietly fixed. The final choice
is a deliberate trade-off rather than a strict improvement, and that trade-off is
stated plainly at the end.

### Attempt 1 — Point the frontend straight at the EC2 IP

```
REACT_APP_API_URL=http://<EC2_PUBLIC_IP>:8000
```

This is the obvious configuration, and it does not work.

The Netlify site is served over **HTTPS**. The EC2 backend speaks plain
**HTTP**. Browsers refuse to let a page loaded over HTTPS make requests to an
HTTP address — this is called **mixed content blocking**. The rule exists
because an attacker positioned on the network can read or alter an unencrypted
response, which would defeat the point of serving the page securely at all.

The failure is quiet and therefore confusing: the page itself loads normally, so
nothing looks broken. Only the API calls are blocked, so the UI renders with no
data. The real explanation appears only in the browser console, as a warning
about blocking insecure content.

The lesson: putting the frontend on HTTPS forces the backend to be reachable
over HTTPS too. That single constraint drove every later attempt.

### Attempt 2 — Put a Cloudflare quick tunnel in front of EC2

A Cloudflare **quick tunnel** gives a plain-HTTP service a public HTTPS address
with no account, no DNS record and no certificate setup:

```bash
cloudflared tunnel --url http://localhost:8000
```

It prints a randomly generated hostname, for example
`https://receptors-cathedral-statutes-penguin.trycloudflare.com`, which was then
set as the production API URL.

This worked, and it is worth being precise about how well, because the tunnel
has real security advantages that the final approach gives up.

`cloudflared` runs *on* the EC2 instance and opens an **outbound TLS connection**
to Cloudflare's edge. Traffic therefore travels like this:

```
Browser ──HTTPS──> Cloudflare edge ──TLS tunnel──> cloudflared ──> localhost:8000
```

Two consequences follow. First, the connection is encrypted the entire way: the
only unencrypted hop is `cloudflared` to `localhost:8000`, which stays inside the
machine and never touches a network. Second, because the tunnel is established
from the inside out, **inbound port 8000 can stay closed to the internet
entirely**. Nothing outside can reach the API except through Cloudflare.

The defect was narrower than it first appeared. A quick tunnel exists only as
long as its process runs, so an EC2 reboot, a crash, or Cloudflare retiring the
tunnel on its own schedule — quick tunnels are explicitly temporary — took the
address down with it.

### Attempt 3 — Run the tunnel as a systemd service

The obvious fix for a process that dies is to supervise it, so `cloudflared` was
installed as a **systemd** service to start on boot and restart on failure.

This solved the wrong half of the problem.

systemd kept the process alive reliably, but a quick tunnel is assigned a **new
random hostname every time it starts**. After a restart the service was running
and healthy, serving traffic at an address nothing pointed to. The hostname in
`.env.production` was now stale, and recovery meant finding the new one in the
service logs, editing the environment file, committing, and waiting for Netlify
to rebuild. The commit history shows the churn directly: two different
`trycloudflare.com` hostnames recorded a day apart.

A code change and a redeploy per server reboot is not a working deployment.

The important lesson is about diagnosis, not supervision. Process supervision was
never the missing piece — **hostname instability** was, and no amount of
restarting fixes that. The correct next step would have been a **named tunnel**:
the same architecture, but registered against a Cloudflare account so it keeps a
fixed hostname across restarts. That would have preserved both the end-to-end
encryption and the closed port while removing the churn.

### Attempt 4 — Proxy the API through Netlify (current approach)

The approach actually adopted removes the tunnel instead.

Netlify can act as a **reverse proxy**. A rule in `frontend/public/_redirects`
forwards any request under `/api/` to the EC2 backend:

```
/api/*  http://<EC2_PUBLIC_IP>:8000/:splat  200
```

and the frontend asks for a relative path rather than an absolute address:

```
REACT_APP_API_URL=/api
```

The status code `200` is what makes this a proxy rather than a redirect. A `301`
or `302` would tell the *browser* to go to the HTTP address itself, re-triggering
mixed content blocking. With `200`, Netlify fetches the response server-side and
returns it as its own.

The request path becomes:

```
Browser ──HTTPS──> Netlify edge ──HTTP──> EC2 (FastAPI :8000)
```

The browser only ever talks to Netlify, over HTTPS, so mixed content blocking
never applies. The plain-HTTP hop happens between Netlify's servers and EC2,
where no browser is involved and therefore no browser policy applies.

Its advantage is singular and real: **nothing extra runs.** There is no tunnel
process, no service to supervise, no daemon to update, and no hostname to
rediscover. The rule is part of the deployed site and is enforced by Netlify's
edge indefinitely.

### What this approach gives up

Choosing the proxy over a named tunnel trades two security properties for that
simplicity. Both are stated here rather than omitted, because the comparison is
the honest result of the exercise.

**The final hop is unencrypted.** Netlify's edge reaches EC2 over plain HTTP, so
that segment crosses the public internet in cleartext. A named tunnel encrypts
the whole path.

**Port 8000 must be open to the world.** Netlify's edge has to connect *inbound*
to EC2, and Netlify runs from a large, changing pool of addresses with no fixed
range to whitelist. The security group therefore has to allow `0.0.0.0/0` on
port 8000. The practical consequence: anyone who knows the instance's address can
query `http://<EC2_PUBLIC_IP>:8000/products` directly and bypass the site
entirely. A tunnel needs no inbound port at all, because the connection is
established outbound from the instance.

| | Named Cloudflare tunnel | Netlify `_redirects` proxy |
|---|---|---|
| Encrypted to the backend | Yes, end to end | No — final hop is plain HTTP |
| Inbound port 8000 exposed | No, stays closed | Yes, to `0.0.0.0/0` |
| Stable address | Yes, fixed hostname | Yes, via Elastic IP |
| Processes to maintain | One daemon | None |
| Own domain required | No | No |

**Why the proxy is nevertheless the right choice here.** This application serves
non-sensitive inventory records with no authentication and no personal data. The
same records are readable through the public site, so an open port 8000 exposes
nothing that is not already public, and an unencrypted hop carries nothing worth
intercepting. Against that, removing a long-running daemon removes the component
that actually failed twice.

Were this handling real user data, the conclusion would reverse — and the proper
answer would not be either option above. It would be **TLS on the backend
itself**: a domain name with Caddy or nginx terminating HTTPS in front of
FastAPI using a Let's Encrypt certificate. The frontend would then call
`https://api.<domain>` directly, the whole path would be encrypted, port 8000
would close to the public, and nothing would be proxied or tunnelled. That is
the correct production shape, and it is what a fifth attempt would build.

### A required prerequisite: an Elastic IP

The proxy rule has the EC2 address written into it. By default an EC2 instance
receives a new public IP every time it is stopped and started, which would
silently break the rule in exactly the way the tunnel's changing hostname did.

Attaching an **Elastic IP** reserves a fixed address for the account and pins it
to the instance across stops, starts and reboots. It is free while associated
with a running instance. Without one, attempt 4 inherits attempt 3's failure
mode in a different file.

### Summary

| Attempt | Approach | Outcome |
|---|---|---|
| 1 | Direct `http://` to EC2 | Failed — mixed content blocking; an HTTPS page cannot call an HTTP API |
| 2 | Cloudflare quick tunnel | Worked, but the tunnel dies with its process |
| 3 | Quick tunnel under systemd | Process survived; the hostname changed on every restart |
| 4 | Netlify `_redirects` proxy | **Current** — no process to maintain, at the cost of an open port and an unencrypted final hop |
| — | Named tunnel, or TLS on the backend | The two correct answers if security mattered more than simplicity |

The throughline: the problem was never a component that kept crashing. It was
that the backend's public address kept changing. Attempts 2 and 3 tried to keep a
moving address alive; attempt 4 removes the need for a second address at all, by
routing through one that was already stable — and pays for that simplicity in
exposure.

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
       Netlify Edge ---- HTTP ----->+
              ^       (/api proxy)
              |
              | HTTPS
              |
           Browser
```

The deployed architecture separates the frontend and backend:

- **Frontend:** React application hosted on **Netlify**
- **Backend:** FastAPI application running in a Docker container on **AWS EC2**
- **Database:** PostgreSQL running in Docker on the EC2 server
- **Communication:** the browser calls `/api` on Netlify over HTTPS, and Netlify's edge proxies it to FastAPI on EC2 over HTTP (see [How the Frontend–Backend Connection Evolved](#-how-the-frontendbackend-connection-evolved))

A typical user request looks like:

```
Browser
   |
   v
React App on Netlify
   |
   | GET /api/products (HTTPS)
   v
Netlify Edge Proxy
   |
   | GET /products (HTTP)
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

### Mixed Content Error

If API calls fail on the live site and the browser console reports blocked insecure content, `REACT_APP_API_URL` is set to an absolute `http://` address instead of `/api`.

See [How the Frontend–Backend Connection Evolved](#-how-the-frontendbackend-connection-evolved) for details.

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
