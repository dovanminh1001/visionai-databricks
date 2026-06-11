<p align="center">
  <img src="docs/images/banner.png" alt="VisionAI Banner" width="100%"/>
</p>

<p align="center">
  <strong>🌐 Full-Stack AI Web Application — Real-time Object Detection, Face Recognition & Analytics</strong>
</p>

<p align="center">
  <a href="https://github.com/dovanminh1001/visionai-databricks/actions"><img src="https://github.com/dovanminh1001/visionai-databricks/actions/workflows/ci.yml/badge.svg" alt="CI/CD"></a>
  <img src="https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.3-green?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/YOLOv8-Ultralytics-purple?logo=yolo&logoColor=white" alt="YOLOv8">
  <img src="https://img.shields.io/badge/Docker-Containerized-blue?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-api-endpoints">API</a> •
  <a href="#-deployment">Deployment</a>
</p>

---

> 📌 **This is the `web-app-deploy` branch** containing the Flask web application.
> For the Data Pipeline & Medallion Architecture, see the [`main` branch](https://github.com/dovanminh1001/visionai-databricks/tree/main).

---

## ✨ Features

| Feature | Description | AI Model |
|---------|-------------|----------|
| 🎯 **Object Detection** | Detect 80+ objects in real-time via webcam or image upload | YOLOv8 Nano |
| 👤 **Face Recognition** | Register & identify faces with confidence scoring | Haar Cascade + Template Matching |
| 🎨 **Color Analysis** | Extract 5 dominant colors (HEX/RGB) from any image | K-Means Clustering (k=5) |
| 📊 **Classification** | Classify objects with bilingual labels (EN/VI) | YOLOv8 + Custom Label Map |
| 😀 **Emotion Detection** | Detect facial emotions from camera or uploads | OpenCV Cascade |
| 📈 **Dashboard** | Real-time statistics, charts & top detected objects | SQLAlchemy + Jinja2 |
| 📜 **History** | Paginated detection history with detail view & CSV export | Flask Pagination |
| 👥 **Admin Panel** | User management, role control, activity monitoring | Flask-Login + RBAC |
| 🔄 **Cloud Sync** | Auto-sync images to Hugging Face & trigger Databricks pipeline | Background Threads |

---

## 🏗 Architecture

<p align="center">
  <img src="docs/images/architecture.png" alt="System Architecture" width="90%"/>
</p>

```mermaid
graph TB
    subgraph Client["🖥️ Browser"]
        A[Camera / Upload]
    end

    subgraph App["🐳 Docker Container"]
        B[Flask + Gunicorn]
        C[YOLOv8 Engine]
        D[OpenCV Engine]
    end

    subgraph Storage["☁️ Cloud Storage"]
        E[(Databricks Unity Catalog)]
        F[🤗 Hugging Face Dataset]
    end

    subgraph Pipeline["📊 Data Pipeline"]
        G[Bronze → Silver → Gold]
        H[Databricks Dashboard]
    end

    A -->|HTTP/WebSocket| B
    B --> C
    B --> D
    B -->|SQLAlchemy ORM| E
    B -->|Async Upload| F
    E --> G
    G --> H
```

---

## 📸 Screen Demos & Platform Integration

Here are some screenshots demonstrating the frontend web application and the Databricks Lakehouse data engineering backend:

### 1. Web Application - Dashboard Overview
The main dashboard provides real-time statistics of total detections, quick shortcuts to all 5 AI features, recent activity stream, and connection status.
<p align="center">
  <img src="docs/images/dashboard_overview.png" alt="Dashboard Overview" width="90%"/>
</p>

### 2. Web Application - Activity Log & Admin Panel
The admin area provides user management and a comprehensive detection log. Admins can view detailed parameters of each detection, download CSV records, and manage account details.
<p align="center">
  <img src="docs/images/activity_log.png" alt="Activity Log & Admin Panel" width="90%"/>
</p>

### 3. Databricks - Unity Catalog (Bronze Layer)
Detection events and metadata are sent directly to the Databricks Unity Catalog (`bronze.raw_detections`), providing a centralized, secure, and governed audit trail.
<p align="center">
  <img src="docs/images/databricks_catalog.png" alt="Databricks Unity Catalog" width="90%"/>
</p>

### 4. Databricks - Workflow Jobs & Pipelines
Automated jobs manage the pipeline lifecycle on Databricks: scheduling ingestion (every 15 min), system monitoring analytics updates (every hour), and daily machine learning model evaluation runs.
<p align="center">
  <img src="docs/images/databricks_jobs.png" alt="Databricks Workflow Jobs" width="90%"/>
</p>

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Databricks workspace (for database backend)

### Installation

```bash
# 1. Clone & checkout this branch
git clone https://github.com/dovanminh1001/visionai-databricks.git
cd visionai-databricks
git checkout web-app-deploy

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Databricks DATABASE_URL

# 5. Run the application
python run.py
# Visit http://localhost:5000
```

### Docker Deployment

```bash
# Development (Flask + PostgreSQL)
docker-compose -f docker/docker-compose.yml up -d

# Production (Flask x2 replicas + PostgreSQL + Nginx SSL)
docker-compose -f docker/docker-compose.production.yml up -d
```

---

## 📁 Project Structure

```
visionai_app/
├── app/
│   ├── __init__.py              # Flask App Factory + Blueprint registration
│   ├── models/
│   │   ├── user.py              # User model (bcrypt auth, RBAC)
│   │   └── detection.py         # Detection model (JSON fields, timestamps)
│   ├── views/
│   │   ├── auth.py              # Login, Register, Logout
│   │   ├── main.py              # Dashboard, History, Admin, CSV Export
│   │   ├── detection.py         # YOLOv8 Object Detection (upload + camera)
│   │   ├── face_detection.py    # Face Recognition (register, detect, manage)
│   │   ├── color_detection.py   # K-Means Color Analysis
│   │   └── classification.py   # Object Classification
│   ├── services/
│   │   ├── db_service.py        # Centralized DB writes + HF upload + Pipeline sync
│   │   └── classification_service.py
│   ├── templates/               # Jinja2 HTML templates (Tailwind CSS)
│   └── static/                  # CSS, JavaScript, images
├── config/
│   └── config.py                # App config, bilingual labels (80+ objects)
├── docker/
│   ├── Dockerfile               # Dev Docker image
│   ├── Dockerfile.production    # Production image (CPU-optimized PyTorch)
│   ├── docker-compose.yml       # Dev: Flask + PostgreSQL
│   ├── docker-compose.production.yml  # Prod: Flask x2 + PG + Nginx
│   └── nginx.conf               # Reverse proxy + SSL config
├── scripts/
│   ├── deploy.sh                # Local production deploy
│   ├── deploy-gcp.sh            # Google Cloud Run deploy
│   ├── deploy-aws.sh            # AWS ECS deploy
│   ├── deploy-azure.sh          # Azure ACI deploy
│   └── quick-deploy.sh          # Interactive deploy menu
├── Dockerfile                   # Production Dockerfile (Render-ready)
├── requirements.txt             # Python dependencies
├── yolov8n.pt                   # YOLOv8 Nano model weights (~6.2 MB)
└── run.py                       # Application entrypoint
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/login` | User login |
| `POST` | `/auth/register` | User registration |
| `GET` | `/auth/logout` | User logout |

### Detection
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/detection/detect_image` | Detect objects in uploaded image |
| `POST` | `/detection/detect_camera` | Detect objects from camera frame |
| `POST` | `/face-detection/detect-upload` | Detect & recognize faces |
| `POST` | `/color-detection/detect` | Analyze dominant colors |
| `POST` | `/classification/classify_upload` | Classify objects in image |

### Data Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/recent-detections` | Get recent detections (JSON) |
| `GET` | `/api/export-detections` | Export all history as CSV |
| `DELETE` | `/api/delete-detection/<id>` | Delete a detection record |

---

## 🐳 Docker Services

### Development (2 services)
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `web` | Custom Flask | 5000 | AI web application |
| `db` | PostgreSQL 13 | 5432 | Local database |

### Production (3 services)
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `web` x2 | Custom Flask | internal | Flask with Gunicorn (2 replicas) |
| `db` | PostgreSQL 13 | internal | Production database |
| `nginx` | nginx:alpine | 80, 443 | Reverse proxy, SSL, load balancing |

---

## ⚙️ Configuration

```env
# Required
DATABASE_URL=databricks://token:YOUR_TOKEN@YOUR_HOST...
SECRET_KEY=your-secret-key-here

# Optional
HF_TOKEN=your-huggingface-token        # For cloud image backup
YOLO_MODEL_PATH=yolov8n.pt             # Model file path
FLASK_ENV=production                    # production or development
TZ=Asia/Ho_Chi_Minh                    # Timezone
```

---

## 🛠 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.11, Flask 2.3, SQLAlchemy, Gunicorn |
| **Frontend** | HTML5, Tailwind CSS, JavaScript (Vanilla) |
| **AI/ML** | YOLOv8 (Ultralytics), OpenCV, PyTorch (CPU) |
| **Database** | Databricks Unity Catalog (prod), PostgreSQL (dev) |
| **Auth** | Flask-Login, bcrypt, Role-Based Access Control |
| **Storage** | Hugging Face Datasets, Local filesystem |
| **Deploy** | Docker, Docker Compose, Nginx, Render |
| **CI/CD** | GitHub Actions (PyTest + Databricks Bundle) |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/dovanminh1001">dovanminh1001</a></sub>
</p>
