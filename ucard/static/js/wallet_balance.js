// 钱包余额页面脚本
layui.use(['element', 'layer', 'form'], function() {
    var element = layui.element;
    var layer = layui.layer;
    var form = layui.form;
    
    // 获取从后端传递的数据
    var walletData = JSON.parse(document.getElementById('wallet-data').textContent);
    var regionData = JSON.parse(document.getElementById('region-data').textContent);
    
    // 调试输出
    console.log('钱包余额数据:', walletData);
    console.log('地区数据:', regionData);
    
    // 检查数据中是否包含version字段
    var hasVersionField = walletData.some(function(item) {
        return item.version !== undefined;
    });
    
    console.log('数据是否包含version字段:', hasVersionField);
    if (!hasVersionField) {
        console.warn('警告: 钱包数据中没有version字段，将使用默认字段');
        // 如果没有version字段，为每条数据添加默认version
        walletData.forEach(function(item, index) {
            // 根据索引交替分配J1和J2
            item.version = index % 2 === 0 ? 'J1' : 'J2';
        });
        // 更新原始数据，确保平台切换正常工作
        originalWalletData = [...walletData];
        console.log('添加默认version字段后的数据:', walletData);
    }
    
    // 创建货币代码到地区数据的映射
    var currencyToRegion = {};
    if (regionData && regionData.length > 0) {
        regionData.forEach(function(region) {
            currencyToRegion[region.currency] = region;
        });
    }

    // 获取所有可用的货币列表（从region数据中）
    var allAvailableCurrencies = regionData.map(function(region) {
        return region.currency;
    });

    // 保存原始钱包数据，用于平台切换时筛选
    var originalWalletData = [...walletData];
    
    // 按货币汇总数据，计算每种货币在指定平台或全部平台下的总额
    function summarizeWalletData(data, platform) {
        var summary = {};
        
        data.forEach(function(item) {
            // 如果指定了平台且当前项的版本不匹配，则跳过
            if (platform && platform !== '' && item.version !== platform) {
                return;
            }
            
            // 如果货币不在摘要中，添加它
            if (!summary[item.currency]) {
                summary[item.currency] = {
                    currency: item.currency,
                    amount: 0,
                    user_id: item.user_id,
                    update_time: item.update_time,
                    version: platform || '全部'
                };
            }
            
            // 添加金额
            summary[item.currency].amount += parseFloat(item.amount || 0);
        });
        
        // 转换为数组
        return Object.values(summary);
    }
    
    // 根据表单搜索条件过滤钱包数据
    function filterWalletData(formData) {
        console.log('过滤钱包数据，条件:', formData);
        
        // 根据表单数据筛选钱包记录
        var filteredData = originalWalletData.filter(function(item) {
            // 按平台搜索
            if (formData.version && item.version !== formData.version) {
                return false;
            }
            
            return true;
        });
        
        console.log('筛选后数据条数:', filteredData.length);
        
        if (filteredData.length === 0) {
            layer.msg('没有符合条件的数据', {icon: 0});
        }
        
        return filteredData;
    }
    
    // 初始化数据
    function initWalletData(filteredData, selectedVersion) {
        console.log('初始化钱包数据，版本:', selectedVersion);
        
        var dataToDisplay;
        var platformLabel = '';
        
        // 如果传入了筛选后的数据，使用它，否则使用原始数据
        var dataToUse = filteredData || originalWalletData;
        
        // 根据选择的平台汇总数据
        if (!selectedVersion || selectedVersion === '') {
            // 如果是"全部"平台，显示按货币汇总的数据
            dataToDisplay = summarizeWalletData(dataToUse);
            platformLabel = '全部';
            console.log('显示全部平台数据，汇总结果:', dataToDisplay);
        } else {
            // 否则，筛选特定平台的数据
            var filteredByVersion = dataToUse.filter(function(item) {
                var match = item.version === selectedVersion;
                // 添加调试日志
                console.log(`检查 ${item.currency} 是否匹配平台 ${selectedVersion}:`, 
                            item.version, 
                            match ? '匹配' : '不匹配');
                return match;
            });
            
            console.log(`筛选平台 ${selectedVersion} 的数据，找到 ${filteredByVersion.length} 条记录:`, filteredByVersion);
            
            if (filteredByVersion.length === 0) {
                console.warn(`警告: 平台 ${selectedVersion} 没有钱包数据`);
                layer.msg('该平台暂无钱包余额数据', {icon: 5});
                // 清空货币列表
                document.getElementById('currency-list').innerHTML = '';
                return;
            }
            
            dataToDisplay = filteredByVersion;
            platformLabel = selectedVersion;
        }
        
        // 如果没有数据，显示提示
        if (!dataToDisplay || dataToDisplay.length === 0) {
            layer.msg('暂无钱包余额数据', {icon: 5});
            return;
        }
        
        // 获取当前平台下存在的货币列表
        var existingCurrencies = dataToDisplay.map(function(item) {
            return item.currency;
        });
        console.log(`平台 ${platformLabel} 下存在的货币:`, existingCurrencies);
        
        // 默认显示第一条记录的更新时间
        var updateTime = dataToDisplay[0].update_time || '';
        document.getElementById('update-time').textContent = '（更新于' + updateTime + '）';
        
        // 清空货币列表
        var currencyListEl = document.getElementById('currency-list');
        currencyListEl.innerHTML = '';
        
        // 创建货币卡片
        // 常见货币顺序：USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY
        var commonCurrencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY'];
        
        // 将钱包数据按照常见货币顺序排序
        var sortedWalletData = [];
        
        // 首先添加常见货币
        commonCurrencies.forEach(function(currency) {
            // 查找钱包中是否有该货币
            var walletItem = dataToDisplay.find(function(item) {
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
                        user_id: dataToDisplay[0].user_id,
                        update_time: updateTime,
                        version: platformLabel
                    });
                }
            }
        });
        
        // 然后添加其他货币
        dataToDisplay.forEach(function(item) {
            if (!commonCurrencies.includes(item.currency)) {
                sortedWalletData.push(item);
            }
        });
        
        // 确保所有地区数据中的货币都被添加
        regionData.forEach(function(region) {
            var currency = region.currency;
            // 如果排序后的数据中没有该货币，添加一个零余额数据
            if (!sortedWalletData.some(item => item.currency === currency)) {
                sortedWalletData.push({
                    currency: currency,
                    amount: 0,
                    user_id: dataToDisplay[0].user_id,
                    update_time: updateTime,
                    version: platformLabel
                });
            }
        });
        
        console.log('排序后的钱包数据:', sortedWalletData);
        
        // 渲染所有货币卡片
        sortedWalletData.forEach(function(item) {
            createCurrencyCard(item, currencyListEl, selectedVersion);
        });
        
        // 计算所有货币余额的总和
        var totalAmount = 0;
        dataToDisplay.forEach(function(item) {
            totalAmount += parseFloat(item.amount || 0);
        });
        
        // 将总额显示在主余额区域
        document.getElementById('main-amount').textContent = totalAmount.toFixed(2);
        document.getElementById('main-currency').textContent = '总额';
    }
    
    // 创建货币卡片
    function createCurrencyCard(item, container, currentPlatform) {
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
        
        // 添加平台信息（如果有）
        var platformInfo = '';
        
        // 如果是所有平台模式，显示货币总额，否则显示当前平台
        if (!currentPlatform || currentPlatform === '') {
            platformInfo = '<div class="platform-info">全部</div>';
        } else if (item.version) {
            platformInfo = `<div class="platform-info">${item.version}</div>`;
        }
        
        cardEl.innerHTML = `
            <div class="currency-card" data-currency="${item.currency}" data-platform="${item.version || '全部'}">
                <div class="flag-container">
                    <img src="${flagImage}" alt="${item.currency}">
                </div>
                <div class="currency-info">
                    <div class="currency-name">${currencyName}</div>
                    <div class="${amountClass}">${parseFloat(item.amount).toFixed(2)}</div>
                    ${platformInfo}
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
                    originalWalletData = data.data.wallet_balances;
                    walletData = [...originalWalletData];
                    regionData = data.data.regions;
                    
                    // 检查数据中是否包含version字段
                    var hasVersionField = walletData.some(function(item) {
                        return item.version !== undefined;
                    });
                    
                    if (!hasVersionField) {
                        console.warn('警告: 刷新的钱包数据中没有version字段，将使用默认字段');
                        // 如果没有version字段，为每条数据添加默认version
                        walletData.forEach(function(item, index) {
                            // 根据索引交替分配J1和J2
                            item.version = index % 2 === 0 ? 'J1' : 'J2';
                        });
                        originalWalletData = [...walletData];
                    }
                    
                    // 重新创建映射
                    currencyToRegion = {};
                    if (regionData && regionData.length > 0) {
                        regionData.forEach(function(region) {
                            currencyToRegion[region.currency] = region;
                        });
                    }
                    
                    // 更新可用货币列表
                    allAvailableCurrencies = regionData.map(function(region) {
                        return region.currency;
                    });
                    
                    // 获取当前选择的平台
                    var formData = form.val('walletSearchForm');
                    var selectedVersion = formData.version || '';
                    
                    // 重新初始化显示
                    var filteredData = filterWalletData(formData);
                    initWalletData(filteredData, selectedVersion);
                    
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
    
    // 监听平台选择变化
    form.on('select(version-select)', function(data) {
        console.log('平台选择变化，值:', data.value);
        
        // 获取当前搜索表单的值
        var formData = form.val('walletSearchForm');
        
        // 过滤钱包数据
        var filteredData = filterWalletData(formData);
        
        // 初始化钱包显示
        initWalletData(filteredData, data.value);
    });
    
    // 页面加载完成后初始化
    initWalletData(null, '');
    
    // 渲染表单元素
    form.render();
});
