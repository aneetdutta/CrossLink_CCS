# from random import choices
from secrets import choice
from string import ascii_uppercase, digits
from math import sqrt
import os
# import cython
import numpy as np
import copy
from collections import defaultdict
from pprint import pprint
import orjson
import pandas as pd
import yaml, bisect
from shapely.geometry import Point, Polygon
import concurrent.futures
from collections import deque
import math, random
import polars as pl



def merge_nested_dicts(d1, d2):
    merged = defaultdict(dict)
    
    for key in set(d1) | set(d2):  # Combine keys from both dictionaries
        if key in d1 and key in d2:  # If both have the key
            if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                # Recursively merge nested dictionaries
                merged[key] = merge_nested_dicts(d1[key], d2[key])
            elif isinstance(d1[key], set) and isinstance(d2[key], set):
                # Merge sets
                merged[key] = d1[key] | d2[key]
            else:
                raise ValueError(f"Conflicting types for key {key}: {type(d1[key])} vs {type(d2[key])}")
        elif key in d1:
            merged[key] = d1[key]
        else:
            merged[key] = d2[key]
    
    return merged

def to_regular_dict(d):
    if isinstance(d, defaultdict):
        return {k: to_regular_dict(v) for k, v in d.items()}
    elif isinstance(d, set):
        return d
    return d

def extend_paths(df, target_timestep):
    result = []
    
    # Group by user_id and process each group
    group_iter = df.group_by("user_id", maintain_order=True) if hasattr(df, "group_by") else df.groupby("user_id")
    for _, group in group_iter:
        max_timestep = group["timestep"].max()
        
        if max_timestep < target_timestep:
            # Extract the original path without changes
            original_path = group.filter(pl.col("timestep") <= max_timestep)
            
            if len(original_path) <= 1:
                combined_path = original_path
            else:
                forward_path = original_path[1:]
                # Reverse path for extension, excluding the last element
                reverse_path = original_path[:-1].reverse()
                # Combine forward and reverse paths
                combined_path = pl.concat([reverse_path, forward_path], how="vertical")
            
            # Generate the extended path
            extended_path = []
            current_timestep = max_timestep + 1
            while current_timestep <= target_timestep:
                for row in combined_path.to_dicts():
                    if current_timestep > target_timestep:
                        break
                    extended_path.append(
                        {
                            "timestep": current_timestep,
                            "user_id": row["user_id"],
                            "loc_x": row["loc_x"],
                            "loc_y": row["loc_y"],
                        }
                    )
                    current_timestep += 1
            
            # Convert the extended path to DataFrame and append to result
            extended_path_df = pl.DataFrame(extended_path).select(original_path.columns)
            result.append(pl.concat([original_path, extended_path_df], how="vertical"))
        else:
            # Append the original group if timestep is already sufficient
            result.append(group)

    # Concatenate all results and return
    return pl.concat(result, how="vertical")


def create_grid_index(points, cell_size):
    """
    Create a grid-based index for spatial points.
    """
    grid_index = defaultdict(list)
    for idx, point in enumerate(points):
        cell_x = math.floor(point[0] / cell_size)
        cell_y = math.floor(point[1] / cell_size)
        grid_index[(cell_x, cell_y)].append((idx, point))
    return grid_index

def remove_random_edges(graph, num_edges_to_remove=10):
    # Ensure the number of edges to remove is not greater than the total number of edges
    num_edges_to_remove = min(num_edges_to_remove, graph.number_of_edges())
    
    # Get all edges in the graph
    edges = list(graph.edges)
    
    # Randomly select edges to remove
    edges_to_remove = random.sample(edges, num_edges_to_remove)
    
    # Remove selected edges from the graph
    graph.remove_edges_from(edges_to_remove)
    
    return edges_to_remove

def convert_numpy_types(obj):
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.int64):
        return int(obj)  # Convert numpy.int64 to int
    return obj

def contains_subsequence(big_list, small_list):
    """Check if small_list is a subsequence of big_list considering extra elements."""
    # Convert both lists to deques for efficient pops
    big_deque = deque(big_list)
    small_deque = deque(small_list)
    
    # Align the start: Remove elements from the start of big_list until it matches small_list
    while big_deque and small_deque and big_deque[0] != small_deque[0]:
        big_deque.popleft()
    
    # Align the end: Remove elements from the end of small_list until it matches big_list
    while big_deque and small_deque and big_deque[-1] != small_deque[-1]:
        small_deque.pop()
    
    # Check subsequence in aligned lists
    for item in big_deque:
        if not small_deque:  # If all elements in small_list are matched
            return True
        if item == small_deque[0]:  # Match the first element in small_list
            small_deque.popleft()
    
    return not small_deque
    

def clean_mappings_refine(mappings):
    mappings_copy = {k: set(v) for k, v in mappings.items()}
    single_mappings = {v[0] for v in mappings_copy.values() if len(v) == 1}
    # print(single_mappings)
    change = True
    single_length = len(single_mappings)
    while change:
        for key, values in mappings_copy.items():
            if len(values) > 1:
                mappings_copy[key] = [value for value in values if value not in single_mappings]
        single_mappings = {v[0] for v in mappings_copy.items() if len(v) == 1}
        # print(single_mappings)
        if len(single_mappings) != single_length:
            change = True
            single_length = len(single_mappings)
        else:
            change = False
    return mappings_copy    
    
    


def clean_mappings(mappings):
    #mappings_copy = {k: set(v) for k, v in mappings.items()}
    single_mappings = {v[0] for v in mappings.values() if len(v) == 1}
    # print(single_mappings)
    change = True
    single_length = len(single_mappings)
    while change:
        for key, values in mappings.items():
            if len(values) > 1:
                mappings[key] = [value for value in values if value not in single_mappings]
        single_mappings = {v[0] for v in mappings.values() if len(v) == 1}
        # print(single_mappings)
        if len(single_mappings) != single_length:
            change = True
            single_length = len(single_mappings)
        else:
            change = False
    return mappings

def merge_matching_sublists(lst, target_sublist):
    # print(target_sublist)
    # print(lst)
    matching_set = set()
    for sublist in lst:
        if set(target_sublist).issubset(set(sublist)):
            matching_set.update(set(sublist))
    return matching_set

def inter_intra_mapper(data, chained_intra):
    if not data:
        return []
    # print("checking")
    o = []
    for p, p_item in data.items():
        sf = set(merge_matching_sublists(chained_intra, p_item))
        # print(sf)
        o.append(sf)
    # print(o)
    return o

def filter_first_occurrences(input_list):
    result = {}
    for number in input_list:
        integer_part = int(number)
        # Only add the number if its integer part hasn't been added yet
        if integer_part not in result:
            result[integer_part] = number
    # Return the values as a list
    return list(result.values())

def crop_lists(L1, L2, min_L1, max_L1, min_L2, max_L2):
    # Find the minimum and maximum values of each list
    # min_L1, max_L1 = min(L1), max(L1)
    # min_L2, max_L2 = min(L2), max(L2)

    # Determine the overlapping range
    lower_bound = max(min_L1, min_L2)
    upper_bound = min(max_L1, max_L2)

    # Crop L1 to the overlapping range
    start_L1 = bisect.bisect_left(L1, lower_bound)
    end_L1 = bisect.bisect_right(L1, upper_bound)
    # print(start_L1,  end_L1)
    cropped_L1 = L1[start_L1-1:end_L1+1] if start_L1 != 0 else L1[start_L1:end_L1+1]

    # Crop L2 to the overlapping range
    start_L2 = bisect.bisect_left(L2, lower_bound)
    end_L2 = bisect.bisect_right(L2, upper_bound)
    # print(start_L2, end_L2)
    cropped_L2 = L2[start_L2-1:end_L2+1] if start_L2 != 0 else L2[start_L2:end_L2+1]

    return cropped_L1, cropped_L2

def remove_subsets_from_dict(dictionary):
    # Make a copy to avoid modifying the dictionary while iterating
    dict_copy = {k: set(v) for k, v in dictionary.items()}

    # print(dict_copy)
    # Iterate through each key-value pair
    for parent_key, parent_values in dict_copy.items():
        for child_key, child_values in dict_copy.items():
            # Skip if comparing the same key
            if parent_key == child_key:
                continue
 
            if (child_values.union({child_key})).issubset((parent_values.union({parent_key}))) and child_values != parent_values:
                # print(True, child_values, parent_values)
                # Remove the child values from the parent values
                parent_values -= child_values

    # Convert the sets back to lists for the final result
    return {k: list(v) for k, v in dict_copy.items()}

def create_chain(L1, L2):
    chain = []
    L1, L2 = sorted(set(L1)), sorted(set(L2))
    flag_l1, flag_l2 = True, True
    
    while len(L1) + len(L2) > 0:
        if flag_l1:
            l1 = L1.pop(0)
        if flag_l2:
            l2 = L2.pop(0)
            
        if l1 > l2:
            flag_l2 = True
            flag_l1 = False
        
        elif l2 > l1:
            flag_l2 = False
            flag_l1 = True
        
        if (len(L2) == 0):
            flag_l2 = False
            flag_l1 = True
        if (len(L1) == 0):
            flag_l1 = False
            flag_l2 = True

        chain.append((l1,l2))

    return list(set(chain))

def find_all_possible_chains(dictionary):
    all_chains = []
    visited_keys = set()

    # Reverse lookup dictionary to support backward traversal
    reverse_dict = {v: k for k, v in dictionary.items() if v}

    def build_chain(start_key):
        chain = []
        current_key = start_key

        # Traverse backwards to find the start of the chain
        while current_key in reverse_dict and current_key not in visited_keys:
            current_key = reverse_dict[current_key]

        # Traverse forwards from the start of the chain
        while current_key and current_key not in visited_keys:
            chain.append(current_key)
            visited_keys.add(current_key)
            current_key = dictionary.get(current_key)  # Move to the next key

        return chain

    # Start a chain from every unvisited key
    for start_key in dictionary:
        if start_key not in visited_keys:
            chain = build_chain(start_key)
            if chain:
                all_chains.append(chain)
    
    return all_chains

class UnionFind:
    def __init__(self):
        self.parent = {}
    
    def find(self, item):
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]
    
    def union(self, item1, item2):
        root1 = self.find(item1)
        root2 = self.find(item2)
        if root1 != root2:
            self.parent[root2] = root1
    
    def add(self, item):
        if item not in self.parent:
            self.parent[item] = item

def group_identifiers(tuples_list):
    uf = UnionFind()
    
    for i, time_epoch, type_, identifiers, ta in tuples_list:
        identifiers = list(identifiers)
        for identifier in identifiers:
            uf.add(identifier)
        for i in range(1, len(identifiers)):
            uf.union(identifiers[0], identifiers[i])
    
    groups = {}
    for identifier in uf.parent:
        root = uf.find(identifier)
        if root not in groups:
            groups[root] = set()
        groups[root].add(identifier)
    
    return list(groups.values())

# def group_identifiers(tuples_list):
#     groups = []
#     identifier_to_group = {}

#     for i, time_epoch, type_, identifiers, ta in tuples_list:
#         current_group = None
        
#         # Find the group for the current tuple
#         for identifier in identifiers:
#             if identifier in identifier_to_group:
#                 current_group = identifier_to_group[identifier]
#                 break
        
#         # If no existing group is found, create a new one
#         if current_group is None:
#             current_group = len(groups)
#             groups.append(set())
        
#         # Add the identifiers to the found/created group
#         groups[current_group].update(identifiers)
        
#         # Update the identifier to group mapping
#         for identifier in identifiers:
#             identifier_to_group[identifier] = current_group

#     # Convert sets to lists for the final output
#     return [set(group) for group in groups]

IDENTIFIER_LENGTH = os.getenv("IDENTIFIER_LENGTH")

def str_to_bool(s):
    return {'true': True, 'false': False}.get(s.strip().lower(), None)

def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def set_env_from_config(section, config):
    for key, value in config.get(section, {}).items():
        if isinstance(value, list):
            # Convert list (e.g., list of lists) to a string representation
            os.environ[key] = str(value)
        else:
            os.environ[key] = str(value)


def remove_subsets_and_merge(data):
    result = []
    for key, value in data.items():
        chain = [key] + value
        chain_set = set(chain)
        # Check if the chain is a subset of any existing chain or if it intersects with any existing chain
        subset = next((existing for existing in result if chain_set.issubset(set(existing))), None)
        intersection = next((existing for existing in result if chain_set.intersection(set(existing))), None)
        if subset:
            continue  # Skip if the chain is a subset of an existing chain
        elif intersection:
            # Merge the chains and remove the old ones
            result = [list(set(existing + chain)) if existing == intersection else existing for existing in result]
        else:
            result.append(chain)
    return result


def get_list_containing_value(merged_data, value):
    for chain in merged_data:
        if value in chain:
            return chain
    return None


def calculate_privacy_score_single(row, dur):
    if row['total_time'] == 0 and row[dur] == 0:
        return 1
    else:
        return row['total_time'] / row[dur]
    
def calculate_privacy_score(row):
    if row['total_time'] == 0 and row['ideal_duration'] == 0:
        return 1
    else:
        return row['total_time'] / row['ideal_duration']

def process_mappings(m1, m2, visited_intra_list):
    local_intra_potential_mapping = defaultdict(set)
    for p1, ids1 in m1.items():
        ''' Comparing with only same protocol types during intra mapping'''
        if p1 not in m2:
            continue
        ids1_set = set(ids1)
        ids2_set = set(m2[p1])
        
        if ids1_set.intersection(ids2_set):
            t0_1 = ids1_set - ids2_set
            t1_0 = ids2_set - ids1_set
        
            if t0_1 and t1_0:
                for i in t0_1:
                    common_set_for_i = visited_intra_list[i].intersection(t1_0)
                    not_common_set = t1_0 - common_set_for_i
                    # local_intra_potential_mapping[i] = set(local_intra_potential_mapping[i])
                    local_intra_potential_mapping[i].update(not_common_set) 
                     
    return local_intra_potential_mapping

def optimized_mapping_comparison(mapping0, mapping1, visited_intra_list, intra_potential_mapping):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_mapping = {
            executor.submit(process_mappings, m1, m2, visited_intra_list): (m1, m2)
            for m1 in mapping0 for m2 in mapping1
        }

        for future in concurrent.futures.as_completed(future_to_mapping):
            result = future.result()
            for key, value in result.items():
                if key not in intra_potential_mapping:
                    intra_potential_mapping[key] = set()
                intra_potential_mapping[key].update(value)
                
    return visited_intra_list, intra_potential_mapping
                
def combine_values(dicts, keys):
    # Initialize a dictionary to hold combined sets for each key
    combined_dict = {key: set() for key in keys}
    
    # Combine values for each key from all dictionaries
    for d in dicts:
        for key in keys:
            combined_dict[key].update(d.get(key, []))
    
    return combined_dict

def create_exclusion_set(combined_set, element):
    return {item for item in combined_set if item != element}

def combine_and_exclude_all(dicts, result_dict=None):
    # Fetch all unique keys from the provided dictionaries
    keys = {key for d in dicts for key in d.keys()}
    
    # Initialize a dictionary to hold combined sets for each key
    combined_dict = {key: set() for key in keys}
    
    # Combine values for each key from all dictionaries
    for d in dicts:
        for key in keys:
            values = d.get(key, [])
            combined_dict[key].update(values)
    
    # Initialize result_dict if not provided
    if result_dict is None:
        result_dict = {}
    else:
        # Ensure existing result_dict values are sets
        for key in result_dict:
            result_dict[key] = set(result_dict[key])
    
    # Create the final dictionary with each element as key and the set without that element as value
    for key, combined_set in combined_dict.items():
        for element in combined_set:
            if element not in result_dict:
                result_dict[element] = combined_set - {element}
            else:
                result_dict[element].update(combined_set - {element})
    
    # Convert sets back to lists for the final result
    return {key: set(value) for key, value in result_dict.items()}

# def combine_and_exclude_all(dicts, keys, result_dict=None):
#     combined_dict = combine_values(dicts, keys)
    
#     if result_dict is None:
#         result_dict = {}
#     else:
#         # Ensure existing result_dict values are sets
#         for key in result_dict:
#             result_dict[key] = set(result_dict[key])
    
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future_to_element = {}
        
#         for key in keys:
#             combined_set = combined_dict[key]
#             for element in combined_set:
#                 future = executor.submit(create_exclusion_set, combined_set, element)
#                 future_to_element[future] = element
        
#         for future in concurrent.futures.as_completed(future_to_element):
#             element = future_to_element[future]
#             exclusion_set = future.result()
#             if element not in result_dict:
#                 result_dict[element] = exclusion_set
#             else:
#                 result_dict[element].update(exclusion_set)
    
#     # Convert sets back to lists for the final result
#     result_dict = {key: value for key, value in result_dict.items()}
    
#     return result_dict

def remove_subsets(chains):
    chains_copy = sorted(chains, key=len, reverse=True)
    subsets_removed = []
    for chain in chains_copy:
        if not any(set(chain).issubset(set(other)) for other in subsets_removed):
            subsets_removed.append(chain)
    return subsets_removed

def remove_subsets_group(sets):
    # Sort the list of sets by length in descending order
    sets = sorted(sets, key=len, reverse=True)
    unique_sets = []

    for current_set in sets:
        is_subset = False
        for unique_set in unique_sets:
            if current_set.issubset(unique_set):
                is_subset = True
                break
        if not is_subset:
            unique_sets.append(current_set)

    return unique_sets

def build_chain_for_key(current_key, current_chain:list, visited: set, data: dict, all_chains, user_id):
    if current_key in visited:
        return

    visited.add(current_key)
    current_chain.append(current_key)

    result = data.get(current_key)
    if result:
        # print(result, "result")
        next_key, next_user_id = result
    else:
        next_key, next_user_id = None, None
        
    if next_user_id != user_id and next_user_id and next_key:
        current_chain.remove(current_key)
        
    if next_key and user_id==next_user_id:
        build_chain_for_key(next_key, current_chain.copy(), visited.copy(), data, all_chains, user_id=user_id)
    else:
        all_chains.append(current_chain.copy())

def find_chain_for_key(data, start_key, user_id):
    all_chains = []
    build_chain_for_key(start_key, [], set(), data, all_chains, user_id)
    return remove_subsets(all_chains)

def convert_sets_to_lists(d):
    d1 = copy.deepcopy(d)
    for k, v in d1.items():
        if isinstance(v, set):
            d1[k] = list(v)
        elif isinstance(v, dict):
            convert_sets_to_lists(v)
    return d1


def serialize_floats(obj):
    if isinstance(obj, np.float64):
        return float(obj)
    return obj

# data_array = pd.DataFrame(data)
def extract_orjson(filename):
    with open(filename, 'rb') as f:
        return orjson.loads(f.read())


def dump_orjson(filename, data):
    with open(filename, "wb") as f:
        f.write(orjson.dumps(data, default=serialize_floats))
    

# Function to check if a point is inside the polygon
def is_point_inside_polygon(x, y, polygon: Polygon):
    point = Point(x, y)
    return polygon.contains(point)

"""
Generates Random Device Identifier
"""
# def random_identifier():
#     return "".join(choice(ascii_uppercase + digits, k=int()))

def random_identifier():
    return "".join(choice(ascii_uppercase + digits) for _ in range(int(IDENTIFIER_LENGTH)))

def dict_to_tuple(dictionary):
    """
    Convert dictionary to tuple of sorted (key, value) pairs.
    """
    return tuple(sorted((key, tuple(value)) for key, value in dictionary.items()))

def remove_subsets_and_duplicates(list_of_arrays):
    """
    Remove arrays that are subsets of another array and remove identical arrays.
    """
    unique_arrays = []
    for array1 in list_of_arrays:
        is_subset_flag = False
        tuple1 = dict_to_tuple(array1)
        for array2 in unique_arrays:
            tuple2 = dict_to_tuple(array2)
            if set(tuple1).issubset(set(tuple2)):
                is_subset_flag = True
                break
        if not is_subset_flag:
            unique_arrays = [arr for arr in unique_arrays if not set(dict_to_tuple(arr)).issubset(set(tuple1))]
            unique_arrays.append(array1)
    return unique_arrays

def calculate_distance_l(location1: list, location2: list):
    dx = location1[0] - location2[0]
    # print(dx)
    dy = location1[1] - location2[1]
    # print(dy)
    return sqrt(dx * dx + dy * dy)


def process_dict(data, threshold):
    segments = []
    for key, values in data.items():
        current_segment = []
        start_time, start_point = values[0]
        current_segment.append(start_point)
        
        for i in range(1, len(values)):
            next_time, next_point = values[i]
            distance = calculate_distance_l(start_point, next_point)
            
            if distance > threshold:
                print(distance, threshold)
                print(start_point, next_point)
                start_point = next_point
                current_segment.append(start_point)
        
        segments.extend(current_segment)
        # # Append the last segment if it's not empty
        # if current_segment:
        #     segments.append(current_segment)
    return segments


class UnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, item):
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, item1, item2):
        root1 = self.find(item1)
        root2 = self.find(item2)

        if root1 != root2:
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1

    def add(self, item):
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0
