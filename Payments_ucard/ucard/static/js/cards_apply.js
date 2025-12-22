layui.use(['form', 'layer','jquery','laydate'], function(){
    var form = layui.form;
    var layer = layui.layer;
    var $ = layui.jquery;
    
    // 获取数据
    var cardHolders = JSON.parse(document.getElementById('card-holders-data').textContent);
    var cardsProduct = JSON.parse(document.getElementById('cards-product-data').textContent);
    var walletBalance = JSON.parse(document.getElementById('wallet-balance-data').textContent);

    // 初始化表单
    function initForm() {
        // 初始化平台选择
        form.on('radio(platform)', function(data){
            updateFormByPlatform(data.value);
        });

        // 初始化币种选择
        form.on('select(currency)', function(data){
            updateAvailableBalance();
        });

        // 初始化用卡人选择
        form.on('select(card_holder_id)', function(data){
            // 可以在这里添加选择用卡人后的处理逻辑
        });

        // 默认显示J1平台的数据
        updateFormByPlatform('J1');
    }

    // 更新可用余额显示
    function updateAvailableBalance() {
        var platform = document.querySelector('input[name="platform"]:checked').value;
        var currency = document.querySelector('select[name="currency"]').value;
        
        var platformBalance = walletBalance[platform] || {};
        var currencyBalance = platformBalance[currency] || {};
        var availableBalance = currencyBalance.available || '0';
        
        document.getElementById('availableBalance').textContent = availableBalance;
    }

    // 根据平台更新表单
    function updateFormByPlatform(platform) {
        // 更新卡产品按钮
        var productButtonsHtml = '';
        cardsProduct.forEach(function(product) {
            if (product.version === platform) {
                productButtonsHtml += `
                    <button type="button" class="layui-btn layui-btn-primary" 
                        data-product-code="${product.product_code}"
                        data-description="${product.description || ''}"
                        data-stock="${product.stock || 0}"
                        data-opened-quantity="${product.opened_quantity || 0}">
                        ${product.product_name}
                    </button>
                `;
            }
        });
        document.getElementById('productButtons').innerHTML = productButtonsHtml;
        document.getElementById('productDescription').textContent = '';
        document.getElementById('productStock').textContent = '';

        // 更新用卡人下拉框
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

        // 更新可用余额显示
        updateAvailableBalance();

        // 清空之前选择的卡产品
        var existingProductCode = document.querySelector('input[name="product_code"]');
        if (existingProductCode) {
            existingProductCode.remove();
        }

        // 重新渲染表单
        form.render('select');
    }

    // 卡产品按钮点击事件
    document.getElementById('productButtons').addEventListener('click', function(e) {
        if (e.target.classList.contains('layui-btn')) {
            // 移除其他按钮的选中状态
            document.querySelectorAll('#productButtons .layui-btn').forEach(btn => {
                btn.classList.remove('layui-btn-normal');
            });
            // 添加当前按钮的选中状态
            e.target.classList.add('layui-btn-normal');
            
            // 显示产品描述（如果有）
            var description = e.target.dataset.description;
            if (description && description.trim() !== '') {
                document.getElementById('productDescription').textContent = description;
            } else {
                document.getElementById('productDescription').textContent = '';
            }
            
            // 显示库存和已开卡数量信息
            var stock = e.target.dataset.stock;
            var openedQuantity = e.target.dataset.openedQuantity;
            document.getElementById('productStock').textContent = `可开卡数：${stock}，已开卡数：${openedQuantity}`;
            
            // 添加隐藏的input用于表单提交
            var existingProductCode = document.querySelector('input[name="product_code"]');
            if (existingProductCode) {
                existingProductCode.remove();
            }
            var productCodeInput = document.createElement('input');
            productCodeInput.type = 'hidden';
            productCodeInput.name = 'product_code';
            productCodeInput.value = e.target.dataset.productCode;
            document.querySelector('form').appendChild(productCodeInput);
        }
    });

    // 表单提交
    form.on('submit(cardApplySubmit)', function(data){
        // 验证是否选择了卡产品
        if (!document.querySelector('input[name="product_code"]')) {
            layer.msg('请选择卡产品', {icon: 2});
            return false;
        }
        
        // 验证交易额度
        var initBalance = parseFloat(data.field.init_balance);
        var platform = data.field.platform;
        var currency = data.field.currency;
        
        var platformBalance = walletBalance[platform] || {};
        var currencyBalance = platformBalance[currency] || {};
        var availableBalance = parseFloat(currencyBalance.available || 0);
        
        if (initBalance > availableBalance) {
            layer.msg('交易额度不能超过可用余额', {icon: 2});
            return false;
        }
        console.log(data.field)
        // 发送表单数据到服务器
        $.ajax({
            url: '/cards/newcard',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data.field),
            success: function(res) {
                if (res.code === 0) {
                    layer.msg('开卡申请提交成功', {icon: 1});
                    // 关闭当前页面
                    var index = parent.layer.getFrameIndex(window.name);
                    parent.layer.close(index);
                } else {
                    layer.msg(res.msg || '开卡申请提交失败', {icon: 2});
                }
            },
            error: function() {
                layer.close(loadIndex);
                layer.msg('服务器错误，请稍后重试', {icon: 2});
            }
        });

        return false;
    });

    // 初始化表单
    initForm();
});
