import sys
import matplotlib.pyplot as plt


def parse_log_line(line):
    parts = line.strip().split()
    if len(parts) < 5:
        return None
    time = float(parts[0])
    job_id = int(parts[1][1:])
    queue_id = parts[3]
    event_type = parts[4]
    return time, job_id, queue_id, event_type

def marker_for_event(event):
    if "ARRIVE" in event or "ENTER" in event or "EXIT" in event:
        return "s"
    elif "TASK" in event:
        return "o"
    elif "ERROR" in event:
        return "x"
    else:
        return "."
    
def main():
    if len(sys.argv) < 3:
        print("Usage: python ./create-event-trace <input_log> <output_png>")
        sys.exit(1)

    log_file = sys.argv[1]
    plot_file = sys.argv[2]

    events = []
    with open(log_file, "r") as f:
        for line in f:
            parsed = parse_log_line(line)
            if parsed:
                events.append(parsed)

    if not events:
        print("No valid events found in log file.")
        sys.exit(1)

    time, job_ids, queues, event_types = zip(*events)

    unique_queues = sorted(set(queues))
    color_map = {q: plt.cm.tab10(i % 10) for i, q in enumerate(unique_queues)}
    colors = [color_map[q] for q in queues]

    plt.figure(figsize=(8, 5))
    for t, j, q, e in events:
        plt.scatter(
            t, j, 
            marker=marker_for_event(e), 
            color=color_map[q], 
            edgecolors="black",
            s=100
        )
    
    plt.xlabel("Time")
    plt.ylabel("Job ID")
    plt.title("Event Trace")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(plot_file, dpi=300)
    print(f"Event trace plot saved to {plot_file}")

if __name__ == "__main__":
    main()