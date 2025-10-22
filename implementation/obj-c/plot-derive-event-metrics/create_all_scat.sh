#!/bin/bash

# Scatter plots for barrista event metrics
# Usage: bash plot_scatter_metrics.sh

python3 plot-derive-event-metrics.py barrista_event_metrics.csv barrista_arrival_vs_queue.png --scat=arrival_time,time_in_queue
python3 plot-derive-event-metrics.py barrista_event_metrics.csv barrista_arrival_vs_service.png --scat=arrival_time,time_in_service
python3 plot-derive-event-metrics.py barrista_event_metrics.csv barrista_arrival_vs_response.png --scat=arrival_time,response_time
python3 plot-derive-event-metrics.py barrista_event_metrics.csv barrista_arrival_vs_turnaround.png --scat=arrival_time,turnaround_time

python3 plot-derive-event-metrics.py barrista_event_metrics.csv barrista_queue_vs_service.png --scat=time_in_queue,time_in_service
python3 plot-derive-event-metrics.py barrista_event_metrics.csv barrista_queue_vs_response.png --scat=time_in_queue,response_time
python3 plot-derive-event-metrics.py barrista_event_metrics.csv barrista_queue_vs_turnaround.png --scat=time_in_queue,turnaround_time

python3 plot-derive-event-metrics.py barrista_event_metrics.csv barrista_service_vs_response.png --scat=time_in_service,response_time
python3 plot-derive-event-metrics.py barrista_event_metrics.csv barrista_service_vs_turnaround.png --scat=time_in_service,turnaround_time

python3 plot-derive-event-metrics.py barrista_event_metrics.csv barrista_response_vs_turnaround.png --scat=response_time,turnaround_time
