// QueueNetwork.cpp
#include "QueueNetwork.h"
#include <iostream>

QueueNetwork::QueueNetwork(const json &config) {
    // Create queues
    for (const auto &qcfg : config) {
        std::string id = qcfg["Queue sys ID"];
        int maxSize = qcfg["Max Queue Size"];
        int servers = qcfg["# of Servers"];
        int rate = qcfg["Server Function Rate"];
        SingleQueue *q = new SingleQueue(id, maxSize, rate, servers);

        // store edges out
        for (auto &e : qcfg["Edges out"])
            q->edgesOut.push_back(e.get<std::string>());

        queues[id] = q;
    }
}

void QueueNetwork::step(int clock) {
    for (auto &[id, q] : queues)
        q->step(clock, queues);
}

bool QueueNetwork::hasJobs() const {
    for (auto &[id, q] : queues)
        if (q->hasJobs()) return true;
    return false;
}

std::vector<SingleQueue*> QueueNetwork::getQueues() const {
    std::vector<SingleQueue*> vec;
    for (const auto &[id, q] : queues) {
        vec.push_back(q);
    }
    return vec;
}
