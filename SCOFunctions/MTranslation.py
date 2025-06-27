"""
Translation module for SC2 Coop Overlay.
Contains functions for loading language packs and translating UI text.
"""

import json
import os
from SCOFunctions.MFilePath import innerPath
from SCOFunctions.MLogging import Logger

logger = Logger('Translation', Logger.levels.INFO)

# 当前语言和翻译字典
current_language = 'zh_CN'
translations = {}

def load_translation(language_code):
    """
    从JSON文件加载指定语言的翻译
    
    参数:
    language_code - 语言代码 (如 'zh_CN', 'en_US')
    
    返回:
    bool - 是否成功加载
    """
    global translations
    
    try:
        # 构建语言文件路径
        lang_file = innerPath(f'src/{language_code}.json')
        
        # 检查文件是否存在
        if not os.path.exists(lang_file):
            logger.error(f"Language file not found: {lang_file}")
            return False
            
        # 加载JSON文件
        with open(lang_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            
        logger.info(f"Loaded language pack: {language_code}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load language pack {language_code}: {str(e)}")
        return False

def set_language(language_code):
    """
    设置当前语言
    
    参数:
    language_code - 语言代码 (如 'zh_CN', 'en_US')
    
    返回:
    bool - 是否成功设置
    """
    global current_language
    
    if load_translation(language_code):
        current_language = language_code
        return True
    return False

def get_current_language():
    """
    获取当前语言代码
    
    返回:
    str - 当前语言代码
    """
    return current_language

def translate(text):
    """
    翻译文本
    如果翻译映射表中没有对应的翻译，则返回原始文本
    
    参数:
    text - 要翻译的文本
    
    返回:
    str - 翻译后的文本
    """
    # 如果没有加载翻译，尝试加载默认语言
    if not translations:
        load_translation(current_language)
        
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
        if isinstance(current_text, str):
            translated = translate(current_text)
            if translated != current_text:  # 只在有翻译时更新
                getattr(widget, f'set{attribute.capitalize()}')(translated)
    
def translate_tooltip(widget):
    """
    翻译控件的工具提示
    """
    if hasattr(widget, 'toolTip'):
        tooltip = widget.toolTip()
        if tooltip:
            translated = translate(tooltip)
            if translated != tooltip:  # 只在有翻译时更新
                widget.setToolTip(translated)
            
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

# 初始化时加载默认语言
load_translation(current_language) 