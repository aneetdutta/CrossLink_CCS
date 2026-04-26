#![allow(unused_imports)]
#![allow(unused_variables)]
#![allow(dead_code)]
#![allow(unused_mut)]

mod tasks;

use crate::tasks::generate_sniffer_data_from_end_device::GenerateSnifferObservationsFromEndDevices;
use crate::tasks::inter_map::InterProtocolMap;
use std::time::Instant;
use tasks::accel_config::AccelConfig;
use tasks::generate_sniffer_data::*;
use tasks::intra_map::*;
use tasks::run_config::*;

fn main() {
    println!("pathleak-rust, to make your simulation fast and practical");

    // a super naive cmd line arg parser
    let args = std::env::args().collect::<Vec<String>>();
    assert!(args.len() >= 3, "not enough argument"); // at least 2 arguments are needed, plus 1st that points to the exec
    let run_config_name = args[1].as_str();
    let task_name = args[2].as_str();

    // load accel config
    let accel_config = AccelConfig::from("./config.yaml");

    // load run config
    let run_config = RunConfig::from(accel_config.root_dir.to_str().unwrap(), run_config_name);
    println!("using run config from: {:?}", run_config.config_filename());

    // dispatch tasks
    match task_name {
        "generate_sniffer_data" => run_config.generate_sniffer_data(),
        "intra_map" => run_config.intra_protocol_map(),
        "inter_map" => run_config.inter_protocol_map(),
        "generate_sniffer_data_from_user_devices" => {
            run_config.generate_sniffer_data_from_end_devices(args[3].parse().unwrap())
        }
        _ => panic!("unknown task name: {}", task_name),
    }
}
