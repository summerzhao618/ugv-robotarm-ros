cmake_minimum_required(VERSION 3.8)
project(husky_ur3_navigation)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)

# Install directories
install(DIRECTORY
  launch
  param
  config
  map
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
