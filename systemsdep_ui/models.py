# Create your models here.
from aenum import Enum
from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection


class NeptuneDB:
    def __init__(self):
        try: 
            self.graph = Graph()

            self.remoteConn = DriverRemoteConnection('wss://db-neptune-1-sakshi.cluster-ci5lfrmfkym5.us-east-1.neptune.amazonaws.com:8182/gremlin','g')

            self.g = self.graph.traversal().withRemote(self.remoteConn)
        
        except Exception as e:
            print(e)

    def get_conn(self):
        return self.g
    
    def close_conn(self):
        self.remoteConn.close()


class Vertex:
    def __init__(self, id, label, properties):
        self.id = id
        self.label = label
        self.properties = properties

    @classmethod
    def from_result(cls, result, g):
        id = result.id
        label = result.label
        vertex_result = g.V(result.id).properties().toList()
        properties = {prop.key: prop.value for prop in vertex_result}
        return cls(id, label, properties)

    def get_property(self, key, default=None):
        return next((prop.value for prop in self.properties if prop.key == key), default)

class Edge:
    def __init__(self, id, label, outV, inV, properties):
        self.id = id
        self.label = label
        self.outV = outV
        self.inV = inV
        self.properties = properties #[Property(key, value) for key, value in properties.items()]

    @classmethod
    def from_result(cls, result, g):
        id = result.id
        label = result.label
        outV = Vertex.from_result(result.outV, g)
        inV = Vertex.from_result(result.inV, g)

        # Fetch the edge properties using elementMap()
        edge_map = g.E(result).elementMap().next()
        kvp_list = list(edge_map.items())
        properties = {item[0]: item[1] for item in kvp_list if not isinstance(item[0], Enum)}

        return cls(id, label, outV, inV, properties)


class Property:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return f"{self.key}: {self.value}"


