// 主JavaScript文件
layui.use(['element', 'layer'], function(){
    var element = layui.element;
    var layer = layui.layer;
    
    // 菜单点击事件
    $('.layui-nav-item a').click(function(){
        var type = $(this).data('type');
        var tab = $(this).data('tab');
        var title = $(this).data('title');
        
        // 如果不是添加标签页操作或者是父级菜单，直接返回
        if(type !== 'tabAdd' || !tab) return;
        
        // 已实现的功能列表
        var implementedFeatures = [
            'card_users',
            'transactions',
            'balance_history',
            'wallet_balance',
            'cards',
            'exchange_usdt',
            'daily',
            'change_password',
            'add_system'
        ];
        
        // 检查功能是否已实现
        if (!implementedFeatures.includes(tab)) {
            layer.msg('该功能正在开发中...', {icon: 5});
            return;
        }
        
        // 显示加载提示
        var loadIndex = layer.load(1);
        
        // 判断标签页是否已存在
        var isTabExist = false;
        $('.layui-tab-title li').each(function(){
            if($(this).attr('lay-id') === tab){
                isTabExist = true;
                element.tabChange('main-tab', tab);
                layer.close(loadIndex);
                return false; // 找到后停止遍历
            }
        });
        
        // 如果标签页不存在，添加新标签页
        if(!isTabExist){
            // 发送AJAX请求获取内容
            $.ajax({
                url: '/' + tab,
                type: 'GET',
                dataType: 'html',
                success: function(response) {
                    // 创建一个临时的div来提取content块的内容
                    var tempDiv = document.createElement('div');
                    tempDiv.innerHTML = response;
                    
                    // 提取content块内容，如果找不到则使用整个响应
                    var contentBlock = tempDiv.querySelector('.add-system-container, .daily-container, .wallet-container, .cards-container, .transactions-container, .balance-history-container');
                    var htmlContent = contentBlock ? contentBlock.outerHTML : response;
                    
                    // 添加新标签页
                    element.tabAdd('main-tab', {
                        title: title,
                        content: '<div class="layui-tab-container">' + htmlContent + '</div>',
                        id: tab
                    });
                    
                    // 切换到新标签页
                    element.tabChange('main-tab', tab);
                    
                    // 执行新加载内容中的脚本
                    executeScripts(tab);
                    
                    // 关闭加载提示
                    layer.close(loadIndex);
                },
                error: function(xhr, status, error) {
                    layer.close(loadIndex);
                    layer.msg('加载失败: ' + error, {icon: 2});
                }
            });
        }
    });
    
    // 执行新加载内容中的脚本
    function executeScripts(tab) {
        // 重新加载相关的JS和CSS
        var jsPath = '/static/js/' + tab + '.js';
        var cssPath = '/static/css/' + tab + '.css';
        
        // 动态加载JS
        if (!isScriptLoaded(jsPath)) {
            var script = document.createElement('script');
            script.src = jsPath;
            script.id = tab + '-js';
            document.body.appendChild(script);
        } else {
            // 如果已加载，尝试重新执行
            var existingScript = document.getElementById(tab + '-js');
            if (existingScript) {
                eval(existingScript.innerHTML);
            }
        }
        
        // 动态加载CSS
        if (!isStyleLoaded(cssPath)) {
            var link = document.createElement('link');
            link.rel = 'stylesheet';
            link.type = 'text/css';
            link.href = cssPath;
            link.id = tab + '-css';
            document.head.appendChild(link);
        }
        
        // 重新初始化layui组件
        layui.use(['form', 'table', 'laydate'], function(){
            var form = layui.form;
            form.render();
        });
    }
    
    // 检查脚本是否已加载
    function isScriptLoaded(src) {
        var scripts = document.getElementsByTagName('script');
        for (var i = 0; i < scripts.length; i++) {
            if (scripts[i].src.indexOf(src) !== -1) {
                return true;
            }
        }
        return false;
    }
    
    // 检查样式是否已加载
    function isStyleLoaded(href) {
        var links = document.getElementsByTagName('link');
        for (var i = 0; i < links.length; i++) {
            if (links[i].href.indexOf(href) !== -1) {
                return true;
            }
        }
        return false;
    }
    
    // 监听标签页切换事件
    element.on('tab(main-tab)', function(data){
        // 如果是首页标签，不需要特殊处理
        if($(this).attr('lay-id') === undefined) return;
    });
    
    // 监听标签页删除事件
    element.on('tabDelete(main-tab)', function(data){
        // 可以在这里添加标签页删除时的操作
    });
}); 