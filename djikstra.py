function dijkstra(graph, start_zone, end_zone):
    # Returns shortest cost path as list of zones
    
    dist: dict[Zone, int] = { all zones: infinity }
    prev: dict[Zone, Zone | None] = { all zones: None }
    dist[start_zone] = 0
    
    priority_queue = MinHeap()
    priority_queue.push((cost=0, zone=start_zone))
    
    while priority_queue is not empty:
        current_cost, current_zone = priority_queue.pop_min()
        
        if current_cost > dist[current_zone]:
            continue  # stale entry, skip
        
        if current_zone == end_zone:
            break  # found shortest path
        
        for each (neighbor, connection) in graph.adjacency[current_zone]:
            if neighbor.zone_type == blocked:
                continue
            
            # cost is based on destination zone type
            if neighbor.zone_type == restricted:
                move_cost = 2
            elif neighbor.zone_type == priority:
                move_cost = 0.9  # slight preference for tie-breaking
            else:
                move_cost = 1
            
            new_cost = current_cost + move_cost
            
            if new_cost < dist[neighbor]:
                dist[neighbor] = new_cost
                prev[neighbor] = current_zone
                priority_queue.push((new_cost, neighbor))
    
    # Reconstruct path by backtracking through prev
    path = []
    current = end_zone
    while current is not None:
        path.prepend(current)
        current = prev[current]
    
    if path[0] != start_zone:
        return None  # no path found
    
    return path


function find_k_paths(graph, start, end, k):
    # Yen's k-shortest paths (no library, implement manually)
    # Gives you k candidate routes to distribute drones across
    
    paths = []
    candidates = MinHeap()
    
    first_path = dijkstra(graph, start, end)
    if first_path is None:
        raise Error("No path exists from start to end")
    paths.append(first_path)
    
    for i in range(1, k):
        previous_path = paths[i - 1]
        
        for spur_index in range(len(previous_path) - 1):
            spur_node = previous_path[spur_index]
            root_path = previous_path[0 : spur_index]
            
            # Temporarily remove edges used by previous paths
            # that share the same root_path
            edges_to_remove = []
            for path in paths:
                if path[0:spur_index] == root_path:
                    edge = (path[spur_index], path[spur_index + 1])
                    edges_to_remove.append(edge)
                    graph.remove_edge_temporarily(edge)
            
            spur_path = dijkstra(graph, spur_node, end)
            
            if spur_path is not None:
                full_path = root_path + spur_path
                if full_path not in candidates:
                    candidates.push(full_path)
            
            graph.restore_removed_edges(edges_to_remove)
        
        if candidates is empty:
            break
        
        paths.append(candidates.pop_min())
    
    return paths