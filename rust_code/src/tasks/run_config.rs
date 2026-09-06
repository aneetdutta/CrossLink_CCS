use std::fmt::format;
use std::fs::{File, read};
use std::io;
use std::io::Read;
use std::path::{Path, PathBuf};
use yaml_rust2::YamlLoader;

#[derive(Debug)]
pub struct RunConfig<'a> {
    pub root_dir: PathBuf,
    pub name: &'a str,

    pub ble_range: f32,
    pub wifi_range: f32,
    pub lte_range: f32,

    pub acceptable_moving_rate: f32,

    pub intra_map_trim_threshold: usize,
    pub intra_map_trim_grace_period: u32,
    pub intra_map_time_delta_threshold: u32,

    pub inter_map_grace_period: u32,

    pub ble_localization_error: f32,
    pub wifi_localization_error: f32,
    pub lte_localization_error: f32,
}

impl<'a> RunConfig<'a> {
    pub fn config_dir(&self) -> PathBuf {
        Path::new(&self.root_dir).join("configs")
    }

    pub fn config_filename(&self) -> PathBuf {
        self.config_dir().join(format!("{}.yml", self.name))
    }

    pub fn generic_data_dir(&self) -> PathBuf {
        Path::new(&self.root_dir).join("data")
    }

    pub fn dedicated_data_dir(&self) -> PathBuf {
        self.generic_data_dir().join(self.name)
    }

    pub fn user_sample_filename(&self) -> String {
        self.dedicated_data_dir()
            .join(format!("user_data_{}.csv", self.name))
            .to_str()
            .unwrap()
            .to_string()
    }

    pub fn from(dir: &'a str, name: &'a str) -> RunConfig<'a> {
        let mut config = RunConfig {
            root_dir: PathBuf::from(dir),
            name,
            ble_range: 0f32,
            wifi_range: 0f32,
            lte_range: 0f32,
            acceptable_moving_rate: 0f32,
            intra_map_trim_threshold: 0,
            intra_map_trim_grace_period: 0u32,
            intra_map_time_delta_threshold: 0u32,
            inter_map_grace_period: 0u32,
            ble_localization_error: 1.5f32,
            wifi_localization_error: 5f32,
            lte_localization_error: 10f32,
        };

        let mut buf = String::new();
        File::open(config.config_filename())
            .unwrap()
            .read_to_string(&mut buf)
            .unwrap();
        let yaml_owned = YamlLoader::load_from_str(&buf).unwrap();
        let yaml = &yaml_owned[0];

        let parse_f32 = |val: &yaml_rust2::Yaml, default: f32| -> f32 {
            if let Some(f) = val.as_f64() {
                f as f32
            } else if let Some(i) = val.as_i64() {
                i as f32
            } else {
                default
            }
        };

        config.ble_localization_error = parse_f32(
            &yaml["localization_errors"]["BLUETOOTH_LOCALIZATION_ERROR"],
            1.5f32,
        );
        config.wifi_localization_error = parse_f32(
            &yaml["localization_errors"]["WIFI_LOCALIZATION_ERROR"],
            5f32,
        );
        config.lte_localization_error = parse_f32(
            &yaml["localization_errors"]["LTE_LOCALIZATION_ERROR"],
            10f32,
        );

        config.ble_range = yaml["communication_range"]["BLUETOOTH_RANGE"]
            .as_i64()
            .unwrap() as f32;
        config.wifi_range = yaml["communication_range"]["WIFI_RANGE"].as_i64().unwrap() as f32;
        config.lte_range = yaml["communication_range"]["LTE_RANGE"].as_i64().unwrap() as f32;

        config.acceptable_moving_rate =
            yaml["mobility"]["MAX_MOBILITY_FACTOR"].as_f64().unwrap() as f32;

        config.intra_map_trim_threshold = yaml["accel_settings"]["intra_map"]["trim_threshold"]
            .as_i64()
            .unwrap() as usize;
        config.intra_map_trim_grace_period =
            yaml["accel_settings"]["intra_map"]["trim_grace_period"]
                .as_i64()
                .unwrap() as u32;
        config.intra_map_time_delta_threshold =
            yaml["accel_settings"]["intra_map"]["time_delta_threshold"]
                .as_i64()
                .unwrap() as u32;
        config.inter_map_grace_period = yaml["accel_settings"]["intra_map"]["time_delta_threshold"]
            .as_i64()
            .unwrap() as u32;

        config
    }
}
