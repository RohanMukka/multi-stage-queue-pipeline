#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <queue>
#include <tuple>
#include <string>
#include <regex>
#include <algorithm>
#include <unordered_map>

using namespace std;

struct Job {
    string id;
    int arrival;
    int service;
};

// Helper to trim whitespace
string trim(const string& s) {
    auto start = s.find_first_not_of(" \t\r\n");
    auto end = s.find_last_not_of(" \t\r\n");
    if (start == string::npos) return "";
    return s.substr(start, end - start + 1);
}

// Parse tasks string into total service time
int parseTasks(const string& taskStr) {
    regex numberRegex(R"((\d+))");
    int total = 0;

    auto begin = sregex_iterator(taskStr.begin(), taskStr.end(), numberRegex);
    auto end = sregex_iterator();
    for (auto i = begin; i != end; ++i) {
        total += stoi((*i).str());
    }
    return total;
}

// Read config CSV into a map
unordered_map<string,string> readConfig(const string& cfgFile) {
    unordered_map<string,string> config;
    ifstream infile(cfgFile);
    if (!infile.is_open()) {
        cerr << "Error opening config file: " << cfgFile << endl;
        exit(1);
    }

    string line;
    while (getline(infile, line)) {
        if (line.empty()) continue;
        stringstream ss(line);
        string key, value;
        getline(ss, key, ',');
        getline(ss, value, ',');
        key = trim(key);
        value = trim(value);
        if (!key.empty() && key != "parameter") {
            config[key] = value;
        }
    }
    infile.close();
    return config;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " <jobs_file.csv> <simple-queue-config.csv>\n";
        return 1;
    }

    string filename = argv[1];
    string cfgFile = argv[2];

    // --- Read config ---
    auto config = readConfig(cfgFile);

    int limit = stoi(config["limit"]);
    int max_queue_size = stoi(config["max_queue_size"]);
    string queue_id = config["queue_id"];
    string server_id = config["server_id"];

    // --- Read jobs file ---
    ifstream infile(filename);
    if (!infile.is_open()) {
        cerr << "Error opening jobs file: " << filename << endl;
        return 1;
    }

    vector<Job> jobs;
    string line;
    while (getline(infile, line)) {
        if (line.empty()) continue;

        stringstream ss(line);
        string id, arrivalStr, taskStr;

        getline(ss, id, ',');
        getline(ss, arrivalStr, ',');
        getline(ss, taskStr, '\n');

        id = trim(id);
        arrivalStr = trim(arrivalStr);
        taskStr = trim(taskStr);

        if (id == "job_id" || arrivalStr == "arrival") continue;

        if (!taskStr.empty() && taskStr.front() == '"') {
            taskStr = taskStr.substr(1, taskStr.size() - 2);
        }

        try {
            int arrival = stoi(arrivalStr);
            int service = parseTasks(taskStr);
            jobs.push_back({id, arrival, service});
        } catch (const exception& e) {
            cerr << "Parse error on line: " << line << "\n";
            cerr << "  what(): " << e.what() << "\n";
        }
    }
    infile.close();

    // --- Simulation setup ---
    int clock = 0;
    int errors = 0;

    queue<Job> work_queue;
    string job_in_service = "";
    int service_time_left = 0;

    ofstream qmet("qmet.csv");
    qmet << "time-step,queue-sys-id,num-jobs-in-queue,num-jobs-in-service,num-of-errors\n";

    ofstream jlog("job.log");

    // --- Simulation loop ---
    while (clock < limit) {
        string input_edge = filename;
        size_t pos = filename.find_last_of("/\\");
        if (pos != string::npos) input_edge = filename.substr(pos + 1);

        // --- Handle new arrivals ---
        while (!jobs.empty() && jobs.front().arrival == clock) {
            Job j = jobs.front();
            jobs.erase(jobs.begin());

            jlog << clock << " " << j.id << " IN " << queue_id << " ARRIVE-VIA " << input_edge << "\n";

            if ((int)work_queue.size() >= max_queue_size) {
                errors++;
                jlog << clock << " " << j.id << " IN " << queue_id << " ERROR QUEUE-FULL\n";
            } else {
                work_queue.push(j);
            }
        }

        // --- Process server job ---
        if (!job_in_service.empty()) {
            service_time_left--;

            if (service_time_left == 0) {
                jlog << clock << " " << job_in_service << " IN " << queue_id 
                     << " TASK-END 0 \"W " << service_time_left+1 << "\"\n";
                jlog << clock << " " << job_in_service << " IN " << queue_id 
                     << " EXITS-SERVER " << server_id << "\n";
                job_in_service = "";
            }
        }

        // --- Move job from queue to server if free ---
        if (job_in_service.empty() && !work_queue.empty()) {
            Job j = work_queue.front();
            work_queue.pop();
            job_in_service = j.id;
            service_time_left = j.service;

            jlog << clock << " " << job_in_service << " IN " << queue_id 
                 << " ENTERS-SERVER " << server_id << "\n";
            jlog << clock << " " << job_in_service << " IN " << queue_id 
                 << " TASK-START 0 \"W " << service_time_left << "\"\n";
        }

        // --- Write queue metrics ---
        int num_in_queue = (int)work_queue.size();
        int num_in_service = job_in_service.empty() ? 0 : 1;
        qmet << clock << "," << queue_id << "," << num_in_queue << "," 
             << num_in_service << "," << errors << "\n";

        clock++;
    }

    qmet.close();
    jlog.close();

    cout << "Simulation complete. Queue metrics written to qmet.csv and job.log\n";
    return 0;
}
