
class Warehouse(object):

    def __init__(self, env, type_id, instance_id):
        self.env = env
        self.type_id = type_id
        self.instance_id = instance_id
        self.id = f"{type_id}-{instance_id}"
        self.stock = []

    def add_item(self, job):
        job.finish_time = self.env.now
        job.overdue = job.finish_time - job.due_date
        self.stock.append(job)

    def __repr__(self):
        warehouse_repr = ", ".join(f"Job(id={job.id}, finish_time={job.finish_time})" for job in self.stock)
        return f"MyWarehouse(id={self.id}, items=[{warehouse_repr}])"
        