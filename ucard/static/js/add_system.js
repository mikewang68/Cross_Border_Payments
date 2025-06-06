layui.use(['table', 'form', 'layer'], function(){
    var table = layui.table;
    var form = layui.form;
    var layer = layui.layer;
    var $ = layui.jquery;
    
    // 初始化表格
    var systemTable = table.render({
        elem: '#systemTable',
        url: '/api/get_all_systems',  // 获取所有平台的API
        page: true,  // 使用分页
        cols: [[
            {field: 'id', title: 'ID', width: 80, sort: true},
            {field: 'system', title: '平台名称', width: 150},
            {field: 'appid', title: '平台ID', width: 200},
            {field: 'key', title: '平台密钥', width: 300, 
                templet: function(d){
                    // 显示密钥的部分内容，保护安全
                    if(d.key && d.key.length > 10) {
                        return d.key.substring(0, 5) + '******' + d.key.substring(d.key.length - 5);
                    }
                    return d.key || '';
                }
            },
            {title: '操作', width: 150, align: 'center', toolbar: '#tableToolbar', fixed: 'right'}
        ]],
        text: {
            none: '暂无平台数据'  // 无数据时显示的文本
        },
        response: {
            statusCode: 0  // 成功的状态码
        },
        parseData: function(res){
            console.log("API返回数据:", res); // 调试日志
            
            if(!res) {
                console.error("API返回数据为空");
                return { code: 1, msg: "数据格式错误", count: 0, data: [] };
            }
            
            // 过滤掉已删除的记录
            if(res.data && Array.isArray(res.data)) {
                res.data = res.data.filter(function(item) {
                    return item.status !== 'deleted';
                });
                console.log("过滤后的数据数量:", res.data.length);
            }
            
            return {
                "code": res.code,
                "msg": res.msg,
                "count": res.data ? res.data.length : 0,
                "data": res.data || []
            };
        },
        done: function(res){
            console.log("表格渲染完成", res);
            
            // 详细检查渲染结果
            if(res.data && res.data.length > 0) {
                console.log("渲染的数据:", res.data);
            } else {
                console.log("没有平台数据或渲染失败");
                // 尝试获取当前表格的配置信息
                var config = table.getConfig('systemTable');
                console.log("表格配置:", config);
            }
        }
    });
    
    // 添加平台按钮点击事件
    $('#addSystemBtn').on('click', function(){
        // 重置表单中的隐藏ID字段
        $('input[name="id"]').remove();
        
        // 弹出添加平台表单
        layer.open({
            type: 1,
            title: '添加平台',
            area: ['500px', '400px'],
            content: $('#addSystemForm'),
            success: function(layero, index){
                // 重置表单
                form.val('systemForm', {
                    system: '',
                    appid: '',
                    key: ''
                });
            }
        });
    });
    
    // 表单提交事件 - 使用off先移除所有已绑定的事件
    $(document).off('submit', '#addSystemForm form').on('submit', '#addSystemForm form', function(e) {
        e.preventDefault(); // 阻止默认提交
        return false;
    });
    
    // 表单提交事件
    form.on('submit(submitSystem)', function(data){
        // 检查是否有提交锁，防止重复提交
        if($(this).data('submitting')) {
            console.log('表单正在提交中，请勿重复点击');
            return false;
        }
        
        // 设置提交锁
        $(this).data('submitting', true);
        
        // 验证表单数据
        if(!data.field.system || !data.field.appid || !data.field.key) {
            layer.msg('请填写完整的平台信息', {icon: 2, time: 2000});
            $(this).data('submitting', false); // 解锁
            return false;
        }
        
        console.log("准备提交的数据:", data.field); // 调试日志
        
        var url = data.field.id ? '/api/update_system' : '/api/add_system';
        var successMsg = data.field.id ? '更新成功' : '添加成功';
        var failMsg = data.field.id ? '更新失败' : '添加失败';
        
        // 提交数据
        $.ajax({
            url: url,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data.field),
            success: function(res){
                console.log("提交结果:", res); // 调试日志
                if(res.code === 0){
                    layer.msg(res.msg || successMsg, {icon: 1, time: 2000}, function(){
                        // 关闭所有弹层
                        layer.closeAll();
                        // 强制刷新表格，不使用缓存
                        table.reload('systemTable', {
                            page: {
                                curr: 1 // 重新从第 1 页开始
                            },
                            where: {
                                _t: new Date().getTime() // 添加时间戳防止缓存
                            }
                        }, 'data');
                        console.log("表格已重新加载");
                        
                        // 额外检查：2秒后再次刷新表格
                        setTimeout(function() {
                            table.reload('systemTable');
                            console.log("表格延迟刷新完成");
                        }, 2000);
                    });
                } else {
                    layer.msg(res.msg || failMsg, {icon: 2, time: 2000});
                }
                // 解锁提交按钮
                $('button[lay-filter="submitSystem"]').data('submitting', false);
            },
            error: function(xhr, status, error){
                console.error("请求错误:", xhr, status, error); // 调试日志
                layer.msg('服务器错误，请稍后重试: ' + error, {icon: 2, time: 2000});
                // 解锁提交按钮
                $('button[lay-filter="submitSystem"]').data('submitting', false);
            }
        });
        
        return false; // 阻止表单默认提交
    });
    
    // 监听工具条事件
    table.on('tool(systemTable)', function(obj){
        var data = obj.data;
        var event = obj.event;
        
        if(event === 'edit'){
            // 编辑平台
            form.val('systemForm', {
                system: data.system,
                appid: data.appid,
                key: data.key
            });
            
            layer.open({
                type: 1,
                title: '编辑平台',
                area: ['500px', '400px'],
                content: $('#addSystemForm'),
                success: function(layero, index){
                    // 动态添加ID字段
                    if($('input[name="id"]').length === 0){
                        $('<input>').attr({
                            type: 'hidden',
                            name: 'id',
                            value: data.id
                        }).appendTo($('#addSystemForm form'));
                    } else {
                        $('input[name="id"]').val(data.id);
                    }
                }
            });
        } else if (event === 'del') {
            layer.confirm('确定要删除该平台吗？', function(index){
                $.ajax({
                    url: '/api/delete_system',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        id: data.id
                    }),
                    success: function(res){
                        if(res.code === 0){
                            layer.msg('删除成功', {icon: 1});
                            // 刷新表格
                            systemTable.reload();
                        }else{
                            layer.msg(res.msg, {icon: 2});
                        }
                    },
                    error: function(){
                        layer.msg('删除失败，请稍后重试', {icon: 2});
                    }
                });
                layer.close(index);
            });
        }
    });

    // 添加刷新按钮事件
    $('#refreshBtn').on('click', function(){
        systemTable.reload();
        layer.msg('刷新成功', {icon: 1});
    });
});
