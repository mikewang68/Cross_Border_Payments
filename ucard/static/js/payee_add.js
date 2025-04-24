/**
 * 添加收款人页面专用脚本
 * 用于处理添加收款人表单的验证、提交等功能
 */

layui.use(['form', 'layer'], function(){
    var form = layui.form;
    var layer = layui.layer;
    var $ = layui.jquery;
    
    // 国家列表
    var countries = [
        {code: "CN", name: "中国"},
        {code: "US", name: "美国"},
        {code: "UK", name: "英国"},
        {code: "JP", name: "日本"},
        {code: "KR", name: "韩国"},
        {code: "SG", name: "新加坡"},
        {code: "MY", name: "马来西亚"},
        {code: "TH", name: "泰国"},
        {code: "ID", name: "印度尼西亚"},
        {code: "VN", name: "越南"},
        {code: "PH", name: "菲律宾"},
        {code: "AU", name: "澳大利亚"},
        {code: "CA", name: "加拿大"}
    ];
    
    // 常用币种列表
    var currencies = [
        {code: "CNY", name: "人民币"},
        {code: "USD", name: "美元"},
        {code: "EUR", name: "欧元"},
        {code: "GBP", name: "英镑"},
        {code: "JPY", name: "日元"},
        {code: "HKD", name: "港币"},
        {code: "KRW", name: "韩元"},
        {code: "SGD", name: "新加坡元"},
        {code: "MYR", name: "马来西亚林吉特"},
        {code: "THB", name: "泰铢"},
        {code: "IDR", name: "印尼盾"},
        {code: "VND", name: "越南盾"},
        {code: "PHP", name: "菲律宾比索"},
        {code: "AUD", name: "澳元"},
        {code: "CAD", name: "加元"}
    ];
    
    // 钱包类型列表
    var walletTypes = [
        {code: "ALIPAY", name: "支付宝"},
        {code: "WECHAT", name: "微信支付"},
        {code: "PAYPAL", name: "PayPal"},
        {code: "SKRILL", name: "Skrill"},
        {code: "NETELLER", name: "Neteller"},
        {code: "PAYTM", name: "Paytm"},
        {code: "GCASH", name: "GCash"},
        {code: "DANA", name: "Dana"},
        {code: "GO_PAY", name: "GoPay"},
        {code: "OVO", name: "OVO"},
        {code: "MOMO", name: "MoMo"},
        {code: "TOUCH_N_GO", name: "Touch 'n Go"}
    ];

    // 页面初始化
    $(function() {
        initForm();
        bindEvents();
    });
    
    // 初始化表单
    function initForm() {
        // 1. 加载国家/地区下拉框
        var countrySelect = $('select[name="country"]');
        countries.forEach(function(country) {
            countrySelect.append('<option value="' + country.code + '">' + country.name + '</option>');
        });
        
        // 2. 加载币种下拉框
        var currencySelect = $('select[name="currency"]');
        currencies.forEach(function(currency) {
            currencySelect.append('<option value="' + currency.code + '">' + currency.name + '</option>');
        });
        
        // 3. 加载钱包类型下拉框
        var walletTypeSelect = $('select[name="wallet_type"]');
        walletTypes.forEach(function(walletType) {
            walletTypeSelect.append('<option value="' + walletType.code + '">' + walletType.name + '</option>');
        });
        
        // 4. 尝试从后端获取支付方式数据
        try {
            // 获取支付方式数据
            var methodsDataElement = document.getElementById('payment-methods-data');
            if (methodsDataElement && methodsDataElement.textContent.trim() !== '') {
                var paymentMethods = JSON.parse(methodsDataElement.textContent);
                console.log("支付方式数据:", paymentMethods);
                // 这里可以进一步处理支付方式数据
            }
        } catch (error) {
            console.error("解析支付方式数据失败:", error);
        }
        
        // 重新渲染表单
        form.render();
    }
    
    // 绑定事件
    function bindEvents() {
        // 1. 账户类型切换事件
        form.on('select(accountType)', function(data){
            var value = data.value;
            if (value === 'BANK_ACCOUNT') {
                $('.bank-account-fields').show();
                $('.e-wallet-fields').hide();
                // 设置银行字段为必填
                $('input[name="bank_name"]').attr('lay-verify', 'required');
                $('input[name="bank_account_number"]').attr('lay-verify', 'required');
                // 移除钱包字段必填
                $('select[name="wallet_type"]').removeAttr('lay-verify');
                $('input[name="wallet_account"]').removeAttr('lay-verify');
            } else if (value === 'E_WALLET') {
                $('.bank-account-fields').hide();
                $('.e-wallet-fields').show();
                // 设置钱包字段为必填
                $('select[name="wallet_type"]').attr('lay-verify', 'required');
                $('input[name="wallet_account"]').attr('lay-verify', 'required');
                // 移除银行字段必填
                $('input[name="bank_name"]').removeAttr('lay-verify');
                $('input[name="bank_account_number"]').removeAttr('lay-verify');
            } else {
                $('.bank-account-fields').hide();
                $('.e-wallet-fields').hide();
                // 移除所有特有字段必填
                $('input[name="bank_name"]').removeAttr('lay-verify');
                $('input[name="bank_account_number"]').removeAttr('lay-verify');
                $('select[name="wallet_type"]').removeAttr('lay-verify');
                $('input[name="wallet_account"]').removeAttr('lay-verify');
            }
            
            // 重新渲染表单
            form.render();
        });
        
        // 2. 表单提交事件
        form.on('submit(payeeAddSubmit)', function(data){
            var formData = data.field;
            console.log("表单提交数据:", formData);
            
            // 构建提交数据
            var submitData = {
                account_type: formData.account_type,
                last_name: formData.last_name,
                first_name: formData.first_name,
                country: formData.country,
                currencies: [formData.currency],
                mobile_nation_code: formData.mobile_nation_code,
                mobile: formData.mobile,
                address: formData.address,
                version: formData.version
            };
            
            // 根据账户类型添加特定字段
            if (formData.account_type === 'BANK_ACCOUNT') {
                submitData.bank_name = formData.bank_name;
                submitData.bank_account_number = formData.bank_account_number;
                submitData.bank_branch = formData.bank_branch;
                submitData.bank_code = formData.bank_code;
            } else if (formData.account_type === 'E_WALLET') {
                submitData.wallet_type = formData.wallet_type;
                submitData.wallet_account = formData.wallet_account;
            }
            
            // 发送请求到后端API
            $.ajax({
                url: '/ucard/api/payee/add',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(submitData),
                success: function(res) {
                    // 处理成功响应
                    if (res.code === 0) {
                        layer.msg('添加收款人成功', {icon: 1, time: 2000}, function(){
                            // 返回收款人列表页面
                            returnToPayeesList();
                        });
                    } else {
                        layer.msg('添加收款人失败: ' + res.msg, {icon: 2});
                    }
                },
                error: function(xhr) {
                    // 处理错误响应
                    layer.msg('添加收款人失败，请稍后重试', {icon: 2});
                    console.error("添加收款人请求失败:", xhr);
                }
            });
            
            // 阻止表单默认提交
            return false;
        });
        
        // 3. 返回按钮点击事件
        $('.return-button').click(function(){
            returnToPayeesList();
        });
    }
    
    // 返回收款人列表页面
    function returnToPayeesList() {
        // 获取父级页面的layui-card-body元素
        var parentBody = window.parent.document.querySelector('.payees-page .layui-card-body');
        if (parentBody) {
            // 移除当前添加表单内容
            parentBody.innerHTML = window.parent.originalPayeesContent;
            
            // 重新初始化收款人列表页面（如果需要）
            if (window.parent.layui && window.parent.layui.table) {
                window.parent.layui.table.reload('payees-table');
            }
        } else {
            // 如果不是在iframe中，直接跳转到收款人列表页面
            window.location.href = '/ucard/payee';
        }
    }
});
