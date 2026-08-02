[Uploading README.md# 🚀 Autopilot AI: Professional YOLOv8 Autonomous Driving Perception Stack & Desktop UI

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112+-green.svg)](https://fastapi.tiangolo.com/)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-orange.svg)](https://github.com/tomschimansky/CustomTkinter)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.5.1%2BCU121-red.svg)](https://pytorch.org/)
[![YOLOv8](https://img.shields.io/badge/Ultralytics-YOLOv8-blueviolet.svg)](https://docs.ultralytics.com/)
[![CUDA](https://img.shields.io/badge/CUDA-12.1-orange.svg)](https://developer.nvidia.com/cuda-toolkit)
[![CARLA](https://img.shields.io/badge/CARLA-0.9.16-red.svg)](https://carla.org/)
[![React](https://img.shields.io/badge/React-18.0-cyan.svg)](https://react.dev/)

A production-ready, ultra-stable autonomous vehicle perception pipeline. It replaces sluggish two-stage detection with a highly optimized, GPU-accelerated **YOLOv8** pipeline, a hybrid **Intersection-over-Union (IoU)** tracker, and an interactive **CustomTkinter Desktop Dashboard** + **FastAPI/React web interfaces** integrated with the **CARLA Simulator**.

---

## 🎯 Key Capabilities & Highlights

### ⚡ YOLOv8 Model Upgrades & Benchmarks
- **Lightning Inference**: Swapped Faster R-CNN for YOLOv8 (`yolov8n.pt`), dropping latency from `49.2 ms` to **`6.7 ms`** (an **86% speedup**).
- **147+ Throughput FPS**: Processes every camera frame in real-time on GPU, eliminating frame-skipping interpolation lag.
- **Low Footprint**: Saves 75% GPU memory, allocating only **`44 MB`** of VRAM on CUDA.
- **Built-in GPU NMS**: Computes class-agnostic NMS directly in VRAM, eliminating PCI-e bus bottlenecks and proposal duplication.

### 🛡️ Hybrid Tracker Stability & Smoothing
- **IoU Greedy Association**: Matches bounding boxes using Intersection-over-Union (IoU) overlap, falling back to centroid Euclidean distance matching for newly appeared or fast-moving objects.
- **EMA Jitter Suppression**: Applies an Exponential Moving Average (EMA) smoothing filter ($\alpha = 0.40$) on box coordinates, yielding zero-jitter visual tracks.
- **Class Majority Voting**: Eliminates frame-to-frame label flickering by taking a rolling majority vote over the last 10 frames for each persistent track ID.

### 🎨 CustomTkinter Desktop App & PIL BBox Renderer
- **Responsive Layout**: Designed with a slate-900 / dark aesthetic, featuring Sidebar navigation, Top Header (active model, live clock), Right Telemetry (latency, model FPS, class list), and a Bottom Status Bar (monitoring CPU%, GPU%, VRAM MB via `psutil`).
- **Pillow Rounded Renderer**: Converts OpenCV frames temporarily to PIL Images to draw smooth rounded bounding boxes with a `6px` radius.
- **Emoji Badges & Tracking IDs**: Labels are color-coded, prefixed with custom class emojis (e.g. `🚗 CAR #2`, `👤 PERSON #4`), and display a separate black badge with the persistent tracking ID.
- **Dual-Queue Threading**: offloads camera frame grabbing and YOLOv8 inference to background worker threads, keeping the desktop UI responsive at **60+ UI FPS**.

---

## 🏗️ System Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │          CustomTkinter Desktop App           │  ◄───  Main Dashboard
                  │           (Webcam / Local Asset Load)        │
                  └──────────────────────┬───────────────────────┘
                                         │ Direct Import &
                                         │ Local Inference
                  ┌──────────────────────▼───────────────────────┐
                  │            FastAPI Server (ASGI)             │  ◄───  Sim Webhooks
                  │          (localhost:8000 / Uvicorn)          │
                  └──────────────────────┬───────────────────────┘
                                         │
                          ┌──────────────┴──────────────┐
                          │                             │
             ┌────────────▼────────────┐   ┌────────────▼────────────┐
             │     CARLA Simulator     │   │      PyTorch Engine     │
             │    (TCP Port 2000)      │   │   ✓ YOLOv8  ✓ CUDA FP16 │
             └─────────────────────────┘   └─────────────────────────┘
```

---

## ⚙️ Repository Structure

```
autopilot-ai/
├── backend/                       # Python Perception Stack & API
│   ├── main_gui.py                # Standalone CustomTkinter Desktop Entry Point
│   ├── main.py                    # FastAPI Gateway & WebSocket server
│   ├── config.py                  # Environment configurations & folders
│   ├── fasterrcnn_detector.py     # YOLOv8 Inference Wrapper (compatibility name preserved)
│   ├── tracker.py                 # Upgraded IoU Tracker & BBox Smoothing
│   ├── stable_renderer.py         # Pillow Anti-Aliasing BBox & HUD Renderer
│   ├── pygame_autopilot.py        # Interactive CARLA autopilot client
│   ├── test_fasterrcnn.py         # Unit testing suite & benchmark tool
│   └── ui/                        # CustomTkinter Modular UI Panels
│       ├── main_window.py         # Grid layout manager & threading loops
│       ├── camera_view.py         # Embedded stream canvas
│       ├── settings.py            # Confidence & NMS threshold sliders
│       ├── stats_panel.py         # Telemetry, object list, & latency stats
│       └── theme.py               # Dark palette colors & fonts
├── src/                           # React Frontend Client (Sidecar Web Interface)
│   ├── pages/AiDetectionPage.tsx  # Telemetry widgets and frame decoder
│   └── main.tsx                   # Client entry point
```

---

## 📋 System Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10/11 or Ubuntu 20.04/22.04 |
| **Python** | 3.12 |
| **GPU** | NVIDIA GTX 1660 / RTX 3050 Laptop or higher (CUDA 12.1 compatible) |
| **RAM** | 16 GB+ |
| **CARLA** | Version 0.9.16 |

---

## 🚀 Quick Start Guide

### 1️⃣ Install Dependencies
Ensure you have the target virtual environment active, then install PyTorch with CUDA and the required Python modules:
```bash
# Move to backend directory
cd backend

# Create virtual environment
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install PyTorch + Torchvision with CUDA 12.1 Support
pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

# Install requirements
pip install -r requirements-backend.txt
```

### 2️⃣ Run Standalone CustomTkinter Desktop GUI
Launch the local desktop dashboard directly:
```bash
python main_gui.py
```
- Click **"Start Camera"** to initialize the optimized webcam stream (automatically configures white balance, auto-exposure, and contrast settings).
- Adjust the **Confidence Threshold** and **NMS IoU Threshold** sliders on-the-fly.
- Load local images or MP4 videos using the **"Upload"** buttons.

### 3️⃣ Run backend API Server & React Frontend (Optional Sidecar)
To start the WebSocket API gateway and run the Vite React browser client:
```bash
# Terminal 1: Start FastAPI Backend
cd backend
python main.py

# Terminal 2: Start Vite Web App (from workspace root)
npm install
npm run dev
```
Open **[http://localhost:8080/](http://localhost:8080/)** in your browser.

---

## 🧪 Verification & Benchmarks
To run the automated perception unit test suite:
```bash
cd backend
python test_fasterrcnn.py
```
Output report:
```
Ran 9 tests in 3.155s

OK
[TEST] Running performance benchmark...
==================================================
YOLOv8 Performance Benchmark
==================================================
Device:            cuda
Avg Latency:       6.77 ms
Average FPS:       147.74
GPU Memory Alloc:  44.11 MB
GPU Memory Reserv: 90.00 MB
==================================================
```

---

## 📄 License
This project is licensed under the **MIT License**.
Includes open-source components from:
- **Ultralytics YOLOv8**: AGPL-3.0 License
- **CARLA Simulator**: NCSA License
…]()
