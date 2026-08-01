# 🎥 Live Camera Feature Guide

## Quick Start

### Option 1: Native Browser Camera (Easiest)
**Best for:** Desktop with built-in/USB webcam

1. Open autopilot-ai on **Chrome, Firefox, or Safari**
2. Go to **"AI Detection"** tab
3. Click **"Start Live Camera"**
4. Grant camera permission
5. See real-time object detection!

### Option 2: Iriun Webcam (Wireless Phone Camera)
**Best for:** Using your phone camera wirelessly

1. Install Iriun on PC and phone (free app)
2. Connect phone to same WiFi as PC
3. Open Iriun app on both devices
4. Open autopilot-ai
5. Click **"Start Live Camera"**
6. System automatically detects Iriun camera
7. Select Iriun from available cameras
8. Start detection with phone camera!

## Camera Device Selection

When you start the camera, autopilot-ai automatically:
- ✅ Scans for available cameras
- ✅ Lists all detected devices (USB webcam, Iriun, etc.)
- ✅ Shows in the console log:
  ```
  📹 Found 2 camera(s):
      📷 HD Webcam
      📱 Iriun Webcam
  ```
- ✅ Tries each camera until one connects
- ✅ Shows which camera is active

## Supported Cameras

| Camera Type | Support | Notes |
|------------|---------|-------|
| Built-in Laptop Webcam | ✅ Full | Works on all laptops |
| USB Webcam | ✅ Full | Plug & play |
| Iriun Webcam | ✅ Full | Wireless phone camera |
| OBS Virtual Camera | ✅ Full | For streaming setups |
| Smartphone Native | ⚠️ Limited | Works in browser if device has camera |
| IP Camera | ⚠️ Partial | Requires special setup |

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ Full | Desktop & mobile |
| Firefox | ✅ Full | Desktop & mobile |
| Safari | ✅ Full | Desktop & mobile |
| Edge | ✅ Full | Windows only |
| Opera | ✅ Full | Desktop & mobile |
| Smart Connect | ❌ None | Use Iriun Webcam instead |
| Samsung Internet | ⚠️ Limited | May have permission issues |

## Live Detection Features

Once camera is connected:

### Real-Time Detection
- **Object Recognition:** Cars, people, bikes, traffic signs
- **Bounding Boxes:** Professional green rectangles with labels
- **Confidence Scores:** "CAR 95%" format
- **Frame Rate:** 8-10 FPS typical (GPU dependent)

### Advanced Features
- **Object Tracking:** Tracks same object across frames
- **Line Crossing Detection:** Detects objects crossing detection lines
- **Action Status:** STOP / SLOW / GO based on detected threats
- **Statistics:** Real-time FPS, object count, detection stats

### Console Output
Real-time log shows:
- Camera connection status
- Resolution and specifications
- Detected objects with confidence
- Crossing events
- Performance metrics

## Troubleshooting

### "Camera not found"
**Solution 1:** Use Iriun Webcam
- Install Iriun app on phone
- Connect to same WiFi as PC
- Open Iriun apps on both
- Try again

**Solution 2:** Check browser permissions
- Chrome: Settings → Privacy → Camera
- Firefox: Settings → Privacy → Permissions
- Enable camera for localhost:3000 or localhost:5173

**Solution 3:** Try different browser
- Chrome, Firefox, or Safari
- Avoid Smart Connect or in-app browsers

### "Camera permission denied"
- Browser asking for permission but you declined
- Settings → Find this website → Camera
- Change to "Allow" or "Always allow"
- Reload page

### "Camera already in use"
- Another app has camera open
- Close: Zoom, Skype, Teams, OBS, etc.
- Check other browser tabs with camera
- Restart browser

### "WebSocket error"
- Backend not running
- Start with: `python backend/main.py`
- Should show: `Uvicorn running on http://0.0.0.0:8000`

## Performance Optimization

### For Better Detection
- **Good lighting:** Well-lit environment
- **Clear view:** Position camera to see objects clearly
- **Stable positioning:** Mount camera, don't hold it

### For Better FPS
- **Close to WiFi router:** For Iriun, get signal strength ≥-50dBm
- **5GHz WiFi:** Faster than 2.4GHz
- **Reduce background apps:** Close Spotify, YouTube, etc.
- **Restart browser:** If it slows down over time

### For Better Accuracy
- **Increase confidence:** Reduce false positives (set to 0.60+)
- **Good camera quality:** HD webcam > phone camera
- **Appropriate distance:** Objects 3-20 meters for cars/people

## Tips & Tricks

### Multiple Cameras
- Connect both USB webcam and Iriun
- Both appear in the list
- Switch between them by restarting camera

### Record Detection
- Browser's screen record: Win+Shift+S (Windows) or Cmd+Shift+5 (Mac)
- Or use OBS with camera feed
- Or upload video to Video Detection feature

### Remote Monitoring
- Use Iriun from different rooms
- Phone in one room, PC in another
- All on same WiFi network

### Best Positions
- **Road monitoring:** Mount camera facing traffic
- **Parking lot:** Elevated position
- **Indoor:** Center of room for best view
- **Outdoor:** Shade to avoid glare

## Advanced Setup

### With Iriun Webcam
**For maximum flexibility:**
1. Install Iriun (see [IRIUN_WEBCAM_SETUP.md](IRIUN_WEBCAM_SETUP.md))
2. Connect phone wirelessly
3. Position phone for best view
4. Monitor from anywhere on same WiFi

### With Multiple Cameras
**For comprehensive monitoring:**
1. Set up Iriun on phone
2. Keep USB webcam connected
3. Switch cameras in console
4. Compare detection between cameras

### With OBS
**For recording + streaming setup:**
1. Open OBS
2. Add Virtual Camera (OBS output)
3. OBS camera appears in autopilot-ai
4. Stream or record while detecting

## Frequently Asked Questions

**Q: Can I use phone camera without Iriun?**
A: Yes, if you open autopilot-ai browser on your phone. But Smart Connect app won't work (use Safari/Chrome instead).

**Q: What's the range of Iriun?**
A: WiFi range of your network (typically 30-50 meters). Must be same WiFi network.

**Q: Can I use multiple phones?**
A: Yes, install Iriun on multiple phones. Each appears as separate camera device.

**Q: Does it work on Raspberry Pi?**
A: Iriun doesn't support Raspberry Pi yet. But USB camera works fine on Pi.

**Q: Can I adjust camera resolution?**
A: Default 640x480 is good for detection. Iriun settings allow customization.

**Q: What's the bandwidth usage?**
A: Iriun typically uses 1-3 Mbps. Works on 4G but WiFi recommended.

**Q: Can I see who accessed my camera?**
A: Iriun is local-only, no cloud logging. Data stays on your network.

## Next Steps

1. **[Iriun Webcam Setup Guide](IRIUN_WEBCAM_SETUP.md)** - Complete Iriun installation
2. **[Camera Fix Documentation](CAMERA_FIX.md)** - Technical details about camera support
3. **Upload Video** - If live camera not working, use video upload feature
4. **Check Logs** - Browser console shows detailed camera info

## Support

- **Technical Issues:** Check browser console (F12) for errors
- **Iriun Support:** [iriun.com](https://iriun.com)
- **Autopilot-AI Issues:** Create GitHub issue with:
  - Browser type and version
  - Camera device (USB/Iriun/Built-in)
  - Error message from console
  - Steps to reproduce
