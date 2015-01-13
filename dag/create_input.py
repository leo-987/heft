import re


def init(filename):
    """
    This function read the tgff file and
    build computation matrix, communication matrix, rate matrix.
    TGFF is a useful tool to generate directed acyclic graph, tfgg file represent a task graph.
    """
    f = file(filename, 'r')
    f.readline()
    f.readline()
    f.readline()

    # Calculate the amount of tasks
    num_of_tasks = 0
    while f.readline().startswith('\tTASK'):
        num_of_tasks += 1
    #print 'Number of tasks = %d' % num_of_tasks

    # Build a communication matrix
    data = [[-1 for i in range(num_of_tasks)] for i in range(num_of_tasks)]
    line = f.readline()
    while line.startswith('\tARC'):
        line = re.sub(r'\bt\d_', '', line)
        i, j, d = [int(s) for s in line.split() if s.isdigit()]
        data[i][j] = d
        line = f.readline()
    #for line in data:
    #    print line

    while not f.readline().startswith('@computation_cost'):
        pass

    # Calculate the amount of processors
    num_of_processors = len(f.readline().split()) - 3
    #print 'Number of processors = %d' % num_of_processors

    # Build a computation matrix
    comp_cost = []
    line = f.readline()
    while line.startswith('  '):
        comp_cost.append(map(int, line.split()[-num_of_processors:]))
        line = f.readline()
    #for line in comp_cost:
    #    print line

    # Build a rate matrix
    rate = [[1 for i in range(num_of_processors)] for i in range(num_of_processors)]
    for i in range(num_of_processors):
        rate[i][i] = 0
    #for line in rate:
    #    print line

    return [num_of_tasks, num_of_processors, comp_cost, rate, data]