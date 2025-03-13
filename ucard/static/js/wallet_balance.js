// 钱包余额页面脚本
layui.use(['element', 'layer'], function() {
    var element = layui.element;
    var layer = layui.layer;
    
    // 获取从后端传递的数据
    var walletData = JSON.parse(document.getElementById('wallet-data').textContent);
    var regionData = JSON.parse(document.getElementById('region-data').textContent);
    
    // 调试输出
    console.log('钱包余额数据:', walletData);
    console.log('地区数据:', regionData);
    
    // 创建货币代码到地区数据的映射
    var currencyToRegion = {};
    if (regionData && regionData.length > 0) {
        regionData.forEach(function(region) {
            currencyToRegion[region.currency] = region;
        });
    }
    
    // 初始化数据
    function initWalletData() {
        // 如果没有数据，显示提示
        if (!walletData || walletData.length === 0) {
            layer.msg('暂无钱包余额数据', {icon: 5});
            return;
        }
        
        // 默认显示第一条记录的更新时间
        var updateTime = walletData[0].update_time || '';
        document.getElementById('update-time').textContent = '（更新于' + updateTime + '）';
        
        // 清空货币列表
        var currencyListEl = document.getElementById('currency-list');
        currencyListEl.innerHTML = '';
        
        // 创建货币卡片
        // 常见货币顺序：USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY
        var commonCurrencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY'];
        var otherCurrencies = [];
        
        // 将钱包数据按照常见货币顺序排序
        var sortedWalletData = [];
        
        // 首先添加常见货币
        commonCurrencies.forEach(function(currency) {
            // 查找钱包中是否有该货币
            var walletItem = walletData.find(function(item) {
                return item.currency === currency;
            });
            
            if (walletItem) {
                sortedWalletData.push(walletItem);
            } else {
                // 如果钱包中没有该货币，但是地区数据中有，创建一个零余额数据
                if (currencyToRegion[currency]) {
                    sortedWalletData.push({
                        currency: currency,
                        amount: 0,
                        user_id: walletData[0].user_id,
                        update_time: updateTime
                    });
                }
            }
        });
        
        // 然后添加其他货币
        walletData.forEach(function(item) {
            if (!commonCurrencies.includes(item.currency)) {
                sortedWalletData.push(item);
            }
        });
        
        // 渲染所有货币卡片
        sortedWalletData.forEach(function(item) {
            createCurrencyCard(item, currencyListEl);
        });
        
        // 计算所有货币余额的总和
        var totalAmount = 0;
        walletData.forEach(function(item) {
            totalAmount += parseFloat(item.amount || 0);
        });
        
        // 将总额显示在主余额区域
        document.getElementById('main-amount').textContent = totalAmount.toFixed(2);
        document.getElementById('main-currency').textContent = '总额';
    }
    
    // 创建货币卡片
    function createCurrencyCard(item, container) {
        // 获取对应的地区数据
        var region = currencyToRegion[item.currency] || {};
        var iconBase64 = region.icon_base64 || '';
        var currencyName = region.name || item.currency;
        
        // 处理Base64图标
        var flagImage = '';
        if (iconBase64) {
            // 检查是否已经包含data:image前缀
            if (iconBase64.startsWith('data:')) {
                flagImage = iconBase64;
            } else {
                // 添加base64图像前缀
                flagImage = 'data:image/png;base64,' + iconBase64;
            }
        } else {
            // 没有图标，使用默认图标
            flagImage = '/static/images/flag-placeholder.png';
        }
        
        // 创建卡片元素
        var cardEl = document.createElement('div');
        cardEl.className = 'layui-col-xs12 layui-col-sm6 layui-col-md4 layui-col-lg3';
        
        // 设置卡片内容
        var isZeroBalance = parseFloat(item.amount) === 0;
        var amountClass = isZeroBalance ? 'currency-amount zero-balance' : 'currency-amount';
        
        cardEl.innerHTML = `
            <div class="currency-card" data-currency="${item.currency}">
                <div class="flag-container">
                    <img src="${flagImage}" alt="${item.currency}">
                </div>
                <div class="currency-info">
                    <div class="currency-name">${currencyName}</div>
                    <div class="${amountClass}">${parseFloat(item.amount).toFixed(2)}</div>
                </div>
            </div>
        `;
        
        // 点击卡片更新主余额显示
        cardEl.querySelector('.currency-card').addEventListener('click', function() {
            document.getElementById('main-amount').textContent = parseFloat(item.amount).toFixed(2);
            document.getElementById('main-currency').textContent = item.currency;
        });
        
        // 添加到容器
        container.appendChild(cardEl);
    }
    
    // 刷新余额按钮点击事件
    document.getElementById('refresh-balance').addEventListener('click', function() {
        var loadingIndex = layer.load(1, {
            shade: [0.1, '#fff']
        });
        
        // 发送AJAX请求获取最新数据
        fetch('/api/wallet_data')
            .then(response => response.json())
            .then(data => {
                layer.close(loadingIndex);
                if (data.status === 'success') {
                    // 更新数据并重新渲染
                    walletData = data.data.wallet_balances;
                    regionData = data.data.regions;
                    
                    // 重新创建映射
                    currencyToRegion = {};
                    if (regionData && regionData.length > 0) {
                        regionData.forEach(function(region) {
                            currencyToRegion[region.currency] = region;
                        });
                    }
                    
                    // 重新初始化显示
                    initWalletData();
                    layer.msg('余额刷新成功', {icon: 1});
                } else {
                    layer.msg('刷新失败: ' + data.message, {icon: 2});
                }
            })
            .catch(error => {
                layer.close(loadingIndex);
                layer.msg('请求出错: ' + error.message, {icon: 2});
            });
    });
    
    // 页面加载完成后初始化
    initWalletData();
});
