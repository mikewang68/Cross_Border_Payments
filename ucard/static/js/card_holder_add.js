layui.use(['form', 'layer', 'laydate', 'jquery'], function(){
    var form = layui.form;
    var layer = layui.layer;
    var laydate = layui.laydate;
    var $ = layui.jquery;
    // 日期选择器
    laydate.render({
        elem: '#birth_date',
        value: new Date() // 默认当天
    });
    // 表单提交
    form.on('submit(cardHolderSubmit)', function(data){
        // 显示加载框
        var loadIndex = layer.load(1);
        
        // 构建提交数据
        var submitData = {
            first_name: data.field.first_name,
            last_name: data.field.last_name,
            birth: data.field.birth_date,
            email: data.field.email,
            mobile:{
                nation_code: data.field.nation_code,
                mobile: data.field.mobile
            },
            region: data.field.region,
            billing_address:{
                postcode: data.field.postcode,
                address: data.field.address,
                city: data.field.city,
                state: data.field.state,
                country: data.field.country,
            },
            version: data.field.version
        };
        console.log(submitData);
        
        // 发送请求
        $.ajax({
            url: '/card_holders/create',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(submitData),
            success: function(res){
                layer.close(loadIndex);
                
                if(res.code === 0){
                    layer.msg('添加成功', {
                        icon: 1,
                        time: 2000
                    }, function(){
                        // 刷新父页面的表格
                        parent.layui.table.reload('user-table');
                        // 关闭当前弹窗
                        var index = parent.layer.getFrameIndex(window.name);
                        parent.layer.close(index);
                    });
                } else {
                    layer.msg(res.msg || '添加失败', {icon: 2});
                }
            },
            error: function(){
                layer.close(loadIndex);
                layer.msg('服务器错误', {icon: 2});
            }
        });
        
        return false; // 阻止表单默认提交
    });
    
    // 自定义验证规则
    form.verify({
        phone: function(value){
            if(!/^1\d{10}$/.test(value)){
                return '请输入正确的手机号';
            }
        }
    });
});

// 发生错误: create_card_holder() takes 3 positional arguments but 4 were given