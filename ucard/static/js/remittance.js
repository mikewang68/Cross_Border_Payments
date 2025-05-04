layui.use(['table', 'form', 'layer', 'util'], function(){
    var table = layui.table;
    var form = layui.form;
    var layer = layui.layer;
    var util = layui.util;
    
    // 从DOM中获取后端传递的付款单数据
    var remittanceOrdersDataElem = document.getElementById('remittance-orders-data');
    var remittanceOrdersData = remittanceOrdersDataElem ? JSON.parse(remittanceOrdersDataElem.innerHTML) : [];
    console.log(remittanceOrdersData)
    
    // 格式化数据
    remittanceOrdersData.forEach(function(item) {
        // 处理为空的情况
        item.create_time = item.create_time || '--';
        item.finish_time = item.finish_time || '--';
        item.error_message = item.error_message || '--';
        item.last_name = item.last_name || '-';
        item.first_name = item.first_name || '-';
        
        // 计算总付款金额（付款金额 + 手续费）
        if (item.pay_amount !== null && item.pay_amount !== undefined && 
            item.surcharge_amount !== null && item.surcharge_amount !== undefined) {
            item.total_pay_amount = parseFloat(item.pay_amount) + parseFloat(item.surcharge_amount);
        } else {
            item.total_pay_amount = item.pay_amount || 0;
        }
    });
    
    // 初始化表格
    table.render({
        elem: '#remittance-table',
        data: remittanceOrdersData,
        toolbar: '#toolbar_remittance', // 指定表格工具栏
        defaultToolbar: ['filter', 'exports'], // 不显示默认工具栏
        page: true,
        limit: 10,
        limits: [10, 20, 50, 100],
        height: 'full-220',
        cols: [[
            {field: 'create_time', title: '创建时间', width: 180, sort: true, templet: function(d){
                return d.create_time !== '--' ? d.create_time.replace('T', ' ').replace('Z', '') : '--';
            }},
            {field: 'order_id', title: '付款流水号', width: 100},
            {field: 'version', title: '平台', width: 80},
            {field: 'receiver_name', title: '收款人', width: 140, templet: function(d){
                return d.last_name + ' ' + d.first_name || '--';
            }},
            {field: 'payment_method', title: '付款方式', width: 180, templet: '#paymentMethodTpl'},
            {field: 'receive_amount', title: '到账金额', width: 150, templet: function(d){
                return (d.receive_amount || '--') + ' ' + (d.receive_amount_currency || '');
            }},
            {field: 'total_pay_amount', title: '付款金额', width: 150, templet: function(d){
                return d.total_pay_amount + ' ' + (d.pay_amount_currency || '');
            }},
            {field: 'surcharge_amount', title: '手续费', width: 120, templet: function(d){
                return (d.surcharge_amount || '--') + ' ' + (d.surcharge_currency || '');
            }},
            {field: 'exchange_rate', title: '付款汇率', width: 120},
            {field: 'finish_time', title: '完成时间', width: 180, templet: function(d){
                return d.finish_time !== '--' ? d.finish_time.replace('T', ' ').replace('Z', '') : '--';
            }},
            {field: 'error_message', title: '状态说明', width: 200},
            {field: 'status', title: '状态', width: 120, fixed: 'right', templet: '#statusTpl'},
            {fixed: 'right', title: '操作', toolbar: '#remittance_barTool', width: 80}
        ]],
        done: function(){
            // 表格加载完成后的回调
        }
    });
    
    // 监听工具条事件
    table.on('tool(remittance-table)', function(obj){
        var data = obj.data;
        if(obj.event === 'detail'){
            // 显示付款单详情
            showRemittanceDetail(data);
        }
    });
    
    // 打开同步数据弹窗
    function openSyncDataDialog() {
        layer.open({
            type: 1,
            title: '同步数据',
            area: ['500px', '280px'],
            content: `
            <div style="padding: 20px;">
                <form class="layui-form" lay-filter="syncDataForm">
                    <div class="layui-form-item">
                        <label class="layui-form-label">平台选择</label>
                        <div class="layui-input-block">
                            <input type="checkbox" name="version[]" value="J1" title="J1" checked>
                            <input type="checkbox" name="version[]" value="J2" title="J2" checked>
                        </div>
                    </div>
                    <div class="layui-form-item">
                        <div class="layui-input-block">
                            <button type="button" class="layui-btn" id="confirmSyncBtn">开始同步</button>
                            <button type="button" class="layui-btn layui-btn-primary" id="cancelSyncBtn">取消</button>
                        </div>
                    </div>
                </form>
            </div>`,
            success: function(layero, index) {
                form.render(null, 'syncDataForm');
                
                // 确定按钮点击事件
                $('#confirmSyncBtn').on('click', function() {
                    // 收集选中的平台
                    var versionList = [];
                    $('input[name="version[]"]:checked').each(function() {
                        versionList.push($(this).val());
                    });
                    
                    // 验证选择项
                    if (versionList.length === 0) {
                        layer.msg('请至少选择一个平台', {icon: 2});
                        return;
                    }
                    
                    // 准备数据
                    var syncData = {
                        version: versionList
                    };
                    
                    // 发送同步请求
                    syncRemittanceData(syncData, index);
                });
                
                // 取消按钮点击事件
                $('#cancelSyncBtn').on('click', function() {
                    layer.close(index);
                });
            }
        });
    }
    
    // 发送同步请求
    function syncRemittanceData(syncData, layerIndex) {
        // 显示加载中
        var loadIndex = layer.load(2, {shade: [0.3, '#000']});
        
        // 发送同步请求
        $.ajax({
            url: '/remittance/rt_remittance',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(syncData),
            success: function(res) {
                layer.close(loadIndex);
                
                if (res.code === 0) {
                    layer.msg(res.msg || '同步成功', {icon: 1});
                    // 同步成功后关闭弹窗并刷新页面
                    layer.close(layerIndex);
                    setTimeout(function() {
                        window.location.reload();
                    }, 1500);
                } else {
                    layer.msg(res.msg || '同步失败', {icon: 2});
                }
            },
            error: function(xhr) {
                layer.close(loadIndex);
                console.error('同步数据请求失败:', xhr);
                layer.msg('网络错误，请稍后重试', {icon: 2});
            }
        });
    }
    
    // 监听表格头部工具栏事件
    table.on('toolbar(remittance-table)', function(obj){
        // 判断事件类型
        if (obj.event === 'sync') {
            // 打开同步数据弹窗
            openSyncDataDialog();
        }
        // 其他内置工具条事件无需单独处理，Layui会自动处理
        console.log('表格工具栏事件：', obj);
    });
    
    // 监听搜索表单提交
    form.on('submit(formSearch)', function(data){
        var formData = data.field;
        
        // 根据表单数据筛选付款单
        table.reload('remittance-table', {
            page: {
                curr: 1 // 重新从第 1 页开始
            },
            where: formData,
            data: filterRemittanceData(remittanceOrdersData, formData)
        });
        
        return false; // 阻止表单跳转
    });
    
    // 根据搜索条件筛选数据
    function filterRemittanceData(data, filter) {
        return data.filter(function(item) {
            // 根据收款人姓名筛选
            if (filter.name && !(item.last_name + item.first_name).toLowerCase().includes(filter.name.toLowerCase())) {
                return false;
            }
            
            // 根据平台筛选
            if (filter.version && item.version !== filter.version) {
                return false;
            }
            
            // 根据状态筛选
            if (filter.status && item.status !== filter.status) {
                return false;
            }
            
            return true;
        });
    }
    
    // 显示付款单详情的函数
    function showRemittanceDetail(data) {
        var html = '<div class="layui-table remittance-detail">';
        
        // 构建详情表格
        html += '<table class="layui-table">';
        html += '<colgroup><col width="30%"><col width="70%"></colgroup>';
        html += '<tbody>';
        
        // 遍历所有属性
        for (var key in data) {
            if (data.hasOwnProperty(key)) {
                var value = data[key] !== null && data[key] !== undefined ? data[key] : '--';
                
                // 格式化显示内容
                if (key === 'create_time' || key === 'finish_time') {
                    value = value !== '--' ? value.replace('T', ' ').replace('Z', '') : '--';
                }
                
                // 特殊处理付款方式
                if (key === 'payment_method' && value !== '--') {
                    value = '<div class="payment-method-item"><img src="/static/image/' + value + '.png" alt="' + value + '" class="payment-icon"><span>' + value + '</span></div>';
                }
                
                html += '<tr>';
                html += '<td>' + formatFieldName(key) + '</td>';
                html += '<td>' + value + '</td>';
                html += '</tr>';
            }
        }
        
        html += '</tbody></table>';
        html += '</div>';
        
        // 打开弹窗
        layer.open({
            type: 1,
            title: '付款单详情',
            content: html,
            area: ['600px', '600px'],
            maxmin: true
        });
    }
    
    // 格式化字段名称
    function formatFieldName(field) {
        var fieldNames = {
            'order_id': '付款流水号',
            'order_source': '订单来源',
            'create_time': '创建时间',
            'finish_time': '完成时间',
            'status': '状态',
            'payee_account_id': '收款账户ID',
            'payment_method': '付款方式',
            'pay_amount': '付款金额',
            'pay_amount_currency': '付款币种',
            'receive_amount': '到账金额',
            'receive_amount_currency': '到账币种',
            'surcharge_amount': '手续费',
            'surcharge_currency': '手续费币种',
            'exchange_rate': '汇率',
            'insert_time': '插入时间',
            'error_message': '错误信息',
            'version': '平台版本',
            'first_name': '收款人名',
            'last_name': '收款人姓',
            'payee_id': '收款人ID',
            'total_pay_amount': '总付款金额'
        };
        
        return fieldNames[field] || field;
    }
});
