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
        # 导出overlay翻译
        export_overlay_translations(language_code)
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

def export_overlay_translations(language_code):
    """
    导出overlay需要的翻译到JSON文件
    
    参数:
    language_code - 语言代码 (如 'zh_CN', 'en_US')
    """
    try:
        # 创建overlay翻译字典
        overlay_translations = {}
        
        # 从主翻译文件中导出所有翻译
        if translations:
            # 添加所有翻译
            overlay_translations.update(translations)
            
            # 从MTranslation_Extra.py中导入额外的翻译
            try:
                from SCOFunctions.MTranslation_Extra import commander_translations, prestige_translations, map_translations
                
                # 如果主翻译文件中没有这些翻译，则添加
                for commander, translation in commander_translations.items():
                    if commander not in overlay_translations:
                        overlay_translations[commander] = translation
                
                for prestige, translation in prestige_translations.items():
                    if prestige not in overlay_translations:
                        overlay_translations[prestige] = translation
                
                for map_name, translation in map_translations.items():
                    if map_name not in overlay_translations:
                        overlay_translations[map_name] = translation
                        
                logger.info("Added extra translations from MTranslation_Extra.py")
            except ImportError:
                logger.warning("MTranslation_Extra.py not found, skipping extra translations")
            
            # 添加指挥官精通翻译
            # 这部分需要特殊处理，因为它们是以数组形式在JS中使用的
            mastery_translations = generate_mastery_translations()
            if mastery_translations:
                overlay_translations["__mastery__"] = mastery_translations
                logger.info("Added mastery translations")
            
            # 添加特殊单位翻译
            special_units = {
                'Slayer': '收割者',
                'Legionnaire': '军团兵',
                'Hybrid': '混合体'
            }
            for unit, translation in special_units.items():
                if unit not in overlay_translations:
                    overlay_translations[unit] = translation
            
            # 输出到JSON文件
            output_path = innerPath(f'Layouts/overlay_{language_code}.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(overlay_translations, f, ensure_ascii=False, indent=4)
                
            logger.info(f"Exported overlay translations to {output_path}")
            return True
        else:
            logger.error("No translations loaded, cannot export")
            return False
            
    except Exception as e:
        logger.error(f"Failed to export overlay translations: {str(e)}")
        return False

def generate_mastery_translations():
    """
    生成指挥官精通的翻译
    
    返回:
    dict - 指挥官精通翻译字典
    """
    # 这里我们可以从zh_CN.json中提取精通翻译
    # 或者直接硬编码，因为这些翻译不太可能改变
    # 为了简化，这里我们直接返回硬编码的翻译
    
    return {
        'Abathur': ['毒气巢伤害', '修复治疗持续时间', '共生体能力改进', '双倍生物质概率', '毒气巢最大充能和冷却时间', '建筑形态变化和进化速度'],
        'Alarak': ['阿拉纳克攻击伤害', '作战单位攻击速度', '强化我持续时间', '死亡舰队冷却时间', '建筑超载护盾和攻击速度', '时空加速效率'],
        'Artanis': ['护盾过载持续时间和伤害吸收', '守护之壳生命和护盾恢复', '能量再生和冷却时间减少', '折跃单位速度提升', '时空加速效率', '艾杜恩之矛初始和最大能量'],
        'Dehaka': ['吞噬治疗增强', '吞噬增益持续时间', '大型原始蠕虫冷却时间', '群体首领活跃时间', '基因突变概率', '德哈卡攻击速度'],
        'Fenix': ['菲尼克斯战衣攻击速度', '菲尼克斯战衣离线能量恢复', '冠军AI攻击速度', '冠军AI生命和护盾', '时空加速效率', '额外起始人口'],
        'Horner': ['攻击战机范围效果', '更强死亡概率', '重要他人加成', '双倍打捞概率', '空中舰队飞行距离', '磁矿装填、冷却和启动时间'],
        'Karax': ['作战单位生命和护盾', '建筑生命和护盾', '修复光束治疗速率', '时空波能量生成', '时空加速效率', '艾杜恩之矛初始和最大能量'],
        'Kerrigan': ['凯瑞甘能量再生', '凯瑞甘攻击伤害', '作战单位瓦斯消耗', '增强型定身波', '快速进化', '主要技能伤害和攻击速度'],
        'Nova': ['核弹和全息诱饵冷却时间', '狮鹫空袭费用', '诺娃主要技能改进', '作战单位攻击速度', '诺娃能量再生', '单位生命再生'],
        'Raynor': ['研究资源消耗', '空投舱单位速度提升', '休伯利安冷却时间', '女妖空袭冷却时间', '医疗兵治疗额外目标', '机械单位攻击速度'],
        'Stetmann': ['升级资源消耗', '盖里技能冷却时间', '斯泰特区域加成', '最大精神能量池', '部署斯泰特卫星冷却时间', '建筑形态变化速率'],
        'Stukov': ['易爆感染体生成概率', '感染建筑冷却时间', '亚历山大号冷却时间', '启示录兽冷却时间', '感染步兵持续时间', '机械单位攻击速度'],
        'Swann': ['聚焦光束宽度和伤害', '战斗空投持续时间和生命', '不朽协议成本和建造时间', '建筑生命值', '瓦斯无人机成本', '激光钻机建造时间、升级时间和升级成本'],
        'Tychus': ['泰凯斯攻击速度', '泰凯斯粉碎手雷冷却时间', '三重歹徒研究改进', '歹徒可用性', '医疗运输机接载冷却时间', '奥丁冷却时间'],
        'Vorazun': ['黑暗水晶塔能量再生', '时间停止持续时间', '暗影守卫持续时间', '黑洞持续时间', '时空加速效率', '裂隙生成冷却时间'],
        'Zagara': ['扎加拉伤害和生命', '作战单位伤害和生命', '孵化速度', '腐化者喷吐冷却时间', '血蜂损失时产生蟑螂', '幼虫孵化数量'],
        'Zeratul': ['神器碎片加成', '泽拉图攻击速度', '传奇军团冷却时间', '作战单位攻击速度', '预言者回避', '虚空裂隙冷却时间'],
        'Mengsk': ['皇家卫队伤害', '皇家卫队生命值', '帝国武器攻击速度', '帝国武器生命值', '皇家学院研究时间', '帝国支援冷却时间']
    }

# 初始化时加载默认语言
load_translation(current_language) 