import tools
import acceptance
import random
import copy
import time

def adaptgreedy(graph, b, c, k, nodes_acceptance):
    activeUser = set()
    x = {}
    for node in graph.nodes:
        x[node] = 0
    cost = 0
    while cost < k:
        user_gain = {}
        candidate = graph.nodes - activeUser
        subgraph = tools.getSubgraph(graph, candidate)
        needRemove = set()
        for u in candidate:
            if x[u] == b:
                needRemove.add(u)
        candidate = candidate - needRemove
        for u in candidate:
            user_gain[u] = nodes_acceptance[u] * compute(subgraph, u) / (c * (1.2 ** x[u]))
        uStar = findMax(user_gain)
        uCost = c * (1.2 ** x[uStar])
        if cost + uCost > k:
            rand = random.random()
            if rand < (1 - (k - cost) / uCost):
                break
        x[uStar] += 1
        cost += uCost
        rand = random.random()
        if rand < nodes_acceptance[uStar]:
            update(subgraph, uStar, activeUser)
    return len(activeUser)

def findMax(user_gain):
    uStar = -10000
    max_gain = -10000
    for node in user_gain:
        if user_gain[node] > max_gain:
            uStar = node
            max_gain = user_gain[node]
    return uStar

def compute(graph, u, R=600):
    influence = 0
    seeds = set()
    seeds.add(u)
    for i in range(R):
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
        influence += len(checked)
    influence = influence / R
    return influence

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

def calcAverage(graph, b, c, k, nodes_acceptance, times=20):
    influence = 0
    for i in range(times):
        current = adaptgreedy(graph, b, c, k, nodes_acceptance)
        influence += current
        print("time = " + str(i))
    average = influence / times
    return average

def nonadaptgreedy(graph, b, c, k, nodes_acceptance):
    x = {}
    for node in graph.nodes:
        x[node] = 0
    cost = 0
    currentInfluence = 0
    while cost < k:
        user_gain = {}
        candidate = copy.deepcopy(graph.nodes)
        needRemove = set()
        for u in candidate:
            if x[u] == b:
                needRemove.add(u)
        candidate = candidate - needRemove
        for u in candidate:
            xx = copy.deepcopy(x)
            xx[u] += 1
            user_gain[u] = (noncompute(graph, xx, nodes_acceptance) - currentInfluence) / (c * (1.2 ** x[u]))
        uStar = findMax(user_gain)
        uCost = c * (1.2 ** x[uStar])
        if cost + uCost > k:
            rand = random.random()
            if rand < (1 - (k - cost) / uCost):
                break
        x[uStar] += 1
        cost += uCost
        print("cost = " + str(cost))
        currentInfluence += user_gain[uStar]
    return x

def noncompute(graph, xx, nodes_acceptance, R=600):
    influence = 0
    seedAccptance = {}
    for node in xx:
        if xx[node] > 0:
            seedAccptance[node] = 1 - ((1 - nodes_acceptance[node]) ** xx[node])
    for i in range(R):
        actualSeeds = set()
        for node in seedAccptance:
            rand = random.random()
            if rand < seedAccptance[node]:
                actualSeeds.add(node)
        queue = []
        queue.extend(actualSeeds)
        checked = copy.deepcopy(actualSeeds)
        while len(queue) != 0:
            current_node = queue.pop(0)
            children = graph.get_children(current_node)
            for child in children:
                if child not in checked:
                    rate = graph.edges[(current_node, child)]
                    if tools.isHappened(rate):
                        checked.add(child)
                        queue.append(child)
        influence += len(checked)
    influence = influence / R
    return influence

if __name__ == '__main__':
    path = "ca-netscience.txt"
    graph = tools.readGraph_Undirect(path)

    nodes_acceptance = acceptance.acceptanceMap06[path]

    b = 5
    c = 1
    k = 50

    print("k = " + str(k))

    # time_start = time.time()
    # influence = calcAverage(graph, b, c, k, nodes_acceptance)
    # print(influence)
    # time_end = time.time()
    # print('totally cost', time_end - time_start)

    time_start = time.time()
    x = nonadaptgreedy(graph, b, c, k, nodes_acceptance)
    time_end = time.time()
    influence = noncompute(graph, x, nodes_acceptance, 1000)
    print(influence)
    print('totally cost', time_end - time_start)
