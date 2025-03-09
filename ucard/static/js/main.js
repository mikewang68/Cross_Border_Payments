// 主JavaScript文件
layui.use(['element', 'layer', 'table', 'form'], function(){
    var element = layui.element;
    var layer = layui.layer;
    var table = layui.table;
    var form = layui.form;
    
    // 菜单点击事件
    $('.layui-nav-item a').click(function(){
        var type = $(this).data('type');
        var tab = $(this).data('tab');
        var title = $(this).data('title');
        
        // 如果不是添加标签页操作或者是父级菜单，直接返回
        if(type !== 'tabAdd' || !tab) return;
        
        // 显示加载提示
        var loadIndex = layer.load(1);
        
        // 判断标签页是否已存在
        var isTabExist = false;
        $('.layui-tab-title li').each(function(){
            if($(this).attr('lay-id') === tab){
                isTabExist = true;
                element.tabChange('main-tab', tab);
                layer.close(loadIndex);
                
                // 如果切换到钱包标签页，重新初始化
                if(tab === 'wallet') {
                    setTimeout(function() {
                        initWalletPage();
                    }, 100);
                }
                
                return false; // 找到后停止遍历
            }
        });
        
        // 如果标签页不存在，添加新标签页
        if(!isTabExist){
            // 发送AJAX请求获取内容
            $.get('/' + tab, function(content) {
                // 添加新标签页
                element.tabAdd('main-tab', {
                    title: title,
                    content: content,
                    id: tab
                });
                
                // 切换到新标签页
                element.tabChange('main-tab', tab);
                
                // 重新渲染表格等组件
                if(tab === 'card_users'){
                    // 延迟一下再渲染表格，确保DOM已经加载完成
                    setTimeout(function() {
                        renderCardUsersTable();
                    }, 100);
                } else if(tab === 'wallet') {
                    // 延迟初始化钱包界面，确保DOM已经加载完成
                    setTimeout(function() {
                        initWalletPage();
                    }, 100);
                }
                
                // 关闭加载提示
                layer.close(loadIndex);
            });
        }
    });
    
    // 渲染用卡人表格
    function renderCardUsersTable() {
        table.render({
            elem: '#user-table',
            url: '/api/card_holders',
            method: 'GET',
            toolbar: '#toolbar',
            defaultToolbar: ['filter', 'exports', 'print'],
            page: true,
            height: 'full-220',
            request: {
                pageName: 'page',
                limitName: 'limit'
            },
            response: {
                statusCode: 0 // 规定成功的状态码，Layui默认为0
            },
            cols: [[
                {type: 'checkbox', fixed: 'left'},
                {field: 'id', title: 'ID', width: 80, sort: true, fixed: 'left'},
                {field: 'name', title: '姓名', width: 120},
                {field: 'card_no', title: '卡号', width: 180},
                {field: 'balance', title: '余额', width: 120, sort: true},
                {field: 'email', title: '邮箱', width: 180},
                {field: 'phone', title: '手机号', width: 150},
                {field: 'country', title: '国家', width: 100},
                {field: 'state', title: '省份/州', width: 100},
                {field: 'city', title: '城市', width: 100},
                {field: 'address', title: '详细地址', width: 200},  
                {field: 'status', title: '状态', width: 100, templet: '#statusTpl'},
                {fixed: 'right', title: '操作', toolbar: '#barTool', width: 150}
            ]],
            parseData: function(res) {
                if (res.code === 500) {
                    layer.msg('获取数据失败：' + res.msg);
                    return {
                        "code": 1,
                        "msg": res.msg,
                        "count": 0,
                        "data": []
                    };
                }
                return {
                    "code": res.code,
                    "msg": res.msg,
                    "count": res.count,
                    "data": res.data
                };
            },
            done: function(res) {
                if (res.code === 500) {
                    layer.msg('获取数据失败：' + res.msg);
                }
            }
        });
        
        // 监听工具条事件
        table.on('tool(user-table)', function(obj){
            var data = obj.data;
            if(obj.event === 'del'){
                layer.confirm('确定要删除这条记录吗？', function(index){
                    $.ajax({
                        url: '/api/card_holders/' + data.id,
                        method: 'DELETE',
                        success: function(res) {
                            if(res.code === 200) {
                                obj.del();
                                layer.msg('删除成功');
                            } else {
                                layer.msg('删除失败：' + res.message);
                            }
                        }
                    });
                    layer.close(index);
                });
            } else if(obj.event === 'edit'){
                layer.open({
                    type: 2,
                    title: '编辑用卡人',
                    area: ['800px', '600px'],
                    content: '/card_holders/edit/' + data.id
                });
            }
        });
        
        // 监听表格工具栏事件
        table.on('toolbar(user-table)', function(obj){
            var checkStatus = table.checkStatus(obj.config.id);
            switch(obj.event){
                case 'add':
                    layer.open({
                        type: 2,
                        title: '添加用卡人',
                        area: ['800px', '600px'],
                        content: '/card_holders/add'
                    });
                    break;
                case 'batchDel':
                    var data = checkStatus.data;
                    if(data.length === 0){
                        layer.msg('请选择要删除的数据');
                        return;
                    }
                    layer.confirm('确定删除选中的数据吗？', function(index){
                        // 执行批量删除
                        layer.close(index);
                    });
                    break;
            }
        });
        
        // 表单搜索
        form.on('submit(formSearch)', function(data){
            table.reload('user-table', {
                where: data.field
            });
            return false;
        });
    }
    
    // 监听标签页切换事件
    element.on('tab(main-tab)', function(data){
        // 如果是用卡人标签页，重新渲染表格
        var layId = $(this).attr('lay-id');
        if(layId === 'card_users'){
            // 延迟一下再渲染表格，确保DOM已经加载完成
            setTimeout(function() {
                renderCardUsersTable();
            }, 100);
        }
    });
    
    // 监听标签页删除事件
    element.on('tabDelete(main-tab)', function(data){
        // 可以在这里添加标签页删除时的操作
    });
    
    // 窗口大小变化时，调整iframe高度
    $(window).resize(function(){
        $('.layadmin-iframe').height($(window).height() - 140);
    });
    
    // 初始化时调整所有iframe高度
    $('.layadmin-iframe').height($(window).height() - 140);
    
    // 添加快捷键支持
    $(document).keydown(function(event){
        // Ctrl+左箭头，切换到上一个选项卡
        if(event.ctrlKey && event.keyCode === 37){
            var prevTab = $('.layui-tab-title .layui-this').prev();
            if(prevTab.length > 0){
                var layId = prevTab.attr('lay-id');
                element.tabChange('demo', layId);
            }
        }
        
        // Ctrl+右箭头，切换到下一个选项卡
        if(event.ctrlKey && event.keyCode === 39){
            var nextTab = $('.layui-tab-title .layui-this').next();
            if(nextTab.length > 0){
                var layId = nextTab.attr('lay-id');
                element.tabChange('demo', layId);
            }
        }
    });
    
    // 关闭其它选项卡
    window.closeOtherTabs = function(){
        var currentId = $('.layui-tab-title .layui-this').attr('lay-id');
        $('.layui-tab-title li').each(function(){
            var id = $(this).attr('lay-id');
            if(id !== currentId && id !== 'home'){
                element.tabDelete('demo', id);
            }
        });
    };
    
    // 关闭全部选项卡
    window.closeAllTabs = function(){
        $('.layui-tab-title li').each(function(){
            var id = $(this).attr('lay-id');
            if(id !== 'home'){
                element.tabDelete('demo', id);
            }
        });
    };

    // 初始化钱包页面
    function initWalletPage() {
        console.log("初始化钱包页面");
        
        // 确保页面上存在钱包相关元素
        if($('#currencyGrid').length === 0) {
            console.log("找不到钱包相关元素，初始化取消");
            return;
        }
        
        console.log("找到钱包元素，开始初始化");
        
        // 显示加载状态
        layer.load(2);
        
        // 注册事件处理（先解绑再绑定，避免重复）
        $("#refreshWallet").off('click').on('click', function() {
            console.log("点击刷新按钮");
            initWalletPage();
            layer.msg('正在刷新数据...');
        });
        
        $("#printWallet").off('click').on('click', function() {
            console.log("点击打印按钮");
            layer.msg('打印功能开发中...');
        });
        
        $("#exportWallet").off('click').on('click', function() {
            console.log("点击导出按钮");
            layer.msg('导出功能开发中...');
        });
        
        // 获取钱包数据
        $.ajax({
            url: '/api/wallet/balance',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                console.log("获取钱包数据:", response);
                
                if(response.success && response.data) {
                    var walletData = response.data;
                    
                    // 更新主余额
                    var mainAmount = walletData.mainAmount || 0;
                    var parts = mainAmount.toString().split('.');
                    var intPart = parts[0];
                    var decPart = parts.length > 1 ? parts[1].padEnd(2, '0').substring(0, 2) : '00';
                    
                    $("#mainAmountInt").text(intPart);
                    $("#mainAmountDec").text(decPart);
                    $("#mainCurrency").text(walletData.mainCurrency);
                    $("#mainCurrencyLabel").text(walletData.mainCurrency);
                    $("#updateTime").text(walletData.updateTime);
                    
                    // 清空并添加货币卡片
                    $("#currencyGrid").empty();
                    
                    if(walletData.currencies && walletData.currencies.length > 0) {
                        walletData.currencies.forEach(function(currency) {
                            var flagHtml = '';
                            if(currency.icon_base64) {
                                flagHtml = `<img src="data:image/png;base64,${currency.icon_base64}" class="currency-flag" alt="${currency.code} flag" onerror="this.onerror=null;this.src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAMCAIAAADtbgqsAAAAFElEQVR4AWP4TyFgoDaMGjhqIL0BAFd5EhdCiGt4AAAAAElFTkSuQmCC';">`;
                            } else {
                                flagHtml = `<div class="currency-flag" style="background-color:#eee;"></div>`;
                            }
                            
                            var amountParts = currency.amount.toString().split('.');
                            var intPart = amountParts[0];
                            var decPart = amountParts.length > 1 ? amountParts[1].padEnd(2, '0').substring(0, 2) : '00';
                            
                            var amountDisplay = intPart + '.' + decPart;
                            
                            var card = `
                                <div class="currency-card">
                                    <div class="currency-header">
                                        ${flagHtml}
                                        <div class="currency-code">${currency.code}</div>
                                    </div>
                                    <div class="currency-label">账户余额</div>
                                    <div class="currency-amount">${amountDisplay}</div>
                                    <div class="currency-dots">...</div>
                                </div>
                            `;
                            $("#currencyGrid").append(card);
                        });
                    } else {
                        $("#currencyGrid").html('<div class="layui-card"><div class="layui-card-body">暂无货币数据</div></div>');
                    }
                } else {
                    layer.msg('获取钱包数据失败: ' + (response.message || '未知错误'));
                }
                
                layer.closeAll('loading');
            },
            error: function(xhr, status, error) {
                layer.closeAll('loading');
                layer.msg('网络错误，请稍后重试');
                console.error('获取钱包数据出错:', error);
            }
        });
    }
}); 