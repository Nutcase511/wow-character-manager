# -*- coding: utf-8 -*-
# 后端启动脚本
import sys, os

# 确保 backend 目录在路径中
os.chdir(r'C:\wow后台管理\wow-character-manager\backend')
sys.path.insert(0, r'C:\wow后台管理\wow-character-manager\backend')

# 启动 uvicorn（不使用 --reload 以避免 Windows multiprocessing 问题）
import uvicorn
uvicorn.run('main:app', host='0.0.0.0', port=8000, log_level='info')