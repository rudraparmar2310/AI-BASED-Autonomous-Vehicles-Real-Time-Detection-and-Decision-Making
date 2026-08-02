# 🚀 Autopilot AI: Production-Grade Faster R-CNN Autonomous Driving Perception Stack

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112+-green.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.5.1%2BCU121-red.svg)](https://pytorch.org/)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-orange.svg)](https://developer.nvidia.com/cuda-toolkit)
[![CARLA](https://img.shields.io/badge/CARLA-0.9.16-red.svg)](https://carla.org/)
[![React](https://img.shields.io/badge/React-18.0-cyan.svg)](https://react.dev/)

A production-ready, high-throughput autonomous vehicle perception pipeline. It replaces basic object detection with a highly optimized, GPU-accelerated, async **Faster R-CNN** detector, constant-velocity trajectory tracker, stable bounding box renderer, and real-time telemetry metrics dashboard integrated with the **CARLA Simulator**.

---

## 🎯 System Highlights & Capabilities

- **GPU-Accelerated Two-Stage Inference**: Runs torchvision's `fasterrcnn_resnet50_fpn_v2` with FPN and RoIAlign, optimized for high accuracy on autonomous driving classes.
- **Mixed-Precision & Tensor Optimizations**: Leverages FP16 mixed-precision autocasting and cuDNN autotuning to achieve a **20.4 FPS** raw model execution speed on mobile GPUs.
- **Intelligent Frame Processing (58 FPS Throughput)**: Performs deep neural inference on every 3rd frame, and extrapolates trajectories using a constant-velocity vector model on intermediate frames (<1ms overhead).
- **GPU-Based Non-Maximum Suppression (NMS)**: Applies strict confidence thresholding (0.70) and class-agnostic NMS (IoU 0.40) directly in GPU VRAM to prevent PCI-e bus bottlenecks and overlapping boxes.
- **Flicker-Free Visualization**: Features bounding box smoothing using exponential moving averages (EMA), motion trails, and traffic banners (STOP, SLOW, GO).
- **Rich Telemetry Monitoring**: Feeds real-time system stats (CPU%, GPU%, VRAM MB, Latency, Model FPS, and Throughput FPS) directly to a React dashboard.
- **CARLA v0.9.16 Integration**: Integrates directly with the CARLA simulation client to orchestrate autopilot vehicle controls and map sensor data.

---

## 🏗️ Architecture Design

```
                     ┌──────────────────────────────────────────────┐
                     │            React Web Dashboard               │
                     │          (localhost:8080 / Vite)             │
                     └──────────────────────┬───────────────────────┘
                                            │ Websocket Stream &
                                            │ Telemetry Metrics
                     ┌──────────────────────▼───────────────────────┐
                     │            FastAPI Server (ASGI)             │
                     │            (localhost:8000 / Uvicorn)        │
                     └──────────────────────┬───────────────────────┘
                                            │
                             ┌──────────────┴──────────────┐
                             │                             │
                ┌────────────▼────────────┐   ┌────────────▼────────────┐
                │     CARLA Simulator     │   │      PyTorch Engine     │
                │    (TCP Port 2000)      │   │   ✓ FP16  ✓ GPU-NMS     │
                └─────────────────────────┘   └─────────────────────────┘
```

1. **Ingestion Layer**: Camera frames are captured at 25 FPS from the client webcam, video uploads, or a CARLA RGB camera sensor.
2. **FastAPI Gateway**: Routes frames into a single-element queue (`maxsize=1`) using non-blocking asynchronous WebSocket channels (`sync=False`).
3. **PyTorch Inference Thread**: Resolves incoming frames, transfers them to CUDA tensors, executes convolution algorithms, and runs NMS.
4. **Tracking & Decision Engine**: Feeds bounding boxes to a Centroid Tracker. The decision layer evaluates line crossings and calculates safety distances, updating vehicle actuators in CARLA.
5. **HUD Render & Stream**: Applies stable visualizations, overlays telemetry data on the frame, and returns a Base64-encoded package to the client.

---

## 📋 System Requirements & Benchmarks

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10/11 or Ubuntu 20.04/22.04 |
| **Python** | 3.12 |
| **GPU** | NVIDIA GeForce RTX 3050 Laptop GPU or higher (CUDA 12.1 compatible) |
| **RAM** | 16GB+ |
| **CARLA** | Version 0.9.16 |

### Performance Metrics (RTX 3050)
*   **Raw Model Inference Latency**: `49.04 ms` (~20.4 FPS)
*   **Constant-Velocity Frame Extrapolation Latency**: `< 1.0 ms`
*   **Total Pipeline Processing Latency (Average)**: `17.1 ms` (~58.5 FPS throughput)
*   **GPU Memory footprint (VRAM)**: `~179 MB` allocated

---

## 🚀 Installation & Setup

### 1️⃣ Download & Setup CARLA
Download and extract the CARLA 0.9.16 simulator:
*   [CARLA 0.9.16 Release Page](https://github.com/carla-simulator/carla/releases/tag/0.9.16)
*   Set your installation path environment variable in your terminal:
    ```powershell
    # Windows
    $env:CARLA_PATH="C:\Users\Acer\CARLA_0.9.16"
    ```

### 2️⃣ Clone and Initialize the Backend
Create your virtual environment and install the optimized machine learning dependencies:
```bash
# Clone the repository
git clone https://github.com/username/autopilot-ai.git
cd autopilot-ai/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install sequential packages (resolves temp drive limits)
pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121
pip install -r requirements-backend.txt
```

### 3️⃣ Configure Environment Variables
Copy and configure the environment variables file (`backend/.env`):
```bash
# CARLA Simulator
CARLA_HOST=localhost
CARLA_PORT=2000

# Faster R-CNN Model
FRCNN_MODEL=fasterrcnn_resnet50_fpn_v2
FRCNN_CONFIDENCE=0.70
FRCNN_IOU=0.45
FRCNN_DEVICE=cuda
```

---

## ⚙️ Running the System

### 1. Launch the FastAPI Backend
Start the server in the backend directory:
```bash
cd backend
python main.py
```
*The API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).*

### 2. Launch the Vite React Frontend
Start the frontend development server in the root workspace directory:
```bash
# Install Node dependencies
npm install

# Start Vite
npm run dev
```
*The web interface will be available at [http://localhost:8080/](http://localhost:8080/).*

### 3. Run Autopilot Integration Tests
Validate the ML inference stack and GPU configurations:
```bash
cd backend
python test_fasterrcnn.py
```

---

## 📁 Repository Structure

```
autopilot-ai/
├── backend/                       # Python FastAPI Backend
│   ├── main.py                    # API Gateway & WebSocket endpoints
│   ├── config.py                  # Global configurations and directories
│   ├── fasterrcnn_detector.py     # Faster R-CNN PyTorch class
│   ├── tracker.py                 # Centroid Tracker & Line crossing logic
│   ├── stable_renderer.py         # Advanced BBox overlays & HUD renderer
│   ├── frame_optimizer.py         # Temporal smoothing utilities
│   ├── pygame_autopilot.py        # Interactive CARLA autopilot vehicle driver
│   └── test_fasterrcnn.py         # Unit tests and model benchmark script
├── src/                           # React Frontend Client
│   ├── components/                # Reusable dashboard widgets
│   ├── pages/                     # Routed views (AiDetectionPage.tsx)
│   └── main.tsx                   # Client entry point
├── package.json                   # NPM configuration and dependencies
└── tsconfig.app.json              # TypeScript rules
```

---

## ⚡ API Examples

### Stream Real-Time Detections
Connect to the full-duplex WebSocket:
```
ws://localhost:8000/ws/ai-camera
```

**Payload Sent by Client (JSON)**:
```json
{
  "frame": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDA..."
}
```

**Payload Returned by Server (JSON)**:
```json
{
  "frame": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDA...",
  "objects": 2,
  "fps": 58.5,
  "detection_fps": 20.4,
  "inference_latency": 49.0,
  "cpu_utilization": 12.0,
  "gpu_utilization": 38.0,
  "vram_allocated_mb": 179.0,
  "action": "GO",
  "reason": "Road clear",
  "detections": [
    { "id": 1, "class": "car", "confidence": 0.94 },
    { "id": 2, "class": "person", "confidence": 0.81 }
  ]
}
```

---

## 🛠️ Tech Stack Summary

*   **Frontend**: React, TypeScript, TailwindCSS, Vite, Lucide Icons, Shadcn/ui.
*   **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic, psutil.
*   **Machine Learning / AI**: PyTorch, Torchvision (`fasterrcnn_resnet50_fpn_v2`), CUDA Toolkit, Mixed Precision (FP16).
*   **Computer Vision**: OpenCV (`cv2`), Hungarian Centroid Tracking, IoU calculations, GPU-based NMS.
*   **Simulation**: CARLA Simulator v0.9.16, CARLA Client Python API.
*   **Dev Tools**: Vitest, ESLint, Python standard unittest.
*   **Deployment**: Docker, Docker Compose, Powershell/Batch setups.

---

## 🤝 Contributing
1. Fork the Repository.
2. Create your Feature Branch: `git checkout -b feature/amazing-feature`.
3. Commit your Changes: `git commit -m 'Add amazing feature'`.
4. Push to the Branch: `git push origin feature/amazing-feature`.
5. Open a Pull Request.

---

## 📄 License
This project combines multiple open-source components:
*   **CARLA Simulator**: NCSA License
*   **Faster R-CNN Models (Torchvision)**: BSD 3-Clause License
*   **This Project**: MIT License
[README.md](https://github.com/user-attachments/files/30629874/README.md)
