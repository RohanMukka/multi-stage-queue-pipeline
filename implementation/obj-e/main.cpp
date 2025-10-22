#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>
#include <filesystem>

struct Task {
    int device_id;
    char type;
    int duration;
};

struct Job {
    std::string id;
    int arrival;
    std::vector<Task> tasks;
};

// ---------------------------
// Utility helpers
// ---------------------------

std::string trim(const std::string &s) {
    size_t start = s.find_first_not_of(" \t\n\r");
    size_t end = s.find_last_not_of(" \t\n\r");
    return (start == std::string::npos) ? "" : s.substr(start, end - start + 1);
}

Task parseTask(const std::string &s) {
    Task t;
    std::stringstream ss(s);
    std::string device_str, type_str;
    int duration;
    std::getline(ss, device_str, ':');
    ss >> type_str >> duration;
    t.device_id = std::stoi(trim(device_str));
    t.type = type_str[0];
    t.duration = duration;
    return t;
}

std::vector<Task> parseTasks(const std::string &taskField) {
    std::vector<Task> tasks;
    std::string cleaned = taskField;
    cleaned.erase(std::remove(cleaned.begin(), cleaned.end(), '['), cleaned.end());
    cleaned.erase(std::remove(cleaned.begin(), cleaned.end(), ']'), cleaned.end());
    cleaned.erase(std::remove(cleaned.begin(), cleaned.end(), '"'), cleaned.end());

    std::stringstream ss(cleaned);
    std::string task_str;
    while (std::getline(ss, task_str, ',')) {
        task_str = trim(task_str);
        if (!task_str.empty())
            tasks.push_back(parseTask(task_str));
    }
    return tasks;
}

std::vector<Job> readJobsFromCSV(const std::string &filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: could not open " << filename << "\n";
        return {};
    }

    std::string line;
    std::getline(file, line); // skip header

    std::vector<Job> jobs;
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        std::stringstream ss(line);
        std::string job_id, arrival_str, tasks_str;
        std::getline(ss, job_id, ',');
        std::getline(ss, arrival_str, ',');
        std::getline(ss, tasks_str);

        Job job;
        job.id = trim(job_id);
        job.arrival = std::stoi(trim(arrival_str));
        job.tasks = parseTasks(tasks_str);
        jobs.push_back(job);
    }

    return jobs;
}

void writeJobsToCSV(const std::string &filename, const std::vector<Job> &jobs) {
    std::ofstream out(filename);
    out << "job_id,arrival,tasks\n";
    for (const auto &job : jobs) {
        out << job.id << "," << job.arrival << ",[";
        for (size_t i = 0; i < job.tasks.size(); ++i) {
            const auto &t = job.tasks[i];
            out << "\"" << t.device_id << ": " << t.type << " " << t.duration << "\"";
            if (i < job.tasks.size() - 1) out << ", ";
        }
        out << "]\n";
    }
}

// ---------------------------
// Main simulation
// ---------------------------

int main() {
    // Change this to match your starting file name
    std::string inputFile = "in.csv";
    int queueCount = 5;

    std::cout << "Looking for input file in: " 
              << std::filesystem::current_path() << "\n";

    std::vector<Job> jobs = readJobsFromCSV(inputFile);
    if (jobs.empty()) {
        std::cerr << "No jobs loaded. Exiting.\n";
        return 1;
    }

    std::cout << "Loaded " << jobs.size() << " jobs into q0\n";

    for (int q = 0; q < queueCount; ++q) {
        std::vector<Job> remainingJobs;

        for (auto &job : jobs) {
            if (!job.tasks.empty()) {
                // Simulate queue processing ONE task per job
                job.tasks.erase(job.tasks.begin());
            }

            // Keep job if it still has tasks remaining
            if (!job.tasks.empty()) {
                remainingJobs.push_back(job);
            }
        }

        std::string outFile = "out" + std::to_string(q) + ".csv";
        writeJobsToCSV(outFile, remainingJobs);
        std::cout << "Wrote final output for q" << q << " → " << outFile << "\n";

        // Remaining jobs become input for next queue
        jobs = remainingJobs;
        if (jobs.empty()) break;
    }

    std::cout << "Simulation finished.\n";
    return 0;
}
