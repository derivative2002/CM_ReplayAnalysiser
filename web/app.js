// 全局变量
let ws = null;
let reconnectTimer = null;
let gameHistory = [];
let charts = {};

// DOM 元素
const elements = {
    connectionStatus: document.getElementById('connection-status'),
    lastUpdate: document.getElementById('last-update')
};

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    console.log('初始化 StarCraft Co-op Overlay Web 界面');
    
    // 初始化标签页
    initTabs();
    
    // 加载游戏历史
    loadGameHistory();
    
    // 检查数据版本，清除旧数据
    const dataVersion = localStorage.getItem('dataVersion');
    const currentVersion = '2.0'; // 数据格式版本
    if (dataVersion !== currentVersion) {
        console.log('检测到旧版本数据，清除缓存...');
        localStorage.clear();
        localStorage.setItem('dataVersion', currentVersion);
    }
    
    // 预加载游戏数据（不管当前是哪个标签页）
    if (gameHistory.length === 0) {
        console.log('预加载游戏数据...');
        loadGamesFromAPI();
    }
    
    // 初始化当前活动标签页
    const activeTab = document.querySelector('.tab.active');
    if (activeTab) {
        const tabName = activeTab.getAttribute('data-tab');
        console.log('初始化活动标签页:', tabName);
        initTabContent(tabName);
    }
    
    // 初始化设置
    initSettings();
    
    // 连接 WebSocket
    connectWebSocket();
    
    // 定期状态检查
    setInterval(checkServerStatus, 30000);
});

// 标签页功能
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.getAttribute('data-tab');
            
            // 移除所有活动状态
            tabs.forEach(t => t.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // 激活选中的标签
            tab.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
            
            // 初始化特定标签页内容
            initTabContent(targetTab);
        });
    });
}

// 初始化标签页内容
function initTabContent(tabName) {
    switch(tabName) {
        case 'settings':
            initSettings();
            break;
        case 'games':
            initGames();
            break;
        case 'players':
            initPlayers();
            break;
        case 'statistics':
            initStatistics();
            break;
        case 'weeklies':
            initWeeklies();
            break;
        case 'mutator-stats':
            initMutatorStats();
            break;
        case 'custom-maps':
            initCustomMaps();
            break;
        default:
            break;
    }
}

// 设置页面
function initSettings() {
    loadSettings();
    bindSettingsEvents();
}

function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('scoSettings') || '{}');
    
    // 加载复选框状态
    const checkboxes = {
        'start-with-windows': settings.startWithWindows || false,
        'start-minimized': settings.startMinimized || false,
        'minimize-to-tray': settings.minimizeToTray || false,
        'enable-logging': settings.enableLogging || false,
        'show-session': settings.showSession || false,
        'show-player-winrates': settings.showPlayerWinrates || false,
        'show-charts': settings.showCharts || true,
        'dark-theme': settings.darkTheme !== false,
        'fast-expand': settings.fastExpand || false
    };
    
    Object.entries(checkboxes).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) element.checked = value;
    });
    
    // 加载数值设置
    if (settings.duration !== undefined) {
        document.getElementById('duration').value = settings.duration;
    }
    if (settings.monitor !== undefined) {
        document.getElementById('monitor').value = settings.monitor;
    }
    
    // 加载文件夹路径
    document.getElementById('account-folder').value = settings.accountFolder || '';
    document.getElementById('screenshot-folder').value = settings.screenshotFolder || '';
    
    // 加载热键
    document.getElementById('hotkey-overlay').value = settings.hotkeyOverlay || 'F2';
}

function bindSettingsEvents() {
    // 绑定所有设置控件
    const settingsInputs = document.querySelectorAll('#settings input, #settings select');
    settingsInputs.forEach(input => {
        input.addEventListener('change', saveSettings);
    });
    
    // 绑定按钮事件
    document.querySelectorAll('.action-button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            handleSettingsAction(e.target.textContent);
        });
    });
    
    // 绑定浏览按钮
    document.querySelectorAll('.browse-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            alert('浏览功能在Web版本中不可用');
        });
    });
    
    // 绑定热键设置按钮
    document.querySelectorAll('.hotkey-set-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            alert('热键设置功能在Web版本中不可用');
        });
    });
}

function saveSettings() {
    const settings = {
        startWithWindows: document.getElementById('start-with-windows').checked,
        startMinimized: document.getElementById('start-minimized').checked,
        minimizeToTray: document.getElementById('minimize-to-tray').checked,
        enableLogging: document.getElementById('enable-logging').checked,
        showSession: document.getElementById('show-session').checked,
        showPlayerWinrates: document.getElementById('show-player-winrates').checked,
        showCharts: document.getElementById('show-charts').checked,
        darkTheme: document.getElementById('dark-theme').checked,
        fastExpand: document.getElementById('fast-expand').checked,
        duration: parseInt(document.getElementById('duration').value),
        monitor: parseInt(document.getElementById('monitor').value),
        accountFolder: document.getElementById('account-folder').value,
        screenshotFolder: document.getElementById('screenshot-folder').value,
        hotkeyOverlay: document.getElementById('hotkey-overlay').value
    };
    
    localStorage.setItem('scoSettings', JSON.stringify(settings));
}

function handleSettingsAction(action) {
    switch(action) {
        case 'Manual analysis':
            sendCommand('manual_analysis');
            break;
        case 'Reset settings':
            if (confirm('确定要重置所有设置吗？')) {
                localStorage.removeItem('scoSettings');
                loadSettings();
            }
            break;
        case 'Export settings':
            exportSettings();
            break;
    }
}

function exportSettings() {
    const settings = localStorage.getItem('scoSettings');
    const blob = new Blob([settings], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sco_settings.json';
    a.click();
    URL.revokeObjectURL(url);
}

// 游戏页面
function initGames() {
    console.log('初始化Games页面');
    // 先从localStorage加载
    loadGameHistory();
    console.log('localStorage中的游戏历史:', gameHistory.length, '条记录');
    
    // 如果没有数据，从API加载
    if (gameHistory.length === 0) {
        console.log('没有本地数据，从API加载...');
        loadGamesFromAPI();
    } else {
        console.log('使用本地数据更新游戏列表');
        updateGamesList();
    }
    
    bindGamesEvents();
}

function bindGamesEvents() {
    const searchInput = document.getElementById('games-search');
    const searchBtn = document.querySelector('.search-btn');
    
    if (searchInput && searchBtn) {
        searchBtn.addEventListener('click', searchGames);
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchGames();
        });
    }
}

function updateGamesList() {
    console.log('更新游戏列表，当前数据:', gameHistory.length, '条');
    const gamesList = document.getElementById('games-list');
    
    if (!gamesList) {
        console.error('找不到games-list元素');
        return;
    }
    
    if (gameHistory.length === 0) {
        console.log('没有游戏数据，显示等待消息');
        gamesList.innerHTML = '<div class="waiting-message"><b>Please wait. This can take few minutes the first time.<br>Analyzing your replays.</b></div>';
        return;
    }
    
    console.log('开始渲染', gameHistory.length, '个游戏条目');
    let html = '';
    gameHistory.forEach((game, index) => {
        html += createGameEntry(game, index);
    });
    
    gamesList.innerHTML = html;
    console.log('游戏列表渲染完成');
}

function createGameEntry(game, index) {
    const resultClass = game.result === 'Victory' ? 'victory' : 'defeat';
    
    return `
        <div class="game-entry" data-index="${index}">
            <div class="game-map">${game.mapName || '未知地图'}</div>
            <div class="game-result ${resultClass}">${game.result || '未知'}</div>
            <div class="game-player1">${game.player1?.name || '玩家1'} (${game.player1?.commander_cn || game.player1?.commander || '未知指挥官'})</div>
            <div class="game-player2">${game.player2?.name || '玩家2'} (${game.player2?.commander_cn || game.player2?.commander || '未知指挥官'})</div>
            <div class="game-enemy">Amon</div>
            <div class="game-length">${formatDuration(game.length)}</div>
            <div class="game-difficulty">${getDifficultyName(game.difficulty)}</div>
            <div class="game-date">${game.date || '未知时间'}</div>
        </div>
    `;
}

function searchGames() {
    const searchText = document.getElementById('games-search').value.toLowerCase();
    const gameEntries = document.querySelectorAll('.game-entry');
    
    gameEntries.forEach(entry => {
        const index = parseInt(entry.dataset.index);
        const game = gameHistory[index];
        
        let visible = true;
        if (searchText && !JSON.stringify(game).toLowerCase().includes(searchText)) {
            visible = false;
        }
        
        entry.style.display = visible ? 'grid' : 'none';
    });
}

// 玩家页面
function initPlayers() {
    updatePlayerStats();
}

function updatePlayerStats() {
    const totalGames = gameHistory.length;
    const victories = gameHistory.filter(game => game.result === 'Victory').length;
    const winRate = totalGames > 0 ? Math.round((victories / totalGames) * 100) : 0;
    
    let totalAPM = 0;
    let apmCount = 0;
    
    gameHistory.forEach(game => {
        if (game.player1?.apm) {
            totalAPM += game.player1.apm;
            apmCount++;
        }
        if (game.player2?.apm) {
            totalAPM += game.player2.apm;
            apmCount++;
        }
    });
    
    const avgAPM = apmCount > 0 ? Math.round(totalAPM / apmCount) : 0;
    
    // 更新显示
    document.getElementById('total-games').textContent = totalGames;
    document.getElementById('win-rate').textContent = `${winRate}%`;
    document.getElementById('avg-apm').textContent = avgAPM;
}

// 统计页面
async function initStatistics() {
    console.log('初始化Statistics页面');
    
    // 确保有游戏数据
    if (gameHistory.length === 0) {
        console.log('Statistics页面：没有本地数据，从API加载...');
        await loadGamesFromAPI();
    }
    
    // 初始化统计模块
    initStatsTabs();
    initStatsFilters();
    initStatsCharts();
    
    // 设置filteredGames初始值
    statsData.filteredGames = gameHistory;
    console.log('Statistics页面：初始化完成，游戏数量:', gameHistory.length);
    
    // 加载统计数据
    loadStatsData();
    
    // 更新概览统计
    updateGeneralStats();
}

// 更新统计概览
function updateGeneralStats() {
    console.log('更新统计概览，游戏数量:', gameHistory.length);
    
    // 计算总游戏数
    const totalGames = gameHistory.length;
    const totalGamesElement = document.getElementById('total-games-stat');
    if (totalGamesElement) {
        totalGamesElement.textContent = totalGames;
    }
    
    // 计算胜率
    const victories = gameHistory.filter(game => game.result === 'Victory').length;
    const winRate = totalGames > 0 ? Math.round((victories / totalGames) * 100) : 0;
    const winRateElement = document.getElementById('win-rate-stat');
    if (winRateElement) {
        winRateElement.textContent = winRate + '%';
    }
    
    // 计算平均游戏时长
    const totalTime = gameHistory.reduce((sum, game) => sum + (game.length || 0), 0);
    const avgTime = totalGames > 0 ? Math.round(totalTime / totalGames) : 0;
    const avgDurationElement = document.getElementById('average-duration');
    if (avgDurationElement) {
        avgDurationElement.textContent = formatDuration(avgTime);
    }
    
    // 找出最快完成时间
    const fastestGame = gameHistory
        .filter(game => game.result === 'Victory' && game.length > 0)
        .sort((a, b) => a.length - b.length)[0];
    const fastestElement = document.getElementById('fastest-completion');
    if (fastestElement) {
        if (fastestGame) {
            fastestElement.textContent = formatDuration(fastestGame.length);
        } else {
            fastestElement.textContent = '-';
        }
    }
    
    // 更新图表数据
    updateChartData();
}

function initCharts() {
    // 难度分布图表
    const difficultyCtx = document.getElementById('difficulty-chart');
    if (difficultyCtx && !charts.difficulty) {
        charts.difficulty = new Chart(difficultyCtx, {
            type: 'doughnut',
            data: {
                labels: ['Casual', 'Normal', 'Hard', 'Brutal', 'Brutal+'],
                datasets: [{
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: [
                        '#4CAF50',
                        '#2196F3',
                        '#FF9800',
                        '#F44336',
                        '#9C27B0'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff'
                        }
                    }
                }
            }
        });
    }
    
    // 指挥官使用图表
    const commanderCtx = document.getElementById('commander-chart');
    if (commanderCtx && !charts.commander) {
        charts.commander = new Chart(commanderCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Usage Count',
                    data: [],
                    backgroundColor: '#87CEEB'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#fff'
                        },
                        grid: {
                            color: '#555'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#fff'
                        },
                        grid: {
                            color: '#555'
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff'
                        }
                    }
                }
            }
        });
    }
    
    updateChartData();
}

function updateChartData() {
    if (!charts.difficulty || !charts.commander) return;
    
    // 更新难度分布数据
    const difficultyCount = [0, 0, 0, 0, 0];
    const commanderCount = {};
    
    gameHistory.forEach(game => {
        if (game.difficulty >= 1 && game.difficulty <= 5) {
            difficultyCount[game.difficulty - 1]++;
        }
        
        [game.player1, game.player2].forEach(player => {
            if (player?.commander) {
                commanderCount[player.commander] = (commanderCount[player.commander] || 0) + 1;
            }
        });
    });
    
    charts.difficulty.data.datasets[0].data = difficultyCount;
    charts.difficulty.update();
    
    // 更新指挥官数据
    const sortedCommanders = Object.entries(commanderCount)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10);
    
    charts.commander.data.labels = sortedCommanders.map(([name]) => name);
    charts.commander.data.datasets[0].data = sortedCommanders.map(([,count]) => count);
    charts.commander.update();
}

// 每周页面
function initWeeklies() {
    // 这里可以添加获取每周突变信息的逻辑
    updateWeeklyInfo();
}

function updateWeeklyInfo() {
    // 模拟数据，实际应该从服务器获取
    document.getElementById('weekly-map').textContent = 'Void Thrashing';
    document.getElementById('weekly-mutators').textContent = 'Diffusion, Void Rifts';
    document.getElementById('weekly-attempts').textContent = '0';
    document.getElementById('weekly-wins').textContent = '0';
    document.getElementById('weekly-winrate').textContent = '0%';
}

// WebSocket 连接
function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        return;
    }

    ws = new WebSocket('ws://localhost:7310');

    ws.onopen = () => {
        console.log('WebSocket连接已建立');
        updateConnectionStatus(true);
        clearTimeout(reconnectTimer);
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log('收到数据:', data);
            handleReplayData(data);
            updateLastUpdateTime();
        } catch (error) {
            console.error('解析数据失败:', error);
        }
    };

    ws.onclose = () => {
        console.log('WebSocket连接已关闭');
        updateConnectionStatus(false);
        scheduleReconnect();
    };

    ws.onerror = (error) => {
        console.error('WebSocket错误:', error);
        updateConnectionStatus(false);
    };
}

function scheduleReconnect() {
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(() => {
        console.log('尝试重新连接...');
        connectWebSocket();
    }, 5000);
}

function updateConnectionStatus(connected) {
    if (connected) {
        elements.connectionStatus.textContent = '● Connected';
        elements.connectionStatus.className = 'status connected';
    } else {
        elements.connectionStatus.textContent = '● Disconnected';
        elements.connectionStatus.className = 'status disconnected';
    }
}

function updateLastUpdateTime() {
    elements.lastUpdate.textContent = new Date().toLocaleTimeString();
}

// 处理回放数据
function handleReplayData(data) {
    if (data.replaydata) {
        addGameToHistory(data);
        
        // 根据当前活动标签页更新内容
        const activeTab = document.querySelector('.tab.active').getAttribute('data-tab');
        if (activeTab === 'games') {
            updateGamesList();
        } else if (activeTab === 'players') {
            updatePlayerStats();
        } else if (activeTab === 'statistics') {
            updateChartData();
        }
    }
}

function addGameToHistory(data) {
    const gameData = {
        mapName: data.MapName,
        difficulty: data.difficulty,
        result: data.result,
        length: data.length,
        date: new Date().toLocaleString(),
        player1: data.replaydata?.player1,
        player2: data.replaydata?.player2
    };
    
    gameHistory.unshift(gameData);
    
    // 只保留最近100场游戏
    if (gameHistory.length > 100) {
        gameHistory.pop();
    }
    
    // 保存到本地存储
    localStorage.setItem('gameHistory', JSON.stringify(gameHistory));
}

// 工具函数
function getDifficultyName(difficulty) {
    const difficultyMap = {
        1: 'Casual',
        2: 'Normal',
        3: 'Hard',
        4: 'Brutal',
        5: 'Brutal+',
        6: 'B+1',
        7: 'B+2',
        8: 'B+3',
        9: 'B+4',
        10: 'B+5',
        11: 'B+6'
    };
    return difficultyMap[difficulty] || `Diff ${difficulty}`;
}

function formatDuration(seconds) {
    if (!seconds) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

function sendCommand(command, data = {}) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ command, ...data }));
    }
}

function loadGameHistory() {
    const saved = localStorage.getItem('gameHistory');
    if (saved) {
        gameHistory = JSON.parse(saved);
    }
}

async function loadGamesFromAPI() {
    try {
        console.log('正在从API加载游戏历史...');
        const response = await fetch('/api/games/history');
        const result = await response.json();
        console.log('API响应:', result);
        
        if (result.status === 'success' && result.data && result.data.length > 0) {
            gameHistory = result.data;
            console.log(`成功加载 ${gameHistory.length} 个游戏记录`);
            console.log('游戏历史数据:', gameHistory);
            
            // 无论当前在哪个标签页，都更新游戏列表显示
            updateGamesList();
            saveGameHistory();
            
            // 如果当前在Games标签页，确保显示正确
            const activeTab = document.querySelector('.tab.active');
            if (activeTab && activeTab.getAttribute('data-tab') === 'games') {
                console.log('当前在Games标签页，重新初始化');
                initGames();
            }
        } else {
            console.log('API返回空数据或失败');
            showGamesEmptyState();
        }
    } catch (error) {
        console.error('加载游戏历史失败:', error);
        showGamesError('无法加载游戏历史数据');
    }
}

function saveGameHistory() {
    try {
        localStorage.setItem('gameHistory', JSON.stringify(gameHistory));
    } catch (error) {
        console.error('保存游戏历史失败:', error);
    }
}

function showGamesEmptyState() {
    const gamesList = document.getElementById('games-list');
    if (gamesList) {
        gamesList.innerHTML = '<div class="waiting-message"><b>暂无游戏记录。<br>请先分析一些回放文件。</b></div>';
    }
}

function showGamesError(message) {
    const gamesList = document.getElementById('games-list');
    if (gamesList) {
        gamesList.innerHTML = `<div class="waiting-message"><b>错误：${message}</b></div>`;
    }
}

async function checkServerStatus() {
    try {
        const response = await fetch('/api/status');
        if (response.ok) {
            const status = await response.json();
            console.log('服务器状态:', status);
        }
    } catch (error) {
        console.error('获取状态失败:', error);
    }
}

// =============== Statistics 页面完整功能 ===============

// 统计数据状态
let statsData = {
    currentFilters: {},
    filteredGames: [],
    charts: {}
};

// 初始化统计子标签页
function initStatsTabs() {
    const statsTabs = document.querySelectorAll('.stats-tab');
    const statsTabPanes = document.querySelectorAll('.stats-tab-pane');
    
    statsTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.getAttribute('data-tab');
            
            // 移除所有活动状态
            statsTabs.forEach(t => t.classList.remove('active'));
            statsTabPanes.forEach(p => p.classList.remove('active'));
            
            // 激活选中的标签
            tab.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
            
            // 初始化选中标签页的内容
            initStatsTabContent(targetTab);
        });
    });
}

// 初始化过滤器系统
function initStatsFilters() {
    // 绑定过滤器事件
    document.getElementById('apply-filters').addEventListener('click', applyFilters);
    document.getElementById('reset-filters').addEventListener('click', resetFilters);
    document.getElementById('export-stats').addEventListener('click', exportStats);
    
    // 初始化日期过滤器
    const today = new Date();
    const oneMonthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
    
    document.getElementById('from-date').value = oneMonthAgo.toISOString().split('T')[0];
    document.getElementById('to-date').value = today.toISOString().split('T')[0];
}

// 初始化统计图表
function initStatsCharts() {
    // 销毁现有图表
    Object.values(statsData.charts).forEach(chart => {
        if (chart) chart.destroy();
    });
    statsData.charts = {};
    
    // 创建难度分布图表
    const difficultyCtx = document.getElementById('difficulty-chart');
    if (difficultyCtx) {
        statsData.charts.difficulty = new Chart(difficultyCtx, {
            type: 'doughnut',
            data: {
                labels: ['休闲', '普通', '困难', '残酷', '残酷+'],
                datasets: [{
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: ['#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9C27B0']
                }]
            },
            options: getChartOptions('难度分布')
        });
    }
    
    // 创建地区分布图表
    const regionCtx = document.getElementById('region-chart');
    if (regionCtx) {
        statsData.charts.region = new Chart(regionCtx, {
            type: 'pie',
            data: {
                labels: ['美洲', '欧洲', '亚洲', '中国'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
                }]
            },
            options: getChartOptions('地区分布')
        });
    }
    
    // 创建盟友指挥官图表
    const allyCommandersCtx = document.getElementById('ally-commanders-chart');
    if (allyCommandersCtx) {
        statsData.charts.allyCommanders = new Chart(allyCommandersCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: '使用次数',
                    data: [],
                    backgroundColor: '#36A2EB'
                }]
            },
            options: getChartOptions('盟友指挥官使用统计', true)
        });
    }
    
    // 创建我的指挥官图表
    const myCommandersCtx = document.getElementById('my-commanders-chart');
    if (myCommandersCtx) {
        statsData.charts.myCommanders = new Chart(myCommandersCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: '使用次数',
                    data: [],
                    backgroundColor: '#4BC0C0'
                }]
            },
            options: getChartOptions('我的指挥官使用统计', true)
        });
    }
}

// 图表配置选项
function getChartOptions(title, hasAxes = false) {
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: true,
                text: title,
                color: '#ffffff'
            },
            legend: {
                labels: {
                    color: '#ffffff'
                }
            }
        }
    };
    
    if (hasAxes) {
        options.scales = {
            y: {
                beginAtZero: true,
                ticks: { color: '#ffffff' },
                grid: { color: '#555555' }
            },
            x: {
                ticks: { color: '#ffffff' },
                grid: { color: '#555555' }
            }
        };
    }
    
    return options;
}

// 加载统计数据
async function loadStatsData() {
    // 从API加载真实统计数据
    try {
        const response = await fetch('/api/stats/summary');
        const result = await response.json();
        
        if (result.status === 'success') {
            const stats = result.data;
            
            // 更新UI显示真实统计数据
            updateStatsDisplay(stats);
        } else {
            console.warn('无统计数据可用:', result.message);
            showNoDataMessage();
        }
    } catch (error) {
        console.error('加载统计数据失败:', error);
        showErrorMessage('无法加载统计数据');
    }
}

// 更新统计显示
function updateStatsDisplay(stats) {
    console.log('更新统计显示:', stats);
    
    // 更新游戏总数显示
    const totalElement = document.querySelector('#total-games');
    if (totalElement) {
        totalElement.textContent = stats.total_games || 0;
    }
    
    // 更新地图统计
    if (stats.maps && Object.keys(stats.maps).length > 0) {
        updateMapDisplay(stats.maps);
    }
    
    // 更新指挥官统计  
    if (stats.commanders && Object.keys(stats.commanders).length > 0) {
        updateCommanderDisplay(stats.commanders);
    }
}

function updateMapDisplay(maps) {
    console.log('地图统计:', maps);
    // 可以在这里添加地图统计的图表更新逻辑
}

function updateCommanderDisplay(commanders) {
    console.log('指挥官统计:', commanders);
    // 可以在这里添加指挥官统计的图表更新逻辑
}

function showNoDataMessage() {
    console.log('暂无统计数据');
    const container = document.querySelector('#stats-content');
    if (container) {
        container.innerHTML = '<p>暂无统计数据，请先分析一些回放文件。</p>';
    }
}

function showErrorMessage(message) {
    console.error('统计数据错误:', message);
    const container = document.querySelector('#stats-content');
    if (container) {
        container.innerHTML = `<p>错误: ${message}</p>`;
    }
}

// 应用过滤器
function applyFilters() {
    // 获取过滤器值
    statsData.currentFilters = {
        difficulty: document.getElementById('difficulty-filter').value,
        region: document.getElementById('region-filter').value,
        gameType: document.getElementById('gametype-filter').value,
        fromDate: document.getElementById('from-date').value,
        toDate: document.getElementById('to-date').value,
        minLength: document.getElementById('min-length').value,
        maxLength: document.getElementById('max-length').value
    };
    
    // 过滤游戏数据
    statsData.filteredGames = gameHistory.filter(game => {
        return matchesFilters(game, statsData.currentFilters);
    });
    
    console.log(`过滤后游戏数量: ${statsData.filteredGames.length}`);
    
    // 更新当前活动的标签页
    const activeStatsTab = document.querySelector('.stats-tab.active');
    if (activeStatsTab) {
        initStatsTabContent(activeStatsTab.getAttribute('data-tab'));
    }
}

// 检查游戏是否匹配过滤器
function matchesFilters(game, filters) {
    // 难度过滤
    if (filters.difficulty && game.difficulty != filters.difficulty) {
        return false;
    }
    
    // 地区过滤
    if (filters.region && game.region !== filters.region) {
        return false;
    }
    
    // 游戏类型过滤
    if (filters.gameType && game.gameType !== filters.gameType) {
        return false;
    }
    
    // 日期过滤
    if (filters.fromDate || filters.toDate) {
        const gameDate = new Date(game.date);
        if (filters.fromDate && gameDate < new Date(filters.fromDate)) {
            return false;
        }
        if (filters.toDate && gameDate > new Date(filters.toDate + 'T23:59:59')) {
            return false;
        }
    }
    
    // 游戏长度过滤
    const gameLengthMinutes = game.length / 60;
    if (filters.minLength && gameLengthMinutes < parseInt(filters.minLength)) {
        return false;
    }
    if (filters.maxLength && gameLengthMinutes > parseInt(filters.maxLength)) {
        return false;
    }
    
    return true;
}

// 重置过滤器
function resetFilters() {
    document.getElementById('difficulty-filter').value = '';
    document.getElementById('region-filter').value = '';
    document.getElementById('gametype-filter').value = '';
    document.getElementById('from-date').value = '';
    document.getElementById('to-date').value = '';
    document.getElementById('min-length').value = '';
    document.getElementById('max-length').value = '';
    
    applyFilters();
}

// 初始化统计子标签页内容
function initStatsTabContent(tabName) {
    switch(tabName) {
        case 'maps':
            updateMapsStats();
            break;
        case 'ally-commanders':
            updateAllyCommandersStats();
            break;
        case 'my-commanders':
            updateMyCommandersStats();
            break;
        case 'difficulty-region':
            updateDifficultyRegionStats();
            break;
        case 'full-analysis':
            initFullAnalysis();
            break;
    }
}

// 更新地图统计
function updateMapsStats() {
    const mapStats = {};
    const fastestCompletions = {};
    
    statsData.filteredGames.forEach(game => {
        if (!mapStats[game.mapName]) {
            mapStats[game.mapName] = {
                total: 0,
                wins: 0,
                losses: 0,
                totalTime: 0,
                fastestTime: Infinity
            };
        }
        
        const stats = mapStats[game.mapName];
        stats.total++;
        stats.totalTime += game.length;
        
        if (game.result === 'Victory') {
            stats.wins++;
            if (game.length < stats.fastestTime) {
                stats.fastestTime = game.length;
                fastestCompletions[game.mapName] = {
                    time: game.length,
                    date: game.date
                };
            }
        } else {
            stats.losses++;
        }
    });
    
    // 更新地图表格
    const tbody = document.getElementById('maps-table-body');
    tbody.innerHTML = '';
    
    Object.entries(mapStats).forEach(([mapName, stats]) => {
        const winRate = stats.total > 0 ? ((stats.wins / stats.total) * 100).toFixed(1) : '0.0';
        const avgTime = stats.total > 0 ? formatDuration(Math.round(stats.totalTime / stats.total)) : '0:00';
        const fastestTime = stats.fastestTime !== Infinity ? formatDuration(stats.fastestTime) : '-';
        
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${mapName}</td>
            <td>${stats.total}</td>
            <td>${stats.wins}</td>
            <td>${stats.losses}</td>
            <td>${winRate}%</td>
            <td>${avgTime}</td>
            <td>${fastestTime}</td>
        `;
    });
    
    // 更新最快完成记录
    const fastestDiv = document.getElementById('fastest-completions');
    fastestDiv.innerHTML = '';
    
    Object.entries(fastestCompletions).forEach(([mapName, record]) => {
        const div = document.createElement('div');
        div.className = 'fastest-record';
        div.innerHTML = `
            <span>${mapName}</span>
            <span>${formatDuration(record.time)} (${new Date(record.date).toLocaleDateString()})</span>
        `;
        fastestDiv.appendChild(div);
    });
}

// 更新盟友指挥官统计
function updateAllyCommandersStats() {
    const commanderStats = {};
    
    statsData.filteredGames.forEach(game => {
        if (game.player2 && game.player2.commander) {
            const commander = game.player2.commander;
            if (!commanderStats[commander]) {
                commanderStats[commander] = {
                    total: 0,
                    wins: 0,
                    losses: 0,
                    totalAPM: 0,
                    totalKills: 0
                };
            }
            
            const stats = commanderStats[commander];
            stats.total++;
            stats.totalAPM += game.player2.apm || 0;
            stats.totalKills += game.player2.kills || 0;
            
            if (game.result === 'Victory') {
                stats.wins++;
            } else {
                stats.losses++;
            }
        }
    });
    
    updateCommanderTable('ally-commanders-table-body', commanderStats);
    updateCommanderChart('allyCommanders', commanderStats);
}

// 更新我的指挥官统计
function updateMyCommandersStats() {
    const commanderStats = {};
    
    statsData.filteredGames.forEach(game => {
        if (game.player1 && game.player1.commander) {
            const commander = game.player1.commander;
            if (!commanderStats[commander]) {
                commanderStats[commander] = {
                    total: 0,
                    wins: 0,
                    losses: 0,
                    totalAPM: 0,
                    totalKills: 0,
                    masteryLevel: Math.floor(Math.random() * 200) // 模拟精通等级
                };
            }
            
            const stats = commanderStats[commander];
            stats.total++;
            stats.totalAPM += game.player1.apm || 0;
            stats.totalKills += game.player1.kills || 0;
            
            if (game.result === 'Victory') {
                stats.wins++;
            } else {
                stats.losses++;
            }
        }
    });
    
    updateCommanderTable('my-commanders-table-body', commanderStats, true);
    updateCommanderChart('myCommanders', commanderStats);
}

// 更新指挥官表格
function updateCommanderTable(tableBodyId, commanderStats, includeMastery = false) {
    const tbody = document.getElementById(tableBodyId);
    tbody.innerHTML = '';
    
    Object.entries(commanderStats).forEach(([commander, stats]) => {
        const winRate = stats.total > 0 ? ((stats.wins / stats.total) * 100).toFixed(1) : '0.0';
        const avgAPM = stats.total > 0 ? Math.round(stats.totalAPM / stats.total) : 0;
        const avgKills = stats.total > 0 ? (stats.totalKills / stats.total).toFixed(1) : '0.0';
        
        const row = tbody.insertRow();
        let html = `
            <td>${commander}</td>
            <td>${stats.total}</td>
            <td>${stats.wins}</td>
            <td>${stats.losses}</td>
            <td>${winRate}%</td>
            <td>${avgAPM}</td>
            <td>${avgKills}</td>
        `;
        
        if (includeMastery) {
            html += `<td>${stats.masteryLevel || 0}</td>`;
        }
        
        row.innerHTML = html;
    });
}

// 更新指挥官图表
function updateCommanderChart(chartName, commanderStats) {
    const chart = statsData.charts[chartName];
    if (!chart) return;
    
    const sortedCommanders = Object.entries(commanderStats)
        .sort(([,a], [,b]) => b.total - a.total)
        .slice(0, 8);
    
    chart.data.labels = sortedCommanders.map(([name]) => name);
    chart.data.datasets[0].data = sortedCommanders.map(([,stats]) => stats.total);
    chart.update();
}

// 更新难度和地区统计
function updateDifficultyRegionStats() {
    updateDifficultyChart();
    updateRegionChart();
    updateDifficultyTable();
}

// 更新难度图表
function updateDifficultyChart() {
    const difficultyCount = [0, 0, 0, 0, 0];
    
    statsData.filteredGames.forEach(game => {
        if (game.difficulty >= 1 && game.difficulty <= 5) {
            difficultyCount[game.difficulty - 1]++;
        }
    });
    
    const chart = statsData.charts.difficulty;
    if (chart) {
        chart.data.datasets[0].data = difficultyCount;
        chart.update();
    }
}

// 更新地区图表
function updateRegionChart() {
    const regionCount = { us: 0, eu: 0, kr: 0, cn: 0 };
    
    statsData.filteredGames.forEach(game => {
        if (regionCount.hasOwnProperty(game.region)) {
            regionCount[game.region]++;
        }
    });
    
    const chart = statsData.charts.region;
    if (chart) {
        chart.data.datasets[0].data = Object.values(regionCount);
        chart.update();
    }
}

// 更新难度表格
function updateDifficultyTable() {
    const difficultyStats = {};
    const difficultyNames = {
        1: '休闲', 2: '普通', 3: '困难', 4: '残酷', 5: '残酷+'
    };
    
    statsData.filteredGames.forEach(game => {
        const diff = game.difficulty;
        if (!difficultyStats[diff]) {
            difficultyStats[diff] = { total: 0, wins: 0, losses: 0 };
        }
        
        difficultyStats[diff].total++;
        if (game.result === 'Victory') {
            difficultyStats[diff].wins++;
        } else {
            difficultyStats[diff].losses++;
        }
    });
    
    const tbody = document.getElementById('difficulty-table-body');
    tbody.innerHTML = '';
    
    Object.entries(difficultyStats).forEach(([difficulty, stats]) => {
        const winRate = stats.total > 0 ? ((stats.wins / stats.total) * 100).toFixed(1) : '0.0';
        
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${difficultyNames[difficulty] || `难度${difficulty}`}</td>
            <td>${stats.total}</td>
            <td>${stats.wins}</td>
            <td>${stats.losses}</td>
            <td>${winRate}%</td>
        `;
    });
}

// 初始化全分析
function initFullAnalysis() {
    document.getElementById('run-full-analysis').addEventListener('click', runFullAnalysis);
}

// 运行全分析
function runFullAnalysis() {
    const includeMutations = document.getElementById('include-mutations').checked;
    const includeCustomMaps = document.getElementById('include-custom-maps').checked;
    const detailedBreakdown = document.getElementById('detailed-breakdown').checked;
    
    const resultsDiv = document.getElementById('analysis-results');
    resultsDiv.innerHTML = '<div style="text-align: center;">正在分析数据...</div>';
    
    // 模拟分析过程
    setTimeout(() => {
        const analysis = generateFullAnalysis(includeMutations, includeCustomMaps, detailedBreakdown);
        resultsDiv.innerHTML = analysis;
    }, 1500);
}

// 生成全分析报告
function generateFullAnalysis(includeMutations, includeCustomMaps, detailedBreakdown) {
    const games = statsData.filteredGames;
    const totalGames = games.length;
    const wins = games.filter(g => g.result === 'Victory').length;
    const winRate = totalGames > 0 ? ((wins / totalGames) * 100).toFixed(1) : '0.0';
    
    let html = `
        <div class="analysis-summary">
            <h4>分析摘要</h4>
            <div class="summary-stats">
                <div>总游戏数: <strong>${totalGames}</strong></div>
                <div>胜利: <strong>${wins}</strong></div>
                <div>失败: <strong>${totalGames - wins}</strong></div>
                <div>总胜率: <strong>${winRate}%</strong></div>
            </div>
        </div>
    `;
    
    if (detailedBreakdown) {
        html += `
            <div class="analysis-breakdown">
                <h4>详细分解</h4>
                <div>平均游戏时长: <strong>${formatDuration(Math.round(games.reduce((sum, g) => sum + g.length, 0) / totalGames))}</strong></div>
                <div>最常游玩地图: <strong>${getMostPlayedMap(games)}</strong></div>
                <div>最常使用指挥官: <strong>${getMostUsedCommander(games)}</strong></div>
            </div>
        `;
    }
    
    return html;
}

// 获取最常游玩地图
function getMostPlayedMap(games) {
    const mapCount = {};
    games.forEach(game => {
        mapCount[game.mapName] = (mapCount[game.mapName] || 0) + 1;
    });
    
    const mostPlayed = Object.entries(mapCount).sort(([,a], [,b]) => b - a)[0];
    return mostPlayed ? `${mostPlayed[0]} (${mostPlayed[1]}次)` : '无数据';
}

// 获取最常使用指挥官
function getMostUsedCommander(games) {
    const commanderCount = {};
    games.forEach(game => {
        if (game.player1 && game.player1.commander) {
            const commander = game.player1.commander;
            commanderCount[commander] = (commanderCount[commander] || 0) + 1;
        }
    });
    
    const mostUsed = Object.entries(commanderCount).sort(([,a], [,b]) => b - a)[0];
    return mostUsed ? `${mostUsed[0]} (${mostUsed[1]}次)` : '无数据';
}

// 导出统计数据
function exportStats() {
    const data = {
        filters: statsData.currentFilters,
        games: statsData.filteredGames,
        exportTime: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `sc2_stats_export_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    URL.revokeObjectURL(url);
}

// 其他标签页初始化函数
function initMutatorStats() {
    console.log('初始化突变因子统计页面');
}

function initCustomMaps() {
    console.log('初始化自定义地图页面');
}