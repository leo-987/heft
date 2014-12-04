from __future__ import division
import glob


def init():
    f = file("input.txt", 'r')

    line = f.readline().strip().split()
    glob.num_task = int(line[0])
    glob.num_processor = int(line[1])
    f.readline()    # blank line

    glob.tasks = [glob.Task(n) for n in range(glob.num_task)]
    glob.processors = [glob.Processor(n) for n in range(glob.num_processor)]

    # Computation matrix
    for task in glob.tasks:
        task.comp_cost = map(int, f.readline().strip().split())
    f.readline()    # blank line

    # Bandwidth matrix
    for i in range(glob.num_processor):
        glob.rate.append(map(int, f.readline().strip().split()))
    f.readline()    # blank line

    # Data matrix
    for i in range(glob.num_task):
        glob.data.append(map(int, f.readline().strip().split()))

    f.close()

    for task in glob.tasks:
        task.avg_comp = sum(task.comp_cost) / glob.num_processor

    cal_up_rank(glob.tasks[0])
    cal_down_rank(glob.tasks[-1])

    glob.tasks.sort(cmp=lambda x, y: cmp(x.up_rank, y.up_rank), reverse=True)


def cal_avg_comm(task1, task2):
    res = 0
    for line in glob.rate:
        for rate in line:
            if rate != 0:
                res += glob.data[task1.number][task2.number] / rate
    return res / (glob.num_processor ** 2 - glob.num_processor)


def cal_up_rank(task):
    longest = 0
    for successor in glob.tasks:
        if glob.data[task.number][successor.number] != -1:
            if successor.up_rank == -1:
                cal_up_rank(successor)

            longest = max(longest, cal_avg_comm(task, successor) + successor.up_rank)

    task.up_rank = task.avg_comp + longest


def cal_down_rank(task):
    if task == glob.tasks[0]:
        task.down_rank = 0
        return
    for pre in glob.tasks:
        if glob.data[pre.number][task.number] != -1:
            if pre.down_rank == -1:
                cal_down_rank(pre)

            task.down_rank = max(task.down_rank, pre.down_rank + pre.avg_comp + cal_avg_comm(pre, task))


def cal_est(task, processor):
    est = 0
    for pre in glob.tasks:
        if glob.data[pre.number][task.number] != -1:
            if pre.processor_num != processor.number:
                c = glob.data[pre.number][task.number] / glob.rate[pre.processor_num][processor.number]
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


def heft():
    for task in glob.tasks:
        if task == glob.tasks[0]:
            w = min(task.comp_cost)
            p = task.comp_cost.index(w)
            task.processor_num = p
            task.ast = 0
            task.aft = w
            glob.processors[p].time_line.append(glob.Duration(task.number, 0, w))
        else:
            aft = 9999
            for processor in glob.processors:
                est = cal_est(task, processor)
                if est + task.comp_cost[processor.number] < aft:
                    aft = est + task.comp_cost[processor.number]
                    p = processor.number

            task.processor_num = p
            task.ast = aft - task.comp_cost[p]
            task.aft = aft
            glob.processors[p].time_line.append(glob.Duration(task.number, task.ast, task.aft))
            glob.processors[p].time_line.sort(cmp=lambda x, y: cmp(x.start, y.start))


init()
for t in glob.tasks:
    print 'task %d : up_rank = %f, down_rank = %f' % (t.number, t.up_rank, t.down_rank)

heft()
for p in glob.processors:
    print 'processor %d:' % (p.number + 1)
    for duration in p.time_line:
        print 'task %d : ast = %d, aft = %d' % (duration.task_num + 1, duration.start, duration.end)