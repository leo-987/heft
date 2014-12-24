from __future__ import division
from dag.create_input import init

"""
This module is the HEFT algorithm.
"""

# Time duration about a task
class Duration:
    def __init__(self, task, start, end):
        self.task_num = task
        self.start = start
        self.end = end


# Task class represent a task
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


# Processor class represent a processor
class Processor:
    def __init__(self, num):
        self.number = num
        self.time_line = []


# A class of scheduling algorithm
class HEFT:
    num_task = 0
    num_processor = 0
    tasks = []
    processors = []
    rate = []
    data = []

    def __init__(self, filename):
        """
        Initialize some parameters.
        """
        self.num_task, self.num_processor, comp_cost, self.rate, self.data = init(filename)

        self.tasks = [Task(n) for n in range(self.num_task)]
        self.processors = [Processor(n) for n in range(self.num_processor)]
        self.start_task_num, self.end_task_num = 0, 1

        for line in self.data:
            print line

        for i in range(self.num_task):
            self.tasks[i].comp_cost = comp_cost[i]

        for task in self.tasks:
            task.avg_comp = sum(task.comp_cost) / self.num_processor

        self.cal_up_rank(self.tasks[self.start_task_num])
        self.cal_down_rank(self.tasks[self.end_task_num])
        self.tasks.sort(cmp=lambda x, y: cmp(x.up_rank, y.up_rank), reverse=True)

    def cal_avg_comm(self, task1, task2):
        """
        Calculate the average communication cost between task1 and task2.
        """
        res = 0
        for line in self.rate:
            for rate in line:
                if rate != 0:
                    res += self.data[task1.number][task2.number] / rate
        return res / (self.num_processor ** 2 - self.num_processor)

    def cal_up_rank(self, task):
        """
        Calculate the upper rank of all tasks.
        Parameter task is the entry node of the DAG.
        """
        longest = 0
        for successor in self.tasks:
            if self.data[task.number][successor.number] != -1:
                if successor.up_rank == -1:
                    self.cal_up_rank(successor)

                longest = max(longest, self.cal_avg_comm(task, successor) + successor.up_rank)

        task.up_rank = task.avg_comp + longest

    def cal_down_rank(self, task):
        """
        Calculate the down rank of all tasks.
        Parameter task is the exit node of the DAG.
        """
        if task == self.tasks[self.start_task_num]:
            task.down_rank = 0
            return
        for pre in self.tasks:
            if self.data[pre.number][task.number] != -1:
                if pre.down_rank == -1:
                    self.cal_down_rank(pre)
    
                task.down_rank = max(task.down_rank,
                                     pre.down_rank + pre.avg_comp + self.cal_avg_comm(pre, task))

    def cal_est(self, task, processor):
        """
        Calculate the earliest start time of task on processor.
        """
        est = 0
        for pre in self.tasks:
            if self.data[pre.number][task.number] != -1:
                if pre.processor_num != processor.number:
                    c = self.data[pre.number][task.number] / self.rate[pre.processor_num][processor.number]
                else:
                    c = 0

                est = max(est, pre.aft + c)
    
        time_slots = []
        if len(processor.time_line) == 0:
            time_slots.append([0, 9999])
        else:
            for i in range(len(processor.time_line)):
                if i == 0:
                    if processor.time_line[i].start != 0:
                        time_slots.append([0, processor.time_line[i].start])
                    else:
                        continue
                else:
                    time_slots.append([processor.time_line[i - 1].end, processor.time_line[i].start])
    
            time_slots.append([processor.time_line[len(processor.time_line) - 1].end, 9999])
    
        for slot in time_slots:
            if est < slot[0] and slot[0] + task.comp_cost[processor.number] <= slot[1]:
                return slot[0]
            if est >= slot[0] and est + task.comp_cost[processor.number] <= slot[1]:
                return est

    def run(self):
        for task in self.tasks:
            if task == self.tasks[0]:
                w = min(task.comp_cost)
                p = task.comp_cost.index(w)
                task.processor_num = p
                task.ast = 0
                task.aft = w
                self.processors[p].time_line.append(Duration(task.number, 0, w))
            else:
                aft = 9999
                for processor in self.processors:
                    est = self.cal_est(task, processor)
                    if est + task.comp_cost[processor.number] < aft:
                        aft = est + task.comp_cost[processor.number]
                        p = processor.number
    
                task.processor_num = p
                task.ast = aft - task.comp_cost[p]
                task.aft = aft
                self.processors[p].time_line.append(Duration(task.number, task.ast, task.aft))
                self.processors[p].time_line.sort(cmp=lambda x, y: cmp(x.start, y.start))

    def display_result(self):
        for t in self.tasks:
            print 'task %d : up_rank = %f, down_rank = %f' % (t.number, t.up_rank, t.down_rank)
            if t.number == self.end_task_num:
                makespan = t.aft

        for p in self.processors:
            print 'processor %d:' % (p.number + 1)
            for duration in p.time_line:
                print 'task %d : ast = %d, aft = %d' % (duration.task_num + 1, duration.start, duration.end)

        print 'makespan = %d' % makespan