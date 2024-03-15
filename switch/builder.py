import xml.etree.ElementTree as ET


class RequestNode:
    def __init__(self, *, tag, children=[], attrib={}, text=None):
        self.tag = tag
        self.text = text
        self.attrib = attrib
        self.children = children

    def append(self, element):
        self.children.append(element)
        return self

    def build(self):
        root = ET.Element(self.tag, self.attrib)
        if self.text is not None:
            root.text = self.text

        for child in self.children:
            root.append(child.build())

        return root


class DeviceConfiguration(RequestNode):
    def __init__(self, children=[]):
        super().__init__(tag="DeviceConfiguration", children=children)


class Version(RequestNode):
    def __init__(self, version):
        super().__init__(tag="version", text=version)

    def append(self, element):
        raise NotImplementedError


class ServiceFactory(RequestNode):
    def __init__(self, *, serviceName, action, children=[]):
        super().__init__(tag=serviceName, children=children, attrib={"action": action})


class Entry(RequestNode):
    def __init__(self, children=[]):
        super().__init__(tag="Entry", children=children)


class Value(RequestNode):
    def __init__(self, *, key, value):
        super().__init__(tag=key, text=value)

    def append(self, element):
        raise NotImplementedError


class CurrentLocalTime(RequestNode):
    def __init__(self, children=[]):
        super().__init__(tag="CurrentLocalTime", children=children)
