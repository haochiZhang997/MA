
class AppConfig:
    POOL_SEQUENCING_RULE = "FCFS" # Pool sequencing rule can be chosen from "FCFS", "CR", "EDD"
    DISPATCHING_RULE = "PST" # Dispatching rule can be chosen from "FCFS", "SPT", "PST"
    WORKLOAD_NORM = 5 # Workload norm for Order Release Control
    PLANNED_START_TIME_ALLOWANCE = 0.0 # Allowance for the waiting time per operation while using PST dispatching rule
    # zeit , kosten(wie viel idle), quality, productions controlling
    # region Jobs' and Stations' generation parameters
    NUM_JOBS = 40
    URGENT_JOBS = 10
    PROCESS_TIME_MEAN = 1.0 # Note: process times apply a 2-Erlang distribution with a truncated mean of 1 time unit
    PROCESS_TIME_MAX = 4.0
    PROCESS_TIME_MIN = 0.0
    DUE_DATE_RANGE = (5, 10)  # Due_date = arrival_time + due_date_range + total_processing_time
    #DUE_DATE_RANGE = (30, 45) 
    INTER_ARRIVAL_TIME_MEAN = 0.648
    STATION_TYPES = ['s1', 's2', 's3', 's4', 's5'] # 5 kinds of stations. If this variable is modified, make sure to re-match the settings in the JobGenerator class
    STATION_INSTANCES = {'s1': 1, 's2': 2, 's3': 2, 's4': 1, 's5': 1} # number of instances per type
    # endregion

app_config = AppConfig()