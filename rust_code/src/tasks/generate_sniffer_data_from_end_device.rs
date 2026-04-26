use crate::tasks::common::{
    Location, ObservationSample, ObservedProtocol, Sniffer, UserTraceSample,
    distance_squared_between,
};
use crate::tasks::generate_sniffer_data::{
    GenerateSnifferObservations, load_user_samples, save_observation_samples,
};
use crate::tasks::intra_map::IntraProtocolMap;
use crate::tasks::run_config::RunConfig;
use itertools::Itertools;
use rand::prelude::IndexedRandom;
use rayon::prelude::*;
use std::collections::{HashMap, HashSet};
use std::time::Instant;

pub trait GenerateSnifferObservationsFromEndDevices {
    fn generate_sniffer_data_from_end_devices(&self, desired_sniffer_count: usize);
    fn sniffer_observation_from_end_device_output_filename(&self) -> String;
}

impl<'a> GenerateSnifferObservationsFromEndDevices for RunConfig<'a> {
    fn sniffer_observation_from_end_device_output_filename(&self) -> String {
        self.dedicated_data_dir()
            .join(format!(
              //  "sniffed_data_end_device_as_sniffers_{}.bin",
               "sniffed_data_{}.bin",
               
                self.name
            ))
            .to_str()
            .unwrap()
            .to_string()
    }

    fn generate_sniffer_data_from_end_devices(&self, desired_sniffer_count: usize) {
        println!("\n\n ==* running task: generate_sniffer_data_from_end_devices");

        let start = Instant::now();
        let user_samples_filename = self.user_sample_filename();
        let user_samples = load_user_samples(user_samples_filename.as_str()).unwrap_or_else(|_| {
            panic!(
                "cannot load user samples from: {}",
                user_samples_filename.as_str()
            )
        });

        println!(
            "loaded {:?} user samples from: {:?}",
            user_samples.len(),
            user_samples_filename
        );

        println!("choosing random users as sniffers");
        let all_user_ids = user_samples
            .iter()
            .unique_by(|x| x.user_id.as_str())
            .map(|x| x.user_id.to_string())
            .collect::<Vec<_>>();
        let sniffer_user_ids = all_user_ids
            .choose_multiple(&mut rand::rng(), desired_sniffer_count)
            .collect::<Vec<_>>();
        println!(
            "found {:?} distinct users, chosen {:?} as sniffers",
            all_user_ids.len(),
            sniffer_user_ids.len()
        );

        println!("pre-building location lists of sniffer users");
        let sniffers = sniffer_user_ids
            .par_iter()
            .map(|id| {
                (
                    (*id).clone(),
                    find_locations_of_user_ordered_by_time(id.as_str(), &user_samples)
                        .iter()
                        .map(|g| (g.timestep, *g))
                        .collect::<HashMap<_, _>>(),
                )
            })
            .collect::<HashMap<_, _>>();
        assert_eq!(sniffer_user_ids.len(), sniffers.len());
        sniffers
            .iter()
            .for_each(|(id, loc)| println!("for id {:?}, found {:?} loc samples", id, loc.len()));
        println!("built location lists of sniffer users");

        println!("generating observation samples");
        let results = generate_observation_samples(
            &sniffers,
            &user_samples,
            self.ble_range,
            self.wifi_range,
            self.lte_range,
        );
        println!("generated {:?} observation samples", results.len());

        save_observation_samples(
            self.sniffer_observation_from_end_device_output_filename()
                .as_str(),
            &results,
        )
        .expect("unable to save observation samples");
    }
}

fn find_locations_of_user_ordered_by_time<'a>(
    user_id: &str,
    samples: &'a [UserTraceSample],
) -> Vec<&'a UserTraceSample> {
    samples
        .iter()
        .filter(|e| e.user_id.as_str() == user_id)
        .collect::<Vec<_>>()
}

pub fn generate_observation_samples(
    sniffers: &HashMap<String, HashMap<u32, &UserTraceSample>>,
    user_samples: &[UserTraceSample],
    ble_range: f32,
    wifi_range: f32,
    lte_range: f32,
) -> Vec<ObservationSample> {
    sniffers
        .iter()
        .map(|(id, loc)| {
            generate_observation_samples_for_one(
                id.as_str(),
                loc,
                user_samples,
                ble_range,
                wifi_range,
                lte_range,
            )
        })
        .flatten()
        .collect()
}

/**
`sniffer_user_locations` are locations of a given sniffer user
indexed by the corresponding timestep.
**/
pub fn generate_observation_samples_for_one(
    sniffer_user_id: &str,
    sniffer_user_locations: &HashMap<u32, &UserTraceSample>,
    user_samples: &[UserTraceSample],
    ble_range: f32,
    wifi_range: f32,
    lte_range: f32,
) -> Vec<ObservationSample> {
    fn make_observation_sample(
        sniffer_user_loc: Location,
        distance: f32,
        observed_user: &UserTraceSample,
        observed_proc: ObservedProtocol,
        observed_device_id: &str,
    ) -> ObservationSample {
        ObservationSample {
            timestep: observed_user.timestep,
            user_id: observed_user.user_id.to_string(),
            device_id: observed_device_id.to_string(),
            user_loc: observed_user.loc,
            sniffer: Sniffer {
                id: 0u16,
                loc: sniffer_user_loc,
            },
            distance,
            protocol: observed_proc,
        }
    }

    let mut observation_samples = Vec::new();

    for sample in user_samples.iter() {
        // first filter out the ones without a sniffer entry in the sniffer trace
        let matching_sniffer_loc = sniffer_user_locations.get(&sample.timestep);
        if matching_sniffer_loc.is_none() {
            continue;
        }
        let matching_sniffer_loc = matching_sniffer_loc.unwrap().loc;

        let distance = distance_squared_between(&matching_sniffer_loc, &sample.loc).sqrt();

        if sample.transmit_ble && distance < ble_range {
            observation_samples.push(make_observation_sample(
                matching_sniffer_loc,
                distance,
                sample,
                ObservedProtocol::BLE,
                sample.ble_id.as_str(),
            ))
        }

        if sample.transmit_wifi && distance < wifi_range {
            observation_samples.push(make_observation_sample(
                matching_sniffer_loc,
                distance,
                sample,
                ObservedProtocol::WIFI,
                sample.wifi_id.as_str(),
            ))
        }

        if sample.transmit_lte && distance < lte_range {
            observation_samples.push(make_observation_sample(
                matching_sniffer_loc,
                distance,
                sample,
                ObservedProtocol::LTE,
                sample.lte_id.as_str(),
            ))
        }
    }

    observation_samples
}
