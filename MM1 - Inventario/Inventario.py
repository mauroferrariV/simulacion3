import random
import math
import statistics
import matplotlib.pyplot as plt

# Definiciones globales
amount = 0
bigs = 0
initial_inv_level = 0
inv_level = 0
next_event_type = 0
num_events = 4
num_months = 0
num_values_demand = 0
smalls = 0

area_holding = 0.0
area_shortage = 0.0
holding_cost = 0.0
incremental_cost = 0.0
maxlag = 0.0
mean_interdemand = 0.0
minlag = 0.0
prob_distrib_demand = [0.0] * 26
setup_cost = 0.0
shortage_cost = 0.0
sim_time = 0.0
time_last_event = 0.0
time_next_event = [0.0] * 5
total_ordering_cost = 0.0

num_runs = 10
results = []

stock_history = []
demand_history = []
ordering_cost_history = []
holding_cost_history = []
shortage_cost_history = []
total_cost_history = []


def initialize():
    global sim_time, inv_level, time_last_event, total_ordering_cost, area_holding, area_shortage, time_next_event
    
    sim_time = 0.0
    inv_level = initial_inv_level
    time_last_event = 0.0
    total_ordering_cost = 0.0
    area_holding = 0.0
    area_shortage = 0.0
    time_next_event[1] = 1.0e+30
    time_next_event[2] = sim_time + expon(mean_interdemand)
    time_next_event[3] = num_months
    time_next_event[4] = 0.0

def timing():
    global sim_time, next_event_type
    min_time_next_event = 1.0e+29
    next_event_type = 0
    
    for i in range(1, num_events + 1):
        if time_next_event[i] < min_time_next_event:
            min_time_next_event = time_next_event[i]
            next_event_type = i
    
    if next_event_type == 0:
        print("\nEvent list empty at time", sim_time)
        exit(1)
    
    sim_time = min_time_next_event

def order_arrival():
    global inv_level, time_next_event
    inv_level += amount
    time_next_event[1] = 1.0e+30

def demand():
    global inv_level, time_next_event
    inv_level -= random_integer(prob_distrib_demand)
    time_next_event[2] = sim_time + expon(mean_interdemand)

def evaluate():
    global amount, total_ordering_cost, time_next_event
    if inv_level < smalls:
        amount = bigs - inv_level
        total_ordering_cost += setup_cost + incremental_cost * amount
        time_next_event[1] = sim_time + uniform(minlag, maxlag)
    time_next_event[4] = sim_time + 1.0

def report():
    global results
    avg_ordering_cost = total_ordering_cost / num_months
    avg_holding_cost = holding_cost * area_holding / num_months
    avg_shortage_cost = shortage_cost * area_shortage / num_months
    total_cost = avg_ordering_cost + avg_holding_cost + avg_shortage_cost
    
    results.append({
        'ordering_cost': avg_ordering_cost,
        'holding_cost': avg_holding_cost,
        'shortage_cost': avg_shortage_cost,
        'total_cost': total_cost
    })

def update_time_avg_stats():
    global time_last_event, area_shortage, area_holding
    time_since_last_event = sim_time - time_last_event
    time_last_event = sim_time
    
    if inv_level < 0:
        area_shortage -= inv_level * time_since_last_event
    elif inv_level > 0:
        area_holding += inv_level * time_since_last_event

def expon(mean):
    return -mean * math.log(random.random())

def random_integer(prob_distrib):
    u = random.random()
    i = 1
    while u >= prob_distrib[i]:
        i += 1
    return i

def uniform(a, b):
    return a + random.random() * (b - a)

def run_simulation():
    global next_event_type, sim_time, stock_history, demand_history, ordering_cost_history, holding_cost_history, shortage_cost_history, total_cost_history
    
    initialize()
    stock_history = []
    demand_history = []
    ordering_cost_history = []
    holding_cost_history = []
    shortage_cost_history = []
    total_cost_history = []
    
    while sim_time < num_months:
        timing()
        update_time_avg_stats()
        
        # Registrar datos para las gráficas
        stock_history.append((sim_time, inv_level))
        
        if next_event_type == 1:
            order_arrival()
        elif next_event_type == 2:
            demand_size = random_integer(prob_distrib_demand)
            demand_history.append((sim_time, demand_size))
            demand()
        elif next_event_type == 4:
            evaluate()
        
        # Registrar costos
        ordering_cost_history.append((sim_time, total_ordering_cost))
        holding_cost_history.append((sim_time, holding_cost * area_holding))
        shortage_cost_history.append((sim_time, shortage_cost * area_shortage))
        total_cost = total_ordering_cost + holding_cost * area_holding + shortage_cost * area_shortage
        total_cost_history.append((sim_time, total_cost))
    
    report()

def create_graphs(policy):
    fig, axs = plt.subplots(1, 2, figsize=(14, 8))
    fig.suptitle(f"Política ({policy[0]}, {policy[1]})")

    # Gráfico de stock
    axs[0].plot(*zip(*stock_history))
    axs[0].set_title("Variación del Stock")
    axs[0].set_xlabel("Tiempo")
    axs[0].set_ylabel("Nivel de Stock")

    # Gráfico de demanda
    axs[1].scatter(*zip(*demand_history))
    axs[1].set_title("Demanda")
    axs[1].set_xlabel("Tiempo")
    axs[1].set_ylabel("Tamaño de Demanda")
    
    plt.tight_layout()
    plt.show()

def main():
    global initial_inv_level, num_months, num_values_demand, mean_interdemand, setup_cost, incremental_cost, holding_cost, shortage_cost, minlag, maxlag, prob_distrib_demand, smalls, bigs, results

    print("Single-product inventory system")
    
    initial_inv_level = int(input("Initial inventory level: "))
    num_months = int(input("Number of months to simulate: "))
    num_policies = int(input("Number of policies to evaluate: "))
    num_values_demand = int(input("Number of demand sizes: "))
    mean_interdemand = float(input("Mean interdemand time: "))
    setup_cost = float(input("Setup cost: "))
    incremental_cost = float(input("Incremental cost: "))
    holding_cost = float(input("Holding cost: "))
    shortage_cost = float(input("Shortage cost: "))
    minlag = float(input("Minimum lag time: "))
    maxlag = float(input("Maximum lag time: "))

    print("Enter the cumulative distribution function of demand sizes:")
    prob_distrib_demand = [0.0] + [float(input(f"Probability for demand size {i}: ")) for i in range(1, num_values_demand + 1)]

    print("\nSimulation parameters:")
    print(f"Initial inventory level: {initial_inv_level} items")
    print(f"Number of demand sizes: {num_values_demand}")
    print(f"Distribution function of demand sizes: {' '.join(f'{p:.3f}' for p in prob_distrib_demand[1:])}")
    print(f"Mean interdemand time: {mean_interdemand:.2f}")
    print(f"Delivery lag range: {minlag:.2f} to {maxlag:.2f} months")
    print(f"Length of the simulation: {num_months} months")
    print(f"K = {setup_cost:.1f}, i = {incremental_cost:.1f}, h = {holding_cost:.1f}, pi = {shortage_cost:.1f}")
    print(f"Number of policies: {num_policies}")

    # Ingresar todas las políticas juntas
    policies = []
    print(f"\nEnter {num_policies} policies in the format 's S' (separated by space):")
    for i in range(num_policies):
        policy = input(f"Policy {i+1}: ").split()
        policies.append((int(policy[0]), int(policy[1])))

    print("\nPolicy    Avg Total Cost    Avg Ordering Cost    Avg Holding Cost    Avg Shortage Cost    Std Dev Total Cost")
        
    for smalls, bigs in policies:
        results = []
        
        # Elegir una corrida aleatoria para graficar
        graph_run = random.randint(0, num_runs - 1)
        
        for run in range(num_runs):
            run_simulation()
            print(f"Run {run + 1} completed. Total cost: {results[-1]['total_cost']:.2f}")
            
            if run == graph_run:
                create_graphs((smalls, bigs))
        
        if len(results) < 2:
            print(f"Warning: Only {len(results)} valid runs. Unable to calculate standard deviation.")
            std_dev_total_cost = float('nan')
        else:
            std_dev_total_cost = statistics.stdev(r['total_cost'] for r in results)
        
        avg_total_cost = statistics.mean(r['total_cost'] for r in results)
        avg_ordering_cost = statistics.mean(r['ordering_cost'] for r in results)
        avg_holding_cost = statistics.mean(r['holding_cost'] for r in results)
        avg_shortage_cost = statistics.mean(r['shortage_cost'] for r in results)
        
        print(f"({smalls:3d},{bigs:3d}){avg_total_cost:18.2f}{avg_ordering_cost:21.2f}"
              f"{avg_holding_cost:20.2f}{avg_shortage_cost:21.2f}{std_dev_total_cost:20.2f}")

if __name__ == "__main__":
    main()