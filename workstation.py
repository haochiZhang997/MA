import simpy
from loggerConfig import logger
from appConfig import app_config

class Workstation(object):
    def __init__(self, env, type_id, instance_id):
        self.env = env
        self.type_id = type_id
        self.instance_id = instance_id
        self.id = f"{type_id}-{instance_id}"
        self.resource = simpy.Resource(env, capacity=1)
        self.ws_job_queue = []
        self.idle = True
        self.idle_event = env.event()  # Initialize idle_event

    @property
    def current_load(self):
       # Calculate the current workload
        calculated_load = 0.0
        for job in self.ws_job_queue:
            calculated_load += job.process_times[job.current_operation]
        return calculated_load

    def add_job(self, job):
        # Add a job to the station's job queue
        self.ws_job_queue.append(job)

    def remove_job(self, job):
        # Remove a job from the station's job queue
        if job in self.ws_job_queue:
            self.ws_job_queue.remove(job)
        else:
            logger.warning("Job {job.id} can not be removed. It is not in the job queue of workstation {self.id}!")
            

    def __repr__(self):
        return (f"Workstation(id={self.id}, idle={self.idle}, "
                f"current_load={self.current_load:.3f}, "
                f"queue_length={len(self.ws_job_queue)})")
        
    def dispatching_rule(self):
        """
        Sort the job queue according to the dispatching rule
            FCFS: First come first serve
            SPT: Shortest processing time
            PST: Planned start time
        """
        if app_config.DISPATCHING_RULE == 'FCFS':
            self.ws_job_queue.sort(key=lambda job: job.arrival_time)
        elif app_config.DISPATCHING_RULE == 'SPT':
            self.ws_job_queue.sort(key=lambda job: job.process_times[job.current_operation])
        elif app_config.DISPATCHING_RULE == 'PST':
            self.ws_job_queue.sort(key=lambda job: job.planned_start_time)
        else:
            logger.error(f"Invalid dispatching rule, please choose from FCFS, SPT, PST")
            print("Invalid dispatching rule, please choose from FCFS, SPT, PST")
        
    def start_processing(self, stations_list, warehouses_list):
        while True:
            if len(self.ws_job_queue) == 0: # If the job queue is empty
                self.idle = True
                self.idle_event.succeed()  # Trigger the idle_event
                self.idle_event = self.env.event()  # Initialize idle_event for the next iteration
                yield self.env.timeout(1)  # Wait 1 time unit for new jobs
            else: # The job queue is not empty
                self.idle = False
                self.dispatching_rule() # Sort the job queue according to the dispatching rule
                job = self.ws_job_queue[0] # get the first job in the queue
                logger.debug(f"{self.env.now:.2f}: Dispatching_rule={app_config.DISPATCHING_RULE}, Station {self.id} has jobs:{self.ws_job_queue}")
                logger.debug(f"{self.env.now:.2f}: Station {self.id} start processing job {job.id}. " 
                            f"Expected processing time: {job.process_times[job.current_operation]}. "
                            f"current_load={self.current_load:.3f}")
                logger.debug(f"{self.env.now:.2f}: Job {job.id} is being processed at the workstation {self.id}.")
                yield self.env.process(self.process_job(job, stations_list, warehouses_list))


    def process_job(self, job, stations_list, warehouses_list):
        required_ws_id = job.detailed_routing[job.current_operation]
        if required_ws_id != self.id: # Make sure that the job belongs to the workstation
            logger.warning(f"{self.env.now:.2f}: Job {job.id} does not belong to the workstation {self.id}!")
        else: # Start processing the job
            with self.resource.request() as request:
                yield request
                process_time = job.process_times[job.current_operation]
                yield self.env.timeout(process_time)
            job.update_current_operation() # update the current operation
            
        # check if the job is finished
        if job.is_finished == False: # Job is not finished
            # Hand over to the next station
            next_st_id = job.detailed_routing[job.current_operation]
            next_ws = next((ws for ws in stations_list if ws.id == next_st_id), None)
            if next_ws is None:
                logger.error(f"{self.env.now:.2f}: The next station {next_st_id} of job {job.id} can not be found!")
            else:
                logger.debug(f"{self.env.now:.2f}: Job {job.id} is going to the next Station {next_st_id}.")
                next_ws.add_job(job)
                self.remove_job(job)
                
        else: # Job is finished, hand over to the warehouse
            target_warehouse = next((wh for wh in warehouses_list if wh.id == job.target_warehouse), None)
            if (target_warehouse is None):
                logger.error(f"{self.env.now:.2f}: Job {job.id} is finished but no target warehouse could be founded!")
            else:
                target_warehouse.add_item(job)
                self.remove_job(job)
                logger.debug(f"{self.env.now:.2f}: Job {job.id} finished at workstation {self.id} and is transported to the warehouse {target_warehouse.id}")

        
            