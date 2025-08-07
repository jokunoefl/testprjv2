#!/usr/bin/env python3
import os
import uvicorn

port = 8000  # 固定ポート
print(f"Railway最小起動 - ポート: {port}")

uvicorn.run("main:app", host="0.0.0.0", port=port) 