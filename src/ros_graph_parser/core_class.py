#!/usr/bin/env python

import rosgraph

ACTION_FILTER = ['goal', 'cancel']
ACTION_FILTER2 = ['status', 'result', 'feedback']


def get_namespace(name):
    try:
        return rosgraph.names.namespace(name)
    except ValueError as ex:
        print("Error: Name Invalid")
        print(ex)
        return ""


class Interface(object):
    def __init__(self, name, itype):
        self.resolved = name
        self.namespace = get_namespace(name)
        self.minimal = name[len(self.namespace)-1:]
        self.itype = itype

    def __eq__(self, other):
        if self.itype == other.itype and self.resolved == other.resolved:
            return True
        else:
            return False

    def get_dict(self):
        return {"Type": self.itype, "Name": self.resolved,
                "Namespace": self.namespace, "Minimal": self.minimal}

    def str_format(self, indent=""):
        return ("%sType: %s\n%sName: %s\n%sNamespace: %s\n%sMinimal: %s\n") % (
            indent, self.itype, indent, self.resolved, indent,
            self.namespace, indent, self.minimal)

    def java_format(self, indent="", name_type="", interface_type=""):
        return ("%s%s { name '%s' %s '%s'}") % (
            indent, name_type, self.resolved, interface_type, self.itype.replace("/", "."))


class InterfaceSet(set):

    def get_with_name(self, name):
        for elem in self:
            if name == elem.resolved:
                return elem
        raise KeyError("Interface with Name '%s' not found." % (name))

    def get_with_minimal(self, name):
        for elem in self:
            if name == elem.minimal:
                return elem
        raise KeyError("Interface with Minimal Name '%s' not found." % (name))

    def get_with_type(self, itype):
        for elem in self:
            if itype == elem.itype:
                return elem
        raise KeyError("No Interface of Type '%s' found." % (itype))

    def remove_with_name(self, name):
        self.remove(self.get_with_name(name))

    def str_format(self, indent=""):
        str_ = ""
        for elem in self:
            str_ += elem.str_format(indent) + "\n"
        return str_

    def java_format_ros_model(self, indent="", name_type="", interface_type="", name_block=""):
        if len(self) == 0:
            return ""
        str_ = ("\n%s%s {\n") % (indent, name_block)
        for elem in self:
            str_ += elem.java_format(indent+"  ",
                                     name_type, interface_type) + ",\n"
        str_ = str_[:-2]
        str_ += "}"
        return str_

    def java_format_system_model(self, indent="", name_type="", name_type2="", node_name="", pkg_name="", name_type3=""):
        if len(self) == 0:
            return ""
        if not name_type3:
            name_type3 = name_type2
        str_ = ("%sRos%s {\n") % (indent, name_type)
        for elem in self:
            str_ += ("%s    Ros%s '%s' {Ref%s '%s.%s.%s.%s'},\n") % (
                indent, name_type3, elem.resolved, name_type2, pkg_name, node_name, node_name, elem.resolved)
        str_ = str_[:-2]
        str_ += "}\n"
        return str_

    def get_list(self):
        return [x.get_dict() for x in self]

    def __str__(self):
        self.str_format()

    def iteritems(self):
        return [(x.resolved, x.itype) for x in self]

    def iterkeys(self):
        return [x.resolved for x in self]


class ParameterInterface(object):

    def __init__(self, name, value, itype):
        self.resolved = name
        self.namespace = get_namespace(name)
        self.minimal = name[len(self.namespace)-1:]
        self.value = value
        self.itype = self.get_type(value)
        self.count = 0

    def __eq__(self, other):
        if self.value == other.value and self.resolved == other.resolved:
            return True
        else:
            return False

    def get_type(self, value):
        itype = type(value)
        itype = (str(itype)).replace("<type '", "").replace("'>", "")
        if itype == 'float':
            return 'Double'
        elif itype == 'bool':
            return 'Boolean'
        elif itype == 'int':
            return 'Integer'
        elif itype == 'str':
            return 'String'
        elif itype == 'list' or itype == 'dict':
            if ":" in str(value):
                return 'Struc'
            else:
                return 'List'
        else:
            return itype

    def set_value(self, value, indent):
        str_param_value = ""
        if self.itype == "String":
            str_param_value += "'"+self.value+"'"
        elif self.itype == "Boolean":
            str_param_value += str(self.value).lower()
        elif self.itype == "List":
            str_param_value += str(self.value).replace(
                "[", "{").replace("]", "}")
        elif self.itype == 'Struc':
            str_param_value += self.value_struc(self.value[0], indent+"  ")
        else:
            str_param_value += str(value)
        return str_param_value

    def get_dict(self):
        return {"Value": self.value, "Name": self.resolved,
                "Namespace": self.namespace, "Minimal": self.minimal}

    def str_format(self, indent=""):
        return ("%sType: %s\n%sName: %s\n%sNamespace: %s\n%sMinimal: %s\n") % (
            indent, self.value, indent, self.resolved, indent,
            self.namespace, indent, self.minimal)

    def java_format(self, indent="", value=""):
        str_param = "%sParameter { name '%s' type %s " % (
            indent, self.resolved, self.itype)
        if self.itype == 'Struc':
            str_param += self.types_struc(self.value[0], indent)
            #str_param = str_param[:-2]
        if self.itype == 'List':
            str_param += self.form_list(self.value)
        str_param += "}"
        return str_param

    def types_struc(self, struc_dict, indent):
        str_param = "{\n"
        indent_new = indent+"  "
        for struc_element in struc_dict:
            sub_name = struc_element
            sub_value = struc_dict[struc_element]
            sub_type = self.get_type(sub_value)
            str_param += "%s'%s' %s" % (indent_new, sub_name, sub_type)
            if sub_type == 'List':
                str_param += self.form_list(sub_value)
            if isinstance(sub_value, dict):
                str_param += self.types_struc(
                    struc_dict[struc_element], indent_new)
            str_param += ",\n"
        str_param = str_param[:-2]
        str_param += "}"
        indent_new = ""
        return str_param

    def value_struc(self, struc_dict, indent):
        str_param = "{\n"
        indent_new = indent+"    "
        for struc_element in struc_dict:
            sub_name = struc_element
            sub_value = struc_dict[struc_element]
            sub_type = self.get_type(sub_value)
            str_param += "%s{ '%s' { value " % (indent_new, sub_name)
            if sub_type == "String":
                sub_value = "'"+sub_value+"'"
            if sub_type == 'List':
                sub_value = str(sub_value).replace(
                    "[", "{").replace("]", "}").replace("{{", "{").replace("}}", "}")
            if sub_type == "Boolean":
                sub_value = str(sub_value).lower()
            if isinstance(sub_value, dict):
                str_param += self.value_struc(
                    struc_dict[struc_element], indent_new)
                self.count = self.count + 1
            else:
                str_param += "%s}}" % (sub_value)
            str_param += ",\n"
        str_param = str_param[:-2]
        str_param += "}"
        if self.count == 1:
            str_param += "}}"
            self.count = self.count - 1
        indent_new = ""
        return str_param

    def form_list(self, value_in):
        str_param = "{"
        for i in value_in:
            str_param += self.get_type(i)
            if self.get_type(i) == "List":
                str_param += self.form_list(i)
            str_param += ","
        str_param = str_param[:-1]
        str_param += "}"
        return str_param


class ParameterSet(set):

    def str_format(self, indent=""):
        str_ = ""
        for elem in self:
            str_ += elem.str_format(indent) + "\n"
        return str_

    def java_format_ros_model(self, indent="", value="", name_block=""):
        if len(self) == 0:
            return ""
        str_ = ("\n%s%s {\n") % (indent, name_block)
        for elem in self:
            str_ += elem.java_format(indent+"  ", value) + ",\n"
        str_ = str_[:-2]
        str_ += "}"
        return str_

    def java_format_system_model(self, indent="", name_type="", name_type2="", node_name="", pkg_name="", name_type3=""):
        if len(self) == 0:
            return ""
        if not name_type3:
            name_type3 = name_type2
        str_ = ("%sRos%s {\n") % (indent, name_type)
        for elem in self:
            str_ += ("%s    Ros%s '%s' {Ref%s '%s.%s.%s.%s' value %s},\n") % (
                indent, name_type3, elem.resolved, name_type2, pkg_name, node_name, node_name, elem.resolved, elem.set_value(elem.value, indent))
        str_ = str_[:-2]
        str_ += "}\n"
        return str_

    def get_list(self):
        return [x.get_dict() for x in self]

    def __str__(self):
        self.str_format()

    def iteritems(self):
        return [(x.resolved, x.itype) for x in self]

    def iterkeys(self):
        return [x.resolved for x in self]


class Node(object):
    def __init__(self, name=""):
        self.name = name
        self.action_clients = InterfaceSet()
        self.action_servers = InterfaceSet()
        self.publishers = InterfaceSet()
        self.subscribers = InterfaceSet()
        self.service_clients = InterfaceSet()
        self.service_servers = InterfaceSet()
        self.params = ParameterSet()

    def get_namespace(self):
        return get_namespace(self.name)

    def _clean_action_client(self):
        for name in self.action_clients.iterkeys():
            for name_ in ACTION_FILTER:
                self.publishers.remove_with_name(name+name_)
            for name_ in ACTION_FILTER2:
                self.subscribers.remove_with_name(name+name_)

    def _clean_action_server(self):
        for name in self.action_servers.iterkeys():
            for name_ in ACTION_FILTER:
                self.subscribers.remove_with_name(name+name_)
            for name_ in ACTION_FILTER2:
                self.publishers.remove_with_name(name+name_)

    def check_actions(self):
        # Check Action client
        for topic_name, topic_type in self.publishers.iteritems():
            if topic_name.endswith(ACTION_FILTER[0]):
                _action_name = topic_name[:-len(ACTION_FILTER[0])]
                if not (_action_name + ACTION_FILTER[1] in self.publishers.iterkeys()):
                    continue
                for name in ACTION_FILTER2:
                    if not (_action_name + name in self.subscribers.iterkeys()):
                        continue
                _action_type = topic_type[:-10]  # Hardcoded ActionGoal
                self.action_clients.add(Interface(_action_name, _action_type))
        self._clean_action_client()
        # Check Action Server
        for topic_name, topic_type in self.subscribers.iteritems():
            if topic_name.endswith(ACTION_FILTER[0]):
                _action_name = topic_name[:-len(ACTION_FILTER[0])]
                if not (_action_name + ACTION_FILTER[1] in self.subscribers.iterkeys()):
                    continue
                for name in ACTION_FILTER2:
                    if not (_action_name + name in self.publishers.iterkeys()):
                        continue
                _action_type = topic_type[:-10]  # Hardcode ActionGoal
                self.action_servers.add(Interface(_action_name, _action_type))
        self._clean_action_server()

    def dump_print(self):
        _str = ""
        _str = "Node: \n\t%s" % (self.name)
        _str = _str + \
            "\tPublishers:\n%s" % (self.publishers.str_format('\t\t'))
        _str = _str + \
            "\tSubscribers:\n%s" % (self.subscribers.str_format('\t\t'))
        _str = _str + "\tServices:\n%s" % (self.service_servers.str_format('\t\t'))
        _str = _str + \
            "\tActionClients:\n%s" % (self.action_clients.str_format('\t\t'))
        _str = _str + \
            "\tActionServers:\n%s" % (self.action_servers.str_format('\t\t'))
        _str = _str + "\tParameters:\n%s" % (self.params.str_format('\t\t'))
        _str = _str + ("\n")
        print(_str)

    def dump_yaml(self):
        yaml_dict = dict()
        yaml_dict['Publishers'] = self.publishers.get_list()
        yaml_dict['Subscribers'] = self.subscribers.get_list()
        yaml_dict['Services'] = self.service_servers.get_list()
        yaml_dict['ActionClients'] = self.action_clients.get_list()
        yaml_dict['ActionServers'] = self.action_servers.get_list()
        yaml_dict['Parameters'] = self.params.get_list()
        return yaml_dict

    def dump_java_ros_model(self):
        ros_model_str = "    Artifact "+self.name+" {\n"
        ros_model_str += "      node Node { name " + self.name+"\n"
        ros_model_str += self.service_servers.java_format_ros_model(
            "        ", "ServiceServer", "service", "serviceserver")
        ros_model_str += self.service_clients.java_format_ros_model(
            "        ", "ServiceClients", "service", "serviceclient")
        ros_model_str += self.publishers.java_format_ros_model(
            "        ", "Publisher", "message", "publisher")
        ros_model_str += self.subscribers.java_format_ros_model(
            "        ", "Subscriber", "message", "subscriber")
        ros_model_str += self.action_servers.java_format_ros_model(
            "        ", "ActionServer", "action", "actionserver")
        ros_model_str += self.action_clients.java_format_ros_model(
            "        ", "ActionClient", "action", "actionclient")
        ros_model_str += self.params.java_format_ros_model(
            "        ", "Parameters", "parameter")
        ros_model_str += "}},\n"
        return ros_model_str

    def dump_java_system_model(self, package=""):
        system_model_str = "        ComponentInterface { name '" + \
            self.name+"'\n"
        system_model_str += self.publishers.java_format_system_model(
            "            ", "Publishers", "Publisher", self.name, package)
        system_model_str += self.subscribers.java_format_system_model(
            "            ", "Subscribers", "Subscriber", self.name, package)
        system_model_str += self.service_servers.java_format_system_model(
            "            ", "SrvServers", "Server", self.name, package, "ServiceServer")
        system_model_str += self.action_servers.java_format_system_model(
            "            ", "ActionServers", "ActionServer", self.name, package)
        system_model_str += self.action_clients.java_format_system_model(
            "            ", "ActionClients", "ActionClient", self.name, package)
        system_model_str += self.params.java_format_system_model(
            "            ", "Parameters", "Parameter", self.name, package)
        system_model_str += "},\n"
        return system_model_str
