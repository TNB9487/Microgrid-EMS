import matplotlib.pyplot as plt


# SMART MICROGRID ENERGY MANAGEMENT SYSTEM (EMS) 


# Section 1: Simulation Environment Profiles

# Power Sources in Megawatts (MW)
power_sources = {
    "solar" : 60.0,
    "diesel_generator": 45.0
}

# Priority Number and Status for each zone 
# Higher numerical priority value indicates lower service importance and will be disconnected first.
grid_zones = {
    "hospital": {"priority": 1, "status": "ONLINE"},
    "residential": {"priority": 2, "status": "ONLINE"},
    "factory": {"priority": 3, "status": "ONLINE"} 
}

# Energy Demand for each zone in MegaWatts (MW)
demand_profiles = {
    "hospital":    [25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25],
    "residential": [15, 12, 12, 12, 15, 25, 35, 30, 20, 18, 18, 20, 22, 20, 20, 22, 30, 45, 55, 50, 40, 30, 22, 18],
    "factory":     [10, 10, 10, 10, 10, 10, 20, 40, 45, 45, 45, 45, 35, 45, 45, 45, 30, 15, 10, 10, 10, 10, 10, 10]
}

# Solar Energy Multiplier for 24-hour simulation from 00:00 to 23:00
solar_profile = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.6, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 0.9, 0.7, 0.5, 0.4, 0.2, 0.0, 0.0, 0.0, 0.0]

# Battery Energy Storage System
# Energy quantities are expressed in MegaWatt-hours (MWh)
battery = {
    "capacity_MWh": 80.0,
    "current_charge_MWh": 25.0,
    "charge_efficiency": 0.88,
    "discharge_efficiency": 0.90
}


# Section 2: Power Balance Calculation

def analyze_grid_balance(current_solar, zones, hour_index):
    total_supply = power_sources["diesel_generator"] + current_solar

    total_demand = 0.0
    for name, zone_data in zones.items():
        if zone_data["status"] == "ONLINE":
            total_demand += demand_profiles[name][hour_index]

    net_balance = total_supply - total_demand

    return total_supply, total_demand, net_balance


# Section 3: Automated Load Shedding System

def run_automated_load_shedding(current_solar, zones, hour_index):
    supply, demand, net_balance = analyze_grid_balance(
        current_solar,
        zones,
        hour_index
    )

    while net_balance < 0.0:
        zone_to_disconnect = None
        highest_priority_number = -1

        for zone_name, zone_data in zones.items():
            if zone_data["status"] == "ONLINE" and zone_data["priority"] > highest_priority_number:
                highest_priority_number = zone_data["priority"]
                zone_to_disconnect = zone_name

        if zone_to_disconnect:
            zones[zone_to_disconnect]["status"] = "OFFLINE"
            print(f" Load Shed. {zone_to_disconnect.capitalize()} forced offline.")
            supply, demand, net_balance = analyze_grid_balance(
                current_solar,
                zones, hour_index)
        else:
            print("All loads disconnected. System collapsed.")
            break
    
    return supply, demand, net_balance


# Section 4: Energy Management System (EMS)

def run_24h_simulation(sources, zones, profile):

    # Code for formatting
    print("\n" + "=" * 115)
    print("                 24-HOUR SMART MICROGRID OPERATIONS LOG")
    print("=" * 115)
    print(f"| {'Hour':<5} | {'Solar':<7} | {'Supply':<7} | {'Demand':<7} | {'Margin':<7} | {'Battery':<8} | {'Hosp':<4} | {'Res':<4} | {'Fact':<4} | {'Event':<30} |")
    print("-" * 115)

    time_iteration = 1.0
    
    #statistics
    total_solar_energy = 0.0
    total_diesel_energy = 0.0
    total_battery_throughput = 0.0
    total_curtailed_energy = 0.0
    total_load_shed = 0.0

    hospital_online_hours = 0.0
    residential_online_hours = 0.0
    factory_online_hours = 0.0

    # Data for plotting
    hours = []

    solar_history = []

    demand_history = []

    initial_balance_history = []

    final_balance_history = []

    battery_history = []


    for hour in range(24): # simulation runs 24 times, from 0 to 23

        # Reset grid zone statuses at start of each hour evaluation
        for zone_name in zones:
            zones[zone_name]["status"] = "ONLINE" 

        # Calculate generation
        current_solar = profile[hour] * sources["solar"]

        total_solar_energy += current_solar * time_iteration
        total_diesel_energy += sources["diesel_generator"] * time_iteration

        supply, demand, balance = analyze_grid_balance(current_solar,zones, hour)

        # Code for plotting (Initial balance)
        initial_balance_history.append(balance)

        original_demand = demand # This stores the demand before load shedding.
        events = []

    # Phase 1: Battery discharge during deficit
        if balance < 0.0:
            power_deficit = abs(balance)
            energy_needed_MWh = power_deficit * time_iteration

            usable_battery_energy = battery["current_charge_MWh"] * battery["discharge_efficiency"]

            if usable_battery_energy >= energy_needed_MWh:
                energy_taken_from_battery = energy_needed_MWh/battery["discharge_efficiency"]
                battery["current_charge_MWh"] -= energy_taken_from_battery
                total_battery_throughput += energy_taken_from_battery
                balance = 0.0
                events.append("DISCHARGE")
            else:
                energy_taken_from_battery = battery["current_charge_MWh"]
                energy_delivered = energy_taken_from_battery * battery["discharge_efficiency"]
                battery["current_charge_MWh"] = 0.0
                total_battery_throughput += energy_taken_from_battery
                balance += energy_delivered/ time_iteration
                events.append("DEPLETED")

        # Phase 2: Load shedding if battery is insufficient
            if balance < 0.0:
                supply, demand, balance = run_automated_load_shedding(current_solar, zones, hour)
                total_load_shed += (original_demand - demand) *time_iteration
                events.append("SHEDDING")
    
    # Phase 3: Battery charging during surplus   
        if balance > 0.0:
            surplus_energy_MWh = balance * time_iteration # extra energy
            empty_space = battery["capacity_MWh"] - battery["current_charge_MWh"]  

            energy_stored = min(
                surplus_energy_MWh* battery["charge_efficiency"],
                empty_space
            ) # Store the smaller of: usable surplus after efficiency, or remaining battery capacity

            battery["current_charge_MWh"] += energy_stored
            total_battery_throughput += energy_stored

            energy_used_for_charging = energy_stored/battery["charge_efficiency"]
            curtailed_energy = max(0.0, surplus_energy_MWh - energy_used_for_charging) # surplus energy not absorbed by the battery

            if curtailed_energy > 0.0:
                total_curtailed_energy += curtailed_energy
                balance = curtailed_energy/time_iteration
                events.append("CURTAILED")
            else:
                balance = 0.0
                events.append("CHARGING")
        
        event = " + ".join(events) if events else "NORMAL"

        h_stat = "ON" if zones["hospital"]["status"] == "ONLINE" else "OFF"
        r_stat = "ON" if zones["residential"]["status"] == "ONLINE" else "OFF"
        f_stat = "ON" if zones["factory"]["status"] == "ONLINE" else "OFF"

        if h_stat == "ON":
            hospital_online_hours += 1
        if r_stat == "ON":
            residential_online_hours += 1
        if f_stat == "ON":
            factory_online_hours += 1

        print(f"| {hour:02d}:00 | {current_solar:<7.1f} | {supply:<7.1f} | {demand:<7.1f} | {balance:<7.1f} | {battery['current_charge_MWh']:<8.1f} | {h_stat:<4} | {r_stat:<4} | {f_stat:<4} | {event:<30} |")

        # Code for plotting
        hours.append(hour)

        solar_history.append(current_solar)

        demand_history.append(demand)

        final_balance_history.append(balance)

        battery_history.append(battery["current_charge_MWh"])

    renewable_penetration = total_solar_energy / (total_solar_energy + total_diesel_energy) * 100

    
    print("=" * 115)
    print("\n24-HOUR SYSTEM PERFORMANCE SUMMARY")
    print("-" * 50)
    print(f"Total Solar Generation:    {total_solar_energy:.1f} MWh")
    print(f"Total Diesel Generation:   {total_diesel_energy:.1f} MWh")
    print(f"Renewable Penetration:     {renewable_penetration:.1f}%")
    print(f"Battery Throughput:        {total_battery_throughput:.1f} MWh")
    print(f"Curtailed Energy:          {total_curtailed_energy:.1f} MWh")
    print(f"Total Load Shed:           {total_load_shed:.1f} MWh")
    print(f"Hospital Uptime:           {hospital_online_hours / 24 * 100:.1f}%")
    print(f"Residential Uptime:        {residential_online_hours / 24 * 100:.1f}%")
    print(f"Factory Uptime:            {factory_online_hours / 24 * 100:.1f}%")
    print("=" * 50)

    # Code for plotting (Battery Energy)
    plt.figure(figsize=(10, 5))

    plt.plot(
        hours,
        battery_history,
        marker="o",
        linewidth=2,
        markersize=5
    )

    plt.title("Battery Energy Throughout 24-Hour Simulation")

    plt.xlabel("Hour")

    plt.ylabel("Battery Energy (MWh)")

    plt.xticks(range(24))

    plt.xlim(0,23)

    plt.ylim(0, battery["capacity_MWh"])

    plt.grid(True)

    plt.tight_layout()

    plt.savefig("battery_soc.png", dpi=300)

    plt.show()

    # Code for plotting (Solar Generation and Load Demand)
    plt.figure(figsize=(10, 5))

    plt.plot(
        hours,
        solar_history,
        marker="o",
        linewidth=2,
        markersize=5,
        label="Solar Generation"
    )

    plt.plot(
        hours,
        demand_history,
        marker="s",
        linewidth=2,
        markersize=5,
        label="Load Demand"
    )

    plt.title("Solar Generation and Load Demand Throughout 24-Hour Simulation")

    plt.xlabel("Hour")

    plt.ylabel("Power (MW)")

    plt.xticks(range(24))

    plt.xlim(0, 23)

    plt.grid(True)

    plt.legend()

    plt.tight_layout()

    plt.savefig("solar_demand.png", dpi=300)

    plt.show()

    # Code for plotting (Initial Power Balance)

    plt.figure(figsize=(10,5))

    plt.plot(
        hours,
        initial_balance_history,
        marker="o",
        linewidth=2,
        markersize=5
    )

    plt.axhline(
        y=0,
        linestyle="--"
    )

    plt.title("Initial Power Balance Before EMS Control")

    plt.xlabel("Hour")

    plt.ylabel("Power Balance (MW)")

    plt.xticks(range(24))

    plt.xlim(0,23)

    plt.grid(True)

    plt.tight_layout()

    plt.savefig("initial_power_balance.png", dpi=300)

    plt.show()

    # Code for plotting (Final Power Balance)
    plt.figure(figsize=(10,5))

    plt.plot(
        hours,
        final_balance_history,
        marker="o",
        linewidth=2,
        markersize=5
    )

    plt.axhline(
        y=0,
        linestyle="--"
    )

    plt.title("Final Power Balance After EMS Control")

    plt.xlabel("Hour")

    plt.ylabel("Power Balance (MW)")

    plt.xticks(range(24))

    plt.xlim(0,23)

    plt.grid(True)

    plt.tight_layout()

    plt.savefig("final_power_balance.png", dpi=300)

    plt.show()

run_24h_simulation(power_sources, grid_zones, solar_profile)

