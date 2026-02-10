# Python数据结构与算法：高效代码的基石

## 引言

在Python系统VIP A1课程的第五部分，我们将深入学习Python数据结构与算法。数据结构是组织和存储数据的方式，而算法是解决问题的步骤。掌握这些知识不仅能帮助你编写更高效的代码，还能提升你的编程思维和解决问题的能力。本文将详细介绍Python数据结构与算法模块的学习内容，帮助你成为一名更优秀的Python开发者。

## 算法复杂度分析

### 时间复杂度

时间复杂度是衡量算法执行时间随输入规模增长的速率：

```python
# O(1) - 常数时间复杂度
def get_first_element(arr):
    return arr[0] if arr else None

# O(n) - 线性时间复杂度
def find_element(arr, target):
    for element in arr:
        if element == target:
            return True
    return False

# O(log n) - 对数时间复杂度
def binary_search(sorted_arr, target):
    left, right = 0, len(sorted_arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if sorted_arr[mid] == target:
            return mid
        elif sorted_arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# O(n²) - 平方时间复杂度
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
```

常见的时间复杂度从优到劣排序：O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)

### 空间复杂度

空间复杂度衡量算法执行过程中所需额外空间随输入规模增长的速率：

```python
# O(1) - 常数空间复杂度
def sum_array(arr):
    total = 0
    for num in arr:
        total += num
    return total

# O(n) - 线性空间复杂度
def duplicate_array(arr):
    return arr.copy()  # 创建一个新数组，需要O(n)空间

# O(n²) - 平方空间复杂度
def create_matrix(n):
    return [[0 for _ in range(n)] for _ in range(n)]
```

## Python内置数据结构

### 列表（List）

列表是Python中最常用的数据结构，它是可变的、有序的元素集合：

```python
# 列表创建和基本操作
numbers = [1, 2, 3, 4, 5]
print(numbers[0])       # 1 (访问元素)
numbers.append(6)       # 添加元素
numbers.insert(0, 0)    # 在指定位置插入元素
numbers.remove(3)       # 删除指定元素
popped = numbers.pop()  # 弹出最后一个元素
print(len(numbers))     # 获取列表长度

# 列表切片
sublist = numbers[1:4]  # 获取索引1到3的元素

# 列表推导式
squares = [x**2 for x in range(10)]
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# 常见列表方法的时间复杂度
# append(): O(1)
# insert(): O(n)
# pop(): O(1) 从末尾弹出，O(n) 从中间弹出
# index(): O(n)
# in 操作: O(n)
# 切片: O(k) 其中k是切片长度
```

### 元组（Tuple）

元组是不可变的、有序的元素集合：

```python
# 元组创建和基本操作
point = (10, 20)
x, y = point  # 元组解包
print(point[0])  # 10 (访问元素)
print(len(point))  # 2 (获取元组长度)

# 元组的不可变性
try:
    point[0] = 15  # 这会引发TypeError
except TypeError as e:
    print(e)  # 'tuple' object does not support item assignment

# 元组作为字典键
locations = {
    (40.7128, -74.0060): "New York",
    (34.0522, -118.2437): "Los Angeles"
}
```

### 字典（Dictionary）

字典是键值对的集合，提供高效的查找、插入和删除操作：

```python
# 字典创建和基本操作
person = {"name": "张三", "age": 30, "city": "北京"}
print(person["name"])  # 张三 (访问值)
person["email"] = "zhangsan@example.com"  # 添加新键值对
person["age"] = 31  # 更新值
del person["city"]  # 删除键值对

# 字典方法
keys = person.keys()  # 获取所有键
values = person.values()  # 获取所有值
items = person.items()  # 获取所有键值对

# 字典推导式
square_dict = {x: x**2 for x in range(5)}

# 使用get方法安全访问
email = person.get("email", "未设置")  # 如果键不存在，返回默认值

# 字典的时间复杂度
# 查找、插入、删除: 平均O(1)，最坏O(n)
```

### 集合（Set）

集合是无序的、不重复元素的集合，支持数学集合操作：

```python
# 集合创建和基本操作
fruits = {"苹果", "香蕉", "橙子"}
fruits.add("草莓")  # 添加元素
fruits.remove("香蕉")  # 删除元素

# 集合操作
set1 = {1, 2, 3, 4, 5}
set2 = {4, 5, 6, 7, 8}
union_set = set1 | set2  # 并集: {1, 2, 3, 4, 5, 6, 7, 8}
intersection_set = set1 & set2  # 交集: {4, 5}
difference_set = set1 - set2  # 差集: {1, 2, 3}
symmetric_difference = set1 ^ set2  # 对称差集: {1, 2, 3, 6, 7, 8}

# 集合推导式
even_set = {x for x in range(10) if x % 2 == 0}

# 集合的时间复杂度
# 添加、删除、检查元素存在性: 平均O(1)，最坏O(n)
```

## 自定义数据结构

### 链表（Linked List）

链表是由节点组成的线性集合，每个节点包含数据和指向下一个节点的引用：

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    
    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
    
    def delete(self, data):
        if not self.head:
            return
        
        if self.head.data == data:
            self.head = self.head.next
            return
        
        current = self.head
        while current.next and current.next.data != data:
            current = current.next
        
        if current.next:
            current.next = current.next.next
    
    def display(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        return elements

# 使用链表
ll = LinkedList()
ll.append(1)
ll.append(2)
ll.append(3)
ll.prepend(0)
print(ll.display())  # [0, 1, 2, 3]
ll.delete(2)
print(ll.display())  # [0, 1, 3]
```

### 栈（Stack）

栈是一种后进先出（LIFO）的数据结构：

```python
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None
    
    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return None
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# 使用栈
stack = Stack()
stack.push(1)
stack.push(2)
stack.push(3)
print(stack.peek())  # 3
print(stack.pop())   # 3
print(stack.size())  # 2

# 栈的应用：括号匹配
def is_balanced(expression):
    stack = Stack()
    brackets = {')': '(', '}': '{', ']': '['}
    
    for char in expression:
        if char in '({[':
            stack.push(char)
        elif char in ')}]':
            if stack.is_empty() or stack.pop() != brackets[char]:
                return False
    
    return stack.is_empty()

print(is_balanced("({[]})"))  # True
print(is_balanced("({[})"))   # False
```

### 队列（Queue）

队列是一种先进先出（FIFO）的数据结构：

```python
from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        if not self.is_empty():
            return self.items.popleft()
        return None
    
    def peek(self):
        if not self.is_empty():
            return self.items[0]
        return None
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)

# 使用队列
queue = Queue()
queue.enqueue(1)
queue.enqueue(2)
queue.enqueue(3)
print(queue.peek())    # 1
print(queue.dequeue()) # 1
print(queue.size())    # 2

# 队列的应用：广度优先搜索
def bfs(graph, start):
    visited = set()
    queue = Queue()
    queue.enqueue(start)
    visited.add(start)
    
    while not queue.is_empty():
        vertex = queue.dequeue()
        print(vertex, end=" ")
        
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.enqueue(neighbor)

# 示例图（邻接表表示）
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}

print("BFS遍历:")
bfs(graph, 'A')  # A B C D E F
```

### 树（Tree）

树是一种分层数据结构，由节点组成，每个节点可以有多个子节点：

```python
class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

# 二叉搜索树
class BinarySearchTree:
    def __init__(self):
        self.root = None
    
    def insert(self, data):
        if not self.root:
            self.root = TreeNode(data)
        else:
            self._insert_recursive(self.root, data)
    
    def _insert_recursive(self, node, data):
        if data < node.data:
            if node.left is None:
                node.left = TreeNode(data)
            else:
                self._insert_recursive(node.left, data)
        else:
            if node.right is None:
                node.right = TreeNode(data)
            else:
                self._insert_recursive(node.right, data)
    
    def search(self, data):
        return self._search_recursive(self.root, data)
    
    def _search_recursive(self, node, data):
        if node is None or node.data == data:
            return node
        
        if data < node.data:
            return self._search_recursive(node.left, data)
        return self._search_recursive(node.right, data)
    
    def inorder_traversal(self):
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node, result):
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node.data)
            self._inorder_recursive(node.right, result)

# 使用二叉搜索树
bst = BinarySearchTree()
bst.insert(50)
bst.insert(30)
bst.insert(70)
bst.insert(20)
bst.insert(40)
bst.insert(60)
bst.insert(80)

print("中序遍历:", bst.inorder_traversal())  # [20, 30, 40, 50, 60, 70, 80]
print("搜索30:", bst.search(30) is not None)  # True
print("搜索100:", bst.search(100) is not None)  # False
```

### 堆（Heap）

堆是一种特殊的完全二叉树，分为最大堆和最小堆：

```python
import heapq

# Python的heapq模块实现的是最小堆

# 创建堆
heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 3)
heapq.heappush(heap, 7)
heapq.heappush(heap, 1)

print("堆:", heap)  # [1, 3, 7, 5]

# 弹出最小元素
print("弹出:", heapq.heappop(heap))  # 1
print("堆:", heap)  # [3, 5, 7]

# 查看最小元素但不移除
print("堆顶:", heap[0])  # 3

# 将列表转换为堆
numbers = [5, 8, 2, 1, 7]
heapq.heapify(numbers)
print("堆化后:", numbers)  # [1, 5, 2, 8, 7]

# 实现最大堆（通过取负值）
max_heap = []
heapq.heappush(max_heap, -5)
heapq.heappush(max_heap, -3)
heapq.heappush(max_heap, -7)
heapq.heappush(max_heap, -1)

# 弹出最大元素（取负后的最小元素）
print("最大元素:", -heapq.heappop(max_heap))  # 7
```

### 图（Graph）

图是由顶点和边组成的数据结构，可以表示复杂的关系：

```python
class Graph:
    def __init__(self):
        self.adjacency_list = {}
    
    def add_vertex(self, vertex):
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []
    
    def add_edge(self, vertex1, vertex2):
        if vertex1 in self.adjacency_list and vertex2 in self.adjacency_list:
            self.adjacency_list[vertex1].append(vertex2)
            self.adjacency_list[vertex2].append(vertex1)  # 无向图
    
    def remove_edge(self, vertex1, vertex2):
        if vertex1 in self.adjacency_list and vertex2 in self.adjacency_list:
            self.adjacency_list[vertex1] = [v for v in self.adjacency_list[vertex1] if v != vertex2]
            self.adjacency_list[vertex2] = [v for v in self.adjacency_list[vertex2] if v != vertex1]
    
    def remove_vertex(self, vertex):
        if vertex in self.adjacency_list:
            for other_vertex in self.adjacency_list:
                self.adjacency_list[other_vertex] = [v for v in self.adjacency_list[other_vertex] if v != vertex]
            del self.adjacency_list[vertex]
    
    def dfs(self, start):
        result = []
        visited = set()
        
        def dfs_recursive(vertex):
            if vertex not in self.adjacency_list:
                return
            
            visited.add(vertex)
            result.append(vertex)
            
            for neighbor in self.adjacency_list[vertex]:
                if neighbor not in visited:
                    dfs_recursive(neighbor)
        
        dfs_recursive(start)
        return result
    
    def bfs(self, start):
        if start not in self.adjacency_list:
            return []
        
        result = []
        visited = set([start])
        queue = [start]
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in self.adjacency_list[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return result

# 使用图
graph = Graph()
graph.add_vertex("A")
graph.add_vertex("B")
graph.add_vertex("C")
graph.add_vertex("D")
graph.add_vertex("E")
graph.add_vertex("F")

graph.add_edge("A", "B")
graph.add_edge("A", "C")
graph.add_edge("B", "D")
graph.add_edge("C", "E")
graph.add_edge("D", "E")
graph.add_edge("D", "F")
graph.add_edge("E", "F")

print("DFS遍历:", graph.dfs("A"))  # ['A', 'B', 'D', 'E', 'C', 'F']
print("BFS遍历:", graph.bfs("A"))  # ['A', 'B', 'C', 'D', 'E', 'F']
```

## 常见算法

### 排序算法

```python
# 冒泡排序 - O(n²)
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        # 优化：如果一轮中没有交换，说明已经排序完成
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr

# 选择排序 - O(n²)
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

# 插入排序 - O(n²)
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

# 归并排序 - O(n log n)
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# 快速排序 - 平均O(n log n)，最坏O(n²)
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)

# 堆排序 - O(n log n)
def heap_sort(arr):
    n = len(arr)
    
    # 构建最大堆
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    
    # 一个个提取元素
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]  # 交换
        heapify(arr, i, 0)
    
    return arr

def heapify(arr, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2
    
    if left < n and arr[left] > arr[largest]:
        largest = left
    
    if right < n and arr[right] > arr[largest]:
        largest = right
    
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

# 测试排序算法
arr = [64, 34, 25, 12, 22, 11, 90]
print("冒泡排序:", bubble_sort(arr.copy()))
print("选择排序:", selection_sort(arr.copy()))
print("插入排序:", insertion_sort(arr.copy()))
print("归并排序:", merge_sort(arr.copy()))
print("快速排序:", quick_sort(arr.copy()))
print("堆排序:", heap_sort(arr.copy()))
```

### 查找算法

```python
# 线性查找 - O(n)
def linear_search(arr, target):
    for i, item in enumerate(arr):
        if item == target:
            return i
    return -1

# 二分查找（要求有序数组）- O(log n)
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# 递归二分查找
def binary_search_recursive(arr, target, left=None, right=None):
    if left is None and right is None:
        left, right = 0, len(arr) - 1
    
    if left > right:
        return -1
    
    mid = (left + right) // 2
    
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)

# 测试查找算法
arr = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
print("线性查找9:", linear_search(arr, 9))  # 4
print("二分查找9:", binary_search(arr, 9))  # 4
print("递归二分查找9:", binary_search_recursive(arr, 9))  # 4
print("二分查找10:", binary_search(arr, 10))  # -1
```

### 动态规划

动态规划是解决具有重叠子问题和最优子结构的问题的方法：

```python
# 斐波那契数列 - 递归解法（低效）
def fibonacci_recursive(n):
    if n <= 1:
        return n
    return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)

# 斐波那契数列 - 动态规划（自底向上）
def fibonacci_dp(n):
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]

# 斐波那契数列 - 备忘录（自顶向下）
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]

# 最长递增子序列
def longest_increasing_subsequence(arr):
    if not arr:
        return 0
    
    n = len(arr)
    dp = [1] * n
    
    for i in range(1, n):
        for j in range(0, i):
            if arr[i] > arr[j]:
                dp[i] = max(dp[i], dp[j] + 1)
    
    return max(dp)

# 0-1背包问题
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i-1] <= w:  # 当前物品可以放入背包
                # 选择放入或不放入当前物品，取最大值
                dp[i][w] = max(values[i-1] + dp[i-1][w-weights[i-1]], dp[i-1][w])
            else:  # 当前物品不能放入背包
                dp[i][w] = dp[i-1][w]
    
    return dp[n][capacity]

# 测试动态规划算法
print("斐波那契数(10)递归:", fibonacci_recursive(10))
print("斐波那契数(10)动态规划:", fibonacci_dp(10))
print("斐波那契数(10)备忘录:", fibonacci_memo(10))

arr = [10, 9, 2, 5, 3, 7, 101, 18]
print("最长递增子序列长度:", longest_increasing_subsequence(arr))  # 4 ([2, 3, 7, 101] 或 [2, 5, 7, 101])

weights = [2, 3, 4, 5]
values = [3, 4, 5, 6]
capacity = 8
print("0-1背包最大价值:", knapsack(weights, values, capacity))  # 10

# 编辑距离问题
def edit_distance(word1, word2):
    m, n = len(word1), len(word2)
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
    
    # 边界条件初始化
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # 填充dp表
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j],      # 删除
                                   dp[i][j-1],      # 插入
                                   dp[i-1][j-1])    # 替换
    
    return dp[m][n]

print("编辑距离:", edit_distance("horse", "ros"))  # 3

### 贪心算法

贪心算法在每一步选择中都采取当前状态下最好的选择，从而希望导致结果是全局最优的：

```python
# 活动选择问题
def activity_selection(start, finish):
    n = len(start)
    # 按结束时间排序
    activities = sorted(zip(start, finish), key=lambda x: x[1])
    
    selected = [activities[0]]
    last_finish_time = activities[0][1]
    
    for i in range(1, n):
        if activities[i][0] >= last_finish_time:
            selected.append(activities[i])
            last_finish_time = activities[i][1]
    
    return selected

# 找零钱问题
def coin_change_greedy(coins, amount):
    # 贪心算法：优先使用面值最大的硬币
    coins.sort(reverse=True)
    count = 0
    result = []
    
    for coin in coins:
        while amount >= coin:
            amount -= coin
            count += 1
            result.append(coin)
    
    if amount == 0:
        return count, result
    else:
        return -1, []  # 无法找零

# 测试贪心算法
start_times = [1, 3, 0, 5, 8, 5]
finish_times = [2, 4, 6, 7, 9, 9]
print("活动选择:", activity_selection(start_times, finish_times))

coins = [25, 10, 5, 1]  # 美分
amount = 63
count, result = coin_change_greedy(coins, amount)
print(f"找零{amount}美分需要{count}枚硬币:", result)
```

### 分治算法

分治算法将问题分解为子问题，解决子问题，然后将结果合并：

```python
# 最大子数组和问题
def max_subarray_sum_divide_conquer(arr, low, high):
    if low == high:
        return arr[low]
    
    mid = (low + high) // 2
    
    # 递归计算左半部分和右半部分的最大子数组和
    left_sum = max_subarray_sum_divide_conquer(arr, low, mid)
    right_sum = max_subarray_sum_divide_conquer(arr, mid + 1, high)
    
    # 计算跨越中点的最大子数组和
    # 左半部分的最大后缀和
    left_max = float('-inf')
    curr_sum = 0
    for i in range(mid, low - 1, -1):
        curr_sum += arr[i]
        left_max = max(left_max, curr_sum)
    
    # 右半部分的最大前缀和
    right_max = float('-inf')
    curr_sum = 0
    for i in range(mid + 1, high + 1):
        curr_sum += arr[i]
        right_max = max(right_max, curr_sum)
    
    # 跨越中点的最大子数组和
    cross_sum = left_max + right_max
    
    # 返回三者中的最大值
    return max(left_sum, right_sum, cross_sum)

# 测试分治算法
arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
print("最大子数组和:", max_subarray_sum_divide_conquer(arr, 0, len(arr) - 1))  # 6 ([4, -1, 2, 1])
```

### 回溯算法

回溯算法通过尝试分步解决问题，当发现当前解不能产生有效结果时，会回退并尝试其他路径：

```python
# N皇后问题
def solve_n_queens(n):
    board = [['.'] * n for _ in range(n)]
    solutions = []
    
    def is_safe(row, col):
        # 检查列
        for i in range(row):
            if board[i][col] == 'Q':
                return False
        
        # 检查左上对角线
        for i, j in zip(range(row-1, -1, -1), range(col-1, -1, -1)):
            if board[i][j] == 'Q':
                return False
        
        # 检查右上对角线
        for i, j in zip(range(row-1, -1, -1), range(col+1, n)):
            if board[i][j] == 'Q':
                return False
        
        return True
    
    def backtrack(row):
        if row == n:
            solutions.append([''.join(row) for row in board])
            return
        
        for col in range(n):
            if is_safe(row, col):
                board[row][col] = 'Q'
                backtrack(row + 1)
                board[row][col] = '.'  # 回溯
    
    backtrack(0)
    return solutions

# 子集问题
def subsets(nums):
    result = []
    
    def backtrack(start, path):
        result.append(path[:])
        
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()  # 回溯
    
    backtrack(0, [])
    return result

# 测试回溯算法
print("4皇后问题解法数量:", len(solve_n_queens(4)))  # 2
print("[1,2,3]的所有子集:", subsets([1, 2, 3]))  # [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
```

## 算法应用案例

### 文本处理：实现简单的搜索引擎

```python
class SimpleSearchEngine:
    def __init__(self):
        self.documents = {}
        self.index = {}
    
    def add_document(self, doc_id, content):
        self.documents[doc_id] = content
        words = content.lower().split()
        
        for word in words:
            if word not in self.index:
                self.index[word] = set()
            self.index[word].add(doc_id)
    
    def search(self, query):
        query_words = query.lower().split()
        if not query_words:
            return []
        
        # 找到包含第一个查询词的文档
        result_docs = self.index.get(query_words[0], set())
        
        # 对于其他查询词，取交集
        for word in query_words[1:]:
            result_docs &= self.index.get(word, set())
        
        return list(result_docs)

# 使用简单搜索引擎
search_engine = SimpleSearchEngine()
search_engine.add_document(1, "Python is a programming language")
search_engine.add_document(2, "Java is also a programming language")
search_engine.add_document(3, "Python is easy to learn")

print("搜索'python':", search_engine.search("python"))  # [1, 3]
print("搜索'programming language':", search_engine.search("programming language"))  # [1, 2]
print("搜索'java easy':", search_engine.search("java easy"))  # []
```

### 图像处理：实现简单的图像滤镜

```python
def apply_blur_filter(image, kernel_size=3):
    """应用简单的模糊滤镜到图像
    
    参数:
    image -- 2D数组表示的图像
    kernel_size -- 卷积核大小
    
    返回:
    模糊后的图像
    """
    if kernel_size % 2 == 0:
        kernel_size += 1  # 确保是奇数
    
    padding = kernel_size // 2
    height, width = len(image), len(image[0])
    result = [[0 for _ in range(width)] for _ in range(height)]
    
    for i in range(height):
        for j in range(width):
            # 计算卷积
            sum_value = 0
            count = 0
            
            for ki in range(max(0, i-padding), min(height, i+padding+1)):
                for kj in range(max(0, j-padding), min(width, j+padding+1)):
                    sum_value += image[ki][kj]
                    count += 1
            
            result[i][j] = sum_value // count
    
    return result

# 示例图像（灰度值）
image = [
    [50, 50, 50, 50, 50],
    [50, 100, 100, 100, 50],
    [50, 100, 200, 100, 50],
    [50, 100, 100, 100, 50],
    [50, 50, 50, 50, 50]
]

blurred_image = apply_blur_filter(image)
print("原始图像:")
for row in image:
    print(row)

print("\n模糊后图像:")
for row in blurred_image:
    print(row)
```

### 网络算法：实现简单的路由算法

```python
def dijkstra(graph, start):
    """Dijkstra算法计算最短路径
    
    参数:
    graph -- 图的邻接表表示，格式为{node: {neighbor: distance, ...}, ...}
    start -- 起始节点
    
    返回:
    从起始节点到所有其他节点的最短距离
    """
    # 初始化距离字典
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    
    # 未访问节点集合
    unvisited = list(graph.keys())
    
    while unvisited:
        # 找到未访问节点中距离最小的节点
        current = min(unvisited, key=lambda node: distances[node])
        
        # 如果当前节点距离是无穷大，说明剩余未访问节点与起始节点不连通
        if distances[current] == float('infinity'):
            break
        
        # 从未访问集合中移除当前节点
        unvisited.remove(current)
        
        # 更新邻居节点的距离
        for neighbor, distance in graph[current].items():
            new_distance = distances[current] + distance
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
    
    return distances

# 示例网络
network = {
    'A': {'B': 5, 'C': 3},
    'B': {'A': 5, 'C': 2, 'D': 1},
    'C': {'A': 3, 'B': 2, 'D': 6},
    'D': {'B': 1, 'C': 6}
}

print("从节点A到所有节点的最短距离:", dijkstra(network, 'A'))
```

## 总结与进阶学习路径

### 本模块要点总结

1. **算法复杂度分析**：学会分析时间和空间复杂度，选择最优算法。
2. **Python内置数据结构**：掌握列表、元组、字典、集合的特性和适用场景。
3. **自定义数据结构**：能够实现链表、栈、队列、树、堆、图等数据结构。
4. **排序与查找算法**：理解并实现各种排序和查找算法，比较它们的效率。
5. **高级算法**：掌握动态规划、贪心、分治、回溯等算法设计范式。
6. **实际应用**：能够将算法应用到实际问题中，如文本处理、图像处理、网络路由等。

### 进阶学习路径

1. **算法竞赛**：参加LeetCode、Codeforces等平台的编程竞赛，提升解题能力。
2. **专业领域算法**：学习机器学习、计算机视觉、自然语言处理等领域的专业算法。
3. **高级数据结构**：学习B树、红黑树、跳表、布隆过滤器等高级数据结构。
4. **并行算法**：学习如何设计和实现并行算法，提高计算效率。
5. **算法可视化**：使用可视化工具帮助理解复杂算法的执行过程。

### 推荐资源

1. **书籍**：《算法导论》、《Python算法图解》、《编程珠玑》
2. **在线课程**：Coursera上的算法专项课程、MIT的算法公开课
3. **网站**：LeetCode、GeeksforGeeks、VisuAlgo（算法可视化）
4. **Python库**：NumPy、SciPy、NetworkX（图算法）、scikit-learn（机器学习算法）

掌握数据结构与算法是成为优秀程序员的基础，它不仅能帮助你编写高效的代码，还能培养你的逻辑思维和问题解决能力。希望本模块的学习能为你的Python编程之旅打下坚实的基础！