import tools
import acceptance
import random
import copy
import time
import math
import multiprocessing

def adaptgreedy(graph, b, c, k, nodes_acceptance, epsilon, delta):
    activeUser = set()
    x = {}
    for node in graph.nodes:
        x[node] = 0
    cost = 0
    flag = True
    while cost < k:
        candidate = graph.nodes - activeUser
        subgraph = tools.getSubgraph(graph, candidate)
        needRemove = set()
        for u in candidate:
            if x[u] == b:
                needRemove.add(u)
        candidate = candidate - needRemove
        r = min(k, len(subgraph.nodes))
        l = math.log(r / delta, len(subgraph.nodes))
        if flag:
            R = Sampling(subgraph, x, c, nodes_acceptance, candidate, epsilon, l)
        print(len(R))
        uStar, Cover_uStar = maxCoverage(R, x, c, candidate, nodes_acceptance)
        uCost = c * (1.2 ** x[uStar])
        if cost + uCost > k:
            rand = random.random()
            if rand < (1 - (k - cost) / uCost):
                break
        x[uStar] += 1
        cost += uCost
        rand = random.random()
        if rand < nodes_acceptance[uStar]:
            flag = True
            update(subgraph, uStar, activeUser)
        else:
            flag = False
    return len(activeUser)

def Sampling(graph, x, c, nodes_acceptance, candidate, epsilon, l):
    epsilonPrime = math.sqrt(2) * epsilon
    LB = 1
    n = len(graph.nodes)
    lambdaPrime = (2 + 2 / 3 * epsilonPrime) * ((l + 1) * math.log(n) + math.log(math.log2(n))) * n / (epsilonPrime ** 2)
    alpha = math.sqrt(l * math.log(n) + math.log(2))
    beta = math.sqrt((1 - 1 / math.e) * ((l + 1) * math.log(n) + math.log(2)))
    lambdaStar = 2 * n * (((1 - 1 / math.e) * alpha + beta) ** 2) / (epsilonPrime ** 2)
    R = []
    for i in range(1, math.ceil(math.log2(n))):
        omega = n / (2 ** i)
        theta = lambdaPrime / omega
        if len(R) <= theta:
            add_R = generate(graph, theta - len(R))
            R.extend(add_R)
        uStar, Cover_uStar = maxCoverage(R, x, c, candidate, nodes_acceptance)
        h = n * Cover_uStar
        if h >= (1 + epsilonPrime) * omega:
            LB = h / (1 + epsilonPrime)
            break
    theta = lambdaStar / LB
    if len(R) <= theta:
        add_R = generate(graph, theta - len(R))
        R.extend(add_R)
    return R

def calcAverage(graph, b, c, k, nodes_acceptance, epsilon, delta, times=10):
    influence = 0
    for i in range(times):
        current = adaptgreedy(graph, b, c, k, nodes_acceptance, epsilon, delta)
        print("inf = " + str(current))
        influence += current
        print("time = " + str(i))
    average = influence / times
    return average

def generateRRset(graph):
    nodes_list = list(graph.nodes)
    rand = random.randint(0, len(nodes_list) - 1)
    selectedNode = nodes_list[rand]
    RRset = reverseSearch(graph, selectedNode)
    return RRset

def generate(graph, theta):
    n = multiprocessing.cpu_count()
    pool = multiprocessing.Pool()
    results = []
    for i in range(n):
        result = pool.apply_async(generateThread, args=(graph, theta / n))
        results.append(result)
    pool.close()
    pool.join()
    R = []
    for result in results:
        R.extend(result.get())
    return R

def generateThread(graph, theta):
    R = []
    th = int(theta)
    for i in range(th):
        current_R = generateRRset(graph)
        R.append(current_R)
    return R

def maxCoverage(R, x, c, candidate, nodes_acceptance):
    n = multiprocessing.cpu_count()
    max_node = -10000
    max_cover = -10000
    pool = multiprocessing.Pool()
    candidate = list(candidate)
    nodes_cpu_list = tools.chunkIt(candidate, n)
    results = []
    for node_section in nodes_cpu_list:
        result = pool.apply_async(maxCoverageThread, args=(R, x, c, node_section, nodes_acceptance))
        results.append(result)
    pool.close()
    pool.join()
    for result in results:
        if result.get()[1] > max_cover:
            max_node = result.get()[0]
            max_cover = result.get()[1]
    return max_node, max_cover

def maxCoverageThread(R, x, c, candidate, nodes_acceptance):
    max_node = -10000
    max_cover = -10000
    for node in candidate:
        node_cover = cover(R, node)
        hh = nodes_acceptance[node] * node_cover / (c * (1.2 ** x[node]))
        if hh > max_cover:
            max_node = node
            max_cover = hh
    result = []
    result.append(max_node)
    result.append(max_cover)
    return result

def cover(R, node):
    sum = 0
    for RRset in R:
        if node in RRset:
            sum += 1
    return sum/len(R)

def reverseSearch(graph, root):
    searchSet = set()
    queue = []
    queue.append(root)
    searchSet.add(root)
    while len(queue) != 0:
        current_node = queue.pop(0)
        parentss = graph.get_parentss(current_node)
        for parent in parentss:
            if parent not in searchSet:
                rate = graph.edges[(parent, current_node)]
                if tools.isHappened(rate):
                    searchSet.add(parent)
                    queue.append(parent)
    return searchSet

def findMax(user_gain):
    uStar = -10000
    max_gain = -10000
    for node in user_gain:
        if user_gain[node] > max_gain:
            uStar = node
            max_gain = user_gain[node]
    return uStar

def update(graph, uStar, activeUser):
    seeds = set()
    seeds.add(uStar)
    queue = []
    queue.extend(seeds)
    checked = copy.deepcopy(seeds)
    while len(queue) != 0:
        current_node = queue.pop(0)
        children = graph.get_children(current_node)
        for child in children:
            if child not in checked:
                rate = graph.edges[(current_node, child)]
                if tools.isHappened(rate):
                    checked.add(child)
                    queue.append(child)
    for node in checked:
        activeUser.add(node)
    return None

if __name__ == '__main__':
    path = "soc-Epinions1.txt"
    graph = tools.readGraph_direct(path)

    # nodes_acceptance = acceptance.acceptanceMap05[path]

    pathh = "Epin-accept"
    nodes_acceptance = tools.readAccept(pathh)

    b = 5
    c = 1
    epsilon = 0.5
    delta = 0.5

    k = 10
    print("k = " + str(k))
    time_start = time.time()
    influence = adaptgreedy(graph, b, c, k, nodes_acceptance, epsilon, delta)
    time_end = time.time()
    print(influence)
    print('totally cost', time_end - time_start)