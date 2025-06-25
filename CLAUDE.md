# Claude Code 操作规范和项目记录

## 标准工作流程

1. **问题分析和规划**：首先分析问题，阅读相关代码，制定详细计划到 projectplan.md
2. **计划确认**：与用户确认计划后开始执行
3. **任务执行**：逐项完成待办事项，及时标记完成状态
4. **进度汇报**：每步都提供简洁的高层次说明
5. **简化原则**：每个任务和代码变更都尽可能简单，影响最小的代码范围
6. **最终总结**：在计划文件中添加变更总结和相关信息

## 项目背景

**星际争霸2合作模式回放分析工具 (SC2 Coop Overlay)**：用于分析星际争霸2合作模式回放的桌面应用程序

### 核心目标
- 提供实时游戏覆盖层显示回放分析结果
- 统计和分析玩家在合作模式中的表现
- 支持直播串流集成（OBS等）
- 提供详细的游戏统计和历史记录

### 关键组件
- **SCO.py**: 主程序入口和应用程序框架
- **SCOFunctions/**: 核心功能模块集合
- **Layouts/**: UI布局和资源文件
- **web/**: Web界面相关文件
- **src/**: 图像资源和配置文件

## 技术架构

### 主要技术栈
- **GUI框架**: PyQt5
- **回放解析**: s2protocol (暴雪官方库)
- **Web服务**: WebSockets服务器
- **快捷键**: keyboard库
- **系统监控**: psutil

### 核心模块结构
```
SCOFunctions/
├── AppFunctions.py          # 应用程序核心功能
├── MainFunctions.py         # 主要业务逻辑
├── ReplayAnalysis.py        # 回放分析逻辑
├── MassReplayAnalysis.py    # 批量回放分析
├── S2Parser.py              # 星际争霸2回放解析器
├── Settings.py              # 设置管理
├── MUserInterface.py        # 用户界面管理
├── Tabs/                    # 各个功能标签页
└── SC2Dictionaries/         # 游戏数据映射
```

## 重要操作记录

### 项目初始状态 (2025-06-24)
- 项目已完成基本开发，版本2.47
- 包含完整的GUI界面和核心功能
- 支持中文本地化
- 具备完整的回放分析能力

### 完成的主要任务 (2025-06-25)

1. **Web界面真实数据集成**
   - 创建了`real_data_server.py`集成真实回放数据
   - 修复了只显示5个回放的限制，现在显示全部19个
   - 修复了游戏时长显示为0的问题
   - 添加了中文指挥官名称映射

2. **数据质量改进**
   - 正确提取玩家名称和指挥官信息
   - 支持中文玩家名显示
   - 统计数据基于真实回放计算

3. **远程访问支持**
   - 配置服务器监听0.0.0.0支持远程访问
   - 提供了多种端口转发方案
   - 更新为3000端口避免冲突

4. **项目清理**
   - 删除了临时测试脚本
   - 清理了旧的日志文件
   - 保持了项目结构整洁

## 常用命令和路径

### 关键文件路径
- 主程序: `SCO.py`
- Web服务器: `real_data_server.py`
- 配置文件: `SCOFunctions/Settings.py`
- 需求文件: `requirements.txt`
- 版本信息: `version.txt`
- 项目计划: `projectplan.md`

### 运行命令
```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python SCO.py

# 使用虚拟环境
_venv.bat  # Windows批处理文件

# 启动Web界面服务器
python3 real_data_server.py
```

### 远程开发访问

当在远程服务器上开发时，有以下几种访问Web界面的方式：

1. **SSH端口转发**（推荐）：
   ```bash
   # 在本地终端运行
   ssh -L 3000:localhost:3000 user@server_ip
   # 然后访问 http://localhost:3000
   ```

2. **VS Code端口转发**：
   - 按 F1 或 Ctrl+Shift+P
   - 搜索"Forward a Port"
   - 输入端口号: 3000
   - 选择转发方式（Local）
   - 访问 http://localhost:3000

3. **JetBrains IDE端口转发**：
   - 在IDE底部找到"Port Forwarding"面板
   - 点击 + 添加新转发
   - Remote port: 3000, Local port: 3000
   - 访问 http://localhost:3000

4. **直接访问**（如果防火墙允许）：
   - 访问: `http://<服务器IP>:3000`
   - 例如: `http://172.18.1.8:3000`

**注意**：IDE端口自动转发有时不稳定，建议使用手动SSH端口转发。

### 项目结构
- 当前分支: `master`
- 项目类型: 桌面应用程序
- 目标平台: Windows (主要), MacOS, Linux

---

*最后更新: 2025-06-24*