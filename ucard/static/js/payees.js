/**
 * 收款人管理页面专用脚本
 * 用于处理收款人表格的渲染、搜索、分页等功能
 */

layui.use(['table', 'form', 'layer'], function(){
    var table = layui.table;
    var form = layui.form;
    var layer = layui.layer;
    var $ = layui.jquery; // 使用jQuery
    
    try {
        // 获取后端传递的收款人数据
        var payeesDataElement = document.getElementById('payees-info-data');
        if (!payeesDataElement) {
            console.error("找不到数据元素 #payees-info-data");
            layer.msg('数据加载失败：找不到收款人数据元素', {icon: 2});
            return;
        }
        
        var payeesDataText = payeesDataElement.textContent;
        if (!payeesDataText || payeesDataText.trim() === '') {
            console.error("收款人数据元素内容为空");
            layer.msg('数据加载失败：收款人数据为空', {icon: 2});
            return;
        }
        
        // 获取支付方式数据
        var methodsDataElement = document.getElementById('methods-data');
        if (!methodsDataElement) {
            console.error("找不到数据元素 #methods-data");
            layer.msg('数据加载失败：找不到支付方式数据元素', {icon: 2});
            return;
        }
        
        var methodsDataText = methodsDataElement.textContent;
        if (!methodsDataText || methodsDataText.trim() === '') {
            console.error("支付方式数据元素内容为空");
            layer.msg('数据加载失败：支付方式数据为空', {icon: 2});
            return;
        }
        
        var payeesData = JSON.parse(payeesDataText);
        var paymentMethods = JSON.parse(methodsDataText);
        
        // 如果数据为null或undefined，初始化为空数组
        if (!payeesData) {
            console.warn("收款人数据为null或undefined，初始化为空数组");
            payeesData = [];
        }
        
        if (!paymentMethods) {
            console.warn("支付方式数据为null或undefined，初始化为空数组");
            paymentMethods = [];
        }
        
        // 处理数据，组合姓名和电话
        var transformedData = payeesData.map(item => {
            const mobileCode = item.mobile_nation_code || '';
            const mobile = item.mobile || '';
            const firstName = item.first_name || '';
            const lastName = item.last_name || '';
            
            return {
                ...item,
                full_name: firstName || lastName ? `${lastName}${ firstName}` : '--',
                phone_number: mobileCode || mobile ? (mobileCode ? `(+${mobileCode})${mobile}` : mobile) : '--',
                address: item.address || '--',
                payment_method: item.payment_method || '--',
                country: item.country || '--'
            };
        });
        
        console.log("处理后的收款人数据:", transformedData);
        
        // 初始化搜索表单
        function initSearchForm() {
            // 收集所有国家并去重
            var countries = [];
            var currencies = [];
            
            payeesData.forEach(item => {
                if (item.country && !countries.includes(item.country)) {
                    countries.push(item.country);
                }
                
                if (item.currencies && Array.isArray(item.currencies)) {
                    item.currencies.forEach(currency => {
                        if (!currencies.includes(currency)) {
                            currencies.push(currency);
                        }
                    });
                }
            });
            
            // 填充国家下拉框
            var countrySelect = $('select[name="country"]');
            countries.forEach(country => {
                countrySelect.append(`<option value="${country}">${country}</option>`);
            });
            
            // 填充币种下拉框
            var currencySelect = $('select[name="currency"]');
            currencies.forEach(currency => {
                currencySelect.append(`<option value="${currency}">${currency}</option>`);
            });
            
            // 重新渲染表单
            form.render();
        }
        
        // 初始化表格
        function initPayeesTable() {
            // 渲染收款人表格
            table.render({
                elem: '#payees-table',
                toolbar: '#toolbar_payees',
                defaultToolbar: ['filter', 'exports'],
                data: transformedData,  // 使用本地数据
                url: null,              // 不使用URL加载数据
                page: true,             // 开启分页
                limit: 10,              // 默认每页显示10条
                limits: [10, 20, 50, 100],
                height: 'auto',         // 使用自动高度
                cols: [[
                    {field: 'payee_id', title: '收款人ID', width: 250, templet: function(d){
                        return d.payee_id || '--';
                    }},
                    {field: 'account_type', title: '收款账户类型', width: 110, templet: function(d){
                        return d.account_type === 'E_WALLET' ? '个人钱包' : 
                               d.account_type === 'BANK_ACCOUNT' ? '银行账户' : 
                               d.account_type || '--';
                    }},
                    {field: 'full_name', title: '收款人姓名', width: 120},
                    {field: 'country', title: '国家/地区', width: 90},
                    {field: 'currencies', title: '币种', width: 80, templet: function(d){
                        return d.currencies || '--';
                    }},
                    {field: 'phone_number', title: '联系电话', width: 150},
                    {field: 'address', title: '收款人地址', width: 150},
                    {field: 'payment_method', title: '收款方式', width: 120},
                    {field: 'version', title: '平台', width: 80},
                    {fixed: 'right', title: '操作', toolbar: '#payees_barTool', width: 120}
                ]],
                done: function(res){
                    // 确保分页正确显示
                    this.count = transformedData.length;
                    console.log("表格渲染完成，数据条数：", this.count);
                    
                    // 如果没有数据，显示提示
                    if(transformedData.length === 0) {
                        layer.msg('暂无收款人数据', {icon: 0});
                    }
                }
            });
        }
        
        // 显示收款人详情弹窗
        function showPayeeDetail(payeeData) {
            // 构建详情内容HTML
            var content = '<div class="layui-card">' +
                '<div class="layui-card-header" font-weight:900>收款人' + (payeeData.full_name || '--') + '详情</div>' +
                '<div class="layui-card-body">' +
                '<table class="layui-table">' +
                '<colgroup><col width="30%"><col width="70%"></colgroup>' +
                '<tbody>' +
                '<tr><td>收款人ID</td><td>' + (payeeData.payee_id || '--') + '</td></tr>' +
                '<tr><td>收款账户类型</td><td>' + (payeeData.account_type === 'E_WALLET' ? '个人钱包' : 
                                         payeeData.account_type === 'BANK_ACCOUNT' ? '银行账户' : payeeData.account_type || '--') + '</td></tr>' +
                '<tr><td>收款人姓名</td><td>' + (payeeData.full_name || '--') + '</td></tr>' +
                '<tr><td>国家/地区</td><td>' + (payeeData.country || '--') + '</td></tr>' +
                '<tr><td>币种</td><td>' + (payeeData.currencies || '--') + '</td></tr>' +
                '<tr><td>联系电话</td><td>' + (payeeData.phone_number || '--') + '</td></tr>' +
                '<tr><td>收款人地址</td><td>' + (payeeData.address || '--') + '</td></tr>' +
                '<tr><td>收款方式</td><td>' + (payeeData.payment_method || '--') + '</td></tr>' +
                '</tbody></table></div></div>';
                  
            // 显示弹窗
            layer.open({
                type: 1,
                title: '收款人详情',
                area: ['600px', '500px'],
                content: content
            });
        }
        
        // 删除收款人确认
        function deletePayee(payeeId) {
            layer.confirm('确定要删除该收款人吗？', {icon: 3, title:'提示'}, function(index){
                // 获取当前表格中的数据
                var currentData = table.checkStatus('payees-table').data;
                
                // 查找对应payeeId的行数据
                var payeeData = null;
                for (var i = 0; i < transformedData.length; i++) {
                    if (transformedData[i].payee_id === payeeId) {
                        payeeData = transformedData[i];
                        break;
                    }
                }
                
                // 检查必要参数是否存在
                if (!payeeData || !payeeData.version || !payeeData.payee_id) {
                    layer.msg('缺少必要的参数(version或payee_id)', {icon: 2});
                    layer.close(index);
                    return;
                }
                
                // 显示加载中
                var loadIndex = layer.load(2);
                
                // 发送删除请求
                $.ajax({
                    url: '/payee/delete',
                    type: 'DELETE',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        version: payeeData.version,
                        payee_id: payeeData.payee_id
                    }),
                    success: function(res) {
                        layer.close(loadIndex);
                        if (res.code === 0) {
                            layer.msg(res.msg || '删除成功', {icon: 1});
                            // 删除成功后重新加载表格
                            table.reload('payees-table');
                        } else {
                            layer.msg(res.msg || '删除失败', {icon: 2});
                        }
                    },
                    error: function(xhr) {
                        layer.close(loadIndex);
                        console.error('删除收款人请求失败:', xhr);
                        layer.msg('网络错误，请稍后重试', {icon: 2});
                    },
                    complete: function() {
                        layer.close(index); // 关闭确认框
                    }
                });
            });
        }
        
        // 打开平台选择弹窗
        function openPlatformSelectDialog() {
            layer.open({
                type: 1,
                title: '选择平台',
                area: ['400px', '250px'],
                content: `
                <div style="padding: 20px;">
                    <form class="layui-form" lay-filter="platformSelectForm">
                        <div class="layui-form-item">
                            <label class="layui-form-label">平台</label>
                            <div class="layui-input-block">
                                <select name="platform" lay-verify="required" lay-filter="platformSelect">
                                    <option value="">请选择平台</option>
                                    <option value="J1">J1</option>
                                    <option value="J2">J2</option>
                                </select>
                            </div>
                        </div>
                        <div class="layui-form-item">
                            <div class="layui-input-block">
                                <button type="button" class="layui-btn" id="confirmPlatformBtn">确定</button>
                                <button type="button" class="layui-btn layui-btn-primary" id="cancelPlatformBtn">取消</button>
                            </div>
                        </div>
                    </form>
                </div>`,
                success: function(layero, index) {
                    form.render('select', 'platformSelectForm');
                    
                    // 确定按钮点击事件
                    $('#confirmPlatformBtn').on('click', function() {
                        var selectedPlatform = $('select[name="platform"]').val();
                        if (!selectedPlatform) {
                            layer.msg('请选择平台', {icon: 2});
                            return;
                        }
                        
                        // 关闭弹窗
                        layer.close(index);
                        
                        // 加载添加收款人页面
                        loadPayeeAddPage(selectedPlatform);
                    });
                    
                    // 取消按钮点击事件
                    $('#cancelPlatformBtn').on('click', function() {
                        layer.close(index);
                    });
                }
            });
        }
        
        // 加载添加收款人页面
        function loadPayeeAddPage(platform) {
            var cardBody = $('.payees-page .layui-card-body');
            window.originalPayeesContent = cardBody.html();
            
            layer.load(2);
            $.ajax({
                url: '/payee/add?version=' + platform,
                type: 'GET',
                success: function(html) {
                    layer.closeAll('loading');
                    
                    // 将加载的HTML内容放入card-body
                    cardBody.html(html);
                    
                    // 设置选择的平台显示
                    $('.selected-platform').text(platform);
                    $('#platformInput').val(platform);
                    $('#platformName').text(platform);
                    
                    // 确保表单被正确渲染
                    if (window.layui && window.layui.form) {
                        window.layui.form.render();
                    }
                    
                    // 绑定返回按钮和取消按钮事件
                    $('.return-button, .cancel-button').on('click', function() {
                        cardBody.html(window.originalPayeesContent);
                        
                        // 重新初始化事件监听
                        initEventListeners();
                        
                        // 重新渲染表单
                        if (window.layui && window.layui.form) {
                            window.layui.form.render();
                        }
                    });
                },
                error: function(xhr) {
                    layer.closeAll('loading');
                    console.error("加载添加收款人页面失败:", xhr);
                    layer.msg('加载添加收款人页面失败，请稍后重试', {icon: 2});
                }
            });
        }
        
        // 打开添加收款人页面
        function openAddPayeePage() {
            // 打开平台选择弹窗
            openPlatformSelectDialog();
        }
        
        // 初始化事件监听
        function initEventListeners() {
            // 监听表格头工具栏事件
            table.on('toolbar(payees-table)', function(obj){  
                switch(obj.event){
                    case 'add':
                        // 打开添加收款人页面
                        openAddPayeePage();
                        break;
                }
            });
            
            // 监听表格行工具事件
            table.on('tool(payees-table)', function(obj){
                var data = obj.data;
                console.log("行工具事件触发，数据：", data);
                if(obj.event === 'detail'){
                    // 显示收款人详情
                    showPayeeDetail(data);
                } else if(obj.event === 'delete'){
                    // 删除收款人
                    deletePayee(data.payee_id);
                }
            });
            
            // 监听搜索表单提交
            form.on('submit(formSearch)', function(data){
                var formData = data.field;
                console.log("搜索表单提交，数据：", formData);
                
                // 根据表单数据筛选收款人记录
                var filteredData = transformedData.filter(function(item) {
                    // 按姓名搜索
                    if (formData.name && item.full_name && item.full_name !== '--' && !item.full_name.includes(formData.name)) {
                        return false;
                    }
                    
                    // 按国家/地区搜索
                    if (formData.country && item.country && item.country !== '--' && item.country !== formData.country) {
                        return false;
                    }
                    
                    // 按币种搜索
                    if (formData.currency && Array.isArray(item.currencies) && item.currencies.length > 0 && !item.currencies.includes(formData.currency)) {
                        return false;
                    }
                    
                    // 按电话搜索
                    if (formData.phone && item.phone_number && item.phone_number !== '--' && !item.phone_number.includes(formData.phone)) {
                        return false;
                    }
                    
                    // 按平台搜索
                    if (formData.version && item.version && item.version !== formData.version) {
                        return false;
                    }
                    
                    return true;
                });
                
                // 使用筛选后的数据重新渲染表格
                table.reload('payees-table', {
                    data: filteredData
                });
                
                return false; // 阻止表单默认提交
            });
        }
        
        // 总初始化函数
        function init() {
            console.log("初始化收款人管理页面");
            initSearchForm();
            initPayeesTable();
            initEventListeners();
        }
        
        // 执行初始化
        init();
        
    } catch (error) {
        console.error("收款人管理页面初始化出错:", error);
        layer.msg('页面初始化失败:' + error.message, {icon: 2});
    }
});
