import pandas as pd
import matplotlib.pyplot as plt

# Load metrics
df = pd.read_csv("metrics_results.csv")

# Separate baseline and logic runs
baseline = df[df["mode"] == "baseline"]
logic = df[df["mode"] == "logic"]

# ----------------------------
# 1. Average Waiting Time (line plot)
plt.figure(figsize=(10, 5))
plt.plot(baseline["step"], baseline["avg_waiting_time"], label="Baseline", color="red")
plt.plot(logic["step"], logic["avg_waiting_time"], label="Logic Engine", color="green")
plt.xlabel("Simulation Step")
plt.ylabel("Average Waiting Time (s)")
plt.title("Average Waiting Time Over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("waiting_time_comparison.png")
plt.show()

# ----------------------------
# 2. Average Queue Length (line plot)
plt.figure(figsize=(10, 5))
plt.plot(baseline["step"], baseline["avg_queue_length"], label="Baseline", color="red")
plt.plot(logic["step"], logic["avg_queue_length"], label="Logic Engine", color="green")
plt.xlabel("Simulation Step")
plt.ylabel("Average Queue Length (vehicles)")
plt.title("Average Queue Length Over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("queue_length_comparison.png")
plt.show()

# ----------------------------
# 3. Throughput (bar chart)
baseline_throughput = baseline["throughput"].iloc[-1]
logic_throughput = logic["throughput"].iloc[-1]

plt.figure(figsize=(6, 5))
plt.bar(["Baseline", "Logic Engine"], [baseline_throughput, logic_throughput], color=["red", "green"])
plt.ylabel("Vehicles Arrived")
plt.title("Total Throughput Comparison")
plt.tight_layout()
plt.savefig("throughput_comparison.png")
plt.show()
