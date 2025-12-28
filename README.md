# swt_and-_wzt_Database_Experiment_Assignment
Database code
# 📚 图书馆管理系统

一个基于Flask + SQLite的完整图书馆管理系统，提供管理员和读者两种角色，涵盖图书管理、借阅管理、入库报损、罚款缴费等核心功能。

## 🌟 功能特性

### 👨‍💼 管理员功能

- **管理员面板**：数据统计、图表展示、系统概览、管理员功能
- **图书管理**：图书增删改查
- **读者管理**：读者信息管理、借阅卡管理、挂失解挂
- **借阅管理**：借书/还书/续借、借阅查询
- **图书入库**：图书入库、入库记录查询、库存更新
- **报损管理**：图书报损登记、报损记录查看
- **查询统计**：图书数据统计、图表分析、报表导出

### 👤 读者功能

- **读者面板**：借阅卡信息、借阅状态、读者功能
- **图书查询**：图书查询、在线借书
- **我的借阅**：个人借阅记录
- **罚款缴费**：查看罚款、在线缴费
- **个人信息**：个人基本信息、借阅卡信息、密码修改
- **借阅卡管理**：借阅卡信息、卡片续期、卡片挂失
- **借阅统计**：个人借阅统计、阅读偏好分析

## 🛠️ 技术栈

- **后端框架**：Flask (Python)
- **数据库**：SQLite3
- **前端技术**：HTML5、JavaScript、Chart.js、Tailwind CSS + DaisyUI组件库
- **数据验证**：服务器端验证 + 客户端验证

## 📁 项目结构

```
library_system/
├── app.py                    # 主应用程序文件
├── library.db               # SQLite数据库文件
├── templates/               # HTML模板文件
│   ├── add_book.html
│   ├── add_reader.html
│   ├── admin_books.html
│   ├── admin_dashboard.html
│   ├── borrow_manage.html
│   ├── damage.html
│   ├── edit_book.html
│   ├── edit_reader.html
│   ├── index.html
│   ├── login.html
│   ├── reader_borrows.html
│   ├── reader_card.html
│   ├── reader_dashboard.html
│   ├── reader_fines.html
│   ├── reader_profile.html
│   ├── reader_search.html
│   ├── reader_stats.html
│   ├── readers.html
│   ├── register.html
│   ├── reports.html
│   ├── search_readers.html
│   └── stock.html
├── requirements.txt        # 项目依赖
└── README.md               # 项目说明文档
```



## 🚀 快速开始

```cmd
conda create -n library python=3.11
conda activate library
pip install -r requirements.txt
python app.py # 首次运行会自动创建数据库和初始数据
```

​	本地访问 http://localhost:5000，即可开始使用图书馆管理系统

## 🔐 登录账户

### 管理员账户

- **用户名**：`admin`
- **密码**：`admin123`
- **权限**：完整系统管理权限

### 测试读者账户

1. **读者001**
   - 用户名：`reader001`
   - 密码：`reader123`
   - 卡号：`C001`
2. **读者002**
   - 用户名：`reader002`
   - 密码：`reader123`
   - 卡号：`C002`

### 新读者注册

- 访问注册页面可注册新读者账户

## 📊 数据库设计

### 核心数据表

1. **book** - 图书信息表
2. **reader** - 读者信息表
3. **bookcredit** - 借阅卡表
4. **borrow** - 借阅记录表
5. **fine** - 罚款记录表
6. **fine_detail** - 罚款详情表
7. **payment** - 缴费记录表
8. **bookstocking** - 入库单表
9. **bookstockingdetail** - 入库明细表
10. **breakage** - 报损单表
11. **breakagedetail** - 报损单详情表
12. **publisher** - 出版社表
13. **booktype** - 图书分类表
14. **manager** - 管理员表

## 🔧 配置说明

### 数据库配置

- 数据库文件：`library.db`
- 自动初始化：包含初始测试数据

### 会话配置

- 密钥：`library_management_system`
- 超时：浏览器会话期间有效

### 服务器配置

- 主机：`0.0.0.0` (所有网络接口)
- 端口：`5000`
- 调试模式：启用

## 📈 业务规则

### 借阅规则

- 默认借期：30天
- 续借次数：1次
- 最大借阅量：默认5本，可通过管理员权限修改为1~20本
- 逾期罚款：1元/天

### 罚款规则

- 逾期罚款：逾期天数 × 1元
- 损坏罚款：图书价格的50%
- 丢失罚款：图书价格的200%

### 入库规则

- 入库单号唯一
- 入库后自动更新库存
- 支持批量入库，单次入库数量范围为1~1000本

### 报损规则

- 报损单号唯一
- 报损数量不能超过库存
- 支持批量报损，单次报损数量范围为1~100本
- 报损后减少库存

## 📄 许可证

本项目仅供学习和参考使用，未经许可不得用于商业用途。
