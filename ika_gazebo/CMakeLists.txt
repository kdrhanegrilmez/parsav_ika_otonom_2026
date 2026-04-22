cmake_minimum_required(VERSION 3.8)
project(ika_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(gazebo_ros REQUIRED)

# Sliding Obstacle Plugin
add_library(sliding_obstacle_plugin SHARED src/sliding_obstacle_plugin.cpp)
target_link_libraries(sliding_obstacle_plugin gazebo_ros::gazebo_ros)

install(TARGETS sliding_obstacle_plugin
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY worlds
  DESTINATION share/${PROJECT_NAME})

ament_package()
