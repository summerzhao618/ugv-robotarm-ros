cmake_minimum_required(VERSION 3.8)
project(husky_ur3_gazebo)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# Include directories
include_directories(
  ${rclcpp_INCLUDE_DIRS}
  ${std_msgs_INCLUDE_DIRS}
)

# Build gazebo_rh_pub node
add_executable(gazebo_rh_pub src/gazebo_rh_pub.cpp)
ament_target_dependencies(gazebo_rh_pub
  rclcpp
  std_msgs
)

# Install executables
install(TARGETS
  gazebo_rh_pub
  DESTINATION lib/${PROJECT_NAME}
)

# Install directories
install(DIRECTORY
  launch
  config
  urdf
  meshes
  worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
