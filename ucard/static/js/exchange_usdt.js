// 汇率报价JS
layui.use(['element', 'layer', 'form', 'table'], function() {
    var element = layui.element;
    var layer = layui.layer;
    var form = layui.form;
    var table = layui.table;
    
    // 全局变量
    var exchangeData = [];
    var selectedCurrency = null;
    var reverseSelectedCurrency = null; // 本币换U的选中币种
    
    // 初始化页面
    function initPage() {
        console.log('初始化汇率报价页面');
        
        // 获取后端传递的汇率数据
        try {
            var exchangeDataJson = document.getElementById('exchange-data').textContent;
            exchangeData = JSON.parse(exchangeDataJson) || [];
            console.log('加载汇率数据:', exchangeData.length, '条记录');
            
            // 初始化币种下拉框（U换本币和本币换U）
            initCurrencySelect();
            initReverseCurrencySelect();
            
            // 渲染汇率表格
            renderExchangeRatesTable();
            renderReverseExchangeRatesTable();
        } catch (e) {
            console.error('解析汇率数据失败:', e);
            exchangeData = [];
            layer.msg('加载汇率数据失败，请刷新页面重试', {icon: 2});
        }
        
        // 绑定事件
        bindEvents();
    }
    
    // 初始化币种下拉框 (U换本币)
    function initCurrencySelect() {
        var select = document.getElementById('currency-select');
        if (!select) return;
        
        // 清空选项
        select.innerHTML = '<option value="">请选择币种</option>';
        
        // 过滤J2平台且is=1的数据
        var j2Data = exchangeData.filter(function(item) {
            return item.version === 'J2' && item.is === 1;
        });
        
        // 添加选项
        j2Data.forEach(function(item) {
            var option = document.createElement('option');
            option.value = item.currency;
            option.textContent = item.currency;
            select.appendChild(option);
        });
        
        // 重新渲染选择框
        form.render('select');
    }
    
    // 初始化币种下拉框 (本币换U)
    function initReverseCurrencySelect() {
        var select = document.getElementById('reverse-currency-select');
        if (!select) return;
        
        // 清空选项
        select.innerHTML = '<option value="">请选择币种</option>';
        
        // 过滤J2平台且is=1的数据
        var j2Data = exchangeData.filter(function(item) {
            return item.version === 'J2' && item.is === 1;
        });
        
        // 添加选项
        j2Data.forEach(function(item) {
            var option = document.createElement('option');
            option.value = item.currency;
            option.textContent = item.currency;
            select.appendChild(option);
        });
        
        // 重新渲染选择框
        form.render('select');
    }
    
    // 渲染汇率表格
    function renderExchangeRatesTable() {
        var tbody = document.getElementById('exchange-rates-body');
        if (!tbody) return;
        
        // 清空表格内容
        tbody.innerHTML = '';
        
        // 过滤J2平台且is=1的数据
        var j2Data = exchangeData.filter(function(item) {
            return item.version === 'J2' && item.is === 1;
        });
        
        // 无数据提示
        if (!j2Data || j2Data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">暂无J2平台有效汇率数据</td></tr>';
            return;
        }
        
        // 添加表格行
        j2Data.forEach(function(item) {
            var row = document.createElement('tr');
            
            // 格式化数据
            var currency = item.currency || '-';
            var officialRate = parseFloat(item.official_rate || 0).toFixed(4);
            var fee = (parseFloat(item.fee || 0) * 100).toFixed(2) + '%';
            var updateTime = item.insert_time || '-';
            
            // 创建表格单元格
            row.innerHTML = `
                <td>${currency}</td>
                <td>${officialRate}</td>
                <td>${fee}</td>
                <td>${updateTime}</td>
            `;
            
            tbody.appendChild(row);
        });
        
        // 初始化表格排序等功能
        table.init('exchange-table', {
            height: 400,
            limit: 10,
            page: true
        });
    }
    
    // 渲染本币换U汇率表格
    function renderReverseExchangeRatesTable() {
        var tbody = document.getElementById('reverse-exchange-rates-body');
        if (!tbody) return;
        
        // 清空表格内容
        tbody.innerHTML = '';
        
        // 过滤J2平台且is=1的数据
        var j2Data = exchangeData.filter(function(item) {
            return item.version === 'J2' && item.is === 1;
        });
        
        // 无数据提示
        if (!j2Data || j2Data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">暂无J2平台有效汇率数据</td></tr>';
            return;
        }
        
        // 添加表格行
        j2Data.forEach(function(item) {
            var row = document.createElement('tr');
            
            // 格式化数据
            var currency = item.currency || '-';
            var officialRate = parseFloat(item.official_rate || 0).toFixed(4);
            var fee = (parseFloat(item.fee || 0) * 100).toFixed(2) + '%';
            var updateTime = item.insert_time || '-';
            
            // 创建表格单元格
            row.innerHTML = `
                <td>${currency}</td>
                <td>${officialRate}</td>
                <td>${fee}</td>
                <td>${updateTime}</td>
            `;
            
            tbody.appendChild(row);
        });
        
        // 初始化表格排序等功能
        table.init('reverse-exchange-table', {
            height: 400,
            limit: 10,
            page: true
        });
    }
    
    // 绑定事件
    function bindEvents() {
        // U换本币 - 币种选择事件
        form.on('select(currency-select)', function(data) {
            var currencyCode = data.value;
            if (!currencyCode) {
                selectedCurrency = null;
                return;
            }
            
            // 查找选中的币种数据，限定J2平台且is=1
            selectedCurrency = exchangeData.find(function(item) {
                return item.currency === currencyCode && item.version === 'J2' && item.is === 1;
            });
            
            console.log('选择币种 (U换本币):', selectedCurrency);
        });
        
        // U换本币 - 计算按钮点击事件
        document.getElementById('calculate-btn').addEventListener('click', function() {
            calculateExchange();
        });
        
        // U换本币 - 重置按钮点击事件
        document.querySelector('form[lay-filter="calculatorForm"]').addEventListener('reset', function() {
            // 隐藏结果容器
            document.getElementById('result-container').style.display = 'none';
            // 重置选中币种
            selectedCurrency = null;
            // 清空手续费率输入框
            document.getElementById('result-fee-input').value = '';
        });
        
        // U换本币 - 金额输入框回车事件
        document.getElementById('amount-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault(); // 阻止默认表单提交
                calculateExchange();
            }
        });

        // U换本币 - 手续费率输入框变化事件
        document.getElementById('result-fee-input').addEventListener('input', function() {
            if (selectedCurrency && document.getElementById('amount-input').value) {
                calculateExchange();
            }
        });
        
        // 本币换U - 币种选择事件
        form.on('select(reverse-currency-select)', function(data) {
            var currencyCode = data.value;
            if (!currencyCode) {
                reverseSelectedCurrency = null;
                return;
            }
            
            // 查找选中的币种数据，限定J2平台且is=1
            reverseSelectedCurrency = exchangeData.find(function(item) {
                return item.currency === currencyCode && item.version === 'J2' && item.is === 1;
            });
            
            console.log('选择币种 (本币换U):', reverseSelectedCurrency);
        });
        
        // 本币换U - 计算按钮点击事件
        document.getElementById('reverse-calculate-btn').addEventListener('click', function() {
            calculateReverseExchange();
        });
        
        // 本币换U - 重置按钮点击事件
        document.querySelector('form[lay-filter="reverseCalculatorForm"]').addEventListener('reset', function() {
            // 隐藏结果容器
            document.getElementById('reverse-result-container').style.display = 'none';
            // 重置选中币种
            reverseSelectedCurrency = null;
            // 清空手续费率输入框
            document.getElementById('reverse-result-fee-input').value = '';
        });
        
        // 本币换U - 金额输入框回车事件
        document.getElementById('reverse-amount-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault(); // 阻止默认表单提交
                calculateReverseExchange();
            }
        });
        
        // 本币换U - 手续费率输入框变化事件
        document.getElementById('reverse-result-fee-input').addEventListener('input', function() {
            if (reverseSelectedCurrency && document.getElementById('reverse-amount-input').value) {
                calculateReverseExchange();
            }
        });
    }
    
    // 计算汇率和最终报价 (U换本币)
    function calculateExchange() {
        // 获取输入金额
        var amountInput = document.getElementById('amount-input');
        var amount = parseFloat(amountInput.value);
        
        // 验证输入
        if (!selectedCurrency) {
            layer.msg('请先选择币种', {icon: 0});
            return;
        }
        
        if (isNaN(amount) || amount <= 0) {
            layer.msg('请输入有效的金额', {icon: 0});
            return;
        }
        
        // 获取汇率和手续费
        var officialRate = parseFloat(selectedCurrency.official_rate || 0);
        var feeInput = document.getElementById('result-fee-input');
        var fee = parseFloat(feeInput.value) / 100;
        
        // 如果手续费率输入框为空，使用数据库中的值
        if (isNaN(fee)) {
            fee = parseFloat(selectedCurrency.fee || 0);
            feeInput.value = (fee * 100).toFixed(2);
        }
        
        if (officialRate <= 0) {
            layer.msg('该币种汇率数据无效', {icon: 2});
            return;
        }
        
        // 计算最终报价
        // 公式：W = T * (1 + fee) * official_rate，其中T为本币金额
        var finalPrice = amount * (1 + fee) * officialRate;
        
        // 计算最终汇率：W / T
        var finalRate = finalPrice / amount;
        
        // 更新结果显示
        document.getElementById('result-currency').textContent = selectedCurrency.currency;
        document.getElementById('result-rate').textContent = officialRate.toFixed(4);
        document.getElementById('result-amount').textContent = amount.toFixed(2);
        document.getElementById('result-total').textContent = finalPrice.toFixed(2);
        document.getElementById('result-final-rate').textContent = finalRate.toFixed(4);
        
        // 显示结果容器
        document.getElementById('result-container').style.display = 'block';
        
        // 滚动到结果区域
        document.getElementById('result-container').scrollIntoView({behavior: 'smooth'});
    }
    
    // 计算汇率和最终报价 (本币换U)
    function calculateReverseExchange() {
        // 获取输入金额
        var amountInput = document.getElementById('reverse-amount-input');
        var amount = parseFloat(amountInput.value);
        
        // 验证输入
        if (!reverseSelectedCurrency) {
            layer.msg('请先选择币种', {icon: 0});
            return;
        }
        
        if (isNaN(amount) || amount <= 0) {
            layer.msg('请输入有效的金额', {icon: 0});
            return;
        }
        
        // 获取汇率和手续费
        var officialRate = parseFloat(reverseSelectedCurrency.official_rate || 0);
        var feeInput = document.getElementById('reverse-result-fee-input');
        var fee = parseFloat(feeInput.value) / 100;
        
        // 如果手续费率输入框为空，使用数据库中的值
        if (isNaN(fee)) {
            fee = parseFloat(reverseSelectedCurrency.fee || 0);
            feeInput.value = (fee * 100).toFixed(2);
        }
        
        if (officialRate <= 0) {
            layer.msg('该币种汇率数据无效', {icon: 2});
            return;
        }
        
        // 计算最终报价
        // 公式：W = B * (1 - X) / Y，其中W为本币数量，B为U数量，X为手续费率，Y为汇率
        var finalPrice = amount * (1 - fee) / officialRate;
        
        // 计算最终汇率：B / W = B / (B * (1 - X) / Y) = Y / (1 - X)
        var finalRate = officialRate / (1 - fee);
        
        // 更新结果显示
        document.getElementById('reverse-result-currency').textContent = reverseSelectedCurrency.currency;
        document.getElementById('reverse-result-rate').textContent = officialRate.toFixed(4);
        document.getElementById('reverse-result-amount').textContent = amount.toFixed(2);
        document.getElementById('reverse-result-total').textContent = finalPrice.toFixed(2);
        document.getElementById('reverse-result-final-rate').textContent = finalRate.toFixed(4);
        
        // 显示结果容器
        document.getElementById('reverse-result-container').style.display = 'block';
        
        // 滚动到结果区域
        document.getElementById('reverse-result-container').scrollIntoView({behavior: 'smooth'});
    }
    
    // 页面加载完成后初始化
    initPage();
});
