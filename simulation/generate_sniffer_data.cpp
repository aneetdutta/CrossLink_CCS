#include <iostream>
#include <vector>
#include <cmath>
#include <deque>
#include <string>
#include <unordered_map>
#include <fstream>
#include <sstream>
#include <json/json.h> // For parsing JSON (use a suitable JSON library)
#include <algorithm>

bool strToBool(const std::string& str) {
    return str == "true" || str == "1";
}

std::vector<std::pair<double, double>> loadSnifferLocations(bool enable_partial_coverage) {
    std::string file_path = enable_partial_coverage
        ? "sniffer_location/partial_coverage_sniffer_location_1.json"
        : "sniffer_location/full_coverage_wifi_sniffer_location.json";

    std::ifstream file(file_path);
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << file_path << std::endl;
        exit(1);
    }

    Json::Value root;
    file >> root;
    file.close();

    std::vector<std::pair<double, double>> sniffer_locations;
    const auto& locations = root["sniffer_location"];
    for (const auto& loc : locations) {
        double x = loc[0].asDouble();
        double y = loc[1].asDouble();
        sniffer_locations.emplace_back(x, y);
    }

    std::cout << "Loaded " << sniffer_locations.size() << " sniffer locations from " << file_path << std::endl;
    return sniffer_locations;
}

struct DetectedUser {
    double timestep;
    std::string user_id; // Changed from int to std::string
    int sniffer_id;
    double sl_x, sl_y, ul_x, ul_y;
    std::string protocol;
    std::string id;
};

class Sniffer {
public:
    int id;
    std::pair<double, double> location;
    double bluetooth_range;
    double wifi_range;
    double lte_range;

    Sniffer(int sniffer_id, std::pair<double, double> loc, double ble_range, double wifi_range, double lte_range)
        : id(sniffer_id), location(loc), bluetooth_range(ble_range), wifi_range(wifi_range), lte_range(lte_range) {}

    std::vector<DetectedUser> detectRawUsers(
        std::string user_id,
        double timestep,
        std::pair<double, double> user_location,
        const std::string& user_lte_id = "",
        const std::string& user_wifi_id = "",
        const std::string& user_bluetooth_id = "",
        bool transmit_ble = false,
        bool transmit_wifi = false,
        bool transmit_lte = false) {

        std::vector<DetectedUser> detected_users;
        double distance = sqrt(pow(location.first - user_location.first, 2) +
                               pow(location.second - user_location.second, 2));

        if (distance <= bluetooth_range && transmit_ble) {
            detected_users.push_back({timestep, user_id, id, location.first, location.second,
                                       user_location.first, user_location.second, "Bluetooth", user_bluetooth_id});
        }
        if (distance <= wifi_range && transmit_wifi) {
            detected_users.push_back({timestep, user_id, id, location.first, location.second,
                                       user_location.first, user_location.second, "WiFi", user_wifi_id});
        }
        if (distance <= lte_range && transmit_lte) {
            detected_users.push_back({timestep, user_id, id, location.first, location.second,
                                       user_location.first, user_location.second, "LTE", user_lte_id});
        }

        return detected_users;
    }
};

std::vector<std::unordered_map<std::string, std::string>> readCSV(const std::string& filepath) {
    std::vector<std::unordered_map<std::string, std::string>> data;
    std::ifstream file(filepath);
    std::string line, header;

    if (file.is_open()) {
        std::getline(file, header);
        std::vector<std::string> headers;
        std::stringstream header_stream(header);
        std::string column;

        while (std::getline(header_stream, column, ',')) {
            headers.push_back(column);
        }

        while (std::getline(file, line)) {
            std::unordered_map<std::string, std::string> row;
            std::stringstream line_stream(line);
            for (const auto& head : headers) {
                std::getline(line_stream, column, ',');
                row[head] = column;
            }
            data.push_back(row);
        }
    }
    return data;
}

int main() {
    // Configuration variables
    double bluetooth_range = std::stod(std::getenv("BLUETOOTH_RANGE"));
    double wifi_range = std::stod(std::getenv("WIFI_RANGE"));
    double lte_range = std::stod(std::getenv("LTE_RANGE"));
    std::string scenario_name = std::getenv("SCENARIO_NAME");

    bool enable_partial_coverage = strToBool(std::getenv("ENABLE_PARTIAL_COVERAGE"));

    // Load sniffer locations based on configuration
    std::vector<std::pair<double, double>> sniffer_locations = loadSnifferLocations(enable_partial_coverage);

    std::cout << "Loaded " << scenario_name << std::endl;
    // Initialize sniffers
    std::vector<Sniffer> sniffers;
    for (size_t i = 0; i < sniffer_locations.size(); ++i) {
        sniffers.emplace_back(i, sniffer_locations[i], bluetooth_range, wifi_range, lte_range);
    }

    std::cout << "Loaded " << scenario_name << std::endl;
    // Load user data
    std::string user_data_file = "data/user_data_" + scenario_name + ".csv";
    auto raw_user_data = readCSV(user_data_file);

    std::cout << "Loaded 234" << scenario_name << std::endl;
    // Process user data
    std::deque<DetectedUser> detected_users;
    for (const auto& user_data : raw_user_data) {
        double loc_x = std::stod(user_data.at("loc_x"));
        double loc_y = std::stod(user_data.at("loc_y"));
        std::string user_id = user_data.at("user_id");
        std::cout << "Loaded 123 " << user_id  << std::endl;
        double timestep = std::stod(user_data.at("timestep"));


        bool transmit_ble = user_data.at("transmit_ble") == "true";
        bool transmit_wifi = user_data.at("transmit_wifi") == "true";
        bool transmit_lte = user_data.at("transmit_lte") == "true";

        for (auto& sniffer : sniffers) {
            auto detections = sniffer.detectRawUsers(
                user_id, timestep, {loc_x, loc_y},
                user_data.at("lte_id"), user_data.at("wifi_id"),
                user_data.at("bluetooth_id"), transmit_ble, transmit_wifi, transmit_lte);

            detected_users.insert(detected_users.end(), detections.begin(), detections.end());
        }
    }

    std::cout << "Loaded 123 " << scenario_name << std::endl;
    // Save detected users to CSV
    std::string output_file = "data/sniffed_data_1_" + scenario_name + ".csv";
    std::ofstream out_file(output_file);
    out_file << "timestep,user_id,sniffer_id,sl_x,sl_y,ul_x,ul_y,protocol,id\n";
    for (const auto& user : detected_users) {
        out_file << user.timestep << "," << user.user_id << "," << user.sniffer_id << ","
                 << user.sl_x << "," << user.sl_y << "," << user.ul_x << "," << user.ul_y << ","
                 << user.protocol << "," << user.id << "\n";
    }

    std::cout << "Saved file to the directory: " << output_file << std::endl;
    return 0;
}
