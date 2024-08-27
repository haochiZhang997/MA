import simpy
import numpy as np
import re
from workstation import  Workstation
from warehouse import Warehouse
from preShopPool import Job, PreShopPool
from orderReleaseControl import OrderReleaseControl
from loggerConfig import logger
from appConfig import app_config


class Main():
    def __init__(self, env):
        self.env = env
        self.stations_list = []
        self.warehouses_list = []

    
    def create_stations_and_warehouses(self):
        """
        This method is used to create stations and warehouses.
        """
        types = app_config.STATION_TYPES  # 5 type station
        instances_per_type = app_config.STATION_INSTANCES  # number of instances per type
        for type_id in types:
            for instance_id in range(1, instances_per_type[type_id] + 1):
                ws = Workstation(self.env, type_id, instance_id)
                self.stations_list.append(ws)
                logger.info(f"Create {ws}")

        output_warehouse = Warehouse(self.env, 'output', 'warehouse') # create the output warehouse
        self.warehouses_list.append(output_warehouse)
        logger.info(f"Create {output_warehouse}")
    


def generate_erlang_2(scale, size):
    """
    Generate 2 erlang distribution
    """
    erlang_2 = np.sum(np.random.exponential(scale, (2, size)), axis=0)
    return erlang_2

def create_jobs():
    """
    This method is used to create jobs according to the parameters.

    Returns: 
        jobs (list): The list of jobs that will be generated
    """
    jobs = []
    arrival_time = 0 # Initialize the arrival time to 0
    num_jobs = app_config.NUM_JOBS
    process_time_mean = app_config.PROCESS_TIME_MEAN
    process_time_max = app_config.PROCESS_TIME_MAX
    process_time_min = app_config.PROCESS_TIME_MIN 
    due_date_range = app_config.DUE_DATE_RANGE
    inter_arrival_time_mean = app_config.INTER_ARRIVAL_TIME_MEAN
    types = app_config.STATION_TYPES
    for job_id in range(1, num_jobs + 1):
        required_num_stations = np.random.randint(2, 6)  # randomly choose between 2 and 5 stations that a job requires
        operations_squence = np.random.choice(types, required_num_stations, replace=False).tolist()  # randomly sample stations without replacement
        process_times = generate_erlang_2(scale=process_time_mean/2, size=required_num_stations) # generate process times for each station
        process_times = np.clip(process_times, process_time_min, process_time_max) 
        sum_process_times = sum(process_times)
        arrival_time += np.random.exponential(inter_arrival_time_mean) # generate inter-arrival time
        due_date = arrival_time + np.random.uniform(*due_date_range) + sum_process_times # generate due date
        job = Job(job_id, operations_squence, process_times, arrival_time, due_date) # create a job
        logger.info(f"Create {job}")
        jobs.append((job))
    return jobs

def create_urgent_jobs():
    """
    This method is used to create 10 urgent jobs according to the parameters.

    Returns: 
        jobs (list): The list of jobs that will be generated
    """
    urgent_jobs = []
    arrival_time = 0 # Initialize the arrival time to 0
    num_jobs = app_config.URGENT_JOBS
    process_time_mean = app_config.PROCESS_TIME_MEAN
    process_time_max = app_config.PROCESS_TIME_MAX
    process_time_min = app_config.PROCESS_TIME_MIN 
    due_date_range = app_config.DUE_DATE_RANGE
    inter_arrival_time_mean = app_config.INTER_ARRIVAL_TIME_MEAN
    types = app_config.STATION_TYPES
    for urgent_job_id in range(1, num_jobs + 1):
        required_num_stations = np.random.randint(2, 6)  # randomly choose between 2 and 5 stations that a job requires
        operations_squence = np.random.choice(types, required_num_stations, replace=False).tolist()  # randomly sample stations without replacement
        process_times = generate_erlang_2(scale=process_time_mean/2, size=required_num_stations) # generate process times for each station
        process_times = np.clip(process_times, process_time_min, process_time_max) 
        sum_process_times = sum(process_times)
        arrival_time += np.random.exponential(inter_arrival_time_mean) # generate inter-arrival time
        due_date = arrival_time + np.random.uniform(*due_date_range) + sum_process_times # generate due date
        job = Job(f"u{urgent_job_id}", operations_squence, process_times, arrival_time, due_date, priority= 1) # create urgent job
        logger.info(f"Create {job}")
        urgent_jobs.append((job))
    return urgent_jobs

    
def start_job_generate(env, job_list, jobs):
    """
    This method is used to generate jobs in Simpy envrionment according to the inter-arrival time.
    Note: A job appears at a specific time point and is added to the environment and the job list at that moment. 

    Args:
        env (simpy.Environment): The simulation environment
        job_list (list): The list of jobs that is used by the pre-shop pool
        jobs (list): The list of jobs that will be generated
    """
    for job in jobs:
        arrival_time = job.arrival_time
        yield env.timeout(arrival_time - env.now)
        job_list.append(job)

def extract_job_id(log):
    """
    This method is used to extract the Job id info from the log file.
    """
    match = re.search(r'Job (\w+)', log)
    if match:
        return match.group(1)
    return 'zzzz'   

def filter_st_id(log):
    """
    This method is used to filter the Station id info from the log file.
    """
    match_st = re.search(r'Station (\w+-\d+)', log)
    if match_st:
        return float('inf')

def extract_st_id(log):
    """
    This method is used to extract the Station id info from the log file.
    """
    match = re.search(r'Station (\w+-\d+)', log)
    if match:
        return match.group(1)
    return 'zzzz' # Return 'zzzz' if no match is found to ensure it's sorted at the end.

def print_results():
    """
    This method is used to print the results.
    """
    print(f"Simulation finished")
    logger.info(f"Simulation finished")
    # Print the jobs in output warehouse
    overdue_job_count = 0
    total_overdue_time = 0
    for wh in main_simulation.warehouses_list:
        logger.info(f"warehouse {wh.id} has {len(wh.stock)} items: ")
        overdue_urgent_jobs = [job for job in wh.stock if str(job.id).startswith('u') and job.overdue > 0]
        overdue_urgent_count = len(overdue_urgent_jobs)
        for job in wh.stock:
            overdue_job_count += 1 if job.overdue > 0 else 0
            total_overdue_time += job.overdue if job.overdue > 0 else 0
            print(f"Job(id={job.id}, arrival_time={job.arrival_time:.3f}, finish_time={job.finish_time:.3f}, "
                  f"total_process_time={job.total_processing_time:.3f}, due_date={job.due_date:.3f}, overdue={job.overdue:.3f})")       
            logger.info(f"Job(id={job.id}, arrival_time={job.arrival_time:.3f}, finish_time={job.finish_time:.3f}, "
                        f"total_process_time={job.total_processing_time:.3f}, due_date={job.due_date:.3f}, overdue={job.overdue:.3f})")
    print (f"total overdue jobs: {overdue_job_count}, total overdue urgent jobs: {overdue_urgent_count}, total overdue time: {total_overdue_time:.3f}")
    logger.info(f"total overdue jobs: {overdue_job_count}, total overdue urgent jobs: {overdue_urgent_count}, total overdue time: {total_overdue_time:.3f}")

    # region create sorted log files
    with open(input_file, 'r') as file:
        logs = file.readlines()
    # Sort the log file by job id 
    filtered_job_logs = [log for log in logs if filter_st_id(log) != float('inf')]
    sorted_by_job_id = sorted(filtered_job_logs, key=extract_job_id) 
    with open(output_file, 'w') as file:
        file.writelines(sorted_by_job_id)
    # Sort the log file by station id
    #filtered_station_logs = [log for log in logs if filter_st_id(log) == float('inf')]
    sorted_by_st_id = sorted(logs, key=extract_st_id)
    with open(output_file2, 'w') as file:
        file.writelines(sorted_by_st_id)
    # endregion

input_file = 'app_all_logs.log'
output_file = 'app_job_logs.log'
output_file2 = 'app_station_logs.log'
np.random.seed(42)
np.set_printoptions(precision=3, suppress=True)

if __name__ == "__main__":  
    env = simpy.Environment()
    main_simulation = Main(env)
    main_simulation.create_stations_and_warehouses()
    stations_list = main_simulation.stations_list
    warehouses_list = main_simulation.warehouses_list
    jobs = create_jobs() # Note: jobs are created and waiting to be added to pre order pool
    ugent_jobs = create_urgent_jobs() # Create some urgent jobs
    all_jobs = jobs + ugent_jobs
    all_jobs.sort(key=lambda job: job.arrival_time)

    # start the simulation
    norm_load = app_config.WORKLOAD_NORM
    orderReleaseControl = OrderReleaseControl(env)
    preShopPool = PreShopPool()
    env.process(start_job_generate(env, preShopPool.job_list, all_jobs)) # Note: jobs are added to pre order pool according to its arrival time
    orderReleaseControl.order_release_with_lums_cor(preShopPool.job_list, stations_list, norm_load) # Start the order release control
    for ws in stations_list:
        env.process(ws.start_processing(stations_list, warehouses_list)) # Let each station start processing
    env.run(until=50)
    print_results()


    
       
        
    