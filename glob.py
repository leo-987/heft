# global variables

num_task = 0
num_processor = 0
tasks = []
processors = []
rate = []
data = []


class Duration:
    def __init__(self, task, start, end):
        self.task_num = task
        self.start = start
        self.end = end


class Task:
    def __init__(self, num):
        self.number = num
        self.ast = -1
        self.aft = -1
        self.processor_num = -1
        self.up_rank = -1
        self.down_rank = -1
        self.comp_cost = []
        self.avg_comp = 0


class Processor:
    def __init__(self, num):
        self.number = num
        self.time_line = []