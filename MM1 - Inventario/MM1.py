import math
import random
import statistics
import matplotlib.pyplot as plt

# Constantes
BUSY = 1
IDLE = 0

class QueueSystem:
    def __init__(self, mean_service, mean_interarrival, queue_limit, num_delays_required):
        self.mean_service = mean_service
        self.mean_interarrival = mean_interarrival
        self.Q_LIMIT = queue_limit
        self.num_delays_required = num_delays_required
        
        self.next_event_type = self.num_custs_delayed = self.num_in_q = self.server_status = 0
        self.area_num_in_q = self.area_server_status = self.sim_time = self.time_last_event = self.total_of_delays = 0.0
        self.time_arrival = [0.0] * (self.Q_LIMIT + 1)
        self.time_next_event = [0.0] * 3
        self.num_in_system = 0
        self.area_num_in_system = 0.0
        self.total_time_in_system = 0.0
        self.num_arrivals = 0
        self.num_departures = 0
        self.num_denials = 0
        self.queue_count = [0] * (self.Q_LIMIT + 1)
        self.arrival_times = []

    def initialize(self):
        self.sim_time = 0.0
        self.server_status = IDLE
        self.num_in_q = 0
        self.time_last_event = 0.0
        self.num_custs_delayed = 0
        self.total_of_delays = 0.0
        self.area_num_in_q = 0.0
        self.area_server_status = 0.0
        self.time_next_event[1] = self.sim_time + self.expon(self.mean_interarrival)
        self.time_next_event[2] = 1e15
        self.num_in_system = 0
        self.area_num_in_system = 0.0
        self.total_time_in_system = 0.0
        self.num_arrivals = 0
        self.num_departures = 0
        self.num_denials = 0
        self.queue_count = [0] * (self.Q_LIMIT + 1)
        self.arrival_times = []

    def timing(self):
        min_time_next_event = 1e15
        self.next_event_type = 0

        for i in range(1, 3):
            if self.time_next_event[i] < min_time_next_event:
                min_time_next_event = self.time_next_event[i]
                self.next_event_type = i

        if self.next_event_type == 0:
            print(f"\nEvent list empty at time {self.sim_time}")
            exit(1)

        self.sim_time = min_time_next_event

    def arrive(self):
        self.time_next_event[1] = self.sim_time + self.expon(self.mean_interarrival)
        self.num_arrivals += 1
        

        if self.server_status == BUSY:
            self.num_in_q += 1
            if self.num_in_q > self.Q_LIMIT:
                self.num_in_q -= 1
                self.num_denials += 1
            else:
                self.arrival_times.append(self.sim_time)
                self.time_arrival[self.num_in_q] = self.sim_time
                self.num_in_system += 1
        else:
            self.arrival_times.append(self.sim_time)
            delay = 0.0
            self.total_of_delays += delay
            self.num_custs_delayed += 1
            self.server_status = BUSY
            self.time_next_event[2] = self.sim_time + self.expon(self.mean_service)
            self.num_in_system += 1

        self.queue_count[self.num_in_q] += 1

    def depart(self):
        if self.num_in_q == 0:
            self.server_status = IDLE
            self.time_next_event[2] = 1e15
        else:
            self.num_in_q -= 1
            delay = self.sim_time - self.time_arrival[1]
            self.total_of_delays += delay
            self.num_custs_delayed += 1
            self.time_next_event[2] = self.sim_time + self.expon(self.mean_service)
            for i in range(1, self.num_in_q + 1):
                self.time_arrival[i] = self.time_arrival[i + 1]

        self.num_departures += 1
        if self.arrival_times:
            arrival_time = self.arrival_times.pop(0)
            self.total_time_in_system += self.sim_time - arrival_time
        self.num_in_system -= 1

    def update_time_avg_stats(self):
        time_since_last_event = self.sim_time - self.time_last_event
        self.time_last_event = self.sim_time
        self.area_num_in_q += self.num_in_q * time_since_last_event
        self.area_server_status += self.server_status * time_since_last_event
        self.area_num_in_system += self.num_in_system * time_since_last_event

    def expon(self, mean):
        return -mean * math.log(random.random())

    def run_simulation(self):
        self.initialize()
        while self.num_custs_delayed < self.num_delays_required:
            self.timing()
            self.update_time_avg_stats()
            
            if self.next_event_type == 1:
                self.arrive()
            elif self.next_event_type == 2:
                self.depart()

        return self.report()

    def report(self):
        avg_delay = self.total_of_delays / self.num_custs_delayed
        avg_num_in_q = self.area_num_in_q / self.sim_time
        avg_num_in_system = self.area_num_in_system / self.sim_time
        avg_time_in_system = self.total_time_in_system / self.num_departures
        server_util = self.area_server_status / self.sim_time
        denial_prob = self.num_denials / self.num_arrivals if self.num_arrivals > 0 else 0

        queue_probs = [count / self.sim_time for count in self.queue_count[1:]]  # Excluimos el índice 0
        queue_probs.insert(0, 0)  # Añadimos 0 al principio para la probabilidad de 0 clientes en cola

        return {
            "avg_delay": avg_delay,
            "avg_num_in_q": avg_num_in_q,
            "avg_num_in_system": avg_num_in_system,
            "avg_time_in_system": avg_time_in_system,
            "server_util": server_util,
            "queue_probs": queue_probs,
            "denial_prob": denial_prob
        }

def run_experiments(mean_service, arrival_rates, queue_sizes, num_delays_required, num_runs):
    results = {}
    for rate in arrival_rates:
        mean_interarrival = mean_service / rate
        for q_size in queue_sizes:
            key = (rate, q_size)
            results[key] = []
            for _ in range(num_runs):
                system = QueueSystem(mean_service, mean_interarrival, q_size, num_delays_required)
                result = system.run_simulation()
                results[key].append(result)
    return results

def print_results(results):
    for (rate, q_size), runs in results.items():
        print(f"\nResultados para tasa de arribos {rate*100}% y tamaño de cola {q_size}:")
        avg_results = {
            k: statistics.mean(run[k] for run in runs) 
            for k in runs[0] if k != "queue_probs"
        }
        avg_results["queue_probs"] = [
            statistics.mean(run["queue_probs"][i] for run in runs)
            for i in range(len(runs[0]["queue_probs"]))
        ]
        
        print(f"Promedio de clientes en el sistema: {avg_results['avg_num_in_system']:.3f}")
        print(f"Promedio de clientes en cola: {avg_results['avg_num_in_q']:.3f}")
        print(f"Tiempo promedio en sistema: {avg_results['avg_time_in_system']:.3f}")
        print(f"Tiempo promedio en cola: {avg_results['avg_delay']:.3f}")
        print(f"Utilización del servidor: {avg_results['server_util']:.3f}")
        print(f"Probabilidad de denegación de servicio: {avg_results['denial_prob']:.3f}")
        print("Probabilidad de encontrar n clientes en cola:")
        for n, prob in enumerate(avg_results["queue_probs"]):
            if n > 0 and prob > 0:
                print(f"  {n}: {prob:.3f}")

def plot_results(results):
    arrival_rates = sorted(set(key[0] for key in results.keys()))
    queue_sizes = sorted(set(key[1] for key in results.keys()))
    
    metrics = ['avg_num_in_system', 'avg_num_in_q', 'avg_time_in_system', 'avg_delay', 'server_util']
    metric_names = ['Promedio de clientes en el sistema', 'Promedio de clientes en cola',
                    'Tiempo promedio en sistema', 'Tiempo promedio en cola', 'Utilización del servidor']
    
    for q_size in queue_sizes:
        fig, axs = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Resultados de la simulación de colas M/M/1 - Tamaño de cola: {q_size}', fontsize=16)
        
        for i, metric in enumerate(metrics):
            row = i // 3
            col = i % 3
            ax = axs[row, col]
            x = arrival_rates
            y = [statistics.mean(run[metric] for run in results[(rate, q_size)]) for rate in arrival_rates]
            ax.plot(x, y, marker='o', color='blue')
            ax.set_title(metric_names[i])
            ax.set_xlabel('Tasa de arribos (λ)')
            ax.set_ylabel('Valor')
            ax.grid(True)
        
        # Gráfica para la probabilidad de denegación
        ax = axs[1, 2]
        x = arrival_rates
        y = [statistics.mean(run['denial_prob'] for run in results[(rate, q_size)]) for rate in arrival_rates]
        ax.plot(x, y, marker='o', color='red')
        ax.set_title('Probabilidad de denegación')
        ax.set_xlabel('Tasa de arribos (λ)')
        ax.set_ylabel('Probabilidad')
        ax.grid(True)

        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        
    plt.show()

def print_and_plot_results(results):
    print_results(results)
    plot_results(results)

if __name__ == "__main__":
    random.seed(1)  # Para reproducibilidad
    
    print("Simulación de colas M/M/1")
    
    mean_service = float(input("Tiempo promedio de servicio: "))
    arrival_rates = [0.25, 0.5, 0.75, 1.0, 1.25]  # Tasas de arribo relativas al servicio
    queue_sizes = [0, 2, 5, 10, 50]  # Tamaños de cola a probar
    num_delays_required = int(input("Numero de clientes: "))  # Número de clientes a simular
    num_runs = 10  # Número de corridas por experimento

    results = run_experiments(mean_service, arrival_rates, queue_sizes, num_delays_required, num_runs)
    print_and_plot_results(results)