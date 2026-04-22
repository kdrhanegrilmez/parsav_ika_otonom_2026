cmake_minimum_required(VERSION 3.8)
project(ika_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Install worlds
install(DIRECTORY worlds
  DESTINATION share/${PROJECT_NAME})

# Install models
install(DIRECTORY models
  DESTINATION share/${PROJECT_NAME})

ament_package()
