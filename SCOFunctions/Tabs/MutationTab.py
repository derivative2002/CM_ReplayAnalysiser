from functools import partial
from typing import Any, Dict

from PyQt5 import QtCore, QtGui, QtWidgets
from SCOFunctions.MainFunctions import show_overlay
from SCOFunctions.MTheming import MColors
from SCOFunctions.MUserInterface import Cline, SortingQLabel, find_file


class CustomMutatorWidget(QtWidgets.QWidget):
    def __init__(self, mutator_name: str):
        super().__init__()
        self.data = dict()
        self.mutator_name = mutator_name

        height = 22
        self.setGeometry(QtCore.QRect(0, 0, 931, 22))
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self.files = []
        self.file_iter = 0
        self.last_type = None

        self.bg = QtWidgets.QFrame(self)
        self.bg.setGeometry(QtCore.QRect(5, 0, 931, height + 1))
        self.bg.setAutoFillBackground(True)
        self.bg.setBackgroundRole(QtGui.QPalette.AlternateBase)
        self.bg.hide()

        self.name = QtWidgets.QLabel(mutator_name, self)
        self.name.setGeometry(QtCore.QRect(10, 0, 300, 20))

        self.wins = QtWidgets.QLabel(self)
        self.wins.setGeometry(QtCore.QRect(320, 0, 40, 20))
        self.wins.setAlignment(QtCore.Qt.AlignCenter)

        self.losses = QtWidgets.QLabel(self)
        self.losses.setGeometry(QtCore.QRect(370, 0, 40, 20))
        self.losses.setAlignment(QtCore.Qt.AlignCenter)

        self.winrate = QtWidgets.QLabel(self)
        self.winrate.setGeometry(QtCore.QRect(420, 0, 60, 20))
        self.winrate.setAlignment(QtCore.Qt.AlignCenter)

        self.games_count = QtWidgets.QLabel(self)
        self.games_count.setGeometry(QtCore.QRect(490, 0, 60, 20))
        self.games_count.setAlignment(QtCore.Qt.AlignCenter)

        self.overlay_btn = QtWidgets.QPushButton("Overlay", self)
        self.overlay_btn.setGeometry(QtCore.QRect(821, 0, 55, 22))
        self.overlay_btn.clicked.connect(lambda: show_overlay(self.get_file(1)))
        self.overlay_btn.hide()

        self.file_btn = QtWidgets.QPushButton("File", self)
        self.file_btn.setGeometry(QtCore.QRect(881, 0, 55, 22))
        self.file_btn.clicked.connect(lambda: find_file(self.get_file(2)))
        self.file_btn.hide()

    def get_file(self, type: int) -> str:
        """ Returns the next file to show"""
        if self.last_type == type:
            self.file_iter += 1
        else:
            self.last_type = type

        if len(self.files) == 0:
            return ""
        
        self.file_iter %= len(self.files)
        return self.files[self.file_iter]

    def update(self, mutator_data: Dict[str, Any]):
        """ Updates the mutator statistics
        Args:
            mutator_data: dictionary containing information about files, and W/L
        """
        self.data = mutator_data

        # Files & buttons
        self.files = mutator_data.get('files', [])
        if self.files:
            self.overlay_btn.show()
            self.file_btn.show()
        else:
            self.overlay_btn.hide()
            self.file_btn.hide()

        # Win/loss statistics
        wins = mutator_data.get('wins', 0)
        losses = mutator_data.get('losses', 0)
        total_games = wins + losses
        
        self.wins.setText(str(wins))
        self.losses.setText(str(losses))
        self.games_count.setText(str(total_games))
        
        if total_games > 0:
            winrate = wins / total_games
            self.winrate.setText(f"{winrate:.0%}")
        else:
            self.winrate.setText("N/A")


class MutationTab(QtWidgets.QWidget):
    def __init__(self, TabWidget):
        super().__init__()
        self.p = self
        self.custom_mutators: Dict[str, CustomMutatorWidget] = dict()

        # Main info label
        self.info_label = QtWidgets.QLabel("自定义突变统计 (Custom Mutator Statistics)", self)
        self.info_label.setGeometry(QtCore.QRect(20, 10, 400, 30))
        self.info_label.setStyleSheet("QLabel {font-size: 14px; font-weight: bold; color: #4CAF50;}")

        self.description_label = QtWidgets.QLabel("显示在自定义地图中遇到的突变器统计信息", self)
        self.description_label.setGeometry(QtCore.QRect(20, 35, 500, 20))
        self.description_label.setStyleSheet("QLabel {color: #888888;}")

        # Column headers
        offset = 10
        header_y = 70

        self.name_header = SortingQLabel(self)
        self.name_header.setText("突变器名称 (Mutator Name)")
        self.name_header.setGeometry(QtCore.QRect(offset + 12, header_y, 280, 20))
        self.name_header.setAlignment(QtCore.Qt.AlignLeft)
        self.name_header.activate()
        self.name_header.clicked.connect(partial(self.sort_mutators, self.name_header))

        self.wins_header = SortingQLabel(self, True)
        self.wins_header.setText("胜利")
        self.wins_header.setAlignment(QtCore.Qt.AlignCenter)
        self.wins_header.setGeometry(QtCore.QRect(offset + 320, header_y, 40, 20))
        self.wins_header.clicked.connect(partial(self.sort_mutators, self.wins_header))

        self.losses_header = SortingQLabel(self, True)
        self.losses_header.setText("失败")
        self.losses_header.setAlignment(QtCore.Qt.AlignCenter)
        self.losses_header.setGeometry(QtCore.QRect(offset + 370, header_y, 40, 20))
        self.losses_header.clicked.connect(partial(self.sort_mutators, self.losses_header))

        self.winrate_header = SortingQLabel(self, True)
        self.winrate_header.setText("胜率")
        self.winrate_header.setGeometry(QtCore.QRect(offset + 420, header_y, 60, 20))
        self.winrate_header.setAlignment(QtCore.Qt.AlignCenter)
        self.winrate_header.clicked.connect(partial(self.sort_mutators, self.winrate_header))

        self.games_header = SortingQLabel(self, True)
        self.games_header.setText("总局数")
        self.games_header.setAlignment(QtCore.Qt.AlignCenter)
        self.games_header.setGeometry(QtCore.QRect(offset + 490, header_y, 60, 20))
        self.games_header.clicked.connect(partial(self.sort_mutators, self.games_header))

        # Style headers
        for header in (self.name_header, self.wins_header, self.losses_header, self.winrate_header, self.games_header):
            header.setStyleSheet("QLabel {font-weight: bold}")

        self.line = Cline(self)
        self.line.setGeometry(QtCore.QRect(5, header_y + 22, 941, 1))

        # Scroll area
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setGeometry(QtCore.QRect(0, header_y + 25, TabWidget.frameGeometry().width() - 5, TabWidget.frameGeometry().height() - header_y - 50))
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area_content = QtWidgets.QWidget()
        self.scroll_area_content.setGeometry(QtCore.QRect(0, 0, 931, 400))

        self.scroll_area_contentLayout = QtWidgets.QVBoxLayout()
        self.scroll_area_contentLayout.setAlignment(QtCore.Qt.AlignTop)
        self.scroll_area_contentLayout.setContentsMargins(10, 0, 0, 0)

        # Finishing
        self.scroll_area_content.setLayout(self.scroll_area_contentLayout)
        self.scroll_area.setWidget(self.scroll_area_content)

        # Placeholder for when no data is available
        self.no_data_label = QtWidgets.QLabel("暂无自定义突变数据", self.scroll_area_content)
        self.no_data_label.setAlignment(QtCore.Qt.AlignCenter)
        self.no_data_label.setStyleSheet("QLabel {color: #666666; font-size: 12px;}")
        self.scroll_area_contentLayout.addWidget(self.no_data_label)

    def update_data(self, custom_mutator_data):
        """Update the tab with custom mutator statistics"""
        # Clear existing widgets
        for mutator_name, widget in self.custom_mutators.items():
            self.scroll_area_contentLayout.removeWidget(widget)
            widget.deleteLater()
        self.custom_mutators.clear()

        # Hide no data label if we have data
        if custom_mutator_data:
            self.no_data_label.hide()
            
            # Create widgets for each custom mutator
            for mutator_name, mutator_stats in custom_mutator_data.items():
                widget = CustomMutatorWidget(mutator_name)
                widget.update(mutator_stats)
                self.custom_mutators[mutator_name] = widget
                self.scroll_area_contentLayout.addWidget(widget)
            
            self.sort_mutators(self.name_header)
        else:
            self.no_data_label.show()

    def sort_mutators(self, caller):
        """Sort the mutator widgets based on the selected column"""
        if type(caller) is SortingQLabel:
            caller.activate()

        if not self.custom_mutators:
            return

        sort_by = SortingQLabel.active[self].value
        reverse = SortingQLabel.active[self].reverse
        widgets = list(self.custom_mutators.values())

        # Remove widgets from layout
        for widget in widgets:
            self.scroll_area_contentLayout.removeWidget(widget)

        # Sort widgets
        def sortingf(item: CustomMutatorWidget):
            if sort_by == "突变器名称 (Mutator Name)":
                return item.mutator_name
            elif sort_by == "胜利":
                return item.data.get('wins', 0)
            elif sort_by == "失败":
                return item.data.get('losses', 0)
            elif sort_by == "胜率":
                wins = item.data.get('wins', 0)
                losses = item.data.get('losses', 0)
                total = wins + losses
                return wins / total if total > 0 else 0
            elif sort_by == "总局数":
                return item.data.get('wins', 0) + item.data.get('losses', 0)
            return 0

        widgets = sorted(widgets, key=sortingf, reverse=reverse)

        # Add widgets back to layout and update backgrounds
        for i, widget in enumerate(widgets):
            self.scroll_area_contentLayout.addWidget(widget)
            widget.bg.show() if i % 2 else widget.bg.hide()
