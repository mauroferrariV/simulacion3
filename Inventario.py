import random
import math
import statistics
import matplotlib.pyplot as plt
import pandas as pd

def input_default(prompt, default, cast_func):
    user_input = input(f"{prompt} (Enter para usar {default}): ")
    return cast_func(user_input) if user_input.strip() != "" else default

# Variables globales
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

num_runs = 0
results = []
policies_results = {}
inv_data = []

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

def run_simulation(run_id):
    initialize()
    while sim_time < num_months:
        timing()
        update_time_avg_stats()

        if int(sim_time) == sim_time and 1 <= int(sim_time) <= num_months:
            inv_data.append({
                "corrida": run_id,
                "mes": int(sim_time),
                "I(t)": inv_level,
                "I+(t)": max(inv_level, 0),
                "I-(t)": max(-inv_level, 0)
            })

        if next_event_type == 1:
            order_arrival()
        elif next_event_type == 2:
            demand()
        elif next_event_type == 4:
            evaluate()
    report()

def main():
    global initial_inv_level, num_months, num_values_demand, mean_interdemand
    global setup_cost, incremental_cost, holding_cost, shortage_cost
    global minlag, maxlag, prob_distrib_demand, smalls, bigs
    global results, policies_results, num_runs, inv_data

    print("Simulación de Inventario (modelo (s,S))")
    
    initial_inv_level = input_default("Nivel inicial de inventario", 60, int)
    num_months = input_default("Meses a simular", 12, int)
    num_runs = input_default("Cantidad de corridas por política", 3, int)
    num_values_demand = input_default("Cantidad de valores de demanda", 6, int)
    mean_interdemand = input_default("Tiempo medio entre demandas", 0.10, float)
    setup_cost = input_default("Costo de setup (orden)", 32.0, float)
    incremental_cost = input_default("Costo incremental por unidad", 3.0, float)
    holding_cost = input_default("Costo de mantenimiento", 1.0, float)
    shortage_cost = input_default("Costo de faltante", 5.0, float)
    minlag = input_default("Demora mínima de entrega", 0.5, float)
    maxlag = input_default("Demora máxima de entrega", 1.0, float)

    print("Función de distribución acumulada de demanda:")
    default_probs = [0.1, 0.3, 0.6, 0.8, 0.95, 1.0]
    prob_distrib_demand = [0.0]
    for i in range(1, num_values_demand + 1):
        val = input(f"Probabilidad acumulada para demanda {i} (Enter para {default_probs[i - 1]}): ")
        prob_distrib_demand.append(float(val) if val.strip() != "" else default_probs[i - 1])

    policies = []
    print("\nIngrese las políticas en el formato 's S':")
    
    s_default = 20
    S_default = 80
    entrada = input(f"Política (Enter para usar s={s_default}, S={S_default}): ")
    if entrada.strip() == "":
        policies.append((s_default, S_default))
    else:
        s, S = map(int, entrada.split())
        policies.append((s, S))

    policies_results = {}
    inv_data = []

    for smalls, bigs in policies:
        results = []
        for run in range(num_runs):
            run_simulation(run)
        policies_results[(smalls, bigs)] = results.copy()

    print("\nResultados por corrida:")
    tabla_corridas = []
    for policy, res in policies_results.items():
        for i, r in enumerate(res, start=1):
            tabla_corridas.append({
                "Corrida": i,
                "s": policy[0],
                "S": policy[1],
                "Costo Total": round(r['total_cost'], 2),
                "Orden": round(r['ordering_cost'], 2),
                "Mantenimiento": round(r['holding_cost'], 2),
                "Faltante": round(r['shortage_cost'], 2),
            })

    df = pd.DataFrame(tabla_corridas)
    print(df.to_string(index=False))

    plot_results(policies_results)
    plot_inventory(inv_data, policies[0][0], policies[0][1])

def plot_results(policies_results):
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()
    metric_names = ["total_cost", "ordering_cost", "holding_cost", "shortage_cost"]
    titles = ["Costo total", "Costo de orden", "Costo de mantenimiento", "Costo de faltante"]
    ylabels = ["Costo total", "Costo orden", "Costo mantenimiento", "Costo faltante"]

    for idx, metric in enumerate(metric_names):
        ax = axes[idx]
        for policy in policies_results:
            corridas = range(1, len(policies_results[policy]) + 1)
            valores = [r[metric] for r in policies_results[policy]]
            label = f"(s={policy[0]}, S={policy[1]})"
            ax.plot(corridas, valores, marker='o', label=label)
        ax.set_title(titles[idx])
        ax.set_xlabel("Corrida")
        ax.set_ylabel(ylabels[idx])
        ax.grid(True)
        ax.legend()

    plt.tight_layout()
    plt.show()

def plot_inventory(inv_data, s, S):
    df = pd.DataFrame(inv_data)
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

    for idx, (col, ax, title) in enumerate(zip(
        ["I(t)", "I+(t)", "I-(t)"],
        axes,
        ["Inventario neto I(t)", "Inventario disponible I+(t)", "Faltantes I-(t)"]
    )):
        for corrida in df["corrida"].unique():
            datos = df[df["corrida"] == corrida]
            ax.plot(datos["mes"], datos[col], marker='o', label=f"Corrida {corrida}")

        # Líneas punteadas
        if idx == 0:
            ax.axhline(y=s, color='gray', linestyle='--', label=f"s = {s}")
            ax.axhline(y=S, color='gray', linestyle='--', label=f"S = {S}")
        else:
            ax.axhline(y=0, color='gray', linestyle='--')

        ax.set_title(title)
        ax.set_ylabel(col)
        ax.legend()

    axes[-1].set_xlabel("Mes")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
