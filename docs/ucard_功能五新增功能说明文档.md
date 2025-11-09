# 新增功能文档说明

**修改时间**: 2025-11-09

---

## 一、新增功能总结

### 1.1 用卡人Telegram邮箱管理功能

**功能描述**: 在用卡人管理页面新增Telegram邮箱字段的显示、编辑和存储功能

**具体功能**:
- 在用卡人页面表格中新增"Telegram邮箱"列，位于"邮箱"列右侧
- Telegram邮箱列默认显示邮箱的值（如果telegram_email为空）
- 用卡人编辑页面新增Telegram邮箱输入框，支持独立编辑
- 编辑保存后数据同步到card_holder表的telegram_email字段
- 保持与现有邮箱字段的独立性，可分别管理

**功能目的**:
- 支持用户管理多个邮箱地址，满足不同通信渠道需求
- 为Telegram通知功能提供数据基础
- 提升用户信息管理的灵活性和完整性
- 保持数据的向后兼容性，不影响现有功能

---

## 二、文件变更清单

### 2.1 修改文件

#### 文件1: 用卡人页面JavaScript文件
- **更改类型**: 修改
- **文件路径**: `ucard/static/js/card_holders.js`
- **变更行号范围**: 第87-91行
- **变更内容概述**: 
  - 在表格列定义中新增telegram_email字段
  - 添加模板函数处理默认值显示逻辑
  - 如果telegram_email为空则显示email的值

#### 文件2: 用卡人编辑页面HTML模板
- **更改类型**: 修改
- **文件路径**: `ucard/templates/main/card_user_edit.html`
- **变更行号范围**: 第68-112行
- **变更内容概述**:
  - 在邮箱输入框右侧新增Telegram邮箱输入框
  - 调整表单布局，将手机号移至下一行
  - 添加邮箱验证规则和占位符文本

#### 文件3: 用卡人编辑JavaScript文件
- **更改类型**: 修改
- **文件路径**: `ucard/static/js/card_holder_edit.js`
- **变更行号范围**: 第27行, 第97行
- **变更内容概述**:
  - 在表单数据加载时添加telegram_email字段处理
  - 如果telegram_email为空，使用email作为默认值
  - 在数据转换函数中添加telegram_email字段传递

#### 文件4: 后端API文件
- **更改类型**: 修改
- **文件路径**: `ucard/blueprint/main.py`
- **变更行号范围**: 第402-449行
- **变更内容概述**:
  - 在用卡人编辑API中提取telegram_email字段
  - 外部API更新成功后，单独更新本地数据库telegram_email字段
  - 添加详细的调试日志和错误处理

### 2.2 新增文件
无新增文件

### 2.3 删除文件
无删除文件

---

## 三、数据库变更

### 3.1 表结构变更
**变更状态**: 新增字段

**表名**: `card_holder`

**新增字段**:
- **字段名**: `telegram_email`
- **数据类型**: `VARCHAR(255)`
- **是否允许NULL**: 是
- **默认值**: NULL
- **注释**: Telegram邮箱

**SQL语句**:
```sql
ALTER TABLE card_holder ADD COLUMN telegram_email VARCHAR(255) NULL COMMENT 'Telegram邮箱';
UPDATE card_holder SET telegram_email = email WHERE email IS NOT NULL AND email != '';
```

**说明**: 
- 新增telegram_email字段用于存储用户的Telegram邮箱地址
- 执行UPDATE语句将现有的email值复制到telegram_email作为默认值
- 保持数据完整性，确保现有用户也有telegram_email数据

---

## 四、技术实现说明

### 4.1 实现原理
- **数据显示**: 前端表格优先显示telegram_email，为空时显示email值
- **数据编辑**: 表单加载时如果telegram_email为空，自动填入email值作为默认值
- **数据存储**: 外部API更新其他字段，本地数据库单独更新telegram_email字段
- **数据同步**: 确保前端显示与数据库存储的一致性

### 4.2 核心功能实现

#### 4.2.1 前端显示逻辑
```javascript
{field: 'telegram_email', title: 'Telegram邮箱', width: 210, templet: function(d){
    // 如果telegram_email为空，则显示email的值
    return d.telegram_email || d.email || '';
}}
```

#### 4.2.2 表单默认值处理
```javascript
"telegram_email": data.telegram_email || data.email, // 如果telegram_email为空，使用email作为默认值
```

#### 4.2.3 后端数据处理
```python
telegram_email = data.pop('telegram_email', None)  # 提取telegram_email字段
# 外部API更新成功后，同步更新本地数据库
if telegram_email is not None:
    local_update_data = {'telegram_email': telegram_email}
    condition = {'card_holder_id': card_holder_id}
    local_result = update_database('card_holder', local_update_data, condition)
```

### 4.3 数据流程
1. **页面加载**: 从card_holder表查询数据，包含telegram_email字段
2. **表格显示**: 优先显示telegram_email，为空时显示email
3. **编辑操作**: 点击编辑按钮，表单自动填入telegram_email或email作为默认值
4. **数据提交**: 前端提交包含telegram_email的完整数据
5. **后端处理**: 外部API更新基础信息，本地数据库更新telegram_email
6. **数据同步**: 确保显示数据与存储数据一致

### 4.4 兼容性说明
- **向后兼容**: 对于没有telegram_email数据的记录，自动显示email值
- **数据完整性**: 新增字段不影响现有功能和数据结构
- **渐进增强**: 功能可选使用，不强制要求填写telegram_email

---

## 五、使用说明

### 5.1 部署步骤
1. 执行数据库变更SQL语句，添加telegram_email字段
2. 重启应用服务
3. 访问用卡人页面验证新列显示正常
4. 测试编辑功能确保数据保存正确

### 5.2 功能验证
1. **显示验证**: 用卡人页面表格中应显示"Telegram邮箱"列
2. **默认值验证**: 对于新字段为空的记录，应显示邮箱的值
3. **编辑验证**: 编辑用卡人时应显示Telegram邮箱输入框
4. **保存验证**: 修改后应正确保存到数据库telegram_email字段

### 5.3 注意事项
- 确保数据库连接正常，避免本地更新失败
- 建议在测试环境先验证功能完整性
- 如需回滚，可删除telegram_email字段，不影响其他功能
