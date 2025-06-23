"""
Translation module for SC2 Coop Overlay.
Contains functions and dictionaries for translating UI text.
"""

# 英文到中文的翻译映射表
translations = {
    # 通用按钮和标签
    "Apply": "应用",
    "Reset": "重置",
    "Cancel": "取消",
    "OK": "确定",
    "Yes": "是",
    "No": "否",
    "Save": "保存",
    "Delete": "删除",
    "Close": "关闭",
    
    # MainTab
    "Start with Windows": "开机启动",
    "Start minimized": "启动时最小化",
    "Enable logging": "启用日志",
    "Show session stats": "显示会话统计",
    "Show player winrates and notes": "显示玩家胜率和笔记",
    "Minimize to tray": "最小化到托盘",
    "Duration": "持续时间",
    "Monitor": "显示器",
    "Show charts": "显示图表",
    "Dark theme": "暗色主题",
    "Fast expand hints": "快速扩张提示",
    "Don't show overlay on-screen": "不在屏幕上显示覆盖层",
    "Change locations of StarCraft II account folder and screenshot folder": "更改星际争霸II账户文件夹和截图文件夹位置",
    "Account folder": "账户文件夹",
    "Screenshot folder": "截图文件夹",
    "Overlay screenshot": "覆盖层截图",
    "Create desktop shortcut": "创建桌面快捷方式",
    "Hotkeys": "热键",
    "Show / Hide": "显示/隐藏",
    "Show": "显示",
    "Hide": "隐藏",
    "Show newer replay": "显示较新回放",
    "Show older replay": "显示较旧回放",
    "Show player info": "显示玩家信息",
    
    # StatsTab
    "Statistics": "统计数据",
    "Main players:": "主要玩家:",
    "Games found:": "找到的游戏:",
    "Full analysis": "完整分析",
    "Run full analysis": "运行完整分析",
    "Stop analysis": "停止分析",
    "Full analysis at start": "启动时进行完整分析",
    "Status:": "状态:",
    "Dump all": "导出全部",
    "Loading...": "加载中...",
    
    # GameTab
    "Games": "游戏",
    "Wins": "胜利",
    "Losses": "失败",
    "Winrate": "胜率",
    "Bonus": "奖励",
    "Duration": "持续时间",
    "Player 1": "玩家 1",
    "Player 2": "玩家 2",
    "Commander": "指挥官",
    "Map": "地图",
    "Result": "结果",
    "Victory": "胜利",
    "Defeat": "失败",
    
    # PlayerTab
    "Players": "玩家",
    "Handle": "游戏ID",
    "Games": "游戏",
    "Note": "笔记",
    "Add note": "添加笔记",
    
    # ResourceTab
    "Performance": "性能",
    "Show performance overlay": "显示性能覆盖层",
    "Change overlay position": "更改覆盖层位置",
    "Fix overlay position": "固定覆盖层位置",
    "Processes to monitor": "监控进程",
    
    # RngTab
    "Randomizer": "随机器",
    "Randomize": "随机选择",
    "Commander selection": "指挥官选择",
    "Show on overlay": "在覆盖层上显示",
    "Include prestiges": "包括声望",
    "Custom pool": "自定义池",
    "All": "全部",
    
    # MutationTab
    "Weeklies": "每周突变",
    "Mutation": "突变",
    
    # LinkTab
    "Links": "链接",
    
    # 工具提示
    "The app will start automatically with Windows": "应用程序将随Windows自动启动",
    "The app will start minimized": "应用程序将以最小化状态启动",
    "App logs will be saved into a text file": "应用程序日志将保存到文本文件中",
    "Shows how many games you played and won in the current session on the overlay": "在覆盖层上显示当前会话中您玩过和赢得的游戏数量",
    "The number of games and winrate you had with your ally will be shown when a game starts.\nPlayer note will show as well if specified. Requires restart to enable.": "游戏开始时将显示您与盟友一起进行的游戏次数和胜率。\n如果指定了玩家笔记，也会显示。需要重新启动才能启用。",
    "On closing the app will minimize to tray. The app can be closed there.": "关闭时应用程序将最小化到托盘。可以在那里关闭应用程序。",
    "How long the overlay will show after a new game is analysed.": "在分析新游戏后覆盖层显示的时间长度。",
    "Determines on which monitor the overlay will be shown": "确定覆盖层将在哪个显示器上显示",
    "Show charts on overlay": "在覆盖层上显示图表",
    "Enables dark theme. Requires restart!": "启用暗色主题。需要重新启动！",
    "The overlay won't show directly on your screen. You can use this setting\nfor example when it's meant to be visible only on stream.": "覆盖层不会直接在屏幕上显示。您可以使用此设置\n例如当它只在直播中可见时。",
    "Choose your account folder.\nThis is usually not necessary and the app will find its location automatically.": "选择您的账户文件夹。\n通常不需要这样做，应用程序会自动找到其位置。",
    "Choose the folder where screenshots are saved": "选择保存截图的文件夹",
    "Take screenshot of the overlay and save it on your desktop or chosen location": "拍摄覆盖层的截图并将其保存到桌面或选择的位置",
    "Resets all settings on this tab apart from login for starcraft2coop.com": "重置此标签上除starcraft2coop.com登录外的所有设置",
    
    # 应用程序标题和标签页
    "StarCraft Co-op Overlay": "星际争霸II 合作模式覆盖层",
    "Settings": "设置",
    "SC2 Coop Overlay": "星际争霸II合作模式覆盖层",
    
    # 信息和状态消息
    "Settings applied": "已应用设置",
    "Warning: Overlapping hotkeys!": "警告：热键重叠！",
    "Permission denied. Add an exception to your anti-virus for this folder. Sorry": "权限被拒绝。请为此文件夹添加杀毒软件例外。很抱歉",
    "New version available!": "有新版本可用！",
    "Download update": "下载更新",
    "Downloading": "正在下载",
    "Restart and update": "重启并更新",
    "Error! Incorrect hash for the downloaded archive.": "错误！下载的归档文件哈希值不正确。",
    "Installation will start shortly...": "安装即将开始...",
    "Installation completed...": "安装完成...",
}

def translate(text):
    """
    将文本从英文翻译为中文
    如果翻译映射表中没有对应的翻译，则返回原始文本
    """
    return translations.get(text, text)

def tr(widget, attribute='text'):
    """
    翻译控件的文本属性
    
    参数:
    widget - 要翻译的控件
    attribute - 包含文本的属性名称 (默认: 'text')
    """
    if hasattr(widget, attribute):
        current_text = getattr(widget, attribute)()
        if isinstance(current_text, str) and current_text in translations:
            getattr(widget, f'set{attribute.capitalize()}')(translations[current_text])
    
def translate_tooltip(widget):
    """
    翻译控件的工具提示
    """
    if hasattr(widget, 'toolTip'):
        tooltip = widget.toolTip()
        if tooltip in translations:
            widget.setToolTip(translations[tooltip])
            
def translate_widget_recursive(widget):
    """
    递归翻译小部件及其所有子部件
    
    参数:
    widget - 要翻译的父部件
    """
    # 翻译当前部件的文本和工具提示
    tr(widget)
    translate_tooltip(widget)
    
    # 如果部件有子部件，递归翻译所有子部件
    if hasattr(widget, 'children'):
        for child in widget.children():
            # 如果子部件是QObject的子类（所有UI控件都是），则尝试翻译
            from PyQt5.QtCore import QObject
            if isinstance(child, QObject):
                translate_widget_recursive(child) 