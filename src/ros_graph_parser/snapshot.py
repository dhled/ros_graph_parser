#!/usr/bin/env python

import rosgraph
import rosparam
import rosservice
import ros_graph_parser.core_class as rg
import yaml

BLACK_LIST_PARAM = ['/rosdistro', '/rosversion', '/run_id']
BLACK_LIST_TOPIC = ["/tf", "/tf_static", "/rosout", "/clock"]
BLACK_LIST_SERV = ["/set_logger_level", "/get_loggers"]
BLACK_LIST_NODE = ["/rosout", "/head_cam",
                   "/graph_monitor", "/ros_graph_parser_node"]

ACTION_FILTER = ['cancel', 'goal', 'status', 'result', 'feedback']


def check_black_list(name, black_list):
    for bl_ in black_list:
        if bl_ in name:
            return False
    return True


def create_ros_graph_snapshot():
    master = rosgraph.Master('snapshot')
    node_names = list()
    nodes = list()
    params = list()
    services_dict = dict()
    topics_dict = dict()
    parameter_dict = dict()

    if not(master.is_online()):
        print("Error: ROSMaster not found")

    # Get parameters
    for param_name in master.getParamNames():
        if param_name not in BLACK_LIST_PARAM and not(param_name.startswith('/roslaunch')):
            params.append(param_name)
    state = master.getSystemState()  # get the system state
    pubs, subs, services = state

    # get all topics type
    topic_list = master.getTopicTypes()
    for topic, topic_type in topic_list:
        topics_dict[topic] = topic_type

    # get all service types
    for service_name, _ in services:
        try:
            services_dict[service_name] = rosservice.get_service_type(
                service_name)
        except:
            pass

    # Get all nodes
    for s in state:
        for _, l in s:
            for n in l:
                if n not in BLACK_LIST_NODE:
                    node_names.append(n)

    node_names = list(set(node_names))
    for n in node_names:
        node = rg.Node(n)
        for pub, nodes_name in pubs:
            if not check_black_list(pub, BLACK_LIST_TOPIC):
                continue
            if n in nodes_name:
                node.publishers.add(rg.Interface(pub, topics_dict[pub]))
        for sub, nodes_name in subs:
            if not check_black_list(sub, BLACK_LIST_TOPIC):
                continue
            if n in nodes_name:
                node.subscribers.add(rg.Interface(sub, topics_dict[sub]))
        for serv, nodes_name in services:
            if not check_black_list(serv, BLACK_LIST_SERV):
                continue
            if n in nodes_name:
                node.services.add(rg.Interface(serv, services_dict[serv]))

        node.check_actions()
        nodes.append(node)

    node_param = rg.Node("parameters_node")
    for param_name in params:
        node_param.params.add(rg.ParameterInterface(
            param_name, master.getParam(param_name), type(master.getParam(param_name))))
    nodes.append(node_param)

    return nodes


def create_java_ros_model(pkg_name="dummy_pkg"):
    try:
        snapshot = create_ros_graph_snapshot()
        ros_model_str = "PackageSet { package { \n"
        ros_model_str += "  CatkinPackage "+pkg_name + " { "
        ros_model_str += "artifact {\n"
        for node in snapshot:
            ros_model_str += node.dump_java_ros_model()
        ros_model_str = ros_model_str[:-2]
        ros_model_str += "\n}}}}"
    except:
        return False, "Scanning Failed", ""

    return True, "Scanning succeeded", ros_model_str


def create_java_system_model(system_name="dummy_system", pkg_name="dummy_pkg"):
    try:
        snapshot = create_ros_graph_snapshot()
        system_model_str = "RosSystem { Name '%s'\n" % system_name
        system_model_str += "    RosComponents ( \n"
        for node in snapshot:
            system_model_str += node.dump_java_system_model(pkg_name)
        system_model_str = system_model_str[:-2]
        system_model_str += "\n)}"
    except:
        return False, "Scanning Failed", ""

    return True, "Scanning succeeded", system_model_str
