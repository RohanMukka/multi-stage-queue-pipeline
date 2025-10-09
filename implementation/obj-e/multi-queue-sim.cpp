#include "QueueNetwork.h"
#include <fstream>
#include "json.hpp"
#include <iostream>
using json = nlohmann::json;

int main() {
    std::ifstream f("multi-queue-config.json");
    if (!f.is_open()) {
        std::cerr << "Failed to open config file\n";
        return 1;
    }

    json cfg; f >> cfg;
    QueueNetwork network(cfg);

    int clock = 0, maxTime = 50;

    std::cout << "Time\tQueueID\tQueueSize\tBusyServers\n";

    while (clock < maxTime && network.hasJobs()) {
        // Step simulation
        network.step(clock);

        // Print metrics for each queue
        for (auto &q : network.getQueues()) {
            std::cout << clock << "\t" << q->id()
                      << "\t" << q->queueSize()
                      << "\t" << q->busyServers() << "\n";
        }

        clock++;
    }

    std::cout << "Simulation complete after " << clock << " timesteps.\n";

    // Optional: final summary
    std::cout << "\nFinal Queue States:\n";
    for (auto &q : network.getQueues()) {
        std::cout << q->id() << ": "
                  << q->queueSize() << " jobs remaining, "
                  << q->busyServers() << " servers busy\n";
    }

    return 0;
}
