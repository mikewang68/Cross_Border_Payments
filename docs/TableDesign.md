数据库设计
3.2.1 管理员 admins表
中文含义	英文名称	字段类型	备注
管理员编号	admin_id	int(11) NOT NULL	DBonly主键
管理员账号	admin_account	varchar(50) NOT NULL	
管理员密码	admin_password	varchar(255) NOT NULL	
3.2.2 同步 async_ctrl表（设置同步时间）
中文含义	英文名称	字段类型	备注
同步时间间隔	async_time	varchar(255) NULL	
起始日	daily_start	varchar(255) NULL	
终止日	daily_end	varchar(255) NULL	
起始周	weekly_start	varchar(255) NULL	
终止周	weekly_end	varchar(255) NULL	
起始月	monthly_start	varchar(255) NULL	
终止月	monthly_end	varchar(255) NULL	
起始年	annual_start	varchar(255) NULL	
终止年	annual_end	varchar(255) NULL	
平台名	version	varchar(255) NULL	
3.2.3 卡余额变更记录 balance_history表
中文含义	英文名称	字段类型	备注
插入时间	insert_time	varchar(255) NULL	
入账id	log_id	varchar(255) NOT NULL	
带掩码卡号	mask_card_number	varchar(255) NULL	
关联卡id	card_id	varchar(255) NULL	
卡交易id	transaction_id	varchar(255) NULL	
账单日，使用ISO-8601日期格式。	bill_date	datetime NULL	
入账时间，使用ISO-8601时间格式	transaction_time		
入账金额	amount	decimal(10,3) NULL	
币种。参考ISO-4217币种列表。	amount_currency	varchar(255) NULL	
卡余额变更流水业务类型	txn_type	varchar(255) NULL	
卡业务类型	card_biz_type	varchar(255) NULL	
交易后账户余额	balance_after_transaction_amount	decimal(10,3) NULL	
币种。参考ISO-4217币种列表。	balance_after_transaction_currency	varchar(255) NULL	
平台名	version	varchar(255) NULL	

3.2.4 卡持有者 card_holder表
中文含义	英文名称	字段类型	备注
持卡人唯一id	card_holder_id	varchar(255) NOT NULL	
持卡人名	first_name	varchar(255) NULL	
持卡人姓	last_name	varchar(255) NULL	
2字符国家码，参考ISO-3166标准国家码清单。	region	varchar(255) NULL	
持卡人生日，使用ISO-8601日期格式	birth	varchar(255) NULL	
国际区号，无需在前面加'+'或'0'。	mobile_nation_code	varchar(255) NULL	
手机号	mobile	varchar(255) NULL	
持卡人email	email	varchar(255) NULL	
2字符国家码，参考ISO-3166国家码清单。	bill_address_country	varchar(255) NULL	
州/省	bill_address_state	varchar(255) NULL	
详细地址	bill_address	varchar(255) NULL	
邮编	bill_address_postcode	varchar(255) NULL	
持卡人创建时间，使用ISO-8601时间格式	create_time	varchar(255) NULL	
用户密钥	user_key	varchar(255) NULL	
持卡人状态	status	varchar(255) NULL	
代理id	qd_id	varchar(255) NULL	
代理名	qd_name	varchar(255) NULL	
代理等级	qd_level	varchar(255) NULL	
电报id	telegram_id	varchar(255) NULL	
用户是否登陆telegram	user_login	varchar(255) NULL	
用户类型	uesr-type	varchar(255) NULL	
平台名	version	varchar(255) NULL	
插入时间	insert_time	varchar(255) NULL	
3.2.5 卡交易记录 card_transactions表
中文含义	英文名称	字段类型	备注
插入时间	insert_time	varchar(255) NULL	
唯一交易id	transaction_id	varchar(255) NOT NULL	
关联交易id，如退款、撤单会关联到付款交易	origin_transaction_id	varchar(255) NULL	
卡id	card_id	varchar(255) NULL	
带掩码卡号	mask_card_number	varchar(255) NULL	
交易发生时间，ISO-8601时间格式	transaction_time	varchar(255) NULL	
入账时间，ISO-8601时间格式	confirm_time	varchar(255) NULL	
原始交易金额	transaction_amount	decimal(10,3) NULL	
原始交易币种。参考ISO-4217币种列表。	transaction_amount_currency	varchar(255) NULL	
入账金额	accounting_amount	decimal(10,3) NULL	
入账金额币种。参考ISO-4217币种列表。	accounting_amount_currency	varchar(255) NULL	
手续费金额	surcharge_amount	decimal(10,3) NULL	
卡业务类型	biz_type	varchar(255) NULL	
卡交易状态	status	varchar(255) NULL	
状态描述，例如失败原因等信息	status_description	varchar(255) NULL	
验证码，VERIFICATION类型的交易会携带此参数。	check_code	varchar(255) NULL	
交易商户名称	merchant_name	varchar(255) NULL	
交易商户所在国家、地区，使用ISO-3166清单中的2字符国家编码.	merchant_region	varchar(255) NULL	
平台名	version	varchar(255) NULL	
3.2.6 卡类型 card_type表（暂时没用，用cards_product表代替）
中文含义	英文名称	字段类型	备注
序号	id	int(11) NOT NULL	
卡片类型	card_type	varchar(255) NOT NULL	
开卡费	opening_fee	varchar(255) NULL	
月服务费	monthly_service_fee	varchar(255) NULL	
跨境手续费	cross_border_fee	varchar(255) NULL	
交易手续费	transaction_fee	varchar(255) NULL	
单笔授权费	authorization_fee	varchar(255) NULL	
消费额度/笔	transaction_limit	varchar(255) NULL	
消费额度/月	monthly_limit	varchar(255) NULL	
消费额度描述	credit_limit	varchar(255) NULL	
区域	region	varchar(255) NULL	
币种	currency	varchar(255) NULL	
免实名认证	real_name_required	varchar(255) NULL	1代表是0代表否
平台名	version	varchar(255) NULL	
插入时间	insert_time	timestamp NULL	
3.2.7  U卡信息 card表
中文含义	英文名称	字段类型	备注
唯一卡id	card_id	varchar(255) NOT NULL	
卡币种，参考ISO-4217币种清单。	card_currency	varchar(255) NULL	
卡状态	status	varchar(255) NULL	
卡品牌	brand_code	varchar(255) NULL	
带掩码卡号	mask_card_number	varchar(255) NULL	
可用消费额度	available_balance	varchar(255) NULL	
持卡人id	card_holder_id	varchar(255) NULL	
平台名	version	varchar(255) NULL	
插入时间	insert_time	varchar(255) NULL	
3.2.8  U卡联系信息 card_info表 (创建卡添加的信息)
中文含义	英文名称	字段类型	备注
唯一卡id	card_id	varchar(255) NOT NULL	
卡昵称	card_name	varchar(255) NULL	
带掩码卡号	mask_card_number	varchar(255) NULL	
卡币种，参考ISO-4217币种清单。	card_currency	varchar(255) NULL	
可用消费额度	available_balance	varchar(255) NULL	
Enum: "VISA" "MASTER"
卡品牌
	brand_code	varchar(255) NULL	
卡状态	status	varchar(255) NULL	
卡类型	card_type		ENTITY: 实体卡
VIRTUAL: 虚拟卡

卡财务类别	accounting_type		SHARE: 共享卡，无需预充值。发生交易时直接扣除钱包账户余额。
RECHARGE: 充值卡，创建卡时需从钱包余额充值金额到卡余额。发生交易时扣除卡账户余额。

发卡国，使用ISO-3166国家码清单的2字符国家码	card_region		
持卡人id	card_holder_id		
持卡人名	first_name		
持卡人姓	last_name		
国际区号，无需在前面加'+'或'0'。	mobile_nation_code		
手机号	mobile		
持卡人email	email		
每日交易限额	limit_per_day		
每月交易限额	limit_per_month		
单笔交易限额	limit_per_transaction		
邮编	bill_address_postcode		
详细地址	bill_address		
城市	bill_address_city		
州/省	bill_address_state		
2字符国家码，参考ISO-3166国家码清单。	bill_address_country		
卡创建时间，使用ISO-8601时间格式	create_time		
插入时间	insert_time	varchar(255) NULL	
平台名	version	varchar(255) NULL	
3.2.9  卡类型 cards_product表
中文含义	英文名称	字段类型	备注
卡产品编码	product_code	varchar(255) NOT NULL	
卡产品名	product_name	varchar(255) NULL	
卡品牌	brand_code	varchar(255) NULL	
货币	currency	varchar(255) NULL	
可开数	stock	varchar(255) NULL	
已经开卡数	opened_quantity	varchar(255) NULL	
卡类型	card_type	varchar(255)  NULL	
描述	description	varchar(255) NULL	
平台名	version	varchar(255) NOT NULL	
插入时间	insert_time	varchar(255) NULL	
3.2.10  卡安全信息 cards_secure_info表
中文含义	英文名称	字段类型	备注
唯一卡id	card_id	varchar(255) NOT NULL	
完整卡号，16-19位数字	pan	varchar(255) NULL	
卡有效期-年，4位数字	expire_year	varchar(255) NULL	
卡有效期-月，2位数字	expire_month	varchar(255) NULL	
卡安全码. 3-4位数字	cvv	varchar(255) NULL	
持卡人	card_holder	varchar(255) NULL	
平台名	version	varchar(255) NOT NULL	
插入时间	insert_time	varchar(255) NULL	
3.2.11  兑换商 exchange_merchants表
中文含义	英文名称	字段类型	备注
序号	id	int(11) NOT NULL	
兑换商名	merchant_name	varchar(255) NOT NULL	
兑换费率	exchange_rate	varchar(255) NOT NULL	
3.2.12  兑换汇率表 exchange_usdt表
中文含义	英文名称	字段类型	备注
序号	id	int(11) NOT NULL	
被兑换的币种	currency_from	varchar(10) NOT NULL	
要兑换的币种	currency_to	varchar(10) NOT NULL	
	official_rate	float NULL	
插入时间	insert_time	varchar(255) NULL	
是否被引用	is	int(11) NULL	
3.2.13   调额返回数据modify_respdata表
中文含义	英文名称	字段类型	备注
gsalary唯一id	gsalary_request_id	varchar(255) NOT NULL	
请求时提交的唯一请求id	request_id	varchar(255) NULL	
唯一卡id	card_id	varchar(255) NULL	
Enum: "PENDING" "SUCCESS" "FAILED"
请求状态
	status	varchar(255) NULL	
请求时间，ISO-8601时间格式。	create_time	varchar(255) NULL	
完成时间，ISO-8601时间格式。	finish_time	varchar(255) NULL	
修改金额	amount	varchar(255) NULL	
Enum: "INCREASE" "DECREASE"
修改类型	type	varchar(255) NULL	
调额后可用余额	post_balance	varchar(255) NULL	
平台名	version	varchar(255)NULL	
插入时间	insert_time	varchar(255) NULL	
3.2.14   push_ctrl表
中文含义	英文名称	字段类型	备注
序号	id	int(11) NOT NULL	
上次插入时间	last_insert_time	varchar(255) NULL	
方法	function	varchar(255) NULL	
3.2.15   rate_ctrl表
中文含义	英文名称	字段类型	备注
序号	id	int(11) NOT NULL	
服务费	fee	float NULL	
百分比	percentage	float NULL	
平台	version	varchar(255) NULL	
3.2.16 国家表  region表
中文含义	英文名称	字段类型	备注
序号	id	int(11) NOT NULL	
英文名	english_name	varchar(255) NULL	
中文名	chinese_name	varchar(255) NULL	
缩写	abbreviation	varchar(10) NOT NULL	
货币	currency	varchar(50) NOT NULL	
图标	icon_base64	text NULL	
是否被引用	is_referenced	tinyint(1) NOT NULL	
插入时间	insert_time	timestamp NULL	
3.2.16 系统平台  system_key表
中文含义	英文名称	字段类型	备注
序号	id	int(11) NOT NULL	
平台id	appid	varchar(255) NULL	
平台密钥	key	varchar(5000) NULL	
平台名	system	varchar(255) NULL	
3.2.17 系统维护  system_maintenance表
中文含义	英文名称	字段类型	备注
序号	id	int(11) NOT NULL	
同步时间	sync_time	time NOT NULL	
同步间隔	sync_interval	int(11) NOT NULL	
汇率开始时间	rate_start_time	time NOT NULL	
汇率结束时间	rate_end_time	time NOT NULL	
日失败次数	daily_failure_count	time NOT NULL	
插入时间	insert_time	timestamp NULL	

3.2.18 钱包余额  wallet_balance表
中文含义	英文名称	字段类型	备注
序号	id	int(11) NOT NULL	
货币	currency	varchar(50) NOT NULL	
余额	amount	decimal(10,3) NOT NULL	
平台	version	varchar(255) NOT NULL	
插入时间	insert_time	varchar(255) NULL	
可用额度	available	decimal(10,3) NULL	
			
3.2.19 钱包余额  wallet_transactions表
中文含义	英文名称	字段类型	备注
插入时间	insert_time	varchar(255) NOT NULL	
流水id	transaction_id	varchar(255) NOT NULL	
入账币种	amount_currency	varchar(255) NULL	
入账金额	amount	decimal(10,3) NULL	
入账时间，使用ISO-8601时间格式	transaction_time	varchar(255) NULL	
流水业务类型	txn_type	varchar(255) NULL	
动账后余额	after_balance_amount	decimal(10,3) NULL	
备注	remark	varchar(255) NULL	
平台	version	varchar(255) NULL	
动账后币种	after_balance_currency	varchar(255) NULL	
