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
    updateGamesList();
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
    const gamesList = document.getElementById('games-list');
    
    if (gameHistory.length === 0) {
        gamesList.innerHTML = '<div class="waiting-message"><b>Please wait. This can take few minutes the first time.<br>Analyzing your replays.</b></div>';
        return;
    }
    
    let html = '';
    gameHistory.forEach((game, index) => {
        html += createGameEntry(game, index);
    });
    
    gamesList.innerHTML = html;
}

function createGameEntry(game, index) {
    const resultClass = game.result === 'Victory' ? 'victory' : 'defeat';
    
    return `
        <div class="game-entry" data-index="${index}">
            <div class="game-map">${game.mapName || '未知地图'}</div>
            <div class="game-result ${resultClass}">${game.result || '未知'}</div>
            <div class="game-player1">${game.player1?.name || '玩家1'} (${game.player1?.commander || '未知指挥官'})</div>
            <div class="game-player2">${game.player2?.name || '玩家2'} (${game.player2?.commander || '未知指挥官'})</div>
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
function initStatistics() {
    initCharts();
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

    ws = new WebSocket('ws://localhost:7307');

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