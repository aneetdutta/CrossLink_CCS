use ObservedProtocol::*;
use serde::{Deserialize, Serialize};
use std::slice::Iter;

/// Defines a 2D location in our simulation map.
#[derive(Debug, Copy, Clone, Serialize, Deserialize, PartialEq)]
pub struct Location {
    pub x: f32,
    pub y: f32,
}

/// Defines a sample of a user's trace.
pub struct UserTraceSample {
    pub timestep: u32,
    pub user_id: String,
    pub loc: Location,
    pub transmit_ble: bool,
    pub transmit_wifi: bool,
    pub transmit_lte: bool,
    pub ble_id: String,
    pub wifi_id: String,
    pub lte_id: String,
}

/// Defines a sniffer
#[derive(Debug, Copy, Clone, Serialize, Deserialize, PartialEq)]
pub struct Sniffer {
    pub id: u16,
    pub loc: Location,
}

/// Defines the protocol of an observation.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash, Serialize, Deserialize)]
pub enum ObservedProtocol {
    BLE = 0,
    WIFI = 1,
    LTE = 2,
}

impl ObservedProtocol {
    pub fn iter() -> Iter<'static, ObservedProtocol> {
        static ALL_PROTOCOLS: [ObservedProtocol; 3] = [BLE, WIFI, LTE];
        ALL_PROTOCOLS.iter()
    }

    pub fn iter_combination() -> Vec<(ObservedProtocol, ObservedProtocol)> {
        static ALL_PROTOCOLS: [ObservedProtocol; 3] = [BLE, LTE, WIFI];

        let mut combinations = Vec::<(ObservedProtocol, ObservedProtocol)>::new();
        for i in 0..(ALL_PROTOCOLS.len() - 1) {
            for j in (i + 1)..(ALL_PROTOCOLS.len()) {
                combinations.push((ALL_PROTOCOLS[i], ALL_PROTOCOLS[j]))
            }
        }

        combinations
    }
}

/// Defines a sample of the sniffer's observation of a user device.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ObservationSample {
    pub timestep: u32,
    pub user_id: String,
    pub device_id: String,
    pub user_loc: Location,
    pub sniffer: Sniffer,
    pub distance: f32,
    pub protocol: ObservedProtocol,
}

pub fn distance_squared_between(a: &Location, b: &Location) -> f32 {
    let x = a.x - b.x;
    let y = a.y - b.y;
    x * x + y * y
}

/**
A compatible pair is basically two indexes pointing to the actual records
in the relevant array.
**/
pub type CompatiblePairs = (usize, usize);
