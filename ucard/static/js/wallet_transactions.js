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

// 交易类型映射表
const TXN_TYPE_MAP = {
    'ACCOUNT_PAY': '账户支付',
    'ACCOUNT_PAY_FEE': '账户支付手续费',
    'BALANCE_RECHARGE': '充值到资金账户',
    'BALANCE_RECHARGE_FEE': '充值手续费',
    'EXCHANGE_OUT': '换汇支出',
    'EXCHANGE_IN': '换汇买入',
    'ACCOUNT_PAY_REVERT': '账户支付退回',
    'ACCOUNT_PAY_FEE_REVERT': '账户支付手续费退回',
    'EXCHANGE_FEE': '换汇手续费',
    'EXCHANGE_FEE_REVERT': '换汇手续费退回',
    'MANUAL': '运营手动调账',
    'CARD_PAYMENT': '虚拟卡交易结算',
    'CARD_PAYMENT_FEE': '虚拟卡交易结算手续费',
    'CARD_PAYMENT_FEE_REVERT': '虚拟卡交易手续费退回',
    'CARD_REFUND': '虚拟卡交易退款',
    'CARD_REFUND_FEE': '虚拟卡交易退款手续费',
    'CARD_PAY_REVERT': '虚拟卡交易撤销',
    'CARD_REFUND_REVERT': '虚拟卡交易退款撤销',
    'CARD_REFUND_FEE_REVERT': '虚拟卡交易退款手续费退回',
    'CARD_PRE_AUTH': '虚拟卡交易授权',
    'CARD_PRE_AUTH_REVERT': '虚拟卡交易授权撤销',
    'CARD_PRE_AUTH_FEE': '虚拟卡交易授权手续费',
    'CHARGEBACK': 'Chargeback手续费',
    'CARD_BALANCE_ADJUST': '卡余额调整',
    'CARD_INIT_FEE': '虚拟卡开卡手续费',
    'CARD_INIT_FEE_REVERT': '创建虚拟卡手续费退回',
    'CARD_SERVICE_FEE': '虚拟卡服务费',
    'CARD_CANCEL_FEE': '销卡手续费',
    'OTHER': '其他'
};

// 获取交易类型的中文描述
function getTxnTypeText(txnType) {
    if (!txnType) return '-';
    return TXN_TYPE_MAP[txnType] || txnType;
}

// 初始化页面
function initTransactionsPage() {
    console.log('初始化交易明细页面');
    
    // 获取钱包数据
    if (typeof walletDataJson !== 'undefined') {
        try {
            walletData = JSON.parse(walletDataJson);
            currentCurrency = walletData.currency_code || '';
            updateCurrencyInfo(walletData);
            updateBalanceSummary(walletData);
            console.log('已加载钱包数据:', walletData);
        } catch (e) {
            console.error('解析钱包数据错误:', e);
        }
    }

    // 获取交易数据
    if (typeof transactionsDataJson !== 'undefined') {
        try {
            transactionData = JSON.parse(transactionsDataJson) || [];
            console.log('已加载交易数据:', transactionData.length, '条记录');
            
            // 初始化后立即渲染交易列表
            let filteredTransactions = filterTransactions();
            console.log('筛选后的交易数据:', filteredTransactions.length, '条记录');
            renderTransactionList(filteredTransactions);
        } catch (e) {
            console.error('解析交易数据错误:', e);
            transactionData = [];
            renderTransactionList([]);
        }
    } else {
        console.warn('未找到交易数据变量');
        renderTransactionList([]);
    }

    // 获取区域数据
    if (typeof regionDataJson !== 'undefined') {
        try {
            regionData = JSON.parse(regionDataJson) || {};
            console.log('已加载区域数据');
        } catch (e) {
            console.error('解析区域数据错误:', e);
            regionData = {};
        }
    }

    // 初始化日期选择器和表单
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
        
        // 确保交易类型下拉框正常渲染
        const transactionTypeSelect = document.querySelector('#transaction-type');
        if (transactionTypeSelect) {
            // 添加layui-form class以确保layui可以正确渲染下拉框
            if (!transactionTypeSelect.classList.contains('layui-select')) {
                transactionTypeSelect.classList.add('layui-select');
            }
            
            // 确保所有交易类型都有对应的选项
            form.render('select');
        }
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
    
    // 先筛选出与当前钱包币种和平台匹配的交易记录
    let filteredByWallet = transactionData.filter(function(transaction) {
        // 检查金额货币是否匹配
        const currencyMatch = transaction.amount_currency === (currentCurrency || walletData.currency || walletData.currency_code);
        
        // 检查平台是否匹配（如果选择了特定平台）
        let versionMatch = true;
        if (walletData && walletData.version && walletData.version !== '全部') {
            versionMatch = transaction.version === walletData.version;
        }
        
        return currencyMatch && versionMatch;
    });
    
    // 再根据搜索条件进一步筛选
    let filteredBySearch = filteredByWallet.filter(function(transaction) {
        let matchTransactionId = true;
        let matchTransactionType = true;
        let matchDateRange = true;
        
        // 流水号搜索
        if (searchParams.transactionId) {
            matchTransactionId = (transaction.transaction_id && 
                transaction.transaction_id.toLowerCase().includes(searchParams.transactionId.toLowerCase()));
        }
        
        // 交易类型搜索
        if (searchParams.transactionType) {
            if (searchParams.transactionType === 'income') {
                // 收入 - 金额为正
                matchTransactionType = parseFloat(transaction.amount || 0) > 0;
            } else if (searchParams.transactionType === 'expense') {
                // 支出 - 金额为负
                matchTransactionType = parseFloat(transaction.amount || 0) < 0;
            } else {
                // 特定交易类型匹配
                matchTransactionType = transaction.txn_type === searchParams.transactionType;
            }
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
        
        return matchTransactionId && matchTransactionType && matchDateRange;
    });
    
    // 按交易时间倒序排序（最新的在前）
    filteredBySearch.sort(function(a, b) {
        const timeA = new Date(a.transaction_time || a.transaction_date || 0);
        const timeB = new Date(b.transaction_time || b.transaction_date || 0);
        return timeB - timeA; // 倒序排列
    });
    
    return filteredBySearch;
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
    
    // 如果没有交易数据，显示空数据提示并渲染分页
    if (!transactions || !transactions.length) {
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:20px;">暂无交易数据</td></tr>`;
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
        const amountCurrency = transaction.amount_currency || '';
        const amountDisplay = formatAmount(amountValue) + (amountCurrency ? ' ' + amountCurrency : '');
        
        // 账户金额
        const afterBalanceAmount = parseFloat(transaction.after_balance_amount || 0);
        const afterBalanceCurrency = transaction.after_balance_currency || '';
        const balanceDisplay = formatAmount(afterBalanceAmount) + (afterBalanceCurrency ? ' ' + afterBalanceCurrency : '');
        
        // 获取交易类型
        const txnType = transaction.txn_type || '-';
        
        // 获取平台版本
        const version = transaction.version || '-';
        
        row.innerHTML = `
            <td>${transactionTime}</td>
            <td title="${transaction.transaction_id || '-'}">${transaction.transaction_id || '-'}</td>
            <td>${getTxnTypeText(txnType)}</td>
            <td class="${amountClass}">${amountDisplay}</td>
            <td>${balanceDisplay}</td>
            <td>${version}</td>
            <td title="${transaction.remark || '-'}">${transaction.remark || '-'}</td>
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
        
        // 添加货币单位
        const amountWithCurrency = `${formatAmount(transaction.amount || 0)} ${transaction.amount_currency || ''}`;
        const balanceWithCurrency = `${formatAmount(transaction.after_balance_amount || 0)} ${transaction.after_balance_currency || ''}`;
        
        const row = [
            transactionTime,
            transaction.transaction_id || '-',
            getTxnTypeText(transaction.txn_type || '-'),
            amountWithCurrency,
            balanceWithCurrency,
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
    currentCurrency = currencyData.currency_code || currencyData.currency || '';
    
    console.log('打开交易明细弹窗:', currentCurrency, '平台:', currencyData.version);
    console.log('钱包数据:', walletData);
    
    layui.use(['layer'], function() {
        const layer = layui.layer;
        
        // 设置平台标题
        let title = '钱包交易明细';
        if (currencyData.version && currencyData.version !== '全部') {
            title += ` (平台: ${currencyData.version})`;
        }
        
        // 直接使用页面上已有的数据
        if (typeof transactionsDataJson !== 'undefined') {
            try {
                transactionData = JSON.parse(transactionsDataJson) || [];
                console.log('加载交易数据:', transactionData.length, '条记录');
            } catch (e) {
                console.error('解析交易数据失败:', e);
                transactionData = [];
            }
        }
        
        // 打开弹窗
        layer.open({
            type: 1,
            title: title,
            area: ['90%', '80%'], // 修改为相对宽度而非固定宽度
            maxWidth: 1200, // 设置最大宽度
            shadeClose: true,
            maxmin: true, // 允许最大化
            content: $('#transactionsContainer'),
            success: function(layero, index) {
                // 调整弹窗位置，确保在屏幕中居中
                $(layero).css({
                    'top': '50%',
                    'margin-top': -$(layero).height() / 2
                });
                
                // 弹窗打开后初始化页面，先更新钱包信息，再处理交易数据
                updateCurrencyInfo(currencyData);
                updateBalanceSummary(currencyData);
                
                // 绑定事件
                bindEvents();
                
                // 根据当前钱包币种和平台筛选并渲染交易列表
                searchParams = {
                    startDate: '',
                    endDate: '',
                    transactionId: '',
                    transactionType: ''
                };
                
                // 重置搜索框值
                const transactionIdInput = document.querySelector('#transaction-id-input');
                const transactionTypeSelect = document.querySelector('#transaction-type');
                const dateStartInput = document.querySelector('#date-start');
                const dateEndInput = document.querySelector('#date-end');
                
                if (transactionIdInput) transactionIdInput.value = '';
                if (transactionTypeSelect) transactionTypeSelect.value = '';
                if (dateStartInput) dateStartInput.value = '';
                if (dateEndInput) dateEndInput.value = '';
                
                // 筛选并渲染交易列表
                const filteredTransactions = filterTransactions();
                console.log('筛选条件 - 币种:', currentCurrency, '平台:', currencyData.version);
                console.log('筛选后交易记录数:', filteredTransactions.length);
                if (filteredTransactions.length > 0) {
                    console.log('示例交易记录:', filteredTransactions[0]);
                }
                
                renderTransactionList(filteredTransactions);
            },
            end: function() {
                // 弹窗关闭时清空容器内容，防止在主页面显示
                const container = document.getElementById('transactionsContainer');
                if (container) {
                    // 保留容器但清空内容
                    container.innerHTML = '';
                    // 隐藏容器
                    container.style.display = 'none';
                }
            }
        });
    });
}

// 导出函数到全局，以供wallet_balance.js调用
window.openTransactionDetails = openTransactionDetails;
