/**
 * 用卡人管理页面专用脚本
 * 用于处理用卡人表格的渲染、搜索、分页等功能
 */

var selectedCardHolderData; // 存储选中的用卡人数据

layui.use(['table', 'form', 'layer'], function(){
    var table = layui.table;
    var form = layui.form;
    var layer = layui.layer;
    var $ = layui.jquery; // 使用jQuery
    
    try {
        // 获取后端传递的数据
        var dataElement = document.getElementById('card-holders-data');
        if (!dataElement) {
            console.error("找不到数据元素 #card-holders-data");
            layer.msg('数据加载失败：找不到数据元素', {icon: 2});
            return;
        }
        
        var dataText = dataElement.textContent;
        if (!dataText || dataText.trim() === '') {
            console.error("数据元素内容为空");
            layer.msg('数据加载失败：数据为空', {icon: 2});
            return;
        }
        
        // console.log("原始数据文本:", dataText);
        
        var allCardHolders = JSON.parse(dataText);

        // 假设原始数据存储在变量 data 中
        var transformedData = allCardHolders.map(item => {
            // 提取 first_name 和 last_name 的值
            const mobileCode = item.mobile_nation_code || '';
            const mobileNum = item.mobile || '';
            const firstName = item.first_name || '';
            const lastName = item.last_name || '';
            
            
            // 创建新对象，删除原字段并添加 name
            const {...rest } = item;
            return {
            ...rest,
            name: `${firstName}${lastName}`,
            phone_number: `${'(+' + mobileCode + ')'}${mobileNum}`
            };
        });
        
        console.log(transformedData);
        
        // 调试输出数据
        // console.log("用卡人数据:", allCardHolders);
        
        // 如果数据为null或undefined，初始化为空数组
        if (!transformedData) {
            console.warn("数据为null或undefined，初始化为空数组");
            transformedData = [];
        }
        
        // 初始化表单组件
        function initForm() {
            // 重新渲染表单元素
            form.render();
        }
        
        // 初始化表格
        function initCardHoldersTable() {
            // 渲染用卡人表格
            table.render({
                elem: '#user-table',
                toolbar: '#toolbar_card_holders',
                defaultToolbar: ['filter', 'exports'],
                data: transformedData,  // 使用本地数据
                url: null,             // 不使用URL加载数据
                page: true,             // 开启分页
                limit: 10,               // 默认每页显示10条
                limits: [10, 20, 50, 100],
                height: 'auto',         // 使用自动高度，不要固定高度
                cols: [[
                    {field: 'card_holder_id', title: 'ID', width: 250},
                    {field: 'name', title: '姓名', width: 120},
                    {field: 'phone_number', title: '手机号码', width: 150},
                    {field: 'region', title: '地区', width: 80},
                    {field: 'email', title: '邮箱', width: 210},
                    {field: 'version', title: '平台', width: 80},
                    {field: 'create_time', title: '创建时间', width: 160},
                    {field: 'bill_address_country', title: '国家', width: 80},  
                    {field: 'bill_address_state', title: '省份/州', width: 100},
                    {field: 'bill_address_city', title: '城市', width: 100},
                    {field: 'bill_address', title: '详细地址', width: 200},
                    {field: 'status', title: '状态', width: 80, templet: function(d){
                        return d.status === 'ACTIVE' ? '<span class="layui-badge layui-bg-green">激活</span>' : '<span class="layui-badge layui-bg-gray">未激活</span>';
                    }},
                    {fixed: 'right', title: '操作', toolbar: '#card_holder_barTool', width: 120}
                ]],
                done: function(res){
                    // 确保分页正确显示
                    this.count = transformedData.length;
                    console.log("表格渲染完成，数据条数：", this.count);
                    
                    // 如果没有数据，显示提示
                    if(transformedData.length === 0) {
                        layer.msg('暂无用卡人数据', {icon: 0});
                    }
                }
            });
        }
        
        // 显示用卡人详情弹窗
        function showCardHolderDetail(cardHolderData) {
            // 构建详情内容HTML
            var content = '<div class="layui-card">' +
                '<div class="layui-card-header" font-weight:900>用卡人' + (cardHolderData.name || '--') + '详情</div>' +
                '<div class="layui-card-body">' +
                '<table class="layui-table">' +
                '<colgroup><col width="30%"><col width="70%"></colgroup>' +
                '<tbody>' +
                // '<tr><td>用户编码</td><td>' + (cardHolderData.user_code || '--') + '</td></tr>' +
                '<tr><td>用户ID</td><td>' + (cardHolderData.card_holder_id || '--') + '</td></tr>' +
                '<tr><td>姓名</td><td>' + (cardHolderData.name || '--') + '</td></tr>' +
                '<tr><td>地区</td><td>' + (cardHolderData.region || '--') + '</td></tr>' +
                '<tr><td>邮箱</td><td>' + (cardHolderData.email || '--') + '</td></tr>' +
                '<tr><td>手机号码</td><td>' + (cardHolderData.phone_number || '--') + '</td></tr>' +
                '<tr><td>平台</td><td>' + (cardHolderData.version || '--') + '</td></tr>' +
                '<tr><td>出生日期</td><td>' + (cardHolderData.birth || '--') + '</td></tr>' +
                '<tr><td>国家</td><td>' + (cardHolderData.bill_address_country || '--') + '</td></tr>' +  
                '<tr><td>省/州</td><td>' + (cardHolderData.bill_address_state || '--') + '</td></tr>' +
                '<tr><td>城市</td><td>' + (cardHolderData.bill_address_city || '--') + '</td></tr>' +
                '<tr><td>地址</td><td>' + (cardHolderData.bill_address || '--') + '</td></tr>' +
                '<tr><td>邮编</td><td>' + (cardHolderData.bill_address_postcode || '--') + '</td></tr>' +
                '<tr><td>创建时间</td><td>' + (cardHolderData.create_time || '--') + '</td></tr>' +
                '<tr><td>状态</td><td>' + (cardHolderData.status === 'ACTIVE' ? 
                    '<span class="layui-badge layui-bg-green">激活</span>' : 
                    '<span class="layui-badge layui-bg-gray">未激活</span>') + '</td></tr>' +
                '<tr><td>Telegram ID</td><td>' + (cardHolderData.telegram_id || '--') + '</td></tr>' +
                '</tbody></table></div></div>';
                  
            // 显示弹窗
            layer.open({
                type: 1,
                title: '用卡人详情',
                area: ['600px', '600px'],
                content: content
            });
        }
        
        // 初始化事件监听
        function initEventListeners() {
            // 监听表格头工具栏事件
            table.on('toolbar(user-table)', function(obj){  
                switch(obj.event){
                    case 'add':
                        // 跳转到添加用卡人页面
                        layer.open({
                            type: 2,
                            title: '添加用卡人',
                            area: ['800px', '600px'],
                            content: '/card_holders/add',
                            end: function(){
                                // 刷新页面
                                // location.reload();
                                // 只刷新表格数据，不刷新整个页面
                                table.reload('user-table', {
                                    page: {
                                        curr: 1 // 重新从第一页开始
                                    }
                                });
                            }
                        });
                        break;
                    // case 'batchDel':
                    //     if(data.length === 0){
                    //         layer.msg('请选择至少一条数据', {icon: 2});
                    //         return;
                    //     }
                    //     layer.confirm('确定删除选中的用卡人吗？', function(index){
                    //         // 这里应该发送请求到后端执行删除
                    //         layer.msg('批量删除功能正在开发中', {icon: 6});
                    //         layer.close(index);
                    //     });
                    //     break;
                    // case 'import':
                    //     layer.msg('导入功能正在开发中', {icon: 6});
                    //     break;
                    // case 'export':
                    //     layer.msg('导出功能正在开发中', {icon: 6});
                    //     break;
                }
            });
            
            // 监听表格行工具事件
            table.on('tool(user-table)', function(obj){
                var data = obj.data;
                console.log("行工具事件触发，数据：", data);
                if(obj.event === 'edit'){
                    selectedCardHolderData = data;
                    // 打开编辑页面
                    layer.open({
                        type: 2,
                        title: '编辑用卡人',
                        area: ['800px', '600px'],
                        content: '/card_holders/edit_page',
                        end: function(){
                            table.reload('user-table', {
                                page: {
                                    curr: 1 // 重新从第一页开始
                                }
                            });

                        }
                    });
                } else if(obj.event === 'detail'){
                    // 显示用卡人详情
                    showCardHolderDetail(data);
                }
            });
            
            // 监听搜索表单提交
            form.on('submit(formSearch)', function(data){
                var formData = data.field;
                console.log("搜索表单提交，数据：", formData);
                
                // 根据表单数据筛选用卡人记录
                var filteredData = transformedData.filter(function(item) {
                    // 按姓名搜索
                    if (formData.name && item.user_name && !item.user_name.toLowerCase().includes(formData.name.toLowerCase())) {
                        return false;
                    }
                    
                    // 按邮箱搜索
                    if (formData.email && item.email && !item.email.toLowerCase().includes(formData.email.toLowerCase())) {
                        return false;
                    }

                    // 按平台搜索
                    if (formData.version && item.version !== formData.version) {
                        return false;
                    }
                    return true;
                });
                
                console.log("筛选后数据条数：", filteredData.length);
                
                // 重新加载表格数据
                table.reload('user-table', {
                    data: filteredData,
                    url: null,  // 不使用URL加载数据
                    page: {
                        curr: 1 // 重新加载时定位到第一页
                    }
                });
                
                return false; // 阻止表单默认提交
            });
        }
        
        // 页面加载完成后执行初始化
        $(function(){
            console.log("页面加载完成，开始初始化");
            initForm();              // 初始化表单
            initCardHoldersTable();  // 初始化表格
            initEventListeners();    // 初始化事件监听
        });
    } catch (error) {
        console.error("初始化过程中发生错误:", error);
        layer.msg('初始化失败: ' + error.message, {icon: 2});
    }
}); 