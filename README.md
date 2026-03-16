# GO2 Simple Workspace 🐕🎤

A lightweight ROS 2 workspace for the **Unitree GO2** that lets you control
the robot using **voice commands** — spoken naturally, recognized via
speech recognition, and sent directly to the GO2's motion API.

[![ROS2](https://img.shields.io/badge/ROS_2-Humble-blue)](https://docs.ros.org/en/humble/)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)

> **Related:** This is a simplified standalone companion to the
> [GO2 Seeing-Eye Dog](https://github.com/yusufdxb/GO2-seeing-eye-dog) thesis project.

---

## What This Does

```
Microphone → Speech Recognition → /go2_command → GO2 Command Bridge → Unitree Motion API
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
| "hello" | Hello behavior | — |
| "estop" / "emergency" | Emergency stop | 1001 |

---

## Package Structure

```
go2-simple-workspace/
├── go2_voice_control/
│   ├── go2_voice_control/
│   │   ├── __init__.py
│   │   ├── speech_command_node.py    ← Mic → speech → /go2_command
│   │   └── go2_command_bridge.py     ← /go2_command → Unitree API
│   ├── launch/
│   │   └── voice_control_launch.py
│   ├── config/
│   │   └── params.yaml
│   ├── package.xml
│   └── setup.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## Setup

```bash
# Python dependencies
pip install SpeechRecognition pyaudio

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
# Both nodes together
ros2 launch go2_voice_control voice_control_launch.py

# Or individually
ros2 run go2_voice_control speech_command_node
ros2 run go2_voice_control go2_command_bridge

# Test without hardware — watch published commands
ros2 topic echo /go2_command

# Send command manually
ros2 topic pub /go2_command std_msgs/msg/String "data: 'sit'" --once
```

---

## Configuration

`config/params.yaml`:
```yaml
speech_command_node:
  ros__parameters:
    device_index: null      # null = default mic, set 0/1/2 for specific mic
    energy_threshold: 300
    pause_threshold: 0.8
```

List available microphones:
```python
import speech_recognition as sr
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {name}")
```

---

## Adding More Commands

In `speech_command_node.py` → `process_command()`:
```python
elif any(word in text for word in ["come", "come here"]):
    self.publish_command("come_here")
```

In `go2_command_bridge.py` → `command_callback()`:
```python
elif cmd == "come_here":
    self.send_api(1012)  # replace with correct Unitree API ID
```

---

## Node Graph

```
[Microphone]
     │
     ▼
[speech_command_node]  →  /go2_command (std_msgs/String)
                                  │
                                  ▼
                       [go2_command_bridge]  →  /api/sport/request
                                                        │
                                                        ▼
                                               [GO2 Unitree API]
```

---

## Author

**Yusuf Guenena** | M.S. Robotics Engineering, Wayne State University
[LinkedIn](https://www.linkedin.com/in/yusuf-guenena) · [GitHub](https://github.com/yusufdxb)
