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
#include <optional>

using namespace std;

struct Job
{
    string id;
    int arrival;
    vector<int> tasks; // workloads for each task
};

// Struct to manage the active job and its current task
struct ActiveJob
{
    Job job;
    int currentTask = 0;
    int service_time_left = 0;
};

// Helper to trim whitespace
string trim(const string &s)
{
    auto start = s.find_first_not_of(" \t\r\n");
    auto end = s.find_last_not_of(" \t\r\n");
    if (start == string::npos)
        return "";
    return s.substr(start, end - start + 1);
}

// Parse tasks string into vector of workloads
vector<int> parseTasks(const string &taskStr)
{
    regex workloadRegex(R"(W\s+(\d+))"); // capture numbers after 'W '
    vector<int> tasks;

    auto begin = sregex_iterator(taskStr.begin(), taskStr.end(), workloadRegex);
    auto end = sregex_iterator();
    for (auto i = begin; i != end; ++i)
    {
        tasks.push_back(stoi((*i)[1].str())); // group(1) = workload
    }
    return tasks;
}

// Read config CSV into a map
unordered_map<string, string> readConfig(const string &cfgFile)
{
    unordered_map<string, string> config;
    ifstream infile(cfgFile);
    if (!infile.is_open())
    {
        cerr << "Error opening config file: " << cfgFile << endl;
        exit(1);
    }

    string line;
    while (getline(infile, line))
    {
        if (line.empty())
            continue;
        stringstream ss(line);
        string key, value;
        getline(ss, key, ',');
        getline(ss, value, ',');
        key = trim(key);
        value = trim(value);
        if (!key.empty() && key != "parameter")
        {
            config[key] = value;
        }
    }
    infile.close();
    return config;
}

int main(int argc, char *argv[])
{
    if (argc < 3)
    {
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
    if (!infile.is_open())
    {
        cerr << "Error opening jobs file: " << filename << endl;
        return 1;
    }

    vector<Job> jobs;
    string line;
    while (getline(infile, line))
    {
        if (line.empty())
            continue;

        stringstream ss(line);
        string id, arrivalStr, taskStr;

        getline(ss, id, ',');
        getline(ss, arrivalStr, ',');
        getline(ss, taskStr, '\n');

        id = trim(id);
        arrivalStr = trim(arrivalStr);
        taskStr = trim(taskStr);

        if (id == "job_id" || arrivalStr == "arrival")
            continue;

        if (!taskStr.empty() && taskStr.front() == '"')
        {
            taskStr = taskStr.substr(1, taskStr.size() - 2);
        }

        try
        {
            int arrival = stoi(arrivalStr);
            vector<int> tasks = parseTasks(taskStr);
            jobs.push_back({id, arrival, tasks});
        }
        catch (const exception &e)
        {
            cerr << "Parse error on line: " << line << "\n";
            cerr << "  what(): " << e.what() << "\n";
        }
    }
    infile.close();

    // --- Simulation setup ---
int clock = 0;
int errors = 0;

queue<Job> work_queue;

optional<ActiveJob> current_job;

// --- Load new server function config ---
int server_function_rate = stoi(config["server_function_rate"]);
int server_function = stoi(config["server_function"]);

ofstream qmet("qmet.csv");
qmet << "time-step,queue-sys-id,num-jobs-in-queue,num-jobs-in-service,num-of-errors\n";

ofstream jlog("job.log");

// --- Simulation loop ---
while (clock < limit)
{
    string input_edge = filename;
    size_t pos = filename.find_last_of("/\\");
    if (pos != string::npos)
        input_edge = filename.substr(pos + 1);

    // --- Handle new arrivals ---
    while (!jobs.empty() && jobs.front().arrival == clock)
    {
        Job j = jobs.front();
        jobs.erase(jobs.begin());

        jlog << clock << " " << j.id << " IN " << queue_id << " ARRIVE-VIA " << input_edge << "\n";

        if ((int)work_queue.size() >= max_queue_size)
        {
            errors++;
            jlog << clock << " " << j.id << " IN " << queue_id << " ERROR QUEUE-FULL\n";
        }
        else
        {
            work_queue.push(j);
        }
    }

    // --- Process server job ---
    if (current_job.has_value())
    {
        // Process workload only at defined rate
        if (clock % server_function_rate == server_function_rate - 1)
        {
            current_job->service_time_left -= server_function;

            // Task finished
            if (current_job->service_time_left <= 0)
            {
                jlog << clock << " " << current_job->job.id << " IN " << queue_id
                     << " TASK-END " << current_job->currentTask
                     << " \"W " << max(0, current_job->service_time_left) << "\"\n";

                current_job->currentTask++;

                // Move to next task if any remain
                if (current_job->currentTask < (int)current_job->job.tasks.size())
                {
                    current_job->service_time_left = current_job->job.tasks[current_job->currentTask];

                    jlog << clock << " " << current_job->job.id << " IN " << queue_id
                         << " TASK-START " << current_job->currentTask
                         << " \"W " << current_job->service_time_left << "\"\n";
                }
                else
                {
                    // Job fully complete
                    jlog << clock << " " << current_job->job.id << " IN " << queue_id
                         << " EXITS-SERVER " << server_id << "\n";
                    current_job.reset();
                }
            }
        }
    }

    // --- Move next job from queue into service if free ---
    if (!current_job.has_value() && !work_queue.empty())
    {
        Job j = work_queue.front();
        work_queue.pop();

        current_job = ActiveJob{j, 0, j.tasks[0]};

        jlog << clock << " " << j.id << " IN " << queue_id
             << " ENTERS-SERVER " << server_id << "\n";
        jlog << clock << " " << j.id << " IN " << queue_id
             << " TASK-START 0 \"W " << current_job->service_time_left << "\"\n";
    }

    // --- Write queue metrics ---
    int num_in_queue = (int)work_queue.size();
    int num_in_service = current_job.has_value() ? 1 : 0;
    qmet << clock << "," << queue_id << "," << num_in_queue << ","
         << num_in_service << "," << errors << "\n";

    clock++;
}

qmet.close();
jlog.close();

cout << "Simulation complete. Queue metrics written to qmet.csv and job.log\n";
return 0;
}
