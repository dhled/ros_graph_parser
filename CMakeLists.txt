cmake_minimum_required(VERSION 2.8.3)
project(ros_graph_parser)

find_package(catkin REQUIRED COMPONENTS
)

catkin_python_setup()

# add_service_files(
#   FILES
#   TestService.srv
# )

# add_action_files(DIRECTORY action  
# 	FILES 
# 	TestAction.action
# )

# generate_messages(
#   DEPENDENCIES
#   actionlib_msgs
#   std_msgs
# )


# catkin_package(
#   CATKIN_DEPENDS actionlib actionlib_msgs message_runtime rospy std_msgs
# )

# install(DIRECTORY resources launch
#   DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
# )

# catkin_install_python(PROGRAMS scripts/nodes/actionrelay_node
#                                scripts/nodes/servicerelay_node
#                                scripts/nodes/topicrelay_node

#   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
# )

# if(CATKIN_ENABLE_TESTING)
#   find_package(rostest REQUIRED)
#   add_rostest(test/test_relay.test)
# endif()
