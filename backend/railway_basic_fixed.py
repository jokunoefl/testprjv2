#!/usr/bin/env python3
import uvicorn

print("Railway基本固定起動")
uvicorn.run("main:app", host="0.0.0.0", port=8000) 