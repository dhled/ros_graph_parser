# ros_graph_parser
A tool to parse the ROS Graph and dump the result into different styles. The goal of this package is to provide a list of node and their currently available interfaces. 

## How To Use

###YAML
This create a snapshot in a yaml format then finish.

rosrun ros_graph_parser yaml_snaphot -f *file_name.yaml*

Parameter:
* *file_name.yaml*: the name of the file. It will be saved in the resource folder of the ros_graph_parser package (ensure that you have the permission).

###ROS Node
This is meant to be runned continually. This node provides a service to be used to acquire a YAML dumped format scan of the ROS Graph
rosrun ros_graph_parser ros_node

This provides a service "/scan_ros_graph" of type "ros_graph_parser.Scan".
The request is empty and the response contain a boolean, a information for error and the dump of the yaml format in case of success.

###JAVA
This create a java format meant to be used with the [ros_model](https://github.com/ipa320/ros-model).

rosrun ros_graph_parser java_snapshot  *ros_model_file* *ros_system_file* *system_name* *package_name*
* *ros_model_file*: name of the file to save the ROS Model
* *ros_system_file*: name of the file to save the ROS System
* *system_name*: name of the system (check ros_model syntax)
* *package_name*" name of the package (check ros_model syntax)

All the files will be saved in the resources folder of the ros_graph_parser.
