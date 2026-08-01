# Quick Start Guide - Fixed Upload Display Issue

## 🚀 Quick Setup (2 minutes)

### Terminal 1: Start Backend
```powershell
cd autopilot-ai-main/backend
.\run_backend.ps1
```

Wait for output:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Start Frontend
```bash
cd autopilot-ai-main
npm run dev
```

### Open Browser
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

---

## 📹 Test Upload Flow

1. **Navigate to "VIDEO DETECTION"**
   - Click the VIDEO DETECTION link in sidebar

2. **Upload a Video**
   - Drag & drop or click to select a video file
   - Supported formats: MP4, AVI, MOV, MKV, WebM
   - File size: Any (but typically 10-500MB)

3. **Configure Settings**
   - **Confidence Threshold**: 0.35 (default is good)
   - **Model**: YOLOv8n (nano - fastest)
   - Keep Frame Skip at 0

4. **Click "DETECT OBJECTS IN VIDEO"**
   - Watch for upload confirmation
   - Processing will start automatically

5. **Watch Live Preview**
   - Live detection frames appear during processing
   - Shows detected objects in real-time

6. **View Results**
   - When complete, detection statistics appear
   - Download the annotated video
   - View detection breakdown by class

---

## ✅ What Should Happen (Fixed)

| Before | After ✓ |
|--------|---------|
| No preview image | Live frames display with detections |
| "Poll failed" error | Real-time status updates |
| No output video | Annotated MP4 plays in browser |
| Cryptic errors | Clear error messages with solutions |

---

## 🐛 If Something Goes Wrong

### Backend won't start?
```powershell
cd autopilot-ai-main/backend
python -c "import fastapi; print('fastapi ok')"
pip install -r requirements.txt
python main.py
```

### No images showing?
1. Check backend is running: http://localhost:8000/health
2. Check frontend is using correct URL: http://localhost:8000
3. Check browser console (F12) for errors
4. Restart both frontend and backend

### Video won't play?
1. Check video is actually created: 
   - `dir autopilot-ai-main/backend/outputs/`
2. Try downloading and playing locally
3. Try different video format (MP4 is best)

---

## 📁 Important Directories (Auto-Created)

All these are automatically created in `backend/` folder:
- `uploads/` - Your uploaded videos
- `outputs/` - Processed videos & frames
- `ai_frames/` - Live preview images
- `ai_outputs/` - Advanced detection results

---

## 🔍 Verify Everything Works

Open this in browser and it should show OK:
```
http://localhost:8000/health
```

You should see:
```json
{
  "status": "ok",
  "components": {
    "api": "running",
    "yolo": "loaded",
    "video_processor": "loaded"
  },
  "directories": {
    "uploads": true,
    "outputs": true,
    "ai_frames": true
  }
}
```

---

## 💡 Tips for Best Results

1. **Use shorter videos first** (5-30 seconds) to test
2. **Use YOLOv8n (nano)** for fastest processing
3. **Confidence 0.35** catches most objects without false positives
4. **MP4 format** works best
5. **Keep browser tab active** to prevent timeout during processing

---

## 📊 Example Expected Times

| Video Length | Model | Time |
|------------|-------|------|
| 5 seconds | Nano | ~2 seconds |
| 30 seconds | Nano | ~10 seconds |
| 1 minute | Small | ~30 seconds |
| 5 minutes | Small | ~2 minutes |

*Times vary based on GPU availability*

---

## 🎯 What's Fixed

✓ Backend now serves images directly (fast & reliable)  
✓ Frontend uses correct image URLs  
✓ Live detection preview works  
✓ Error handling is clear  
✓ Auto-creates all needed directories  
✓ Health check shows component status  
✓ Easy startup scripts for Windows  

---

**Still having issues?** Check [UPLOAD_DISPLAY_FIX.md](UPLOAD_DISPLAY_FIX.md) for detailed troubleshooting.
