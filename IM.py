import tools
import copy
import multiprocessing

def compute(graph, seeds, R=100):
    influence = 0
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
    influence = influence/R
    return influence

def greedy(graph, k):
    seeds = set()
    n = multiprocessing.cpu_count()
    for i in range(k):
        pool = multiprocessing.Pool()
        results = []
        candidate = graph.nodes - seeds
        candidate = list(candidate)
        nodes_cpu_list = tools.chunkIt(candidate, n)
        for node_section in nodes_cpu_list:
            result = pool.apply_async(greedy_thread, args=(graph, node_section, seeds))
            results.append(result)
        pool.close()
        pool.join()
        current_seed = 0
        current_result = 0
        for result in results:
            if result.get()[1] > current_result:
                current_seed = result.get()[0]
                current_result = result.get()[1]
        seeds.add(current_seed)
        print("i = " + str(i) + ", " + str(current_result))
    return seeds

def greedy_thread(graph, node_section, seeds):
    max_seed = 0
    max_seed_result = 0
    for node in node_section:
        current_seeds = copy.deepcopy(seeds)
        current_seeds.add(node)
        current_seeds_result = compute(graph, current_seeds)
        if current_seeds_result > max_seed_result:
            max_seed = node
            max_seed_result = current_seeds_result
    result = []
    result.append(max_seed)
    result.append(max_seed_result)
    return result

if __name__ == '__main__':
    path = "ca-netscience.txt"

    k = 10
    graph = tools.readGraph_1(path)
    seeds = greedy(graph, k)
    graph = tools.readGraph_2(path)
    seeds = greedy(graph, k)