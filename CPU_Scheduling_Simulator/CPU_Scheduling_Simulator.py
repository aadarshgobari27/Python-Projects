
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from collections import deque
import copy

# ---------- Utility Functions ----------
def calculate_times(processes):
    print("PID\tAT\tBT\tCT\tTAT\tWT")
    for p in processes:
        print(f"{p['pid']}\t{p['arrival_time']}\t{p['burst_time']}\t{p['completion_time']}\t{p['turnaround_time']}\t{p['waiting_time']}")

def plot_gantt(processes):
    fig, gnt = plt.subplots()
    gnt.set_title("Gantt Chart")
    gnt.set_xlabel("Time")
    gnt.set_ylabel("Processes")
    gnt.set_yticks([10 + i*10 for i in range(len(processes))])
    gnt.set_yticklabels([p['pid'] for p in processes])
    gnt.grid(True)

    for i, p in enumerate(processes):
        gnt.broken_barh([(p['start_time'], p['burst_time'])], (10 + i*10, 9))

    plt.show()

# ---------- Scheduling Algorithms ----------
def fcfs(processes):
    processes.sort(key=lambda x: x['arrival_time'])
    time = 0
    for p in processes:
        if time < p['arrival_time']:
            time = p['arrival_time']
        p['start_time'] = time
        time += p['burst_time']
        p['completion_time'] = time
        p['turnaround_time'] = p['completion_time'] - p['arrival_time']
        p['waiting_time'] = p['turnaround_time'] - p['burst_time']
    print("\n--- FCFS Scheduling ---")
    calculate_times(processes)
    plot_gantt(processes)

def sjf_non_preemptive(processes):
    processes.sort(key=lambda x: (x['arrival_time'], x['burst_time']))
    n = len(processes)
    time = 0
    completed = []
    remaining = processes.copy()

    while len(completed) < n:
        available = [p for p in remaining if p['arrival_time'] <= time]
        if not available:
            time = remaining[0]['arrival_time']
            continue
        shortest = min(available, key=lambda x: x['burst_time'])
        if time < shortest['arrival_time']:
            time = shortest['arrival_time']
        shortest['start_time'] = time
        time += shortest['burst_time']
        shortest['completion_time'] = time
        shortest['turnaround_time'] = shortest['completion_time'] - shortest['arrival_time']
        shortest['waiting_time'] = shortest['turnaround_time'] - shortest['burst_time']
        completed.append(shortest)
        remaining.remove(shortest)

    print("\n--- SJF (Non-Preemptive) Scheduling ---")
    calculate_times(completed)
    plot_gantt(completed)

def round_robin(processes, time_quantum):
    queue = deque()
    time = 0
    completed = 0
    processes = sorted(processes, key=lambda x: x['arrival_time'])
    remaining_bt = {p['pid']: p['burst_time'] for p in processes}
    pid_to_process = {p['pid']: p.copy() for p in processes}
    visited = set()
    i = 0

    while completed < len(processes):
        while i < len(processes) and processes[i]['arrival_time'] <= time:
            if processes[i]['pid'] not in visited:
                queue.append(processes[i]['pid'])
                visited.add(processes[i]['pid'])
            i += 1

        if not queue:
            time += 1
            continue

        current_pid = queue.popleft()
        process = pid_to_process[current_pid]

        if 'start_time' not in process:
            process['start_time'] = time

        if remaining_bt[current_pid] > time_quantum:
            time += time_quantum
            remaining_bt[current_pid] -= time_quantum
        else:
            time += remaining_bt[current_pid]
            remaining_bt[current_pid] = 0
            process['completion_time'] = time
            process['turnaround_time'] = time - process['arrival_time']
            process['waiting_time'] = process['turnaround_time'] - process['burst_time']
            completed += 1

        while i < len(processes) and processes[i]['arrival_time'] <= time:
            if processes[i]['pid'] not in visited:
                queue.append(processes[i]['pid'])
                visited.add(processes[i]['pid'])
            i += 1

        if remaining_bt[current_pid] > 0:
            queue.append(current_pid)

        pid_to_process[current_pid] = process

    print("\n--- Round Robin Scheduling (TQ =", time_quantum, ") ---")
    final_list = [pid_to_process[p['pid']] for p in processes]
    calculate_times(final_list)
    plot_gantt(final_list)

def priority_scheduling(processes):
    processes = [p.copy() for p in processes]
    n = len(processes)
    time = 0
    completed = []
    remaining = processes.copy()

    while len(completed) < n:
        available = [p for p in remaining if p['arrival_time'] <= time]
        if not available:
            time = remaining[0]['arrival_time']
            continue
        highest = min(available, key=lambda x: (x['priority'], x['arrival_time']))
        if time < highest['arrival_time']:
            time = highest['arrival_time']
        highest['start_time'] = time
        time += highest['burst_time']
        highest['completion_time'] = time
        highest['turnaround_time'] = highest['completion_time'] - highest['arrival_time']
        highest['waiting_time'] = highest['turnaround_time'] - highest['burst_time']
        completed.append(highest)
        remaining.remove(highest)

    print("\n--- Priority Scheduling (Non-Preemptive) ---")
    calculate_times(completed)
    plot_gantt(completed)

# ---------- Console Menu ----------
def main_menu():
    print("\nCPU Scheduling Simulator")
    print("------------------------")
    print("1. FCFS")
    print("2. SJF (Non-Preemptive)")
    print("3. Round Robin")
    print("4. Priority (Non-Preemptive)")
    choice = int(input("Enter your choice (1-4): "))

    n = int(input("Enter number of processes: "))
    processes = []
    for i in range(n):
        pid = f'P{i+1}'
        at = int(input(f"Enter Arrival Time for {pid}: "))
        bt = int(input(f"Enter Burst Time for {pid}: "))
        process = {'pid': pid, 'arrival_time': at, 'burst_time': bt}
        if choice == 4:
            pr = int(input(f"Enter Priority for {pid}: "))
            process['priority'] = pr
        processes.append(process)

    if choice == 1:
        fcfs(copy.deepcopy(processes))
    elif choice == 2:
        sjf_non_preemptive(copy.deepcopy(processes))
    elif choice == 3:
        tq = int(input("Enter Time Quantum: "))
        round_robin(copy.deepcopy(processes), tq)
    elif choice == 4:
        priority_scheduling(copy.deepcopy(processes))
    else:
        print("Invalid choice.")

# ---------- GUI Interface ----------
def launch_gui():
    def run_simulation():
        algo = algo_var.get()
        try:
            data = input_text.get("1.0", tk.END).strip().split("\n")
            processes = []
            for i, line in enumerate(data):
                parts = line.strip().split()
                p = {'pid': f'P{i+1}', 'arrival_time': int(parts[0]), 'burst_time': int(parts[1])}
                if algo == "Priority":
                    p['priority'] = int(parts[2])
                processes.append(p)

            if algo == "FCFS":
                fcfs(processes)
            elif algo == "SJF":
                sjf_non_preemptive(processes)
            elif algo == "Round Robin":
                tq = int(q_entry.get())
                round_robin(processes, tq)
            elif algo == "Priority":
                priority_scheduling(processes)
        except Exception as e:
            print(f"Error: {e}")

    win = tk.Tk()
    win.title("CPU Scheduling Simulator")

    tk.Label(win, text="Enter Processes (AT BT [Priority]):").pack()
    input_text = tk.Text(win, height=8, width=40)
    input_text.pack()

    algo_var = tk.StringVar(value="FCFS")
    ttk.Combobox(win, textvariable=algo_var, values=["FCFS", "SJF", "Round Robin", "Priority"]).pack()

    tk.Label(win, text="Time Quantum (for RR):").pack()
    q_entry = tk.Entry(win)
    q_entry.insert(0, "2")
    q_entry.pack()

    tk.Button(win, text="Run Simulation", command=run_simulation).pack()

    win.mainloop()

# To run:
# main_menu()  # For CLI
# launch_gui()  # For GUI
