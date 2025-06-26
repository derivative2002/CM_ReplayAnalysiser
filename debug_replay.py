#!/usr/bin/env python3
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SCOFunctions.MainFunctions import find_replays
from SCOFunctions.ReplayAnalysis import parse_replay_file, analyse_parsed_replay
from SCOFunctions.IdentifyMutators import identify_mutators

# 分析一个回放文件
test_replay_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_replay')
replays = find_replays(test_replay_path)

if replays:
    replay_path = list(replays)[0]
    print(f"分析文件: {os.path.basename(replay_path)}")
    
    # 解析回放
    parsed_replay = parse_replay_file(replay_path)
    
    if parsed_replay:
        # 分析回放
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
        
        print("\n=== 突变因子信息 ===")
        print(f"mutator_info type: {type(mutator_info)}")
        print(f"mutator_info: {mutator_info}")
        
        if 'mutators' in analysis_result:
            print(f"\nanalysis_result['mutators']: {analysis_result['mutators']}")
        if 'weekly' in analysis_result:
            print(f"analysis_result['weekly']: {analysis_result['weekly']}")
        
        print("\n=== 分析结果 ===")
        if analysis_result:
            print("analysis_result keys:")
            for k in sorted(analysis_result.keys()):
                print(f"  - {k}")
            
            if 'custom_kill_count' in analysis_result:
                print("\ncustom_kill_count:")
                print(json.dumps(analysis_result['custom_kill_count'], indent=2))
            else:
                print("\ncustom_kill_count not found in analysis_result")
                
            # 检查player_stats
            if 'player_stats' in analysis_result:
                print("\nplayer_stats structure:")
                for player_key, player_data in analysis_result['player_stats'].items():
                    print(f"  Player {player_key}:")
                    if isinstance(player_data, dict):
                        for k in sorted(player_data.keys()):
                            print(f"    - {k}")
                        if 'custom_kill_count' in player_data:
                            print(f"    custom_kill_count: {player_data['custom_kill_count']}")
            
            # 检查Icons
            for icon_type in ['mainIcons', 'allyIcons']:
                if icon_type in analysis_result:
                    print(f"\n{icon_type}:")
                    print(json.dumps(analysis_result[icon_type], indent=2))