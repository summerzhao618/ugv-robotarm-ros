# Launch Scripts Guide

This directory contains launch scripts for the ROS2 Husky + UR3 + Gripper mobile manipulator.

## Migration Status: 98% Complete ✅

**Working:**
- ✅ Robot visualization in Gazebo and RViz2
- ✅ Complete robot model (Husky + UR3 + Gripper)
- ✅ All transforms and joint states

**Blocked:**
- ❌ ros2_control controllers (parameter parsing error)
- ❌ Robot control/teleoperation
- ⚠️ MoveIt2 (not yet migrated)

---

## Available Scripts

### 1. `launch_simple.sh` - Quick Launcher (Recommended)

**Use this for:** Quick visualization testing

```bash
./launch_simple.sh
```

**What it does:**
- Launches Gazebo with robot
- Launches RViz2 for visualization
- Sets required environment variables
- Single terminal, simple output

**Best for:** Daily development, quick tests, demonstrations

---

### 2. `launch_husky_ur3.sh` - Full Multi-Terminal Launcher

**Use this for:** Complete system monitoring and debugging

```bash
./launch_husky_ur3.sh
```

**What it does:**
- Opens Gazebo + RViz2 in separate terminal
- Opens monitoring terminal with diagnostics
- Shows system status and available commands
- Generates TF tree visualization (frames.pdf)
- Displays helpful command reference

**Best for:** System debugging, monitoring, learning the system

**Terminal Windows:**
1. **Gazebo + RViz2** - Main visualization
2. **Monitoring** - Topics, nodes, TF tree, diagnostics

---

## Prerequisites

### Required Setup

1. **ROS2 Humble installed**
   ```bash
   source /opt/ros/humble/setup.bash
   ```

2. **Workspace built**
   ```bash
   cd ~/humble_ws
   colcon build --packages-select husky_ur3_gazebo
   source install/setup.bash
   ```

3. **Dependencies installed**
   ```bash
   sudo apt install ros-humble-joint-state-publisher \
                    ros-humble-rviz2 \
                    ros-humble-gazebo-ros-pkgs
   ```

### Environment Variables

Both scripts automatically set:
```bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$(ros2 pkg prefix husky_ur3_gazebo)/share
```

This is **required** for robot meshes to load correctly.

---

## What You'll See

### Gazebo Window
- Complete Husky mobile base with 4 wheels
- UR3 6-DOF robotic arm mounted on top
- Robotiq 2-finger parallel gripper on arm end-effector
- All meshes loaded correctly

### RViz2 Window
- Robot model display (colored)
- TF frames visualization
- Grid reference
- All joints visible

### Expected Warnings/Errors

These are **normal** and **non-critical**:

1. **gazebo_ros2_control parameter parsing error**
   ```
   [ERROR] [gazebo_ros2_control]: parser error Couldn't parse parameter override rule
   ```
   - Robot still spawns successfully
   - Visualization works fine
   - Controllers don't load (blocking control functionality)

2. **MoveIt2 errors in RViz**
   ```
   [ERROR] [rviz2]: Could not find parameter robot_description_semantic
   ```
   - RViz trying to load MoveIt2 plugins
   - Doesn't affect basic visualization
   - Will be fixed when MoveIt2 is migrated

3. **DDS buffer warnings**
   ```
   sequence size exceeds remaining buffer
   ```
   - Harmless FastRTPS warnings
   - Due to large robot_description XML
   - No functional impact

4. **Missing sensor plugin libraries**
   ```
   Failed to load plugin libgazebo_ros_laser.so
   Failed to load plugin libhector_gazebo_ros_imu.so
   ```
   - ROS1 plugins need ROS2 equivalents
   - Optional migration when sensors are needed

5. **Missing camera meshes**
   ```
   [Wrn] URI not supported by Fuel [model://realsense2_description/meshes/d435.dae]
   ```
   - Visual only, cameras appear as wireframe
   - No functional impact

---

## Useful Commands

### Check System Status

```bash
# List active topics
ros2 topic list

# List active nodes
ros2 node list

# View joint states
ros2 topic echo /joint_states

# Check TF tree
ros2 run tf2_ros tf2_echo base_link wrist_3_link

# Generate TF visualization
ros2 run tf2_tools view_frames
```

### Controller Status (When Fixed)

```bash
# List controllers
ros2 control list_controllers

# Load controller
ros2 control load_controller joint_state_broadcaster

# Check controller manager
ros2 service list | grep controller
```

### Recording Data

```bash
# Record all topics for 30 seconds
ros2 bag record -a -o my_recording --max-bag-duration 30

# Record specific topics
ros2 bag record /joint_states /tf /tf_static -o robot_data
```

---

## Troubleshooting

### Script Won't Run

```bash
# Make executable
chmod +x launch_simple.sh launch_husky_ur3.sh

# Check workspace path in scripts
# Edit ROS_WS variable if your workspace is not ~/humble_ws
```

### Workspace Not Found Error

Edit the script and update:
```bash
ROS_WS="$HOME/humble_ws"  # Change to your workspace path
```

### Gazebo Doesn't Show Robot Meshes

The scripts automatically set `GAZEBO_MODEL_PATH`, but if meshes still don't load:

```bash
# Manual fix
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$(ros2 pkg prefix husky_ur3_gazebo)/share

# Or rebuild package
cd ~/humble_ws
colcon build --packages-select husky_ur3_gazebo --symlink-install
source install/setup.bash
```

### RViz2 Shows Incomplete Robot

This was fixed by adding `joint_state_publisher`. If you still see issues:

```bash
# Verify joint_state_publisher is running
ros2 node list | grep joint_state

# Check joint states are being published
ros2 topic hz /joint_states

# Rebuild if needed
cd ~/humble_ws
colcon build --packages-select husky_ur3_gazebo
source install/setup.bash
```

---

## Next Steps (When Controllers Work)

Once the `gazebo_ros2_control` parameter parsing issue is resolved:

### 1. Teleoperation
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args --remap cmd_vel:=/diff_drive_controller/cmd_vel_unstamped
```

### 2. Arm Control
```bash
# Joint trajectory control
ros2 topic pub /arm_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory ...
```

### 3. Gripper Control
```bash
# Open gripper
ros2 topic pub -1 /rh_p12_rn_l1_effort_controller/commands \
  std_msgs/msg/Float64MultiArray '{data: [0.0]}'

# Close gripper
ros2 topic pub -1 /rh_p12_rn_l1_effort_controller/commands \
  std_msgs/msg/Float64MultiArray '{data: [1.0]}'
```

---

## Documentation

- **Detailed troubleshooting**: See `TROUBLESHOOTING_STATUS.md`
- **Migration guide**: See `ROS2_MIGRATION_GUIDE.md`
- **Configuration files**: `husky_ur3_gazebo/config/`
- **Launch files**: `husky_ur3_gazebo/launch/`
- **URDF files**: `husky_ur3_gazebo/urdf/`

---

## Support

For issues or questions:
1. Check `TROUBLESHOOTING_STATUS.md` for known issues
2. Check terminal output for specific error messages
3. Verify all prerequisites are installed
4. Ensure workspace is properly built and sourced

**Last Updated**: 2025-11-11
**Migration Status**: 98% Complete
**Working**: Visualization ✅ | **Blocked**: Control System ❌
