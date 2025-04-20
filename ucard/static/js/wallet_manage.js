layui.use(['table', 'form', 'layer'], function(){
    var table = layui.table;
    var form = layui.form;
    var layer = layui.layer;
    var $ = layui.jquery;
    
    // 初始化表格
    var walletTable = table.render({
        elem: '#walletManageTable',
        url: '/api/wallet_manage/list',  // 获取钱包管理数据的API
        page: true,  // 使用分页
        cols: [[
            {field: 'id', title: 'ID', width: 80, sort: true},
            {field: 'fee', title: '手续费率', width: 150},
            {field: 'percentage', title: '利润率', width: 150},
            {field: 'exchange_rate', title: '兑换费率', width: 150},
            {title: '操作', width: 150, align: 'center', toolbar: '#tableToolbar', fixed: 'right'}
        ]],
        text: {
            none: '暂无费率数据'  // 无数据时显示的文本
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
            
            return {
                "code": res.code,
                "msg": res.msg,
                "count": res.count,
                "data": res.data || []
            };
        },
        done: function(res){
            console.log("表格渲染完成", res);
        }
    });
    
    // 添加钱包管理按钮点击事件
    $('#addWalletBtn').on('click', function(){
        // 重置表单中的隐藏ID字段
        $('input[name="id"]').remove();
        
        // 弹出添加表单
        layer.open({
            type: 1,
            title: '添加费率',
            area: ['500px', '400px'],
            content: $('#walletManageForm'),
            success: function(layero, index){
                // 重置表单
                form.val('walletForm', {
                    fee: '',
                    percentage: '',
                    exchange_rate: ''
                });
            }
        });
    });
    
    // 表单提交事件 - 使用off先移除所有已绑定的事件
    $(document).off('submit', '#walletManageForm form').on('submit', '#walletManageForm form', function(e) {
        e.preventDefault(); // 阻止默认提交
        return false;
    });
    
    // 表单提交事件
    form.on('submit(submitWallet)', function(data){
        // 检查是否有提交锁，防止重复提交
        if($(this).data('submitting')) {
            console.log('表单正在提交中，请勿重复点击');
            return false;
        }
        
        // 设置提交锁
        $(this).data('submitting', true);
        
        // 验证表单数据有效性
        if(!validateForm(data.field)) {
            $(this).data('submitting', false); // 解锁
            return false;
        }
        
        console.log("准备提交的数据:", data.field); // 调试日志
        
        var url = data.field.id ? '/api/wallet_manage/update' : '/api/wallet_manage/add';
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
                        table.reload('walletManageTable', {
                            page: {
                                curr: 1 // 重新从第 1 页开始
                            },
                            where: {
                                _t: new Date().getTime() // 添加时间戳防止缓存
                            }
                        }, 'data');
                        console.log("表格已重新加载");
                    });
                } else {
                    layer.msg(res.msg || failMsg, {icon: 2, time: 2000});
                }
                // 解锁提交按钮
                $('button[lay-filter="submitWallet"]').data('submitting', false);
            },
            error: function(xhr, status, error){
                console.error("请求错误:", xhr, status, error); // 调试日志
                layer.msg('服务器错误，请稍后重试: ' + error, {icon: 2, time: 2000});
                // 解锁提交按钮
                $('button[lay-filter="submitWallet"]').data('submitting', false);
            }
        });
        
        return false; // 阻止表单默认提交
    });
    
    // 监听工具条事件
    table.on('tool(walletManageTable)', function(obj){
        var data = obj.data;
        var event = obj.event;
        
        if(event === 'edit'){
            // 编辑钱包管理数据
            form.val('walletForm', {
                fee: data.fee,
                percentage: data.percentage,
                exchange_rate: data.exchange_rate
            });
            
            layer.open({
                type: 1,
                title: '编辑费率',
                area: ['500px', '400px'],
                content: $('#walletManageForm'),
                success: function(layero, index){
                    // 动态添加ID字段
                    if($('input[name="id"]').length === 0){
                        $('<input>').attr({
                            type: 'hidden',
                            name: 'id',
                            value: data.id
                        }).appendTo($('#walletManageForm form'));
                    } else {
                        $('input[name="id"]').val(data.id);
                    }
                }
            });
        } else if (event === 'del') {
            layer.confirm('确定要删除该费率数据吗？', function(index){
                $.ajax({
                    url: '/api/wallet_manage/delete',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        id: data.id
                    }),
                    success: function(res){
                        if(res.code === 0){
                            layer.msg('删除成功', {icon: 1});
                            // 刷新表格
                            walletTable.reload();
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
        walletTable.reload();
        layer.msg('刷新成功', {icon: 1});
    });
    
    // 表单验证函数
    function validateForm(data) {
        // 验证手续费率
        if(!data.fee || !isValidRate(data.fee)) {
            layer.msg('请输入有效的手续费率，如：0.01 或 1%', {icon: 2, time: 2000});
            return false;
        }
        
        // 验证利润率
        if(!data.percentage || !isValidRate(data.percentage)) {
            layer.msg('请输入有效的利润率，如：0.05 或 5%', {icon: 2, time: 2000});
            return false;
        }
        
        // 验证兑换费率
        if(!data.exchange_rate || !isValidRate(data.exchange_rate)) {
            layer.msg('请输入有效的兑换费率，如：0.02 或 2%', {icon: 2, time: 2000});
            return false;
        }
        
        return true;
    }
    
    // 验证费率格式是否有效
    function isValidRate(rate) {
        // 允许百分比格式（如 5%）或小数格式（如 0.05）
        var percentPattern = /^(\d+(\.\d+)?)%$/;
        var decimalPattern = /^(\d+(\.\d+)?)$/;
        
        return percentPattern.test(rate) || decimalPattern.test(rate);
    }
});
