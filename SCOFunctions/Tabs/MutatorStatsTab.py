from functools import partial
from typing import Any, Dict

from PyQt5 import QtCore, QtGui, QtWidgets
from SCOFunctions.MTheming import MColors
from SCOFunctions.MUserInterface import Cline, SortingQLabel
from SCOFunctions.SC2Dictionaries import Mutators


class MutatorItemWidget(QtWidgets.QWidget):
    def __init__(self, mutator_name: str):
        super().__init__()
        self.mutator_name = mutator_name
        self.description = Mutators.get(mutator_name, "")
        
        height = 22
        self.setGeometry(QtCore.QRect(0, 0, 931, 22))
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.bg = QtWidgets.QFrame(self)
        self.bg.setGeometry(QtCore.QRect(5, 0, 931, height + 1))
        self.bg.setAutoFillBackground(True)
        self.bg.setBackgroundRole(QtGui.QPalette.AlternateBase)
        self.bg.hide()

        self.name = QtWidgets.QLabel(mutator_name, self)
        self.name.setGeometry(QtCore.QRect(10, 0, 300, 20))
        
        self.count = QtWidgets.QLabel("0", self)
        self.count.setGeometry(QtCore.QRect(320, 0, 60, 20))
        self.count.setAlignment(QtCore.Qt.AlignCenter)
        
        self.percentage = QtWidgets.QLabel("0%", self)
        self.percentage.setGeometry(QtCore.QRect(390, 0, 60, 20))
        self.percentage.setAlignment(QtCore.Qt.AlignCenter)
        
        self.description_label = QtWidgets.QLabel(self.description[:100] + ("..." if len(self.description) > 100 else ""), self)
        self.description_label.setGeometry(QtCore.QRect(460, 0, 450, 20))
        
    def update_stats(self, count: int, total: int):
        """更新突变因子统计数据
        
        参数:
        count - 突变因子出现次数
        total - 所有带突变因子的游戏总数
        """
        self.count.setText(str(count))
        percentage = (count / total * 100) if total > 0 else 0
        self.percentage.setText(f"{percentage:.1f}%")
        
        # 根据出现频率设置高亮颜色
        if percentage > 30:
            self.setStyleSheet(f"QLabel {{color: {MColors.game_weekly}}}")
        elif percentage > 15:
            self.setStyleSheet(f"QLabel {{color: {MColors.player_highlight}}}")
        else:
            self.setStyleSheet("")


class MutatorStatsTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.p = self
        self.mutator_widgets = {}
        self.total_mutation_games = 0
        
        # 标签
        offset = 10
        
        self.name_label = SortingQLabel(self)
        self.name_label.setText("突变因子")
        self.name_label.setGeometry(QtCore.QRect(offset + 12, 4, 300, 20))
        self.name_label.setAlignment(QtCore.Qt.AlignLeft)
        self.name_label.activate()
        self.name_label.clicked.connect(partial(self.sort_mutators, self.name_label))
        
        self.count_label = SortingQLabel(self, True)
        self.count_label.setText("出现次数")
        self.count_label.setAlignment(QtCore.Qt.AlignCenter)
        self.count_label.setGeometry(QtCore.QRect(offset + 320, 4, 60, 20))
        self.count_label.clicked.connect(partial(self.sort_mutators, self.count_label))
        
        self.percentage_label = SortingQLabel(self, True)
        self.percentage_label.setText("出现比例")
        self.percentage_label.setAlignment(QtCore.Qt.AlignCenter)
        self.percentage_label.setGeometry(QtCore.QRect(offset + 390, 4, 60, 20))
        self.percentage_label.clicked.connect(partial(self.sort_mutators, self.percentage_label))
        
        self.description_label = QtWidgets.QLabel("描述", self)
        self.description_label.setGeometry(QtCore.QRect(offset + 460, 4, 450, 20))
        
        self.stats_label = QtWidgets.QLabel("突变游戏总数: 0", self)
        self.stats_label.setGeometry(QtCore.QRect(offset + 700, 4, 200, 20))
        
        self.line = Cline(self)
        self.line.setGeometry(QtCore.QRect(5, 22, 941, 1))
        
        for item in (self.name_label, self.count_label, self.percentage_label, self.description_label, self.stats_label):
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
        
        # 创建所有突变因子控件
        mutator_list = sorted(list(Mutators.keys()))
        for mutator_name in mutator_list:
            if mutator_name != "Random" and mutator_name != "BlizzCon Challenge":
                self.mutator_widgets[mutator_name] = MutatorItemWidget(mutator_name)
                self.scroll_area_contentLayout.addWidget(self.mutator_widgets[mutator_name])
    
    def update_data(self, mutator_stats: Dict[str, int], total_games: int):
        """更新突变因子统计数据
        
        参数:
        mutator_stats - 包含突变因子名称和出现次数的字典
        total_games - 所有带突变因子的游戏总数
        """
        self.total_mutation_games = total_games
        self.stats_label.setText(f"突变游戏总数: {total_games}")
        
        # 更新每个突变因子的统计数据
        for mutator_name, widget in self.mutator_widgets.items():
            count = mutator_stats.get(mutator_name, 0)
            widget.update_stats(count, total_games)
            
        # 排序
        self.sort_mutators(self.count_label, reverse=True)
    
    def sort_mutators(self, clicked_label, reverse=False):
        """根据选定的列对突变因子列表排序
        
        参数:
        clicked_label - 被点击的标签
        reverse - 是否反向排序
        """
        # 停用所有标签
        for label in (self.name_label, self.count_label, self.percentage_label):
            if label != clicked_label:
                label.deactivate()
        
        # 更新排序方向
        clicked_label.change_direction()
        reverse = clicked_label.ascending
        
        # 确定排序标准
        def sortingf(item: MutatorItemWidget):
            if clicked_label == self.name_label:
                return item.mutator_name
            elif clicked_label == self.count_label:
                return int(item.count.text())
            elif clicked_label == self.percentage_label:
                return float(item.percentage.text().replace('%', ''))
            return 0
        
        # 移除所有控件
        for i in reversed(range(self.scroll_area_contentLayout.count())):
            self.scroll_area_contentLayout.itemAt(i).widget().setParent(None)
        
        # 排序并重新添加控件
        sorted_widgets = sorted(self.mutator_widgets.values(), key=sortingf, reverse=reverse)
        for i, widget in enumerate(sorted_widgets):
            # 设置交替背景色
            if i % 2 == 0:
                widget.bg.hide()
            else:
                widget.bg.show()
            self.scroll_area_contentLayout.addWidget(widget)

    def calculate_mutator_stats(self, replay_data):
        """计算所有突变因子的出现频率
        
        参数:
        replay_data - 包含所有回放数据的列表
        
        返回:
        (mutator_stats, total_games) - 突变因子统计数据和总游戏数
        """
        mutator_stats = {}
        total_games = 0
        
        # 统计每个突变因子出现的次数
        for replay in replay_data:
            if hasattr(replay, 'mutators') and replay.mutators:
                total_games += 1
                for mutator in replay.mutators:
                    if mutator in mutator_stats:
                        mutator_stats[mutator] += 1
                    else:
                        mutator_stats[mutator] = 1
        
        self.update_data(mutator_stats, total_games)
        return mutator_stats, total_games 