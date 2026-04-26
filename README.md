# CrossLink: Breaking Location Privacy by Linking Device Identifiers Across Protocols

---

Official Repository for the paper titled "CrossLink: Breaking Location Privacy by Linking Device Identifiers Across Protocols" 

![pipeline of the attack](design/design_arch.png)

Adversary can sniff the user data through multiple protocols like Bluetooth, WiFi, and LTE.  The sniffed data from all the sniffers would be sent to the tracking algorithm present at the backend. The sniffed data would consists of identifiers of all protocols and the probable distance between the sniffer and the measured user location. The adversary through the tracking algorithm would perform following steps:

1) Create inter-links of the identifiers from each sniffer based on the localization error and user mobility. (Maintain a list of not possible inter-linkages. Discard any linkages if linkages exists in not possible inter-linkages.)
2) Create intra-links of the identifiers based on if new identifiers of same protocol are present at the consecutive timestep. (Maintain a list of not possible intra-linkages. Discard any linkages if linkages exists in not possible intra-linkages.)
3) Refine the inter-linkages with help of intra-linkages and refine the intra-linkages with help of updated inter-linkages.
4) Store and utilize this linkage data for the next timesteps as the data is sent by the sniffer at every timestep.
5) Finally, reconstruct the user location traces after sometime to measure the privacy leakage of the users.

---


![code pipeline](design/code_pipeline.pdf)




Here is a brief introduction to start with the code. 

## Hardware
Our code works on most of the hardware settings. However, for efficiency and speed, we recommend Core i7 CPUs and memory (Atleast 16GB+) and disk size of 100GB. We ran our code on 11th Gen Intel Core i7-1165G7 @2.80Ghz Processor. Overall memory of our system was 32Gb with operating system Ubuntu 22.04LTS and disk space of 2TB. The CPU Blowfish benchmarks scored 1.33.

## Package Dependency
The requirements for the code are listed in the ```pyproject.toml```. These requirements require poetry package to be installed. ```pip3 install poetry```.
Once the poetry tool is installed, the packages can be installed using ```poetry install``` command and then using ```poetry shell```, the temporary shell can be invoked to run the code.

## Repository structure

The repository structure can be found in the ```design/code_pipeline.pdf```

The repository contains the following sub-artifacts:

1) simulation: contains two separate folders one for SuMO simulation and another for graph simulation. 

2) tracing_algorithm: contains the code of our propsed algorithm.

3) reconstruction: contains the code for path reconstruction algorithm.

4) plot: folder contains the code for creating the plots presented in our paper.

5) configs: folder contains the different configuration files for different parameter setting explained in our work.

## TODO before you start
0) Clone the repository with 
```bash
https://projects.cispa.saarland/c01mrsi/path-leakage.git
```
and checkout the branch ```usenix``` with command:
```bash
git checkout usenix
```

1) Check the ```<config file name>.yml``` file which you make. This file contains the conigurations required for the simulation setup.

2) For every scenarios configured through the yml file, the yml file name would become the database name where the respective collections would be added. 

3) The code consists of various scripts in the folders namely group, tracking, sumo, sanity, reconstruction. While these scripts could run individual by prescribing the environment variables, these scripts are stitched using the ```main.py``` and ```pipeline.py```. The ```main.py``` used **setuptools** to create various pipelines as showcased in ```pipeline.py```. For future purpose, more such pipeline functions can be added to ```pipeline.py```.

4) Code utilizes SuMO simulation package and the configurations used for the setup are located in the ```scenario``` folder at the root of the repository.

## Simulation Setup

To ensure our readers have an understand of the code, we will try to follow an example.

#### 1. Initialization

First we configure the ```scenario.yml``` file. All the below mentioned environment variables are part of this config file. This would be situated in the code folder of the repository. 

To understand the argument params, the command used would be:
```bash 
python3 main.py -h
```

To know the pipelines for running the code, run the command
```bash
python3 main.py -c scenario.yml -t help
```

Clean any older files in ```log, output, data folders``` with command:
```bash
python3 main.py -c scenario.yml -t clean_all
```

To only clean pycache, run 
```bash
python3 main.py -c scenario.yml -t clean
```

**(Ensure that the shell path is situated in the code folder and not in the root folder to run the code.)**.

#### 2. Data Generation Phase

##### 2.1 Sumo Simulation (Raw data generation)

The environment variables required are ```POLYGON_COORDS```, ```USER_TIMESTEPS``` and ```mobility_factor``` for running the sumo simulation code. Here the user movements data would generated.

This can be run with the command
```bash
python3 main.py -c scenario_result_512_sumo_all.yml -t sumo
```

With this command, the file with name ```raw_user_data_<config filename>.csv``` would be created.
Here for ```project.yml```, ```raw_user_data_project.csv``` file would be created in the ```data/scenario_name/``` folder. Also the file named ```raw_user_data_scenario_name.csv``` would be created. We use this filtered file for user data generation.

> Note: This is RAM intensive (as the code is not optimized). The SUMO data gets loaded in the memory and for filtering, multiple copies are made in the memory.


##### 2.2 User data generation

To generate user data based on this obtained sumo simulation data, we require to configure following env variables: 

Parameters to set transmission interval are:
```BLUETOOTH_MIN_TRANSMIT,BLUETOOTH_MAX_TRANSMIT,WIFI_MIN_TRANSMIT,WIFI_MAX_TRANSMIT,LTE_MIN_TRANSMIT,LTE_MAX_TRANSMIT```  for Bluetooth, WiFi and LTE protocols.

Parameters to set randomization interval are: 
```BLUETOOTH_MIN_REFRESH,BLUETOOTH_MAX_REFRESH,WIFI_MIN_REFRESH,WIFI_MAX_REFRESH,LTE_MIN_REFRESH,LTE_MAX_REFRESH``` for Bluetooth, WiFi and LTE protocols.

Parameters to enable synced randomization (Randomization at the same time) are: ```ENABLE_SYNCED_RANDOMIZATION, PROTOCOL_MIN_REFRESH, PROTOCOL_MAX_REFRESH```.

Apart from these params, few generic parameters to set are:
```DATA_USECASE```: here to run our scenario on previous ```raw_user_data_<config filename>.csv``` config file, ```DATA_USECASE = <config filename>```
For our usecase, ```DATA_USECASE = project```.
Users get added after every timesteps. To ensure that we want only a particular amount of users or less in the simulation, we should use ```ENABLE_USER_THRESHOLD, TOTAL_NUMBER_OF_USERS```.
The ```MAX_MOBILITY_FACTOR``` ensures the max mobility of the users that could be captured. By setting this, any users beyond the max mobility would be filtered.

To generate user data, we can run the command
```bash
python3 main.py -c scenario_result_512_sumo_all.yml -t generate_user_data
```

With this command, the file with name ```user_data_<config filename>.csv``` would be created.
Here for ```scenario_result_512_sumo_all.yml```, ```user_data_scenario_result_512_sumo_all.csv``` file would be created in the ```data/scenario_result_512_sumo_all/``` folder.


##### 2.3 Sniffer data generation

To generate the sniffer, first we need to check the sniffer placements. To generate the sniffer location coordinates, one can directly run 
```bash
python3 services/sl_coordinates.py
```
To enable diverse range of polygon co-ordinates, the required editing can be performed in ```service/sl_coordinates.py``` file.
Alternatively, we provide ```full_coverage_ble_sniffer_location.json```, ```full_coverage_wifi_sniffer_location.json``` and ```partial_coverage_sniffer_location.json``` files in the ```data``` folder.

These files can be directly used for generating the sniffer data.

For generating the sniffer data, we need to set the following parameters:

Parameters for Protocol Range are: ```BLUETOOTH_RANGE, WIFI_RANGE, LTE_RANGE``` 

For parallel processing we split the user data into batches. Thus, we need to set ```SNIFFER_PROCESSING_BATCH_SIZE```.

Apart from this, we need to also set the protocols that sniffer can sniff through with:```ENABLE_BLUETOOTH, ENABLE_WIFI, ENABLE_LTE```.

If we need to use ```partial_coverage_sniffer_location.json```, we need to set ```ENABLE_PARTIAL_COVERAGE```.

Once we have set the parameters, we can generate the sniffer data through command
```bash
python3 main.py -c scenario_result_512_sumo_all.yml -t generate_sniffer_data
```
With this command, the file with name ```sniffed_data_<config filename>.csv``` would be created.
Here for ```scenario_result_512_sumo_all.yml```, ```sniffed_data_scenario_result_512_sumo_all.yml.csv``` file would be created in the ```data/scenario_result_512_sumo_all/``` folder.



#### 3. Data Aggregation Phase

Data aggregation phase consists of

- Aggregation by users
 '''

Both these procedures are run with command:
```bash
python3 main.py -c scenario_result_512_sumo_all.yml -t aggregate
```

Once the aggregation is completed, we will have the file ```aggregated_id_scenario_512_sumo_all.parquet```

#### 4. Tracing Algorithm

To generate initial set of inter-protocol and intra-protocol linkages, we would run the grouping python files.

Here we would be required to set the following parameters:

Parameter to set the Localization Error are: ```BLUETOOTH_LOCALIZATION_ERROR```, ```WIFI_LOCALIZATION_ERROR```, ```LTE_LOCALIZATION_ERROR```.

For tracing, we would run the command:

```bash
python3 main.py -c scenario_result_512_sumo_all.yml -t intermap_new

python3 main.py -c scenario_result_512_sumo_all.yml -t intramap_new

python3 main.py -c scenario_result_512_sumo_all.yml -t generate_mappings

python3 main.py -c scenario_result_512_sumo_all.yml -t refine_intramap

python3 main.py -c scenario_result_512_sumo_all.yml -t intra_filter

```

We would have ```filtered_intramap_scenario_result_512_sumo_all.npy``` and ```refined_intermap_scenario_result_512_sumo_all.npy``` in ```data/scenario_result_512_sumo_all``` folder for multi-protocol mappings.

For single protocol mapping, we would have ```filtered_intramap_single_scenario_result_512_sumo_all.npy``` in ```data/scenario_result_512_sumo_all``` folder.



```


#### 5. Reconstruction

Once we have received the linkages through tracking. We will create user traces through reconstruction.

##### 7.1 Reconstruct the user data

This is a prior data preparation step.

Where we add the start timestep and final timestep of a user by merge aggregate timestep collection to aggregate user collection.

We run the command:
```bash
python3 main.py -c scenario_result_512_sumo_all.yml -t reconstruction
```



#### 6. Plotting the graphs

Once we have reconstructed and found the user traces, we plot the cdf graph for it.

This can be done using the command:
```bash
python3 main.py -c scenario_result_512_sumo_all.yml -t plot
```
The plots would be present in the ```output/images/scenario_name/``` folder
