# 用户激励系统后端

基于机器学习的个性化激励推荐系统后端，采用FastAPI框架，提供RESTful API接口。

## 项目结构

```
backend/
├── app/                        # 应用主目录
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py               # 配置文件
│   ├── database.py             # 数据库连接
│   ├── models/                 # SQLAlchemy数据模型
│   ├── schemas/                # Pydantic验证schema
│   ├── api/                    # API路由
│   ├── services/               # 业务逻辑服务
│   ├── ml/                     # 机器学习模块
│   └── utils/                  # 工具函数
├── data/                       # 数据目录
├── tests/                      # 测试文件
├── requirements.txt            # 依赖包
├── Dockerfile                  # Docker配置
└── README.md                   # 项目说明
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
uvicorn app.main:app --reload
```

应用将在 `http://localhost:8000` 上运行。

### API文档

- Swagger文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc

## 数据库

使用MySQL数据库，需要先创建数据库：

```sql
CREATE DATABASE incentive_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `app/config.py` 中的 `DATABASE_URL` 配置数据库连接。

## Docker部署

```bash
docker build -t incentive-system .
docker run -p 8000:8000 incentive-system
```
