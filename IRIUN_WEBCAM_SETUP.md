# 📱 Iriun Webcam Setup Guide

## Overview

**Iriun Webcam** allows you to use your phone's camera as a wireless virtual webcam on your PC/Mac/Linux. This is perfect for:
- Using your phone camera with autopilot-ai on your desktop
- Wireless streaming (no cables needed)
- Automatic camera detection in the application
- Works with Smart Connect and limited browsers

## Installation

### Step 1: Download & Install Desktop App

#### Windows
1. Visit [iriun.com](https://iriun.com)
2. Download **Iriun for Windows** v2.9.5 or later
3. Run installer, follow setup wizard
4. Restart your PC

#### Mac
1. Visit [iriun.com](https://iriun.com)
2. Download **Iriun for Mac** v2.9.1 or later
3. Open `.dmg` file, drag to Applications
4. Launch from Applications folder

#### Linux (Ubuntu 22.04+)
1. Visit [iriun.com](https://iriun.com)
2. Download **Iriun for Linux** v2.9.1 or later
3. Install: `sudo dpkg -i iriun_webcam*.deb`
4. Restart system

### Step 2: Install Phone App

1. **On your phone**, go to App Store / Play Store
2. Search: **"Iriun Webcam"**
3. Install the Iriun Webcam app
4. Open the app on your phone

### Step 3: Connect Phone & PC

#### Requirements
- **Same WiFi network** (PC and phone on same WiFi)
- **Both apps running** (desktop and mobile)
- **Strong connection** (5GHz WiFi recommended)

#### Connection Steps
1. Open Iriun app on phone
2. Open Iriun on PC/Mac (system tray icon)
3. Phone app should detect the PC
4. Tap phone name in app to connect
5. Accept connection request on PC (if prompted)
6. Phone camera should now appear in your PC

## Using with Autopilot-AI

### Automatic Camera Detection

When you open the Live Camera feature in autopilot-ai:
1. System automatically detects **all connected cameras**, including Iriun
2. Available cameras are listed in the console:
   ```
   📹 Found 2 camera(s):
       📷 HD Webcam (USB)
       📱 Iriun Webcam
   ```

### Selecting Iriun Camera

The camera selection works automatically:
- If you have an **Iriun Webcam**, it will be detected
- Click **"Start Live Camera"** button
- System will connect to Iriun and start streaming
- You'll see: `✅ Using: Iriun Webcam`

### Live Detection with Iriun

Once connected:
- ✅ Real-time object detection from phone camera
- ✅ Bounding boxes drawn on detected objects
- ✅ Line crossing detection
- ✅ Statistics (FPS, object count, action)
- ✅ Smooth 8-10 FPS streaming

## Troubleshooting

### Phone Not Detected

**Problem:** "No device found" in Iriun app

**Solutions:**
1. Check both on **same WiFi network**
   - Ensure phone WiFi is ON
   - Ensure PC WiFi is ON (not just Ethernet)
   - Try 5GHz WiFi band (faster, less interference)

2. Restart both apps
   - Close Iriun on PC
   - Close Iriun on phone
   - Wait 10 seconds
   - Reopen on phone first, then PC

3. Check firewall
   - Iriun needs network access
   - Add Iriun to Windows firewall exceptions
   - Try temporarily disabling firewall (if safe)

4. Update both apps
   - PC: Get latest from iriun.com
   - Phone: Update from App Store / Play Store

### Camera Not Appearing in Autopilot-AI

**Problem:** Camera detected by Iriun but not showing in autopilot-ai

**Solutions:**
1. **Refresh page**
   - Close autopilot-ai browser tab
   - Reopen it
   - Check console for detected cameras

2. **Check camera enumeration**
   - Open browser Developer Tools (F12)
   - Look at console for "Found X camera(s)" message
   - If Iriun not listed, reconnect Iriun app

3. **Test in other apps**
   - Open Zoom, Skype, or Google Meet
   - See if Iriun camera works there
   - If yes, issue is with autopilot-ai browser
   - If no, issue is with Iriun connection

### Connection Drops / Frames Skip

**Problem:** Connection to Iriun keeps dropping, frames lag

**Solutions:**
1. **Use 5GHz WiFi**
   - Faster and more stable
   - Less interference from other devices
   - Check your router settings

2. **Reduce background WiFi usage**
   - Close other apps using internet on phone
   - Stop large downloads on PC
   - Close streaming services (YouTube, Netflix)

3. **Get closer to router**
   - Move phone and PC closer to WiFi router
   - Minimize walls/obstacles between devices
   - Try removing thick barriers

4. **Reduce resolution**
   - Default is 640x480
   - Works fine for detection
   - You can manually reduce in Iriun app settings

5. **Restart WiFi**
   - Restart WiFi router (unplug 10 seconds)
   - Reconnect phone and PC
   - Relaunch Iriun apps

### "Camera is already in use" Error

**Problem:** Error message says camera is in use by another app

**Solutions:**
1. **Close other camera apps**
   - Zoom, Skype, OBS, Snap Camera
   - Windows Camera app
   - Any other app using camera

2. **Close browser tabs using camera**
   - Other open video call tabs
   - Other camera streaming pages

3. **Restart Iriun**
   - Close Iriun app on phone
   - Close Iriun on PC
   - Wait 10 seconds
   - Reopen PC Iriun first, then phone

### "Can't connect to backend" After Iriun Setup

**Problem:** Camera connects but shows backend error

**Solutions:**
1. **Ensure backend is running**
   ```bash
   cd autopilot-ai-main/backend
   python main.py
   ```
   Should show: `Uvicorn running on http://0.0.0.0:8000`

2. **Check firewall allows localhost**
   - Backend runs on localhost:8000
   - Should be accessible from browser
   - Check Windows firewall if on Windows

3. **Try different browser**
   - Chrome or Firefox recommended
   - Safari also supported
   - Avoid Smart Connect's WebView

## Performance Tips

### Best Results
- **5GHz WiFi** (faster than 2.4GHz)
- **Close proximity** to router
- **High-quality phone** (modern smartphones best)
- **Good lighting** (helps object detection)
- **Minimal background apps** (smoother streaming)

### Settings to Optimize

In Iriun app settings on phone:
- Resolution: 640x480 (default, good for detection)
- Frame rate: 30 FPS (default)
- Quality: Medium/High (depending on WiFi)

In autopilot-ai:
- Confidence: 0.50-0.60 (adjust as needed)
- Live camera resolution: 640x480 (pre-set)

## Alternative Solutions

If Iriun Webcam doesn't work for you:

### 1. Use Browser's Native Camera
- Works on Chrome, Firefox, Safari (desktop & mobile)
- No extra app needed
- Limited to same device

### 2. Use Video Upload Feature
- Record video with phone camera
- Upload to autopilot-ai
- Get same detection + tracking results
- Recommended for slower devices

### 3. Use Native Webcam
- Attach USB webcam to desktop
- Plug & play, no setup needed
- Works without WiFi
- Limited positioning

### 4. MJPEG IP Camera
- Advanced option for professionals
- Requires IP camera hardware
- More complex setup

## Frequently Asked Questions

### Q: Does Iriun work on mobile phones?
**A:** Iriun app works on phones to send camera to PC. On phone's browser, you need native camera support (Chrome, Firefox, Safari). Smart Connect has limitations.

### Q: What's the latency?
**A:** ~100-300ms depending on WiFi. Good enough for real-time detection but not for critical timing applications.

### Q: Can I use multiple phones?
**A:** Yes, Iriun shows them as separate cameras. Each appears as "Iriun Webcam (Phone Name)". Connect whichever one you want to use.

### Q: Does it work over internet / VPN?
**A:** No, Iriun requires local WiFi network. It will not work over cellular data, VPN, or remote connections. Must be same WiFi.

### Q: Can I use USB cable instead of WiFi?
**A:** No, Iriun is WiFi-only. USB connection not supported.

### Q: What if I have multiple cameras (webcam + Iriun)?
**A:** All will appear in the list. System automatically detects all devices. You can choose which one to use.

### Q: Is my data secure?
**A:** Iriun streams locally on your WiFi. Data never goes to cloud or external servers. Completely private.

### Q: What about battery drain?
**A:** Iriun uses moderate battery. For extended use, keep phone plugged in.

### Q: Can I record the stream?
**A:** You can use the Video Upload feature or screen record your browser. Iriun app itself has no built-in recording.

## System Requirements

### Desktop Requirements
- **Windows:** 7 or later
- **Mac:** 10.12 (Sierra) or later  
- **Linux:** Ubuntu 22.04 or later

### Phone Requirements
- **iOS:** 12.0 or later (iPhone/iPad)
- **Android:** 6.0 or later

### Network Requirements
- **WiFi:** 2.4GHz or 5GHz
- **Speed:** Minimum 2 Mbps for good experience
- **Network:** Local WiFi only (not internet)

## Getting Help

- **Iriun Website:** https://iriun.com
- **Iriun Support:** support@iriun.com
- **Iriun Reddit:** r/iphone or r/android search "Iriun"
- **Autopilot-AI Issues:** Create GitHub issue

## Summary

With Iriun Webcam setup:
- ✅ Use phone camera on PC for detection
- ✅ Works wirelessly over WiFi
- ✅ Automatic camera detection
- ✅ Full live detection with tracking
- ✅ No Smart Connect limitations
- ✅ Professional wireless camera solution
