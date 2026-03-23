#!/usr/bin/env python3
"""
GO2 Command Bridge
==================
Maps /go2_command strings to Unitree Sport API IDs
and publishes to /api/sport/request.

Subscribed topic:  /go2_command       (std_msgs/String)
Published topic:   /api/sport/request (unitree_api/Request)

Author: Yusuf Guenena
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from unitree_api.msg import Request


# ── Unitree Sport API ID map ─────────────────────────────────
# Full reference: https://support.unitree.com/home/en/developer/sports_services
API_IDS = {
    'sit':        1009,   # StandDown
    'stand':      1010,   # StandUp
    'forward':    1008,   # Move forward
    'jump':       1006,   # Jump
    'flip':       1025,   # Backflip
    'dance':      1022,   # Dance 1
    'dance_two':  1023,   # Dance 2
    'shake':      1019,   # Shake hands
    'hello':      1016,   # Greet / hello
    'estop':      1001,   # Emergency stop (StopMove)
}


class GO2CommandBridge(Node):
    def __init__(self):
        super().__init__('go2_command_bridge')

        self.sub = self.create_subscription(
            String,
            '/go2_command',
            self.command_callback,
            10
        )

        self.pub = self.create_publisher(
            Request,
            '/api/sport/request',
            10
        )

        self.get_logger().info('GO2 Command Bridge Ready')
        self.get_logger().info(f'Commands: {list(API_IDS.keys())}')

    # ── API helper ────────────────────────────────────────────

    def send_api(self, api_id: int):
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
        self.get_logger().info(f'Received: {cmd}')

        if cmd in API_IDS:
            api_id = API_IDS[cmd]
            self.get_logger().info(f'Executing "{cmd}" → API ID {api_id}')
            self.send_api(api_id)
        else:
            self.get_logger().warn(
                f'Unknown command: "{cmd}" — add it to API_IDS'
            )


def main(args=None):
    rclpy.init(args=args)
    node = GO2CommandBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
