import os
from ament_index_python.packages import get_package_share_directory
import launch
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction,Shutdown
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch.conditions import IfCondition, UnlessCondition

def generate_nodes(context, *, num_trucks, map_name, host):
    nodes = []

    ros_param_file = os.path.join(
            get_package_share_directory('carla-virtual-platoon'), 
            'config', 
            'config.yaml') 

    for i in range(1, int(num_trucks) + 1):
        node = Node(
            package='carla-virtual-platoon',
            executable='main',
            name=f'bridge{i-1}',
            namespace=f'truck{i-1}',
            output='screen',
            parameters=[
                ros_param_file,
                {'host': host}
            ],
            arguments=[
                f'--truck_id={i-1}', 
                f'--map={map_name}'
            ],
            on_exit=launch.actions.Shutdown()  
        )
        nodes.append(node)
    return nodes

# # 긴급 상황 트럭 노드를 생성하는 함수
# def generate_emergency_truck_node(context, map_name, host):
#     ros_param_file = os.path.join(
#                 get_package_share_directory('carla-virtual-platoon'), 
#                 'config', 
#                 'config.yaml') 
    
#     # 새로운 truck_id (예: 100)를 사용
#     emergency_truck_id = 100 

#     node = Node(
#         package='carla-virtual-platoon',
#         executable='main',
#         name=f'emergency_truck_bridge', # 고유한 이름
#         namespace=f'truck_emergency', # 고유한 네임스페이스
#         output='screen',
#         parameters=[
#             ros_param_file,
#             {'host': host}
#         ],
#         arguments=[
#             f'--truck_id={emergency_truck_id}', # 긴급 상황 트럭의 ID 전달
#             f'--map={map_name}'
#         ],
#         on_exit=launch.actions.Shutdown()
#     )
#     return node

def launch_setup(context):
    num_trucks = LaunchConfiguration('NumTrucks').perform(context)
    map_name = LaunchConfiguration('Map').perform(context)  
    host = LaunchConfiguration('Host').perform(context)

    # spawn_emergency_truck = LaunchConfiguration('SpawnEmergencyTruck').perform(context) # <-- 수정 부분
    all_nodes = generate_nodes(context, num_trucks=num_trucks, map_name=map_name, host=host)
    
    # 긴급 상황 트럭 노드 조건부 추가
    # SpawnEmergencyTruck가 '1'일 때만 이 노드를 생성
    emergency_truck_id = 100 # carlalocation.hpp에 정의된 긴급 트럭 ID
    emergency_truck_node = Node(
        package='carla-virtual-platoon',
        executable='main',
        name=f'emergency_truck_bridge', 
        namespace=f'truck_emergency', 
        output='screen',
        parameters=[
            os.path.join(
                get_package_share_directory('carla-virtual-platoon'), 
                'config', 
                'config.yaml'),
            {'host': host}
        ],
        arguments=[
            f'--truck_id={emergency_truck_id}', 
            f'--map={map_name}'
        ],
        on_exit=launch.actions.Shutdown(),
        condition=IfCondition(LaunchConfiguration('SpawnEmergencyTruck')) # <-- 중요: SpawnEmergencyTruck가 '1'이면 스폰
    )
    all_nodes.append(emergency_truck_node)

    return all_nodes


def generate_launch_description():

    declare_num_trucks = DeclareLaunchArgument(
        'NumTrucks',
        default_value='1',
        description='Number of trucks'
    )

    declare_map_name = DeclareLaunchArgument(
        'Map',
        default_value='IHP',
        description='MapName'
    )

    declare_host = DeclareLaunchArgument(
        'Host',
        default_value='localhost',
        description='CARLA host address'
    )

    declare_spawn_emergency_truck = DeclareLaunchArgument(
        'SpawnEmergencyTruck',
        default_value='0', # 기본값은 스폰하지 않음 (0)
        description='Set to 1 to spawn an emergency truck, 0 otherwise.'
    )

    return LaunchDescription([
        declare_num_trucks,
        declare_map_name,
        declare_host,
        declare_spawn_emergency_truck,
        OpaqueFunction(function=launch_setup)
    ])
