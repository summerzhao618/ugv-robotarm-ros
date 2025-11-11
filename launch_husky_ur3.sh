#!/bin/bash
# ROS 2 Husky + UR3 + Gripper Launch Script
# ROS2 Humble Migration - Updated for Current Status
# Date: 2025-11-11
# Migration Status: 98% Complete (Visualization Working, Control System Blocked)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ROS 2 workspace paths
ROS_DISTRO="humble"
ROS_WS="$HOME/humble_ws"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  ROS2 Husky + UR3 + Gripper Launcher  ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo -e "${YELLOW}Note: Controllers are not yet functional due to gazebo_ros2_control issue${NC}"
echo -e "${YELLOW}Currently: Visualization-only mode (Gazebo + RViz2)${NC}"
echo ""

# Check and deactivate conda if active
if [ ! -z "$CONDA_PREFIX" ]; then
    echo -e "${YELLOW}Deactivating conda environment...${NC}"
    conda deactivate 2>/dev/null || true
fi

# Check if workspace exists
if [ ! -d "$ROS_WS" ]; then
    echo -e "${RED}ERROR: Workspace not found at $ROS_WS${NC}"
    echo -e "${YELLOW}Please update ROS_WS variable in this script to match your workspace location${NC}"
    exit 1
fi

# STEP 1: Opens up a terminal window 1 - Gazebo + RViz2 Simulation
echo -e "${GREEN}Step 1: Launching Gazebo + RViz2 visualization with Husky + UR3 + Gripper...${NC}"
gnome-terminal -- bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && \
    source ${ROS_WS}/install/setup.bash && \
    export GAZEBO_MODEL_PATH=\$GAZEBO_MODEL_PATH:\$(ros2 pkg prefix husky_ur3_gazebo)/share && \
    echo -e '${GREEN}Starting Gazebo + RViz2...${NC}' && \
    echo -e '${YELLOW}This will spawn:${NC}' && \
    echo -e '  - Gazebo simulation' && \
    echo -e '  - Robot state publisher' && \
    echo -e '  - Joint state publisher' && \
    echo -e '  - RViz2 visualization' && \
    echo '' && \
    ros2 launch husky_ur3_gazebo test_urdf.launch.py; \
    exec bash"
sleep 8

# STEP 2: Opens a monitoring terminal - Check topics and system state
echo -e "${GREEN}Step 2: Opening monitoring terminal...${NC}"
gnome-terminal -- bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && \
    source ${ROS_WS}/install/setup.bash && \
    echo -e '${BLUE}=========================================${NC}' && \
    echo -e '${BLUE}  System Monitoring Terminal${NC}' && \
    echo -e '${BLUE}=========================================${NC}' && \
    echo '' && \
    echo 'Waiting for system to initialize...' && sleep 5 && \
    echo '' && \
    echo -e '${GREEN}=== Active Topics ===${NC}' && \
    ros2 topic list && \
    echo '' && \
    echo -e '${GREEN}=== Active Nodes ===${NC}' && \
    ros2 node list && \
    echo '' && \
    echo -e '${GREEN}=== Joint States (should show all robot joints) ===${NC}' && \
    timeout 3 ros2 topic echo /joint_states --once && \
    echo '' && \
    echo -e '${YELLOW}=== TF Tree Check ===${NC}' && \
    echo 'Generating TF tree visualization...' && \
    ros2 run tf2_tools view_frames && \
    echo -e '${GREEN}TF tree saved to frames.pdf${NC}' && \
    echo '' && \
    echo -e '${YELLOW}=== Available Commands ===${NC}' && \
    echo 'Monitor joint states:  ros2 topic echo /joint_states' && \
    echo 'Monitor TF:            ros2 run tf2_ros tf2_echo base_link wrist_3_link' && \
    echo 'List controllers:      ros2 control list_controllers' && \
    echo '' && \
    echo 'Press Enter to continue...' && \
    read && \
    exec bash"

# STEP 3: Teleoperation - DISABLED (Controllers not working yet)
echo -e "${RED}Step 3: Teleoperation DISABLED - ros2_control not functional yet${NC}"
echo -e "${YELLOW}  Reason: gazebo_ros2_control parameter parsing error prevents controller loading${NC}"
echo -e "${YELLOW}  Error: 'Couldn't parse parameter override rule: --param robot_description:=...'${NC}"
# gnome-terminal -- bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && \
#     source ${ROS_WS}/install/setup.bash && \
#     ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/husky_velocity_controller/cmd_vel_unstamped; \
#     exec bash"
# sleep 3

# STEP 4: Gripper Controller - DISABLED (Controllers not working yet)
echo -e "${RED}Step 4: Gripper Controller DISABLED - ros2_control not functional yet${NC}"
# gnome-terminal -- bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && \
#     source ${ROS_WS}/install/setup.bash && \
#     ros2 run husky_ur3_gazebo gripper_controller; \
#     exec bash"
# sleep 3

# STEP 5: ROS 2 Bag Recording (optional)
echo -e "${YELLOW}Step 5: Recording setup (uncomment in script to enable)...${NC}"
# gnome-terminal -- bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && \
#     source ${ROS_WS}/install/setup.bash && \
#     ros2 bag record -a -o husky_ur3_recording --max-bag-duration 30; \
#     exec bash"
# sleep 3

# STEP 6: MoveIt2 - NOT YET MIGRATED
echo -e "${RED}Step 6: MoveIt2 NOT YET MIGRATED to ROS2${NC}"
echo -e "${YELLOW}  Package husky_ur3_gripper_moveit_config needs ROS2 migration${NC}"
echo -e "${YELLOW}  RViz shows MoveIt errors looking for robot_description_semantic (SRDF)${NC}"
# gnome-terminal -- bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && \
#     source ${ROS_WS}/install/setup.bash && \
#     ros2 launch husky_ur3_gripper_moveit_config demo.launch.py; \
#     exec bash"
# sleep 3

# STEP 7: Navigation Stack - NOT YET TESTED
echo -e "${YELLOW}Step 7: Navigation stack (not yet configured)...${NC}"
# gnome-terminal -- bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && \
#     source ${ROS_WS}/install/setup.bash && \
#     ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true; \
#     exec bash"
# sleep 3

echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}  Launch sequence completed!${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo -e "${YELLOW}Terminal Windows Opened:${NC}"
echo "  1. Gazebo + RViz2 Visualization"
echo "  2. Monitoring Terminal"
echo ""
echo -e "${GREEN}Current System Status (98% Migration Complete):${NC}"
echo -e "  ${GREEN}✓${NC} Robot spawns in Gazebo with all meshes"
echo -e "  ${GREEN}✓${NC} RViz2 shows complete robot (Husky + UR3 + Gripper)"
echo -e "  ${GREEN}✓${NC} All 54 robot segments with TF transforms"
echo -e "  ${GREEN}✓${NC} Joint state publisher providing joint states"
echo -e "  ${RED}✗${NC} Controllers NOT loading (gazebo_ros2_control parameter parsing error)"
echo -e "  ${RED}✗${NC} Cannot control robot yet"
echo -e "  ${YELLOW}○${NC} MoveIt2 not yet migrated"
echo ""
echo -e "${YELLOW}Known Issues:${NC}"
echo "  • gazebo_ros2_control parameter parsing error (blocking controller loading)"
echo "  • MoveIt2 errors in RViz (non-critical, looking for SRDF file)"
echo "  • Sensor plugins using ROS1 libraries (optional migration needed)"
echo "  • Camera meshes missing (visual only, no functional impact)"
echo "  • DDS buffer warnings (harmless, due to large robot_description)"
echo ""
echo -e "${YELLOW}Available Commands (Once Controllers Work):${NC}"
echo "  # Check controller manager status"
echo "  ros2 control list_controllers"
echo ""
echo "  # Manual controller loading (when ros2_control is fixed)"
echo "  ros2 control load_controller joint_state_broadcaster"
echo "  ros2 control load_controller diff_drive_controller"
echo "  ros2 control load_controller arm_controller"
echo ""
echo "  # Teleoperation (when diff_drive_controller works)"
echo "  ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/diff_drive_controller/cmd_vel_unstamped"
echo ""
echo "  # Gripper control (when controllers work)"
echo "  ros2 topic pub -1 /rh_p12_rn_l1_effort_controller/commands std_msgs/msg/Float64MultiArray '{data: [0.0]}'   # Open"
echo "  ros2 topic pub -1 /rh_p12_rn_l1_effort_controller/commands std_msgs/msg/Float64MultiArray '{data: [1.0]}'   # Close"
echo ""
echo -e "${YELLOW}To record rosbag:${NC}"
echo "  ros2 bag record -a -o husky_ur3_data --max-bag-duration 30"
echo ""
echo -e "${YELLOW}Debug ros2_control issue:${NC}"
echo "  ros2 topic list | grep -E '(controller|control)'"
echo "  ros2 service list | grep -E '(controller|control)'"
echo "  ros2 param list | grep gazebo_ros2_control"
echo ""
echo -e "${GREEN}For detailed troubleshooting: $ROS_WS/src/ugv-robotarm-ros/TROUBLESHOOTING_STATUS.md${NC}"
echo -e "${GREEN}Script completed. Check terminal windows for any errors.${NC}"
