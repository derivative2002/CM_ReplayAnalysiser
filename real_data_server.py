#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实数据Web服务器 - 集成回放分析功能
"""
import asyncio
import json
import os
import sys
import threading
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import websockets

# 指挥官中文名称映射
COMMANDER_NAME_MAP = {
    'Zagara': '扎加拉',
    'Tychus': '泰凯斯',
    'Raynor': '雷诺',
    'Kerrigan': '凯瑞甘',
    'Swann': '斯旺',
    'Artanis': '阿塔尼斯',
    'Vorazun': '沃拉尊',
    'Karax': '卡拉克斯',
    'Abathur': '阿巴瑟',
    'Alarak': '阿拉纳克',
    'Nova': '诺娃',
    'Stukov': '斯托科夫',
    'Fenix': '菲尼克斯',
    'Dehaka': '德哈卡',
    'Han': '韩',
    'Horner': '霍纳',
    'Zeratul': '泽拉图',
    'Stetmann': '斯台特曼',
    'Mengsk': '蒙斯克'
}

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SCOFunctions.MainFunctions import find_replays
from SCOFunctions.ReplayAnalysis import parse_replay_file

# 全局数据存储
latest_replay_data = {}
replay_cache = {}
connected_clients = set()

class APIHandler(SimpleHTTPRequestHandler):
    """支持API的HTTP请求处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="web", **kwargs)
    
    def end_headers(self):
        # 添加CORS头部
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # API端点处理
        if path == '/api/status':
            self.handle_api_status()
        elif path == '/api/replay/latest':
            self.handle_api_latest_replay()
        elif path == '/api/stats/summary':
            self.handle_api_stats_summary()
        elif path == '/api/games/history':
            self.handle_api_games_history()
        elif path.startswith('/api/'):
            self.send_404()
        else:
            # 默认文件服务
            super().do_GET()
    
    def handle_api_status(self):
        """处理状态API"""
        status = {
            'status': 'success',
            'data': {
                'connected': True,
                'websocket_clients': len(connected_clients),
                'replay_count': len(replay_cache),
                'last_analysis': datetime.now().isoformat() if latest_replay_data else None
            },
            'timestamp': datetime.now().isoformat()
        }
        self.send_json_response(status)
    
    def handle_api_latest_replay(self):
        """处理最新回放API"""
        if latest_replay_data:
            response = {
                'status': 'success',
                'data': latest_replay_data,
                'timestamp': datetime.now().isoformat()
            }
        else:
            response = {
                'status': 'no_data',
                'message': '暂无回放数据',
                'timestamp': datetime.now().isoformat()
            }
        self.send_json_response(response)
    
    def handle_api_stats_summary(self):
        """处理统计摘要API"""
        if replay_cache:
            # 计算统计数据
            total_games = len(replay_cache)
            maps = {}
            commanders = {}
            
            for filepath, data in replay_cache.items():
                if data and 'map_name' in data:
                    map_name = data['map_name']
                    maps[map_name] = maps.get(map_name, 0) + 1
                
                if data and 'players' in data:
                    for player in data['players']:
                        race = player.get('race', 'Unknown')
                        commanders[race] = commanders.get(race, 0) + 1
            
            summary = {
                'total_games': total_games,
                'maps': maps,
                'commanders': commanders,
                'last_updated': datetime.now().isoformat()
            }
            
            response = {
                'status': 'success',
                'data': summary,
                'timestamp': datetime.now().isoformat()
            }
        else:
            response = {
                'status': 'no_data',
                'message': '暂无统计数据',
                'timestamp': datetime.now().isoformat()
            }
        
        self.send_json_response(response)
    
    def handle_api_games_history(self):
        """处理游戏历史API"""
        if replay_cache:
            # 将回放数据转换为前端期望的游戏历史格式
            games_data = []
            
            for i, (filepath, data) in enumerate(replay_cache.items()):
                if data:
                    # 从回放数据中提取真实信息
                    game_length = data.get('length', data.get('accurate_length', 0))
                    if isinstance(game_length, (int, float)):
                        game_length = int(game_length)
                    else:
                        game_length = 0
                    
                    game_entry = {
                        'id': i + 1,
                        'mapName': data.get('map_name', 'Unknown'),
                        'difficulty': self.extract_difficulty(data),
                        'result': data.get('result', 'Unknown'),
                        'length': game_length,
                        'date': data.get('date', datetime.now().isoformat()),
                        'fileName': os.path.basename(filepath),
                        'region': data.get('region', 'Unknown'),
                        'gameType': 'mutation' if data.get('mutators') else 'normal',
                        'player1': {
                            'name': 'Player1',
                            'commander': 'Unknown',
                            'apm': 120,
                            'kills': 25
                        },
                        'player2': {
                            'name': 'Player2', 
                            'commander': 'Unknown',
                            'apm': 110,
                            'kills': 30
                        }
                    }
                    
                    # 尝试从回放数据中提取玩家信息
                    if 'players' in data and len(data['players']) >= 2:
                        players = data['players']
                        
                        # 找到两个真正的玩家（非AI）
                        human_players = []
                        for player in players:
                            # 跳过埃蒙的部队和其他AI单位
                            if player.get('result') in ['Win', 'Loss'] and player.get('commander'):
                                human_players.append(player)
                        
                        # 更新玩家信息
                        if len(human_players) >= 1:
                            commander = human_players[0].get('commander', 'Unknown')
                            commander_cn = COMMANDER_NAME_MAP.get(commander, commander)
                            game_entry['player1'].update({
                                'name': human_players[0].get('name', 'Player1'),
                                'commander': commander,
                                'commander_cn': commander_cn,
                                'apm': human_players[0].get('apm', 0),
                                'kills': human_players[0].get('kills', 0)
                            })
                        
                        if len(human_players) >= 2:
                            commander = human_players[1].get('commander', 'Unknown')
                            commander_cn = COMMANDER_NAME_MAP.get(commander, commander)
                            game_entry['player2'].update({
                                'name': human_players[1].get('name', 'Player2'),
                                'commander': commander,
                                'commander_cn': commander_cn,
                                'apm': human_players[1].get('apm', 0),
                                'kills': human_players[1].get('kills', 0)
                            })
                    
                    games_data.append(game_entry)
            
            response = {
                'status': 'success',
                'data': games_data,
                'meta': {
                    'total': len(games_data),
                    'page': 1,
                    'per_page': len(games_data)
                },
                'timestamp': datetime.now().isoformat()
            }
        else:
            response = {
                'status': 'no_data',
                'message': '暂无游戏历史记录',
                'data': [],
                'meta': {
                    'total': 0,
                    'page': 1,
                    'per_page': 0
                },
                'timestamp': datetime.now().isoformat()
            }
        
        self.send_json_response(response)
    
    def extract_difficulty(self, data):
        """提取游戏难度"""
        if 'difficulty' in data:
            diff = data['difficulty']
            if isinstance(diff, tuple) and len(diff) > 0:
                diff_name = diff[0]
                # 转换难度名称为数字
                difficulty_map = {
                    'Casual': 1,
                    'Normal': 2, 
                    'Hard': 3,
                    'Brutal': 4,
                    'Brutal+': 5
                }
                return difficulty_map.get(diff_name, 4)
            elif isinstance(diff, str):
                difficulty_map = {
                    'Casual': 1,
                    'Normal': 2,
                    'Hard': 3, 
                    'Brutal': 4,
                    'Brutal+': 5
                }
                return difficulty_map.get(diff, 4)
        
        # 检查是否有Brutal+信息
        if 'brutal_plus' in data:
            return 5
        
        return 4  # 默认Brutal
    
    def send_json_response(self, data):
        """发送JSON响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_404(self):
        """发送404响应"""
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_response = {
            'status': 'error',
            'message': 'API端点不存在',
            'timestamp': datetime.now().isoformat()
        }
        json_data = json.dumps(error_response, ensure_ascii=False)
        self.wfile.write(json_data.encode('utf-8'))

def analyze_replays():
    """分析回放文件"""
    global latest_replay_data, replay_cache
    
    test_replay_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_replay')
    
    if not os.path.exists(test_replay_path):
        print(f"警告: test_replay 文件夹不存在: {test_replay_path}")
        return
    
    print(f"开始分析回放文件: {test_replay_path}")
    
    # 查找所有回放文件
    replays = find_replays(test_replay_path)
    print(f"找到 {len(replays)} 个回放文件")
    
    # 分析每个回放文件
    sorted_replays = sorted(replays)
    total_replays = len(sorted_replays)
    for i, replay_path in enumerate(sorted_replays):
        try:
            print(f"分析 {i+1}/{total_replays}: {os.path.basename(replay_path)}")
            
            # 解析回放文件
            replay_data = parse_replay_file(replay_path)
            
            if replay_data:
                # 清理数据中的bytes对象
                cleaned_data = clean_replay_data(replay_data)
                replay_cache[replay_path] = cleaned_data
                
                # 更新最新回放数据
                latest_replay_data = {
                    'replayPath': replay_path,
                    'fileName': os.path.basename(replay_path),
                    'mapName': cleaned_data.get('map_name', 'Unknown'),
                    'players': cleaned_data.get('players', []),
                    'gameLength': cleaned_data.get('game_length', 0),
                    'analyzedAt': datetime.now().isoformat()
                }
                
                print(f"  ✓ 成功: {cleaned_data.get('map_name', 'Unknown')}")
            else:
                print(f"  ✗ 解析失败")
                
        except Exception as e:
            print(f"  ✗ 错误: {e}")
    
    print(f"分析完成，成功解析 {len(replay_cache)} 个回放")

def clean_replay_data(data):
    """清理回放数据中的bytes对象"""
    if isinstance(data, dict):
        return {k: clean_replay_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_replay_data(item) for item in data]
    elif isinstance(data, bytes):
        try:
            return data.decode('utf-8')
        except:
            return str(data)
    else:
        return data

async def websocket_handler(websocket, path):
    """WebSocket处理器"""
    connected_clients.add(websocket)
    print(f"WebSocket客户端连接: {websocket.remote_address}")
    
    try:
        # 发送最新数据
        if latest_replay_data:
            await websocket.send(json.dumps({
                'type': 'replay_data',
                'data': latest_replay_data,
                'timestamp': datetime.now().isoformat()
            }))
        
        # 保持连接
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        print(f"WebSocket客户端断开: {websocket.remote_address}")

def run_http_server(port=3000):
    """运行HTTP服务器"""
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"HTTP服务器启动在 http://0.0.0.0:{port}")
    print(f"远程访问: http://<服务器IP>:{port}")
    print(f"API端点:")
    print(f"  - GET /api/status")
    print(f"  - GET /api/replay/latest") 
    print(f"  - GET /api/stats/summary")
    server.serve_forever()

async def run_websocket_server(port=7310):
    """运行WebSocket服务器"""
    print(f"WebSocket服务器启动在 ws://0.0.0.0:{port}")
    return await websockets.serve(websocket_handler, "0.0.0.0", port)

async def main():
    """主函数"""
    print("=== SC2 Co-op Overlay 真实数据服务器 ===")
    
    # 分析回放文件
    print("\n1. 分析回放文件...")
    analyze_replays()
    
    # 启动HTTP服务器
    print("\n2. 启动HTTP服务器...")
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # 启动WebSocket服务器
    print("\n3. 启动WebSocket服务器...")
    websocket_server = await run_websocket_server()
    
    print("\n✓ 服务器启动完成!")
    print("请访问 http://localhost:9999 查看Web界面")
    print("按 Ctrl+C 停止服务器")
    
    # 保持运行
    try:
        await websocket_server.wait_closed()
    except KeyboardInterrupt:
        print("\n正在停止服务器...")

if __name__ == "__main__":
    asyncio.run(main())