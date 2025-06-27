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
        
        // Maps
        'Chain of Ascension': '升格之链',
        'Cradle of Death': '死亡摇篮',
        'Dead of Night': '亡者之夜',
        'Lock & Load': '装弹上膛',
        'Malwarfare': '恶意软件',
        'Miner Evacuation': '矿工撤离',
        'Mist Opportunities': '迷雾之机',
        'Oblivion Express': '湮灭快车',
        'Part and Parcel': '分秒必争',
        'Rifts to Korhal': '克哈裂缝',
        'Scythe of Amon': '埃蒙之镰',
        'Temple of the Past': '往日神殿',
        'The Vermillion Problem': '朱红问题',
        'Void Launch': '虚空出击',
        'Void Thrashing': '虚空撕裂',
        
        // Difficulties
        'Casual': '休闲',
        'Normal': '普通',
        'Hard': '困难',
        'Brutal': '残酷',
        
        // Enemy races
        'Amon': '埃蒙'
    },
    'en_US': {
        // For English, we return the same text
        'NO DATA': 'NO DATA',
        'BEST TIME!': 'BEST TIME!',
        'Session:': 'Session:',
        'wins': 'wins',
        'games': 'games',
        'Randomized commander:': 'Randomized commander:',
        'Weekly': 'Weekly',
        'Custom': 'Custom',
        'kills': 'kills',
        'Replay uploaded successfully!': 'Replay uploaded successfully!',
        'Replay not uploaded!': 'Replay not uploaded!',
        'No games played with': 'No games played with',
        'You played': 'You played',
        'games with': 'games with',
        'winrate': 'winrate',
        'APM': 'APM',
        'Last game played together:': 'Last game played together:'
    }
};

// Translation function
function t(text) {
    if (!translations[currentLanguage]) {
        return text;
    }
    return translations[currentLanguage][text] || text;
}

// Set language function
function setLanguage(lang) {
    currentLanguage = lang;
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
    updateStaticTranslations();
}); 