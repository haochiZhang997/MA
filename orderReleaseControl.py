import sys
from loggerConfig import logger
from appConfig import app_config

class OrderReleaseControl(object):
    def __init__(self, env):
        self.env = env

    def select_station(self, workstations):
        """
        This method is used to select the workstation with the least current load
        Args:
            workstations (list): list of workstations
        """
        return min(workstations, key=lambda ws: ws.current_load)
    
    def sort_jobs(self, job_list):
        """
        This method is used to sort the jobs based on the specified pool sequencing rule
            FCFS: First Come First Served
            EDD: Earliest Due Date
            CR: Critical Ratio = (Due Date - Current Time) / Total Processing Time
        """
        rule = app_config.POOL_SEQUENCING_RULE
        if len(job_list) > 0:
            if rule == "FCFS":
                job_list.sort(key=lambda job: (job.priority, job.arrival_time))
            elif rule == "EDD":
                job_list.sort(key=lambda job: (job.priority, job.due_date))
            elif rule == "CR":
                job_list.sort(key=lambda job: (job.priority, (job.due_date - self.env.now) / job.total_processing_time))
            else:
                logger.error("Invalid pool sequencing rule, please choose from FCFS, EDD, CR")
                print("Invalid pool sequencing rule, please choose from FCFS, EDD, CR")
                
    def order_release_with_lums_cor(self, job_list, stations_list, norm_load):
        """
        This method is used to release jobs based on the LUMS COR rule
        Args:
            job_list (list): list of jobs
            stations_list (list): list of workstations
            norm_load (float): normal load
        """
        logger.info(f"{self.env.now:.2f}: Start LUMS COR order release control")
        # Start periodic release process
        self.env.process(self.periodic_release(job_list, stations_list, norm_load))

        # Continuous release trigger when any workstation becomes idle
        for station in stations_list:
            self.env.process(self.continuous_release(job_list, stations_list, station))

    def periodic_release(self, job_list, stations_list, norm_load):
        while True:
            yield self.env.timeout(4) # Periodic release every 4 time units
            logger.info(f"{self.env.now:.2f}: New round of Periodic Order Release: there remains {len(job_list)} jobs.")
            if len(job_list) > 0:
                self.sort_jobs(job_list)  # Sort job list
                # Go through the job list, decide for each job whether it can be released or not
                for job in job_list[:]:  
                    self.set_detailed_routing(job, stations_list)
                    if self.can_release_job(job, stations_list, norm_load):
                        self.release_job(job, stations_list)
                        job_list.remove(job)
                
    def continuous_release(self, job_list, stations_list, station):
        while True:
            yield station.idle_event  # Wait until the workstation becomes idle
            logger.debug(f"{self.env.now:.2f}: Station {station.id} is idle, triggering job release check.")
            if len(job_list) > 0:
                self.sort_jobs(job_list)# Sort job list
                # Find the first job that can be routed to the idle station, regardless of its workload
                for job in job_list:
                    next_ws_id = job.operations_sequence[job.current_operation]
                    if station.id.startswith(f"{next_ws_id}"):
                        logger.info(f"{self.env.now:.2f}: Continous release triggered: Found job {job.id} for Station {station.id}.")
                        self.set_detailed_routing(job, stations_list)
                        self.release_job(job, stations_list)
                        job_list.remove(job)
                        break  # Only release one job for this station
    
    def set_detailed_routing(self, job, stations_list):
        detailed_routing = []  # Create a detailed routing list that contains the specific workstation id 
        for operation_index in range(job.current_operation, len(job.operations_sequence)):  # Estimate the workload of each required workstation after job release
            st_type_id = job.operations_sequence[operation_index]  # Get the required workstation type id
            stations_suitable = [st for st in stations_list if st.id.startswith(f"{st_type_id}")]  # Get all suitable workstations
            ws = self.select_station(stations_suitable)  # Always select the workstation with the least work load
            detailed_routing.append(ws.id)  # Add to detailed routing 
        job.detailed_routing = detailed_routing

    def can_release_job(self, job, stations_list, norm_load):
        logger.info(f"{self.env.now:.2f}: Periodic release: Checking job {job.id}, routing info: {job.operations_sequence}")
        temp_loads = {ws.id: round(float(ws.current_load), 3) for ws in stations_list}  # Current workload of each workstation
        logger.info(f"{self.env.now:.2f}: Current workload: {temp_loads}")
        for operation_index in range(job.current_operation, len(job.operations_sequence)):  # Estimate the workload of each required workstation after job release
            required_ws_id = job.detailed_routing[operation_index]
            required_ws = next((station for station in stations_list if station.id == required_ws_id), None)
            corrected_load = job.process_times[operation_index] / (operation_index + 1) + required_ws.current_load  # Calculate the corrected load
            if required_ws is None:
                logger.error(f"{self.env.now:.2f}: No workstation found with id {required_ws_id} while setting detailed routing")
            if corrected_load > norm_load:
                logger.info(f"{self.env.now:.2f}: Exceeding the normal load! job {job.id} cannot be released to the station {required_ws_id}")
                return False
        return True
    
    def release_job(self, job, stations_list):
        logger.debug(f"{self.env.now:.2f}: Job {job.id} is released with routing: {job.detailed_routing}, process_times: {job.process_times}")
        next_ws_id = job.detailed_routing[job.current_operation]
        next_station = next((station for station in stations_list if station.id == next_ws_id), None)
        if next_station:
            next_station.ws_job_queue.append(job)
            logger.info(f"{self.env.now:.2f}: job {job.id} is released, adding workload {job.process_times[job.current_operation]} to Station {next_station.id}")
        else:
            logger.error(f"{self.env.now:.2f}: No workstation found with id {next_ws_id}")

    # def adjust_workload_norms(self):
    #     # dynmic load adujstment
    #     total_load = sum(ws.current_load for ws in self.stations)
    #     avg_load = total_load / len(self.stations)
    #     for ws in self.stations:
    #         ws.norm_load = max(1, avg_load * 1.5)  

        
                

                        


                  
                   