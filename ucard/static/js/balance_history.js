/**
 * 交易记录页面专用脚本
 * 用于处理交易记录表格的渲染、搜索、分页等功能
 */

layui.use(['table', 'form', 'layer'], function(){
    var table = layui.table;
    var form = layui.form;
    var layer = layui.layer;
    
    // 获取后端传递的数据
    var allBalanceHistory = JSON.parse(document.getElementById('balance-history-data').textContent);
    
    // 初始化表单组件
    function initForm() {
        form.render();
    }
    
    // 初始化表格
    function initBalanceTable() {
        table.render({
            elem: '#balance-table',
            toolbar: '#toolbar',
            defaultToolbar: ['filter', 'exports'],
            data: allBalanceHistory,
            page: true,
            limit: 10,
            limits: [10, 20, 50, 100],
            height: 'full-220',
            cols: [[
                {type: 'checkbox', fixed: 'left'},
                {field: 'transaction_time', title: '交易时间', width: 160, sort: true},
                {field: 'transaction_id', title: '流水号', width: 180},
                {field: 'mask_card_number', title: '卡号', width: 160},
                {field: 'card_id', title: '卡ID', width: 120},
                {field: 'amount', title: '交易金额', width: 120, sort: true, templet: function(d){
                    return d.amount + ' ' + d.amount_currency;
                }},
                {field: 'txn_type', title: '业务类型', width: 120, templet: function(d){
                    // 交易类型中文映射
                    var txnTypeMap = {
                        'CARD_PAYMENT': '虚拟卡交易结算',
                        'CARD_PAYMENT_FEE': '虚拟卡交易手续费',
                        'CARD_REFUND': '虚拟卡交易退款',
                        'CARD_REFUND_FEE': '虚拟卡交易退款手续费',
                        'CARD_REFUND_REVERT': '虚拟卡交易退款撤销',
                        'CARD_REFUND_FEE_REVERT': '虚拟卡交易手续费退回',
                        'CARD_PRE_AUTH': '虚拟卡交易授权',
                        'CARD_PRE_AUTH_REVERT': '虚拟卡交易授权撤销',
                        'CARD_PRE_AUTH_FEE': '虚拟卡交易授权手续费，包括扣除和返还',
                        'CHARGEBACK': 'Chargeback手续费',
                        'CARD_BALANCE_ADJUST': '卡余额调整',
                        'CARD_INIT_FEE': '虚拟卡开卡手续费',
                        'CARD_INIT_FEE_REVERT': '创建虚拟卡手续费退回',
                        'CARD_SERVICE_FEE': '虚拟卡服务费',
                        'CARD_CANCEL_FEE': '销卡手续费',
                        'OTHER': '其他'
                    };
                    return txnTypeMap[d.txn_type] || d.txn_type;
                }},
                {field: 'card_biz_type', title: '交易类型', width: 120, templet: function(d){
                    // 交易类型中文映射
                    var cardbizTypeMap = {
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
                    return cardbizTypeMap[d.card_biz_type] || d.card_biz_type;
                }},
                {field: 'balance_after_transaction_amount', title: '账户余额', width: 120, sort: true, templet: function(d){
                    return d.balance_after_transaction_amount + ' ' + d.balance_after_transaction_currency;
                }},
                {field: 'version', title: '平台', width: 80},
                {fixed: 'right', title: '操作', toolbar: '#barTool', width: 80}
            ]],
            done: function(res){
                this.count = allBalanceHistory.length;
            }
        });
    }
    
    // 显示详情弹窗
    function showBalanceDetail(data) {
        // 获取业务类型和交易类型的中文映射
        var txnTypeMap = {
            'CARD_PAYMENT': '虚拟卡交易结算',
            'CARD_PAYMENT_FEE': '虚拟卡交易手续费',
            'CARD_REFUND': '虚拟卡交易退款',
            'CARD_REFUND_FEE': '虚拟卡交易退款手续费',
            'CARD_REFUND_REVERT': '虚拟卡交易退款撤销',
            'CARD_REFUND_FEE_REVERT': '虚拟卡交易手续费退回',
            'CARD_PRE_AUTH': '虚拟卡交易授权',
            'CARD_PRE_AUTH_REVERT': '虚拟卡交易授权撤销',
            'CARD_PRE_AUTH_FEE': '虚拟卡交易授权手续费，包括扣除和返还',
            'CHARGEBACK': 'Chargeback手续费',
            'CARD_BALANCE_ADJUST': '卡余额调整',
            'CARD_INIT_FEE': '虚拟卡开卡手续费',
            'CARD_INIT_FEE_REVERT': '创建虚拟卡手续费退回',
            'CARD_SERVICE_FEE': '虚拟卡服务费',
            'CARD_CANCEL_FEE': '销卡手续费',
            'OTHER': '其他'
        };

        var cardbizTypeMap = {
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

        layer.open({
            type: 1,
            title: '额度明细详情',
            area: ['600px', '500px'],
            content: `
                <div class="layui-card">
                    <div class="layui-card-body">
                        <table class="layui-table">
                            <colgroup>
                                <col width="30%">
                                <col width="70%">
                            </colgroup>
                            <tbody>
                                <tr><td>流水号</td><td>${data.transaction_id || '--'}</td></tr>
                                <tr><td>交易时间</td><td>${data.transaction_time || '--'}</td></tr>
                                <tr><td>卡号</td><td>${data.mask_card_number || '--'}</td></tr>
                                <tr><td>卡ID</td><td>${data.card_id || '--'}</td></tr>
                                <tr><td>交易金额</td><td>${data.amount} ${data.amount_currency}</td></tr>
                                <tr><td>业务类型</td><td>${txnTypeMap[data.txn_type] || data.txn_type || '--'}</td></tr>
                                <tr><td>交易类型</td><td>${cardbizTypeMap[data.card_biz_type] || data.card_biz_type || '--'}</td></tr>
                                <tr><td>账户余额</td><td>${data.balance_after_transaction_amount} ${data.balance_after_transaction_currency}</td></tr>
                                <tr><td>平台</td><td>${data.version || '--'}</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>`
        });
    }
    
    // 初始化事件监听
    function initEventListeners() {
        // 监听表格工具栏事件
        table.on('toolbar(balance-table)', function(obj){
            switch(obj.event) {
                case 'LAYTABLE_EXPORT':
                    table.exportFile(obj.config.id, allBalanceHistory, 'xls');
                    break;
            }
        });
        
        // 监听行工具事件
        table.on('tool(balance-table)', function(obj){
            if(obj.event === 'detail'){
                showBalanceDetail(obj.data);
            }
        });
        
        // 监听搜索表单提交
        form.on('submit(formSearch)', function(data){
            var formData = data.field;
            
            // 根据表单数据筛选记录
            var filteredData = allBalanceHistory.filter(function(item) {
                if (formData.transaction_id && !item.transaction_id.includes(formData.transaction_id)) {
                    return false;
                }
                if (formData.card_last_digits) {
                    var cardNumber = item.mask_card_number || '';
                    if (!cardNumber.endsWith(formData.card_last_digits)) {
                        return false;
                    }
                }
                if (formData.version && item.version !== formData.version) {
                    return false;
                }
                return true;
            });
            
            // 重新加载表格数据
            table.reload('balance-table', {
                data: filteredData,
                page: {
                    curr: 1
                }
            });
            
            return false;
        });
    }
    
    // 页面加载完成后执行初始化
    $(function(){
        initForm();
        initBalanceTable();
        initEventListeners();
    });
}); 