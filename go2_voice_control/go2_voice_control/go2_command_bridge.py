#!/usr/bin/env python3
"""
GO2 Command Bridge
==================
Subscribes to /go2_command (std_msgs/String) and maps each
command string to the corresponding Unitree Sport API ID,
publishing to /api/sport/request.

Subscribed topic:  /go2_command       (std_msgs/String)
Published topic:   /api/sport/request (unitree_api/Request)

Unitree API IDs used:
  1001 — Emergency stop
  1009 — Sit
  1010 — Stand up

Author: Yusuf Guenena
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from unitree_api.msg import Request


# ── Unitree Sport API ID reference ──────────────────────────
# Full list: https://support.unitree.com/home/en/developer/sports_services
API_IDS = {
    'estop':  1001,   # Emergency stop (StopMove)
    'sit':    1009,   # StandDown
    'stand':  1010,   # StandUp
    # Add more mappings here as needed:
    # 'hello':   1016,
    # 'come_here': 1012,
}


class GO2CommandBridge(Node):
    def __init__(self):
        super().__init__('go2_command_bridge')

        # Subscribe to simple command topic
        self.sub = self.create_subscription(
            String,
            '/go2_command',
            self.command_callback,
            10
        )

        # Publish to Unitree motion API
        self.pub = self.create_publisher(
            Request,
            '/api/sport/request',
            10
        )

        self.get_logger().info('GO2 Command Bridge ready.')
        self.get_logger().info(
            f'Mapped commands: {list(API_IDS.keys())}'
        )

    # ── API helper ────────────────────────────────────────────

    def send_api(self, api_id: int):
        """Constructs and publishes a Unitree API Request message."""
        msg = Request()
        msg.header.identity.id      = 0
        msg.header.identity.api_id  = api_id
        msg.header.lease.id         = 0
        msg.header.policy.priority  = 0
        msg.header.policy.noreply   = False
        msg.parameter = ""
        msg.binary    = []
        self.pub.publish(msg)

    # ── Command callback ──────────────────────────────────────

    def command_callback(self, msg: String):
        cmd = msg.data.lower().strip()
        self.get_logger().info(f'Received command: {cmd}')

        if cmd in API_IDS:
            api_id = API_IDS[cmd]
            self.get_logger().info(
                f'Executing "{cmd}" → API ID {api_id}'
            )
            self.send_api(api_id)
        elif cmd == 'hello':
            # Hello is a behavior — handle separately or map to an ID
            self.get_logger().info('Hello! (no API ID mapped — add one in API_IDS)')
        else:
            self.get_logger().warn(
                f'Unknown command: "{cmd}" — add it to API_IDS in go2_command_bridge.py'
            )


# ── Entry point ───────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = GO2CommandBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
