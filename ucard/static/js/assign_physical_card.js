layui.use(['form', 'layer','jquery'], function(){
    var form = layui.form;
    var layer = layui.layer; // 确保layer模块正确加载
    var $ = layui.jquery;

    // 获取数据
    var cardHolders = JSON.parse(document.getElementById('card-holders-data').textContent || '[]');

    // 初始化表单
    function initForm() {
        // 平台选择事件
        form.on('radio(platform)', function(data){
            updateFormByPlatform(data.value);
        });

        // 用卡人选择事件
        form.on('select(card_holder_id)', function(data){
            // 处理逻辑
        });

        // 表单验证规则
        form.verify({
            cardNumber: function(value) {
                if (!value) return '请输入实体卡卡号';
                if (!/^\d+$/.test(value)) return '卡号只能包含数字';
                if (value.length < 16 || value.length > 19) return '卡号长度应为16-19位';
            }
        });

        // 默认加载选中平台数据
        var defaultPlatform = $('input[name="version"]:checked').val();
        updateFormByPlatform(defaultPlatform);
    }

    // 根据平台更新用卡人
    function updateFormByPlatform(platform) {
        var cardHolderSelect = document.getElementById('card_holder_select');
        cardHolderSelect.innerHTML = '<option value="">请选择用卡人</option>';

        cardHolders.forEach(function(holder) {
            if (holder.version === platform) {
                var option = document.createElement('option');
                option.value = holder.card_holder_id;
                option.textContent = holder.first_name + ' ' + holder.last_name;
                cardHolderSelect.appendChild(option);
            }
        });
        form.render('select');
    }

    // 表单提交处理
    form.on('submit(cardAssignSubmit)', function(data){
        // 显示加载提示
        var loadIndex = layer.load(2, {shade: 0.3});

        // 发送请求
        $.ajax({
            url: '/cards/assign',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data.field),
            dataType: 'json', // 明确指定预期响应格式为JSON
            success: function(res) {
                layer.close(loadIndex); // 关闭加载提示

                // 验证响应格式
                if (typeof res !== 'object' || res.code === undefined) {
                    layer.msg('服务器响应格式错误', {icon: 2});
                    return;
                }

                // 显示结果提示
                if (res.code === 0) {
                    layer.msg(res.msg || '实体卡分配申请提交成功', {
                        icon: 1,
                        time: 2000 // 2秒后自动关闭
                    });
                } else {
                    layer.msg(res.msg || '提交失败', {icon: 2});
                }
            },
            error: function(xhr, status, error) {
                layer.close(loadIndex); // 关闭加载提示
                // 详细错误信息，便于调试
                console.error('请求错误:', status, error);
                layer.msg('网络错误，请稍后重试', {icon: 2});
            }
        });

        return false;
    });

    // 初始化
    initForm();
});
