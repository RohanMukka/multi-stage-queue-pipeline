// SingleQueue.h
#pragma once
#include <queue>
#include <vector>
#include <string>
#include <optional>
#include <unordered_map>

struct Task {
    int index;
    int work;
};

struct Job {
    std::string id;
    int arrival;
    std::vector<Task> tasks;
};

struct ActiveJob {
    Job job;
    int currentTask = 0;
    int service_time_left = 0;
};

class SingleQueue {
public:
    SingleQueue(const std::string &queueId, int maxQueueSize, int serverRate, int numServers);

    void addArrivingJobs(const std::vector<Job>& arrivingJobs, int clock);
    void step(int clock, std::unordered_map<std::string, SingleQueue*> &network); // step one timestep
    bool hasJobs() const;

    // Metrics
    int queueSize() const;
    int busyServers() const;
    const std::string& id() const;
    std::vector<std::string> edgesOut; // queue IDs this queue feeds into

private:
    std::string queueId;
    int maxQueueSize;
    int serverRate;
    int numServers;
    std::queue<Job> q;
    std::vector<std::optional<ActiveJob>> servers;
    int errors = 0;

    void processServers(int clock, std::unordered_map<std::string, SingleQueue*> &network);
};
