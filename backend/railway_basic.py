#!/usr/bin/env python3
"""
Railway用の最も基本的な起動スクリプト
環境変数の問題を完全に回避するアプローチ
"""

import os
import uvicorn

# 最もシンプルな起動
port = int(os.environ.get("PORT", 8000))
print(f"Railway基本起動 - ポート: {port}")

uvicorn.run("main:app", host="0.0.0.0", port=port) 