# Config file

The CrossLink pipeline relies on a config file to describe the needed information, including input & output settings, as well as parameters for different tasks. We detail the config file structure below.

## Overview

A config file is a YAML file with various sections. All sections and subsections are required unless specified otherwise.


### Rust-specific settings

Found under the section name `accel_settings`. Contains two subsections: `intra_map` controls intra-protocol mapping and `inter_map` controls inter-protocol mapping.

The options are used to control the so-called "trimming" feature, which throws away mapping candidates that are unlikely to produce a true matching. In which: `trim_threshold` controls the length of traces for a single identifier below which trimming would be disabled unconditionally. `trim_grace_period` controls the length of the core overlapping time window for evaluating whether a pair of traces can constitute a match. `time_delta_threshold` controls the timing difference between two traces over which they would be immediately considered impossible to produce a match.

The trimming feature is disabled by default in all makefile targets.

```yaml
accel_settings:
  intra_map:
    trim_threshold: 180
    trim_grace_period: 180
    time_delta_threshold: 100
  inter_map:
    trim_grace_period: 100

```

### General

Found under the `general` sections. Most keys are very self-explanatory. `LTE_RANDOMIZATION_MODE` controls whether we randomize a device's LTE identifier at fixed time interval or depending on its location (more similar to real-world situation).

```yaml
general:
USER_TIMESTEPS: 25200       # Number of user timesteps
DATA_SOURCE: "scenario_sumo"
SNIFFER_DATA_SOURCE: "scenario_test_32_sumo_smoke"
MAPPING_SOURCE: "scenario_test_32_sumo_smoke"
IDENTIFIER_LENGTH: 6
ID_RANDOMIZATION: uniform
ID_TRANSMISSION: exponential
LTE_RANDOMIZATION_MODE: "time"
```

### Movement simulation

Controls the movement simulation via SUMO and the `filter_by_Polygon` step. All keys are very self-explanatory.

```yaml
user_threshold:
  TOTAL_NUMBER_OF_USERS: 32          # Create only same set of users for different run

movement_parameters:
  POLYGON_COORDS:                     # Polygon coordinates
    - [3499.77, 1500.07]
    - [5798.43, 3799.93]
    - [6452.11, 3150.56]
    - [5401.44, 2099.71]
    - [5751.91, 1749.63]
    - [4500.10, 498.92]
```

### Device randomization, transmission and sniffing

Controls how and when device identifiers are randomized (for different protocols), and how often they transmit (therefore how often we can obtain a sniffing sample).

```yaml
randomization_intervals:
  # Bluetooth IDs refresh range uniform (in seconds)
  BLUETOOTH_MIN_REFRESH: 420
  BLUETOOTH_MAX_REFRESH: 900

  # WiFi ID refresh range uniform (in seconds)
  WIFI_MIN_REFRESH: 1
  WIFI_MAX_REFRESH: 60

  # LTE refresh range exponential (in seconds)
  LTE_MIN_REFRESH: 420


#Transmission Intervals
transmission_intervals:
  # Bluetooth IDs transmit range exponential (in seconds)

  BLUETOOTH_MAX_TRANSMIT: 5

  # WiFi ID transmit range uniform (in seconds)
  WIFI_MIN_TRANSMIT: 1
  WIFI_MAX_TRANSMIT: 60

  # LTE transmit range exponential (in seconds)
  
  LTE_MAX_TRANSMIT: 3
```

### Protocol localization traits

Controls the assumption we use when pairing traces on how far each protocol can reach, and the localization error inherent to each protocol (e.g., LTE can transmit signal much farther but also has a larger error margin then Bluetooth).

```yaml
# Range for communication protocols
communication_range:
  BLUETOOTH_RANGE: 30                # Bluetooth range (in meters)
  WIFI_RANGE: 50                     # WiFi range (in meters)
  LTE_RANGE: 100                     # LTE range (in meters)

# Localization errors
localization_errors:
  BLUETOOTH_LOCALIZATION_ERROR: 1.5    # Bluetooth localization error (in meters)
  WIFI_LOCALIZATION_ERROR: 5         # WiFi localization error (in meters)
  LTE_LOCALIZATION_ERROR: 10         # LTE localization error (in meters)
```

### Sniffing sample generation

Controls how sniffing samples are generated. Most keys are very self-explanatory. The mobility factor controls the fastest speed a device can move. The smart tracking and multilateration options are obsolete and no longer used in any task.

```yaml
smart:
  ENABLE_SMART_TRACKING: true

# Mobility settings
mobility:
  MAX_MOBILITY_FACTOR: 1.5       # Mobility factor in m/s

# Sniffer settings
sniffer:
  GENERATE_SNIFFER_DATA: true
  ENABLE_PARTIAL_COVERAGE: false
  ENABLE_MULTILATERATION: false
  ENABLE_BLUETOOTH: true       # Enable Bluetooth
  ENABLE_WIFI: true           # Enable WiFi
  ENABLE_LTE: true             # Enable LTE
  TRANSMIT_WHEN_RANDOMIZED: false
  SNIFFER_PROCESSING_BATCH_SIZE: 100 # Sniffer processing batch size
```



