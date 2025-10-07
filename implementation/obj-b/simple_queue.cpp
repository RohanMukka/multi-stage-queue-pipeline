#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <queue>
#include <string>
#include <regex>
#include <unordered_map>
#include <optional>
using namespace std;

// Each task keeps both its original index and workload
struct Task {
    int index;
    int work;
};

struct Job {
    string id;
    int arrival;
    vector<Task> tasks;
};

struct ActiveJob {
    Job job;
    int currentTask = 0;
    int service_time_left = 0;
};

string trim(const string &s) {
    auto start = s.find_first_not_of(" \t\r\n");
    auto end = s.find_last_not_of(" \t\r\n");
    if (start == string::npos) return "";
    return s.substr(start, end - start + 1);
}

// Parse "0: W 10", "1: W 20" into vector<Task>
vector<Task> parseTasks(const string &taskStr) {
    regex workloadRegex(R"((\d+):\s*W\s*(\d+))");
    vector<Task> tasks;
    for (auto it = sregex_iterator(taskStr.begin(), taskStr.end(), workloadRegex);
         it != sregex_iterator(); ++it) {
        int idx = stoi((*it)[1].str());
        int val = stoi((*it)[2].str());
        tasks.push_back({idx, val});
    }
    return tasks;
}

unordered_map<string, string> readConfig(const string &cfgFile) {
    unordered_map<string, string> config;
    ifstream infile(cfgFile);
    string line;
    while (getline(infile, line)) {
        if (line.empty()) continue;
        stringstream ss(line);
        string key, val;
        getline(ss, key, ',');
        getline(ss, val, ',');
        key = trim(key);
        val = trim(val);
        if (!key.empty() && key != "parameter")
            config[key] = val;
    }
    return config;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " <jobs_file.csv> <simple-queue-config.csv>\n";
        return 1;
    }

    string filename = argv[1];
    string cfgFile = argv[2];
    auto cfg = readConfig(cfgFile);

    int limit = stoi(cfg["limit"]);
    int max_q = stoi(cfg["max_queue_size"]);
    string qid = cfg["queue_id"], sid = cfg["server_id"];
    int rate = stoi(cfg["server_function_rate"]);

    string sinkFile = cfg.count("sink") ? cfg["sink"] : "out0.wl";
    ofstream sinkOut(sinkFile);
    sinkOut << "job_id,arrival,Tasks\n";

    ofstream jlog("job.log");
    ofstream qmet("qmet.csv");
    qmet << "time-step,queue-sys-id,num-jobs-in-queue,num-jobs-in-service,num-of-errors\n";

    // Load jobs
    ifstream in(filename);
    if (!in.is_open()) {
        cerr << "Error opening jobs file: " << filename << endl;
        return 1;
    }

    string line;
    vector<Job> jobs;
    while (getline(in, line)) {
        if (line.empty()) continue;
        stringstream ss(line);
        string id, arrStr, taskStr;
        getline(ss, id, ',');
        getline(ss, arrStr, ',');
        getline(ss, taskStr, '\n');
        id = trim(id);
        arrStr = trim(arrStr);
        taskStr = trim(taskStr);
        if (id == "job_id") continue;

        if (!taskStr.empty() && taskStr.front() == '"')
            taskStr = taskStr.substr(1, taskStr.size() - 2);

        // Fix duplicated quotes if any
        for (size_t pos = taskStr.find("\"\""); pos != string::npos; pos = taskStr.find("\"\"", pos))
            taskStr.replace(pos, 2, "\"");

        int arr = stoi(arrStr);
        vector<Task> tasks = parseTasks(taskStr);
        jobs.push_back({id, arr, tasks});
    }

    queue<Job> q;
    optional<ActiveJob> current;
    int clock = 0, errors = 0;

    while (clock < limit) {
        // Handle arrivals
        while (!jobs.empty() && jobs.front().arrival == clock) {
            Job j = jobs.front();
            jobs.erase(jobs.begin());
            jlog << clock << " " << j.id << " IN " << qid << " ARRIVE-VIA " << filename << "\n";
            if ((int)q.size() >= max_q) {
                errors++;
                jlog << clock << " " << j.id << " IN " << qid << " ERROR QUEUE-FULL\n";
            } else q.push(j);
        }

        // Process one job at Sub-X rate
        if (current && clock % rate == rate - 1) {
            Job &jb = current->job;

            // Remove the first completed task
            if (!jb.tasks.empty())
                jb.tasks.erase(jb.tasks.begin());

            jlog << clock << " " << jb.id << " IN " << qid
                 << " EXITS-SERVER " << sid << "\n";
            jlog << clock << " " << jb.id << " IN " << qid
                 << " DEPART-VIA " << sinkFile << "\n";

            // ✅ Print remaining tasks (keep original indices)
            if (!jb.tasks.empty()) {
                sinkOut << jb.id << "," << clock + 1 << ",[";
                for (size_t i = 0; i < jb.tasks.size(); ++i) {
                    sinkOut << "\"" << jb.tasks[i].index << ": W " << jb.tasks[i].work << "\"";
                    if (i + 1 < jb.tasks.size()) sinkOut << ", ";
                }
                sinkOut << "]\n";
            }

            current.reset();
        }

        // Move next job into service if free
        if (!current && !q.empty()) {
            Job j = q.front(); q.pop();
            current = ActiveJob{j, 0, j.tasks.empty() ? 0 : j.tasks[0].work};
            jlog << clock << " " << j.id << " IN " << qid
                 << " ENTERS-SERVER " << sid << "\n";
        }

        qmet << clock << "," << qid << "," << q.size() << "," << (current ? 1 : 0) << "," << errors << "\n";
        clock++;
    }

    cout << "Simulation complete. Outputs: qmet.csv, job.log, " << sinkFile << "\n";
    return 0;
}