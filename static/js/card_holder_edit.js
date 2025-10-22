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
                "card_holder_id": data.card_holder_id,
                "first_name": data.first_name,
                "last_name": data.last_name,
                "version": data.version,
                "region": data.region,
                "birth": data.birth,
                "email": data.email,
                "telegram_email": data.telegram_email || data.email, // 如果telegram_email为空，使用email作为默认值
                "mobile_nation_code": data.mobile_nation_code,
                "mobile": data.mobile,
                "bill_address_country": data.bill_address_country,
                "bill_address_state": data.bill_address_state,
                "bill_address_city": data.bill_address_city,
                "bill_address": data.bill_address,
                "bill_address_postcode": data.bill_address_postcode
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
        transfromData = transformData(formData);
        
        // 显示加载中
        var loadIndex = layer.load(2);
        
        // 向服务器提交数据
        $.ajax({
            url: '/card_holders/edit',
            type: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(transfromData),
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

    // 转换函数
function transformData(original) {
    return {
      // 保留原始字段
        card_holder_id : original.card_holder_id,
        version: original.version,
        first_name: original.first_name,
        last_name: original.last_name,
        birth: original.birth,
        email: original.email,
        telegram_email: original.telegram_email,
        // 重组手机号字段
        mobile: {
            nation_code: original.mobile_nation_code,
            mobile: original.mobile
        },
        region: original.region,
        // 重组账单地址字段
        bill_address: {
            postcode: original.bill_address_postcode,
            address: original.bill_address,
            city: original.bill_address_city,
            state: original.bill_address_state,
            country: original.bill_address_country
        }
    };
  }
});
