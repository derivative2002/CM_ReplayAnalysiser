#!/usr/bin/env python3
"""
Web服务器模块 - 提供Web界面来展示SC2回放分析数据
"""
import asyncio
import json
import os
import threading
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any

import websockets

from SCOFunctions.MLogging import Logger
from SCOFunctions.Settings import Setting_manager as SM

logger = Logger('WebServer', Logger.levels.INFO)

# 存储最新的回放数据
latest_replay_data = {}
connected_clients = set()


class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def __init__(self, *args, **kwargs):
        # 设置web目录为根目录
        super().__init__(*args, directory="web", **kwargs)
    
    def end_headers(self):
        # 添加CORS头部，允许跨域访问
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/api/latest_replay':
            # 返回最新的回放数据
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(latest_replay_data).encode())
        elif self.path == '/api/status':
            # 返回服务器状态
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = {
                'connected': True,
                'websocket_clients': len(connected_clients),
                'latest_update': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            # 默认文件服务
            super().do_GET()


async def websocket_client():
    """WebSocket客户端 - 连接到主应用的WebSocket服务器"""
    uri = "ws://localhost:7305"
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("已连接到主应用WebSocket服务器")
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        
                        # 更新最新的回放数据
                        if 'replaydata' in data:
                            global latest_replay_data
                            latest_replay_data = data
                            logger.info(f"收到新的回放数据: {data.get('MapName', 'Unknown')}")
                            
                            # 转发给所有连接的Web客户端
                            if connected_clients:
                                await asyncio.gather(
                                    *[client.send(message) for client in connected_clients],
                                    return_exceptions=True
                                )
                    except json.JSONDecodeError:
                        logger.error(f"无法解析消息: {message}")
                    except Exception as e:
                        logger.error(f"处理消息时出错: {e}")
                        
        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")
            await asyncio.sleep(5)  # 5秒后重试


async def handle_web_client(websocket, path):
    """处理Web客户端的WebSocket连接"""
    connected_clients.add(websocket)
    logger.info(f"Web客户端已连接: {websocket.remote_address}")
    
    try:
        # 发送最新的回放数据（如果有）
        if latest_replay_data:
            await websocket.send(json.dumps(latest_replay_data))
            
        # 保持连接
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        logger.info(f"Web客户端已断开: {websocket.remote_address}")


def run_http_server(port=8082):
    """运行HTTP服务器"""
    server = HTTPServer(('0.0.0.0', port), CustomHTTPRequestHandler)
    logger.info(f"HTTP服务器启动在 http://0.0.0.0:{port}")
    server.serve_forever()


async def main():
    """主函数"""
    # 启动HTTP服务器
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # 启动WebSocket服务器（供Web客户端连接）
    web_ws_server = await websockets.serve(handle_web_client, "0.0.0.0", 7308)
    logger.info("Web WebSocket服务器启动在 ws://0.0.0.0:7308")
    
    # 启动WebSocket客户端（连接到主应用）
    client_task = asyncio.create_task(websocket_client())
    
    # 保持运行
    await asyncio.gather(
        web_ws_server.wait_closed(),
        client_task
    )


if __name__ == "__main__":
    # 创建web目录
    os.makedirs("web", exist_ok=True)
    
    # 运行服务器
    asyncio.run(main())