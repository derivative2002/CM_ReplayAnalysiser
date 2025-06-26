# 游戏因子分析功能设计文档

## 概述
将"Weekly Mutations"功能替换为"游戏因子分析和统计"功能，提供每场游戏的详细因子分析。

## 功能设计

### 1. 因子类别
- **地图因子**: 地图特性、布局复杂度、资源分布
- **难度因子**: 游戏难度、突变因子（如有）
- **性能因子**: APM、单位控制效率、资源采集效率
- **战斗因子**: 击杀效率、损失比率、DPS
- **协作因子**: 与盟友的配合度、资源共享
- **时间因子**: 游戏时长、关键时间点

### 2. 数据结构
```python
game_factors = {
    "game_id": "unique_id",
    "map_factors": {
        "map_name": str,
        "map_size": str,  # small/medium/large
        "enemy_composition": str,
        "objective_type": str
    },
    "performance_factors": {
        "player1": {
            "apm": float,
            "resource_efficiency": float,
            "unit_control_score": float
        },
        "player2": {...}
    },
    "combat_factors": {
        "total_kills": int,
        "kill_death_ratio": float,
        "damage_dealt": int,
        "damage_taken": int
    },
    "cooperation_factors": {
        "sync_score": float,  # 协同作战评分
        "resource_sharing": int,
        "combined_attacks": int
    },
    "difficulty_factors": {
        "base_difficulty": int,
        "mutators": list,
        "adjusted_difficulty": float
    }
}
```

### 3. 前端UI设计

#### 3.1 标签页更新
- 将"Weeklies"标签改为"游戏因子分析"
- 保留现有布局结构，重新设计内容

#### 3.2 页面布局
```
+----------------------------------+
|        游戏选择器                |
| [下拉菜单: 选择游戏]             |
+----------------------------------+
|        因子分析雷达图            |
|     [Chart.js雷达图]             |
+----------------------------------+
|        详细因子列表              |
| - 地图因子: [详细数据]           |
| - 性能因子: [详细数据]           |
| - 战斗因子: [详细数据]           |
| - 协作因子: [详细数据]           |
+----------------------------------+
|        对比分析                  |
| [与历史平均值对比]               |
+----------------------------------+
```

### 4. API设计

#### 4.1 获取游戏因子分析
```
GET /api/game/factors/{game_id}
Response: {
    "status": "success",
    "data": {game_factors}
}
```

#### 4.2 获取因子统计
```
GET /api/factors/statistics
Response: {
    "status": "success", 
    "data": {
        "average_factors": {...},
        "factor_trends": {...}
    }
}
```

### 5. 实现步骤
1. 修改后端解析逻辑，提取因子数据
2. 创建因子分析API端点
3. 更新前端HTML结构
4. 实现因子可视化（雷达图）
5. 添加游戏选择和对比功能

### 6. 技术考虑
- 使用Chart.js绘制雷达图
- 因子数据缓存以提高性能
- 支持实时更新当前游戏因子