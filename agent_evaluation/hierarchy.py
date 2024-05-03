"""
This module contains the Hierarchy class for the agent evaluation module.
One source of Datasets is a hierarchical network in HCX (CX2) format.
Optionally, a parent interactome network in CX2 format will be used in creating Dataset instances.
We therefore need a Hierarchy class to represent the hierarchical network with methods to
obtain the parent network and to create Dataset instances from the hierarchical network. 
"""
from agent_evaluation.dataset import Dataset

class Hierarchy():
    def __init__(self, hierarchy_cx, derived_from_cx=None):
        self.hierarchy_cx = hierarchy_cx
        self.derived_from_cx = derived_from_cx

    def get_experiment_description(self):
        return self.hierarchy_cx.get_network_attributes().get("experiment_description")
    
    def get_assemblies(self, filter=None):
        assemblies = []
        for assembly in self.hierarchy_cx.get_nodes().values():
            attributes = assembly.get("v")
            # print(attributes.get("name"))
            size = attributes.get("CD_MemberList_Size")
           
            members = attributes.get("CD_MemberList")
            # print(members)
            if members is not None and size is not None:
                if filter is not None:
                    names = filter.get("names")
                    if names is not None and not names.contains(assembly.get_name()):
                        continue
                    max_size = filter.get("max_size")
                    if max_size is not None and size > max_size:
                        # print(f'size {size} is greater than max_size {max_size}')
                        continue
                    min_size = filter.get("min_size")
                    if min_size is not None and size < min_size:
                        continue
                assemblies.append(assembly) 
        return assemblies

    def get_datasets(self, filter=None, member_attributes=None, member_data_only=True):
        assemblies = self.get_assemblies(filter)
        # print(f'number of assemblies = {len(assemblies)}')        
        datasets = []
        interactome_nodes = self.derived_from_cx.get_nodes().values()
        interactome_data =[]
        for interactome_node in interactome_nodes:
            interactome_node_attributes = interactome_node.get("v")
            if member_attributes is not None:
                interactome_data.append( {key: value for key, value in interactome_node_attributes.items() if key in member_attributes})
            else:
                interactome_data.append(interactome_node_attributes)
        for assembly in assemblies:
            attributes = assembly.get("v")
            members = attributes.get("CD_MemberList").split(" ")
            if member_data_only:
                filtered_interactome_data = [data for data in interactome_data if data['name'] in members]
                datasets.append({"data": filtered_interactome_data, 
                                 "experiment_description":self.get_experiment_description()})
            else:
                datasets.append({"data": interactome_data, 
                                 "experiment_description":self.get_experiment_description()})
        return datasets