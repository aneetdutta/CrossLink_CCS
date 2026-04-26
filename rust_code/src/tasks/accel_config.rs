use std::fs::File;
use std::io::Read;
use std::path::PathBuf;
use yaml_rust2::YamlLoader;

pub struct AccelConfig {
    pub root_dir: PathBuf,
}

impl AccelConfig {
    pub fn from(root_dir: &str) -> AccelConfig {
        let mut config_src = String::new();
        File::open(root_dir)
            .unwrap()
            .read_to_string(&mut config_src)
            .unwrap();
        let all_yaml_documents = YamlLoader::load_from_str(&config_src).unwrap();
        let actual_config = all_yaml_documents.first().unwrap();

        AccelConfig {
            root_dir: PathBuf::from(actual_config["root_dir"].as_str().unwrap()),
        }
    }
}
