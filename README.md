# GO2 Simple Workspace 🐕🎤

A lightweight ROS 2 workspace for the **Unitree GO2** that lets you control
the robot using **voice commands** — spoken naturally, recognized via
Google Speech Recognition with **OpenAI Whisper** as offline fallback,
and sent directly to the GO2's motion API.

[![ROS2](https://img.shields.io/badge/ROS_2-Humble-blue)](https://docs.ros.org/en/humble/)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)

> **Related:** This is a simplified standalone companion to the
> [GO2 Seeing-Eye Dog](https://github.com/yusufdxb/GO2-seeing-eye-dog) thesis project.

---

## 📹 Demo

**Whisper has been implemented and more commands are live — see the demo below**

<p align="center">
  <a href="https://youtu.be/Ac-OsyQlgBo">
    <img src="https://img.youtube.com/vi/Ac-OsyQlgBo/maxresdefault.jpg" width="640">
  </a>
</p>

---

## What This Does

```
Microphone → Google SR / Whisper → /go2_command → GO2 Command Bridge → Unitree Motion API
```

Two ROS 2 nodes work together:

| Node | File | What it does |
|---|---|---|
| `speech_command_node` | `speech_command_node.py` | Listens to mic, transcribes speech, publishes to `/go2_command` |
| `go2_command_bridge` | `go2_command_bridge.py` | Subscribes to `/go2_command`, maps to Unitree API IDs, sends to robot |

---

## Supported Voice Commands

| You say | Robot does | Unitree API ID |
|---|---|---|
| "sit" / "seat" / "set" | Sit down | 1009 |
| "stand" / "stan" | Stand up | 1010 |
| "jump" | Jump | 1006 |
| "flip" / "backflip" | Backflip | 1025 |
| "dance" / "dance one" | Dance 1 | 1022 |
| "dance two" / "dance again" | Dance 2 | 1023 |
| "shake" / "shake hands" / "paw" | Shake hands | 1019 |
| "forward" / "move forward" | Walk forward | 1008 |
| "hello" / "greet" | Greet behavior | 1016 |
| "estop" / "emergency" | Emergency stop | 1001 |

---

## Package Structure

```
go2_assist/
├── speech_command_node.py    ← Mic → Google SR / Whisper → /go2_command
├── go2_command_bridge.py     ← /go2_command → Unitree API
├── webrtc_video_node.py      ← WebRTC video stream
├── setup.py
├── setup.cfg
└── package.xml
```

---

## Setup

```bash
# Python dependencies
pip install SpeechRecognition pyaudio

# Whisper (for offline fallback)
pip install openai-whisper torch soundfile

# Clone and build
mkdir -p ~/go2_ws/src && cd ~/go2_ws/src
git clone https://github.com/yusufdxb/go2-simple-workspace.git
cd ~/go2_ws
colcon build --symlink-install
source install/setup.bash
```

---

## Run

```bash
# Speech node
ros2 run go2_assist speech_command_node

# Command bridge (separate terminal)
ros2 run go2_assist go2_command_bridge

# Test without hardware — watch published commands
ros2 topic echo /go2_command

# Send a command manually
ros2 topic pub /go2_command std_msgs/msg/String "data: 'sit'" --once
ros2 topic pub /go2_command std_msgs/msg/String "data: 'dance'" --once
```

---

## How Whisper Works

Google Speech Recognition is the primary engine — fast and requires no
local model. If Google SR fails (bad audio, no internet, or unrecognized
speech), **Whisper automatically takes over** using a local model running
entirely on your machine.

```
Audio captured
     │
     ▼
Google SR ── success ──► publish command
     │
   fails
     │
     ▼
Whisper (local) ──────► publish command
```

Whisper is enabled by default. To disable:
```bash
ros2 run go2_assist speech_command_node --ros-args -p use_whisper:=false
```

---

## Adding More Commands

In `speech_command_node.py` → `process_command()`:
```python
elif any(w in text for w in ["roll over", "roll"]):
    self.publish_command("roll")
```

In `go2_command_bridge.py` → `API_IDS`:
```python
'roll': 1030,  # replace with correct Unitree API ID
```

---

## Node Graph

```
[Microphone]
     │
     ▼
[speech_command_node]
  Google SR → Whisper fallback
     │
     │  /go2_command (std_msgs/String)
     ▼
[go2_command_bridge]
  command → Unitree API ID
     │
     │  /api/sport/request (unitree_api/Request)
     ▼
[GO2 Unitree Motion API]
```

---

## Author

**Yusuf Guenena** | M.S. Robotics Engineering, Wayne State University
[LinkedIn](https://www.linkedin.com/in/yusuf-guenena) · [GitHub](https://github.com/yusufdxb)
