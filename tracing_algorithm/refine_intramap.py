import os, sys
sys.path.append(os.getcwd())
from modules.general import *
import numpy as np
import copy
import pickle
from modules.general import *
from modules.general import extract_orjson, str_to_bool

ENABLE_PARTIAL_COVERAGE = str_to_bool(os.getenv("ENABLE_PARTIAL_COVERAGE", "False"))
SCENARIO_NAME = os.getenv("SCENARIO_NAME")

ENABLE_BLUETOOTH = str_to_bool(os.getenv("ENABLE_BLUETOOTH"))
ENABLE_WIFI = str_to_bool(os.getenv("ENABLE_WIFI"))
ENABLE_LTE = str_to_bool(os.getenv("ENABLE_LTE"))

intramap=np.load(f'data/{SCENARIO_NAME}/intramap_{SCENARIO_NAME}.npy', allow_pickle=True).item()


#print(intramap)
intermap=np.load(f'data/{SCENARIO_NAME}/intermap_{SCENARIO_NAME}.npy', allow_pickle=True).item()

#with open(f'data/{SCENARIO_NAME}/intramap_{SCENARIO_NAME}.pickle', mode='rb') as intra_source:
 #   intramap = pickle.load(intra_source)
#with open(f'data/{SCENARIO_NAME}/intermap_{SCENARIO_NAME}.pickle', mode='rb') as inter_source:
 #   intermap = pickle.load(inter_source)
print(intermap)
#for key in intermap.keys():
 #   if "_W_" not in key:
  #      print(key)
   #     print(intermap[key])
#print(intramap)
enabled={"Bluetooth":ENABLE_BLUETOOTH,"WiFi":ENABLE_WIFI,"LTE":ENABLE_LTE}




def filter_protocols_per_id(data: dict, enabled: dict, drop_empty_ids: bool = False) -> dict:
    out = {}
    for _id, proto_map in data.items():
        if not isinstance(proto_map, dict):
            out[_id] = proto_map
            continue

        # keep only protocols whose enabled flag is True
        filtered = {k: v for k, v in proto_map.items() if enabled.get(k, True)}

        if filtered or not drop_empty_ids:
            out[_id] = filtered

    return out


intermap = filter_protocols_per_id(intermap, enabled)
#print(filtered)



if not enabled["WiFi"]:
    intermap = {k: v for k, v in intermap.items() if "_W_" not in k}
if not enabled["LTE"]:
    intermap = {k: v for k, v in intermap.items() if "_L_" not in k}
if not enabled["Bluetooth"]:
    intermap = {k: v for k, v in intermap.items() if "_B_" not in k}
    
    
if not enabled["WiFi"]:
    intramap = {k: v for k, v in intramap.items() if "_W_" not in k}
if not enabled["LTE"]:
    intramap = {k: v for k, v in intramap.items() if "_L_" not in k}
if not enabled["Bluetooth"]:
    intramap = {k: v for k, v in intramap.items() if "_B_" not in k}
np.save(f'data/{SCENARIO_NAME}/intramap_single_{SCENARIO_NAME}.npy', intramap, allow_pickle=True)



PARQUET_FILE_PATH = f"data/{SCENARIO_NAME}/aggregated_id_{SCENARIO_NAME}.parquet"
df = pl.read_parquet(PARQUET_FILE_PATH)
id_protocol_dict = {row["id"]: row["protocol"] for row in df.to_dicts()}

def filter_intermap(intermp):
    for id1 in intermp.keys():
        user_id = '_'.join(id1.split("_")[0:3])
        p1 = id_protocol_dict[id1]
        for p in intermp[id1]:
            set_id1=intermp[id1][p]
            temp_list=set()
            for id2 in set_id1:
                if id1 not in intermp[id2][p1]:
                    if '_'.join(id2.split("_")[0:3]) == user_id:
                        print(user_id, id1, id2)
                        #a=1
                    temp_list.add(id2)
            intermp[id1][p]=set(set(intermp[id1][p])-temp_list)
    return intermp


def compute_common_id(intramp, intermp):
    common_id = defaultdict(set)
    for id1 in intramp.keys():
        intra_mapping=intramp[id1]
       # if len(intra_mapping)==1:
        #    continue
        temp_list = set()
        for id2 in intra_mapping:
            if id1 == id2:
                continue
            remove = False
            if id1 not in intermp:
                continue
            for p in intermp[id1]:
                
                set_id1= set(intermp[id1][p])
                if id2 not in intermp.keys():
                    continue
                if p in intermp[id2]:
                    set_id2 = set(intermp[id2][p])
                else:
                    set_id2 = set()
            
                common = set_id1.intersection(set_id2)
                
                if not common: # no common set found     
                    break
                else:
                    common_id[id1].update(common)
    return common_id


def refine_intramap(intramp, intermp, chnge):
   
    for id1 in intramp.keys():
        intra_mapping=intramp[id1]
        if len(intra_mapping)==1:
            continue
        temp_list = set()
        for id2 in intra_mapping:
            '''Remove Flag - For all logic'''
            remove = False
            '''Common Check Flag - For any logic'''
            common_check = True
            if id1 in intermp:
                for p in intermp[id1]:
                    set_id1= set(intermp[id1][p])
                    if id2 not in intermp.keys():
                        continue
                    if p in intermp[id2]:
                        set_id2 = set(intermp[id2][p])
                    else:
                        set_id2 = set()
                
                    common = set_id1.intersection(set_id2)
                    
                    if not ENABLE_PARTIAL_COVERAGE:
                        if not common: # no common set found
                            remove = True        
                            break
                    else:
                        if common:
                            common_check = False

                    if not ENABLE_PARTIAL_COVERAGE:
                        if not set_id1 or not set_id2:
                            remove = True
                            break
                    else:
                        if not set_id1 or not set_id2:
                            continue
                if not ENABLE_PARTIAL_COVERAGE:
                    if remove:
                        chnge = True
                        temp_list.add(id2)
                else:
                    if common_check:
                        temp_list.add(id2)
        intramp[id1]=list(set(intramp[id1])-temp_list)          
    return intramp, chnge

def refine_intermap(intramp, intermp, chnge, common_id):
    for id1 in intermp.keys():
        common_set_id = common_id[id1]
        for p in intermp[id1]:
            set_id1= set(intermp[id1][p])
            if len(set_id1)==1:
                continue
            if common_set_id: # no common set found
                ''' If common set id, remove common id from intermap(id1) '''
                id1_remaining = set()
                id1_remaining = set_id1 - common_set_id
                
                LHS = set()
                for id2 in id1_remaining:
                    if id2 in intramp.keys():
                        if set(intramp[id2]).intersection(common_set_id):
                            LHS.add(id2)

                id1_remaining=id1_remaining-LHS

                while(True):
                    l = len(LHS)
                    for id2 in id1_remaining:
                        if id2 in intramp.keys():
                            if set(intramp[id2]).intersection(LHS):
                                LHS.add(id2)
                                
                    if len(LHS) == l:
                        break

                discard_id1_mappings=id1_remaining-LHS
                user_id = '_'.join(id1.split("_")[0:3])
                for i in discard_id1_mappings:
                    if user_id in i:
                        print(id1, i)
                        #a=1
                        
                        
                ''' Remove discard_id1_mappings from  intermap - Refining procedure '''
                a = len(intermp[id1][p])
                intermp[id1][p] = set(intermp[id1][p]) - discard_id1_mappings
                if not (len(intermp[id1][p]) == a):
                    chnge = True
    return intramp, intermp, chnge

#intramap,change=refine_intramap(intramap,intermap,False)
#print(intramap)
change = True
while(change):
    change = False
    ''' Refine Intramap Procedure '''
    #intramap=remove_subsets_from_dict(intramap)
    
    intramap, change = refine_intramap(intramap, intermap, change)
    if not ENABLE_PARTIAL_COVERAGE:
        intramap = clean_mappings(intramap)
    ''' Refine Intermap Procedure '''    
    common_id = compute_common_id(intramap, intermap)
    intramap, intermap, change = refine_intermap(intramap, intermap, change, common_id)
    intermap=filter_intermap(intermap)

    print("Refining")

#intramap,change=refine_intramap(intramap,intermap,False)

#print(intramap)

np.save(f'data/{SCENARIO_NAME}/refined_intermap_{SCENARIO_NAME}.npy', intermap, allow_pickle=True)
np.save(f'data/{SCENARIO_NAME}/refined_intramap_{SCENARIO_NAME}.npy', intramap, allow_pickle=True)

print("Refine completed")
