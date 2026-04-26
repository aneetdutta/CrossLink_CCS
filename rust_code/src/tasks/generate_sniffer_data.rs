use super::common::*;
use super::run_config::RunConfig;
use binrw;
use binrw::{BinReaderExt, BinWrite, BinWriterExt};
use rayon::prelude::*;
use serde_json::Value;
use serde_pickle::{DeOptions, SerOptions};
use std::error::Error;
use std::fs::File;
use std::io;
use std::io::{BufWriter, Read, Seek, SeekFrom, Write};
use std::path::PathBuf;
use std::str::FromStr;
use std::time::Instant;
use serde::Serialize;

pub trait GenerateSnifferObservations {
    fn generate_sniffer_data(&self);
    fn load_sniffer_observations_binary(&self) -> Vec<ObservationSample>;
    fn sniffer_observations_binary_filename(&self) -> PathBuf;
    fn sniffer_locations_filename(&self) -> PathBuf;
}

impl<'a> GenerateSnifferObservations for RunConfig<'a> {
    fn generate_sniffer_data(&self) {
        println!("\n\n ==* running task: generate_sniffer_observations");

        let start = Instant::now();
        println!(
            "loading user samples from: {:?}",
            self.user_sample_filename()
        );
        let user_samples = load_user_samples(self.user_sample_filename().as_str()).unwrap();
        println!("loaded {} user samples", user_samples.len());

        let sniffer_locations =
            load_sniffer_locations(self.sniffer_locations_filename().to_str().unwrap()).unwrap();
        println!("loaded {} sniffer locations", sniffer_locations.len());

        let elapsed = start.elapsed();
        println!("load elapsed: {:?}", elapsed);

        let compute_start = Instant::now();
        let observation_samples = generate_observation_samples(
            &sniffer_locations,
            &user_samples,
            self.ble_range,
            self.wifi_range,
            self.lte_range,
        )
        .into_iter()
        .flatten()
        .collect::<Vec<_>>();
        let compute_elapsed = compute_start.elapsed();
        println!("compute elapsed: {:?}", compute_elapsed);

        let save_start = Instant::now();
        let filename = self
            .sniffer_observations_binary_filename()
            .to_str()
            .unwrap()
            .to_string();
        save_observation_samples(filename.as_str(), &observation_samples)
            .expect("unable to save observation samples to disk");
        println!("saved {:?} observations", observation_samples.len());
        let save_elapsed = save_start.elapsed();
        println!("save elapsed: {:?}", save_elapsed);

        // let loaded = load_observation_samples(filename.as_str())
        //     .expect("unable to load observation samples from disk");
        // assert_eq!(observation_samples, loaded);
    }

    fn load_sniffer_observations_binary(&self) -> Vec<ObservationSample> {
        load_observation_samples(
            self.sniffer_observations_binary_filename()
                .to_str()
                .unwrap(),
        )
        .expect("unable to load sniffer observations binary from disk")
    }

    fn sniffer_observations_binary_filename(&self) -> PathBuf {
        self.dedicated_data_dir()
            .join(format!("sniffed_data_{}.bin", self.name))
    }

    fn sniffer_locations_filename(&self) -> PathBuf {
        self.root_dir
            .join("sniffer_location")
            //.join("full_coverage_wifi_sniffer_location.json")
            .join("handover_sniffer_location_r100_2.json")
    }
}

pub fn load_user_samples(filename: &str) -> Result<Vec<UserTraceSample>, Box<dyn Error>> {
    let mut reader = csv::Reader::from_path(filename)?;
    let mut samples: Vec<UserTraceSample> = Vec::new();
    for record in reader.records() {
        let line = record?;
        samples.push(UserTraceSample {
            timestep: f32::from_str(&line[0])? as u32,
            user_id: String::from(&line[1]),
            loc: Location {
                x: f32::from_str(&line[2])?,
                y: f32::from_str(&line[3])?,
            },
            ble_id: String::from(&line[4]),
            wifi_id: String::from(&line[5]),
            lte_id: String::from(&line[6]),
            transmit_ble: bool::from_str(&line[7])?,
            transmit_wifi: bool::from_str(&line[8])?,
            transmit_lte: bool::from_str(&line[9])?,
        })
    }

    Ok(samples)
}

pub fn load_sniffer_locations(filename: &str) -> Result<Vec<Sniffer>, Box<dyn Error>> {
    let json_src = std::fs::read_to_string(filename).unwrap();
    let src: Value = serde_json::from_str(&json_src).unwrap();

    let mut sniffers: Vec<Sniffer> = Vec::new();
    let mut count: u16 = 0;
    for s in src["sniffer_location"].as_array().unwrap() {
        let ss = s.as_array().unwrap();
        sniffers.push(Sniffer {
            id: count,
            loc: Location {
                x: ss[0].as_f64().unwrap() as f32,
                y: ss[1].as_f64().unwrap() as f32,
            },
        });

        count += 1
    }

    Ok(sniffers)
}

pub fn generate_observation_samples(
    sniffers: &[Sniffer],
    user_samples: &[UserTraceSample],
    ble_range: f32,
    wifi_range: f32,
    lte_range: f32,
) -> Vec<Vec<ObservationSample>> {
    sniffers
        .par_iter()
        .map(|s| {
            generate_observation_samples_for_one(
                s,
                user_samples,
                ble_range,
                wifi_range,
                lte_range,
            )
        })
        .collect()
}

pub fn generate_observation_samples_for_one(
    sniffer: &Sniffer,
    user_samples: &[UserTraceSample],
    ble_range: f32,
    wifi_range: f32,
    lte_range: f32,
) -> Vec<ObservationSample> {
    fn make_observation_sample(
        sniffer: &Sniffer,
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
            sniffer: *sniffer,
            distance,
            protocol: observed_proc,
        }
    }

    let mut observation_samples = Vec::new();
    for sample in user_samples.iter() {
        let distance = distance_squared_between(&sniffer.loc, &sample.loc).sqrt();

        if sample.transmit_ble && distance < ble_range {
            observation_samples.push(make_observation_sample(
                &sniffer,
                distance,
                sample,
                ObservedProtocol::BLE,
                sample.ble_id.as_str(),
            ))
        }

        if sample.transmit_wifi && distance < wifi_range {
            observation_samples.push(make_observation_sample(
                &sniffer,
                distance,
                sample,
                ObservedProtocol::WIFI,
                sample.wifi_id.as_str(),
            ))
        }

        if sample.transmit_lte && distance < lte_range {
            observation_samples.push(make_observation_sample(
                &sniffer,
                distance,
                sample,
                ObservedProtocol::LTE,
                sample.lte_id.as_str(),
            ))
        }
    }

    observation_samples
}

pub fn save_observation_samples(
    filename: &str,
    observation_samples: &[ObservationSample],
) -> Result<(), Box<dyn Error>> {
    let mut output = io::BufWriter::new(File::create(filename)?);
    postcard::to_io(observation_samples, &mut output)?;

    Ok(())
}

pub fn load_observation_samples(filename: &str) -> Result<Vec<ObservationSample>, Box<dyn Error>> {
    let mut input = io::BufReader::new(File::open(filename)?);
    let mut buf = [0u8; 2048];
    let (vec, _) = postcard::from_io((&mut input, &mut buf))?;

    Ok(vec)
}
