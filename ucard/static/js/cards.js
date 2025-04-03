/**
 * 所有卡管理页面专用脚本
 * 用于处理所有卡表格的渲染，搜索，分页功能
 */

layui.use(['table', 'form', 'laydate', 'layer', 'dropdown'], function () {
    var table = layui.table; //表格
    var form = layui.form;  //表单
    var laydate = layui.laydate;  //日期
    var layer = layui.layer;  //弹出层
    var $ = layui.jquery; // jQuery

    try{
        //获取后端数据
        var cardsdataElement = document.getElementById('cards-data');
        var cardholderdataElement = document.getElementById('card-holders-data');
        var wallet_balance_dataElement = document.getElementById('wallet_balance-data');
        if (!cardsdataElement && !cardholderdataElement && !wallet_balance_dataElement) {
            console.error("找不到数据元素 #cardsdata 或 #card-holders-data 或 #wallet_balance-data");
            layer.msg('数据加载失败：找不到数据元素', {icon: 2});
            return;
        }
        var cardsText = cardsdataElement.textContent;
        var cardholdersText = cardholderdataElement.textContent;
        if (!cardsText || cardsText.trim() === '' || !cardholdersText || cardholdersText.trim() === '') {
            console.error("数据元素内容为空");
            layer.msg('数据加载失败：数据为空', {icon: 2});
            return;
        }
        var cardsData = JSON.parse(cardsText);
        var cardholdersData = JSON.parse(cardholdersText);
        var wallet_balance_data = JSON.parse(wallet_balance_dataElement.textContent);

        console.log("卡数据:", cardsData);
        console.log("用卡人数据:", cardholdersData);
        console.log("钱包余额数据:", wallet_balance_data);

        if (!cardsData && !cardholdersData && !wallet_balance_data) {
            console.warn("数据为null或undefined,初始化为空数组");
            cardsData = [];
            cardholdersData = [];
            wallet_balance_data = [];
        }
        
        // 初始化表单组件
        function initForm() {
            // 初始化用卡人下拉菜单
            var cardHolderSelect = document.getElementById('card_holder_select');
            if (cardHolderSelect && cardholdersData && cardholdersData.length > 0) {
                // 清空现有选项（保留全部选项）
                while (cardHolderSelect.options.length > 1) {
                    cardHolderSelect.remove(1);
                }
                
                // 添加用卡人选项
                cardholdersData.forEach(function(holder) {
                    var option = document.createElement('option');
                    option.value = holder.card_holder_id;
                    option.text = holder.first_name + holder.last_name;
                    cardHolderSelect.appendChild(option);
                });
            }
            
            // 重新渲染表单元素
            form.render();
            
            // 监听搜索表单提交
            form.on('submit(formSearch)', function(data) {
                // 获取表单数据
                var formData = data.field; 
                console.log("表单搜索条件:", formData);
                
                // 执行搜索，使用本地数据筛选
                var filteredData = cardsData;
                
                // 按卡号后四位筛选
                if (formData.card_last_digits && formData.card_last_digits.trim() !== '') {
                    filteredData = filteredData.filter(function(item) {
                        var cardNumber = item.mask_card_number || '';
                        // 获取卡号后四位并进行精确匹配
                        var lastFourDigits = cardNumber.slice(-4);
                        return lastFourDigits === formData.card_last_digits;
                    });
                }
                
                // 按平台(version)筛选
                if (formData.version && formData.version !== '') {
                    filteredData = filteredData.filter(function(item) {
                        return item.version === formData.version;
                    });
                }
                
                // 按用卡人筛选
                if (formData.card_holder_id && formData.card_holder_id !== '') {
                    filteredData = filteredData.filter(function(item) {
                        return item.card_holder_id === formData.card_holder_id;
                    });
                }
                
                // 重载表格，使用筛选后的数据
                table.reload('cards-table', {
                    data: filteredData,
                    page: {
                        curr: 1  // 重置到第一页
                    }
                });
                
                // 如果没有找到匹配的数据，显示提示
                if (filteredData.length === 0) {
                    layer.msg('未找到符合条件的数据', {icon: 0});
                } else {
                    layer.msg('找到 ' + filteredData.length + ' 条符合条件的数据', {icon: 1});
                }
                
                return false;  // 阻止表单默认提交
            });
        }

        function formatTime(timeStr) {
            if (!timeStr) return '--';
            
            // 处理ISO格式时间
            try {
                var date = new Date(timeStr);
                
                // 检查日期是否有效
                if (isNaN(date.getTime())) return timeStr;
                
                var year = date.getFullYear();
                var month = String(date.getMonth() + 1).padStart(2, '0');
                var day = String(date.getDate()).padStart(2, '0');
                var hours = String(date.getHours()).padStart(2, '0');
                var minutes = String(date.getMinutes()).padStart(2, '0');
                var seconds = String(date.getSeconds()).padStart(2, '0');
                return `<div class="date-part">${year}-${month}-${day}</div><div class="time-part">${hours}:${minutes}:${seconds}</div>`;
            } catch (e) {
                console.error("时间格式化错误:", e);
                return timeStr; // 发生错误时返回原始时间字符串
            }
        }

        // 计算剩余有效期（月份）
        function calculateRemainingMonths(expire_year, expire_month) {
            if (!expire_year || !expire_month) return 0;
            const now = new Date();
            const currentYear = now.getFullYear();
            const currentMonth = now.getMonth() + 1; // JavaScript月份从0开始
            return (expire_year - currentYear) * 12 + (expire_month - currentMonth);
        }

        // 初始化表格
        function initCardsTable() {
            // 渲染卡表格
            table.render({
                elem: '#cards-table',
                toolbar: '#toolbar_card_list',
                defaultToolbar: ['filter', 'exports'],
                data: cardsData,
                page: true,
                url: null,
                limit: 5,
                limits: [5, 10, 20],
                height: 'auto',
                cols:[[
                    {
                        field: 'mask_card_number', 
                        title: '卡号', 
                        width: 210,
                        align: 'center',
                        templet: function(d) {
                            var currency = d.card_currency || 'USD';
                            var cardNumber = d.mask_card_number || '5258********9110';
                            var cardName = d.card_name || '--';
                            // 生成卡片模板，模仿图片样式
                            return '<div class="list-card">' +
                                   '<span class="card-number">' + cardNumber + '</span>' +
                                   '<div class="card-currency">' + currency + '</div>' +
                                   '</div>';
                        }
                    },
                    {
                        field: 'limits', 
                        title: '可用余额', 
                        width: 140,
                        align: 'center',
                        templet: function(d) {
                            var singleLimit = d.limit_per_transaction || '0.00';
                            var dayLimit = d.limit_per_day || '0.00';
                            var monthLimit = d.limit_per_month || '0.00';
                            return '<div class="limit-info">' +
                                '<div>单笔限额: ' + singleLimit + '</div>' +
                                '<div>日限额: ' + dayLimit + '</div>' +
                                '<div>月限额: ' + monthLimit + '</div>' +
                                '</div>';
                        }
                    },
                    {
                        field: 'name',
                        title: '姓名',
                        width: 140,
                        align: 'center',
                        templet: function(d){
                            return d.first_name + ' ' + d.last_name;
                        }
                    },
                    {
                        field: 'available_balance', 
                        title: '剩余额度', 
                        width: 150,
                        align: 'center',
                        templet: function(d){
                            var balance = d.available_balance || '0.00';
                            var currency = d.card_currency || 'USD';
                            return balance + ' ' + currency;
                        }
                    },
                    {
                        field: 'expire_date', 
                        title: '有效期', 
                        width: 80,
                        align: 'center',
                        templet: function(d) {
                            var months = calculateRemainingMonths(d.expire_year, d.expire_month);
                            return months + '个月';
                        }
                    },
                    {
                        field: 'cards_status', 
                        title: '状态', 
                        width: 80,
                        align: 'center',
                        templet: function(d){
                            var status = d.cards_status || 'INACTIVE';
                            if (status === 'ACTIVE') {
                                return '<span class="layui-badge layui-bg-green">激活</span>';
                            } else if (status === 'FROZEN') {
                                return '<span class="layui-badge layui-bg-orange">冻结</span>';
                            } else if (status === 'CANCELLED'){
                                return '<span class="layui-badge layui-bg-red">销卡</span>';
                            } else if (status === 'EXPIRED'){
                                return '<span class="layui-badge layui-bg-black">过期</span>';
                            } else if (status === 'INACTIVE'){
                                return '<span class="layui-badge layui-bg-cyan">待激活</span>';
                            } else if (status === 'FREEZING'){
                                return '<span class="layui-badge layui-bg-cyan">冻结中</span>';
                            } else if (status === 'UNFREEZING'){
                                return '<span class="layui-badge layui-bg-cyan">解冻中</span>';
                            } else if (status === 'CANCELLING') {
                                return '<span class="layui-badge layui-bg-cyan">销卡中</span>';
                            } else {
                                return '<span class="layui-badge layui-bg-cyan">未知</span>';
                            }
                        }
                    },
                    {
                        field: 'create_time', 
                        title: '申请时间', 
                        width: 120, 
                        align: 'center',
                        templet: function(d){
                            return formatTime(d.create_time);
                        },
                    },
                    {field: 'brand_code', title: '卡组织', width: 100, align: 'center'},
                    {field: 'version', title: '平台', width: 80, align: 'center'},
                    {title: '操作', toolbar: '#card_barTool', width: 150, align: 'center'},
                ]],
                done: function(res){
                    // 确保分页正确显示
                    this.count = cardsData.length;
                    console.log("表格渲染完成，数据条数：", this.count);
                    
                    // 如果没有数据，显示提示
                    if(cardsData.length === 0) {
                        layer.msg('暂无卡数据', {icon: 0});
                    }
                }
            });
        }

        function showBalanceDetail(balanceData) {
            var rows = [];
            for (var version in balanceData) {
                if (balanceData.hasOwnProperty(version)) {
                    // 版本标题
                    rows.push('<tr><td colspan="3" style="font-weight: bold;background-color:#f2f2f2">版本 ' + version + '</td></tr>');
                    
                    // 表头
                    rows.push(
                        '<tr>' + 
                            '<th style="width:22%;background-color:#f8f8f8">币种</th>' +
                            '<th style="width:39%;background-color:#f8f8f8">总金额</th>' +
                            '<th style="width:39%;background-color:#f8f8f8">可用余额</th>' +
                        '</tr>'
                    );

                    // 数据行
                    var currencies = balanceData[version];
                    for (var currency in currencies) {
                        var info = currencies[currency];
                        rows.push(
                            '<tr>' +
                                '<td>' + currency + '</td>' +
                                '<td>' + (info.amount || '--') + '</td>' +
                                '<td>' + (info.available || '--') + '</td>' +
                            '</tr>'
                        );
                    }
                }
            }

            var content = '<div class="layui-card">' +
                '<div class="layui-card-header" style="font-weight: 900">账户余额详情</div>' +
                '<div class="layui-card-body">' +
                '<table class="layui-table">' +
                '<tbody>' + rows.join('') + '</tbody>' +
                '</table></div></div>';

            layer.open({
                type: 1,
                title: '账户余额详情',
                area: ['700px', '600px'], // 加宽以适应三列
                content: content
            });
        }

        // 显示卡片详情弹窗
        function showCardDetail(data) {
            // 获取卡片状态中文映射
            var statusMap = {
                'ACTIVE': '激活',
                'FROZEN': '冻结',
                'CANCELLED': '销卡',
                'EXPIRED': '过期',
                'INACTIVE': '待激活',
                'FREEZING': '冻结中',
                'UNFREEZING': '解冻中',
                'CANCELLING': '销卡中'
            };

            // 计算剩余有效期
            var remainingMonths = calculateRemainingMonths(data.expire_year, data.expire_month);

            layer.open({
                type: 1,
                title: '卡片详情',
                area: ['600px', '550px'],
                content: `
                    <div class="layui-card">
                        <div class="layui-card-body">
                            <table class="layui-table">
                                <colgroup>
                                    <col width="30%">
                                    <col width="70%">
                                </colgroup>
                                <tbody>
                                    <tr><td>卡号</td><td>${data.mask_card_number || '--'}</td></tr>
                                    <tr><td>卡ID</td><td>${data.card_id || '--'}</td></tr>
                                    <tr><td>姓名</td><td>${data.first_name || ''} ${data.last_name || ''}</td></tr>
                                    <tr><td>卡昵称</td><td>${data.card_name || '--'}</td></tr>
                                    <tr><td>卡组织</td><td>${data.brand_code || '--'}</td></tr>
                                    <tr><td>平台</td><td>${data.version || '--'}</td></tr>
                                    <tr><td>币种</td><td>${data.card_currency || 'USD'}</td></tr>
                                    <tr><td>可用余额</td><td>${data.available_balance || '0.00'} ${data.card_currency || 'USD'}</td></tr>
                                    <tr><td>单笔限额</td><td>${data.limit_per_transaction || '0.00'} ${data.card_currency || 'USD'}</td></tr>
                                    <tr><td>日限额</td><td>${data.limit_per_day || '0.00'} ${data.card_currency || 'USD'}</td></tr>
                                    <tr><td>月限额</td><td>${data.limit_per_month || '0.00'} ${data.card_currency || 'USD'}</td></tr>
                                    <tr><td>有效期</td><td>${data.expire_month || '--'}月/${data.expire_year || '--'}年 (剩余${remainingMonths}个月)</td></tr>
                                    <tr><td>卡片状态</td><td>${statusMap[data.cards_status] || data.cards_status || '--'}</td></tr>
                                    <tr><td>申请时间</td><td>${formatTime(data.create_time)}</td></tr>
                                    <tr><td>激活时间</td><td>${formatTime(data.active_time)}</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>`
            });
        }

        // 初始化事件监听
        function initEventListeners() {
            // 监听表格工具栏事件
            table.on('toolbar(cards-table)', function(obj){
                if (obj.event === 'add_card') {
                    layer.open({
                        type: 2,
                        title: '开卡',
                        area: ['800px', '600px'],
                        content: '/cards/cards_apply',
                        end: function(){
                            table.reload('cards-table', {
                                page: {
                                    curr: 1 // 重新从第一页开始
                                }
                            });
                        }
                    });
                }else if (obj.event === 'wallet_balance') {
                    showBalanceDetail(wallet_balance_data);
                }
            });
            
            // 监听表格行工具条事件
            table.on('tool(cards-table)', function(obj){
                var data = obj.data; // 获得当前行数据
                var layEvent = obj.event; // 获得 lay-event 对应的值
                
                switch(layEvent) {
                    case 'detail':
                        showCardDetail(data);
                        break;
                    case 'modify':
                        // 打开调额弹窗 - 使用iframe加载独立的HTML页面
                        layer.open({
                            type: 2,  // iframe类型
                            title: '调整卡额度',
                            area: ['500px', '500px'],
                            content: '/cards/modify_card_balance',  // 加载后端路由
                            success: function(layero, index) {
                                // 获取iframe中的window对象
                                var iframeWin = window[layero.find('iframe')[0]['name']];
                                
                                // 传递数据到iframe
                                iframeWin.initCardData({
                                    card_id: data.card_id,
                                    mask_card_number: data.mask_card_number,
                                    first_name: data.first_name,
                                    last_name: data.last_name,
                                    version: data.version,
                                    available_balance: data.available_balance,
                                    card_currency: data.card_currency || 'USD',
                                    wallet_balance_data: wallet_balance_data
                                });
                            },
                            end: function() {
                                // 弹窗关闭后刷新表格
                                table.reload('cards-table');
                            }
                        });
                        break;
                    case 'set_limit':
                        layer.msg('设置限额功能待实现', {icon: 0});
                        break;
                    case 'edit_nickname':
                        layer.prompt({
                            formType: 0,
                            title: '编辑卡昵称',
                                alue: data.card_name || ''
                        }, function(value, index){
                            layer.msg('昵称修改功能待实现', {icon: 0});
                            layer.close(index);
                        });
                        break;
                    case 'cancel':
                        layer.confirm('确定要销卡吗？确定后销卡操作无法撤回', function(index){
                            layer.close(index); // 先关闭确认弹窗
                            
                            // 获取卡号后四位
                            var cardLastFour = '';
                            if(data && data.mask_card_number) {
                                // 确保mask_card_number是字符串类型
                                var cardNumberStr = String(data.mask_card_number);
                                cardLastFour = cardNumberStr.slice(-4);
                                console.log("卡号后四位:", cardLastFour);
                            }
                            console.log("卡号后四位:", cardLastFour);
                            // 创建自定义表单弹窗
                            layer.open({
                                type: 1,
                                title: '安全验证',
                                area: ['400px', '250px'],
                                content: '<div style="padding: 20px;">' +
                                    '<div style="margin-bottom: 15px; color: #FF5722; font-weight: bold;">请输入 DEL+卡号后四位 以确认销卡操作</div>' +
                                    '<div class="layui-form">' +
                                    '<div class="layui-form-item">' +
                                    '<label class="layui-form-label">验证码：</label>' +
                                    '<div class="layui-input-block">' +
                                    '<input type="text" id="cancel-verify-input" placeholder="请输入DEL+卡号后四位" class="layui-input" autocomplete="off">' +
                                    '</div>' +
                                    '</div>' +
                                    '<div class="layui-form-item" style="margin-top: 30px; text-align: center;">' +
                                    '<button type="button" class="layui-btn layui-btn-danger" id="cancel-verify-btn">确认销卡</button>' +
                                    '<button type="button" class="layui-btn layui-btn-primary" id="cancel-cancel-btn" style="margin-left: 10px;">取消</button>' +
                                    '</div>' +
                                    '</div>' +
                                    '</div>',
                                success: function(layero, index) {
                                    var $verifyInput = $('#cancel-verify-input');
                                    var expectedInput = 'DEL' + cardLastFour;
                                    
                                    // 聚焦到输入框
                                    $verifyInput.focus();
                                    
                                    // 取消按钮事件
                                    $('#cancel-cancel-btn').on('click', function() {
                                        layer.close(index);
                                    });
                                    
                                    // 提交按钮事件
                                    $('#cancel-verify-btn').on('click', function() {
                                        var inputValue = $verifyInput.val();
                                        
                                        // 验证输入
                                        if (inputValue === expectedInput) {
                                            // 输入正确，关闭验证框，继续销卡操作
                                            layer.close(index);
                                            layer.msg('正在销卡，需要等待几秒', {icon: 0});
                                            
                                            if (data) {
                                                // 显示加载中
                                                var loadIndex = layer.load(2);
                                                
                                                // 构建要发送的数据
                                                var formData = {
                                                    "card_id": data.card_id,
                                                    "version": data.version,
                                                };
                                                console.log(formData)
                                                
                                                // 向服务器提交数据
                                                $.ajax({
                                                    url: '/cards/cancel_card',
                                                    type: 'DELETE',
                                                    contentType: 'application/json',
                                                    data: JSON.stringify(formData),
                                                    success: function(res) {
                                                        layer.close(loadIndex);
                                                        if (res.code === 0) {
                                                            layer.msg('销卡成功', {icon: 1, time: 5000});
                                                            
                                                            // 重新加载表格数据
                                                            table.reload('cards-table');
                                                        } else {
                                                            layer.msg(res.msg || '销卡失败', {icon: 2});
                                                        }
                                                    },
                                                    error: function(xhr, status, error) {
                                                        layer.close(loadIndex);
                                                        console.error('AJAX错误:', status, error);
                                                        layer.msg('服务器错误，请稍后重试: ' + error, {icon: 2});
                                                    }
                                                });
                                            } else {
                                                layer.msg('获取此行数据异常', {icon: 2});
                                            }
                                        } else {
                                            // 输入错误，提示用户
                                            layer.msg('验证失败！请输入 DEL + 卡号后四位', {icon: 2});
                                        }
                                    });
                                    
                                    // 绑定回车键事件
                                    $verifyInput.on('keydown', function(e) {
                                        if (e.keyCode === 13) { // 回车键
                                            $('#cancel-verify-btn').click();
                                        }
                                    });
                                }
                            });
                        });
                        break;
                    case 'freeze':
                        layer.confirm('确定要冻结该卡吗？', function(index){
                            console.log('冻结卡', data);
                            layer.msg('正在冻结，需要等待几秒', {icon: 0});
                            if (data && data.cards_status === 'ACTIVE') {
                                // 显示加载中
                                var loadIndex = layer.load(2);
                                
                                // 构建要发送的数据
                                var formData = {
                                    "card_id": data.card_id,
                                    "version": data.version,
                                    "freeze": true
                                };
                                
                                // 向服务器提交数据
                                $.ajax({
                                    url: '/cards/freeze_unfreeze',
                                    type: 'PUT',
                                    contentType: 'application/json',
                                    data: JSON.stringify(formData),
                                    success: function(res) {
                                        layer.close(loadIndex);
                                        if (res.code === 0) {
                                            layer.msg('冻结成功', {icon: 1, time: 5000});
                                            layer.close(index); // 关闭确认弹窗
                                            
                                            // 重新加载表格数据
                                            table.reload('cards-table');
                                        } else {
                                            layer.msg(res.msg || '冻结失败', {icon: 2});
                                        }
                                    },
                                    error: function(xhr, status, error) {
                                        layer.close(loadIndex);
                                        console.error('AJAX错误:', status, error);
                                        layer.msg('服务器错误，请稍后重试: ' + error, {icon: 2});
                                    }
                                });
                            } else {
                                layer.msg('只能冻结激活状态的卡', {icon: 2});
                                layer.close(index);
                            }
                        });
                        break;
                    case 'unfreeze':
                        layer.confirm('确定要解冻该卡吗？', function(index){
                            console.log('解冻卡', data);
                            layer.msg('正在解冻，需要等待几秒', {icon: 0});
                            if (data && data.cards_status === 'FROZEN') {
                                // 显示加载中
                                var loadIndex = layer.load(2);
                                
                                // 构建要发送的数据
                                var formData = {
                                    "card_id": data.card_id,
                                    "version": data.version,
                                    "freeze": false
                                };
                                
                                // 向服务器提交数据
                                $.ajax({
                                    url: '/cards/freeze_unfreeze',
                                    type: 'PUT',
                                    contentType: 'application/json',
                                    data: JSON.stringify(formData),
                                    success: function(res) {
                                        console.log('解冻结果', res);
                                        layer.close(loadIndex);
                                        if (res.code === 0) {
                                            layer.msg('解冻成功', {icon: 1, time: 5000});
                                            layer.close(index); // 关闭确认弹窗
                                            
                                            // 重新加载表格数据
                                            table.reload('cards-table');
                                        } else {
                                            layer.msg(res.msg || '解冻失败', {icon: 2});
                                        }
                                    },
                                    error: function(xhr, status, error) {
                                        layer.close(loadIndex);
                                        console.error('AJAX错误:', status, error);
                                        layer.msg('服务器错误，请稍后重试: ' + error, {icon: 2});
                                    }
                                });
                            } else {
                                layer.msg('只能解冻冻结状态的卡', {icon: 2});
                                layer.close(index);
                            }
                        });
                        break;
                }
            });
        }

        // 初始化所有功能
        initForm();
        initCardsTable();
        initEventListeners();
        
    } catch (error) {
        console.error("初始化过程中发生错误:", error);
        layer.msg('初始化失败: ' + error.message, {icon: 2});
    };
});

