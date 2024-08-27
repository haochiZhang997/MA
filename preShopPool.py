from appConfig import app_config
from loggerConfig import logger

class PreShopPool(object):
    def __init__(self) :
        self.job_list = []


class Job(object):
    def __init__(self, id, task_list, process_times, arrival_time, due_date, priority=2, target_warehouse=None):
        self.id = id
        #self.operations_sequence = operations_squence
        self.task_list = task_list
        self.process_times = process_times
        self.total_processing_time = sum(process_times)
        self.arrival_time = arrival_time
        self.due_date = due_date
        self.priority = priority # 2 = normal (default), 1 = urgent, 0 = emergency
        self.target_warehouse = target_warehouse if target_warehouse is not None else 'output-warehouse'

        self.current_operation = 0 # Initialize current operation to 0
        self.detailed_routing = [] # Routing information based on work station id
        self.overdue = None # Job is overdue when > 0
        self.is_finished = False
        self.finish_time = None
    
    @property
    def planned_start_time(self):
        k = app_config.PLANNED_START_TIME_ALLOWANCE # k = allowance for the waiting time per operation
        routing = self.operations_sequence
        if 0 <= self.current_operation < len(routing):
            remaining_operation_indices = list(range(self.current_operation, len(routing)))
            pst = self.due_date - sum([self.process_times[i] + k for i in remaining_operation_indices]) # calculate the planned start time
            return pst
        else:
            logger.error("Failed to calculate planned start time.")
            print("Failed to calculate planned start time.")
            return None

    def update_current_operation(self):
        if self.current_operation < len(self.operations_sequence) - 1:
            self.current_operation += 1
        else:
            self.current_operation = None
            self.is_finished = True

    def __repr__(self):
        return (f"Job(id={self.id}, routing={self.operations_sequence}, process_times={self.process_times}, arrival_time={self.arrival_time:.3f}, due_date={self.due_date:.3f}, PST={self.planned_start_time})")

