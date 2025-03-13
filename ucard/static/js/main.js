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
            'balance_history'
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
            $.get('/' + tab, function(content) {
                // 添加新标签页
                element.tabAdd('main-tab', {
                    title: title,
                    content: content,
                    id: tab
                });
                
                // 切换到新标签页
                element.tabChange('main-tab', tab);
                
                // 关闭加载提示
                layer.close(loadIndex);
            }).fail(function(xhr, status, error) {
                layer.close(loadIndex);
                layer.msg('加载失败: ' + error, {icon: 2});
            });
        }
    });
    
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