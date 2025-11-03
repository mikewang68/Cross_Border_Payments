layui.use(['form', 'laydate', 'table'], function(){
    var form = layui.form;
    var laydate = layui.laydate;
    var table = layui.table;
    var $ = layui.jquery;

    // 初始化日期选择器
    laydate.render({
        elem: '#dateFilter',
        type: 'date',
        value: '', // 默认不选择日期
        format: 'yyyy-MM-dd', // 指定显示格式
        done: function(value){ // 日期选择完成后的回调
            console.log('日期选择完成：', value);
            // 选择日期后自动更新数据
            var platform = $('select[name="platform"]').val();
            updateDailyStats(value, null, null, platform);
        }
    });

    // 初始化时间段选择器
    laydate.render({
        elem: '#dateRangeFilter',
        type: 'date',
        range: true, // 开启范围选择
        format: 'yyyy-MM-dd', // 指定显示格式
        done: function(value, date, endDate){ // 日期选择完成后的回调
            console.log('时间段选择完成：', value);
            if (value) {
                var dates = value.split(' - ');
                var startDate = dates[0];
                var endDate = dates[1];
                // 选择时间段后自动更新数据
                var platform = $('select[name="platform"]').val();
                updateDailyStats(null, startDate, endDate, platform);
            }
        }
    });

    // 获取页面数据
    var cardsData = [];
    var walletTransactionsData = [];
    var cardTransactionsData = [];
    
    try {
        cardsData = JSON.parse(document.getElementById('cards-data').textContent || '[]');
        walletTransactionsData = JSON.parse(document.getElementById('wallet-transactions-data').textContent || '[]');
        cardTransactionsData = JSON.parse(document.getElementById('card-transactions-data').textContent || '[]');
        console.log('数据加载完成，卡片数据：', cardsData.length, '条，钱包交易：', walletTransactionsData.length, '条，卡交易：', cardTransactionsData.length, '条');

        // 获取所有不重复的平台类型
        var platforms = Array.from(new Set(cardTransactionsData.map(function(trans) {
            return trans.version;
        }))).filter(Boolean); // 过滤掉null、undefined和空字符串

        // 按字母顺序排序平台
        platforms.sort();

        // 生成平台选项
        var platformSelect = $('select[name="platform"]');
        platformSelect.empty(); // 清空现有选项
        platformSelect.append('<option value="">全部平台</option>'); // 添加默认选项

        // 添加从数据中获取的平台选项
        platforms.forEach(function(platform) {
            platformSelect.append('<option value="' + platform + '">' + platform + '</option>');
        });

        // 重新渲染表单
        form.render('select');
        
        console.log('平台选项更新完成：', platforms);
    } catch (e) {
        console.error('数据解析错误:', e);
        layer.msg('数据加载失败，请刷新页面重试', {icon: 2});
    }

    // 初始化异常交易表格
    var errorTransTable = table.render({
        elem: '#errorTransTable',
        data: [],
        cols: [[
            {field: 'transaction_time', title: '交易时间', width: 180, sort: true, templet: function(d){
                return d.transaction_time ? new Date(d.transaction_time).toLocaleString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                }) : '';
            }},
            {field: 'mask_card_number', title: '卡号', width: 180},
            {field: 'accounting_amount', title: '交易本金(资金账户)', width: 180},
            {field: 'transaction_amount', title: '交易金额', width: 180},
            {field: 'biz_type', title: '交易类型', width: 120},
            {field: 'merchant_name', title: '商户名称', width: 200},
            {field: 'merchant_region', title: '商户所属', width: 120},
            {field: 'status', title: '状态', width: 100, templet: function(d){
                var statusMap = {
                    'FAILED': '<span class="status-failed">失败</span>',
                    'VOID': '<span class="status-void">作废</span>'
                };
                return statusMap[d.status] || d.status;
            }},
            {field: 'version', title: '平台', width: 100}
        ]],
        page: true,
        limit: 10,
        limits: [10, 20, 50, 100],
        text: {
            none: '暂无异常交易数据'
        },
        initSort: {
            field: 'transaction_time',
            type: 'desc'
        }
    });

    // 初始化今日钱包充值记录表格
    var rechargeTable = table.render({
        elem: '#rechargeTable',
        data: [],
        cols: [[
            {field: 'transaction_time', title: '充值时间', width: 180, sort: true, templet: function(d){
                return d.transaction_time ? new Date(d.transaction_time).toLocaleString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                }) : '';
            }},
            {field: 'transaction_id', title: '交易ID', width: 250},
            {field: 'amount_formatted', title: '充值金额', width: 150},
            {field: 'after_balance_formatted', title: '充值后余额', width: 150},
            {field: 'txn_type', title: '交易类型', width: 150},
            {field: 'remark', title: '备注', minWidth: 200},
            {field: 'version', title: '平台', width: 100}
        ]],
        page: true,
        limit: 10,
        limits: [10, 20, 50, 100],
        text: {
            none: '今日暂无充值记录'
        },
        initSort: {
            field: 'transaction_time',
            type: 'desc'
        }
    });

    // 全局变量控制显示模式
    var showAllRechargeRecords = false;

    // 加载钱包充值记录数据
    function loadRechargeData(showAll) {
        var rechargeList = [];
        
        if (showAll) {
            // 显示全部充值记录
            rechargeList = walletTransactionsData.filter(function(trans) {
                if (trans.txn_type === 'BALANCE_RECHARGE' || trans.txn_type === 'MANUAL') {
                    var amount = trans.amount || 0;
                    return parseFloat(amount) > 0;
                }
                return false;
            });
        } else {
            // 显示今日充值记录
            var today = new Date().toISOString().split('T')[0];
            rechargeList = walletTransactionsData.filter(function(trans) {
                if (trans.txn_type === 'BALANCE_RECHARGE' || trans.txn_type === 'MANUAL') {
                    var transTime = trans.transaction_time || '';
                    if (transTime.startsWith(today)) {
                        var amount = trans.amount || 0;
                        return parseFloat(amount) > 0;
                    }
                }
                return false;
            });
        }

        // 格式化数据
        var formattedData = rechargeList.map(function(trans) {
            return {
                transaction_time: trans.transaction_time,
                transaction_id: trans.transaction_id || '-',
                amount_formatted: (parseFloat(trans.amount || 0).toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })) + ' ' + (trans.amount_currency || 'USD'),
                after_balance_formatted: (parseFloat(trans.after_balance_amount || 0).toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })) + ' ' + (trans.after_balance_currency || 'USD'),
                txn_type: trans.txn_type || '-',
                remark: trans.remark || '-',
                version: trans.version || '-'
            };
        });

        // 按时间倒序排序
        formattedData.sort(function(a, b) {
            return new Date(b.transaction_time) - new Date(a.transaction_time);
        });

        // 更新表格提示文本
        var noneText = showAll ? '暂无充值记录' : '今日暂无充值记录';
        
        // 重新渲染表格
        table.reload('rechargeTable', {
            data: formattedData,
            text: {
                none: noneText
            }
        });
        
        console.log(`加载了 ${formattedData.length} 条${showAll ? '全部' : '今日'}充值记录`);
    }

    // 初始化今日充值记录数据（保持向后兼容）
    function loadTodayRechargeData() {
        loadRechargeData(false);
    }

    // 页面加载时初始化今日充值记录
    loadTodayRechargeData();

    // 将日期转换为YYYY-MM-DD格式，仅保留日期部分
    function formatDateToYYYYMMDD(dateStr) {
        if (!dateStr) return null;
        try {
            const date = new Date(dateStr);
            return date.toISOString().split('T')[0];
        } catch (e) {
            console.error('日期格式化错误：', e, dateStr);
            return null;
        }
    }

    // 处理数据并更新页面
    function updateDailyStats(date, startDate, endDate, platform) {
        console.log('开始更新数据:', date, startDate, endDate, platform); // 调试日志

        // 过滤卡片数据
        var filteredCards = cardsData.filter(function(card) {
            var matchDate = true;
            var matchPlatform = true;
            
            if (date) {
                var cardDate = formatDateToYYYYMMDD(card.create_time);
                matchDate = cardDate === date;
            } else if (startDate && endDate) {
                var cardDate = formatDateToYYYYMMDD(card.create_time);
                matchDate = cardDate >= startDate && cardDate <= endDate;
            }
            
            if (platform) {
                matchPlatform = card.version === platform;
            }
            
            return matchDate && matchPlatform;
        });

        // 过滤交易数据
        var filteredCardTrans = cardTransactionsData.filter(function(trans) {
            var matchDate = true;
            var matchPlatform = true;
            
            if (date) {
                var transDate = formatDateToYYYYMMDD(trans.transaction_time);
                matchDate = transDate === date;
            } else if (startDate && endDate) {
                var transDate = formatDateToYYYYMMDD(trans.transaction_time);
                matchDate = transDate >= startDate && transDate <= endDate;
            }
            
            if (platform) {
                matchPlatform = trans.version === platform;
            }
            
            return matchDate && matchPlatform;
        });

        // 计算每张卡的消费金额和次数
        var cardStats = {};
        var errorCardStats = {}; // 新增：统计每张卡的异常交易次数
        
        // 只对筛选后的交易数据进行统计
        filteredCardTrans.forEach(function(trans) {
            var cardNumber = trans.mask_card_number;
            if (!cardNumber) return; // 跳过没有卡号的交易
            
            // 统计正常交易
            if (trans.status !== 'FAILED' && trans.status !== 'VOID') {
                if (!cardStats[cardNumber]) {
                    cardStats[cardNumber] = {
                        count: 0,
                        totalAmount: 0,
                        currencies: {'USD': 0} // 默认至少有一种币种，避免空数组
                    };
                }
                
                cardStats[cardNumber].count++; // 增加消费次数计数
                
                // 统计消费金额
                if (trans.accounting_amount) {
                    try {
                        var amount = parseFloat(trans.accounting_amount);
                        var currency = trans.accounting_amount_currency || 'USD';
                        if (!isNaN(amount)) {
                            if (!cardStats[cardNumber].currencies[currency]) {
                                cardStats[cardNumber].currencies[currency] = 0;
                            }
                            cardStats[cardNumber].currencies[currency] += amount;
                            cardStats[cardNumber].totalAmount += amount;
                        }
                    } catch (e) {
                        console.warn("金额解析错误:", e, trans);
                    }
                }
            }
            
            // 统计异常交易
            if (trans.status === 'FAILED' || trans.status === 'VOID') {
                if (!errorCardStats[cardNumber]) {
                    errorCardStats[cardNumber] = {
                        count: 0
                    };
                }
                errorCardStats[cardNumber].count++;
            }
        });
        
        console.log(`根据筛选条件(日期:${date}, 平台:${platform})找到 ${Object.keys(cardStats).length} 张卡的消费数据`);
        console.log(`找到 ${Object.keys(errorCardStats).length} 张卡有异常交易`);
        
        // 转换为数组以便排序
        var cardStatsArray = [];
        for (var cardNumber in cardStats) {
            var stats = cardStats[cardNumber];
            var currenciesFormatted = [];
            
            // 格式化币种金额
            for (var currency in stats.currencies) {
                var amount = stats.currencies[currency];
                if (amount > 0 || currency === 'USD') { // 只保留有消费的币种或默认USD
                    currenciesFormatted.push({
                        currency: currency,
                        amount: amount,
                        formatted: amount.toLocaleString('en-US', {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2
                        }) + ' ' + currency
                    });
                }
            }
            
            cardStatsArray.push({
                cardNumber: cardNumber,
                count: stats.count,
                totalAmount: stats.totalAmount,
                currencies: currenciesFormatted
            });
        }
        
        // 按消费次数排序
        var countTop3 = cardStatsArray.sort(function(a, b) {
            return b.count - a.count;
        }).slice(0, 3);
        
        // 更新消费次数TOP3显示
        var countTop3Container = document.getElementById('countTop3');
        if (!countTop3Container) {
            console.error("未找到countTop3容器元素");
            return;
        }
        
        var countItems = countTop3Container.getElementsByClassName('top3-item');
        for (var i = 0; i < 3; i++) {
            var cardInfo = countTop3[i];
            var item = countItems[i];
            if (!item) {
                console.warn(`未找到第${i+1}个top3-item元素`);
                continue;
            }
            
            var cardNumberEl = item.querySelector('.card-number');
            var countEl = item.querySelector('.count');
            
            if (cardInfo) {
                cardNumberEl.textContent = cardInfo.cardNumber || '--';
                countEl.textContent = cardInfo.count + ' 笔';
                
                // 添加标题提示，显示明细
                var currenciesText = cardInfo.currencies.map(function(c) {
                    return c.formatted;
                }).join(', ');
                
                item.title = "卡号: " + cardInfo.cardNumber + 
                             "\n消费次数: " + cardInfo.count + " 笔" + 
                             "\n总消费: " + cardInfo.totalAmount.toLocaleString('en-US', {
                                 minimumFractionDigits: 2,
                                 maximumFractionDigits: 2
                             }) +
                             "\n币种明细: " + currenciesText;
                             
                // 设置点击事件
                item.setAttribute('data-card-number', cardInfo.cardNumber);
            } else {
                cardNumberEl.textContent = '--';
                countEl.textContent = '--';
                item.title = "";
                item.removeAttribute('data-card-number');
            }
        }
        
        // 按异常交易次数排序
        var errorCardStatsArray = [];
        for (var cardNumber in errorCardStats) {
            errorCardStatsArray.push({
                cardNumber: cardNumber,
                count: errorCardStats[cardNumber].count
            });
        }
        
        var errorTop3 = errorCardStatsArray.sort(function(a, b) {
            return b.count - a.count;
        }).slice(0, 3);
        
        // 更新异常交易TOP3显示
        var errorTop3Container = document.getElementById('errorTop3');
        if (!errorTop3Container) {
            console.error("未找到errorTop3容器元素");
            return;
        }
        
        var errorItems = errorTop3Container.getElementsByClassName('top3-item');
        for (var i = 0; i < 3; i++) {
            var cardInfo = errorTop3[i];
            var item = errorItems[i];
            if (!item) {
                console.warn(`未找到第${i+1}个error-top3-item元素`);
                continue;
            }
            
            var cardNumberEl = item.querySelector('.card-number');
            var countEl = item.querySelector('.count');
            
            if (cardInfo) {
                cardNumberEl.textContent = cardInfo.cardNumber || '--';
                countEl.textContent = cardInfo.count + ' 笔';
                
                // 添加标题提示
                item.title = "卡号: " + cardInfo.cardNumber + 
                             "\n异常交易次数: " + cardInfo.count + " 笔";
                             
                // 设置点击事件
                item.setAttribute('data-card-number', cardInfo.cardNumber);
            } else {
                cardNumberEl.textContent = '--';
                countEl.textContent = '--';
                item.title = "";
                item.removeAttribute('data-card-number');
            }
        }

        var filteredWalletTrans = walletTransactionsData.filter(function(trans) {
            if (date) {
                var transDate = formatDateToYYYYMMDD(trans.transaction_time);
                if (transDate !== date) return false;
            }
            if (platform && trans.version !== platform) return false;
            return true;
        });

        console.log('筛选后卡片数据：', filteredCards.length, '条，卡交易：', filteredCardTrans.length, '条，钱包交易：', filteredWalletTrans.length, '条');

        // 计算统计数据
        var cardCount = filteredCards.length;
        
        // 计算消费总额（按币种分组）
        var totalAmountByCurrency = {};
        filteredCardTrans.forEach(function(trans) {
            if (trans.accounting_amount) {
                var currency = trans.accounting_amount_currency || 'USD';
                var amount = parseFloat(trans.accounting_amount);
                if (!isNaN(amount)) {
                    totalAmountByCurrency[currency] = (totalAmountByCurrency[currency] || 0) + amount;
                }
            }
        });

        // 计算钱包和卡交易笔数
        var walletTransCount = filteredWalletTrans.length;
        var cardTransCount = filteredCardTrans.length;

        // 计算异常交易
        var errorTrans = filteredCardTrans.filter(function(trans) {
            return trans.status === 'FAILED' || trans.status === 'VOID';
        });
        var errorCount = errorTrans.length;

        // 更新统计卡片
        $('#cardCount').text(cardCount || '0');
        
        // 格式化并显示消费总额
        var totalAmountText = Object.entries(totalAmountByCurrency)
            .map(function([currency, amount]) {
                return amount.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }) + ' ' + currency;
            })
            .join(', ') || '0.00';
        $('#totalAmount').text(totalAmountText);

        $('#walletTransCount').text(walletTransCount || '0');
        $('#cardTransCount').text(cardTransCount || '0');
        $('#errorCount').text(errorCount || '0');

        // 更新异常交易表格
        var tableData = errorTrans.map(function(trans) {
            return {
                transaction_time: trans.transaction_time,
                mask_card_number: trans.mask_card_number,
                accounting_amount: (parseFloat(trans.accounting_amount || 0).toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })) + ' ' + (trans.accounting_amount_currency || 'USD'),
                transaction_amount: (parseFloat(trans.transaction_amount || 0).toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })) + ' ' + (trans.transaction_amount_currency || 'USD'),
                biz_type: trans.biz_type || '-',
                merchant_name: trans.merchant_name || '-',
                merchant_region: trans.merchant_region || '-',
                status: trans.status,
                version: trans.version || '-'
            };
        });

        // 根据交易时间进行倒序排序
        tableData.sort(function(a, b) {
            return new Date(b.transaction_time) - new Date(a.transaction_time);
        });

        table.reload('errorTransTable', {
            data: tableData,
            initSort: {
                field: 'transaction_time',
                type: 'desc'
            }
        });

        // 如果选择了具体日期，才计算环比
        if (date) {
            // 计算环比数据（与前一天比较）
            var targetDate = new Date(date);
            var previousDate = new Date(targetDate);
            previousDate.setDate(previousDate.getDate() - 1);
            var previousDateStr = formatDateToYYYYMMDD(previousDate);

            // 获取前一天的数据并按币种计算总额
            var previousTotalAmountByCurrency = {};
            var previousCardTrans = cardTransactionsData.filter(function(trans) {
                var transDate = formatDateToYYYYMMDD(trans.transaction_time);
                if (transDate === previousDateStr) {
                    if (platform && trans.version !== platform) return false;
                    
                    if (trans.accounting_amount) {
                        var currency = trans.accounting_amount_currency || 'USD';
                        var amount = parseFloat(trans.accounting_amount);
                        if (!isNaN(amount)) {
                            previousTotalAmountByCurrency[currency] = (previousTotalAmountByCurrency[currency] || 0) + amount;
                        }
                    }
                    return true;
                }
                return false;
            });

            // 计算每个币种的环比变化
            var amountTrends = [];
            Object.keys(totalAmountByCurrency).forEach(function(currency) {
                var currentAmount = totalAmountByCurrency[currency] || 0;
                var previousAmount = previousTotalAmountByCurrency[currency] || 0;
                var trend = previousAmount === 0 ? 
                    (currentAmount > 0 ? 100 : 0) : 
                    ((currentAmount - previousAmount) / previousAmount * 100);
                
                if (trend > 0) {
                    amountTrends.push('+' + trend.toFixed(1) + '%');
                } else if (trend < 0) {
                    amountTrends.push(trend.toFixed(1) + '%');
                } else {
                    amountTrends.push('0%');
                }
            });

            // 更新金额环比趋势
            var trendText = amountTrends.join(', ') || '--';
            var overallTrend = amountTrends.length > 0 ? 
                parseFloat(amountTrends[0].replace(/[+%]/g, '')) : 0;
            
            $('#amountTrend').text(trendText);
            if (overallTrend > 0) {
                $('#amountTrend').addClass('up').removeClass('down');
                $('#amountTrend').next('.layui-icon').addClass('layui-icon-up').removeClass('layui-icon-down');
            } else if (overallTrend < 0) {
                $('#amountTrend').addClass('down').removeClass('up');
                $('#amountTrend').next('.layui-icon').addClass('layui-icon-down').removeClass('layui-icon-up');
            } else {
                $('#amountTrend').removeClass('up down');
                $('#amountTrend').next('.layui-icon').removeClass('layui-icon-up layui-icon-down');
            }

            // 获取前一天的卡片和钱包交易数据
            var previousCards = cardsData.filter(function(card) {
                var cardDate = formatDateToYYYYMMDD(card.create_time);
                if (cardDate !== previousDateStr) return false;
                if (platform && card.version !== platform) return false;
                return true;
            });

            var previousWalletTrans = walletTransactionsData.filter(function(trans) {
                var transDate = formatDateToYYYYMMDD(trans.transaction_time);
                if (transDate !== previousDateStr) return false;
                if (platform && trans.version !== platform) return false;
                return true;
            });

            updateTrend('cardTrend', cardCount, previousCards.length);
            updateTrend('walletTransTrend', walletTransCount, previousWalletTrans.length);
            updateTrend('cardTransTrend', cardTransCount, previousCardTrans.length);
        } else {
            // 不显示环比数据
            ['cardTrend', 'amountTrend', 'walletTransTrend', 'cardTransTrend'].forEach(function(id) {
                $('#' + id).text('--');
                $('#' + id).next('.layui-icon').removeClass('layui-icon-up layui-icon-down');
            });
        }
        
        console.log('数据更新完成'); // 调试日志
    }

    // 更新趋势显示
    function updateTrend(elementId, current, previous) {
        var trend = previous === 0 ? (current > 0 ? 100 : 0) : ((current - previous) / previous * 100);
        var $trend = $('#' + elementId);
        var $icon = $trend.next('.layui-icon');
        
        if (trend > 0) {
            $trend.text('+' + trend.toFixed(1) + '%');
            $trend.addClass('up').removeClass('down');
            $icon.addClass('layui-icon-up').removeClass('layui-icon-down');
        } else if (trend < 0) {
            $trend.text(trend.toFixed(1) + '%');
            $trend.addClass('down').removeClass('up');
            $icon.addClass('layui-icon-down').removeClass('layui-icon-up');
        } else {
            $trend.text('0%');
            $trend.removeClass('up down');
            $icon.removeClass('layui-icon-up layui-icon-down');
        }
    }

    // 监听筛选表单提交按钮点击
    $('.layui-btn[lay-filter="filterSubmit"]').on('click', function(){
        var date = $('#dateFilter').val();
        var dateRange = $('#dateRangeFilter').val();
        var platform = $('select[name="platform"]').val();
        
        if (dateRange) {
            var dates = dateRange.split(' - ');
            var startDate = dates[0];
            var endDate = dates[1];
            updateDailyStats(null, startDate, endDate, platform);
        } else {
            updateDailyStats(date, null, null, platform);
        }
    });

    // 监听平台选择变化
    form.on('select(platformSelect)', function(data){
        var date = $('#dateFilter').val();
        console.log('平台选择变化：', date, data.value);
        updateDailyStats(date, null, null, data.value);
    });

    // 监听重置按钮
    $('button[type="reset"]').click(function(){
        console.log('点击重置按钮');
        setTimeout(function(){
            $('#dateFilter').val('');
            $('#dateRangeFilter').val('');
            form.val('dailyFilterForm', {
                platform: ''
            });
            updateDailyStats('', null, null, '');
        }, 0);
    });

    // 切换充值记录显示模式
    function toggleRechargeRecords() {
        showAllRechargeRecords = !showAllRechargeRecords;
        
        // 更新标题文本和图标状态
        var titleText = showAllRechargeRecords ? '全部钱包充值记录' : '今日钱包充值记录';
        var tooltipText = showAllRechargeRecords ? '点击切换显示今日记录' : '点击切换显示全部记录';
        
        $('#rechargeTitleText').text(titleText);
        $('#toggleIcon').attr('title', tooltipText);
        
        // 更新样式状态
        if (showAllRechargeRecords) {
            $('#rechargeTitle').addClass('active');
        } else {
            $('#rechargeTitle').removeClass('active');
        }
        
        // 重新加载数据
        loadRechargeData(showAllRechargeRecords);
        
        console.log('切换到显示：' + titleText);
    }

    // 初始化页面加载完成后设置点击事件
    $(document).ready(function() {
        // 为充值记录标题添加点击事件
        $('#rechargeTitle').on('click', function() {
            toggleRechargeRecords();
        });
        
        // 为TOP3项目添加点击事件处理
        $('#countTop3').on('click', '.top3-item', function() {
            var cardNumber = $(this).attr('data-card-number');
            if (cardNumber && cardNumber !== '--') {
                // 使用当前筛选条件
                var date = $('#dateFilter').val();
                var platform = $('select[name="platform"]').val();
                
                // 弹出详细信息层
                showCardTransactionDetails(cardNumber, date, platform);
            }
        });
        
        // 为异常交易TOP3项目添加点击事件处理
        $('#errorTop3').on('click', '.top3-item', function() {
            var cardNumber = $(this).attr('data-card-number');
            if (cardNumber && cardNumber !== '--') {
                // 使用当前筛选条件
                var date = $('#dateFilter').val();
                var platform = $('select[name="platform"]').val();
                
                // 弹出详细信息层
                showCardErrorTransactionDetails(cardNumber, date, platform);
            }
        });
    });
    
    // 显示卡片交易详情 - 确保使用当前筛选条件
    function showCardTransactionDetails(cardNumber, date, platform) {
        // 获取原始交易数据
        var allCardTrans = cardTransactionsData;
        
        // 根据筛选条件过滤交易数据，并排除交易失败的记录
        var filteredTrans = allCardTrans.filter(function(trans) {
            // 排除交易失败的记录
            if (trans.status === 'FAILED' || trans.status === 'VOID') {
                return false;
            }
            
            var matchCard = trans.mask_card_number === cardNumber;
            var matchDate = true;
            var matchPlatform = true;
            
            if (date) {
                var transDate = formatDateToYYYYMMDD(trans.transaction_time);
                matchDate = transDate === date;
            }
            
            if (platform) {
                matchPlatform = trans.version === platform;
            }
            
            return matchCard && matchDate && matchPlatform;
        });
        
        console.log(`找到卡号 ${cardNumber} 的 ${filteredTrans.length} 条成功交易记录`);
        
        // 计算总额
        var totalByCurrency = {}; // 交易本金(资金账户)汇总
        var transactionTotalByCurrency = {}; // 交易金额汇总
        filteredTrans.forEach(function(trans) {
            // 统计交易本金(资金账户)
            if (trans.accounting_amount) {
                var amount = parseFloat(trans.accounting_amount);
                var currency = trans.accounting_amount_currency || 'USD';
                if (!isNaN(amount)) {
                    totalByCurrency[currency] = (totalByCurrency[currency] || 0) + amount;
                }
            }
            
            // 统计交易金额
            if (trans.transaction_amount) {
                var transAmount = parseFloat(trans.transaction_amount);
                var transCurrency = trans.transaction_amount_currency || 'USD';
                if (!isNaN(transAmount)) {
                    transactionTotalByCurrency[transCurrency] = (transactionTotalByCurrency[transCurrency] || 0) + transAmount;
                }
            }
        });
        
        // 格式化交易本金(资金账户)总额显示
        var totalAmountText = Object.entries(totalByCurrency)
            .map(function([currency, amount]) {
                return amount.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }) + ' ' + currency;
            })
            .join(', ');
            
        // 格式化交易金额总额显示
        var transactionTotalText = Object.entries(transactionTotalByCurrency)
            .map(function([currency, amount]) {
                return amount.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }) + ' ' + currency;
            })
            .join(', ');
        
        // 构建HTML内容
        var content = '<div class="card-detail-popup">';
        content += '<div class="card-info">';
        content += '<div class="card-number">卡号: ' + cardNumber + '</div>';
        content += '<div class="card-stats">消费笔数: ' + filteredTrans.length + ' 笔</div>';
        content += '<div class="card-stats">交易本金(资金账户): ' + (totalAmountText || '0.00') + '</div>';
        content += '<div class="card-stats">交易金额: ' + (transactionTotalText || '0.00') + '</div>';
        content += '</div>';
        
        if (filteredTrans.length > 0) {
            content += '<div class="transaction-list">';
            content += '<table class="layui-table">';
            content += '<thead><tr>';
            content += '<th>交易时间</th>';
            content += '<th>交易本金(资金账户)</th>';
            content += '<th>交易金额</th>';
            content += '<th>交易类型</th>';
            content += '<th>商户名称</th>';
            content += '<th>商户所属</th>';
            content += '<th>平台</th>';
            content += '<th>状态</th>';
            content += '</tr></thead>';
            content += '<tbody>';
            
            filteredTrans.forEach(function(trans) {
                var transTime = trans.transaction_time ? new Date(trans.transaction_time).toLocaleString('zh-CN') : '-';
                
                // 交易本金(资金账户)
                var accountingAmount = trans.accounting_amount ? parseFloat(trans.accounting_amount).toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }) + ' ' + (trans.accounting_amount_currency || 'USD') : '-';
                
                // 交易金额
                var transactionAmount = trans.transaction_amount ? parseFloat(trans.transaction_amount).toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }) + ' ' + (trans.transaction_amount_currency || 'USD') : '-';
                
                var bizType = trans.biz_type || '-';
                var merchantName = trans.merchant_name || '-';
                var merchantRegion = trans.merchant_region || '-';
                var version = trans.version || '-';
                var status = trans.status || '-';
                var statusClass = '';
                
                if (status === 'FAILED') {
                    statusClass = 'status-failed';
                    status = '<span class="status-failed">失败</span>';
                } else if (status === 'VOID') {
                    statusClass = 'status-void';
                    status = '<span class="status-void">作废</span>';
                }
                
                content += '<tr>';
                content += '<td>' + transTime + '</td>';
                content += '<td>' + accountingAmount + '</td>';
                content += '<td>' + transactionAmount + '</td>';
                content += '<td>' + bizType + '</td>';
                content += '<td>' + merchantName + '</td>';
                content += '<td>' + merchantRegion + '</td>';
                content += '<td>' + version + '</td>';
                content += '<td>' + status + '</td>';
                content += '</tr>';
            });
            
            content += '</tbody></table>';
            content += '</div>';
        } else {
            content += '<div class="no-data">暂无交易数据</div>';
        }
        
        content += '</div>';
        
        // 使用layui的弹出层
        layer.open({
            type: 1,
            title: '卡片交易详情',
            area: ['90%', '80%'],
            shadeClose: true,
            content: content,
            success: function(layero, index) {
                // 弹出层显示成功后的回调
                $(layero).find('.layui-layer-content').css('overflow', 'auto');
            }
        });
    }

    // 显示卡片异常交易详情
    function showCardErrorTransactionDetails(cardNumber, date, platform) {
        // 获取原始交易数据
        var allCardTrans = cardTransactionsData;
        
        // 根据筛选条件过滤交易数据，只显示异常交易
        var filteredTrans = allCardTrans.filter(function(trans) {
            // 只显示异常交易
            if (trans.status !== 'FAILED' && trans.status !== 'VOID') {
                return false;
            }
            
            var matchCard = trans.mask_card_number === cardNumber;
            var matchDate = true;
            var matchPlatform = true;
            
            if (date) {
                var transDate = formatDateToYYYYMMDD(trans.transaction_time);
                matchDate = transDate === date;
            }
            
            if (platform) {
                matchPlatform = trans.version === platform;
            }
            
            return matchCard && matchDate && matchPlatform;
        });
        
        console.log(`找到卡号 ${cardNumber} 的 ${filteredTrans.length} 条异常交易记录`);
        
        // 构建HTML内容
        var content = '<div class="card-detail-popup">';
        content += '<div class="card-info warning">';
        content += '<div class="card-number">卡号: ' + cardNumber + '</div>';
        content += '<div class="card-stats">异常交易笔数: ' + filteredTrans.length + ' 笔</div>';
        content += '</div>';
        
        if (filteredTrans.length > 0) {
            content += '<div class="transaction-list">';
            content += '<table class="layui-table">';
            content += '<thead><tr>';
            content += '<th>交易时间</th>';
            content += '<th>交易金额</th>';
            content += '<th>交易类型</th>';
            content += '<th>商户名称</th>';
            content += '<th>商户所属</th>';
            content += '<th>平台</th>';
            content += '<th>状态</th>';
            content += '</tr></thead>';
            content += '<tbody>';
            
            filteredTrans.forEach(function(trans) {
                var transTime = trans.transaction_time ? new Date(trans.transaction_time).toLocaleString('zh-CN') : '-';
                var amount = trans.transaction_amount ? parseFloat(trans.transaction_amount).toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }) + ' ' + (trans.transaction_amount_currency || 'USD') : '-';
                var bizType = trans.biz_type || '-';
                var merchantName = trans.merchant_name || '-';
                var merchantRegion = trans.merchant_region || '-';
                var version = trans.version || '-';
                var status = trans.status || '-';
                var statusClass = '';
                
                if (status === 'FAILED') {
                    statusClass = 'status-failed';
                    status = '<span class="status-failed">失败</span>';
                } else if (status === 'VOID') {
                    statusClass = 'status-void';
                    status = '<span class="status-void">作废</span>';
                }
                
                content += '<tr>';
                content += '<td>' + transTime + '</td>';
                content += '<td>' + amount + '</td>';
                content += '<td>' + bizType + '</td>';
                content += '<td>' + merchantName + '</td>';
                content += '<td>' + merchantRegion + '</td>';
                content += '<td>' + version + '</td>';
                content += '<td>' + status + '</td>';
                content += '</tr>';
            });
            
            content += '</tbody></table>';
            content += '</div>';
        } else {
            content += '<div class="no-data">暂无异常交易数据</div>';
        }
        
        content += '</div>';
        
        // 使用layui的弹出层
        layer.open({
            type: 1,
            title: '卡片异常交易详情',
            area: ['90%', '80%'],
            shadeClose: true,
            content: content,
            success: function(layero, index) {
                // 弹出层显示成功后的回调
                $(layero).find('.layui-layer-content').css('overflow', 'auto');
            }
        });
    }

    // 页面加载时初始化数据
    updateDailyStats('', null, null, '');
});
