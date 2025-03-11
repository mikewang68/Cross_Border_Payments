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
                if(tab === 'wallet') {
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
    
    // 监听标签页切换事件
    element.on('tab(main-tab)', function(data){
        // 如果是钱包标签页，重新初始化
        var layId = $(this).attr('lay-id');
        if(layId === 'wallet'){
            setTimeout(function() {
                initWalletPage();
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