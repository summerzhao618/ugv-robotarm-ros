cmake_minimum_required(VERSION 3.8)
project(husky_ur3_gripper_moveit_config)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)

# Install directories
install(DIRECTORY
  launch
  config
  scripts
  DESTINATION share/${PROJECT_NAME}
  PATTERN "setup_assistant.launch*" EXCLUDE
)

ament_package()
