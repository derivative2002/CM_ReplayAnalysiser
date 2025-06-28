// Overlay translation system
var currentLanguage = 'zh_CN';
var translations = {
    'zh_CN': {
        // HTML static text
        'NO DATA': '无数据',
        'BEST TIME!': '最佳时间！',
        
        // JavaScript dynamic text
        'Session:': '会话:',
        'wins': '胜',
        'games': '局',
        'Randomized commander:': '随机指挥官:',
        'Weekly': '每周',
        'Custom': '自定义',
        'kills': '击杀',
        'Replay uploaded successfully!': '回放上传成功！',
        'Replay not uploaded!': '回放上传失败！',
        'No games played with': '未与此玩家进行过游戏',
        'You played': '您进行了',
        'games with': '场游戏，队友是',
        'winrate': '胜率',
        'APM': 'APM',
        'Last game played together:': '最后一起游戏时间:',
        'Player note:': '玩家笔记:',
        
        // Unit stats labels
        'created': '创建',
        'lost': '损失',
        
        // Common units
        'Marine': '陆战队员',
        'Marauder': '掠夺者',
        'Reaper': '死神',
        'Ghost': '幽灵',
        'Hellion': '恶火',
        'Siege Tank': '攻城坦克',
        'Thor': '雷神',
        'Viking': '维京战机',
        'Medivac': '医疗运输机',
        'Liberator': '解放者',
        'Raven': '渡鸦',
        'Banshee': '女妖',
        'Battlecruiser': '战列巡航舰',
        'SCV': 'SCV',
        'MULE': '矿骡',
        
        'Probe': '探机',
        'Zealot': '狂热者',
        'Stalker': '追猎者',
        'Sentry': '哨兵',
        'Adept': '使徒',
        'High Templar': '高阶圣堂武士',
        'Dark Templar': '黑暗圣堂武士',
        'Archon': '执政官',
        'Immortal': '不朽者',
        'Colossus': '巨像',
        'Disruptor': '干扰者',
        'Observer': '观察者',
        'Warp Prism': '折跃棱镜',
        'Phoenix': '凤凰',
        'Void Ray': '虚空辉光舰',
        'Oracle': '先知',
        'Tempest': '风暴战舰',
        'Carrier': '航母',
        
        'Drone': '工蜂',
        'Overlord': '领主',
        'Queen': '女王',
        'Zergling': '跳虫',
        'Baneling': '毒爆虫',
        'Roach': '蟑螂',
        'Ravager': '破坏者',
        'Hydralisk': '刺蛇',
        'Lurker': '潜伏者',
        'Infestor': '感染虫',
        'Swarm Host': '虫群宿主',
        'Mutalisk': '飞龙',
        'Corruptor': '腐化者',
        'Brood Lord': '巢虫领主',
        'Viper': '飞蛇',
        'Ultralisk': '雷兽',
        
        // Special units
        'Slayer': '收割者',
        'Legionnaire': '军团兵',
        'Hybrid': '混合体',
        
        // Commanders
        'Abathur': '阿巴瑟',
        'Alarak': '阿拉纳克',
        'Artanis': '阿塔尼斯',
        'Dehaka': '德哈卡',
        'Fenix': '菲尼克斯',
        'Horner': '霍纳',
        'Karax': '卡拉克斯',
        'Kerrigan': '凯瑞甘',
        'Nova': '诺娃',
        'Raynor': '雷诺',
        'Stetmann': '斯台特曼',
        'Stukov': '斯杜科夫',
        'Swann': '斯旺',
        'Tychus': '泰凯斯',
        'Vorazun': '沃拉尊',
        'Zagara': '扎加拉',
        'Zeratul': '泽拉图',
        'Mengsk': '蒙斯克',
        
        // Maps - 使用游戏内官方翻译
        'Chain of Ascension': '升格之链',
        'Cradle of Death': '死亡摇篮',
        'Dead of Night': '亡者之夜',
        'Lock & Load': '天界封锁',
        'Malwarfare': '净网行动',
        'Miner Evacuation': '营救矿工',
        'Mist Opportunities': '机会渺茫',
        'Oblivion Express': '湮灭快车',
        'Part and Parcel': '聚铁成兵',
        'Rifts to Korhal': '克哈裂痕',
        'Scythe of Amon': '黑暗杀星',
        'Temple of the Past': '往日神庙',
        'The Vermillion Problem': '熔火危机',
        'Void Launch': '虚空降临',
        'Void Thrashing': '虚空撕裂',
        
        // Difficulties
        'Casual': '休闲',
        'Normal': '普通',
        'Hard': '困难',
        'Brutal': '残酷',
        
        // Enemy races
        'Amon': '埃蒙',
        'Kills': '击杀',
        'Supply': '人口',
        'Mining': '采集',
        'Army': '部队',
        'Session': '本次会话',
        'Wins': '胜利',
        'Games': '场数',
        '(No data)': '(无数据)',
        'Difficulty': '难度'
    },
    'en_US': {
        // Maps
        'Chain of Ascension': 'Chain of Ascension',
        'Cradle of Death': 'Cradle of Death',
        'Dead of Night': 'Dead of Night',
        'Lock & Load': 'Lock & Load',
        'Malwarfare': 'Malwarfare',
        'Miner Evacuation': 'Miner Evacuation',
        'Mist Opportunities': 'Mist Opportunities',
        'Oblivion Express': 'Oblivion Express',
        'Part and Parcel': 'Part and Parcel',
        'Rifts to Korhal': 'Rifts to Korhal',
        'Scythe of Amon': 'Scythe of Amon',
        'Temple of the Past': 'Temple of the Past',
        'The Vermillion Problem': 'The Vermillion Problem',
        'Void Launch': 'Void Launch',
        'Void Thrashing': 'Void Thrashing',
        
        // Overlay specific
        'NO DATA': 'NO DATA',
        'BEST TIME!': 'BEST TIME!',
        'Kills': 'Kills',
        'Supply': 'Supply',
        'Mining': 'Mining',
        'Army': 'Army',
        'Session': 'Session',
        'Wins': 'Wins',
        'Games': 'Games',
        '(No data)': '(No data)',
        'Difficulty': 'Difficulty',
        'Brutal': 'Brutal',
        'Hard': 'Hard',
        'Normal': 'Normal',
        'Casual': 'Casual',

        // Commanders
        'Abathur': 'Abathur',
        'Alarak': 'Alarak',
        'Artanis': 'Artanis',
        'Dehaka': 'Dehaka',
        'Fenix': 'Fenix',
        'Horner': 'Horner',
        'Karax': 'Karax',
        'Kerrigan': 'Kerrigan',
        'Nova': 'Nova',
        'Raynor': 'Raynor',
        'Stetmann': 'Stetmann',
        'Stukov': 'Stukov',
        'Swann': 'Swann',
        'Tychus': 'Tychus',
        'Vorazun': 'Vorazun',
        'Zagara': 'Zagara',
        'Zeratul': 'Zeratul',
        'Mengsk': 'Mengsk'
    }
};

// 加载外部JSON翻译文件
var externalTranslations = {};
var jsonLoaded = false;

function loadExternalTranslations(language) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', `overlay_${language}.json`, true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                try {
                    externalTranslations = JSON.parse(xhr.responseText);
                    console.log(`Loaded external translations for ${language}`);
                    jsonLoaded = true;
                    
                    // 如果包含精通翻译，将其提取出来
                    if (externalTranslations["__mastery__"]) {
                        // 将精通翻译保存到全局变量中
                        masteryNames_zhCN = externalTranslations["__mastery__"];
                        // 从翻译对象中删除这个特殊键
                        delete externalTranslations["__mastery__"];
                    }
                    
                    // 更新页面上的静态文本
                    updateStaticTranslations();
                } catch (e) {
                    console.error(`Error parsing external translations: ${e}`);
                }
            } else {
                console.warn(`External translation file not found for ${language}, using built-in translations`);
            }
        }
    };
    xhr.send();
}

// Translation function
function t(text) {
    // 优先使用外部JSON文件中的翻译
    if (jsonLoaded && externalTranslations[text]) {
        return externalTranslations[text];
    }
    
    // 如果外部翻译不存在，使用内置翻译
    if (!translations[currentLanguage]) {
        return text;
    }
    return translations[currentLanguage][text] || text;
}

// Set language function
function setLanguage(lang) {
    currentLanguage = lang;
    // 尝试加载外部翻译
    loadExternalTranslations(lang);
    // 更新静态翻译
    updateStaticTranslations();
}

// Update static HTML translations
function updateStaticTranslations() {
    // Update NO DATA text
    var noDataElement = document.getElementById('nodata');
    if (noDataElement) {
        noDataElement.textContent = t('NO DATA');
    }
    
    // Update BEST TIME text
    var recordElement = document.getElementById('record');
    if (recordElement) {
        recordElement.textContent = t('BEST TIME!');
    }
}

// Initialize translations when page loads
document.addEventListener('DOMContentLoaded', function() {
    // 加载外部翻译
    loadExternalTranslations(currentLanguage);
    // 更新静态翻译
    updateStaticTranslations();
}); 

// 中文版指挥官精通数据
var masteryNames_zhCN = {
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
    'Vorazun': ['暗能塔范围', '黑洞持续时间', '暗影守卫持续时间', '时间停止单位速度提升', '时空加速效率', '艾杜恩之矛初始和最大能量'],
    'Zagara': ['扎加拉和女王再生', '扎加拉攻击伤害', '强化狂热', '跳虫闪避', '蟑螂伤害和生命', '毒爆虫攻击伤害'],
    'Zeratul': ['泽拉图攻击速度', '作战单位攻击速度', '神器碎片生成速率', '支援呼叫冷却时间减少', '传奇军团成本', '化身冷却时间'],
    'Mengsk': ['劳工和士兵帝国支援', '皇家卫队支援', '可怕伤害', '皇家卫队成本', '起始帝国授权', '皇家卫队经验获取速率']
};