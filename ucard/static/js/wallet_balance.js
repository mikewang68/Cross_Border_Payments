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
    
    // 初始化钱包数据
    function initWalletData(data, selectedVersion) {
        console.log('初始化钱包数据:', data);
        console.log('选择的平台:', selectedVersion);
        
        // 清空货币列表
        var currencyListElem = document.getElementById('currency-list');
        if (currencyListElem) {
            currencyListElem.innerHTML = '';
        }
        
        // 处理数据为空的情况
        if (!data || data.length === 0) {
            console.log('钱包数据为空');
            var emptyNotice = document.createElement('div');
            emptyNotice.className = 'layui-col-xs12 layui-col-sm12 layui-col-md12';
            emptyNotice.innerHTML = '<div class="empty-notice">暂无钱包余额数据</div>';
            currencyListElem.appendChild(emptyNotice);
            return;
        }
        
        // 根据选定的版本/平台，汇总每种货币的余额
        var summaryData = {};
        
        data.forEach(function(item) {
            // 如果选择了特定平台，且当前项不是该平台，则跳过
            if (selectedVersion && selectedVersion !== '' && item.version !== selectedVersion) {
                return;
            }
            
            var currency = item.currency;
            
            // 如果该货币还没有在汇总中，则创建
            if (!summaryData[currency]) {
                summaryData[currency] = {
                    currency: currency,
                    amount: 0,
                    available: 0, // 增加available字段用于计算
                    user_id: item.user_id,
                    update_time: item.update_time || new Date().toISOString(),
                    version: selectedVersion || '全部'
                };
            }
            
            // 累加余额和可用余额
            summaryData[currency].amount += parseFloat(item.amount || 0);
            summaryData[currency].available += parseFloat(item.available || 0);
        });
        
        // 将汇总数据转为数组并排序
        var currencyList = Object.values(summaryData);
        currencyList.sort(function(a, b) {
            return b.amount - a.amount; // 按金额从高到低排序
        });
        
        // 计算总余额
        var totalAmount = 0;
        currencyList.forEach(function(item) {
            totalAmount += item.amount;
        });
        
        // 更新总余额显示
        var mainAmountElem = document.getElementById('main-amount');
        if (mainAmountElem) {
            mainAmountElem.textContent = totalAmount.toFixed(2);
        }
        
        // 为每种货币创建卡片
        currencyList.forEach(function(currencyData) {
            var currencyCode = currencyData.currency;
            var amount = parseFloat(currencyData.amount);
            var regionInfo = currencyToRegion[currencyCode] || {};
            
            var colDiv = document.createElement('div');
            colDiv.className = 'layui-col-xs12 layui-col-sm6 layui-col-md4 layui-col-lg3';
            
            var cardContent = `
                <div class="currency-card" data-currency="${currencyCode}">
                    <div class="card-header">
                        <div class="flag-container">
                            ${regionInfo.icon_base64 ? 
                                `<img src="data:image/png;base64,${regionInfo.icon_base64}" alt="${currencyCode}" class="flag-icon">` :
                                `<div class="flag-placeholder">${currencyCode.substring(0, 2)}</div>`
                            }
                        </div>
                        <div class="currency-info">
                            <div class="currency-code">${currencyCode}</div>
                            <div class="currency-name">${regionInfo.name || currencyCode}</div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="amount-container">
                            <div class="amount">${amount.toFixed(2)}</div>
                            <div class="available-amount">可用: ${(parseFloat(currencyData.available) || 0).toFixed(2)}</div>
                        </div>
                        <div class="transaction-btn">
                            <button class="layui-btn layui-btn-normal layui-btn-sm view-transactions" data-currency="${currencyCode}">
                                <i class="layui-icon layui-icon-list"></i> 明细
                            </button>
                        </div>
                    </div>
                </div>`;
            
            colDiv.innerHTML = cardContent;
            currencyListElem.appendChild(colDiv);
            
            // 为明细按钮添加点击事件
            var transactionBtn = colDiv.querySelector('.view-transactions');
            if (transactionBtn) {
                transactionBtn.addEventListener('click', function() {
                    openCurrencyTransactions(currencyData, regionInfo);
                });
            }
        });
    }
    
    // 打开货币交易明细弹窗
    function openCurrencyTransactions(walletItem, regionInfo) {
        // 获取当前选择的平台
        var formData = form.val('walletSearchForm');
        var selectedVersion = formData.version || '';
        
        var totalBalance = 0;
        var availableBalance = 0;
        var sharedBalance = 0;
        
        // 如果是特定平台，则使用该平台的金额和可用余额
        if (selectedVersion && selectedVersion !== '') {
            // 使用特定平台的余额
            totalBalance = parseFloat(walletItem.amount);
            availableBalance = parseFloat(walletItem.available || 0);
        } else {
            // 全部平台情况 - 需要根据相同货币和用户ID汇总不同平台的余额
            var totalAmount = 0;
            var totalAvailable = 0;
            
            originalWalletData.forEach(function(item) {
                if (item.currency === walletItem.currency) {
                    totalAmount += parseFloat(item.amount || 0);
                    totalAvailable += parseFloat(item.available || 0);
                }
            });
            
            totalBalance = totalAmount;
            availableBalance = totalAvailable;
        }
        
        // 计算共享卡已开卡余额 = 总额 - 可用余额
        sharedBalance = totalBalance - availableBalance;
        
        // 构建完整的钱包数据对象
        var currencyData = {
            currency_code: walletItem.currency,
            currency_name: regionInfo.name || walletItem.currency,
            balance: totalBalance,
            shared_balance: sharedBalance,
            available_balance: availableBalance,
            user_id: walletItem.user_id,
            update_time: walletItem.update_time,
            version: selectedVersion || '全部',
            // 添加国旗图标数据
            icon_base64: regionInfo.icon_base64 || null
        };
        
        // 检查交易明细函数是否已加载
        if (typeof window.openTransactionDetails !== 'function') {
            // 如果函数不存在，动态加载脚本
            var script = document.createElement('script');
            script.src = '/static/js/wallet_transactions.js';
            script.onload = function() {
                // 脚本加载完成后调用函数
                window.openTransactionDetails(currencyData);
            };
            document.head.appendChild(script);
            
            // 加载CSS
            if (!document.querySelector('link[href="/static/css/wallet_transactions.css"]')) {
                var link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = '/static/css/wallet_transactions.css';
                document.head.appendChild(link);
            }
        } else {
            // 如果函数已存在，直接调用
            window.openTransactionDetails(currencyData);
        }
    }
    
    // 页面加载完成后初始化和自动刷新余额
    initWalletData(walletData, '');
    
    // 自动刷新余额信息
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
                
                layer.msg('余额已自动刷新', {icon: 1});
            } else {
                console.error('自动刷新失败:', data.message);
            }
        })
        .catch(error => {
            layer.close(loadingIndex);
            console.error('自动刷新请求出错:', error.message);
        });
    
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
    
    // 渲染表单元素
    form.render();
});

// 重构renderTransactionList函数，动态创建表格，不显示"暂无交易数据"
function renderTransactionList(transactions) {
    const tableContainer = document.querySelector('.transactions-table');
    
    // 创建表格结构
    let tableHTML = `
    <table class="layui-table" id="transactions-table" lay-skin="line">
        <thead>
            <tr>
                <th>交易时间</th>
                <th>流水号</th>
                <th>交易类型</th>
                <th>交易金额</th>
                <th>账户金额</th>
                <th>平台</th>
                <th>交易备注</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>`;
    
    tableContainer.innerHTML = tableHTML;
    
    const tableBody = document.querySelector('#transactions-table tbody');
    if (!tableBody) return;
    
    // 如果没有交易数据，仅渲染分页
    if (!transactions || !transactions.length) {
        renderPagination(0);
        return;
    }
    
    // 计算分页
    totalPages = Math.ceil(transactions.length / pageSize);
    const start = (currentPage - 1) * pageSize;
    const end = Math.min(start + pageSize, transactions.length);
    const pageTransactions = transactions.slice(start, end);
    
    // 渲染数据
    pageTransactions.forEach(function(transaction) {
        const row = document.createElement('tr');
        
        // 格式化日期
        const transactionTime = transaction.transaction_time ? 
            new Date(transaction.transaction_time).toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            }).replace(/\//g, '-') : '-';
        
        // 确定金额的正负 (收入为正, 支出为负)
        const amountValue = parseFloat(transaction.amount || 0);
        const amountClass = amountValue >= 0 ? 'positive-amount' : 'negative-amount';
        const amountDisplay = formatAmount(amountValue);
        
        // 账户金额
        const afterBalanceAmount = parseFloat(transaction.after_balance_amount || 0);
        const balanceDisplay = formatAmount(afterBalanceAmount);
        
        // 获取交易类型
        const txnType = transaction.txn_type || '-';
        
        // 获取平台版本
        const version = transaction.version || '-';
        
        row.innerHTML = `
            <td>${transactionTime}</td>
            <td>${transaction.transaction_id || '-'}</td>
            <td>${txnType}</td>
            <td class="${amountClass}">${amountDisplay}</td>
            <td>${balanceDisplay}</td>
            <td>${version}</td>
            <td>${transaction.remark || '-'}</td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // 渲染分页
    renderPagination(transactions.length);
}
