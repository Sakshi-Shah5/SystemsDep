from __future__  import print_function  # Python 2/3 compatibility

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from aenum import Enum
from gremlin_python.structure.graph import Vertex, Edge, Path
from gremlin_python.driver import client, serializer
from gremlin_python.process.traversal import Cardinality
import time
from . import neptune_dao
from gremlin_python.process.traversal import T

from .models import NeptuneDB, Edge, Vertex, Property

def perform_gremlin_query(node_val):
    
    links = get_neptune_data()

    # print(links)

    search_links = []
    # print(links)
    for link in links:
        if link.get('source', None) and link.get('destination', None):
            link_id = link.get('source', '')
            link_destination = link.get('destination', '')
            link['id'] = link.get('source', '')

            # to check if the provided node_val is present in either the source vertex('id') or the destination vertex('destination):
            if node_val.lower() in str(link_id).lower() or node_val.lower() in str(link_destination).lower():
                search_links.append(link)

    # print(search_links)

    return search_links

def get_vertex_properties(g, vertex_id):
    vertex_result = g.V(vertex_id).properties().toList()
    return {prop.key: prop.value for prop in vertex_result}


def process_edges(g, edges_result):
    processed_edges = []
    for edge in edges_result:
        in_vertex_properties = get_vertex_properties(g, edge.inV.id)
        out_vertex_properties = get_vertex_properties(g, edge.outV.id)

        in_vertex_system_name = in_vertex_properties.get("SystemName", edge.inV.label)
        out_vertex_system_name = out_vertex_properties.get("SystemName", edge.outV.label)

        edge_obj = Edge.from_result(edge, g)

        properties = [value for key, value in edge_obj.properties.items()]

        processed_edge = {
            "edge": edge_obj,
            "in_vertex_system_name": in_vertex_system_name,
            "out_vertex_system_name": out_vertex_system_name,
            "properties": properties
        }
        processed_edges.append(processed_edge)

    return processed_edges

def get_neptune_data():
    neptune_db = NeptuneDB()
    neptune_conn = neptune_db.get_conn()
    g = neptune_conn

    dao = neptune_dao.NeptuneDAO(neptune_conn)

    edges_result = dao.get_all_edges()

    vertices_result = dao.get_all_vertices_with_values()

    vertices = []

    for vertex in vertices_result:
        try:
            vertices.append(vertex.get('SystemName')[0])
        except Exception as e:
            continue

    processed_edges = process_edges(g, edges_result)

    links = []

    for edge_data in processed_edges:
        edge = edge_data["edge"]
        in_vertex_system_name = edge_data["in_vertex_system_name"]
        out_vertex_system_name = edge_data["out_vertex_system_name"]
        properties = edge_data["properties"]

        # print(f"Edge: {edge.label} ({edge.id})")
        # print(f"In Vertex: {in_vertex_system_name} ({edge.inV.id})")
        # print(f"Out Vertex: {out_vertex_system_name} ({edge.outV.id})")
        # print(f"Properties: {properties}")
        # print("---")

        

        links.append({
            "id": str(out_vertex_system_name),    
            "label": 'vertex', 
            "destination": str(in_vertex_system_name),
            "dataObject": properties[0],
            "integrationType": properties[1],
            "platformType": properties[2] if len(properties) >2 else '--',  
            "implementationType": properties[3] if len(properties) >3 else '--', 
            "techLead": properties[4] if len(properties) >4 else '--',  
            "description": properties[5] if len(properties) >5 else '--'  
            })


    edges = []

    edges_added = set()

    for edge in links:
        edges_added.add(edge['id'])
        edges_added.add(edge['destination'])
        edges.append({
            'source': edge['id'],
            'destination': edge['destination'],
            'dataObject': edge['dataObject'],
            'integrationType': edge['integrationType'],
            'platformType': edge.get('platformType',None),
            'implementationType':edge.get('implementationType',None),
            'techLead':edge.get('techLead',None), 
            'description':edge.get('description',None),
        })

    for vertex in vertices:
        if vertex not in edges_added:
            edges.append({
                'source': vertex,
                'destination': '--',
                'dataObject': '--',
                'integrationType': '--'
            })
        
    neptune_db.close_conn()    
    return edges

       
# utils.py
def add_dependency_to_neptune(source_system_name, destination_system_name, data_object, integration_type, platform_type, implementation_type, tech_lead, description):
    neptune_db = NeptuneDB()
    neptune_conn = neptune_db.get_conn()
    dao = neptune_dao.NeptuneDAO(neptune_conn)
    try:
        # Check if the source system exists
        source_vertex = dao.get_vertex_by_system_name(source_system_name)
        if not source_vertex:
            source_vertex = dao.add_system_vertex(source_system_name)

        print(source_vertex.id)

        # Check if the destination system exists
        destination_vertex = dao.get_vertex_by_system_name(destination_system_name)
        if not destination_vertex:
            destination_vertex = dao.add_system_vertex(destination_system_name)

        print(destination_vertex)

        # Check if the dependency exists
        # dependency = g.V(source_vertex.id).outE('dependency').inV().has('SystemName', destination_system_name).next()
        # if dependency:
        #     # Dependency already exists, terminate
        #     neptune_db.close_conn()
        #     return False, "Dependency already exists."

        # Add the dependency
        edge_label = 'dependency'
       
        # properties = {

        #     'DataObject': data_object,
        #     'IntegrationType': integration_type,
        #     'PlatformType': platform_type,
        #     'ImplementationType': implementation_type,
        #     'TechLead': tech_lead,
        #     'Description': description

        # }
        dao.add_edge_with_properties(
            source_vertex,
            destination_vertex, 
            edge_label,  
            data_object, 
            integration_type, 
            platform_type, 
            implementation_type, 
            tech_lead, 
            description
        )            
        
        neptune_db.close_conn()

        # Update the links data with the new dependency
        return True, {
                'id': source_system_name,
                'source': source_system_name,
                'destination': destination_system_name,
                'dataObject': data_object,
                'integrationType': integration_type
            }

    except Exception as e:
        print(f"Error adding dependency to Neptune: {e}")
        neptune_db.close_conn()
        return False, []


def add_system_to_neptune(system_name):
    neptune_db = NeptuneDB()
    neptune_conn = neptune_db.get_conn()
    dao = neptune_dao.NeptuneDAO(neptune_conn)

    try:
        # Create a new vertex with the label 'system' and add the system_name as a property
        dao.add_system_vertex(system_name)
        neptune_db.close_conn()

        return True, system_name

    except Exception as e:
        print(f"Error adding system to Neptune: {e}")
        neptune_db.close_conn()
        return False, []
    
def edit_system_to_neptune(system_id, system_name):
    neptune_db = NeptuneDB()
    neptune_conn = neptune_db.get_conn()
    dao = neptune_dao.NeptuneDAO(neptune_conn)

    try:
        vertex = dao.get_vertex_by_id(system_id) 
        if vertex is not None:
            updated_vertex = dao.set_vertex_property_single(vertex, system_name) 
            return True, updated_vertex['SystemName'][0]
        else:
            return False, f"No vertex found with id {system_id}"
    except Exception as e:
        return False, str(e)
    finally:
        neptune_db.close_conn()  

def get_distinct_labels_from_neptune():
    neptune_db = NeptuneDB()
    neptune_conn = neptune_db.get_conn()
    dao = neptune_dao.NeptuneDAO(neptune_conn)
    
    try:
        distinct_labels = dao.get_vertex_labels()
        neptune_db.close_conn()
        return set(distinct_labels)
    except Exception as e:
        print(f"Error retrieving distinct labels: {e}")
        neptune_db.close_conn()
        return []


# retrieves all the existing system names and their corresponding IDs from the Neptune database:
def get_all_systems_from_neptune():
    neptune_db = NeptuneDB()
    neptune_conn = neptune_db.get_conn()
    dao = neptune_dao.NeptuneDAO(neptune_conn)

    try:
        systems = dao.get_system_vertices_with_ids()
        systems_id_labels = []

        for vertex in systems:
            vertex_id = vertex.get(T.id, None)
            system_name = vertex['SystemName'][0]  
            systems_id_labels.append({'id': vertex_id, 'name': system_name})

        neptune_db.close_conn()
        return systems_id_labels
    except Exception as e:
        print(f"Error retrieving systems: {e}")
        neptune_db.close_conn()
        return []

def delete_system_from_neptune(system_id):
    try:
        neptune_db = NeptuneDB()
        neptune_conn = neptune_db.get_conn()
        dao = neptune_dao.NeptuneDAO(neptune_conn)
        vertex = dao.get_vertex_by_id(system_id)
        if vertex:
            neptune_dao.delete_system_vertex(system_id)
            return True, "System deleted successfully."
        else:
            return False, "System not found."
    except Exception as e:
        return False, str(e)
