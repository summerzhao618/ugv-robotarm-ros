#!/bin/bash
# Minimal ROS2 Husky + UR3 + Gripper Visualization Launcher
# Quick launch for current working state (98% migration)
# Date: 2025-11-11

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
ROS_DISTRO="humble"
ROS_WS="$HOME/humble_ws"

echo -e "${GREEN}Starting Husky + UR3 + Gripper Visualization...${NC}"
echo -e "${YELLOW}Note: Controllers not yet functional (visualization only)${NC}"
echo ""

# Source ROS2
source /opt/ros/${ROS_DISTRO}/setup.bash
source ${ROS_WS}/install/setup.bash

# Set Gazebo model path for meshes
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$(ros2 pkg prefix husky_ur3_gazebo)/share

# Launch
echo -e "${GREEN}Launching Gazebo + RViz2...${NC}"
ros2 launch husky_ur3_gazebo test_urdf.launch.py
