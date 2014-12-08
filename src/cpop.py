from __future__ import division


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
        self.is_cp = False


# Processor class represent a processor
class Processor:
    def __init__(self, num):
        self.number = num
        self.time_line = []


# A class of scheduling algorithm
class CPOP:
    num_task = 0
    num_processor = 0
    tasks = []
    processors = []
    rate = []
    data = []
    queue = []
    cp_num = -1     # The number of critical path processor

    def __init__(self, input_file):
        f = file(input_file, 'r')
        line = f.readline().strip().split()
        CPOP.num_task = int(line[0])
        CPOP.num_processor = int(line[1])
        f.readline()    # blank line

        CPOP.tasks = [Task(n) for n in range(CPOP.num_task)]
        CPOP.processors = [Processor(n) for n in range(CPOP.num_processor)]

        # Computation matrix
        for task in CPOP.tasks:
            task.comp_cost = map(int, f.readline().strip().split())
        f.readline()    # blank line

        # Bandwidth matrix
        for i in range(CPOP.num_processor):
            CPOP.rate.append(map(int, f.readline().strip().split()))
        f.readline()    # blank line

        # Data matrix
        for i in range(CPOP.num_task):
            CPOP.data.append(map(int, f.readline().strip().split()))

        f.close()

        for task in CPOP.tasks:
            task.avg_comp = sum(task.comp_cost) / CPOP.num_processor

        self.cal_up_rank(CPOP.tasks[0])
        self.cal_down_rank(CPOP.tasks[-1])
        self.cal_critical_path()
        self.cal_critical_processor()
        self.sort_tasks(CPOP.tasks[0])

    def cal_critical_path(self):
        cp_length = CPOP.tasks[0].up_rank + CPOP.tasks[0].down_rank
        for task in CPOP.tasks:
            if round(task.up_rank + task.down_rank) == round(cp_length):
                task.is_cp = True

    def cal_critical_processor(self):
        cost = [0] * CPOP.num_processor
        for task in CPOP.tasks:
            if task.is_cp:
                for i in range(CPOP.num_processor):
                    cost[i] += task.comp_cost[i]
        CPOP.cp_num = cost.index(min(cost))

    def sort_tasks(self, task):
        for pre in CPOP.tasks:
            if CPOP.data[pre.number][task.number] != -1 and pre not in CPOP.queue:
                return

        CPOP.queue.append(task)
        for successor in CPOP.tasks:
            if CPOP.data[task.number][successor.number] != -1:
                self.sort_tasks(successor)

    def cal_avg_comm(self, task1, task2):
        res = 0
        for line in CPOP.rate:
            for rate in line:
                if rate != 0:
                    res += CPOP.data[task1.number][task2.number] / rate
        return res / (CPOP.num_processor ** 2 - CPOP.num_processor)

    def cal_up_rank(self, task):
        longest = 0
        for successor in CPOP.tasks:
            if CPOP.data[task.number][successor.number] != -1:
                if successor.up_rank == -1:
                    self.cal_up_rank(successor)

                longest = max(longest, self.cal_avg_comm(task, successor) + successor.up_rank)

        task.up_rank = task.avg_comp + longest

    def cal_down_rank(self, task):
        if task == CPOP.tasks[0]:
            task.down_rank = 0
            return
        for pre in CPOP.tasks:
            if CPOP.data[pre.number][task.number] != -1:
                if pre.down_rank == -1:
                    self.cal_down_rank(pre)
    
                task.down_rank = max(task.down_rank,
                                     pre.down_rank + pre.avg_comp + self.cal_avg_comm(pre, task))

    def cal_est(self, task, processor):
        est = 0
        for pre in CPOP.tasks:
            if CPOP.data[pre.number][task.number] != -1:
                if pre.processor_num != processor.number:
                    c = CPOP.data[pre.number][task.number] / CPOP.rate[pre.processor_num][processor.number]
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
        for task in CPOP.queue:
            if task.is_cp:
                task.ast = self.cal_est(task, CPOP.processors[CPOP.cp_num])
                task.aft = task.ast + task.comp_cost[CPOP.cp_num]
                task.processor_num = CPOP.cp_num
                CPOP.processors[CPOP.cp_num].time_line.append(Duration(task.number, task.ast, task.aft))
                CPOP.processors[CPOP.cp_num].time_line.sort(cmp=lambda x, y: cmp(x.start, y.start))
            else:
                aft = 9999
                for processor in CPOP.processors:
                    est = self.cal_est(task, processor)
                    if est + task.comp_cost[processor.number] < aft:
                        aft = est + task.comp_cost[processor.number]
                        p = processor.number
    
                task.processor_num = p
                task.ast = aft - task.comp_cost[p]
                task.aft = aft
                CPOP.processors[p].time_line.append(Duration(task.number, task.ast, task.aft))
                CPOP.processors[p].time_line.sort(cmp=lambda x, y: cmp(x.start, y.start))

    def display_result(self):
        for t in CPOP.tasks:
            print 'task %d : up_rank = %f, down_rank = %f' % (t.number, t.up_rank, t.down_rank)

        for p in CPOP.processors:
            print 'processor %d:' % (p.number + 1)
            for duration in p.time_line:
                print 'task %d : ast = %d, aft = %d' % (duration.task_num + 1, duration.start, duration.end)