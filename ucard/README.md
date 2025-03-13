# UCard管理系统

UCard管理系统是一个基于Flask和Layui的跨境支付管理平台，用于企业管理吉薪卡、工资支付等功能。

## 已完成功能
- 登录操作
- 用卡人查询
- 交易记录查询
- 添加用卡人
- 额度查询
- ...

## 项目结构

```
ucard/
├── blueprint/          # 蓝图包
│   └── main.py         # 主蓝图
│   └── auth.py
├── static/             # 静态资源
│   ├── css/            # CSS样式
│   ├── js/             # JavaScript文件
│   ├── images/         # 图片资源
│   └── layui/          # Layui框架
├── templates/          # 模板文件
│   ├── auth/           # 认证相关
│   ├── main/           # 主要功能
│   └── error/          # 错误页面
├── views/              # 
├── app.py              # 应用程序入口
└── requirements.txt    # 依赖包
```

## 功能模块

- 账户管理：钱包功能
- 企业用户：充值功能
- 工资&付款：收款人、付款人、付款
- 吉薪卡：用卡人、交易明细、额度、所有卡
- 统计分析：日报、周报、月报、年报、异常
- 系统维护：钱包管理、本地设置、国家设置、更新时间、添加平台、密码修改
- 汇率报价：汇率信息

## 安装运行

1. 创建虚拟环境（推荐）：
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

3. 运行应用：
   ```
   python app.py
   ```

4. 访问应用：
   打开浏览器访问 http://localhost:5000

## 技术栈

- 后端：Flask + SQLAlchemy
- 数据库：MariaDB
- 前端：Layui + jQuery

