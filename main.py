import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import time
from collections import deque, defaultdict
import heapq
import random
from typing import List, Dict, Tuple

# 페이지 설정
st.set_page_config(
    page_title="스마트그리드 알고리즘 시각화",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .algorithm-box {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

class SmartGridDataStructures:
    """정보과학 성취기준에 따른 자료구조 구현"""
    
    def __init__(self):
        # 선형 자료구조 (성취기준 02-01)
        self.power_queue = deque()  # 전력 요청 큐
        self.history_stack = []     # 작업 이력 스택
        self.power_array = []       # 발전량 배열
        
        # 비선형 자료구조 (성취기준 02-02)
        self.grid_graph = nx.Graph()  # 전력망 그래프
        self.supply_tree = nx.DiGraph()  # 공급 트리
        
        # 초기 데이터 설정
        self._initialize_data()
    
    def _initialize_data(self):
        """초기 스마트그리드 데이터 설정"""
        # 그래프 노드 생성 (발전소, 변전소, 소비지)
        nodes = {
            'solar1': {'type': 'solar', 'capacity': 100, 'pos': (0, 2)},
            'wind1': {'type': 'wind', 'capacity': 150, 'pos': (2, 2)},
            'hydro1': {'type': 'hydro', 'capacity': 200, 'pos': (1, 3)},
            'sub1': {'type': 'substation', 'capacity': 300, 'pos': (1, 1)},
            'sub2': {'type': 'substation', 'capacity': 250, 'pos': (3, 1)},
            'city1': {'type': 'consumer', 'demand': 180, 'pos': (0, 0)},
            'city2': {'type': 'consumer', 'demand': 220, 'pos': (2, 0)},
            'factory1': {'type': 'consumer', 'demand': 150, 'pos': (4, 0)}
        }
        
        for node_id, attrs in nodes.items():
            self.grid_graph.add_node(node_id, **attrs)
        
        # 그래프 간선 생성 (전력선)
        edges = [
            ('solar1', 'sub1', {'capacity': 100, 'distance': 1.5}),
            ('wind1', 'sub2', {'capacity': 150, 'distance': 1.2}),
            ('hydro1', 'sub1', {'capacity': 200, 'distance': 2.0}),
            ('hydro1', 'sub2', {'capacity': 200, 'distance': 1.8}),
            ('sub1', 'city1', {'capacity': 180, 'distance': 1.0}),
            ('sub1', 'city2', {'capacity': 220, 'distance': 2.5}),
            ('sub2', 'city2', {'capacity': 220, 'distance': 1.1}),
            ('sub2', 'factory1', {'capacity': 150, 'distance': 1.3}),
            ('sub1', 'sub2', {'capacity': 100, 'distance': 2.0})
        ]
        
        for source, target, attrs in edges:
            self.grid_graph.add_edge(source, target, **attrs)

class SortingAlgorithms:
    """정렬 알고리즘 구현 및 비교 (성취기준 02-03)"""
    
    @staticmethod
    def bubble_sort(arr, key_func=None):
        """버블 정렬"""
        arr = arr.copy()
        n = len(arr)
        comparisons = 0
        swaps = 0
        
        for i in range(n):
            for j in range(0, n-i-1):
                comparisons += 1
                val1 = key_func(arr[j]) if key_func else arr[j]
                val2 = key_func(arr[j+1]) if key_func else arr[j+1]
                
                if val1 > val2:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    swaps += 1
        
        return arr, comparisons, swaps
    
    @staticmethod
    def quick_sort(arr, key_func=None):
        """퀵 정렬"""
        comparisons = [0]  # 리스트로 참조 전달
        swaps = [0]
        
        def _quick_sort(arr, low, high):
            if low < high:
                pi = partition(arr, low, high)
                _quick_sort(arr, low, pi - 1)
                _quick_sort(arr, pi + 1, high)
        
        def partition(arr, low, high):
            pivot_val = key_func(arr[high]) if key_func else arr[high]
            i = low - 1
            
            for j in range(low, high):
                comparisons[0] += 1
                current_val = key_func(arr[j]) if key_func else arr[j]
                
                if current_val <= pivot_val:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
                    swaps[0] += 1
            
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            swaps[0] += 1
            return i + 1
        
        arr_copy = arr.copy()
        _quick_sort(arr_copy, 0, len(arr_copy) - 1)
        return arr_copy, comparisons[0], swaps[0]

class SearchAlgorithms:
    """탐색 알고리즘 구현 (성취기준 02-04)"""
    
    @staticmethod
    def linear_search(arr, target, key_func=None):
        """순차 탐색"""
        comparisons = 0
        for i, item in enumerate(arr):
            comparisons += 1
            value = key_func(item) if key_func else item
            if value == target:
                return i, comparisons
        return -1, comparisons
    
    @staticmethod
    def binary_search(arr, target, key_func=None):
        """이진 탐색 (정렬된 배열 필요)"""
        left, right = 0, len(arr) - 1
        comparisons = 0
        
        while left <= right:
            comparisons += 1
            mid = (left + right) // 2
            mid_value = key_func(arr[mid]) if key_func else arr[mid]
            
            if mid_value == target:
                return mid, comparisons
            elif mid_value < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return -1, comparisons

class GraphTraversal:
    """그래프 순회 알고리즘 (성취기준 02-05)"""
    
    @staticmethod
    def dfs(graph, start, target=None):
        """깊이 우선 탐색"""
        visited = set()
        path = []
        stack = [start]
        
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                path.append(node)
                
                if target and node == target:
                    return path, len(path)
                
                # 인접 노드를 역순으로 스택에 추가
                neighbors = list(graph.neighbors(node))
                for neighbor in reversed(neighbors):
                    if neighbor not in visited:
                        stack.append(neighbor)
        
        return path, len(path)
    
    @staticmethod
    def bfs(graph, start, target=None):
        """너비 우선 탐색"""
        visited = set()
        path = []
        queue = deque([start])
        
        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                path.append(node)
                
                if target and node == target:
                    return path, len(path)
                
                for neighbor in graph.neighbors(node):
                    if neighbor not in visited:
                        queue.append(neighbor)
        
        return path, len(path)

def main():
    st.markdown("<h1 class='main-header'>⚡ 스마트그리드 알고리즘 시각화</h1>", unsafe_allow_html=True)
    
    # 사이드바 메뉴
    st.sidebar.header("📋 메뉴 선택")
    menu = st.sidebar.selectbox(
        "분석할 알고리즘 선택",
        ["🏠 대시보드", "📊 자료구조", "🔄 정렬 알고리즘", "🔍 탐색 알고리즘", "🌐 그래프 순회", "⚡ 최적화 문제"]
    )
    
    # 데이터 초기화
    if 'grid_data' not in st.session_state:
        st.session_state.grid_data = SmartGridDataStructures()
    
    grid_data = st.session_state.grid_data
    
    if menu == "🏠 대시보드":
        show_dashboard(grid_data)
    elif menu == "📊 자료구조":
        show_data_structures(grid_data)
    elif menu == "🔄 정렬 알고리즘":
        show_sorting_algorithms(grid_data)
    elif menu == "🔍 탐색 알고리즘":
        show_search_algorithms(grid_data)
    elif menu == "🌐 그래프 순회":
        show_graph_traversal(grid_data)
    elif menu == "⚡ 최적화 문제":
        show_optimization_problems(grid_data)

def show_dashboard(grid_data):
    """메인 대시보드"""
    st.header("📈 스마트그리드 실시간 현황")
    
    # 실시간 데이터 시뮬레이션
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        solar_power = np.random.randint(60, 100)
        st.metric("☀️ 태양광 발전", f"{solar_power} MW", f"{np.random.randint(-5, 10)} MW")
    
    with col2:
        wind_power = np.random.randint(80, 150)
        st.metric("💨 풍력 발전", f"{wind_power} MW", f"{np.random.randint(-8, 15)} MW")
    
    with col3:
        hydro_power = np.random.randint(150, 200)
        st.metric("💧 수력 발전", f"{hydro_power} MW", f"{np.random.randint(-3, 8)} MW")
    
    with col4:
        total_demand = np.random.randint(400, 600)
        st.metric("🏭 총 전력 수요", f"{total_demand} MW", f"{np.random.randint(-20, 30)} MW")
    
    # 그리드 네트워크 시각화
    st.subheader("🌐 전력 네트워크 구조")
    
    fig = create_network_visualization(grid_data.grid_graph)
    st.plotly_chart(fig, use_container_width=True)
    
    # 실시간 전력 흐름
    st.subheader("📊 실시간 전력 흐름")
    
    # 시간별 데이터 생성
    hours = list(range(24))
    solar_data = [max(0, 80 * np.sin(np.pi * h / 12) + np.random.randint(-10, 10)) for h in hours]
    wind_data = [100 + 30 * np.sin(2 * np.pi * h / 24) + np.random.randint(-15, 15) for h in hours]
    demand_data = [400 + 100 * (0.5 + 0.3 * np.sin(2 * np.pi * (h - 6) / 24)) + np.random.randint(-20, 20) for h in hours]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=solar_data, name='태양광', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=hours, y=wind_data, name='풍력', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=hours, y=demand_data, name='수요', line=dict(color='red', dash='dash')))
    
    fig.update_layout(
        title="24시간 전력 공급/수요 예측",
        xaxis_title="시간 (hour)",
        yaxis_title="전력 (MW)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_data_structures(grid_data):
    """자료구조 시각화"""
    st.header("📊 자료구조 구현 및 시각화")
    
    tab1, tab2 = st.tabs(["선형 자료구조", "비선형 자료구조"])
    
    with tab1:
        st.subheader("📈 선형 자료구조 (성취기준 02-01)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔄 전력 요청 큐 (Queue)")
            
            # 큐 조작
            if st.button("새 전력 요청 추가"):
                request = f"REQ-{len(grid_data.power_queue)+1:03d}"
                grid_data.power_queue.append(request)
                st.success(f"요청 {request} 추가됨")
            
            if st.button("요청 처리 (Dequeue)") and grid_data.power_queue:
                processed = grid_data.power_queue.popleft()
                st.info(f"요청 {processed} 처리됨")
            
            # 현재 큐 상태
            if grid_data.power_queue:
                st.write("**현재 대기 중인 요청:**")
                for i, req in enumerate(grid_data.power_queue):
                    st.write(f"{i+1}. {req}")
            else:
                st.write("대기 중인 요청이 없습니다.")
        
        with col2:
            st.markdown("### 📚 작업 이력 스택 (Stack)")
            
            # 스택 조작
            if st.button("작업 이력 추가"):
                action = f"ACTION-{len(grid_data.history_stack)+1:03d}"
                grid_data.history_stack.append(action)
                st.success(f"작업 {action} 기록됨")
            
            if st.button("마지막 작업 취소 (Pop)") and grid_data.history_stack:
                canceled = grid_data.history_stack.pop()
                st.warning(f"작업 {canceled} 취소됨")
            
            # 현재 스택 상태
            if grid_data.history_stack:
                st.write("**작업 이력 (최신순):**")
                for i, action in enumerate(reversed(grid_data.history_stack)):
                    st.write(f"{len(grid_data.history_stack)-i}. {action}")
            else:
                st.write("작업 이력이 없습니다.")
    
    with tab2:
        st.subheader("🌐 비선형 자료구조 (성취기준 02-02)")
        
        st.markdown("### 그래프 (Graph) - 스마트그리드 네트워크")
        
        # 그래프 정보 표시
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("노드 수", grid_data.grid_graph.number_of_nodes())
        with col2:
            st.metric("엣지 수", grid_data.grid_graph.number_of_edges())
        with col3:
            connectivity = nx.is_connected(grid_data.grid_graph)
            st.metric("연결성", "연결됨" if connectivity else "분리됨")
        
        # 인접 리스트 표시
        st.markdown("**인접 리스트:**")
        for node in grid_data.grid_graph.nodes():
            neighbors = list(grid_data.grid_graph.neighbors(node))
            st.write(f"• {node}: {neighbors}")

def show_sorting_algorithms(grid_data):
    """정렬 알고리즘 비교"""
    st.header("🔄 정렬 알고리즘 구현 및 비교 (성취기준 02-03)")
    
    # 발전소 데이터 생성
    power_plants = []
    for i in range(10):
        power_plants.append({
            'id': f'Plant-{i+1:02d}',
            'efficiency': np.random.randint(60, 95),
            'capacity': np.random.randint(50, 200),
            'cost': np.random.randint(20, 80)
        })
    
    # 정렬 기준 선택
    sort_key = st.selectbox(
        "정렬 기준 선택:",
        ['efficiency', 'capacity', 'cost'],
        format_func=lambda x: {'efficiency': '효율성', 'capacity': '용량', 'cost': '비용'}[x]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🫧 버블 정렬")
        
        start_time = time.time()
        bubble_result, bubble_comp, bubble_swaps = SortingAlgorithms.bubble_sort(
            power_plants, key_func=lambda x: x[sort_key]
        )
        bubble_time = time.time() - start_time
        
        st.write(f"**수행 시간:** {bubble_time:.6f}초")
        st.write(f"**비교 횟수:** {bubble_comp}")
        st.write(f"**교환 횟수:** {bubble_swaps}")
        st.write(f"**시간 복잡도:** O(n²)")
        
        # 결과 표시
        df_bubble = pd.DataFrame(bubble_result)
        st.dataframe(df_bubble[['id', sort_key]], height=200)
    
    with col2:
        st.subheader("⚡ 퀵 정렬")
        
        start_time = time.time()
        quick_result, quick_comp, quick_swaps = SortingAlgorithms.quick_sort(
            power_plants, key_func=lambda x: x[sort_key]
        )
        quick_time = time.time() - start_time
        
        st.write(f"**수행 시간:** {quick_time:.6f}초")
        st.write(f"**비교 횟수:** {quick_comp}")
        st.write(f"**교환 횟수:** {quick_swaps}")
        st.write(f"**시간 복잡도:** O(n log n)")
        
        # 결과 표시
        df_quick = pd.DataFrame(quick_result)
        st.dataframe(df_quick[['id', sort_key]], height=200)
    
    # 성능 비교 차트
    st.subheader("📊 성능 비교")
    
    comparison_data = {
        '알고리즘': ['버블 정렬', '퀵 정렬'],
        '수행 시간 (초)': [bubble_time, quick_time],
        '비교 횟수': [bubble_comp, quick_comp],
        '교환 횟수': [bubble_swaps, quick_swaps]
    }
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('수행 시간', '비교 횟수', '교환 횟수'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 각 메트릭별 막대 차트
    for i, metric in enumerate(['수행 시간 (초)', '비교 횟수', '교환 횟수']):
        fig.add_trace(
            go.Bar(x=comparison_data['알고리즘'], y=comparison_data[metric], name=metric),
            row=1, col=i+1
        )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def show_search_algorithms(grid_data):
    """탐색 알고리즘 구현"""
    st.header("🔍 탐색 알고리즘 구현 및 비교 (성취기준 02-04)")
    
    # 발전소 효율성 데이터
    efficiencies = [65, 72, 78, 81, 85, 88, 90, 92, 94, 97]
    plant_names = [f"Plant-{i+1:02d}" for i in range(len(efficiencies))]
    
    target_efficiency = st.slider("찾을 효율성 값:", 60, 100, 85)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 순차 탐색 (Linear Search)")
        
        start_time = time.time()
        linear_result, linear_comp = SearchAlgorithms.linear_search(efficiencies, target_efficiency)
        linear_time = time.time() - start_time
        
        st.write(f"**수행 시간:** {linear_time:.6f}초")
        st.write(f"**비교 횟수:** {linear_comp}")
        st.write(f"**시간 복잡도:** O(n)")
        
        if linear_result != -1:
            st.success(f"✅ 효율성 {target_efficiency}% 발견: {plant_names[linear_result]}")
        else:
            st.error("❌ 해당 효율성을 가진 발전소를 찾을 수 없습니다.")
    
    with col2:
        st.subheader("🎯 이진 탐색 (Binary Search)")
        
        start_time = time.time()
        binary_result, binary_comp = SearchAlgorithms.binary_search(efficiencies, target_efficiency)
        binary_time = time.time() - start_time
        
        st.write(f"**수행 시간:** {binary_time:.6f}초")
        st.write(f"**비교 횟수:** {binary_comp}")
        st.write(f"**시간 복잡도:** O(log n)")
        
        if binary_result != -1:
            st.success(f"✅ 효율성 {target_efficiency}% 발견: {plant_names[binary_result]}")
        else:
            st.error("❌ 해당 효율성을 가진 발전소를 찾을 수 없습니다.")
    
    # 데이터 시각화
    st.subheader("📊 발전소 효율성 데이터")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=plant_names, 
        y=efficiencies,
        marker_color=['red' if eff == target_efficiency else 'blue' for eff in efficiencies]
    ))
    
    fig.update_layout(
        title=f"발전소별 효율성 (목표값: {target_efficiency}%)",
        xaxis_title="발전소",
        yaxis_title="효율성 (%)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 성능 비교
    if linear_result != -1 and binary_result != -1:
        st.subheader("⚡ 성능 비교")
        
        efficiency_gain = (linear_comp - binary_comp) / linear_comp * 100
        time_gain = (linear_time - binary_time) / linear_time * 100 if linear_time > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("비교 횟수 절약", f"{efficiency_gain:.1f}%")
        with col2:
            st.metric("시간 절약", f"{time_gain:.1f}%")

def show_graph_traversal(grid_data):
    """그래프 순회 알고리즘"""
    st.header("🌐 그래프 순회 알고리즘 (성취기준 02-05)")
    
    # 시작점과 목표점 선택
    nodes = list(grid_data.grid_graph.nodes())
    
    col1, col2 = st.columns(2)
    with col1:
        start_node = st.selectbox("시작 노드:", nodes, index=0)
    with col2:
        target_node = st.selectbox("목표 노드:", nodes, index=len(nodes)-1 if nodes else 0)
    
    # DFS와 BFS 실행
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 깊이 우선 탐색 (DFS)")
        
        start_time = time.time()
        dfs_path, dfs_length = GraphTraversal.dfs(grid_data.grid_graph, start_node, target_node)
        dfs_time = time.time() - start_time
        
        st.write(f"**수행 시간:** {dfs_time:.6f}초")
        st.write(f"**방문 노드 수:** {dfs_length}")
        st.write(f"**경로:** {' → '.join(dfs_path)}")
        st.write(f"**공간 복잡도:** O(V)")
        
        if target_node in dfs_path:
            target_index = dfs_path.index(target_node)
            st.success(f"✅ 목표 노드 {target_node}를 {target_index + 1}번째로 발견")
    
    with col2:
        st.subheader("🌊 너비 우선 탐색 (BFS)")
        
        start_time = time.time()
        bfs_path, bfs_length = GraphTraversal.bfs(grid_data.grid_graph, start_node, target_node)
        bfs_time = time.time() - start_time
        
        st.write(f"**수행 시간:** {bfs_time:.6f}초")
        st.write(f"**방문 노드 수:** {bfs_length}")
        st.write(f"**경로:** {' → '.join(bfs_path)}")
        st.write(f"**공간 복잡도:** O(V)")
        
        if target_node in bfs_path:
            target_index = bfs_path.index(target_node)
            st.success(f"✅ 목표 노드 {target_node}를 {target_index + 1}번째로 발견")
    
    # 시각화
    st.subheader("🗺️ 탐색 경로 시각화")
    
    fig = create_traversal_visualization(grid_data.grid_graph, dfs_path, bfs_path, start_node, target_node)
    st.plotly_chart(fig, use_container_width=True)
    
    # 알고리즘 비교
    st.subheader("📊 DFS vs BFS 비교")
    
    comparison_df = pd.DataFrame({
        '알고리즘': ['DFS (깊이 우선)', 'BFS (너비 우선)'],
        '수행 시간 (초)': [dfs_time, bfs_time],
        '방문 노드 수': [dfs_length, bfs_length],
        '메모리 사용': ['O(h) - 깊이', 'O(w) - 너비'],
        '최단 경로 보장': ['❌', '✅']
    })
    
    st.dataframe(comparison_df, use_container_width=True)

def show_optimization_problems(grid_data):
    """최적화 문제 분류 및 해결"""
    st.header("⚡ 계산 문제 분류 및 최적화 (성취기준 03-01, 03-02)")
    
    st.markdown("""
    <div class='algorithm-box'>
    <h3>🎯 문제 분류 (성취기준 03-01)</h3>
    <ul>
        <li><strong>결정 문제:</strong> 전력 공급이 가능한가? (YES/NO)</li>
        <li><strong>탐색 문제:</strong> 최적 공급 경로는 무엇인가?</li>
        <li><strong>계수 문제:</strong> 가능한 공급 경로가 몇 개인가?</li>
        <li><strong>최적해 문제:</strong> 최소 비용으로 최대 효율을 내는 방법은?</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["결정 문제", "탐색 문제", "계수 문제", "최적해 문제"])
    
    with tab1:
        st.subheader("🤔 결정 문제: 전력 공급 가능성 판단")
        
        # 입력 파라미터
        total_demand = st.slider("총 전력 수요 (MW):", 100, 800, 500)
        
        # 현재 발전 용량 계산
        solar_capacity = np.random.randint(80, 120)
        wind_capacity = np.random.randint(100, 180)
        hydro_capacity = np.random.randint(150, 220)
        total_supply = solar_capacity + wind_capacity + hydro_capacity
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("☀️ 태양광", f"{solar_capacity} MW")
        with col2:
            st.metric("💨 풍력", f"{wind_capacity} MW")
        with col3:
            st.metric("💧 수력", f"{hydro_capacity} MW")
        with col4:
            st.metric("🔋 총 공급", f"{total_supply} MW")
        
        # 결정 문제 해결
        can_supply = total_supply >= total_demand
        margin = total_supply - total_demand
        
        if can_supply:
            st.success(f"✅ **공급 가능!** 여유 용량: {margin} MW")
        else:
            st.error(f"❌ **공급 불가!** 부족량: {abs(margin)} MW")
        
        # 알고리즘 의사코드
        st.markdown("""
        **의사코드:**
        ```
        function canSupplyPower(demand):
            totalSupply = solarCapacity + windCapacity + hydroCapacity
            if totalSupply >= demand:
                return TRUE
            else:
                return FALSE
        ```
        **시간 복잡도:** O(1) - 상수 시간
        """)
    
    with tab2:
        st.subheader("🗺️ 탐색 문제: 최적 공급 경로 찾기")
        
        # 다익스트라 알고리즘으로 최단 경로 찾기
        source = st.selectbox("발전소 선택:", 
                            [node for node in grid_data.grid_graph.nodes() 
                             if grid_data.grid_graph.nodes[node]['type'] in ['solar', 'wind', 'hydro']])
        target = st.selectbox("목적지 선택:",
                             [node for node in grid_data.grid_graph.nodes() 
                              if grid_data.grid_graph.nodes[node]['type'] == 'consumer'], index=0)  # index=-1을 index=0으로 변경
        
        if st.button("최적 경로 계산"):
            try:
                # 거리 기반 최단 경로
                path = nx.shortest_path(grid_data.grid_graph, source, target, weight='distance')
                total_distance = nx.shortest_path_length(grid_data.grid_graph, source, target, weight='distance')
                
                st.success(f"**최적 경로:** {' → '.join(path)}")
                st.info(f"**총 거리:** {total_distance:.2f} km")
                
                # 경로 시각화
                fig = create_path_visualization(grid_data.grid_graph, path)
                st.plotly_chart(fig, use_container_width=True)
                
            except nx.NetworkXNoPath:
                st.error("경로를 찾을 수 없습니다!")
        
        st.markdown("""
        **다익스트라 알고리즘 의사코드:**
        ```
        function dijkstra(graph, source):
            distance[source] = 0
            for each vertex v:
                if v ≠ source: distance[v] = ∞
            
            while Q is not empty:
                u = vertex with minimum distance in Q
                remove u from Q
                for each neighbor v of u:
                    alt = distance[u] + weight(u,v)
                    if alt < distance[v]:
                        distance[v] = alt
        ```
        **시간 복잡도:** O((V + E) log V)
        """)
    
    with tab3:
        st.subheader("🔢 계수 문제: 가능한 경로 개수")
        
        source = st.selectbox("시작점:", 
                            [node for node in grid_data.grid_graph.nodes() 
                             if grid_data.grid_graph.nodes[node]['type'] in ['solar', 'wind', 'hydro']], 
                            key="count_source")
        target = st.selectbox("도착점:",
                              [node for node in grid_data.grid_graph.nodes() 
                               if grid_data.grid_graph.nodes[node]['type'] == 'consumer'],  key="count_target",  index=0)  # index=-1 제거하고 index=0으로 변경
        
        max_length = st.slider("최대 경로 길이:", 2, 6, 4)
        
        if st.button("경로 개수 계산"):
            # 모든 단순 경로 찾기
            all_paths = list(nx.all_simple_paths(grid_data.grid_graph, source, target, cutoff=max_length))
            
            st.success(f"**총 {len(all_paths)}개의 경로 발견**")
            
            if len(all_paths) <= 10:  # 너무 많으면 일부만 표시
                st.write("**발견된 경로들:**")
                for i, path in enumerate(all_paths, 1):
                    path_length = sum(grid_data.grid_graph[path[j]][path[j+1]]['distance'] 
                                    for j in range(len(path)-1))
                    st.write(f"{i}. {' → '.join(path)} (거리: {path_length:.2f}km)")
            else:
                st.write(f"경로가 너무 많습니다. 처음 10개만 표시:")
                for i, path in enumerate(all_paths[:10], 1):
                    path_length = sum(grid_data.grid_graph[path[j]][path[j+1]]['distance'] 
                                    for j in range(len(path)-1))
                    st.write(f"{i}. {' → '.join(path)} (거리: {path_length:.2f}km)")
        
        st.markdown("""
        **경로 계수 알고리즘 의사코드:**
        ```
        function countPaths(graph, source, target, maxLength):
            count = 0
            for each path in allSimplePaths(graph, source, target):
                if length(path) <= maxLength:
                    count += 1
            return count
        ```
        **시간 복잡도:** O(V! / (V-k)!) - 최악의 경우
        """)
    
    with tab4:
        st.subheader("🎯 최적해 문제: 비용 최소화")
        
        st.markdown("**목표:** 전력 수요를 만족하면서 총 운영 비용을 최소화")
        
        # 발전소별 비용과 용량
        power_sources = {
            'solar1': {'capacity': 100, 'cost_per_mw': 50, 'efficiency': 0.85},
            'wind1': {'capacity': 150, 'cost_per_mw': 45, 'efficiency': 0.80},
            'hydro1': {'capacity': 200, 'cost_per_mw': 35, 'efficiency': 0.90}
        }
        
        demand = st.slider("전력 수요 (MW):", 100, 400, 250)
        
        # 그리디 알고리즘으로 최적해 근사
        if st.button("최적 발전 계획 수립"):
            # 효율성 대비 비용으로 정렬
            sorted_sources = sorted(power_sources.items(), 
                                  key=lambda x: x[1]['cost_per_mw'] / x[1]['efficiency'])
            
            total_cost = 0
            total_generated = 0
            generation_plan = {}
            
            for source_name, source_data in sorted_sources:
                if total_generated >= demand:
                    break
                
                needed = min(demand - total_generated, source_data['capacity'])
                if needed > 0:
                    generation_plan[source_name] = needed
                    total_generated += needed
                    total_cost += needed * source_data['cost_per_mw']
            
            st.success(f"**총 비용:** ${total_cost:,}")
            st.info(f"**총 발전량:** {total_generated} MW")
            
            if total_generated >= demand:
                st.write("**✅ 수요 만족 가능**")
            else:
                st.write(f"**❌ 수요 부족:** {demand - total_generated} MW")
            
            # 발전 계획 표시
            st.write("**발전 계획:**")
            plan_df = pd.DataFrame([
                {
                    '발전소': name,
                    '발전량 (MW)': amount,
                    '단가 ($/MW)': power_sources[name]['cost_per_mw'],
                    '총 비용 ($)': amount * power_sources[name]['cost_per_mw']
                }
                for name, amount in generation_plan.items()
            ])
            st.dataframe(plan_df, use_container_width=True)
            
            # 비용 구성 차트
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(generation_plan.keys()),
                    values=[amount * power_sources[name]['cost_per_mw'] 
                           for name, amount in generation_plan.items()],
                    title="비용 구성"
                )
            ])
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **그리디 알고리즘 의사코드:**
        ```
        function optimizePowerGeneration(demand, sources):
            sort sources by cost_efficiency ratio
            totalCost = 0
            totalGenerated = 0
            
            for each source in sorted_sources:
                if totalGenerated >= demand: break
                needed = min(demand - totalGenerated, source.capacity)
                if needed > 0:
                    use source for needed amount
                    totalCost += needed * source.cost
                    totalGenerated += needed
            
            return totalCost, generation_plan
        ```
        **시간 복잡도:** O(n log n) - 정렬 때문
        """)

def create_network_visualization(graph):
    """네트워크 그래프 시각화"""
    pos = nx.get_node_attributes(graph, 'pos')
    
    # 엣지 그리기
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='gray'),
        hoverinfo='none',
        mode='lines'
    )
    
    # 노드 그리기
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    
    color_map = {
        'solar': 'orange',
        'wind': 'blue',
        'hydro': 'cyan',
        'substation': 'green',
        'consumer': 'red'
    }
    
    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_info = graph.nodes[node]
        node_text.append(f"{node}<br>Type: {node_info['type']}")
        node_color.append(color_map.get(node_info['type'], 'gray'))
        
        if 'capacity' in node_info:
            node_size.append(node_info['capacity'] / 10)
        elif 'demand' in node_info:
            node_size.append(node_info['demand'] / 10)
        else:
            node_size.append(20)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[node for node in graph.nodes()],
        textposition="middle center",
        hovertext=node_text,
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color='white')
        )
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
    title='스마트그리드 네트워크',
    showlegend=False,
    hovermode='closest',
    margin=dict(b=20,l=5,r=5,t=40),
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    fig.add_annotation(
    text="노드 크기는 용량/수요에 비례",
    showarrow=False,
    xref="paper", yref="paper",
    x=0.005, y=-0.002,
    xanchor="left", yanchor="bottom",
    font=dict(size=12)
    )
    
    return fig

def create_traversal_visualization(graph, dfs_path, bfs_path, start, target):
    """DFS/BFS 경로 시각화"""
    pos = nx.get_node_attributes(graph, 'pos')
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('DFS 경로', 'BFS 경로'),
        specs=[[{"type": "scatter"}, {"type": "scatter"}]]
    )
    
    # DFS 시각화
    for i, (path, col, title) in enumerate([(dfs_path, 1, 'DFS'), (bfs_path, 2, 'BFS')]):
        # 모든 엣지 (회색)
        edge_x, edge_y = [], []
        for edge in graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        fig.add_trace(
            go.Scatter(x=edge_x, y=edge_y, mode='lines', 
                      line=dict(color='lightgray', width=1),
                      showlegend=False, hoverinfo='none'),
            row=1, col=col
        )
        
        # 경로 엣지 (색상)
        path_edge_x, path_edge_y = [], []
        for j in range(len(path) - 1):
            if path[j+1] in graph.neighbors(path[j]):
                x0, y0 = pos[path[j]]
                x1, y1 = pos[path[j+1]]
                path_edge_x.extend([x0, x1, None])
                path_edge_y.extend([y0, y1, None])
        
        fig.add_trace(
            go.Scatter(x=path_edge_x, y=path_edge_y, mode='lines',
                      line=dict(color='red' if title == 'DFS' else 'blue', width=3),
                      showlegend=False, hoverinfo='none'),
            row=1, col=col
        )
        
        # 노드
        node_x = [pos[node][0] for node in graph.nodes()]
        node_y = [pos[node][1] for node in graph.nodes()]
        node_colors = []
        
        for node in graph.nodes():
            if node == start:
                node_colors.append('green')
            elif node == target:
                node_colors.append('purple')
            elif node in path:
                node_colors.append('red' if title == 'DFS' else 'blue')
            else:
                node_colors.append('lightgray')
        
        fig.add_trace(
            go.Scatter(x=node_x, y=node_y, mode='markers+text',
                      text=list(graph.nodes()), textposition="middle center",
                      marker=dict(size=15, color=node_colors),
                      showlegend=False),
            row=1, col=col
        )
    
    fig.update_layout(height=400)
    fig.update_xaxes(showgrid=False, showticklabels=False)
    fig.update_yaxes(showgrid=False, showticklabels=False)
    
    return fig

def create_path_visualization(graph, path):
    """최단 경로 시각화"""
    pos = nx.get_node_attributes(graph, 'pos')
    
    # 모든 엣지
    edge_x, edge_y = [], []
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, mode='lines',
        line=dict(color='lightgray', width=1),
        hoverinfo='none', showlegend=False
    )
    
    # 최단 경로 엣지
    path_edge_x, path_edge_y = [], []
    for i in range(len(path) - 1):
        x0, y0 = pos[path[i]]
        x1, y1 = pos[path[i+1]]
        path_edge_x.extend([x0, x1, None])
        path_edge_y.extend([y0, y1, None])
    
    path_trace = go.Scatter(
        x=path_edge_x, y=path_edge_y, mode='lines',
        line=dict(color='red', width=4),
        hoverinfo='none', showlegend=False
    )
    
    # 노드
    node_x = [pos[node][0] for node in graph.nodes()]
    node_y = [pos[node][1] for node in graph.nodes()]
    node_colors = ['red' if node in path else 'lightblue' for node in graph.nodes()]
    
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text',
        text=list(graph.nodes()), textposition="middle center",
        marker=dict(size=15, color=node_colors),
        showlegend=False
    )
    
    fig = go.Figure(data=[edge_trace, path_trace, node_trace])
    fig.update_layout(
        title=f'최단 경로: {" → ".join(path)}',
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        height=400
    )
    
    return fig

if __name__ == "__main__":
    main()
