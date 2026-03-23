# GO2 Voice Control Workspace

> Narrow companion repo for voice-command control of the Unitree GO2.

This repository is intentionally smaller in scope than the thesis repo. It focuses on one subsystem: taking spoken commands, converting them into normalized robot commands, and forwarding them to the Unitree motion interface through ROS 2.

## What This Repo Is Good For

- showing a clean speech-command control path on real hardware
- demonstrating ROS 2 topic plumbing for voice-to-action control
- isolating one practical subsystem from the broader GO2 thesis work

## What It Is Not

This is not the main flagship GO2 repository. It is best read as a companion subsystem repo to [GO2 Seeing-Eye Dog](https://github.com/yusufdxb/GO2-seeing-eye-dog), not as a full autonomy project.

## Pipeline

```text
microphone --> speech recognition --> normalized command --> ROS 2 topic --> Unitree command bridge --> GO2 motion API
```

## Nodes

| Node | Role |
|---|---|
| `speech_command_node` | captures speech and publishes normalized commands |
| `go2_command_bridge` | maps commands onto Unitree motion API IDs |

## Recognition Strategy

The public implementation uses an online recognizer with Whisper as a fallback path. That is useful for a demoable control stack, but it should not be oversold as a hardened speech interface for field robotics.

## Supported Commands

| Speech intent | Robot action |
|---|---|
| sit | sit down |
| stand | stand up |
| jump | jump |
| dance | dance behavior |
| shake / paw | shake hands |
| forward | walk forward |
| hello / greet | greeting motion |
| estop / emergency | emergency stop |

## Package Layout

| Path | Purpose |
|---|---|
| `go2_voice_control/go2_voice_control/speech_command_node.py` | speech processing node |
| `go2_voice_control/go2_voice_control/go2_command_bridge.py` | ROS 2 to Unitree command bridge |
| `go2_voice_control/launch/voice_control_launch.py` | launch file |
| `go2_voice_control/config/params.yaml` | runtime configuration |

## Setup

```bash
mkdir -p ~/go2_ws/src
cd ~/go2_ws/src
git clone https://github.com/yusufdxb/go2-simple-workspace.git
cd ~/go2_ws
colcon build --symlink-install
source install/setup.bash
```

Additional Python dependencies are listed in `requirements.txt`.

## Run

```bash
ros2 run go2_voice_control speech_command_node
ros2 run go2_voice_control go2_command_bridge
```

## Why This Repo Helps The Portfolio

This repo is useful when framed correctly:
- it shows a practical voice-control subsystem on a real robot platform
- it is narrower and more honest than pretending to be a complete HRI stack
- it complements the larger GO2 thesis repo instead of competing with it
