import time
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import deque
import heapq

app = Flask(__name__)
CORS(app)

goal_state = "123456780"  # 目标状态
directions = {'U': -3, 'D': 3, 'L': -1, 'R': 1}  # 上下左右移动

# 判断是否有解（逆序数）
def is_solvable(state):
    state = state.replace("0", "")  # 忽略空格
    inversions = sum(
        1 for i in range(len(state)) for j in range(i + 1, len(state)) if state[i] > state[j]
    )
    return inversions % 2 == 0

# 随机生成初始数组
def generate_random_state():
    while True:
        state = list("123456780")
        random.shuffle(state)
        state = ''.join(state)
        if is_solvable(state):  # 保证生成的状态有解
            return state

# 公共求解逻辑（仅用于 BFS）
def solve_bfs(start_state):
    def is_valid_move(index, direction):
        if direction == 'U' and index < 3: return False
        if direction == 'D' and index > 5: return False
        if direction == 'L' and index % 3 == 0: return False
        if direction == 'R' and index % 3 == 2: return False
        return True

    def generate_moves(state):
        zero_index = state.index('0')
        for move, offset in directions.items():
            if is_valid_move(zero_index, move):
                new_state = list(state)
                swap_index = zero_index + offset
                new_state[zero_index], new_state[swap_index] = new_state[swap_index], new_state[zero_index]
                yield ''.join(new_state)

    visited = set()
    queue = deque([(start_state, [])])
    nodes_explored = 0

    start_time = time.time()

    while queue:
        current_state, path = queue.popleft()
        nodes_explored += 1
        if current_state == goal_state:
            elapsed_time = round((time.time() - start_time) * 1000, 3)  # 转换为毫秒，保留三位小数
            return path, elapsed_time, nodes_explored
        if current_state not in visited:
            visited.add(current_state)
            for next_state in generate_moves(current_state):
                queue.append((next_state, path + [next_state]))

    return [], 0, nodes_explored

# DFS 求解逻辑
def solve_dfs(start_state, max_depth=200):
    visited = set()
    stack = [(start_state, [])]
    nodes_explored = 0
    reached_limit = False  # 用于标记是否达到深度限制

    start_time = time.time()

    while stack:
        current_state, path = stack.pop()
        nodes_explored += 1

        if current_state == goal_state:
            elapsed_time = round((time.time() - start_time) * 1000, 3)
            return path, elapsed_time, nodes_explored, reached_limit

        if len(path) > max_depth:  # 深度限制
            reached_limit = True  # 标记达到限制
            continue

        if current_state not in visited:
            visited.add(current_state)
            for next_state in generate_moves(current_state):
                stack.append((next_state, path + [current_state]))

    elapsed_time = round((time.time() - start_time) * 1000, 3)
    return [], elapsed_time, nodes_explored, reached_limit

# A* 求解逻辑
def solve_astar(start_state):
    def heuristic(state):
        # 曼哈顿距离启发式
        distance = 0
        for i, char in enumerate(state):
            if char == '0': continue
            target = goal_state.index(char)
            distance += abs(i // 3 - target // 3) + abs(i % 3 - target % 3)
        return distance

    visited = set()
    priority_queue = []
    heapq.heappush(priority_queue, (heuristic(start_state), 0, start_state, []))
    nodes_explored = 0
    start_time = time.time()

    while priority_queue:
        _, cost, current_state, path = heapq.heappop(priority_queue)
        nodes_explored += 1

        if current_state == goal_state:
            elapsed_time = round((time.time() - start_time) * 1000, 3)  # 转换为毫秒，保留三位小数
            return path + [goal_state], elapsed_time, nodes_explored

        if current_state not in visited:
            visited.add(current_state)
            for next_state in generate_moves(current_state):
                if next_state not in visited:
                    heapq.heappush(priority_queue, (
                        cost + 1 + heuristic(next_state),  # 总代价：g(n) + h(n)
                        cost + 1,  # g(n)：路径长度
                        next_state,
                        path + [current_state]
                    ))

    return [], 0, nodes_explored  # 无解

# 双向BFS求解逻辑
def solve_bibfs(start_state):
    def generate_moves(state):
        zero_index = state.index('0')
        for move, offset in directions.items():
            if move == 'U' and zero_index < 3: continue
            if move == 'D' and zero_index > 5: continue
            if move == 'L' and zero_index % 3 == 0: continue
            if move == 'R' and zero_index % 3 == 2: continue

            new_state = list(state)
            swap_index = zero_index + offset
            new_state[zero_index], new_state[swap_index] = new_state[swap_index], new_state[zero_index]
            yield ''.join(new_state)

    if start_state == goal_state:
        return [goal_state], 0, 0

    start_time = time.time()

    # 初始化
    forward_queue = deque([(start_state, [])])  # 从起点开始的队列
    backward_queue = deque([(goal_state, [])])  # 从目标开始的队列
    forward_visited = {start_state: []}
    backward_visited = {goal_state: []}

    nodes_explored = 0

    while forward_queue and backward_queue:
        # 从前向扩展
        current_forward, forward_path = forward_queue.popleft()
        nodes_explored += 1

        for next_state in generate_moves(current_forward):
            if next_state in forward_visited:
                continue
            forward_visited[next_state] = forward_path + [current_forward]
            forward_queue.append((next_state, forward_path + [current_forward]))

            # 如果在后向访问中找到，则路径完成
            if next_state in backward_visited:
                backward_path = backward_visited[next_state]
                elapsed_time = round((time.time() - start_time) * 1000, 3)

                # 确保最后一步从相遇点到目标状态
                if next_state != goal_state:
                    full_path = forward_path + [next_state] + backward_path[::-1]
                    full_path.append(goal_state)  # 补充最后一步
                else:
                    full_path = forward_path + [next_state] + backward_path[::-1]

                return full_path, elapsed_time, nodes_explored

        # 从后向扩展
        current_backward, backward_path = backward_queue.popleft()
        nodes_explored += 1

        for next_state in generate_moves(current_backward):
            if next_state in backward_visited:
                continue
            backward_visited[next_state] = backward_path + [current_backward]
            backward_queue.append((next_state, backward_path + [current_backward]))

            # 如果在前向访问中找到，则路径完成
            if next_state in forward_visited:
                forward_path = forward_visited[next_state]
                elapsed_time = round((time.time() - start_time) * 1000, 3)

                # 确保最后一步从相遇点到目标状态
                if next_state != goal_state:
                    full_path = forward_path + [next_state] + backward_path[::-1]
                    full_path.append(goal_state)  # 补充最后一步
                else:
                    full_path = forward_path + [next_state] + backward_path[::-1]

                return full_path, elapsed_time, nodes_explored

    return [], 0, nodes_explored  # 无解

# IDA*求解逻辑
def solve_idastar(start_state):
    def heuristic(state):
        distance = 0
        for i, char in enumerate(state):
            if char == '0': continue
            target = goal_state.index(char)
            distance += abs(i // 3 - target // 3) + abs(i % 3 - target % 3)
        return distance

    def search(path, g, bound):
        current_state = path[-1]
        f = g + heuristic(current_state)
        if f > bound:
            return f
        if current_state == goal_state:
            return True
        min_bound = float('inf')
        zero_index = current_state.index('0')
        for move, offset in directions.items():
            swap_index = zero_index + offset
            if swap_index < 0 or swap_index >= len(current_state):
                continue
            new_state = list(current_state)
            new_state[zero_index], new_state[swap_index] = new_state[swap_index], new_state[zero_index]
            new_state = ''.join(new_state)
            if new_state not in path:
                path.append(new_state)
                result = search(path, g + 1, bound)
                if result is True:
                    return True
                if result < min_bound:
                    min_bound = result
                path.pop()
        return min_bound

    start_time = time.time()
    bound = heuristic(start_state)
    path = [start_state]
    nodes_explored = 0

    while True:
        result = search(path, 0, bound)
        nodes_explored += 1
        if result is True:
            elapsed_time = round((time.time() - start_time) * 1000, 3)
            return path, elapsed_time, nodes_explored
        if result == float('inf'):
            return [], 0, nodes_explored
        bound = result

# 通用函数，用于生成移动
def generate_moves(state):
    zero_index = state.index('0')
    for move, offset in directions.items():
        if move == 'U' and zero_index < 3: continue
        if move == 'D' and zero_index > 5: continue
        if move == 'L' and zero_index % 3 == 0: continue
        if move == 'R' and zero_index % 3 == 2: continue

        new_state = list(state)
        swap_index = zero_index + offset
        new_state[zero_index], new_state[swap_index] = new_state[swap_index], new_state[zero_index]
        yield ''.join(new_state)

# BFS 接口
@app.route('/solve_bfs', methods=['POST'])
def solve_bfs_interface():
    start_state = request.json.get('start', generate_random_state())
    if not is_solvable(start_state):
        return jsonify({"error": "该状态无解！"}), 400
    path, elapsed_time, nodes_explored = solve_bfs(start_state)
    return jsonify({
        "moves": path,
        "time": elapsed_time,
        "path_length": len(path),
        "nodes_explored": nodes_explored
    })

# DFS 接口
@app.route('/solve_dfs', methods=['POST'])
def solve_dfs_interface():
    start_state = request.json.get('start', generate_random_state())
    max_depth = request.json.get('max_depth', 200)  # 动态指定最大深度
    if not is_solvable(start_state):
        return jsonify({"error": "该状态无解！"}), 400

    path, elapsed_time, nodes_explored, reached_limit = solve_dfs(start_state, max_depth)

    response = {
        "moves": path,
        "time": elapsed_time,
        "path_length": len(path),
        "nodes_explored": nodes_explored,
    }
    if reached_limit:
        response["warning"] = f"达到最大深度限制({max_depth})，可能无法移动到最终结果。"

    return jsonify(response)

# A* 接口
@app.route('/solve_astar', methods=['POST'])
def solve_astar_interface():
    start_state = request.json.get('start')
    if not start_state or not is_solvable(start_state):
        return jsonify({"error": "无效状态或该状态无解！"}), 400
    path, elapsed_time, nodes_explored = solve_astar(start_state)
    if not path:  # 如果无解，返回错误
        return jsonify({"error": "该状态无解！"}), 400
    return jsonify({
        "moves": path,
        "time": elapsed_time,
        "path_length": len(path),
        "nodes_explored": nodes_explored
    })

# IDA*接口
@app.route('/solve_idastar', methods=['POST'])
def solve_idastar_interface():
    start_state = request.json.get('start', generate_random_state())
    if not is_solvable(start_state):
        return jsonify({"error": "该状态无解！"}), 400
    path, elapsed_time, nodes_explored = solve_idastar(start_state)
    return jsonify({
        "moves": path,
        "time": elapsed_time,
        "path_length": len(path),
        "nodes_explored": nodes_explored
    })


# 双向BFS接口
@app.route('/solve_bibfs', methods=['POST'])
def solve_bibfs_interface():
    start_state = request.json.get('start', generate_random_state())
    if not is_solvable(start_state):
        return jsonify({"error": "该状态无解！"}), 400
    path, elapsed_time, nodes_explored = solve_bibfs(start_state)
    return jsonify({
        "moves": path,
        "time": elapsed_time,
        "path_length": len(path),
        "nodes_explored": nodes_explored
    })


if __name__ == '__main__':
    app.run(debug=True)
