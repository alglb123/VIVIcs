# 可视化智能语音交互控制系统

基于 Python 的智能家居控制系统，支持语音指令、手势识别、声纹身份验证，配合 Canvas 仿真建模实时展示设备状态。

## 功能模块

| 模块 | 功能 |
|------|------|
| 模块一 | 基础框架、EventBus 事件总线、工程目录结构 |
| 模块二三 | 指令系统、设备状态管理、CustomTkinter GUI + Canvas 仿真建模 |
| 模块四 | 麦克风录音、环境降噪、Google STT 中文语音识别、多线程后台监听 |
| 模块五 | MediaPipe 手势识别（手掌/握拳/比耶/举手）、OpenCV 可视化窗口 |
| 模块六 | resemblyzer 声纹注册与校验，非授权用户拒绝执行 |

## 环境要求

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) 包管理器

## 快速开始

```bash
uv sync
uv run python main.py
```

## 使用说明

### 语音控制
1. 点击 **🎤 开始监听**，按钮变红表示监听中
2. 对麦克风说出指令（如"打开空调"、"关闭灯光"）
3. 识别结果自动执行，Canvas 仿真视图实时刷新

支持指令：`打开/关闭空调`、`打开/关闭灯光`、`打开/关闭风扇`

### 手势控制
1. 点击 **✋ 开始手势**，弹出摄像头窗口
2. 对摄像头做出手势，左上角显示识别结果

| 手势 | 指令 |
|------|------|
| 手掌张开（四指伸直） | 打开灯光 |
| 握拳（四指弯曲） | 关闭灯光 |
| 比耶 ✌ | 打开空调 |
| 举手 ☝ | 关闭空调 |

按 `q` 或关闭窗口停止手势识别。

### 声纹注册
1. 点击 **🔐 注册声纹**，按日志提示录制 3 段语音（各 5 秒）
2. 注册完成后，每次语音指令前自动校验身份
3. 相似度低于阈值（默认 0.75）时拒绝执行

可在 `config.py` 中调整 `VOICEPRINT_THRESHOLD`。

## 项目结构

```
├── main.py
├── config.py
├── hand_landmarker.task         # MediaPipe 手部关键点模型
├── modules/
│   ├── event_bus.py             # 事件总线（线程安全）
│   ├── control/
│   │   ├── command_dict.py      # 指令字典
│   │   ├── device_state.py      # 设备状态管理
│   │   └── executor.py          # 指令执行器
│   ├── gui/
│   │   ├── main_window.py       # 主窗口
│   │   ├── device_panel.py      # 设备指示灯面板
│   │   ├── log_panel.py         # 日志输出面板
│   │   └── room_canvas.py       # Canvas 仿真建模
│   ├── voice/
│   │   └── listener.py          # 语音采集 + 降噪 + ASR
│   ├── gesture/
│   │   └── detector.py          # 手势检测 + 可视化
│   └── voiceprint/
│       ├── enroll.py            # 声纹注册
│       └── verifier.py          # 声纹校验
```

## 依赖说明

| 库 | 用途 |
|----|------|
| [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | 现代化 GUI 框架 |
| [SpeechRecognition](https://github.com/Uberi/speech_recognition) | 语音识别接入 Google STT |
| [noisereduce](https://github.com/timsainburg/noisereduce) | 环境降噪 |
| [mediapipe](https://github.com/google-ai-edge/mediapipe) | 手部关键点检测 |
| [resemblyzer](https://github.com/resemble-ai/Resemblyzer) | 声纹嵌入向量提取 |
| [opencv-python](https://github.com/opencv/opencv-python) | 摄像头采集与可视化 |
