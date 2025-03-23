// 汇率报价JS
layui.use(['element', 'layer', 'form', 'table'], function() {
    var element = layui.element;
    var layer = layui.layer;
    var form = layui.form;
    var table = layui.table;
    
    // 全局变量
    var exchangeData = [];
    var selectedCurrency = null;
    
    // 初始化页面
    function initPage() {
        console.log('初始化汇率报价页面');
        
        // 获取后端传递的汇率数据
        try {
            var exchangeDataJson = document.getElementById('exchange-data').textContent;
            exchangeData = JSON.parse(exchangeDataJson) || [];
            console.log('加载汇率数据:', exchangeData.length, '条记录');
            
            // 初始化币种下拉框
            initCurrencySelect();
            
            // 渲染汇率表格
            renderExchangeRatesTable();
        } catch (e) {
            console.error('解析汇率数据失败:', e);
            exchangeData = [];
            layer.msg('加载汇率数据失败，请刷新页面重试', {icon: 2});
        }
        
        // 绑定事件
        bindEvents();
    }
    
    // 初始化币种下拉框
    function initCurrencySelect() {
        var select = document.getElementById('currency-select');
        if (!select) return;
        
        // 清空选项
        select.innerHTML = '<option value="">请选择币种</option>';
        
        // 添加选项
        exchangeData.forEach(function(item) {
            var option = document.createElement('option');
            option.value = item.currency;
            option.textContent = item.currency + (item.currency_name ? ' - ' + item.currency_name : '');
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
        
        // 无数据提示
        if (!exchangeData || exchangeData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">暂无汇率数据</td></tr>';
            return;
        }
        
        // 添加表格行
        exchangeData.forEach(function(item) {
            var row = document.createElement('tr');
            
            // 格式化数据
            var currency = item.currency || '-';
            var currencyName = item.currency_name || '-';
            var officialRate = parseFloat(item.official_rate || 0).toFixed(4);
            var fee = (parseFloat(item.fee || 0) * 100).toFixed(2) + '%';
            var version = item.version || '-';
            var updateTime = item.insert_time || '-';
            
            // 创建表格单元格
            row.innerHTML = `
                <td>${currency}</td>
                <td>${currencyName}</td>
                <td>${officialRate}</td>
                <td>${fee}</td>
                <td>${version}</td>
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
    
    // 绑定事件
    function bindEvents() {
        // 币种选择事件
        form.on('select(currency-select)', function(data) {
            var currencyCode = data.value;
            if (!currencyCode) {
                selectedCurrency = null;
                return;
            }
            
            // 查找选中的币种数据
            selectedCurrency = exchangeData.find(function(item) {
                return item.currency === currencyCode;
            });
            
            console.log('选择币种:', selectedCurrency);
        });
        
        // 计算按钮点击事件
        document.getElementById('calculate-btn').addEventListener('click', function() {
            calculateExchange();
        });
        
        // 重置按钮点击事件（通过监听表单reset事件）
        document.querySelector('form[lay-filter="calculatorForm"]').addEventListener('reset', function() {
            // 隐藏结果容器
            document.getElementById('result-container').style.display = 'none';
            // 重置选中币种
            selectedCurrency = null;
        });
        
        // 金额输入框回车事件
        document.getElementById('amount-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault(); // 阻止默认表单提交
                calculateExchange();
            }
        });
    }
    
    // 计算汇率和最终报价
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
        var fee = parseFloat(selectedCurrency.fee || 0);
        
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
        document.getElementById('result-currency').textContent = selectedCurrency.currency + 
            (selectedCurrency.currency_name ? ' (' + selectedCurrency.currency_name + ')' : '');
        document.getElementById('result-rate').textContent = officialRate.toFixed(4);
        document.getElementById('result-fee').textContent = (fee * 100).toFixed(2) + '%';
        document.getElementById('result-amount').textContent = amount.toFixed(2);
        document.getElementById('result-total').textContent = finalPrice.toFixed(2);
        document.getElementById('result-final-rate').textContent = finalRate.toFixed(4);
        
        // 显示结果容器
        document.getElementById('result-container').style.display = 'block';
        
        // 滚动到结果区域
        document.getElementById('result-container').scrollIntoView({behavior: 'smooth'});
    }
    
    // 页面加载完成后初始化
    initPage();
});
