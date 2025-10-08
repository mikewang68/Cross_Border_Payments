/**
 * 交易记录页面专用脚本
 * 用于处理交易记录表格的渲染、搜索、分页等功能
 */

layui.use(['table', 'form', 'layer', 'laydate'], function(){
    var table = layui.table;
    var form = layui.form;
    var layer = layui.layer;
    var laydate = layui.laydate;
    
    // 获取后端传递的数据
    var allTransactions = JSON.parse(document.getElementById('transactions-data').textContent);
    
    // 初始化表单组件
    function initForm() {
        // 初始化日期选择器
        laydate.render({
            elem: '#date_start',
            type: 'datetime',
            format: 'yyyy-MM-dd HH:mm:ss',
            trigger: 'click' // 确保点击触发
        });
        
        laydate.render({
            elem: '#date_end',
            type: 'datetime',
            format: 'yyyy-MM-dd HH:mm:ss',
            trigger: 'click' // 确保点击触发
        });
        
        // 重新渲染表单元素，特别是下拉菜单
        form.render();
    }
    
    // 初始化表格
    function initTransactionTable() {
        // 渲染交易记录表格
        table.render({
            elem: '#transaction-table',
            toolbar: '#toolbar_transactions',
            defaultToolbar: ['filter', 'exports'],
            data: allTransactions,  // 使用本地数据
            page: true,             // 开启分页
            limit: 10,               // 默认每页显示10条
            limits: [10, 20, 50, 100],
            height: 'auto',         // 使用自动高度，不要固定高度
            cols: [[
                {field: 'transaction_time', title: '交易时间', width: 160, sort: true, templet: function(d){
                    return formatTime(d.transaction_time);
                }},
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
                {fixed: 'right', title: '操作', toolbar: '#barTool', width: 80}
            ]],
            done: function(res){
                // 确保分页正确显示
                this.count = allTransactions.length;
            }
        });
    }
    
    // 格式化时间函数
    function formatTime(timeStr) {
        if (!timeStr) return '--';
        
        // 处理ISO格式时间
        try {
            var date = new Date(timeStr);
            
            // 检查日期是否有效
            if (isNaN(date.getTime())) return timeStr;
            
            var year = date.getFullYear();
            var month = String(date.getMonth() + 1).padStart(2, '0');
            var day = String(date.getDate()).padStart(2, '0');
            var hours = String(date.getHours()).padStart(2, '0');
            var minutes = String(date.getMinutes()).padStart(2, '0');
            var seconds = String(date.getSeconds()).padStart(2, '0');
            
            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
        } catch (e) {
            console.error("时间格式化错误:", e);
            return timeStr; // 发生错误时返回原始时间字符串
        }
    }
    
    // 显示交易详情弹窗
    function showTransactionDetail(transactionData) {
        // 获取交易类型和业务类型的中文映射
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

        layer.open({
            type: 1,
            title: '交易详情',
            area: ['600px', '550px'],
            content: `
                <div class="layui-card">
                    <div class="layui-card-body">
                        <div class="detail-section">
                            <div class="detail-section-title"><i class="layui-icon layui-icon-form"></i> 交易信息</div>
                            <table class="layui-table">
                                <colgroup>
                                    <col width="30%">
                                    <col width="70%">
                                </colgroup>
                                <tbody>
                                    <tr><td>交易流水号</td><td>${transactionData.transaction_id || '--'}</td></tr>
                                    <tr><td>原始交易号</td><td>${transactionData.origin_transaction_id || '--'}</td></tr>
                                    <tr><td>交易时间</td><td>${formatTime(transactionData.transaction_time)}</td></tr>
                                    <tr><td>卡号</td><td>${transactionData.mask_card_number || '--'}</td></tr>
                                    <tr><td>卡ID</td><td>${transactionData.card_id || '--'}</td></tr>
                                    <tr><td>交易类型</td><td>${bizTypeMap[transactionData.biz_type] || transactionData.biz_type || '--'}</td></tr>
                                    <tr><td>交易金额</td><td>${transactionData.transaction_amount || '0'} ${transactionData.transaction_amount_currency || ''}</td></tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-section-title"><i class="layui-icon layui-icon-rmb"></i> 资金信息</div>
                            <table class="layui-table">
                                <colgroup>
                                    <col width="30%">
                                    <col width="70%">
                                </colgroup>
                                <tbody>
                                    <tr><td>交易本金(资金账户)</td><td>${transactionData.accounting_amount || '0'} ${transactionData.accounting_amount_currency || ''}</td></tr>
                                    <tr><td>总手续费(资金账户)</td><td>${transactionData.surcharge_amount || '0'} ${transactionData.surcharge_currency || ''}</td></tr>
                                    <tr><td>状态</td><td>${transactionData.status || '--'}</td></tr>
                                    <tr><td>状态说明</td><td>${transactionData.status_description || '--'}</td></tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-section-title"><i class="layui-icon layui-icon-user"></i> 商户信息</div>
                            <table class="layui-table">
                                <colgroup>
                                    <col width="30%">
                                    <col width="70%">
                                </colgroup>
                                <tbody>
                                    <tr><td>商户名称</td><td>${transactionData.merchant_name || '--'}</td></tr>
                                    <tr><td>商户地区</td><td>${transactionData.merchant_region || '--'}</td></tr>
                                    <tr><td>平台</td><td>${transactionData.version || '--'}</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>`
        });
    }
    
    // 初始化事件监听
    function initEventListeners() {
        // 监听表格工具栏事件
        table.on('toolbar(transaction-table)', function(obj){
            switch(obj.event) {
                case 'LAYTABLE_EXPORT':
                    table.exportFile(obj.config.id, allTransactions, 'xls');
                    break;
            }
        });
        
        // 监听行工具事件
        table.on('tool(transaction-table)', function(obj){
            if(obj.event === 'detail'){
                // 直接使用行数据显示详情
                showTransactionDetail(obj.data);
            }
        });
        
        // 监听搜索表单提交
        form.on('submit(transactionSearch)', function(data){
            var formData = data.field;
            
            console.log("搜索条件:", formData); // 添加日志记录搜索条件
            
            // 根据表单数据筛选交易记录
            var filteredData = allTransactions.filter(function(item) {
                if (formData.transaction_id && !item.transaction_id.includes(formData.transaction_id)) {
                    return false;
                }

                // 按平台搜索
                if (formData.version && item.version !== formData.version) {
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
                
                // 添加日期范围筛选 - 修改为更健壮的处理方式
                if (formData.date_start || formData.date_end) {
                    var transactionTime = item.transaction_time || '';
                    if (!transactionTime) return false;
                    
                    // 直接创建Date对象，浏览器会自动处理ISO格式
                    var transactionDate = new Date(transactionTime);
                    console.log("记录时间:", transactionTime, "→", transactionDate);
                    
                    if (formData.date_start && formData.date_start.trim() !== '') {
                        var startDate = new Date(formData.date_start);
                        console.log("开始时间:", formData.date_start, "→", startDate);
                        if (isNaN(startDate.getTime())) {
                            console.error("无效的开始日期:", formData.date_start);
                        } else if (transactionDate < startDate) {
                            return false;
                        }
                    }
                    
                    if (formData.date_end && formData.date_end.trim() !== '') {
                        var endDate = new Date(formData.date_end);
                        console.log("结束时间:", formData.date_end, "→", endDate);
                        if (isNaN(endDate.getTime())) {
                            console.error("无效的结束日期:", formData.date_end);
                        } else {
                            // 设置结束日期为当天最后一秒
                            endDate.setHours(23, 59, 59, 999);
                            if (transactionDate > endDate) {
                                return false;
                            }
                        }
                    }
                }
                
                return true;
            });
            
            console.log("筛选后记录数:", filteredData.length); // 添加日志记录筛选结果
            
            // 重新加载表格数据
            table.reload('transaction-table', {
                data: filteredData,
                page: {
                    curr: 1 // 重新加载时定位到第一页
                }
            });
            
            return false; // 阻止表单默认提交
        });
    }
    
    // 页面加载完成后执行初始化
    $(function(){
        initForm();              // 初始化表单
        initTransactionTable();  // 初始化表格
        initEventListeners();    // 初始化事件监听
    });
}); 