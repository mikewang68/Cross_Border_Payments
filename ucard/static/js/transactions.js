/**
 * 交易记录页面专用脚本
 * 用于处理交易记录表格的渲染、搜索、分页等功能
 */

layui.use(['table', 'form', 'layer'], function(){
    var table = layui.table;
    var form = layui.form;
    var layer = layui.layer;
    
    // 获取后端传递的数据
    var allTransactions = JSON.parse(document.getElementById('transactions-data').textContent);
    
    // 初始化表单组件
    function initForm() {
        // 重新渲染表单元素，特别是下拉菜单
        form.render();
    }
    
    // 初始化表格
    function initTransactionTable() {
        // 渲染交易记录表格
        table.render({
            elem: '#transaction-table',
            data: allTransactions,  // 使用本地数据
            page: true,             // 开启分页
            limit: 10,               // 默认每页显示5条
            limits: [5, 10, 20, 50],
            height: 'auto',         // 使用自动高度，不要固定高度
            cols: [[
                {field: 'transaction_time', title: '交易时间', width: 160},
                {field: 'transaction_id', title: '交易流水号', width: 180},
                {field: 'mask_card_number', title: '卡号', width: 160},
                {field: 'card_id', title: '卡ID', width: 120},
                {field: 'biz_type', title: '交易类型', width: 100, templet: function(d){
                    // 交易类型中文映射
                    var bizTypeMap = {
                        'AUTH': '交易扣款',
                        'CORRECTIVE_AUTH': '交易扣款修正',
                        'VERIFICATION': '验证交易',
                        'VOID': '交易撤单',
                        'REFUND': '交易退款',
                        'SETTLE': '交易结算',
                        'CORRECTIVE_REFUND': '退款修正',
                        'CORRECTIVE_REFUND_VOID': '退款修正取消',
                        'REFUND_REVERSAL': '撤销退款',
                        'SERVICE_FEE': '卡服务费'
                    };
                    return bizTypeMap[d.biz_type] || d.biz_type;
                }},
                {field: 'transaction_amount', title: '交易金额', width: 120, sort: true, templet: function(d){
                    return d.transaction_amount + ' ' + d.transaction_amount_currency;
                }},
                {field: 'surcharge_amount', title: '交易手续费', width: 120, templet: function(d){
                    return d.surcharge_amount + ' ' + d.surcharge_currency;
                }},
                {field: 'status', title: '状态', width: 100},
                {field: 'version', title: '平台', width: 120},


                {field: 'status_description', title: '备注', width: 120},
                {fixed: 'right', title: '操作', width: 100, templet: function(d){
                    return '<a class="layui-btn layui-btn-xs" lay-event="detail">详情</a>';
                }}
            ]],
            done: function(res){
                // 确保分页正确显示
                this.count = allTransactions.length;
            }
        });
    }
    
    // 显示交易详情弹窗
    function showTransactionDetail(transactionData) {
        // 构建详情内容HTML
        var content = '<div class="layui-card">' +

            '<div class="layui-card-body">' +
            '<table class="layui-table">' +
            '<colgroup><col width="30%"><col width="70%"></colgroup>' +
            '<tbody>' +
            '<tr><td>交易流水号</td><td>' + (transactionData.transaction_id || '--') + '</td></tr>' +
            '<tr><td>交易时间</td><td>' + (transactionData.transaction_time || '--') + '</td></tr>' +
            '<tr><td>卡号</td><td>' + (transactionData.mask_card_number || '--') + '</td></tr>' +
            '<tr><td>卡ID</td><td>' + (transactionData.card_id || '--') + '</td></tr>' +
            '<tr><td>交易类型</td><td>' + (transactionData.biz_type || '--') + '</td></tr>' +
            '<tr><td>交易金额</td><td>' + (transactionData.transaction_amount || '0') + ' ' + 
                  (transactionData.transaction_amount_currency || '') + '</td></tr>' +
            '<tr><td>交易手续费</td><td>' + (transactionData.surcharge_amount || '0') + ' ' + 
                  (transactionData.surcharge_currency || '') + '</td></tr>' +
            '<tr><td>状态</td><td><span class="layui-badge layui-bg-green">成功</span></td></tr>' +
            '</tbody></table></div></div>';
            
        // 显示弹窗
        layer.open({
            type: 1,
            title: '交易详情',
            area: ['600px', '500px'],
            content: content
        });
    }
    
    // 初始化事件监听
    function initEventListeners() {
        // 监听表格工具条点击事件
        table.on('tool(transaction-table)', function(obj){
            var data = obj.data;
            if(obj.event === 'detail'){
                // 直接使用行数据显示详情
                showTransactionDetail(data);
            }
        });
        
        // 监听搜索表单提交
        form.on('submit(transactionSearch)', function(data){
            var formData = data.field;
            
            // 根据表单数据筛选交易记录
            var filteredData = allTransactions.filter(function(item) {
                if (formData.transaction_id && !item.transaction_id.includes(formData.transaction_id)) {
                    return false;
                }

                if (formData.version && !item.version.includes(formData.version)) {
                    return false;
                }

                if (formData.card_last_digits) {
                    var maskCardNumber = item.mask_card_number || '';
                    if (!maskCardNumber.endsWith(formData.card_last_digits)) {
                        return false;
                    }
                }
                if (formData.biz_type && item.biz_type !== formData.biz_type) {
                    return false;
                }
                return true;
            });
            
            // 重新加载表格数据
            table.reload('transaction-table', {
                data: filteredData,
                page: {
                    curr: 1 // 重新加载时定位到第一页
                }
            });
            
            return false; // 阻止表单默认提交
        });
        
        // 导出按钮点击事件
        $('#exportTransactions').on('click', function(){
            layer.msg('导出功能正在开发中', {icon: 6});
        });
    }
    
    // 页面加载完成后执行初始化
    $(function(){
        initForm();              // 初始化表单
        initTransactionTable();  // 初始化表格
        initEventListeners();    // 初始化事件监听
    });
}); 