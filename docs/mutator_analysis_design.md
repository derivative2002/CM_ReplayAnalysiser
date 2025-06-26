# 突变因子分析功能设计文档

## 功能概述
基于已有的突变因子追踪逻辑，实现Web界面的突变因子综合分析功能，提供突变因子统计、特殊单位击杀统计、AI分析等功能。

## 核心功能

### 1. 突变因子统计
- **出现频率**: 每个突变因子在所有游戏中的出现次数和百分比
- **组合分析**: 常见的突变因子组合
- **难度分布**: 不同难度下的突变因子分布
- **时间趋势**: 突变因子随时间的变化趋势

### 2. 特殊单位击杀统计
基于ReplayAnalysis.py中已有的追踪逻辑：
- **Void Rifts** (虚空裂缝): 击杀数量统计
- **Propagators** (传播者): 击杀数量统计
- **Time Units** (时间单位): 击杀数量统计
- **Void Reanimators** (虚空复活者): 击杀数量统计
- 其他突变特定单位

### 3. 敌人AI分析
- **AI种族分布**: 遭遇的AI种族（虫族/人族/神族）
- **AI组成分析**: 混合AI的组成情况
- **地图-AI关联**: 不同地图上的AI倾向

### 4. 成功率分析
- **突变因子胜率**: 每个突变因子的胜率
- **组合胜率**: 不同突变因子组合的胜率
- **指挥官表现**: 不同指挥官对抗特定突变的表现

## 数据结构

### API响应格式
```json
{
  "mutator_stats": {
    "total_mutation_games": 45,
    "mutators": {
      "Void Rifts": {
        "count": 12,
        "percentage": 26.7,
        "win_rate": 83.3,
        "avg_completion_time": 1234
      },
      "Just Die": {
        "count": 8,
        "percentage": 17.8,
        "win_rate": 62.5,
        "avg_completion_time": 1456
      }
    }
  },
  "special_kills": {
    "voidrifts": {
      "total": 234,
      "avg_per_game": 19.5,
      "player_distribution": {
        "player1": 142,
        "player2": 92
      }
    },
    "propagators": {
      "total": 567,
      "avg_per_game": 47.3
    }
  },
  "enemy_composition": {
    "Zerg": 45,
    "Terran": 38,
    "Protoss": 42,
    "Mixed": 15
  },
  "commander_performance": {
    "Zagara": {
      "vs_voidrifts": {"games": 5, "win_rate": 80},
      "vs_justdie": {"games": 3, "win_rate": 66.7}
    }
  }
}
```

## 前端UI设计

### 页面布局
```
+----------------------------------+
|        突变因子概览              |
| [总突变游戏数] [平均胜率] [难度] |
+----------------------------------+
|        突变因子分布图            |
|     [饼图/柱状图切换]            |
+----------------------------------+
|        特殊单位击杀统计          |
| [雷达图展示各类特殊单位击杀]     |
+----------------------------------+
|        详细统计表格              |
| 突变因子 | 次数 | 胜率 | 特殊击杀 |
+----------------------------------+
|        指挥官表现矩阵            |
| [热力图展示指挥官vs突变因子]     |
+----------------------------------+
```

## 实现步骤

### 1. 后端增强 (real_data_server.py)
- 集成IdentifyMutators.py的突变识别逻辑
- 提取特殊单位击杀数据
- 添加新的API端点:
  - `/api/mutator/overview` - 突变因子概览
  - `/api/mutator/kills` - 特殊单位击杀统计
  - `/api/mutator/performance` - 指挥官表现数据

### 2. 数据处理
- 从replay_cache中提取突变相关数据
- 计算统计指标
- 聚合特殊单位击杀数据

### 3. 前端实现
- 替换当前的游戏因子分析页面
- 使用Chart.js创建可视化图表:
  - 饼图: 突变因子分布
  - 雷达图: 特殊单位击杀分布
  - 热力图: 指挥官-突变因子表现矩阵
- 实现交互式筛选和排序

## 技术要点

### 突变因子识别
```python
# 需要集成的关键函数
from SCOFunctions.IdentifyMutators import identify_mutators

# 特殊单位追踪 (已在ReplayAnalysis.py中实现)
if _killed_unit_type == 'MutatorVoidRift':
    custom_kill_count['voidrifts'][_killing_player] += 1
```

### 数据聚合
- 遍历所有回放数据
- 提取mutators字段
- 统计特殊单位击杀
- 计算各项指标

### 可视化
- Chart.js配置突变因子主题色
- 响应式图表设计
- 交互式工具提示

## 扩展功能

### 1. 突变因子推荐
- 基于玩家历史表现推荐适合的突变因子
- 提供突变因子攻略建议

### 2. 对比分析
- 与其他玩家的突变表现对比
- 时间段对比（本周vs上周）

### 3. 成就追踪
- 突变相关成就完成情况
- 特殊击杀里程碑