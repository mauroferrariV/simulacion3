import random
import math
import statistics
import matplotlib.pyplot as plt

# Variables globales (idénticas al original)
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
policies_results = {}

# --------------------------------------------------------

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
    initialize()
    while sim_time < num_months:
        timing()
        update_time_avg_stats()
        
        if next_event_type == 1:
            order_arrival()
        elif next_event_type == 2:
            demand()
        elif next_event_type == 4:
            evaluate()
    
    report()

# --------------------------------------------------------

def main():
    global initial_inv_level, num_months, num_values_demand, mean_interdemand, setup_cost, incremental_cost, holding_cost, shortage_cost, minlag, maxlag, prob_distrib_demand, smalls, bigs, results, policies_results

    print("Simulación de Inventario (modelo (s,S))")
    
    initial_inv_level = int(input("Nivel inicial de inventario: "))
    num_months = int(input("Meses a simular: "))
    num_policies = int(input("Cantidad de políticas a evaluar: "))
    num_values_demand = int(input("Cantidad de valores de demanda: "))
    mean_interdemand = float(input("Tiempo medio entre demandas: "))
    setup_cost = float(input("Costo de setup (orden): "))
    incremental_cost = float(input("Costo incremental por unidad: "))
    holding_cost = float(input("Costo de mantenimiento: "))
    shortage_cost = float(input("Costo de faltante: "))
    minlag = float(input("Demora mínima de entrega: "))
    maxlag = float(input("Demora máxima de entrega: "))

    print("Función de distribución acumulada de demanda:")
    prob_distrib_demand = [0.0] + [float(input(f"Probabilidad acumulada para demanda {i}: ")) for i in range(1, num_values_demand + 1)]

    policies = []
    print("\nIngrese las políticas en el formato 's S':")
    for i in range(num_policies):
        policy = input(f"Política {i+1}: ").split()
        policies.append((int(policy[0]), int(policy[1])))

    policies_results = {}

    for smalls, bigs in policies:
        results = []
        for run in range(num_runs):
            run_simulation()
        policies_results[(smalls, bigs)] = results.copy()

    # Mostrar resultados
    print("\nResultados por política:")
    for policy, res in policies_results.items():
        avg_ordering = statistics.mean(r['ordering_cost'] for r in res)
        avg_holding = statistics.mean(r['holding_cost'] for r in res)
        avg_shortage = statistics.mean(r['shortage_cost'] for r in res)
        avg_total = statistics.mean(r['total_cost'] for r in res)
        std_total = statistics.stdev(r['total_cost'] for r in res)
        print(f"(s,S)=({policy[0]},{policy[1]}) -> Total={avg_total:.2f} | Orden={avg_ordering:.2f} | Mantenimiento={avg_holding:.2f} | Faltante={avg_shortage:.2f} | Std={std_total:.2f}")

    # Generar gráficos
    plot_results(policies_results)

# --------------------------------------------------------

def plot_results(policies_results):
    policies = list(policies_results.keys())
    total_costs = [statistics.mean([r['total_cost'] for r in policies_results[p]]) for p in policies]
    ordering_costs = [statistics.mean([r['ordering_cost'] for r in policies_results[p]]) for p in policies]
    holding_costs = [statistics.mean([r['holding_cost'] for r in policies_results[p]]) for p in policies]
    shortage_costs = [statistics.mean([r['shortage_cost'] for r in policies_results[p]]) for p in policies]

    x = [f"{p[0]},{p[1]}" for p in policies]
    
    plt.figure(figsize=(14, 6))
    plt.plot(x, total_costs, label="Costo total", marker='o')
    plt.plot(x, ordering_costs, label="Costo de orden", marker='o')
    plt.plot(x, holding_costs, label="Costo de mantenimiento", marker='o')
    plt.plot(x, shortage_costs, label="Costo de faltante", marker='o')
    plt.title("Comparación de políticas de inventario")
    plt.xlabel("(s,S)")
    plt.ylabel("Costo promedio")
    plt.grid()
    plt.legend()
    plt.show()

# --------------------------------------------------------

if __name__ == "__main__":
    main()
