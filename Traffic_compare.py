import os
import sys
import traci
import sumolib
import csv

# Paths (later we’ll load from your config file)
SUMO_BINARY = "sumo"  # or "sumo-gui" for GUI mode
CONFIG_FILE = "Test_Traffic.sumocfg"  # you need to make this

# Simulation parameters
SIM_STEPS = 1000  # total steps

# CSV output file
OUTPUT_FILE = "metrics_results.csv"

# -------------------------------
# Helper: Collect metrics each step
def collect_metrics(step, mode, metrics):
    waiting_times = []
    queue_lengths = []

    for veh_id in traci.vehicle.getIDList():
        waiting_times.append(traci.vehicle.getWaitingTime(veh_id))

    for lane_id in traci.lane.getIDList():
        queue_lengths.append(traci.lane.getLastStepVehicleNumber(lane_id))

    metrics.append({
        "step": step,
        "mode": mode,
        "avg_waiting_time": sum(waiting_times) / len(waiting_times) if waiting_times else 0,
        "avg_queue_length": sum(queue_lengths) / len(queue_lengths) if queue_lengths else 0,
        "throughput": traci.simulation.getArrivedNumber()
    })


# -------------------------------
# Logic Engine: Simple Rule-based
def apply_logic():
    for tl in traci.trafficlight.getIDList():
        phase = traci.trafficlight.getPhase(tl)
        lanes = traci.trafficlight.getControlledLanes(tl)

        # Example rule: if avg queue on controlled lanes > 5, extend green
        queue = sum(traci.lane.getLastStepVehicleNumber(l) for l in lanes) / len(lanes)
        if queue > 5 and phase % 2 == 0:  # green phase is even index
            traci.trafficlight.setPhaseDuration(tl, 10)  # extend green
        else:
            # otherwise, just let it cycle
            pass


# -------------------------------
# Run Simulation
def run_simulation(mode="baseline"):
    cmd = [SUMO_BINARY, "-c", CONFIG_FILE, "--no-step-log", "true"]
    traci.start(cmd)

    metrics = []

    for step in range(SIM_STEPS):
        traci.simulationStep()

        if mode == "logic":
            apply_logic()

        collect_metrics(step, mode, metrics)

    traci.close()
    return metrics


# -------------------------------
# Save results to CSV
def save_results(all_metrics):
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["step", "mode", "avg_waiting_time", "avg_queue_length", "throughput"])
        writer.writeheader()
        writer.writerows(all_metrics)


# -------------------------------
if __name__ == "__main__":
    print("Running baseline simulation...")
    baseline_metrics = run_simulation(mode="baseline")

    print("Running logic engine simulation...")
    logic_metrics = run_simulation(mode="logic")

    # Merge results
    all_metrics = baseline_metrics + logic_metrics
    save_results(all_metrics)

    print(f"Metrics saved to {OUTPUT_FILE}")
