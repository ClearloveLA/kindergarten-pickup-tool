# Kindergarten Pickup

一个基于 Python Tkinter 的幼儿园离园接送登记小工具，用于记录孩子、班级、家长、老师、安全员和接送时间，并支持语音广播提醒。

## 功能特点

- 接送登记：记录孩子姓名、班级、家长、老师、安全员和接送时间
- 记录查看：表格展示当日或本地保存的接送记录
- 语音广播：对指定孩子进行离园提醒播报，默认重复 3 次
- 人员维护：可临时新增班级、老师和安全员选项
- 本地存储：使用 `pickup_data.json` 保存运行数据，适合轻量场景快速使用

## 技术栈

- Python
- Tkinter / ttk
- pyttsx3
- JSON 本地存储

## 运行方式

```bash
pip install -r requirements.txt
python kindergarten_pickup_app.py
```

运行后会在项目目录下自动生成 `pickup_data.json`。该文件属于本地运行数据，默认不会提交到仓库，避免误传学生或家长信息。

## 项目结构

```text
kindergarten_pickup/
├── kindergarten_pickup_app.py  # 主程序
├── requirements.txt            # 依赖列表
├── .gitignore                  # 忽略运行数据与缓存
└── README.md                   # 项目说明
```

## 适用场景

这个项目适合作为幼儿园、托管班、小型培训机构的离园登记原型工具，也可以作为 Tkinter GUI、JSON 本地存储和 Python 语音播报的学习示例。

## 注意事项

- `pickup_data.json` 中可能包含学生和家长姓名，请仅在本地使用，不建议上传到公开仓库。
- 语音播报依赖系统语音环境，不同操作系统上的中文语音效果可能不同。
- 当前项目定位为轻量桌面工具，如果用于真实生产环境，建议继续加入权限控制、数据加密、备份和多端同步。

