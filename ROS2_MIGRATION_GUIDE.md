# ROS2 Humble Migration Guide
## Husky + UR3 + Gripper Mobile Manipulator

---

## Migration Status: ✅ Core Functionality Complete

The mobile manipulator system has been successfully migrated from ROS1 Noetic to ROS2 Humble.

### ✅ Completed Components

1. **Build System** - All packages converted to ament_cmake
2. **ros2_control Integration** - Full controller support for all DOFs
3. **Gazebo Integration** - gazebo_ros2_control plugin configured
4. **Teleoperation** - Joystick and keyboard control ready
5. **Gripper Control** - Open/close functionality implemented
6. **Localization** - robot_localization EKF configured
7. **Launch System** - Python launch files created

---

## System Architecture

### 13 DOF Mobile Manipulator:
- **Mobile Base**: 6-DOF in SE(3) - Differential drive (x, y, θ controllable)
- **UR3 Arm**: 6-DOF robotic manipulator
- **Gripper**: 1-DOF parallel jaw gripper

### Control Stack:
```
┌─────────────────────────────────────────────────┐
│                  User Input                     │
│  (Joystick / Keyboard / ROS2 Topics)           │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │    twist_mux       │  ← Velocity command multiplexer
         └─────────┬──────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
    ▼                             ▼
┌──────────────────┐    ┌─────────────────────────┐
│ diff_drive_ctr   │    │   arm_controller        │
│ (Mobile Base)    │    │   (UR3 - 6 joints)      │
└──────────────────┘    └─────────────────────────┘
                        ┌─────────────────────────┐
                        │ gripper_controllers     │
                        │ (4 joints with PID)     │
                        └─────────────────────────┘
```

---

## Installation

### 1. Install ROS2 Humble Dependencies

```bash
# Core ROS2 Humble packages
sudo apt update
sudo apt install ros-humble-desktop

# Gazebo and ros2_control
sudo apt install ros-humble-gazebo-ros-pkgs
sudo apt install ros-humble-gazebo-ros2-control
sudo apt install ros-humble-ros2-control
sudo apt install ros-humble-ros2-controllers
sudo apt install ros-humble-controller-manager

# Mobile base support
sudo apt install ros-humble-twist-mux
sudo apt install ros-humble-teleop-twist-joy
sudo apt install ros-humble-teleop-twist-keyboard
sudo apt install ros-humble-robot-localization

# State publishing
sudo apt install ros-humble-robot-state-publisher
sudo apt install ros-humble-joint-state-publisher
sudo apt install ros-humble-xacro

# Sensors
sudo apt install ros-humble-realsense2-camera
sudo apt install ros-humble-pointcloud-to-laserscan

# Additional tools
sudo apt install ros-humble-joy
```

### 2. Build the Workspace

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash

# Build packages
colcon build --packages-select husky_ur3_gazebo \
                              husky_ur3_gripper_moveit_config \
                              husky_ur3_navigation \
                              husky_ur3_nav_without_map

# Source the workspace
source install/setup.bash
```

---

## Usage

### 1. Launch Gazebo Simulation

Start the complete mobile manipulator in Gazebo:

```bash
ros2 launch husky_ur3_gazebo gazebo.launch.py
```

**Launch Arguments:**
- `world:=<path>` - Specify world file (default: HRI_lab.world)
- `gui:=true/false` - Launch with/without Gazebo GUI
- `x:=0.0 y:=0.0 z:=0.0 yaw:=0.0` - Initial robot pose
- `laser_enabled:=true/false` - Enable SICK laser scanner
- `camera_h_enabled:=true/false` - Enable RealSense cameras

**Example:**
```bash
# Launch with custom world
ros2 launch husky_ur3_gazebo gazebo.launch.py world:=/path/to/custom.world

# Launch headless (no GUI)
ros2 launch husky_ur3_gazebo gazebo.launch.py gui:=false

# Launch at specific pose
ros2 launch husky_ur3_gazebo gazebo.launch.py x:=1.0 y:=2.0 yaw:=1.57
```

---

### 2. Teleoperate the Mobile Base

#### Option A: Joystick Control

```bash
# Launch joystick teleop (requires connected joystick at /dev/input/js0)
ros2 launch husky_ur3_gazebo teleop_joy.launch.py
```

**Joystick Controls (PS4/Xbox):**
- **L1 (PS4) / LB (Xbox)**: Hold to enable movement
- **Left Stick Vertical**: Forward/backward linear velocity
- **Left Stick Horizontal**: Rotational velocity (turning)

#### Option B: Keyboard Control

```bash
# Launch keyboard teleop
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args \
  --remap /cmd_vel:=/cmd_vel
```

**Keyboard Controls:**
```
Moving around:
   u    i    o
   j    k    l
   m    ,    .

u/o : increase/decrease linear velocity by 10%
j/l : increase/decrease angular velocity by 10%
i : forward
, : backward
j : turn left
l : turn right
k : stop
SPACE : emergency stop
```

#### Option C: Direct Topic Publishing

```bash
# Command constant forward velocity (0.3 m/s)
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.0}}"

# Command rotation (0.5 rad/s)
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

---

### 3. Control the Gripper

#### Gripper Commands:

The gripper uses effort-based position control with PID. Command values range from 0.0 (open) to 1.05 (closed).

**Open Gripper:**
```bash
ros2 topic pub -1 /rh_p12_rn_controller/commands std_msgs/msg/Float64 "{data: 0.0}"
```

**Close Gripper:**
```bash
ros2 topic pub -1 /rh_p12_rn_controller/commands std_msgs/msg/Float64 "{data: 1.05}"
```

**Partially Close (50%):**
```bash
ros2 topic pub -1 /rh_p12_rn_controller/commands std_msgs/msg/Float64 "{data: 0.525}"
```

**Note:** The gripper republisher node automatically coordinates all 4 gripper joints when you command the main joint.

---

### 4. Control the UR3 Arm

The UR3 arm uses a `JointTrajectoryController` and accepts trajectory commands via ROS2 actions.

#### Check arm controller status:
```bash
ros2 control list_controllers
```

#### Send joint trajectory (example):
```bash
# Move to home position (all zeros)
ros2 action send_goal /arm_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{
    trajectory: {
      joint_names: [shoulder_pan_joint, shoulder_lift_joint, elbow_joint,
                    wrist_1_joint, wrist_2_joint, wrist_3_joint],
      points: [
        {
          positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
          time_from_start: {sec: 2, nanosec: 0}
        }
      ]
    }
  }"
```

For advanced manipulation, use MoveIt2 (see section below).

---

## Monitoring & Debugging

### Check Active Controllers:
```bash
ros2 control list_controllers
```

**Expected output:**
```
joint_state_broadcaster[joint_state_broadcaster/JointStateBroadcaster] active
diff_drive_controller[diff_drive_controller/DiffDriveController] active
arm_controller[joint_trajectory_controller/JointTrajectoryController] active
rh_p12_rn_controller[effort_controllers/JointEffortController] active
rh_r2_controller[effort_controllers/JointEffortController] active
rh_l1_controller[effort_controllers/JointEffortController] active
rh_l2_controller[effort_controllers/JointEffortController] active
```

### View Joint States:
```bash
ros2 topic echo /joint_states
```

### View Odometry:
```bash
# Raw wheel odometry
ros2 topic echo /diff_drive_controller/odom

# Fused odometry (EKF with IMU)
ros2 topic echo /odometry/filtered
```

### View TF Tree:
```bash
ros2 run tf2_tools view_frames
```

### Monitor Topics:
```bash
# List all topics
ros2 topic list

# Check cmd_vel
ros2 topic echo /cmd_vel

# Check twist_mux output
ros2 topic echo /diff_drive_controller/cmd_vel_unstamped
```

---

## Coordinate Control: Mobile Base + Arm

You can simultaneously control the base and arm:

**Terminal 1: Move the base**
```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.0}}"
```

**Terminal 2: Move the arm**
```bash
ros2 action send_goal /arm_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{ trajectory: { joint_names: [shoulder_pan_joint, shoulder_lift_joint, elbow_joint, wrist_1_joint, wrist_2_joint, wrist_3_joint], points: [{ positions: [0.5, -0.5, 1.0, 0.0, 0.0, 0.0], time_from_start: {sec: 3} }] } }"
```

**Terminal 3: Control the gripper**
```bash
ros2 topic pub -1 /rh_p12_rn_controller/commands std_msgs/msg/Float64 "{data: 1.05}"
```

---

## Available Worlds

The package includes several Gazebo worlds:

- `HRI_lab.world` - Default lab environment
- `HRI_MAP.world` - Mapped environment for navigation
- `clearpath_playpen.world` - Clearpath testing arena
- `empty.world` - Empty world for testing
- `test_world.world` - Custom test environment

**Launch with specific world:**
```bash
ros2 launch husky_ur3_gazebo gazebo.launch.py \
  world:=$(ros2 pkg prefix husky_ur3_gazebo)/share/husky_ur3_gazebo/worlds/clearpath_playpen.world
```

---

## Troubleshooting

### Controllers not spawning:
```bash
# Check controller manager
ros2 control list_controllers

# Manually spawn controller
ros2 run controller_manager spawner diff_drive_controller
```

### Gripper not responding:
```bash
# Check gripper publisher node is running
ros2 node list | grep gripper

# Restart gripper node
ros2 run husky_ur3_gazebo gazebo_rh_pub
```

### Gazebo crashes:
```bash
# Clear Gazebo cache
rm -rf ~/.gazebo/

# Check system resources
htop
```

### Robot falls through ground:
- Ensure world file is loaded correctly
- Check URDF collision geometries
- Verify Gazebo physics parameters

---

## Next Steps

### 1. MoveIt2 Integration (Planned)

MoveIt2 configuration will enable:
- Motion planning for the UR3 arm
- Collision avoidance
- Inverse kinematics solving
- Grasp planning
- Pick and place operations

**Usage (when available):**
```bash
ros2 launch husky_ur3_gripper_moveit_config demo.launch.py
```

### 2. Nav2 Navigation (Planned)

Nav2 integration will provide:
- Autonomous navigation
- Dynamic path planning
- Obstacle avoidance
- Map-based localization

**Usage (when available):**
```bash
ros2 launch husky_ur3_navigation navigation.launch.py
```

---

## Key Differences from ROS1

| Feature | ROS1 Noetic | ROS2 Humble |
|---------|-------------|-------------|
| **Controllers** | `joint_state_controller` | `joint_state_broadcaster` |
| **Diff Drive** | `husky_velocity_controller` | `diff_drive_controller` |
| **Control Plugin** | `libgazebo_ros_control.so` | `libgazebo_ros2_control.so` |
| **Launch Files** | XML `.launch` | Python `.launch.py` |
| **Topic Echo** | `rostopic echo` | `ros2 topic echo` |
| **Node List** | `rosnode list` | `ros2 node list` |
| **Parameters** | Parameter server | Per-node parameters |
| **Actions** | `actionlib` | `rclpy.action` / `rclcpp.action` |

---

## Quick Reference Commands

```bash
# Build workspace
colcon build

# Source workspace
source install/setup.bash

# Launch simulation
ros2 launch husky_ur3_gazebo gazebo.launch.py

# Teleop keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Open gripper
ros2 topic pub -1 /rh_p12_rn_controller/commands std_msgs/msg/Float64 "{data: 0.0}"

# Close gripper
ros2 topic pub -1 /rh_p12_rn_controller/commands std_msgs/msg/Float64 "{data: 1.05}"

# List controllers
ros2 control list_controllers

# View topics
ros2 topic list

# Echo joint states
ros2 topic echo /joint_states
```

---

## Architecture Summary

```
ROS2 Humble Mobile Manipulator System
├── husky_ur3_gazebo/
│   ├── urdf/
│   │   ├── husky_ur3_gripper.urdf.xacro  (Main robot description)
│   │   ├── ros2_control.xacro            (Controller interfaces)
│   │   └── common.gazebo.xacro           (Gazebo plugins)
│   ├── config/
│   │   ├── control.yaml                  (Controller config)
│   │   ├── twist_mux.yaml               (Velocity multiplexing)
│   │   └── localization.yaml            (EKF configuration)
│   ├── launch/
│   │   ├── gazebo.launch.py             (Main launcher)
│   │   ├── spawn_robot.launch.py        (Robot + controllers)
│   │   └── teleop_joy.launch.py         (Joystick teleop)
│   └── src/
│       └── gazebo_rh_pub.cpp            (Gripper coordinator)
├── husky_ur3_gripper_moveit_config/     (MoveIt2 - TODO)
├── husky_ur3_navigation/                (Nav2 - TODO)
└── husky_ur3_nav_without_map/           (SLAM - TODO)
```

---

## Support

For issues, questions, or contributions:
- Check existing ROS2 Humble documentation
- Review ros2_control tutorials
- Consult Nav2 documentation for navigation
- MoveIt2 tutorials for manipulation

---

**Migration completed:** January 2025
**Target Platform:** ROS2 Humble on Ubuntu 22.04
**Tested with:** Gazebo 11.x, ros2_control, ros2_controllers
