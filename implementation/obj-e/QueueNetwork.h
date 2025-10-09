// QueueNetwork.h
#pragma once
#include "SingleQueue.h"
#include <unordered_map>
#include <vector>
#include <string>
#include "json.hpp"
using json = nlohmann::json;

class QueueNetwork {
public:
    QueueNetwork(const json &config);
    void step(int clock);
    bool hasJobs() const;
     std::vector<SingleQueue*> getQueues() const;

private:
    std::unordered_map<std::string, SingleQueue*> queues;
};
