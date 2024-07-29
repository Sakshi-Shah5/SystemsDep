from .models import NeptuneDB

from gremlin_python import statics
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import Cardinality
from gremlin_python.process.strategies import *
from gremlin_python.process.traversal import T
from aenum import Enum

class NeptuneDAO:
    def __init__(self, neptune_conn):
        self.g = neptune_conn

    def get_all_edges(self):
        result = self.g.E().toList()
        return result

    def get_all_vertices_with_values(self):
        result = self.g.V().valueMap().toList()
        return result

    def get_vertex_by_system_name(self, system_name):
        result = self.g.V().has('SystemName', system_name).next()
        return result

    def add_system_vertex(self, system_name):
        result = self.g.addV('system').property('SystemName', system_name).next()
        return result

    def add_edge_with_properties(self, source_vertex, destination_vertex, edge_label, data_object, integration_type, platform_type, implementation_type, tech_lead, description):
        result = self.g.V(source_vertex.id).addE(edge_label).to(__.V(destination_vertex.id)).property('DataObject', data_object).property('IntegrationType', integration_type).property('PlatformType', platform_type).property('ImplementationType', implementation_type).property('TechLead', tech_lead).property('Description', description).next()
        return result

    def set_vertex_property(self, vertex, system_name):
        result = self.g.V(vertex).property(statics.single, 'SystemName', system_name).next()
        return result

    def get_vertex_by_id(self, system_id):
        result = self.g.V().has('~id', system_id).next()
        return result

    def get_vertex_labels(self):
        result = self.g.V().label().toList()
        return result

    def get_system_vertices_with_ids(self):

        result = self.g.V().valueMap(True, 'id', 'label', 'SystemName').toList()
        return result
    
    def set_vertex_property_single(self, vertex, system_name):
        result = self.g.V(vertex).property(Cardinality.single, 'SystemName', system_name).next()
        return result
    
    def delete_system_vertex(self, system_id):
        result = self.g.V().has('~id', system_id).drop().iterate()
        return result