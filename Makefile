# Multi-Stage Queue Pipeline
#
# make build   compile the simulators into bin/
# make demo    run the whole pipeline end to end into build/demo/
# make clean   remove build output

CXX      ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall
PYTHON   ?= python3

BIN  := bin
DEMO := build/demo

OBJ_A := implementation/obj-a
OBJ_B := implementation/obj-b
OBJ_C := implementation/obj-c
OBJ_E := implementation/obj-e

# Workload knobs for `make demo` — override on the command line, e.g.
#   make demo DIST=normal END=500
START ?= 0
END   ?= 100
DIST  ?= poisson
LAM   ?= 3

.DEFAULT_GOAL := help
.PHONY: help build demo plots clean

help:
	@echo "Multi-Stage Queue Pipeline"
	@echo
	@echo "  make build   compile the single-queue and multi-queue simulators into $(BIN)/"
	@echo "  make demo    generate a workload, simulate it, derive metrics and plot them"
	@echo "  make plots   regenerate the analysis/simple histograms and scatter plots"
	@echo "  make clean   remove build output"
	@echo
	@echo "Python tools need the dependencies in requirements.txt:"
	@echo "  pip install -r requirements.txt"

build: $(BIN)/simple-queue $(BIN)/multi-queue

$(BIN)/simple-queue: $(OBJ_B)/simple_queue.cpp | $(BIN)
	$(CXX) $(CXXFLAGS) -o $@ $<

$(BIN)/multi-queue: $(OBJ_E)/main.cpp | $(BIN)
	$(CXX) $(CXXFLAGS) -o $@ $<

$(BIN):
	mkdir -p $(BIN)

demo: build
	mkdir -p $(DEMO)
	@echo "==> 1/4 generating a $(DIST) workload over [$(START), $(END)]"
	$(PYTHON) $(OBJ_A)/generator.py --start $(START) --end $(END) --dist $(DIST) --lam $(LAM) \
		--tasks-per-job 2 --task-mode fixed --task-fixed-len 10 --out $(DEMO)/workload.csv
	@echo "==> 2/4 simulating a single queue"
	cd $(DEMO) && $(CURDIR)/$(BIN)/simple-queue workload.csv $(CURDIR)/$(OBJ_B)/simple-queue-config.csv
	@echo "==> 3/4 deriving metrics"
	$(PYTHON) $(OBJ_C)/derive-event-metrics/derive-event-metrics.py $(DEMO)/job.log $(DEMO)/emetric.csv
	$(PYTHON) $(OBJ_C)/derive-system-metrics/derive-system-metrics.py $(DEMO)/job.log $(DEMO)/sysmetric.csv
	$(PYTHON) $(OBJ_C)/compute-use/compute-use.py $(DEMO)/qmet.csv $(DEMO)/quse.csv
	@echo "==> 4/4 plotting"
	$(PYTHON) $(OBJ_C)/plot-derive-event-metrics/plot-derive-event-metrics.py \
		$(DEMO)/emetric.csv $(DEMO)/response_time.png --hist=response_time
	$(PYTHON) $(OBJ_C)/plot-use/plot-use.py $(DEMO)/quse.csv $(DEMO)/use.png
	$(PYTHON) $(OBJ_C)/plot-system-metrics/plot-system-metrics.py $(DEMO)/sysmetric.csv $(DEMO)/system.png
	@echo
	@echo "Done. Results in $(DEMO)/"

plots:
	bash $(OBJ_C)/plot-derive-event-metrics/create_all_histograms.sh
	bash $(OBJ_C)/plot-derive-event-metrics/create_all_scat.sh

clean:
	rm -rf $(BIN) build
	rm -f $(OBJ_B)/exe $(OBJ_B)/job.log $(OBJ_B)/qmet.csv $(OBJ_B)/out.csv
	rm -f $(OBJ_E)/sim $(OBJ_E)/out*.csv
