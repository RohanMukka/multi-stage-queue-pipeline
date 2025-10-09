// SingleQueue.cpp
#include "SingleQueue.h"
#include <iostream>

SingleQueue::SingleQueue(const std::string &queueId, int maxQueueSize, int serverRate, int numServers)
    : queueId(queueId), maxQueueSize(maxQueueSize), serverRate(serverRate), numServers(numServers), servers(numServers) {}

void SingleQueue::addArrivingJobs(const std::vector<Job>& arrivingJobs, int clock) {
    for (const auto& j : arrivingJobs) {
        if ((int)q.size() >= maxQueueSize) {
            errors++;
            std::cout << clock << " " << j.id << " IN " << queueId << " ERROR QUEUE-FULL\n";
        } else {
            q.push(j);
            std::cout << clock << " " << j.id << " IN " << queueId << " ARRIVED\n";
        }
    }
}

void SingleQueue::step(int clock, std::unordered_map<std::string, SingleQueue*> &network) {
    processServers(clock, network);

    // Move waiting jobs into free servers
    for (auto &srv : servers) {
        if (!srv.has_value() && !q.empty()) {
            Job j = q.front(); q.pop();
            srv = ActiveJob{j, 0, j.tasks.empty() ? 0 : j.tasks[0].work};
            std::cout << clock << " " << j.id << " IN " << queueId << " ENTERS SERVER\n";
        }
    }
}

bool SingleQueue::hasJobs() const {
    if (!q.empty()) return true;
    for (const auto &srv : servers)
        if (srv.has_value()) return true;
    return false;
}

int SingleQueue::queueSize() const { return q.size(); }
int SingleQueue::busyServers() const {
    int count = 0;
    for (const auto &srv : servers)
        if (srv.has_value()) count++;
    return count;
}
const std::string& SingleQueue::id() const { return queueId; }

void SingleQueue::processServers(int clock, std::unordered_map<std::string, SingleQueue*> &network) {
    for (auto &srv : servers) {
        if (!srv.has_value()) continue;

        ActiveJob &job = *srv;
        if (clock % serverRate == serverRate - 1) {
            if (!job.job.tasks.empty())
                job.job.tasks.erase(job.job.tasks.begin());

            std::cout << clock << " " << job.job.id << " IN " << queueId << " FINISHED TASK\n";

            if (job.job.tasks.empty()) {
                // Send to downstream queues
                for (const auto &nextId : edgesOut) {
                    if (network.count(nextId))
                        network[nextId]->addArrivingJobs({job.job}, clock);
                }
                srv.reset();
            }
        }
    }
}
