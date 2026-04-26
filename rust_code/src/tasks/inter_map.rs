use crate::tasks::common::ObservedProtocol::{BLE, LTE, WIFI};
use crate::tasks::common::{distance_squared_between, CompatiblePairs, ObservationSample, ObservedProtocol};
use crate::tasks::generate_sniffer_data::GenerateSnifferObservations;
use crate::tasks::intra_map::{
    GroupedSample, apply_localisation_error, group_observations_by_device_id,
};
use crate::tasks::run_config::RunConfig;
use rayon::prelude::*;
use serde_pickle::SerOptions;
use std::collections::HashMap;
use std::error::Error;
use std::fs::File;
use std::io;
use std::time::Instant;

pub trait InterProtocolMap {
    fn inter_protocol_map(&self);
    fn inter_map_output_filename(&self) -> String;
}

impl<'a> InterProtocolMap for RunConfig<'a> {
    fn inter_protocol_map(&self) {
        // first load all observation samples
        let process_start = Instant::now();
        let mut samples = self.load_sniffer_observations_binary();
        println!("loaded {} sniffer observations", samples.len());

        // apply localization error
        apply_localisation_error(&mut samples);
        println!("applied localisation error\n");

        // then group samples by protocols
        let grouped_samples = group_observations_by_device_id(&samples);
        let grouped_wifi_samples: Vec<_> = grouped_samples
            .iter()
            .filter(|s| s.protocol == WIFI)
            .collect();
        println!(
            "found {} set of traces for WIFI",
            grouped_wifi_samples.len()
        );

        let grouped_lte_samples: Vec<_> = grouped_samples
            .iter()
            .filter(|s| s.protocol == LTE)
            .collect();
        println!("found {} set of traces for LTE", grouped_lte_samples.len());

        let grouped_ble_samples: Vec<_> = grouped_samples
            .iter()
            .filter(|s| s.protocol == BLE)
            .collect();
        println!(
            "found {} set of traces for BLE\n",
            grouped_ble_samples.len()
        );

        let grouped_samples_by_protocols = HashMap::from([
            (WIFI, grouped_wifi_samples),
            (LTE, grouped_lte_samples),
            (BLE, grouped_ble_samples),
        ]);

        let mut all_compatible_pairs = HashMap::new();

        // then for each combination of protocol pairs
        // we first filter by overlapped time period
        let filtering_start = Instant::now();
        for (protocol_a, protocol_b) in ObservedProtocol::iter_combination() {
            let pair_processing_start = Instant::now();

            let samples_a = &grouped_samples_by_protocols[&protocol_a];
            let samples_b = &grouped_samples_by_protocols[&protocol_b];

            let overlapping_pairs = filter_pairs_for_overlapping_time_period(
                samples_a,
                samples_b,
                self.inter_map_grace_period,
            );
            println!(
                "=> found {} candidate pairs for protocol pair: ({:?}, {:?})",
                overlapping_pairs.len(),
                protocol_a,
                protocol_b
            );
            println!(
                "candidate pair filtering used {:?}",
                pair_processing_start.elapsed()
            );

            let compatible_processing_start = Instant::now();
            let compatible_pairs = evaluate_compatibility(
                &overlapping_pairs,
                samples_a,
                samples_b,
                self.acceptable_moving_rate,
                self.inter_map_grace_period,
            );
            println!(
                "==> found {} compatible pairs out of {} for protocol pair ({:?}, {:?})",
                compatible_pairs.len(),
                overlapping_pairs.len(),
                protocol_a,
                protocol_b
            );
            println!(
                "compatible pair filtering used {:?}",
                compatible_processing_start.elapsed()
            );

            let verification_start = Instant::now();
            let correct_count = verify(&compatible_pairs, samples_a, samples_b);
            println!(
                "===> of which {} is correct ({}%)",
                correct_count,
                correct_count as f32 / compatible_pairs.len() as f32 * 100.0f32
            );
            println!(
                "valid pair filter used {:?}\n",
                verification_start.elapsed()
            );

            // for debugging purpose
            // if protocol_a == BLE && protocol_b == LTE || protocol_a == LTE && protocol_b == BLE {
            //     dump_pairs("output.json", &compatible_pairs, &samples_a, &samples_b);
            // }

            convert_compatible_pairs_to_pickle_dict(
                &compatible_pairs,
                &samples_a,
                &samples_b,
                &mut all_compatible_pairs,
            )
        }

        println!("total elapsed: {:?}", process_start.elapsed());
        println!(
            "=> in which filtering + pre-pickling used: {:?}",
            filtering_start.elapsed()
        );

        println!("\nsaving result in pickle format for python interop...");
        save_compatible_pairs_to_pickle(
            &all_compatible_pairs,
            self.inter_map_output_filename().as_str(),
        )
        .unwrap();
        println!("saved result in pickle format for python interop");
    }

    fn inter_map_output_filename(&self) -> String {
        self.dedicated_data_dir()
            .join(format!("intermap_{}.pickle", self.name))
            .to_str()
            .unwrap()
            .to_string()
    }
}

fn filter_pairs_for_overlapping_time_period(
    samples_left: &[&GroupedSample],
    samples_right: &[&GroupedSample],
    max_non_overlapping_period: u32,
) -> Vec<(usize, usize)> {
    (0..samples_left.len())
        .into_par_iter()
        .map(|li| {
            filter_pairs_for_overlapping_time_period_one(
                li,
                &samples_left[li],
                samples_right,
                max_non_overlapping_period,
            )
        })
        .flatten()
        .collect()
}

fn filter_pairs_for_overlapping_time_period_one(
    sample_base_index: usize,
    sample_base: &GroupedSample,
    samples_right: &[&GroupedSample],
    max_non_overlapping_period: u32,
) -> Vec<(usize, usize)> {
    (0..samples_right.len())
        .into_iter()
        .filter(|ri| {
            let sample_right = samples_right[*ri];

            !((sample_base.max_timestep + max_non_overlapping_period < sample_right.min_timestep)
                || (sample_right.max_timestep + max_non_overlapping_period
                    < sample_base.min_timestep))
        })
        .map(|ri| (sample_base_index, ri))
        .collect()
}

fn evaluate_compatibility(
    pairs: &[(usize, usize)],
    samples_left: &[&GroupedSample],
    samples_right: &[&GroupedSample],
    max_mobility_factor: f32,
    max_transmisstion_interval: u32,
) -> Vec<(usize, usize)> {
    if cfg!(feature = "inter_map_disable_trim") {
        println!("WARNING: TRIM IS DISABLED")
    }

    pairs
        .into_par_iter()
        .filter(|p| {
            let (left_index, right_index) = **p;
            let left = samples_left[left_index];
            let right = samples_right[right_index];

            if cfg!(feature = "inter_map_disable_trim")
                || (left.samples.len() < 3 && right.samples.len() < 3)
            {
                // do not trim!
                evaluate_compatibility_one(&left.samples, &right.samples, max_mobility_factor)
            } else {
                // trim time!

                // special note:
                // for overlapping traces, we trim to the range
                // [right_min - max_transmission, left_max + max_transmission]
                // for disjoint traces, we fall back to search the
                // entire range over both traces

                let left_start = if left.max_timestep < right.min_timestep {
                    0
                } else {
                    left.samples
                        .binary_search_by_key(
                            &(right.min_timestep - max_transmisstion_interval),
                            |s| s.timestep,
                        )
                        .unwrap_or_else(|e| e)
                };

                let right_end = if right.min_timestep > left.max_timestep {
                    right.samples.len()
                } else {
                    right
                        .samples
                        .binary_search_by_key(
                            &(left.max_timestep + max_transmisstion_interval),
                            |s| s.timestep,
                        )
                        .unwrap_or_else(|e| e)
                };

                let left_trimmed = &left.samples[left_start..];
                let right_trimmed = &right.samples[..right_end];

                evaluate_compatibility_one(left_trimmed, right_trimmed, max_mobility_factor)
            }
        })
        .map(|g| *g)
        .collect()
}

fn evaluate_compatibility_one(
    observations_left: &[&ObservationSample],
    observations_right: &[&ObservationSample],
    max_mobility_rate: f32,
) -> bool {
    for left in observations_left {
        for right in observations_right.iter().rev() {
            let delta_t =
                ((left.timestep as f32) - (right.timestep as f32)).abs() * max_mobility_rate;
            let delta_d = left.distance + right.distance;

            // as usual, avoid square root computation
            // let delta_sniffer_d_squared = delta_x * delta_x + delta_y * delta_y;
            // if delta_sniffer_d_squared
            //     > delta_d * delta_d + 2f32 * delta_d * delta_t + delta_t * delta_t
            // {
            //     return false;
            // }
            let delta_sniffer_d = distance_squared_between(&left.sniffer.loc, &right.sniffer.loc).sqrt();
            if delta_sniffer_d > delta_t + delta_d {
                return false;
            }
        }
    }

    true
}

fn verify(
    pairs: &[(usize, usize)],
    left_samples: &[&GroupedSample],
    right_samples: &[&GroupedSample],
) -> usize {
    pairs
        .par_iter()
        .filter(|(a, b)| verify_one(&left_samples[*a], &right_samples[*b]))
        .count()
}

fn verify_one(left: &GroupedSample, right: &GroupedSample) -> bool {
    left.user_id == right.user_id
}

fn save_compatible_pairs_to_pickle(
    converted_compatible_pairs: &HashMap<String, HashMap<String, Vec<String>>>,
    filename: &str,
) -> Result<(), Box<dyn Error>> {
    let mut output = io::BufWriter::new(File::create(filename)?);
    match serde_pickle::to_writer(&mut output, converted_compatible_pairs, SerOptions::new()) {
        Ok(_) => Ok(()),
        Err(e) => Err(Box::new(e)),
    }
}

fn convert_compatible_pairs_to_pickle_dict(
    pairs: &[CompatiblePairs],
    left_samples: &[&GroupedSample],
    right_samples: &[&GroupedSample],
    dest: &mut HashMap<String, HashMap<String, Vec<String>>>,
) {
    fn inner(
        id1: String,
        id2: String,
        proc: &str,
        dest: &mut HashMap<String, HashMap<String, Vec<String>>>,
    ) {
        match dest.get_mut(id1.as_str()) {
            Some(proc_map) => match proc_map.get_mut(proc) {
                None => {
                    proc_map.insert(proc.to_string(), vec![id2]);
                }
                Some(existing) => existing.push(id2),
            },
            None => {
                let mut new_proc_map = HashMap::new();
                new_proc_map.insert(proc.to_string(), vec![id2]);
                dest.insert(id1, new_proc_map);
                ()
            }
        }
    }

    for pair in pairs {
        let (index1, index2) = *pair;
        let id1 = left_samples[index1].device_id;
        let id2 = right_samples[index2].device_id;
        let proc1 = match left_samples[index1].protocol {
            BLE => "BLE",
            WIFI => "Wifi",
            LTE => "Lte",
        };
        let proc2 = match right_samples[index2].protocol {
            BLE => "BLE",
            WIFI => "Wifi",
            LTE => "Lte",
        };

        inner(id1.to_string(), id2.to_string(), proc2, dest);
        inner(id2.to_string(), id1.to_string(), proc1, dest);
    }
}

