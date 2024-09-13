import os
import psutil

def kill_process_by_pid(pid):
    try:
        os.kill(pid, 9)
        print(f"Process with PID {pid} has been killed.")
    except Exception as e:
        print(f"Failed to kill process with PID {pid}: {e}")

def list_all_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def display_processes(processes):
    for proc in processes:
        cmdline = ' '.join(proc['cmdline']) if proc['cmdline'] else ''
        print(f"PID: {proc['pid']}, Name: {proc['name']}, Command Line: {cmdline}")

def filter_processes_by_keyword(processes, keyword):
    return [proc for proc in processes if proc['cmdline'] and keyword.lower() in ' '.join(proc['cmdline']).lower()]

def kill_processes_by_keyword(keyword):
    processes = list_all_processes()
    filtered_processes = filter_processes_by_keyword(processes, keyword)
    if filtered_processes:
        for proc in filtered_processes:
            try:
                psutil.Process(proc['pid']).kill()
                print(f"Killed process {proc['name']} (PID: {proc['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                print(f"Failed to kill process {proc['name']} (PID: {proc['pid']}): {e}")
    else:
        print(f"No processes found with keyword: {keyword}")

if __name__ == "__main__":
    # Step 1: List all processes
    processes = list_all_processes()
    display_processes(processes)

    # Step 2: Get keyword from user and filter processes
    keyword = input("\nEnter a keyword to filter processes: ")
    filtered_processes = filter_processes_by_keyword(processes, keyword)

    if filtered_processes:
        print("\nFiltered Processes:")
        display_processes(filtered_processes)

        # Step 3: Allow user to select which process to kill
        action = input("\nEnter '1' to kill a single process by PID or '2' to kill all processes by keyword: ")
        if action == '1':
            try:
                pid_to_kill = int(input("\nEnter the PID of the process you want to kill (or 0 to cancel): "))
                if pid_to_kill != 0:
                    kill_process_by_pid(pid_to_kill)
                else:
                    print("No process was killed.")
            except ValueError:
                print("Invalid PID entered.")
        elif action == '2':
            kill_processes_by_keyword(keyword)
        else:
            print("Invalid action selected.")
    else:
        print("No processes matched the keyword.")