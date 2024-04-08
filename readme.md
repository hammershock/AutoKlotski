# 自动求解华容道(klotski)

```bash
pip install -r requirements.txt
```
1. 拖动滑块以移动方块
2. 按s键进入自动求解
3. 可以自由编辑起始状态和终止状态，默认代表空的编号为0
4. 提供对于A*算法的 c extensions:
   先运行build.sh
   然后设置`accelerate=True`加速求解

