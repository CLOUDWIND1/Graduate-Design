# 全民获客智能推荐系统

基于机器学习的个性化激励推荐系统，通过分析用户画像特征，为用户精准推荐适合的营销活动，提升用户参与率和转化率。

## 🚀 技术栈

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Element Plus** - 基于 Vue 3 的组件库
- **Vite** - 下一代前端构建工具
- **Pinia** - Vue 状态管理
- **Vue Router** - 官方路由管理器
- **ECharts** - 数据可视化图表库

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **SQLAlchemy** - Python ORM 框架
- **Pydantic** - 数据验证库
- **MySQL** - 关系型数据库
- **scikit-learn** - 机器学习库

## 📁 项目结构

```
Graduate-Design/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── api/             # API 接口封装
│   │   ├── assets/          # 静态资源
│   │   ├── components/      # 公共组件
│   │   ├── router/          # 路由配置
│   │   ├── store/           # 状态管理
│   │   └── views/           # 页面组件
│   └── package.json
│
├── backend/                  # 后端项目
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # Pydantic 验证
│   │   ├── services/        # 业务逻辑
│   │   └── ml/              # 机器学习模块
│   ├── .env                 # 环境变量配置（不上传）
│   └── requirements.txt
│
└── README.md                # 项目说明
```

## ⚙️ 环境要求

- Node.js >= 16.0
- Python >= 3.9
- MySQL >= 8.0

## 🛠️ 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/CLOUDWIND1/Graduate-Design.git
cd Graduate-Design
```

### 2. 配置数据库

```sql
CREATE DATABASE recommendation_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 启动后端

```bash
cd backend

# 创建虚拟环境（可选）
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 复制 .env.example 为 .env 并修改数据库连接信息

# 启动服务
uvicorn app.main:app --reload --port 8000
```

后端 API 文档：http://localhost:8000/docs

### 4. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端访问地址：http://localhost:5173

## 📖 功能模块

### 用户端
- 🔐 用户注册/登录
- 📝 个性化问卷（用户画像采集）
- 🎯 智能活动推荐
- 🔄 换一批推荐
- 👤 个人中心与偏好设置

### 管理端
- 📊 数据看板（用户统计、活动效果）
- 👥 用户管理
- 🎪 活动管理
- 📈 推荐效果分析

## 🧠 推荐算法

系统采用基于用户画像的协同过滤推荐算法：
1. **因子分析**：提取用户六维特征（社交、心理、激励、技术、环境、个人）
2. **K-Means 聚类**：将用户分为不同群体
3. **随机森林模型**：预测用户对活动的参与概率
4. **个性化排序**：结合匹配度和多样性生成推荐列表

## 📄 License

MIT License
