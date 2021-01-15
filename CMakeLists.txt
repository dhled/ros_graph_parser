cmake_minimum_required(VERSION 2.8.3)
project(ros_graph_parser)

find_package(catkin REQUIRED COMPONENTS
    message_generation
)

catkin_python_setup()

add_service_files(
   FILES
   GetROSModel.srv
   GetROSSystemModel.srv
)

generate_messages()

catkin_package(
   CATKIN_DEPENDS message_runtime
)

catkin_install_python(PROGRAMS scripts/ros_node
                                scripts/print_snapshot
                                scripts/java_snapshot
                                scripts/yaml_snapshot

   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

# if(CATKIN_ENABLE_TESTING)
#   find_package(rostest REQUIRED)
#   add_rostest(test/test_relay.test)
# endif()
