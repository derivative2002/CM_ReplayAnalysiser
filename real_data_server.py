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
from SCOFunctions.ReplayAnalysis import parse_replay_file, analyse_parsed_replay
from SCOFunctions.IdentifyMutators import identify_mutators

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
        elif path.startswith('/api/game/factors/'):
            self.handle_api_game_factors(path)
        elif path == '/api/factors/statistics':
            self.handle_api_factors_statistics()
        elif path == '/api/mutator/overview':
            self.handle_api_mutator_overview()
        elif path == '/api/mutator/kills':
            self.handle_api_mutator_kills()
        elif path == '/api/mutator/performance':
            self.handle_api_mutator_performance()
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
    
    def handle_api_game_factors(self, path):
        """处理游戏因子分析API"""
        game_id = path.split('/')[-1]
        
        try:
            game_id = int(game_id) - 1  # 转换为0索引
            if 0 <= game_id < len(replay_cache):
                filepath = list(replay_cache.keys())[game_id]
                data = replay_cache[filepath]
                
                factors = self.extract_game_factors(data, filepath)
                response = {
                    'status': 'success',
                    'data': factors,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                response = {
                    'status': 'error',
                    'message': '游戏ID不存在',
                    'timestamp': datetime.now().isoformat()
                }
        except:
            response = {
                'status': 'error',
                'message': '无效的游戏ID',
                'timestamp': datetime.now().isoformat()
            }
        
        self.send_json_response(response)
    
    def handle_api_factors_statistics(self):
        """处理因子统计API"""
        if replay_cache:
            all_factors = []
            for filepath, data in replay_cache.items():
                factors = self.extract_game_factors(data, filepath)
                all_factors.append(factors)
            
            # 计算平均值
            avg_factors = self.calculate_average_factors(all_factors)
            
            response = {
                'status': 'success',
                'data': {
                    'total_games': len(all_factors),
                    'average_factors': avg_factors,
                    'factor_ranges': self.calculate_factor_ranges(all_factors)
                },
                'timestamp': datetime.now().isoformat()
            }
        else:
            response = {
                'status': 'no_data',
                'message': '暂无因子统计数据',
                'timestamp': datetime.now().isoformat()
            }
        
        self.send_json_response(response)
    
    def extract_game_factors(self, replay_data, filepath):
        """从回放数据中提取游戏因子"""
        factors = {
            'game_id': os.path.basename(filepath),
            'map_factors': {
                'map_name': replay_data.get('map_name', 'Unknown'),
                'map_size': 'medium',  # 可以根据地图名称推断
                'enemy_composition': replay_data.get('enemy_race', 'Mixed'),
                'objective_type': 'standard'
            },
            'performance_factors': {},
            'combat_factors': {
                'total_kills': 0,
                'kill_death_ratio': 0,
                'damage_dealt': 0,
                'damage_taken': 0
            },
            'cooperation_factors': {
                'sync_score': 0,
                'resource_sharing': 0,
                'combined_attacks': 0
            },
            'difficulty_factors': {
                'base_difficulty': self.extract_difficulty(replay_data),
                'mutators': replay_data.get('mutators', []),
                'adjusted_difficulty': self.extract_difficulty(replay_data)
            },
            'time_factors': {
                'game_length': replay_data.get('length', 0),
                'early_game_score': 0,
                'mid_game_score': 0,
                'late_game_score': 0
            }
        }
        
        # 提取玩家性能因子
        if 'players' in replay_data:
            human_players = []
            for player in replay_data['players']:
                if player.get('result') in ['Win', 'Loss'] and player.get('commander'):
                    human_players.append(player)
            
            for i, player in enumerate(human_players[:2]):
                player_key = f'player{i+1}'
                factors['performance_factors'][player_key] = {
                    'name': player.get('name', f'Player{i+1}'),
                    'commander': player.get('commander', 'Unknown'),
                    'apm': player.get('apm', 0),
                    'resource_efficiency': self.calculate_resource_efficiency(player),
                    'unit_control_score': self.calculate_unit_control_score(player)
                }
                
                # 累加战斗因子
                factors['combat_factors']['total_kills'] += player.get('kills', 0)
        
        # 计算协作分数
        factors['cooperation_factors']['sync_score'] = self.calculate_sync_score(replay_data)
        
        return factors
    
    def calculate_resource_efficiency(self, player_data):
        """计算资源效率"""
        # 简化计算：基于APM和游戏结果
        base_score = 50
        if player_data.get('result') == 'Win':
            base_score += 20
        apm = player_data.get('apm', 100)
        return min(100, base_score + (apm / 10))
    
    def calculate_unit_control_score(self, player_data):
        """计算单位控制评分"""
        # 基于APM和击杀数
        apm = player_data.get('apm', 100)
        kills = player_data.get('kills', 0)
        return min(100, (apm / 2) + (kills / 10))
    
    def calculate_sync_score(self, replay_data):
        """计算协同作战评分"""
        # 简化：基于游戏结果和时长
        base_score = 50
        if replay_data.get('result') == 'Victory':
            base_score += 30
        # 游戏时长越接近20分钟，协同分越高
        game_length = replay_data.get('length', 1200)
        if 900 <= game_length <= 1500:  # 15-25分钟
            base_score += 20
        return min(100, base_score)
    
    def calculate_average_factors(self, all_factors):
        """计算平均因子值"""
        if not all_factors:
            return {}
        
        avg = {
            'performance': {
                'avg_apm': 0,
                'avg_resource_efficiency': 0,
                'avg_unit_control': 0
            },
            'combat': {
                'avg_kills': 0,
                'avg_kd_ratio': 0
            },
            'cooperation': {
                'avg_sync_score': 0
            }
        }
        
        total_apm = 0
        total_efficiency = 0
        total_control = 0
        total_kills = 0
        total_sync = 0
        player_count = 0
        
        for factors in all_factors:
            for player_key in ['player1', 'player2']:
                if player_key in factors['performance_factors']:
                    player = factors['performance_factors'][player_key]
                    total_apm += player.get('apm', 0)
                    total_efficiency += player.get('resource_efficiency', 0)
                    total_control += player.get('unit_control_score', 0)
                    player_count += 1
            
            total_kills += factors['combat_factors']['total_kills']
            total_sync += factors['cooperation_factors']['sync_score']
        
        if player_count > 0:
            avg['performance']['avg_apm'] = total_apm / player_count
            avg['performance']['avg_resource_efficiency'] = total_efficiency / player_count
            avg['performance']['avg_unit_control'] = total_control / player_count
        
        if all_factors:
            avg['combat']['avg_kills'] = total_kills / len(all_factors)
            avg['cooperation']['avg_sync_score'] = total_sync / len(all_factors)
        
        return avg
    
    def calculate_factor_ranges(self, all_factors):
        """计算因子范围"""
        ranges = {
            'apm': {'min': float('inf'), 'max': 0},
            'kills': {'min': float('inf'), 'max': 0},
            'game_length': {'min': float('inf'), 'max': 0}
        }
        
        for factors in all_factors:
            # APM范围
            for player_key in ['player1', 'player2']:
                if player_key in factors['performance_factors']:
                    apm = factors['performance_factors'][player_key].get('apm', 0)
                    ranges['apm']['min'] = min(ranges['apm']['min'], apm)
                    ranges['apm']['max'] = max(ranges['apm']['max'], apm)
            
            # 击杀范围
            kills = factors['combat_factors']['total_kills']
            ranges['kills']['min'] = min(ranges['kills']['min'], kills)
            ranges['kills']['max'] = max(ranges['kills']['max'], kills)
            
            # 游戏时长范围
            length = factors['time_factors']['game_length']
            if length > 0:
                ranges['game_length']['min'] = min(ranges['game_length']['min'], length)
                ranges['game_length']['max'] = max(ranges['game_length']['max'], length)
        
        # 处理无数据情况
        for key in ranges:
            if ranges[key]['min'] == float('inf'):
                ranges[key]['min'] = 0
        
        return ranges
    
    def handle_api_mutator_overview(self):
        """处理突变因子概览API"""
        mutator_stats = {}
        total_mutation_games = 0
        total_games = len(replay_cache)
        
        # 从单位击杀信息推断突变因子的映射
        mutator_unit_mapping = {
            'MutatorDeathBot': 'Kill Bots',
            'MutatorMurderBot': 'Kill Bots',
            'MutatorBoomBot': 'Boom Bots',
            'MutatorPropagator': 'Propagators',
            'MutatorSpiderMine': 'Minesweeper',
            'MutatorPurifierBeam': 'Purifier Beam',
            'MutatorTornado': 'Twister',
            'MutatorAmonArtanis': 'Heroes from the Storm',
            'MutatorAmonKerrigan': 'Heroes from the Storm',
            'MutatorAmonZeratul': 'Heroes from the Storm',
            'MutatorAmonNova': 'Heroes from the Storm',
            'MutatorAmonRaynor': 'Heroes from the Storm',
            'MutatorAmonZagara': 'Heroes from the Storm',
            'MutatorAmonTychus': 'Heroes from the Storm',
            'MutatorAmonDehaka': 'Heroes from the Storm',
        }
        
        # 统计突变因子
        for filepath, data in replay_cache.items():
            mutators = list(data.get('mutators', []))
            detected_mutators = set()
            
            # 从击杀信息推断突变因子
            if 'amon_units' in data:
                for unit in data['amon_units']:
                    for mutator_unit, mutator_name in mutator_unit_mapping.items():
                        if mutator_unit in unit:
                            detected_mutators.add(mutator_name)
            
            # 合并识别的突变因子
            all_mutators = set(mutators) | detected_mutators
            
            if all_mutators:
                total_mutation_games += 1
                for mutator in all_mutators:
                    if mutator not in mutator_stats:
                        mutator_stats[mutator] = {
                            'count': 0,
                            'wins': 0,
                            'total_time': 0,
                            'games': []
                        }
                    mutator_stats[mutator]['count'] += 1
                    mutator_stats[mutator]['games'].append(filepath)
                    if data.get('result') == 'Victory':
                        mutator_stats[mutator]['wins'] += 1
                    mutator_stats[mutator]['total_time'] += data.get('length', 0)
        
        # 计算百分比和胜率
        for mutator, stats in mutator_stats.items():
            stats['percentage'] = (stats['count'] / total_mutation_games * 100) if total_mutation_games > 0 else 0
            stats['win_rate'] = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
            stats['avg_completion_time'] = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0
            del stats['games']  # 移除文件路径列表
        
        # 获取敌人组成
        enemy_composition = {}
        for filepath, data in replay_cache.items():
            enemy_race = data.get('enemy_race', 'Unknown')
            enemy_composition[enemy_race] = enemy_composition.get(enemy_race, 0) + 1
        
        response = {
            'status': 'success',
            'data': {
                'mutator_stats': {
                    'total_mutation_games': total_mutation_games,
                    'total_games': total_games,
                    'mutation_percentage': (total_mutation_games / total_games * 100) if total_games > 0 else 0,
                    'mutators': mutator_stats
                },
                'enemy_composition': enemy_composition
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_json_response(response)
    
    def handle_api_mutator_kills(self):
        """处理突变因子特殊击杀统计API"""
        special_kills = {
            'voidrifts': {'total': 0, 'player1': 0, 'player2': 0, 'games_with': 0},
            'propagators': {'total': 0, 'player1': 0, 'player2': 0, 'games_with': 0},
            'tus': {'total': 0, 'player1': 0, 'player2': 0, 'games_with': 0},
            'voidreanimators': {'total': 0, 'player1': 0, 'player2': 0, 'games_with': 0},
            'turkey': {'total': 0, 'player1': 0, 'player2': 0, 'games_with': 0},
            'hfts': {'total': 0, 'player1': 0, 'player2': 0, 'games_with': 0}
        }
        
        # 统计特殊单位击杀
        for filepath, data in replay_cache.items():
            kills = data.get('special_kills', {})
            if isinstance(kills, dict):
                for unit_type, unit_kills in kills.items():
                    if unit_type in special_kills and isinstance(unit_kills, dict):
                        if 1 in unit_kills or 2 in unit_kills:
                            special_kills[unit_type]['games_with'] += 1
                            special_kills[unit_type]['player1'] += unit_kills.get(1, 0)
                            special_kills[unit_type]['player2'] += unit_kills.get(2, 0)
                            special_kills[unit_type]['total'] += unit_kills.get(1, 0) + unit_kills.get(2, 0)
        
        # 计算平均值
        total_games = len(replay_cache)
        for unit_type in special_kills:
            games_with = special_kills[unit_type]['games_with']
            if games_with > 0:
                special_kills[unit_type]['avg_per_game'] = special_kills[unit_type]['total'] / games_with
            else:
                special_kills[unit_type]['avg_per_game'] = 0
            
            special_kills[unit_type]['player_distribution'] = {
                'player1': special_kills[unit_type]['player1'],
                'player2': special_kills[unit_type]['player2']
            }
        
        response = {
            'status': 'success',
            'data': {
                'special_kills': special_kills,
                'total_games': total_games
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_json_response(response)
    
    def handle_api_mutator_performance(self):
        """处理指挥官对抗突变表现API"""
        commander_performance = {}
        
        # 分析每个指挥官对抗不同突变的表现
        for filepath, data in replay_cache.items():
            mutators = data.get('mutators', [])
            if not mutators:
                continue
                
            # 获取玩家信息
            if 'players' in data:
                for player in data['players'][:2]:  # 只看前两个玩家
                    commander = player.get('commander', 'Unknown')
                    if commander == 'Unknown':
                        continue
                        
                    if commander not in commander_performance:
                        commander_performance[commander] = {}
                    
                    # 对每个突变因子记录表现
                    for mutator in mutators:
                        key = f'vs_{mutator.lower().replace(" ", "_")}'
                        if key not in commander_performance[commander]:
                            commander_performance[commander][key] = {
                                'games': 0,
                                'wins': 0,
                                'total_apm': 0,
                                'total_kills': 0
                            }
                        
                        stats = commander_performance[commander][key]
                        stats['games'] += 1
                        if data.get('result') == 'Victory':
                            stats['wins'] += 1
                        stats['total_apm'] += player.get('apm', 0)
                        stats['total_kills'] += player.get('kills', 0)
        
        # 计算胜率和平均值
        for commander, mutator_stats in commander_performance.items():
            for mutator_key, stats in mutator_stats.items():
                if stats['games'] > 0:
                    stats['win_rate'] = (stats['wins'] / stats['games'] * 100)
                    stats['avg_apm'] = stats['total_apm'] / stats['games']
                    stats['avg_kills'] = stats['total_kills'] / stats['games']
                else:
                    stats['win_rate'] = 0
                    stats['avg_apm'] = 0
                    stats['avg_kills'] = 0
                
                # 清理临时字段
                del stats['total_apm']
                del stats['total_kills']
        
        response = {
            'status': 'success',
            'data': {
                'commander_performance': commander_performance
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_json_response(response)
    
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
            parsed_replay = parse_replay_file(replay_path)
            
            if parsed_replay:
                # 分析回放数据
                try:
                    analysis_result = analyse_parsed_replay(replay_path, parsed_replay)
                    
                    # 识别突变因子
                    mutator_info = {}
                    if parsed_replay.get('m_version') and parsed_replay.get('m_syncLobbyState'):
                        events = parsed_replay.get('events', [])
                        mutator_info = identify_mutators(
                            events, 
                            extension=True,
                            detailed_info=parsed_replay
                        )
                    
                    # 合并数据
                    replay_data = {
                        **parsed_replay,
                        'analysis': analysis_result,
                        'mutators': mutator_info.get('mutators', []) if isinstance(mutator_info, dict) else [],
                        'special_kills': extract_special_kills(analysis_result) if analysis_result else {}
                    }
                    
                    # 清理数据中的bytes对象
                    cleaned_data = clean_replay_data(replay_data)
                    replay_cache[replay_path] = cleaned_data
                except Exception as e:
                    print(f"  ✗ 分析失败: {e}")
                    # 使用基础数据
                    replay_data = parsed_replay
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

def extract_special_kills(analysis_result):
    """从分析结果中提取特殊单位击杀数据"""
    special_kills = {}
    
    # 特殊单位类型映射
    special_units = ['voidrifts', 'propagators', 'tus', 'voidreanimators', 'turkey', 'hfts']
    
    # 从mainIcons和allyIcons中提取数据
    main_icons = analysis_result.get('mainIcons', {})
    ally_icons = analysis_result.get('allyIcons', {})
    
    for unit_type in special_units:
        if unit_type in main_icons or unit_type in ally_icons:
            # 获取主玩家击杀数（玩家1）
            player1_kills = 0
            if unit_type in main_icons and isinstance(main_icons[unit_type], (int, float)):
                player1_kills = int(main_icons[unit_type])
            
            # 获取盟友击杀数（玩家2）
            player2_kills = 0
            if unit_type in ally_icons and isinstance(ally_icons[unit_type], (int, float)):
                player2_kills = int(ally_icons[unit_type])
            
            special_kills[unit_type] = {
                1: player1_kills,
                2: player2_kills
            }
    
    return special_kills

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