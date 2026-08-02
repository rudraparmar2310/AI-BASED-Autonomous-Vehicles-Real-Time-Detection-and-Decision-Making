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
<img width="585" height="1189" alt="download" src="https://github.com/user-attachments/assets/1c227357-a989-4501-afec-ab3088a218b8" />

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 584.6299999999999 1189.3" width="584.6299999999999" height="1189.3" style="--bg:#FFFFFF;--fg:#3B3B3B;--line:#3B3B3B;--accent:#005FB8;--muted:#3B3B3BCC;--surface:#F8F8F8;--border:#3B3B3B;background:var(--bg)">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap');
  text { font-family: 'Inter', system-ui, sans-serif; }
  svg {
    /* Derived from --bg and --fg (overridable via --line, --accent, etc.) */
    --_text:          var(--fg);
    --_text-sec:      var(--muted, color-mix(in srgb, var(--fg) 60%, var(--bg)));
    --_text-muted:    var(--muted, color-mix(in srgb, var(--fg) 40%, var(--bg)));
    --_text-faint:    color-mix(in srgb, var(--fg) 25%, var(--bg));
    --_line:          var(--line, color-mix(in srgb, var(--fg) 50%, var(--bg)));
    --_arrow:         var(--accent, color-mix(in srgb, var(--fg) 85%, var(--bg)));
    --_node-fill:     var(--surface, color-mix(in srgb, var(--fg) 3%, var(--bg)));
    --_node-stroke:   var(--border, color-mix(in srgb, var(--fg) 20%, var(--bg)));
    --_group-fill:    var(--bg);
    --_group-hdr:     color-mix(in srgb, var(--fg) 5%, var(--bg));
    --_inner-stroke:  color-mix(in srgb, var(--fg) 12%, var(--bg));
    --_key-badge:     color-mix(in srgb, var(--fg) 10%, var(--bg));
  }
</style>
<defs>
  <marker id="arrowhead" markerWidth="8" markerHeight="5" refX="7" refY="2.5" orient="auto">
    <polygon points="0 0, 8 2.5, 0 5" fill="var(--_arrow)" stroke="var(--_arrow)" stroke-width="0.75" stroke-linejoin="round" />
  </marker>
  <marker id="arrowhead-start" markerWidth="8" markerHeight="5" refX="1" refY="2.5" orient="auto-start-reverse">
    <polygon points="8 0, 0 2.5, 8 5" fill="var(--_arrow)" stroke="var(--_arrow)" stroke-width="0.75" stroke-linejoin="round" />
  </marker>
</defs>
<polyline class="edge" data-from="A" data-to="B" data-style="solid" data-arrow-start="false" data-arrow-end="true" data-label="Raw Images / Frames" points="301.9479999999999,76.9 301.9479999999999,193.2" fill="none" stroke="var(--_line)" stroke-width="1" marker-end="url(#arrowhead)" />
<polyline class="edge" data-from="B" data-to="C" data-style="solid" data-arrow-start="false" data-arrow-end="true" data-label="Ingest Queue maxsize=1" points="301.9479999999999,230.10000000000002 301.9479999999999,346.40000000000003" fill="none" stroke="var(--_line)" stroke-width="1" marker-end="url(#arrowhead)" />
<polyline class="edge" data-from="C" data-to="D" data-style="solid" data-arrow-start="false" data-arrow-end="true" data-label="Tensor Preprocessing &amp; CUDA FP16 Autocast" points="301.9479999999999,383.3 301.9479999999999,499.6000000000001" fill="none" stroke="var(--_line)" stroke-width="1" marker-end="url(#arrowhead)" />
<polyline class="edge" data-from="D" data-to="E" data-style="solid" data-arrow-start="false" data-arrow-end="true" data-label="GPU-Based Confidence &amp; Class Filtering" points="301.9479999999999,536.5 301.948,652.8" fill="none" stroke="var(--_line)" stroke-width="1" marker-end="url(#arrowhead)" />
<polyline class="edge" data-from="E" data-to="F" data-style="solid" data-arrow-start="false" data-arrow-end="true" data-label="Clean Boxes &amp; Labels" points="301.948,689.6999999999999 301.9479999999999,805.9999999999999" fill="none" stroke="var(--_line)" stroke-width="1" marker-end="url(#arrowhead)" />
<polyline class="edge" data-from="F" data-to="G" data-style="solid" data-arrow-start="false" data-arrow-end="true" data-label="Smoothed Trails &amp; IDs" points="259.14133333333325,842.8999999999999 259.14133333333325,878.9 168.79049999999995,878.9 168.79049999999995,959.1999999999999" fill="none" stroke="var(--_line)" stroke-width="1" marker-end="url(#arrowhead)" />
<polyline class="edge" data-from="G" data-to="H" data-style="solid" data-arrow-start="false" data-arrow-end="true" data-label="Annotated Frame Base64" points="168.79049999999995,996.0999999999999 168.79049999999995,1112.3999999999999" fill="none" stroke="var(--_line)" stroke-width="1" marker-end="url(#arrowhead)" />
<polyline class="edge" data-from="F" data-to="I" data-style="solid" data-arrow-start="false" data-arrow-end="true" data-label="Traffic Decisions STOP/SLOW/GO" points="344.7546666666666,842.8999999999999 344.7546666666666,878.8999999999999 435.1054999999999,878.8999999999999 435.1054999999999,959.1999999999998" fill="none" stroke="var(--_line)" stroke-width="1" marker-end="url(#arrowhead)" />
<g class="edge-label" data-from="A" data-to="B" data-label="Raw Images / Frames">
  <rect x="243.44799999999992" y="119.9" width="116.25400000000002" height="30.3" rx="2" ry="2" fill="var(--bg)" stroke="var(--_inner-stroke)" stroke-width="1" />
  <text x="301.57499999999993" y="135.05" text-anchor="middle" font-size="11" font-weight="400" fill="var(--_text-sec)" dy="3.8499999999999996">Raw Images / Frames</text>
</g>
<g class="edge-label" data-from="B" data-to="C" data-label="Ingest Queue maxsize=1">
  <rect x="237.44799999999998" y="273.1" width="128.13400000000001" height="30.3" rx="2" ry="2" fill="var(--bg)" stroke="var(--_inner-stroke)" stroke-width="1" />
  <text x="301.515" y="288.25" text-anchor="middle" font-size="11" font-weight="400" fill="var(--_text-sec)" dy="3.8499999999999996">Ingest Queue maxsize=1</text>
</g>
<g class="edge-label" data-from="C" data-to="D" data-label="Tensor Preprocessing &amp; CUDA FP16 Autocast">
  <rect x="184.94799999999992" y="426.30000000000007" width="233.27199999999996" height="30.3" rx="2" ry="2" fill="var(--bg)" stroke="var(--_inner-stroke)" stroke-width="1" />
  <text x="301.5839999999999" y="441.45000000000005" text-anchor="middle" font-size="11" font-weight="400" fill="var(--_text-sec)" dy="3.8499999999999996">Tensor Preprocessing &amp; CUDA FP16 Autocast</text>
</g>
<g class="edge-label" data-from="D" data-to="E" data-label="GPU-Based Confidence &amp; Class Filtering">
  <rect x="198.94799999999992" y="579.5" width="205.94799999999998" height="30.3" rx="2" ry="2" fill="var(--bg)" stroke="var(--_inner-stroke)" stroke-width="1" />
  <text x="301.9219999999999" y="594.65" text-anchor="middle" font-size="11" font-weight="400" fill="var(--_text-sec)" dy="3.8499999999999996">GPU-Based Confidence &amp; Class Filtering</text>
</g>
<g class="edge-label" data-from="E" data-to="F" data-label="Clean Boxes &amp; Labels">
  <rect x="241.44799999999992" y="732.6999999999999" width="120.41200000000002" height="30.3" rx="2" ry="2" fill="var(--bg)" stroke="var(--_inner-stroke)" stroke-width="1" />
  <text x="301.65399999999994" y="747.8499999999999" text-anchor="middle" font-size="11" font-weight="400" fill="var(--_text-sec)" dy="3.8499999999999996">Clean Boxes &amp; Labels</text>
</g>
<g class="edge-label" data-from="F" data-to="G" data-label="Smoothed Trails &amp; IDs">
  <rect x="108.79049999999995" y="885.9" width="119.22400000000005" height="30.3" rx="2" ry="2" fill="var(--bg)" stroke="var(--_inner-stroke)" stroke-width="1" />
  <text x="168.40249999999997" y="901.05" text-anchor="middle" font-size="11" font-weight="400" fill="var(--_text-sec)" dy="3.8499999999999996">Smoothed Trails &amp; IDs</text>
</g>
<g class="edge-label" data-from="G" data-to="H" data-label="Annotated Frame Base64">
  <rect x="100.29049999999997" y="1039.1" width="136.45000000000002" height="30.3" rx="2" ry="2" fill="var(--bg)" stroke="var(--_inner-stroke)" stroke-width="1" />
  <text x="168.51549999999997" y="1054.25" text-anchor="middle" font-size="11" font-weight="400" fill="var(--_text-sec)" dy="3.8499999999999996">Annotated Frame Base64</text>
</g>
<g class="edge-label" data-from="F" data-to="I" data-label="Traffic Decisions STOP/SLOW/GO">
  <rect x="345.6054999999999" y="885.8999999999999" width="178.62399999999997" height="30.3" rx="2" ry="2" fill="var(--bg)" stroke="var(--_inner-stroke)" stroke-width="1" />
  <text x="434.9174999999999" y="901.0499999999998" text-anchor="middle" font-size="11" font-weight="400" fill="var(--_text-sec)" dy="3.8499999999999996">Traffic Decisions STOP/SLOW/GO</text>
</g>
<g class="node" data-id="A" data-label="Camera Feed / CARLA Simulator / Video Upload" data-shape="rectangle">
  <rect x="143.51749999999996" y="40" width="316.86099999999993" height="36.900000000000006" rx="0" ry="0" fill="var(--_node-fill)" stroke="var(--_node-stroke)" stroke-width="0.75" />
  <text x="301.9479999999999" y="58.45" text-anchor="middle" font-size="13" font-weight="500" fill="var(--_text)" dy="4.55">Camera Feed / CARLA Simulator / Video Upload</text>
</g>
<g class="node" data-id="B" data-label="FastAPI WebSockets / REST API" data-shape="rectangle">
  <rect x="185.38399999999996" y="193.2" width="233.12799999999993" height="36.900000000000006" rx="0" ry="0" fill="var(--_node-fill)" stroke="var(--_node-stroke)" stroke-width="0.75" />
  <text x="301.9479999999999" y="211.64999999999998" text-anchor="middle" font-size="13" font-weight="500" fill="var(--_text)" dy="4.55">FastAPI WebSockets / REST API</text>
</g>
<g class="node" data-id="C" data-label="PyTorch Faster R-CNN Detector" data-shape="rectangle">
  <rect x="186.12499999999994" y="346.40000000000003" width="231.64599999999996" height="36.900000000000006" rx="0" ry="0" fill="var(--_node-fill)" stroke="var(--_node-stroke)" stroke-width="0.75" />
  <text x="301.9479999999999" y="364.85" text-anchor="middle" font-size="13" font-weight="500" fill="var(--_text)" dy="4.55">PyTorch Faster R-CNN Detector</text>
</g>
<g class="node" data-id="D" data-label="Neural Network Inference" data-shape="rectangle">
  <rect x="206.13199999999995" y="499.6000000000001" width="191.63199999999998" height="36.900000000000006" rx="0" ry="0" fill="var(--_node-fill)" stroke="var(--_node-stroke)" stroke-width="0.75" />
  <text x="301.9479999999999" y="518.0500000000001" text-anchor="middle" font-size="13" font-weight="500" fill="var(--_text)" dy="4.55">Neural Network Inference</text>
</g>
<g class="node" data-id="E" data-label="torchvision.ops.nms" data-shape="rectangle">
  <rect x="221.69299999999996" y="652.8" width="160.51" height="36.900000000000006" rx="0" ry="0" fill="var(--_node-fill)" stroke="var(--_node-stroke)" stroke-width="0.75" />
  <text x="301.948" y="671.25" text-anchor="middle" font-size="13" font-weight="500" fill="var(--_text)" dy="4.55">torchvision.ops.nms</text>
</g>
<g class="node" data-id="F" data-label="CentroidTracker &amp; Motion Prediction" data-shape="rectangle">
  <rect x="173.52799999999996" y="805.9999999999999" width="256.8399999999999" height="36.900000000000006" rx="0" ry="0" fill="var(--_node-fill)" stroke="var(--_node-stroke)" stroke-width="0.75" />
  <text x="301.9479999999999" y="824.4499999999999" text-anchor="middle" font-size="13" font-weight="500" fill="var(--_text)" dy="4.55">CentroidTracker &amp; Motion Prediction</text>
</g>
<g class="node" data-id="G" data-label="StableBBoxRenderer &amp; HUD Overlay" data-shape="rectangle">
  <rect x="40" y="959.1999999999999" width="257.5809999999999" height="36.900000000000006" rx="0" ry="0" fill="var(--_node-fill)" stroke="var(--_node-stroke)" stroke-width="0.75" />
  <text x="168.79049999999995" y="977.65" text-anchor="middle" font-size="13" font-weight="500" fill="var(--_text)" dy="4.55">StableBBoxRenderer &amp; HUD Overlay</text>
</g>
<g class="node" data-id="H" data-label="React Frontend Client" data-shape="rectangle">
  <rect x="84.83049999999997" y="1112.3999999999999" width="167.92" height="36.900000000000006" rx="0" ry="0" fill="var(--_node-fill)" stroke="var(--_node-stroke)" stroke-width="0.75" />
  <text x="168.79049999999995" y="1130.85" text-anchor="middle" font-size="13" font-weight="500" fill="var(--_text)" dy="4.55">React Frontend Client</text>
</g>
<g class="node" data-id="I" data-label="CARLA PID Controller / Web UI" data-shape="rectangle">
  <rect x="325.5809999999999" y="959.1999999999998" width="219.049" height="36.900000000000006" rx="0" ry="0" fill="var(--_node-fill)" stroke="var(--_node-stroke)" stroke-width="0.75" />
  <text x="435.1054999999999" y="977.6499999999999" text-anchor="middle" font-size="13" font-weight="500" fill="var(--_text)" dy="4.55">CARLA PID Controller / Web UI</text>
</g>
</svg>
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
