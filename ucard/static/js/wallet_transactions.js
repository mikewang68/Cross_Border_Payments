/* 钱包交易明细页面脚本 */

// 初始化变量
let walletData = {};
let transactionData = [];
let regionData = {};
let currentCurrency = '';
let currentPage = 1;
let pageSize = 10;
let totalPages = 0;
let searchParams = {
    startDate: '',
    endDate: '',
    transactionId: '',
    transactionType: ''
};

// 初始化页面
function initTransactionsPage() {
    // 获取钱包数据
    if (typeof walletDataJson !== 'undefined') {
        walletData = JSON.parse(walletDataJson);
        currentCurrency = walletData.currency_code || '';
        updateCurrencyInfo(walletData);
        updateBalanceSummary(walletData);
    }

    // 获取交易数据
    if (typeof transactionsDataJson !== 'undefined') {
        transactionData = JSON.parse(transactionsDataJson) || [];
        renderTransactionList(filterTransactions());
    }

    // 获取区域数据
    if (typeof regionDataJson !== 'undefined') {
        regionData = JSON.parse(regionDataJson) || {};
    }

    // 初始化日期选择器
    layui.use(['laydate', 'form'], function() {
        const laydate = layui.laydate;
        const form = layui.form;
        
        laydate.render({
            elem: '#date-start',
            type: 'date',
            done: function(value) {
                searchParams.startDate = value;
            }
        });
        
        laydate.render({
            elem: '#date-end',
            type: 'date',
            done: function(value) {
                searchParams.endDate = value;
            }
        });
        
        // 渲染表单元素
        form.render('select');
    });

    // 绑定事件
    bindEvents();
}

// 更新货币信息
function updateCurrencyInfo(data) {
    const flagElement = document.querySelector('#currency-flag');
    const codeElement = document.querySelector('#currency-code');
    const nameElement = document.querySelector('#currency-name-full');
    
    if (data && data.currency_code) {
        if (flagElement) {
            // 确保清除旧内容
            flagElement.innerHTML = '';
            
            // 使用传入的icon_base64数据设置国旗图标
            if (data.icon_base64) {
                const img = document.createElement('img');
                img.src = `data:image/png;base64,${data.icon_base64}`;
                img.alt = data.currency_code;
                flagElement.appendChild(img);
            } else {
                // 使用默认图标或创建文本占位符
                const placeholder = document.createElement('div');
                placeholder.textContent = data.currency_code.substring(0, 2);
                placeholder.className = 'flag-placeholder';
                flagElement.appendChild(placeholder);
            }
        }
        
        if (codeElement) {
            codeElement.textContent = data.currency_code;
        }
        
        if (nameElement && data.currency_name) {
            nameElement.textContent = data.currency_name;
        }
    }
}

// 更新余额摘要
function updateBalanceSummary(data) {
    if (!data) return;
    
    const totalBalanceElement = document.querySelector('#total-balance');
    const sharedBalanceElement = document.querySelector('#shared-balance');
    const availableBalanceElement = document.querySelector('#available-balance');
    
    if (totalBalanceElement) {
        totalBalanceElement.textContent = formatAmount(data.balance || 0);
    }
    
    if (sharedBalanceElement) {
        sharedBalanceElement.textContent = formatAmount(data.shared_balance || 0);
    }
    
    if (availableBalanceElement) {
        availableBalanceElement.textContent = formatAmount(data.available_balance || 0);
    }
}

// 绑定事件
function bindEvents() {
    // 搜索按钮
    const searchButton = document.querySelector('#search-btn');
    if (searchButton) {
        searchButton.addEventListener('click', function() {
            searchParams.transactionId = document.querySelector('#transaction-id-input').value;
            searchParams.transactionType = document.querySelector('#transaction-type').value;
            currentPage = 1;
            renderTransactionList(filterTransactions());
        });
    }
    
    // 交易类型选择
    const transactionTypeSelect = document.querySelector('#transaction-type');
    if (transactionTypeSelect) {
        transactionTypeSelect.addEventListener('change', function() {
            searchParams.transactionType = this.value;
        });
    }
    
    // 重置按钮
    const clearButton = document.querySelector('#clear-btn');
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            document.querySelector('#transaction-id-input').value = '';
            document.querySelector('#transaction-type').value = '';
            document.querySelector('#date-start').value = '';
            document.querySelector('#date-end').value = '';
            
            searchParams = {
                startDate: '',
                endDate: '',
                transactionId: '',
                transactionType: ''
            };
            
            currentPage = 1;
            renderTransactionList(filterTransactions());
        });
    }
    
    // 导出按钮
    const exportButton = document.querySelector('#export-btn');
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            exportTransactionData();
        });
    }
}

// 过滤交易数据
function filterTransactions() {
    if (!transactionData || !transactionData.length) return [];
    
    return transactionData.filter(function(transaction) {
        let matchTransactionId = true;
        let matchTransactionType = true;
        let matchDateRange = true;
        let matchVersion = true;
        
        // 流水号搜索
        if (searchParams.transactionId) {
            matchTransactionId = (transaction.transaction_id && 
                transaction.transaction_id.toLowerCase().includes(searchParams.transactionId.toLowerCase()));
        }
        
        // 交易类型搜索
        if (searchParams.transactionType) {
            if (searchParams.transactionType === 'income') {
                matchTransactionType = parseFloat(transaction.amount || 0) > 0;
            } else if (searchParams.transactionType === 'expense') {
                matchTransactionType = parseFloat(transaction.amount || 0) < 0;
            }
        }
        
        // 平台(版本)筛选
        if (walletData && walletData.version && walletData.version !== '全部') {
            matchVersion = transaction.version === walletData.version;
        }
        
        // 日期范围搜索
        if (searchParams.startDate) {
            const transactionDate = new Date(transaction.transaction_time || transaction.transaction_date);
            const startDate = new Date(searchParams.startDate);
            matchDateRange = transactionDate >= startDate;
        }
        
        if (searchParams.endDate && matchDateRange) {
            const transactionDate = new Date(transaction.transaction_time || transaction.transaction_date);
            const endDate = new Date(searchParams.endDate);
            // 设置结束日期为当天的最后一刻
            endDate.setHours(23, 59, 59, 999);
            matchDateRange = transactionDate <= endDate;
        }
        
        return matchTransactionId && matchTransactionType && matchDateRange && matchVersion;
    });
}

// 渲染交易列表
function renderTransactionList(transactions) {
    const tableContainer = document.querySelector('.transactions-table');
    
    // 创建表格结构
    let tableHTML = `
    <table class="layui-table" id="transactions-table" lay-filter="transactions-table">
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
    
    // 如果没有交易数据，不显示任何内容
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

// 渲染分页
function renderPagination(total) {
    const paginationElement = document.querySelector('.transactions-pagination');
    if (!paginationElement) return;
    
    totalPages = Math.ceil(total / pageSize);
    
    layui.use(['laypage'], function() {
        const laypage = layui.laypage;
        
        laypage.render({
            elem: 'transactions-pagination',
            count: total,
            limit: pageSize,
            curr: currentPage,
            layout: ['count', 'prev', 'page', 'next', 'skip'],
            jump: function(obj, first) {
                if (!first) {
                    currentPage = obj.curr;
                    renderTransactionList(filterTransactions());
                }
            }
        });
    });
}

// 导出交易数据
function exportTransactionData() {
    const filteredData = filterTransactions();
    if (!filteredData || !filteredData.length) {
        layer.msg('没有可导出的数据');
        return;
    }
    
    // 构建CSV内容
    let csvContent = "交易时间,流水号,交易类型,交易金额,账户金额,平台,交易备注\n";
    
    filteredData.forEach(function(transaction) {
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
        
        const row = [
            transactionTime,
            transaction.transaction_id || '-',
            transaction.txn_type || '-',
            formatAmount(transaction.amount || 0),
            formatAmount(transaction.after_balance_amount || 0),
            transaction.version || '-',
            transaction.remark || '-'
        ];
        
        // 处理备注中可能的逗号
        row[6] = `"${row[6]}"`;
        
        csvContent += row.join(',') + '\n';
    });
    
    // 创建下载
    const encodedUri = encodeURI("data:text/csv;charset=utf-8," + csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `${currentCurrency}_交易明细_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 格式化金额
function formatAmount(amount) {
    const num = parseFloat(amount);
    if (isNaN(num)) return '0.00';
    
    return num.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initTransactionsPage();
});

// 打开交易明细弹窗
function openTransactionDetails(currencyData) {
    // 保存当前货币数据
    walletData = currencyData;
    currentCurrency = currencyData.currency_code;
    
    layui.use(['layer'], function() {
        const layer = layui.layer;
        
        // 设置平台标题
        let title = '钱包交易明细';
        if (currencyData.version && currencyData.version !== '全部') {
            title += ` (平台: ${currencyData.version})`;
        }
        
        // 显示加载中
        const loadingIndex = layer.load(1, {
            shade: [0.1, '#fff']
        });
        
        // 自动刷新交易数据
        fetch(`/api/wallet_transactions?currency=${currencyData.currency_code}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`网络请求失败: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                layer.close(loadingIndex);
                
                if (data && data.status === 'success') {
                    // 更新交易数据
                    transactionData = data.data || [];
                } else if (data) {
                    console.warn('获取交易数据不成功:', data.message || '未知错误');
                }
                
                // 打开弹窗
                openTransactionsPopup(layer, title, currencyData);
            })
            .catch(error => {
                layer.close(loadingIndex);
                console.error('自动刷新交易数据请求出错:', error.message);
                
                // 失败时尝试使用页面上已有的数据
                if (typeof transactionsDataJson !== 'undefined') {
                    try {
                        transactionData = JSON.parse(transactionsDataJson) || [];
                    } catch (e) {
                        console.error('解析现有交易数据失败:', e);
                        transactionData = [];
                    }
                }
                
                // 出错时仍然打开弹窗但使用现有数据
                openTransactionsPopup(layer, title, currencyData);
            });
    });
}

// 打开交易弹窗 - 提取为单独函数以避免代码重复
function openTransactionsPopup(layer, title, currencyData) {
    layer.open({
        type: 1,
        title: title,
        area: ['900px', '80%'],
        shadeClose: true,
        content: $('#transactionsContainer'),
        success: function() {
            // 弹窗打开后初始化页面
            updateCurrencyInfo(currencyData);
            updateBalanceSummary(currencyData);
            bindEvents();
            renderTransactionList(filterTransactions());
        }
    });
}

// 导出函数
window.openTransactionDetails = openTransactionDetails;
