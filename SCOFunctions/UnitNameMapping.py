"""
Unit name mapping for StarCraft II units
Maps English unit names to Chinese translations
"""

from SCOFunctions.MTranslation import translate

# Create a comprehensive unit name mapping
UNIT_NAME_MAPPING = {
    # Terran Units
    "Marine": "陆战队员",
    "Marauder": "掠夺者",
    "Reaper": "死神",
    "Ghost": "幽灵",
    "Hellion": "恶火",
    "Hellbat": "烈焰车",
    "SiegeTank": "攻城坦克",
    "Siege Tank": "攻城坦克",
    "SiegeTankSieged": "攻城坦克(架起)",
    "Thor": "雷神",
    "Viking": "维京战机",
    "VikingAssault": "维京战机(地面)",
    "VikingFighter": "维京战机(空中)",
    "Medivac": "医疗运输机",
    "Liberator": "解放者",
    "LiberatorAG": "解放者(防守模式)",
    "Raven": "渡鸦",
    "Banshee": "女妖",
    "Battlecruiser": "战列巡航舰",
    "SCV": "SCV",
    "MULE": "矿骡",
    "WidowMine": "寡妇雷",
    "WidowMineBurrowed": "寡妇雷(潜地)",
    "Cyclone": "旋风",
    
    # Protoss Units
    "Probe": "探机",
    "Zealot": "狂热者",
    "Stalker": "追猎者",
    "Sentry": "哨兵",
    "Adept": "使徒",
    "HighTemplar": "高阶圣堂武士",
    "High Templar": "高阶圣堂武士",
    "DarkTemplar": "黑暗圣堂武士",
    "Dark Templar": "黑暗圣堂武士",
    "Archon": "执政官",
    "Immortal": "不朽者",
    "Colossus": "巨像",
    "Disruptor": "干扰者",
    "Observer": "观察者",
    "WarpPrism": "折跃棱镜",
    "Warp Prism": "折跃棱镜",
    "WarpPrismPhasing": "折跃棱镜(相位模式)",
    "Phoenix": "凤凰",
    "VoidRay": "虚空辉光舰",
    "Void Ray": "虚空辉光舰",
    "Oracle": "先知",
    "Tempest": "风暴战舰",
    "Carrier": "航母",
    "Mothership": "母舰",
    "MothershipCore": "母舰核心",
    "Interceptor": "截击机",
    
    # Zerg Units
    "Larva": "幼虫",
    "Drone": "工蜂",
    "Overlord": "领主",
    "Overseer": "监察王虫",
    "Queen": "女王",
    "Zergling": "跳虫",
    "Baneling": "毒爆虫",
    "BanelingBurrowed": "毒爆虫(潜地)",
    "Roach": "蟑螂",
    "RoachBurrowed": "蟑螂(潜地)",
    "Ravager": "破坏者",
    "Hydralisk": "刺蛇",
    "HydraliskBurrowed": "刺蛇(潜地)",
    "Lurker": "潜伏者",
    "LurkerBurrowed": "潜伏者(潜地)",
    "LurkerMPBurrowed": "潜伏者(潜地)",
    "Infestor": "感染虫",
    "InfestorBurrowed": "感染虫(潜地)",
    "SwarmHost": "虫群宿主",
    "Swarm Host": "虫群宿主",
    "SwarmHostBurrowed": "虫群宿主(潜地)",
    "Locust": "蝗虫",
    "Mutalisk": "飞龙",
    "Corruptor": "腐化者",
    "BroodLord": "巢虫领主",
    "Brood Lord": "巢虫领主",
    "Broodling": "幼虫",
    "Viper": "飞蛇",
    "Ultralisk": "雷兽",
    "UltraliskBurrowed": "雷兽(潜地)",
    "Changeling": "变形虫",
    "ChangelingZealot": "变形虫(狂热者)",
    "ChangelingMarine": "变形虫(陆战队员)",
    "ChangelingZergling": "变形虫(跳虫)",
    "InfestedTerran": "被感染的人类",
    "Infested Terran": "被感染的人类",
    
    # Buildings - Terran
    "CommandCenter": "指挥中心",
    "Command Center": "指挥中心",
    "OrbitalCommand": "轨道指挥部",
    "Orbital Command": "轨道指挥部",
    "PlanetaryFortress": "行星要塞",
    "Planetary Fortress": "行星要塞",
    "SupplyDepot": "补给站",
    "Supply Depot": "补给站",
    "SupplyDepotLowered": "补给站(降下)",
    "Refinery": "精炼厂",
    "Barracks": "兵营",
    "Factory": "重工厂",
    "Starport": "星港",
    "EngineeringBay": "工程站",
    "Engineering Bay": "工程站",
    "Armory": "军械库",
    "Bunker": "地堡",
    "MissileTurret": "导弹塔",
    "Missile Turret": "导弹塔",
    "SensorTower": "感应塔",
    "Sensor Tower": "感应塔",
    "TechLab": "科技实验室",
    "Tech Lab": "科技实验室",
    "Reactor": "反应堆",
    "GhostAcademy": "幽灵学院",
    "Ghost Academy": "幽灵学院",
    "FusionCore": "聚变核心",
    "Fusion Core": "聚变核心",
    
    # Buildings - Protoss
    "Nexus": "星灵枢纽",
    "Pylon": "水晶塔",
    "Assimilator": "吸收舱",
    "Gateway": "传送门",
    "WarpGate": "折跃门",
    "Warp Gate": "折跃门",
    "Forge": "锻炉",
    "CyberneticsCore": "控制核心",
    "Cybernetics Core": "控制核心",
    "RoboticsFacility": "机械台",
    "Robotics Facility": "机械台",
    "Stargate": "星门",
    "TwilightCouncil": "暮光议会",
    "Twilight Council": "暮光议会",
    "RoboticsBay": "机械研究所",
    "Robotics Bay": "机械研究所",
    "FleetBeacon": "舰队航标",
    "Fleet Beacon": "舰队航标",
    "TemplarArchive": "圣堂武士档案馆",
    "Templar Archives": "圣堂武士档案馆",
    "DarkShrine": "黑暗圣所",
    "Dark Shrine": "黑暗圣所",
    "PhotonCannon": "光子炮台",
    "Photon Cannon": "光子炮台",
    "ShieldBattery": "护盾充能器",
    "Shield Battery": "护盾充能器",
    
    # Buildings - Zerg
    "Hatchery": "孵化场",
    "Lair": "虫穴",
    "Hive": "主巢",
    "SpawningPool": "孵化池",
    "Spawning Pool": "孵化池",
    "EvolutionChamber": "进化腔",
    "Evolution Chamber": "进化腔",
    "RoachWarren": "蟑螂巢穴",
    "Roach Warren": "蟑螂巢穴",
    "BanelingNest": "毒爆虫巢",
    "Baneling Nest": "毒爆虫巢",
    "SpineCrawler": "脊针爬虫",
    "Spine Crawler": "脊针爬虫",
    "SpineCrawlerUprooted": "脊针爬虫(移动)",
    "SporeCrawler": "孢子爬虫",
    "Spore Crawler": "孢子爬虫",
    "SporeCrawlerUprooted": "孢子爬虫(移动)",
    "HydraliskDen": "刺蛇巢穴",
    "Hydralisk Den": "刺蛇巢穴",
    "LurkerDen": "潜伏者巢穴",
    "Lurker Den": "潜伏者巢穴",
    "InfestationPit": "感染深渊",
    "Infestation Pit": "感染深渊",
    "Spire": "尖塔",
    "GreaterSpire": "大尖塔",
    "Greater Spire": "大尖塔",
    "NydusNetwork": "坑道网络",
    "Nydus Network": "坑道网络",
    "NydusWorm": "坑道虫",
    "Nydus Worm": "坑道虫",
    "UltraliskCavern": "雷兽洞穴",
    "Ultralisk Cavern": "雷兽洞穴",
    "CreepTumor": "菌毯瘤",
    "Creep Tumor": "菌毯瘤",
    "CreepTumorBurrowed": "菌毯瘤(潜地)",
    
    # Special/Campaign Units
    "Hybrid": "混合体",
    "HybridDestroyer": "混合体毁灭者",
    "HybridReaver": "混合体掠夺者",
    "HybridDominator": "混合体支配者",
    "HybridBehemoth": "混合体巨兽",
    
    # Common variations
    "AutoTurret": "自动机炮",
    "Auto-Turret": "自动机炮",
    "PointDefenseDrone": "防御无人机",
    "Point Defense Drone": "防御无人机",
}


def translate_unit_name(unit_name: str) -> str:
    """
    Translate a unit name from English to Chinese.
    If no translation is found, try using the translate function.
    If that also fails, return the original name.
    
    Args:
        unit_name: The English unit name
        
    Returns:
        The Chinese translation or original name if not found
    """
    # First try direct mapping
    if unit_name in UNIT_NAME_MAPPING:
        return UNIT_NAME_MAPPING[unit_name]
    
    # Try translation function as fallback
    translated = translate(unit_name)
    if translated != unit_name:
        return translated
    
    # Return original if no translation found
    return unit_name


def get_all_unit_translations() -> dict:
    """
    Get all unit translations including those from the mapping and translate function.
    
    Returns:
        Dictionary of English to Chinese unit name translations
    """
    translations = UNIT_NAME_MAPPING.copy()
    
    # Add any additional translations from the translate function
    for eng_name in UNIT_NAME_MAPPING:
        translations[eng_name] = translate_unit_name(eng_name)
    
    return translations 