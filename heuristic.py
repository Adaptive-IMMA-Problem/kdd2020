import tools
import acceptance
import random
import copy

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

def randomm(graph, b, c, k, nodes_acceptance):
    activeUser = set()
    x = {}
    for node in graph.nodes:
        x[node] = 0
    cost = 0
    while cost < k:
        candidate = graph.nodes - activeUser
        subgraph = tools.getSubgraph(graph, candidate)
        needRemove = set()
        for u in candidate:
            if x[u] == b:
                needRemove.add(u)
        candidate = candidate - needRemove
        uStar = randomSelect(candidate)
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

def randomSelect(candiate):
    nodes_list = list(candiate)
    rand = random.randint(0, len(nodes_list) - 1)
    selectedNode = nodes_list[rand]
    return selectedNode

def maxDegree(graph, b, c, k, nodes_acceptance):
    activeUser = set()
    x = {}
    for node in graph.nodes:
        x[node] = 0
    cost = 0
    while cost < k:
        candidate = graph.nodes - activeUser
        subgraph = tools.getSubgraph(graph, candidate)
        needRemove = set()
        for u in candidate:
            if x[u] == b:
                needRemove.add(u)
        candidate = candidate - needRemove
        uStar = maxDegSelect(subgraph, candidate, x, c)
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

def maxDegSelect(graph, candidate, x, c):
    max_node = -10000
    max_degree = -10000
    for node in candidate:
        increment = len(graph.get_children(node)) / c * (1.2 ** x[node])
        if increment > max_degree:
            max_node = node
            max_degree = increment
    return max_node

def maxProb(graph, b, c, k, nodes_acceptance):
    activeUser = set()
    x = {}
    for node in graph.nodes:
        x[node] = 0
    cost = 0
    while cost < k:
        candidate = graph.nodes - activeUser
        subgraph = tools.getSubgraph(graph, candidate)
        needRemove = set()
        for u in candidate:
            if x[u] == b:
                needRemove.add(u)
        candidate = candidate - needRemove
        uStar = maxProbSelect(nodes_acceptance, candidate, x, c)
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

def maxProbSelect(nodes_acceptance, candidate, x, c):
    max_node = -10000
    max_prob = -10000
    for node in candidate:
        increment = nodes_acceptance[node] / c * (1.2 ** x[node])
        if increment > max_prob:
            max_node = node
            max_prob = increment
    return max_node

def maxDegProb(graph, b, c, k, nodes_acceptance):
    activeUser = set()
    x = {}
    for node in graph.nodes:
        x[node] = 0
    cost = 0
    while cost < k:
        candidate = graph.nodes - activeUser
        subgraph = tools.getSubgraph(graph, candidate)
        needRemove = set()
        for u in candidate:
            if x[u] == b:
                needRemove.add(u)
        candidate = candidate - needRemove
        uStar = maxDegProbSelect(subgraph, nodes_acceptance, candidate, x, c)
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

def maxDegProbSelect(graph, nodes_acceptance, candidate, x, c):
    max_node = -10000
    max_degprob = -10000
    for node in candidate:
        increment = nodes_acceptance[node] * len(graph.get_children(node)) / c * (1.2 ** x[node])
        if increment > max_degprob:
            max_node = node
            max_degprob = increment
    return max_node

if __name__ == '__main__':
    path = "soc-Epinions1.txt"
    graph = tools.readGraph_direct(path)

    # nodes_acceptance = acceptance.acceptanceMap05[path]

    pathh = "Epin-accept"
    nodes_acceptance = tools.readAccept(pathh)

    b = 5
    c = 1
    k = 10
    times = 20

    print("k = " + str(k))
    influence = 0
    for i in range(times):
        current = maxProb(graph, b, c, k, nodes_acceptance)
        influence += current
        print("time = " + str(i))
    average = influence / times
    print(average)