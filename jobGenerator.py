import numpy as np
import random
import logging
from preShopPool import Job

class TaskNode:
    def __init__(self, task_id, depth):
        self.task_id = task_id  # Task ID based on depth, e.g., "1.1", "2.2"
        self.depth = depth  # Depth in the tree
        self.children = []  # List to hold child tasks

class JobGenerator:
    def __init__(self, types, process_time_mean, process_time_min, process_time_max, inter_arrival_time_mean, due_date_range):
        self.types = types
        self.process_time_mean = process_time_mean
        self.process_time_min = process_time_min
        self.process_time_max = process_time_max
        self.inter_arrival_time_mean = inter_arrival_time_mean
        self.due_date_range = due_date_range
    
    def generate_fixed_tree_tasks(self):
        """
        Generate a fixed tree structure with six tasks.
        Task 1.1 -> Task 2.1, Task 2.2 -> Task 3.1 -> Task 4.1, Task 4.2
        """
        # Define tasks with fixed workstations
        task1_1 = TaskNode(task_id="1.1", depth=1, required_workstation=self.types[0])
        task2_1 = TaskNode(task_id="2.1", depth=2, required_workstation=self.types[2])
        task2_2 = TaskNode(task_id="2.2", depth=2, required_workstation=self.types[1])
        task3_1 = TaskNode(task_id="3.1", depth=3, required_workstation=self.types[3])
        task4_1 = TaskNode(task_id="4.1", depth=4, required_workstation=self.types[2])
        task4_2 = TaskNode(task_id="4.2", depth=4, required_workstation=self.types[4])

        # Define relationships
        task1_1.children.extend([task2_1, task2_2])
        task2_2.children.append(task3_1)
        task3_1.children.extend([task4_1, task4_2])

        # Return the root of the tree
        return task1_1

    def create_tasklist(self, root, max_depth):
        """
        Generate the task list by traversing the tree up to the specified depth.
        """
        tasklist = []
        def traverse(node):
            if node.depth > max_depth:
                return
            process_time = self.generate_erlang_2(scale=self.process_time_mean / 2, size=1)
            process_time = np.clip(process_time, self.process_time_min, self.process_time_max).tolist()

            task = {
                'id': node.task_id,
                'depth': node.depth,
                'required_workstation': node.required_workstation,
                'process_time': process_time
            }
            tasklist.append(task)

            for child in node.children:
                traverse(child)
        
        traverse(root)
        return tasklist

    def generate_jobs(self, num_jobs):
        """
        Generate a list of jobs, where each job contains a list of tasks with random generated disassembly depth .
        """
        jobs = []
        arrival_time = 0

        for job_id in range(1, num_jobs + 1):
            max_depth = np.random.randint(1, 5)  # This will determine how deep we execute disassembly tasks (between 1 and 4)
            root = self.generate_fixed_tree_tasks()
            tasklist = self.create_tasklist(root, max_depth)
            
         
            #sum_process_times = sum(sum(task['process_times']) for task in tasklist)
            arrival_time += np.random.exponential(self.inter_arrival_time_mean)
            due_date = arrival_time + np.random.uniform(*self.due_date_range) + sum_process_times
            
            job = Job(job_id, tasklist, arrival_time, due_date)
            self.logger.info(f"Create {job}")
            jobs.append(job)

        return jobs

    @staticmethod
    def generate_erlang_2(scale, size):
        """
        Generate 2 erlang distribution
            """
        erlang_2 = np.sum(np.random.exponential(scale, (2, size)), axis=0)
        return erlang_2


    
    # def generate_random_tree(self, num_tasks, linear_probability=0.6):
    #     """
    #     Generates a random tree of tasks. With a certain probability, the tree will
    #     be a single branch (linear sequence), otherwise, it will have a more complex structure.
    #     """
    #     is_linear = np.random.rand() < linear_probability
    #     root = TaskNode(task_id="1.1", depth=1)
    #     nodes = [root]
    #     if is_linear:
    #         current_node = root
    #         for i in range(2, num_tasks + 1):
    #             depth = current_node.depth + 1
    #             task_id = f"{depth}.1"
    #             new_node = TaskNode(task_id=task_id, depth=depth)
    #             current_node.children.append(new_node)
    #             nodes.append(new_node)
    #             current_node = new_node
    #     else:
    #         for i in range(2, num_tasks + 1):
    #             parent_node = random.choice(nodes)
    #             depth = parent_node.depth + 1
    #             task_id = f"{depth}.{len(parent_node.children) + 1}"
    #             child_node = TaskNode(task_id=task_id, depth=depth)
    #             parent_node.children.append(child_node)
    #             nodes.append(child_node)
    #     return root, nodes
    
    # def create_tasklist(self, task_nodes):
    #     """
    #     Create a task list from the generated task nodes, assigning workstations and process times.
    #     """
    #     tasklist = []
    #     for task_node in task_nodes:
    #         required_workstations = np.random.choice(self.types).tolist()
    #         process_times = self.generate_erlang_2(scale=self.process_time_mean / 2, size=len(required_workstations))
    #         process_times = np.clip(process_times, self.process_time_min, self.process_time_max)
            
    #         task = {
    #             'id': task_node.task_id,
    #             'depth': task_node.depth,
    #             'required_workstations': required_workstations,
    #             'process_times': process_times
    #         }
    #         tasklist.append(task)
        
    #     return tasklist

    # def generate_jobs(self, num_jobs):
    #     """
    #     Generate a list of jobs, where each job contains a randomly generated tree of tasks.
    #     """
    #     jobs = []
    #     arrival_time = 0

    #     for job_id in range(1, num_jobs + 1):
    #         num_tasks = np.random.randint(3, 7)
    #         root, task_nodes = self.generate_random_tree(num_tasks)
    #         tasklist = self.create_tasklist(task_nodes)
            
    #         sum_process_times = sum(sum(task['process_times']) for task in tasklist)
    #         arrival_time += np.random.exponential(self.inter_arrival_time_mean)
    #         due_date = arrival_time + np.random.uniform(*self.due_date_range) + sum_process_times
            
    #         job = Job(job_id, tasklist, arrival_time, due_date)
    #         self.logger.info(f"Create {job}")
    #         jobs.append(job)

    #     return jobs