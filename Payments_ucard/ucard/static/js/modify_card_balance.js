// 全局变量存储卡数据
let cardData = null;
let walletBalanceData = null;
let accountAvailableBalance = 0; // 用于存储账户剩余余额

// 初始化卡数据，这个函数由父窗口调用
function initCardData(data) {
    cardData = data;
    walletBalanceData = data.wallet_balance_data;
    
    // 保存账户剩余余额
    accountAvailableBalance = data.available_balance ? parseFloat(data.available_balance) : 0;
    
    // 设置表单数据
    document.getElementById('card_id').value = data.card_id;
    document.getElementById('mask_card_number').value = data.mask_card_number;
    document.getElementById('full_name').value = data.first_name + ' ' + data.last_name;
    document.getElementById('version').value = data.version;
    
    // 设置币种标签
    document.getElementById('currency_label').innerText = data.card_currency || 'USD';
    
    // 设置账户余额信息
    const currency = data.card_currency || 'USD';
    document.getElementById('account_balance_label').innerText = 
        '账户余额: ' + accountAvailableBalance + ' ' + currency;
    
    // 设置平台可用余额
    const platform = data.version; // 例如 "J1" 或 "J2"
    
    if (walletBalanceData && walletBalanceData[platform] && 
        walletBalanceData[platform][currency] && 
        walletBalanceData[platform][currency].available) {
        
        const platformAvailable = walletBalanceData[platform][currency].available;
        document.getElementById('platform_balance_label').innerText = 
            '平台可用余额: ' + platformAvailable + ' ' + currency;
    } else {
        document.getElementById('platform_balance_label').innerText = '该平台余额不可用';
    }
    
    // 在控制台输出调试信息
    console.log('卡片平台:', data.version);
    console.log('钱包余额数据:', walletBalanceData);
}

// 使用layui
layui.use(['form', 'layer', 'jquery'], function() {
    var form = layui.form;
    var layer = layui.layer;
    var $ = layui.jquery; // 使用layui内置的jQuery
    
    // 表单提交事件
    form.on('submit(submitForm)', function(data) {
        // 获取表单数据
        const formData = data.field;
        const amount = parseFloat(formData.amount);
        
        // 校验金额
        if (isNaN(amount) || amount <= 0) {
            layer.msg('请输入有效的金额', {icon: 2});
            return false;
        }
        
        // 查找对应平台的可用余额
        let platformAvailableBalance = 0;
        const platform = cardData.version;
        const currency = cardData.card_currency || 'USD';
        
        if (walletBalanceData && walletBalanceData[platform] && 
            walletBalanceData[platform][currency] && 
            walletBalanceData[platform][currency].available) {
            
            platformAvailableBalance = parseFloat(walletBalanceData[platform][currency].available);
        }
        
        // 根据不同操作类型进行验证
        if (formData.type === 'INCREASE') {
            // 增加时，检查是否超过平台可用余额
            if (amount > platformAvailableBalance) {
                layer.msg('增加的金额不能超过平台可用余额 ' + platformAvailableBalance, {icon: 2});
                return false;
            }
        } else if (formData.type === 'DECREASE') {
            // 减少时，检查是否超过账户剩余余额
            if (amount > accountAvailableBalance) {
                layer.msg('减少的金额不能超过账户剩余余额 ' + accountAvailableBalance, {icon: 2});
                return false;
            }
        }
        
        // 构建请求数据
        const requestData = {
            card_id: cardData.card_id,
            amount: amount,
            type: formData.type,
            version: cardData.version
        };
        
        // 显示加载中
        var loadIndex = layer.load(2);
        
        // 发送请求
        $.ajax({
            url: '/cards/modify_card',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(requestData),
            success: function(res) {
                layer.close(loadIndex);
                if (res.code === 0) {
                    layer.msg('调整卡额度成功', {icon: 1, time: 2000}, function() {
                        // 成功后关闭窗口
                        var index = parent.layer.getFrameIndex(window.name);
                        parent.layer.close(index);
                    });
                } else {
                    layer.msg(res.msg || '调整卡额度失败', {icon: 2});
                }
            },
            error: function(xhr, status, error) {
                layer.close(loadIndex);
                console.error('AJAX错误:', status, error);
                layer.msg('服务器错误，请稍后重试: ' + error, {icon: 2});
            }
        });
        
        return false; // 阻止表单默认提交
    });
    
    // 监听金额输入，确保金额有效
    $('#amount').on('input', function() {
        const amount = parseFloat($(this).val());
        const type = $('input[name="type"]:checked').val();
        
        // 查找对应平台的可用余额
        let platformAvailableBalance = 0;
        const platform = cardData.version;
        const currency = cardData.card_currency || 'USD';
        
        if (walletBalanceData && walletBalanceData[platform] && 
            walletBalanceData[platform][currency] && 
            walletBalanceData[platform][currency].available) {
            
            platformAvailableBalance = parseFloat(walletBalanceData[platform][currency].available);
        }
        
        if (type === 'INCREASE' && platformAvailableBalance > 0) {
            // 增加时，检查是否超过平台可用余额
            if (amount > platformAvailableBalance) {
                layer.msg('增加的金额不能超过平台可用余额 ' + platformAvailableBalance, {icon: 2});
                $(this).addClass('input-error');
            } else {
                $(this).removeClass('input-error');
            }
        } else if (type === 'DECREASE' && accountAvailableBalance > 0) {
            // 减少时，检查是否超过账户剩余余额
            if (amount > accountAvailableBalance) {
                layer.msg('减少的金额不能超过账户剩余余额 ' + accountAvailableBalance, {icon: 2});
                $(this).addClass('input-error');
            } else {
                $(this).removeClass('input-error');
            }
        }
    });
    
    // 监听类型选择变化
    form.on('radio', function(data) {
        // 如果切换类型，重新验证金额
        const amount = parseFloat($('#amount').val());
        if (!isNaN(amount)) {
            // 查找对应平台的可用余额
            let platformAvailableBalance = 0;
            const platform = cardData.version;
            const currency = cardData.card_currency || 'USD';
            
            if (walletBalanceData && walletBalanceData[platform] && 
                walletBalanceData[platform][currency] && 
                walletBalanceData[platform][currency].available) {
                
                platformAvailableBalance = parseFloat(walletBalanceData[platform][currency].available);
            }
            
            // 根据类型进行不同的验证
            if (data.value === 'INCREASE' && platformAvailableBalance > 0) {
                // 增加时，检查是否超过平台可用余额
                if (amount > platformAvailableBalance) {
                    layer.msg('增加的金额不能超过平台可用余额 ' + platformAvailableBalance, {icon: 2});
                    $('#amount').addClass('input-error');
                } else {
                    $('#amount').removeClass('input-error');
                }
            } else if (data.value === 'DECREASE' && accountAvailableBalance > 0) {
                // 减少时，检查是否超过账户剩余余额
                if (amount > accountAvailableBalance) {
                    layer.msg('减少的金额不能超过账户剩余余额 ' + accountAvailableBalance, {icon: 2});
                    $('#amount').addClass('input-error');
                } else {
                    $('#amount').removeClass('input-error');
                }
            } else {
                $('#amount').removeClass('input-error');
            }
        }
    });
});
