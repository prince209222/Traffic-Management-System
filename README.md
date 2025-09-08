# Traffic Simulation and Analysis with SUMO

This project demonstrates a traffic simulation using **SUMO (Simulation of Urban Mobility)** and Python scripts for analyzing results.  
It includes network definitions, route files, and configuration for running experiments, as well as scripts for comparing traffic performance and plotting results.

---

## 📂 Project Structure

- **README.md** → Documentation of the project.  
- **Test_Traffic.net.xml** → SUMO network file (road network definition).  
- **Test_Traffic.netecfg** → SUMO network configuration file.  
- **Test_Traffic.rou.xml** → Route file (defines vehicle flows, routes, and traffic demand).  
- **Test_Traffic.sumocfg** → SUMO simulation configuration file (main entry point for simulation).  
- **Traffic_compare.py** → Python script for comparing traffic metrics (e.g., waiting time, flow).  
- **plot_results.py** → Python script for plotting and visualizing results.  

---

## 🚦 How It Works

1. **Build the Network**  
   The `.net.xml` file defines the road network and junctions.  

2. **Define Routes**  
   The `.rou.xml` file specifies vehicle types, flows, and routes through the network.  

3. **Run the Simulation**  
   The `.sumocfg` file ties everything together and is used to launch the SUMO simulation.  

4. **Analyze Results**  
   - `Traffic_compare.py` processes output from SUMO to compare different traffic metrics.  
   - `plot_results.py` visualizes the results (graphs, performance trends, etc.).  

---

## ▶️ Running the Project

### Prerequisites
- [SUMO](https://www.eclipse.org/sumo/) installed and added to your system path.  
- Python 3.x installed with required libraries (`matplotlib`, `pandas`, `numpy`).  

### Steps
1. Open a terminal in the project folder.  
2. Run the SUMO simulation:  
   ```bash
   sumo-gui -c Test_Traffic.sumocfg

