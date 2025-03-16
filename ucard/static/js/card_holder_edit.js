layui.use(['form', 'layer', 'laydate'], function(){
    var form = layui.form;
    var layer = layui.layer;
    var laydate = layui.laydate;
    var $ = layui.jquery;
    
    // 初始化日期选择器
    laydate.render({
        elem: '#birth',
        type: 'date'
    });
    
    // 加载表单数据
    function loadFormData() {
        // 从父窗口获取选中的行数据
        var data = parent.selectedCardHolderData;
        if (data) {
            // 使用 form.val 方法填充表单
            form.val('card-holder-edit-form', {
                "id": data.id,
                "region": data.region,
                "birth": data.birth,
                "email": data.email,
                "mobile": data.mobile,
                "country": data.country,
                "state": data.state,
                "city": data.city,
                "address": data.address,
                "postcode": data.postcode
            });
        } else {
            layer.msg('获取用卡人信息失败', {icon: 2});
            setTimeout(function() {
                var index = parent.layer.getFrameIndex(window.name);
                parent.layer.close(index);
            }, 1000);
        }
    }
    
    // 页面加载完成后加载数据
    $(function() {
        loadFormData();
    });
    
    // 表单提交
    form.on('submit(card-holder-edit-submit)', function(data){
        var formData = data.field;
        
        // 显示加载中
        var loadIndex = layer.load(2);
        
        // 向服务器提交数据
        $.ajax({
            url: '/card_holders/edit',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(res) {
                layer.close(loadIndex);
                if (res.code === 0) {
                    layer.msg('修改成功', {icon: 1});
                    // 关闭当前弹出层
                    setTimeout(function() {
                        var index = parent.layer.getFrameIndex(window.name);
                        parent.layer.close(index);
                    }, 1000);
                } else {
                    layer.msg(res.msg || '修改失败', {icon: 2});
                }
            },
            error: function() {
                layer.close(loadIndex);
                layer.msg('服务器错误，请稍后重试', {icon: 2});
            }
        });
        
        // 阻止表单默认提交
        return false;
    });
});
