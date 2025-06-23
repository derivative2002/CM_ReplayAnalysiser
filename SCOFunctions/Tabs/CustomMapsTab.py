from functools import partial
from typing import Any, Dict, List
from collections import defaultdict
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from SCOFunctions.MTheming import MColors
from SCOFunctions.MUserInterface import Cline, SortingQLabel


class CustomMapItemWidget(QtWidgets.QWidget):
    def __init__(self, map_name: str):
        super().__init__()
        self.map_name = map_name
        
        height = 22
        self.setGeometry(QtCore.QRect(0, 0, 931, 22))
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.bg = QtWidgets.QFrame(self)
        self.bg.setGeometry(QtCore.QRect(5, 0, 931, height + 1))
        self.bg.setAutoFillBackground(True)
        self.bg.setBackgroundRole(QtGui.QPalette.AlternateBase)
        self.bg.hide()

        self.name = QtWidgets.QLabel(map_name, self)
        self.name.setGeometry(QtCore.QRect(10, 0, 300, 20))
        
        self.count = QtWidgets.QLabel("0", self)
        self.count.setGeometry(QtCore.QRect(320, 0, 60, 20))
        self.count.setAlignment(QtCore.Qt.AlignCenter)
        
        self.wins = QtWidgets.QLabel("0", self)
        self.wins.setGeometry(QtCore.QRect(390, 0, 60, 20))
        self.wins.setAlignment(QtCore.Qt.AlignCenter)
        
        self.losses = QtWidgets.QLabel("0", self)
        self.losses.setGeometry(QtCore.QRect(450, 0, 60, 20))
        self.losses.setAlignment(QtCore.Qt.AlignCenter)
        
        self.winrate = QtWidgets.QLabel("0%", self)
        self.winrate.setGeometry(QtCore.QRect(510, 0, 60, 20))
        self.winrate.setAlignment(QtCore.Qt.AlignCenter)
        
        self.commanders = QtWidgets.QLabel("", self)
        self.commanders.setGeometry(QtCore.QRect(580, 0, 330, 20))
        
    def update_stats(self, count: int, wins: int, losses: int, common_commanders: List[str]):
        """更新自定义地图统计数据
        
        参数:
        count - 地图出现次数
        wins - 胜利次数
        losses - 失败次数
        common_commanders - 最常用的指挥官列表
        """
        self.count.setText(str(count))
        self.wins.setText(str(wins))
        self.losses.setText(str(losses))
        
        winrate = (wins / count * 100) if count > 0 else 0
        self.winrate.setText(f"{winrate:.1f}%")
        
        # 最多显示3个最常用指挥官
        self.commanders.setText(", ".join(common_commanders[:3]))
        
        # 根据胜率设置高亮颜色
        if winrate > 70:
            self.setStyleSheet(f"QLabel {{color: {MColors.game_weekly}}}")
        elif winrate < 40 and count > 5:
            self.setStyleSheet(f"QLabel {{color: {MColors.msg_failure}}}")
        elif count > 10:
            self.setStyleSheet(f"QLabel {{color: {MColors.player_highlight}}}")
        else:
            self.setStyleSheet("")


class CustomMapsTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.p = self
        self.map_widgets = {}
        self.total_custom_games = 0
        
        # 标签
        offset = 10
        
        self.name_label = SortingQLabel(self)
        self.name_label.setText("地图名称")
        self.name_label.setGeometry(QtCore.QRect(offset + 12, 4, 300, 20))
        self.name_label.setAlignment(QtCore.Qt.AlignLeft)
        self.name_label.activate()
        self.name_label.clicked.connect(partial(self.sort_maps, self.name_label))
        
        self.count_label = SortingQLabel(self, True)
        self.count_label.setText("游戏次数")
        self.count_label.setAlignment(QtCore.Qt.AlignCenter)
        self.count_label.setGeometry(QtCore.QRect(offset + 320, 4, 60, 20))
        self.count_label.clicked.connect(partial(self.sort_maps, self.count_label))
        
        self.wins_label = SortingQLabel(self, True)
        self.wins_label.setText("胜利")
        self.wins_label.setAlignment(QtCore.Qt.AlignCenter)
        self.wins_label.setGeometry(QtCore.QRect(offset + 390, 4, 60, 20))
        self.wins_label.clicked.connect(partial(self.sort_maps, self.wins_label))
        
        self.losses_label = SortingQLabel(self, True)
        self.losses_label.setText("失败")
        self.losses_label.setAlignment(QtCore.Qt.AlignCenter)
        self.losses_label.setGeometry(QtCore.QRect(offset + 450, 4, 60, 20))
        self.losses_label.clicked.connect(partial(self.sort_maps, self.losses_label))
        
        self.winrate_label = SortingQLabel(self, True)
        self.winrate_label.setText("胜率")
        self.winrate_label.setAlignment(QtCore.Qt.AlignCenter)
        self.winrate_label.setGeometry(QtCore.QRect(offset + 510, 4, 60, 20))
        self.winrate_label.clicked.connect(partial(self.sort_maps, self.winrate_label))
        
        self.commanders_label = QtWidgets.QLabel("常用指挥官", self)
        self.commanders_label.setGeometry(QtCore.QRect(offset + 580, 4, 330, 20))
        
        self.stats_label = QtWidgets.QLabel("自定义地图游戏总数: 0", self)
        self.stats_label.setGeometry(QtCore.QRect(offset + 700, 4, 200, 20))
        
        self.line = Cline(self)
        self.line.setGeometry(QtCore.QRect(5, 22, 941, 1))
        
        for item in (self.name_label, self.count_label, self.wins_label, self.losses_label, 
                    self.winrate_label, self.commanders_label, self.stats_label):
            item.setStyleSheet("QLabel {font-weight: bold}")
            
        # 滚动区域
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setGeometry(QtCore.QRect(0, 23, 970, 540))
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scroll_area.setWidgetResizable(True)
        
        self.scroll_area_content = QtWidgets.QWidget()
        self.scroll_area_content.setGeometry(QtCore.QRect(0, 0, 931, 561))
        
        self.scroll_area_contentLayout = QtWidgets.QVBoxLayout()
        self.scroll_area_contentLayout.setAlignment(QtCore.Qt.AlignTop)
        self.scroll_area_contentLayout.setContentsMargins(10, 0, 0, 0)
        
        # 收尾
        self.scroll_area_content.setLayout(self.scroll_area_contentLayout)
        self.scroll_area.setWidget(self.scroll_area_content)
    
    def update_data(self, maps_data: Dict[str, Dict[str, Any]]):
        """更新自定义地图统计数据
        
        参数:
        maps_data - 包含地图名称和统计数据的字典
        """
        self.total_custom_games = sum(data['count'] for data in maps_data.values())
        self.stats_label.setText(f"自定义地图游戏总数: {self.total_custom_games}")
        
        # 删除旧的控件
        for i in reversed(range(self.scroll_area_contentLayout.count())):
            self.scroll_area_contentLayout.itemAt(i).widget().setParent(None)
        
        # 创建新的控件
        self.map_widgets = {}
        for map_name, data in maps_data.items():
            self.map_widgets[map_name] = CustomMapItemWidget(map_name)
            self.map_widgets[map_name].update_stats(
                data['count'], 
                data['wins'], 
                data['losses'], 
                data['common_commanders']
            )
            self.scroll_area_contentLayout.addWidget(self.map_widgets[map_name])
            
        # 排序
        self.sort_maps(self.count_label, reverse=True)
    
    def sort_maps(self, clicked_label, reverse=False):
        """根据选定的列对地图列表排序
        
        参数:
        clicked_label - 被点击的标签
        reverse - 是否反向排序
        """
        # 停用所有标签
        for label in (self.name_label, self.count_label, self.wins_label, 
                     self.losses_label, self.winrate_label):
            if label != clicked_label:
                label.deactivate()
        
        # 更新排序方向
        clicked_label.change_direction()
        reverse = clicked_label.ascending
        
        # 确定排序标准
        def sortingf(item: CustomMapItemWidget):
            if clicked_label == self.name_label:
                return item.map_name
            elif clicked_label == self.count_label:
                return int(item.count.text())
            elif clicked_label == self.wins_label:
                return int(item.wins.text())
            elif clicked_label == self.losses_label:
                return int(item.losses.text())
            elif clicked_label == self.winrate_label:
                return float(item.winrate.text().replace('%', ''))
            return 0
        
        # 移除所有控件
        for i in reversed(range(self.scroll_area_contentLayout.count())):
            self.scroll_area_contentLayout.itemAt(i).widget().setParent(None)
        
        # 排序并重新添加控件
        sorted_widgets = sorted(self.map_widgets.values(), key=sortingf, reverse=reverse)
        for i, widget in enumerate(sorted_widgets):
            # 设置交替背景色
            if i % 2 == 0:
                widget.bg.hide()
            else:
                widget.bg.show()
            self.scroll_area_contentLayout.addWidget(widget)

    def analyze_custom_maps(self, replay_data):
        """分析自定义地图数据
        
        参数:
        replay_data - 包含所有回放数据的列表
        
        返回:
        maps_data - 包含地图名称和统计数据的字典
        """
        maps_data = {}
        commander_usage = defaultdict(lambda: defaultdict(int))
        
        # 打印一些调试信息
        print("开始分析自定义地图数据，总回放数量:", len(replay_data))
        
        # 检查第一个replay对象的结构
        if replay_data and len(replay_data) > 0:
            self.print_replay_structure(replay_data[0])
        
        # 获取官方地图列表
        official_maps = [
            "Chain of Ascension", "Dead of Night", "Lock & Load", "Malwarfare", 
            "Miner Evacuation", "Mist Opportunities", "Oblivion Express", 
            "Part and Parcel", "Rifts to Korhal", "Scythe of Amon", 
            "Temple of the Past", "The Vermillion Problem", "Void Launch", 
            "Void Thrashing", "Cradle of Death", "Void Sliver"
        ]
        
        # 自定义地图关键词
        custom_keywords = ['CM', 'cm', 'Custom', 'custom', 'MOD', 'mod', 'DIY', 'diy', '[CM]', '(CM)', 'CM_']
        
        # 分析回放数据，查找自定义地图
        custom_count = 0
        for i, replay in enumerate(replay_data):
            # 调试前10个回放以获取更多信息
            if i < 10:
                print(f"处理回放 {i+1} ...")
                if hasattr(replay, 'file'):
                    print(f"  文件路径: {replay.file}")
                    file_name = os.path.basename(replay.file)
                    print(f"  文件名: {file_name}")
                    # 检查文件名是否包含自定义地图关键词
                    has_custom_keyword = any(kw in file_name for kw in custom_keywords)
                    print(f"  文件名包含自定义地图关键词: {has_custom_keyword}")
            
            # 尝试不同的方式获取地图名称
            map_name = None
            
            # 1. 尝试从file属性获取文件名作为地图名称
            if hasattr(replay, 'file') and replay.file:
                file_path = replay.file
                file_name = os.path.basename(file_path)
                # 移除扩展名
                base_name = os.path.splitext(file_name)[0]
                
                # 检查文件名是否包含自定义地图关键词
                if any(kw in file_name for kw in custom_keywords):
                    map_name = base_name
                    if i < 10:
                        print(f"  通过文件名直接识别为自定义地图: {map_name}")
                        custom_count += 1
            
            # 2. 如果没有通过文件名识别，尝试常规属性
            if not map_name:
                # 尝试常规属性名
                map_name_attrs = ['map_name', 'map', 'mapName', 'name']
                for attr in map_name_attrs:
                    if hasattr(replay, attr):
                        map_name = getattr(replay, attr)
                        if i < 10:
                            print(f"  通过属性 {attr} 找到地图名称: {map_name}")
                        break
                
                # 如果还没找到，尝试从玩家信息中获取
                if not map_name and hasattr(replay, 'players'):
                    for p in replay.players:
                        if isinstance(p, dict) and 'map' in p:
                            map_name = p['map']
                            if i < 10:
                                print(f"  从玩家信息中找到地图名称: {map_name}")
                            break
            
            # 如果无法获取到地图名称，尝试使用文件名
            if not map_name and hasattr(replay, 'file') and replay.file:
                file_name = os.path.basename(replay.file)
                base_name = os.path.splitext(file_name)[0]
                map_name = base_name
                if i < 10:
                    print(f"  无法获取地图名称，使用文件名: {map_name}")
            
            # 如果依然无法获取地图名称，跳过此回放
            if not map_name:
                if i < 10:
                    print(f"  无法获取地图名称，跳过")
                continue
            
            # 转换为字符串，以防是其他类型
            map_name = str(map_name)
            
            # 检查是否是自定义地图
            is_custom = False
            
            # 检查地图名称
            if map_name not in official_maps:
                for kw in custom_keywords:
                    if kw in map_name:
                        is_custom = True
                        if i < 10:
                            print(f"  通过地图名称确认为自定义地图: {map_name}")
                        break
            
            # 如果地图名称不确定是自定义地图，检查文件名
            if not is_custom and hasattr(replay, 'file'):
                file_name = os.path.basename(replay.file)
                for kw in custom_keywords:
                    if kw in file_name:
                        is_custom = True
                        if i < 10:
                            print(f"  通过文件名确认为自定义地图: {map_name}")
                        break
            
            # 检查中文自定义地图关键词
            chinese_custom_keywords = ['聚铁成兵', '奇数偶数', '双倍压力', '净化者', '净化舰', '泰坦', '黑暗教堂']
            if not is_custom:
                # 检查地图名称是否包含中文自定义地图关键词
                for kw in chinese_custom_keywords:
                    if kw in map_name:
                        is_custom = True
                        if i < 10:
                            print(f"  通过中文关键词确认为自定义地图: {map_name}")
                        break
                
                # 检查文件名是否包含中文自定义地图关键词
                if not is_custom and hasattr(replay, 'file'):
                    file_name = os.path.basename(replay.file)
                    for kw in chinese_custom_keywords:
                        if kw in file_name:
                            is_custom = True
                            if i < 10:
                                print(f"  通过文件名中的中文关键词确认为自定义地图: {map_name}")
                            break
            
            # 如果是自定义地图，处理数据
            if is_custom:
                # 初始化该地图的数据
                if map_name not in maps_data:
                    maps_data[map_name] = {
                        'count': 0,
                        'wins': 0,
                        'losses': 0,
                        'common_commanders': []
                    }
                    print(f"发现新的自定义地图: {map_name}")
                
                # 更新计数
                maps_data[map_name]['count'] += 1
                
                # 更新胜负数据
                result = None
                if hasattr(replay, 'result'):
                    result = replay.result
                elif hasattr(replay, 'victory') and isinstance(replay.victory, bool):
                    result = 'Victory' if replay.victory else 'Defeat'
                
                if result:
                    if result == 'Victory':
                        maps_data[map_name]['wins'] += 1
                    else:
                        maps_data[map_name]['losses'] += 1
                
                # 统计指挥官使用情况
                if hasattr(replay, 'players'):
                    for p_idx in range(1, min(3, len(replay.players))):
                        commander = None
                        player = replay.players[p_idx]
                        
                        if isinstance(player, dict) and 'commander' in player:
                            commander = player['commander']
                        elif hasattr(player, 'commander'):
                            commander = player.commander
                        
                        if commander:
                            commander_usage[map_name][commander] += 1
        
        # 处理指挥官使用数据，找出每个地图最常用的指挥官
        for map_name in maps_data:
            common_commanders = sorted(
                commander_usage[map_name].items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            maps_data[map_name]['common_commanders'] = [cmd for cmd, _ in common_commanders]
        
        print(f"分析完成，找到 {len(maps_data)} 个自定义地图，总游戏次数: {sum(data['count'] for data in maps_data.values())}")
        if custom_count > 0 and len(maps_data) == 0:
            print(f"警告: 发现 {custom_count} 个可能的自定义地图文件，但没有被成功识别为自定义地图。")
            
        # 如果没有识别到自定义地图，但有自定义地图的文件名，强制添加
        if len(maps_data) == 0 and custom_count > 0:
            print("尝试强制识别自定义地图...")
            for i, replay in enumerate(replay_data):
                if hasattr(replay, 'file') and replay.file:
                    file_name = os.path.basename(replay.file)
                    base_name = os.path.splitext(file_name)[0]
                    
                    # 检查文件名是否包含自定义地图关键词
                    if any(kw in file_name for kw in custom_keywords) or any(kw in file_name for kw in chinese_custom_keywords):
                        if base_name not in maps_data:
                            maps_data[base_name] = {
                                'count': 1,
                                'wins': 1 if (hasattr(replay, 'result') and replay.result == 'Victory') else 0,
                                'losses': 1 if (hasattr(replay, 'result') and replay.result == 'Defeat') else 0,
                                'common_commanders': []
                            }
                            print(f"强制添加自定义地图: {base_name}")
            
            print(f"强制识别完成，现在有 {len(maps_data)} 个自定义地图")
        
        # 更新UI
        self.update_data(maps_data)
        
        return maps_data
        
    def print_replay_structure(self, replay, level=0, max_level=2):
        """打印replay对象的结构，帮助调试
        
        参数:
        replay - 要打印的对象
        level - 当前递归级别
        max_level - 最大递归级别
        """
        if level > max_level:
            return
            
        prefix = "  " * level
        
        if hasattr(replay, '__dict__'):
            print(f"{prefix}Object type: {type(replay).__name__}")
            for key, value in replay.__dict__.items():
                print(f"{prefix}  {key}: ", end="")
                if isinstance(value, (str, int, float, bool)) or value is None:
                    print(value)
                elif isinstance(value, (list, tuple)) and len(value) > 0:
                    print(f"[{len(value)} items]")
                    if level < max_level:
                        print(f"{prefix}    First item type: {type(value[0]).__name__}")
                        if level + 1 < max_level and hasattr(value[0], '__dict__'):
                            self.print_replay_structure(value[0], level + 2, max_level)
                elif isinstance(value, dict):
                    print(f"{{{len(value)} key-value pairs}}")
                    if level < max_level and len(value) > 0:
                        first_key = next(iter(value))
                        print(f"{prefix}    Example key: {first_key}, value type: {type(value[first_key]).__name__}")
                else:
                    print(f"Complex type: {type(value).__name__}")
        else:
            print(f"{prefix}Simple value: {replay}")
            
        if hasattr(replay, '__slots__'):
            print(f"{prefix}Slots: {', '.join(replay.__slots__)}")
            for slot in replay.__slots__:
                if hasattr(replay, slot):
                    value = getattr(replay, slot)
                    print(f"{prefix}  {slot}: ", end="")
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        print(value)
                    else:
                        print(f"Complex type: {type(value).__name__}") 