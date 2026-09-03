use crate::tasks::common::{
    CompatiblePairs, ObservationSample, ObservedProtocol, distance_squared_between,
};
use crate::tasks::generate_sniffer_data::GenerateSnifferObservations;
use crate::tasks::run_config::RunConfig;
use rayon::prelude::*;
use regex::{Match, Regex};
use serde::ser::SerializeSeq;
use serde::{Serialize, Serializer};
use serde_pickle::SerOptions;
use serde_pickle::ser::PickleProto;
use std::collections::HashMap;
use std::error::Error;
use std::fmt::format;
use std::fs::File;
use std::io;
use std::time::{Duration, Instant};

pub trait IntraProtocolMap {
    fn intra_protocol_map(&self);
    fn intra_map_output_filename(&self) -> String;
}

impl<'a> IntraProtocolMap for RunConfig<'a> {
    fn intra_map_output_filename(&self) -> String {
        self.dedicated_data_dir()
            .join(format!("intramap_{}.pickle", self.name))
            .to_str()
            .unwrap()
            .to_string()
    }

    fn intra_protocol_map(&self) {
        println!("\n\n ==* running task: intra_protocol_map");

        let load_start = Instant::now();
        println!(
            "loading binary sniffer observations from: {:?}",
            self.sniffer_observations_binary_filename()
        );
        let mut observations = self.load_sniffer_observations_binary();
        apply_localisation_error(&mut observations);
        println!("loaded {} observations", observations.len());
        println!("|| loading used {:?}\n", load_start.elapsed());

        let group_start = Instant::now();
        let all_observations_grouped = group_observations_by_device_id(&observations);
        println!(
            "identified {:?} groups by device id",
            all_observations_grouped.len()
        );
        println!("|| grouping used {:?}\n", group_start.elapsed());

        let mut grouping_total_elapsed = Duration::new(0, 0);
        let mut linking_total_elapsed = Duration::new(0, 0);
        let mut compatibility_total_elapsed = Duration::new(0, 0);
        let mut verification_total_elapsed = Duration::new(0, 0);

        let mut potentially_linked_pairs_grouped =
            HashMap::<ObservedProtocol, Vec<(usize, usize)>>::new();

        let mut total_compatible_pairs = HashMap::<String, Vec<String>>::new();

        for proc in ObservedProtocol::iter() {
            let grouping_started = Instant::now();
            let mut proc_observations: Vec<&GroupedSample> = all_observations_grouped
                .iter()
                .filter(|g| g.protocol == *proc)
                .collect();

            // make sure that all observations are indeed of given protocol
            assert!(!proc_observations.iter().any(|g| g.protocol != *proc));

            // for debugging
            // proc_observations.sort_by_key(|e| e.max_timestep);
            // proc_observations.sort_by_key(|e| e.min_timestep);

            grouping_total_elapsed += grouping_started.elapsed();
            println!(
                "found {} unique device IDs for {:?}",
                proc_observations.len(),
                proc
            );

            let linking_started = Instant::now();
            let mut potentially_linked_pairs = find_potentially_linked_pairs(
                &proc_observations,
                self.intra_map_time_delta_threshold,
            );
            linking_total_elapsed += linking_started.elapsed();
            println!(
                "=> among which {} are potentially linked, {:?}",
                potentially_linked_pairs.len(),
                proc
            );

            // for debugging, to produce stable and reproducible order into find_compatible_paris_for_one
            // potentially_linked_pairs.sort_by_key(|(a, b)| *b);
            // potentially_linked_pairs.sort_by_key(|(a, b)| *a);

            let compatible_started = Instant::now();
            let compatible_linked_pairs = find_compatible_pairs(
                &proc_observations,
                &potentially_linked_pairs,
                self.acceptable_moving_rate,
                self.intra_map_trim_grace_period,
                self.intra_map_trim_threshold,
            );

            // make sure all compatible pairs are indeed of the same protocol
            assert!(compatible_linked_pairs.iter().all(|(a, b)| {
                let (a, b) = (proc_observations[*a], proc_observations[*b]);
                a.protocol == b.protocol
            }));

            compatibility_total_elapsed += compatible_started.elapsed();
            println!(
                "==> among which {} are compatible, {:?}",
                compatible_linked_pairs.len(),
                proc
            );

            let verification_started = Instant::now();
            let wrongly_linked_pairs_count =
                verify_linked_pairs(&compatible_linked_pairs, &proc_observations);
            println!(
                "===> among which {}% are wrong",
                wrongly_linked_pairs_count as f32 / compatible_linked_pairs.len() as f32 * 100f32
            );
            println!(
                "===> among which {} are correct",
                compatible_linked_pairs.len() - wrongly_linked_pairs_count
            );

            verification_total_elapsed += verification_started.elapsed();
            println!(
                "|| processing for proc {:?} took {:?}\n",
                proc,
                grouping_started.elapsed()
            );

            // save found compatible pairs
            convert_compatible_pairs_to_pickle_dict(
                &compatible_linked_pairs,
                &proc_observations,
                &mut total_compatible_pairs,
            )
        }

        // end
        println!("|| total elapsed: {:?}", load_start.elapsed());
        println!(
            "|||> in which grouping elapsed: {:?}",
            grouping_total_elapsed
        );
        println!("|||> in which linking elapsed: {:?}", linking_total_elapsed);
        println!(
            "|||> in which compatibility elapsed: {:?}",
            compatibility_total_elapsed
        );
        println!(
            "|||> in which verification elapsed: {:?}",
            verification_total_elapsed
        );

        // save pairs
        println!("\nsaving result in pickle format for python interop...");
        save_compatible_pairs_to_pickle(
            &total_compatible_pairs,
            self.intra_map_output_filename().as_str(),
        )
        .unwrap();
        println!("saved result in pickle format for python interop");
    }
}

/// Defines a set of observation samples that share the same device ID.
pub struct GroupedSample<'a> {
    pub samples: Vec<&'a ObservationSample>,
    pub max_timestep: u32,
    pub min_timestep: u32,
    pub protocol: ObservedProtocol,
    pub user_id: &'a str,
    pub device_id: &'a str,
}

impl<'a> Serialize for GroupedSample<'a> {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        serializer.serialize_str(self.device_id)
    }
}

pub fn apply_localisation_error(observations: &mut [ObservationSample]) {
    for observation in observations.iter_mut() {
        observation.distance += match observation.protocol {
            ObservedProtocol::BLE => 1.5f32,
            ObservedProtocol::WIFI => 5f32,
            ObservedProtocol::LTE => 10f32,
        }
    }
}

pub fn group_observations_by_device_id(
    observations: &'_ [ObservationSample],
) -> Vec<GroupedSample<'_>> {
    // first group the observations by device id
    let mut groups: HashMap<&str, Vec<&ObservationSample>> = HashMap::new();
    for o in observations.iter() {
        if groups.contains_key(o.device_id.as_str()) {
            groups.get_mut(&o.device_id.as_str()).unwrap().push(o);
        } else {
            groups.insert(&o.device_id, vec![o]);
        }
    }

    for group in groups.values_mut() {
        // for debugging
        // group.sort_by(|g1, g2| g1.distance.partial_cmp(&g2.distance).unwrap());
        group.sort_by_key(|e| e.timestep);
    }

    // then pre-compute the min and max timestep for each group
    let mut precomputed_groups = Vec::<GroupedSample>::new();
    for (device_id, group) in groups {
        let max = group.iter().max_by_key(|s| s.timestep).unwrap().timestep;
        let min = group.iter().min_by_key(|s| s.timestep).unwrap().timestep;
        let protocol = group.first().unwrap().protocol;
        let user_id = &group.first().unwrap().user_id;

        precomputed_groups.push(GroupedSample {
            samples: group,
            max_timestep: max,
            min_timestep: min,
            protocol,
            user_id,
            device_id,
        });
    }

    precomputed_groups
}

pub fn find_potentially_linked_pairs(
    grouped_observations: &[&GroupedSample],
    time_delta_threshold: u32,
) -> Vec<(usize, usize)> {
    (0..grouped_observations.len())
        .into_par_iter()
        .map(|base_index| {
            find_potentially_linked_pairs_for_one(
                base_index,
                &grouped_observations[base_index],
                &grouped_observations,
                time_delta_threshold,
            )
        })
        .flatten()
        .collect()
}

pub fn find_potentially_linked_pairs_for_one(
    base_index: usize,
    base_group: &GroupedSample,
    grouped_observations: &[&GroupedSample],
    time_delta_threshold: u32,
) -> Vec<(usize, usize)> {
    (0..grouped_observations.len())
        .into_iter()
        .filter(|right_index| {
            base_index != *right_index
                && base_group.max_timestep < grouped_observations[*right_index].min_timestep
                && grouped_observations[*right_index].min_timestep - base_group.max_timestep
                    <= time_delta_threshold
        })
        .map(|right_index| (base_index, right_index))
        .collect()
}

pub fn find_compatible_pairs<'a>(
    groups: &[&GroupedSample],
    pairs: &'a [(usize, usize)],
    acceptable_moving_rate: f32,
    trim_grace_period: u32,
    trim_threshold: usize,
) -> Vec<&'a (usize, usize)> {
    pairs
        .par_iter()
        .filter(|(left, right)| {
            let left_group = groups[*left];
            let right_group = groups[*right];

            // skip trimming
            if cfg!(feature = "intra_map_disable_trim")
                || left_group.samples.len() < trim_threshold
                || right_group.samples.len() < trim_threshold
            {
                check_compatibility_for_one(
                    &left_group.samples,
                    &right_group.samples,
                    acceptable_moving_rate,
                )
            } else {
                // find out backwards the first left sample before max - trim_threshold
                let left_cutoff = left_group.max_timestep as i32 - trim_grace_period as i32;
                let left_u_cutoff = left_cutoff as u32;
                // only do the scan where not all left samples are below the cutoff value
                // and fallback to full series in case of no match
                let left_start = if left_cutoff > 0 && left_group.min_timestep < left_u_cutoff {
                    left_group
                        .samples
                        .iter()
                        .rposition(|s| s.timestep < left_u_cutoff)
                        .unwrap()
                } else {
                    0
                };
                let left_view = &left_group.samples[left_start..];

                // find out the first right sample after min + trim_threshold
                let right_cutoff = right_group.min_timestep + trim_grace_period;
                // only do the scan where not all left samples are below the cutoff value
                // and fallback to full series in case of no match
                let right_end = if right_group.max_timestep > right_cutoff {
                    right_group
                        .samples
                        .iter()
                        .position(|s| s.timestep > right_cutoff)
                        .unwrap()
                } else {
                    right_group.samples.len()
                };

                let right_view = &right_group.samples[..right_end];
                // check_compatibility_for_one(&left_group.samples, &right_group.samples, acceptable_moving_rate)
                check_compatibility_for_one(left_view, right_view, acceptable_moving_rate)
            }
        })
        .collect()
}

pub fn check_compatibility_for_one(
    left: &[&ObservationSample],
    right: &[&ObservationSample],
    acceptable_moving_rate: f32,
) -> bool {
    let row_cnt = left.len();
    let col_cnt = right.len();

    for i in 0..row_cnt {
        for j in (0..col_cnt).rev() {
            let distance = left[i].distance + right[j].distance;
            let delta_time = left[i].timestep as f32 - right[j].timestep as f32;

            let sniffer_distance =
                distance_squared_between(&left[i].sniffer.loc, &right[j].sniffer.loc).sqrt();
            let acceptable_delta_distance = delta_time.abs() * acceptable_moving_rate;
            if sniffer_distance > acceptable_delta_distance + distance {
                return false;
            }
        }
    }

    true
}

pub fn verify_linked_pairs(pairs: &[&(usize, usize)], groups: &[&GroupedSample]) -> usize {
    pairs
        .iter()
        .filter(|pair| !verify_linked_pair(**pair, groups))
        .count()
}

pub fn verify_linked_pair(pair: &(usize, usize), groups: &[&GroupedSample]) -> bool {
    let (left_index, right_index) = pair;
    let left = &groups[*left_index];
    let right = &groups[*right_index];

    // basically, left and right are assumed to be linked (aka. from the same user)
    // we verify this by checking the user id associated with both samples

    // note the invariable here: samples are grouped by device id, thus all samples
    // in a group must share the same device id, and thus must share the same user id

    let result = left.user_id == right.user_id;

    // report wrong pairs when requested
    if cfg!(feature = "intra_map_report_wrong_pairs") && !result {
        println!(
            "!! WARNING: wrongly linked pair: left = {}, right = {}",
            left.user_id, right.user_id
        );
    }

    result
}

/**
Save the compatible pairs in npy format that could be read by subsequent python
scripts. Here, the catch is that the original python script for intramap saves
_dictionaries_ instead of the natively supported arrays.

Upon closer inspection, we notice that the original python scripts merely uses
the pickled dictionary part of the saved npy files, thus we can simply save
the rust dictionary in python's pickle format and skip the numpy intermediary
altogether. This requires very little code change in the subsequent python scripts
that rely the saved npy files.
**/
fn save_compatible_pairs_to_pickle(
    converted_compatible_pairs: &HashMap<String, Vec<String>>,
    filename: &str,
) -> Result<(), Box<dyn Error>> {
    let mut output = io::BufWriter::new(File::create(filename)?);

    // then save te dict in python's pickle format
    match serde_pickle::to_writer(&mut output, &converted_compatible_pairs, SerOptions::new()) {
        Ok(()) => Ok(()),
        Err(e) => Err(Box::new(e)),
    }
}

fn convert_compatible_pairs_to_pickle_dict(
    pairs: &[&CompatiblePairs],
    samples: &[&GroupedSample],
    dest: &mut HashMap<String, Vec<String>>,
) {
    for pair in pairs {
        let (index1, index2) = *pair;

        debug_assert_eq!(samples[*index1].protocol, samples[*index2].protocol);
        debug_assert_eq!(
            samples[*index1].protocol,
            extract_protocol_from_device_id(samples[*index1].device_id)
        );
        debug_assert_eq!(
            samples[*index2].protocol,
            extract_protocol_from_device_id(samples[*index2].device_id)
        );

        let id1 = samples[*index1].device_id.to_string();
        let id2 = samples[*index2].device_id.to_string();

        match dest.get_mut(id1.as_str()) {
            Some(arr) => arr.push(id2),
            None => {
                dest.insert(id1, vec![id2]);
                ()
            }
        }
    }
}

fn extract_protocol_from_device_id(device_id: &str) -> ObservedProtocol {
    let m = Regex::new(r"pedestrian_.+_([WLB])_.+").unwrap();
    let g = match m.captures(device_id).unwrap().get(1) {
        None => panic!("cannot find protocol id"),
        Some(f) => f.as_str(),
    };
    match g {
        "W" => ObservedProtocol::WIFI,
        "B" => ObservedProtocol::BLE,
        "L" => ObservedProtocol::LTE,
        _ => panic!("not possible"),
    }
}

