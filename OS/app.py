from flask import Flask, render_template, request

app = Flask(__name__)

def fcfs(processes):
    n = len(processes)
    processes.sort(key=lambda x: x[0])  
    gantt_chart = []
    current_time = 0
    waiting_times = [0] * n
    turnaround_times = [0] * n

    for process in processes:
        arrival_time, burst_time, _ = process
        if arrival_time > current_time:
            current_time = arrival_time
        waiting_time = current_time - arrival_time
        turnaround_time = waiting_time + burst_time
        gantt_chart.append(f'P{processes.index(process)}')
        current_time += burst_time
        waiting_times[processes.index(process)] = waiting_time
        turnaround_times[processes.index(process)] = turnaround_time

    return gantt_chart, waiting_times, turnaround_times

def sjf(processes):
    n = len(processes)
    processes.sort(key=lambda x: (x[0], x[1])) 
    gantt_chart = []
    current_time = 0
    waiting_times = [0] * n
    turnaround_times = [0] * n
    remaining_burst_times = [burst_time for _, burst_time, _ in processes]

    while any(remaining_burst_times):
        available_processes = [(i, burst_time) for i, burst_time in enumerate(remaining_burst_times) if burst_time > 0 and processes[i][0] <= current_time]
        if not available_processes:
            current_time += 1
            continue
        shortest_process = min(available_processes, key=lambda x: x[1])
        process_index, burst_time = shortest_process
        gantt_chart.append(f'P{process_index}')
        current_time += burst_time
        waiting_time = current_time - processes[process_index][0] - processes[process_index][1]
        turnaround_time = waiting_time + processes[process_index][1]
        waiting_times[process_index] = waiting_time
        turnaround_times[process_index] = turnaround_time
        remaining_burst_times[process_index] = 0

    return gantt_chart, waiting_times, turnaround_times


import heapq

def sjf(processes):
    n = len(processes)
    processes.sort(key=lambda x: x[0])
    gantt_chart = []
    current_time = 0
    waiting_times = [0] * n
    turnaround_times = [0] * n
    available_processes = []  

    i = 0  
    while i < n or available_processes:
        while i < n and processes[i][0] <= current_time:
            heapq.heappush(available_processes, (processes[i][1], i))
            i += 1

        if available_processes:
            burst_time, process_index = heapq.heappop(available_processes)
            gantt_chart.append(f'P{process_index}')
            waiting_time = current_time - processes[process_index][0]
            turnaround_time = waiting_time + burst_time
            current_time += burst_time
            waiting_times[process_index] = waiting_time
            turnaround_times[process_index] = turnaround_time
        else:
            current_time = processes[i][0]

    return gantt_chart, waiting_times, turnaround_times

def round_robin(processes, time_quantum):
    n = len(processes)
    gantt_chart = []
    current_time = 0
    remaining_burst_times = [burst_time for _, burst_time, _ in processes]
    waiting_times = [0] * n
    turnaround_times = [0] * n

    while any(remaining_burst_times):
        for i in range(n):
            if remaining_burst_times[i] > 0:
                if remaining_burst_times[i] <= time_quantum:
                    gantt_chart.append(f'P{i}')
                    current_time += remaining_burst_times[i]
                    remaining_burst_times[i] = 0
                    turnaround_time = current_time - processes[i][0]
                    waiting_times[i] = turnaround_time - processes[i][1]
                    turnaround_times[i] = turnaround_time
                else:
                    gantt_chart.append(f'P{i}')
                    current_time += time_quantum
                    remaining_burst_times[i] -= time_quantum

    return gantt_chart, waiting_times, turnaround_times

# ...

def non_preemptive_priority(processes):
    n = len(processes)
    processes.sort(key=lambda x: (x[0], -x[2]))  
    gantt_chart = []
    current_time = 0
    waiting_times = [0] * n
    turnaround_times = [0] * n

    i = 0 
    while i < n:
        if processes[i][0] <= current_time:
            highest_priority_process = max(processes[i:], key=lambda x: x[2])
            process_index = processes.index(highest_priority_process)
            gantt_chart.append(f'P{process_index}')
            waiting_time = current_time - processes[process_index][0]
            turnaround_time = waiting_time + highest_priority_process[1]
            current_time += highest_priority_process[1]
            waiting_times[process_index] = waiting_time
            turnaround_times[process_index] = turnaround_time
            i += 1
        else:
            current_time += 1

    return gantt_chart, waiting_times, turnaround_times




def preemptive_priority(processes):
    n = len(processes)
    gantt_chart = []
    current_time = 0
    remaining_burst_times = [burst_time for _, burst_time, _ in processes]
    waiting_times = [0] * n
    turnaround_times = [0] * n

    while any(remaining_burst_times):
        available_processes = [(i, burst_time, priority) for i, (burst_time, _, priority) in enumerate(processes) if burst_time > 0 and processes[i][0] <= current_time]
        if not available_processes:
            current_time += 1
            continue
        highest_priority_process = min(available_processes, key=lambda x: x[2])
        process_index, burst_time, _ = highest_priority_process
        gantt_chart.append(f'P{process_index}')
        current_time += 1
        remaining_burst_times[process_index] -= 1
        if remaining_burst_times[process_index] == 0:
            turnaround_time = current_time - processes[process_index][0]
            waiting_times[process_index] = turnaround_time - processes[process_index][1]
            turnaround_times[process_index] = turnaround_time

    return gantt_chart, waiting_times, turnaround_times



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        algorithm = request.form.get('algorithm')
        arrival_times = list(map(int, request.form.get('arrival_times').split(',')))
        burst_times = list(map(int, request.form.get('burst_times').split(',')))
        priorities = list(map(int, request.form.get('priorities').split(',')))
        time_quantum = int(request.form.get('time_quantum'))

        processes = list(zip(arrival_times, burst_times, priorities))

        if algorithm == 'fcfs':
            gantt_chart, waiting_times, turnaround_times = fcfs(processes)
        elif algorithm == 'sjf':
            gantt_chart, waiting_times, turnaround_times = sjf(processes)
        elif algorithm == 'srtf':
            gantt_chart, waiting_times, turnaround_times = srtf(processes)
        elif algorithm == 'round_robin':
            gantt_chart, waiting_times, turnaround_times = round_robin(processes, time_quantum)
        elif algorithm == 'non_preemptive_priority':
            gantt_chart, waiting_times, turnaround_times = non_preemptive_priority(processes)
        elif algorithm == 'preemptive_priority':
            gantt_chart, waiting_times, turnaround_times = preemptive_priority(processes)

        avg_waiting_time = sum(waiting_times) / len(waiting_times)
        avg_turnaround_time = sum(turnaround_times) / len(turnaround_times)
        num_processes = len(waiting_times)

        return render_template('result.html', gantt_chart=gantt_chart, waiting_times=waiting_times, turnaround_times=turnaround_times,
                               avg_waiting_time=avg_waiting_time, avg_turnaround_time=avg_turnaround_time, num_processes=num_processes,
                               arrival_times=arrival_times, burst_times=burst_times, priorities=priorities)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
