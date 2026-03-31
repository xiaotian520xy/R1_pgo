from setuptools import find_packages, setup
import os
import glob

package_name = 'fyt_pos'
config_files = glob.glob(os.path.join(
    os.path.dirname(__file__), 'config', '*.yaml'))

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', config_files),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='upre',
    maintainer_email='upre@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'tf_listen = fyt_pos.tf_listen:main',
            'radar_position = fyt_pos.radar_position:main',
            'picture = fyt_pos.picture:main',
            'aruco = fyt_pos.aruco:main',
            'path = fyt_pos.path:main',
        ],
    },
)
