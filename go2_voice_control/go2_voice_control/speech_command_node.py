#!/usr/bin/env python3
"""
GO2 Speech Command Node
=======================
Listens to the microphone, transcribes speech using Google Speech
Recognition, and publishes normalized commands to /go2_command.

Optionally falls back to OpenAI Whisper for offline recognition
(set use_whisper:=true in params.yaml).

Published topic:  /go2_command  (std_msgs/String)

Supported commands:
  "sit" / "seat" / "set"      → sit
  "stand" / "stan"            → stand
  "hello"                     → hello
  "estop" / "emergency"       → estop

Author: Yusuf Guenena
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import speech_recognition as sr


class SpeechCommandNode(Node):
    def __init__(self):
        super().__init__('speech_command_node')

        # ── Parameters ────────────────────────────────────────
        self.declare_parameter('device_index',    -1)     # -1 = system default
        self.declare_parameter('energy_threshold', 300)
        self.declare_parameter('pause_threshold',  0.8)
        self.declare_parameter('use_whisper',      False)
        self.declare_parameter('whisper_model',    'base.en')

        device_idx       = self.get_parameter('device_index').value
        energy_threshold = self.get_parameter('energy_threshold').value
        pause_threshold  = self.get_parameter('pause_threshold').value
        self.use_whisper = self.get_parameter('use_whisper').value

        # ── ROS Publisher ─────────────────────────────────────
        self.publisher = self.create_publisher(String, '/go2_command', 10)

        # ── Speech Recognition Setup ──────────────────────────
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold   = energy_threshold
        self.recognizer.pause_threshold    = pause_threshold
        self.recognizer.dynamic_energy_threshold = True

        # Microphone — device_index=-1 means system default
        mic_index = None if device_idx < 0 else device_idx
        self.mic  = sr.Microphone(device_index=mic_index)

        # ── Optional Whisper fallback ─────────────────────────
        self.whisper_model = None
        if self.use_whisper:
            try:
                import whisper
                model_name = self.get_parameter('whisper_model').value
                self.get_logger().info(f'Loading Whisper model: {model_name}')
                self.whisper_model = whisper.load_model(model_name)
                self.get_logger().info('Whisper model loaded.')
            except ImportError:
                self.get_logger().warn(
                    'use_whisper=True but openai-whisper is not installed. '
                    'Falling back to Google SR only. '
                    'Install with: pip install openai-whisper'
                )

        self.get_logger().info('Speech Command Node ready.')
        self.listen_loop()

    # ── Main listen loop ──────────────────────────────────────

    def listen_loop(self):
        while rclpy.ok():
            try:
                with self.mic as source:
                    self.get_logger().info('Listening...')
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self.recognizer.listen(source)

                text = self._transcribe(audio)
                if text:
                    self.get_logger().info(f'Heard: {text}')
                    self.process_command(text)

            except sr.UnknownValueError:
                self.get_logger().info('Could not understand audio')
            except sr.RequestError as e:
                self.get_logger().error(f'Speech API error: {e}')
            except Exception as e:
                self.get_logger().error(f'Unexpected error: {e}')

    # ── Transcription ─────────────────────────────────────────

    def _transcribe(self, audio) -> str:
        """
        Tries Google Speech Recognition first.
        Falls back to Whisper if Google fails and use_whisper=True.
        Returns lowercase string or empty string on failure.
        """
        try:
            return self.recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            if self.whisper_model is not None:
                return self._transcribe_whisper(audio)
            raise
        except sr.RequestError:
            if self.whisper_model is not None:
                self.get_logger().warn('Google SR unavailable — using Whisper')
                return self._transcribe_whisper(audio)
            raise

    def _transcribe_whisper(self, audio) -> str:
        import numpy as np
        import io
        import soundfile as sf

        wav_bytes = audio.get_wav_data()
        audio_np, _ = sf.read(io.BytesIO(wav_bytes), dtype='float32')
        result = self.whisper_model.transcribe(audio_np, language='en', fp16=False)
        return result['text'].strip().lower()

    # ── Command processor ─────────────────────────────────────

    def process_command(self, text: str):
        # SIT
        if any(word in text for word in ["sit", "seat", "set"]):
            self.publish_command("sit")
        # STAND
        elif any(word in text for word in ["stand", "stan"]):
            self.publish_command("stand")
        # HELLO
        elif "hello" in text:
            self.publish_command("hello")
        # EMERGENCY STOP
        elif any(word in text for word in ["estop", "emergency stop", "emergency"]):
            self.publish_command("estop")
        # ── Add more commands here ──
        # elif any(word in text for word in ["come", "come here"]):
        #     self.publish_command("come_here")
        else:
            self.get_logger().info(f'No matching command for: "{text}"')

    # ── Publisher ─────────────────────────────────────────────

    def publish_command(self, command: str):
        msg = String()
        msg.data = command
        self.publisher.publish(msg)
        self.get_logger().info(f'Sent command: {command}')


# ── Entry point ───────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = SpeechCommandNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
