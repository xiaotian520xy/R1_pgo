import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point
from tf2_ros import Buffer, TransformListener
from tf2_ros import TransformException
import threading


class CorrectedOdomPublisher(Node):
    def __init__(self):
        super().__init__('corrected_odom_publisher')

        # TF 相关
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # 发布器
        self.pub = self.create_publisher(Odometry, '/tf_odometry', 10)

        # 线程锁，防止并发访问
        self.lock = threading.Lock()

        # 存储最新的变换
        self.latest_transform = None

        # 使用一个较慢的定时器发布
        self.timer = self.create_timer(0.1, self.publish_callback)  # 10Hz

        # 使用一个较快的定时器获取 TF
        self.tf_timer = self.create_timer(
            0.05, self.tf_update_callback)  # 20Hz

        self.get_logger().info('Corrected Odom Publisher started')

    def tf_update_callback(self):
        """快速更新 TF 变换"""
        try:
            # 获取最新变换（不指定时间）
            transform = self.tf_buffer.lookup_transform(
                'lidar',
                'body',
                rclpy.time.Time(seconds=0, nanoseconds=0)  # 获取最新
            )

            with self.lock:
                self.latest_transform = transform

        except TransformException as e:
            pass  # 静默处理，避免日志刷屏
        except Exception as e:
            self.get_logger().debug(f'TF error: {str(e)}')

    def publish_callback(self):
        """发布回调，频率较低"""
        with self.lock:
            if self.latest_transform is None:
                return

            transform = self.latest_transform

            # 检查时间戳是否合理（避免发布太旧的数据）
            transform_time = transform.header.stamp.sec + \
                transform.header.stamp.nanosec * 1e-9
            now_time = self.get_clock().now().nanoseconds * 1e-9

            # 如果数据太旧（超过0.5秒），跳过
            if now_time - transform_time > 0.5:
                self.get_logger().warn(
                    f'Skipping old transform: {now_time - transform_time:.2f}s old')
                return

            # 创建里程计消息
            odom = Odometry()
            odom.header.stamp = transform.header.stamp
            odom.header.frame_id = 'lidar'
            odom.child_frame_id = 'body'

            odom.pose.pose.position = Point(
                x=transform.transform.translation.x,
                y=transform.transform.translation.y,
                z=transform.transform.translation.z
            )
            odom.pose.pose.orientation = transform.transform.rotation

            self.pub.publish(odom)

def main(args=None):
    rclpy.init(args=args)
    node = CorrectedOdomPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
