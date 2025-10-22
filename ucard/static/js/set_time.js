layui.use(['table', 'form', 'layer', 'laydate'], function(){
    var table = layui.table;
    var form = layui.form;
    var layer = layui.layer;
    var laydate = layui.laydate;
    var $ = layui.jquery;
    
    // 初始化表格
    var timeTable = table.render({
        elem: '#setTimeTable',
        url: '/api/set_time/list',  // 获取更新时间数据的API
        page: true,  // 使用分页
        cols: [[
            {field: 'id', title: 'ID', width: 60, sort: true},
            {field: 'async_time', title: '同步时间间隔(秒)', width: 140},
            {field: 'daily_report', title: '日报更新时间', width: 140},
            {field: 'daily_start', title: '日汇率起始', width: 120},
            {field: 'daily_end', title: '日汇率截止', width: 120},
            {field: 'weekly_start', title: '周起始日期', width: 120},
            {field: 'weekly_end', title: '周截止日期', width: 120},
            {field: 'monthly_start', title: '月起始日期', width: 120},
            {field: 'monthly_end', title: '月截止日期', width: 120},
            {field: 'annual_start', title: '起始年份', width: 100},
            {field: 'annual_end', title: '截止年份', width: 100},
            {field: 'version', title: '平台名', width: 120},
            {title: '操作', width: 80, align: 'center', toolbar: '#tableToolbar', fixed: 'right'}
        ]],
        text: {
            none: '暂无更新时间数据'  // 无数据时显示的文本
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
    
    // 初始化日期控件
    function initDatePickers(){
        // 日期选择器
        laydate.render({
            elem: 'input[name="daily_report"]',
            type: 'time'
        });
        
        laydate.render({
            elem: 'input[name="daily_start"]',
            type: 'time'
        });
        
        laydate.render({
            elem: 'input[name="daily_end"]',
            type: 'time'
        });
        
        laydate.render({
            elem: 'input[name="weekly_start"]',
            type: 'date'
        });
        
        laydate.render({
            elem: 'input[name="weekly_end"]',
            type: 'date'
        });
        
        laydate.render({
            elem: 'input[name="monthly_start"]',
            type: 'date'
        });
        
        laydate.render({
            elem: 'input[name="monthly_end"]',
            type: 'date'
        });
        
        // 年份选择器
        laydate.render({
            elem: 'input[name="annual_start"]',
            type: 'year'
        });
        
        laydate.render({
            elem: 'input[name="annual_end"]',
            type: 'year'
        });
    }
    
    // 表单提交事件
    form.on('submit(submitTime)', function(data){
        // 检查是否有提交锁，防止重复提交
        if($(this).data('submitting')) {
            console.log('表单正在提交中，请勿重复点击');
            return false;
        }
        
        // 设置提交锁
        $(this).data('submitting', true);
        
        // 验证同步时间间隔
        if(!data.field.async_time || isNaN(data.field.async_time) || parseInt(data.field.async_time) <= 0) {
            layer.msg('请输入有效的同步时间间隔（正整数）', {icon: 2, time: 2000});
            $(this).data('submitting', false); // 解锁
            return false;
        }
        
        console.log("准备提交的数据:", data.field); // 调试日志
        
        // 提交数据
        $.ajax({
            url: '/api/set_time/update',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data.field),
            success: function(res){
                console.log("提交结果:", res); // 调试日志
                if(res.code === 0){
                    layer.msg(res.msg || '更新成功', {icon: 1, time: 2000}, function(){
                        // 关闭所有弹层
                        layer.closeAll();
                        // 强制刷新表格，不使用缓存
                        table.reload('setTimeTable', {
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
                    layer.msg(res.msg || '更新失败', {icon: 2, time: 2000});
                }
                // 解锁提交按钮
                $('button[lay-filter="submitTime"]').data('submitting', false);
            },
            error: function(xhr, status, error){
                console.error("请求错误:", xhr, status, error); // 调试日志
                layer.msg('服务器错误，请稍后重试: ' + error, {icon: 2, time: 2000});
                // 解锁提交按钮
                $('button[lay-filter="submitTime"]').data('submitting', false);
            }
        });
        
        return false; // 阻止表单默认提交
    });
    
    // 监听工具条事件
    table.on('tool(setTimeTable)', function(obj){
        var data = obj.data;
        var event = obj.event;
        
        if(event === 'edit'){
            // 编辑更新时间数据
            form.val('timeForm', {
                id: data.id,
                async_time: data.async_time,
                daily_report: data.daily_report,
                daily_start: data.daily_start,
                daily_end: data.daily_end,
                weekly_start: data.weekly_start,
                weekly_end: data.weekly_end,
                monthly_start: data.monthly_start,
                monthly_end: data.monthly_end,
                annual_start: data.annual_start,
                annual_end: data.annual_end,
                version: data.version
            });
            
            layer.open({
                type: 1,
                title: '编辑更新时间',
                area: ['600px', '600px'],
                content: $('#setTimeForm'),
                success: function(layero, index){
                    // 确保ID字段存在
                    if($('input[name="id"]').length === 0){
                        $('<input>').attr({
                            type: 'hidden',
                            name: 'id',
                            value: data.id
                        }).appendTo($('#setTimeForm form'));
                    } else {
                        $('input[name="id"]').val(data.id);
                    }
                    
                    // 初始化日期控件
                    initDatePickers();
                }
            });
        }
    });

    // 添加刷新按钮事件
    $('#refreshBtn').on('click', function(){
        timeTable.reload();
        layer.msg('刷新成功', {icon: 1});
    });
}); 