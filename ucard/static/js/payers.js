/**
 * 付款人管理页面专用脚本
 * 用于处理付款人表格的渲染、搜索、分页等功能
 */

// 业务范围映射表
const businessScopeMap = {
    "MISCELLANEOUS_SERVICES": "杂项事务",
    "AUTOMOBILE_RENTAL_SERVICES": "汽车租赁服务",
    "RESTAURANTS_LEISURE": "餐厅休闲",
    "PROFESSIONAL_CONSULTING": "专业咨询",
    "EDUCATION": "教育",
    "DATA_PROCESSING_SERVICES": "数据处理服务",
    "HUMAN_RESOURCE_EMPLOYMENT_SERVICES": "人力资源就业服务",
    "ENVIRONMENTAL_FACILITIES_SERVICES": "环境设施服务",
    "OTHER_SERVICES": "其他服务",
    "AGRICULTURAL": "农业",
    "FORESTRY": "林业",
    "FISHING_HUNTING_AND_TRAPPING": "渔猎和诱捕",
    "TRANSPORTATION": "运输",
    "LOGISTICS_WAREHOUSING": "物流仓储",
    "AIRLINES_AIR_CARRIERS": "航空公司",
    "TRAVEL_ACCOMMODATION": "旅行住宿",
    "AUTOMOBILES_AND_VEHICLES": "汽车和车辆",
    "OFFICE_SUPPLIES": "办公用品",
    "DISTRIBUTORS": "分销商",
    "APPAREL_RETAIL": "服装零售",
    "COMPUTER_ELECTRONICS_RETAIL": "电脑电子零售",
    "HOME_IMPROVEMENT_HOMEFURNISHING_RETAIL": "家居装修家居零售",
    "CULTURE_AMUSEMENT_PETS": "文化娱乐宠物",
    "OTHER_RETAIL": "其他零售",
    "CONSTRUCTION_MATERIALS": "建筑材料",
    "CONTAINERS_PACKAGING": "集装箱包装",
    "BUILDING_PRODUCTS": "建筑产品",
    "CONSTRUCTION_ENGINEERING": "建筑工程",
    "ELECTRICAL_EQUIPMENT": "电气设备",
    "INDUSTRIAL_CONGLOMERATES": "工业集团",
    "MACHINERY": "机械",
    "TRADING_COMPANIES_DISTRIBUTORS": "贸易公司经销商",
    "AUTOMOBILE_COMPONENTS": "汽车零部件",
    "AUTOMOBILES": "汽车",
    "HOUSEHOLD_DURABLES": "家庭耐用品",
    "LEISURE_PRODUCTS": "休闲产品",
    "TEXTILES_APPAREL_LUXURY_GOODS": "纺织品服装奢侈品",
    "CONSUMER_STAPLES_DISTRIBUTION_RETAIL": "消费必需品分销零售",
    "BEVERAGES": "饮料",
    "FOOD_PRODUCTS": "食品",
    "HOUSEHOLD_PRODUCTS": "家用产品",
    "PERSONAL_CARE_PRODUCTS": "个人护理产品",
    "HEALTH_CARE_TECHNOLOGY": "医疗保健技术",
    "BIOTECHNOLOGY": "生物技术",
    "SOFTWARE": "软件",
    "TECHNOLOGY_HARDWARE_STORAGE_PERIPHERALS": "技术、硬件存储、外围设备",
    "ELECTRONIC_EQUIPMENT_INSTRUMENTS_COMPONENTS": "电子设备、仪器元件",
    "SEMICONDUCTORS_SEMICONDUCTOR_EQUIPMENT": "半导体设备",
    "MEDIA": "媒体",
    "ENTERTAINMENT": "娱乐",
    "INTERACTIVE_MEDIA_SERVICES": "互动媒体服务",
    "OTHERS": "其他"
};

// 付款人类型映射
const subjectTypeMap = {
    "INDIVIDUAL": "个人",
    "ENTERPRISE": "企业"
};

// 证件类型映射
const certTypeMap = {
    "PASSPORT": "护照",
    "DRIVING_LICENSE": "驾照",
    "ID_CARD": "身份证",
    "BUSINESS_LICENSE": "营业执照"
};

// 格式化业务范围
function formatBusinessScopes(scopes) {
    // 确保scopes是一个数组
    if (!scopes || !Array.isArray(scopes) || scopes.length === 0) {
        return '--';
    }
    
    return scopes.map(scope => businessScopeMap[scope] || scope).join('、');
}

// 格式化证件信息
function formatCertInfo(certType, certNumber) {
    if (!certType || !certNumber) {
        return '--';
    }
    
    const typeText = certTypeMap[certType] || certType;
    return `${typeText}(${certNumber})`;
}

layui.use(['table', 'form', 'layer'], function(){
    var table = layui.table;
    var form = layui.form;
    var layer = layui.layer;
    var $ = layui.jquery;
    
    try {
        // 获取后端传递的数据
        var dataElement = document.getElementById('payers-info-data');
        if (!dataElement) {
            console.error("找不到数据元素 #payers-info-data");
            layer.msg('数据加载失败：找不到数据元素', {icon: 2});
            return;
        }
        
        var dataText = dataElement.textContent;
        if (!dataText || dataText.trim() === '') {
            console.error("数据元素内容为空");
            layer.msg('数据加载失败：数据为空', {icon: 2});
            return;
        }
        
        var payersData = JSON.parse(dataText);
        
        // 如果数据为null或undefined，初始化为空数组
        if (!payersData) {
            console.warn("数据为null或undefined，初始化为空数组");
            payersData = [];
        }
        
        // 转换数据
        var transformedData = payersData.map(item => {
            // 确保business_scopes是数组
            const businessScopes = Array.isArray(item.business_scopes) ? item.business_scopes : [];
            
            return {
                ...item,
                business_scopes: businessScopes, // 确保business_scopes是数组
                full_name: (item.first_name || '') + ' ' + (item.last_name || ''),
                subject_type_text: subjectTypeMap[item.subject_type] || item.subject_type,
                cert_info: formatCertInfo(item.cert_type, item.cert_number),
                business_scopes_text: formatBusinessScopes(businessScopes)
            };
        });
        
        console.log("付款人数据:", transformedData);
        
        // 初始化表单组件
        function initForm() {
            form.render();
        }
        
        // 初始化表格
        function initPayersTable() {
            table.render({
                elem: '#payer-table',
                toolbar: '#toolbar_payers',
                defaultToolbar: ['filter', 'exports'],
                data: transformedData,
                url: null,
                page: true,
                limit: 10,
                limits: [10, 20, 50, 100],
                height: 'auto',
                cols: [[
                    {field: 'subject_type_text', title: '付款人类型', width: 100},
                    {field: 'full_name', title: '付款人名称', width: 120},
                    {field: 'cert_info', title: '证件', width: 180},
                    {field: 'birthday', title: '出生年月', width: 120},
                    {field: 'business_scopes_text', title: '业务范围', width: 150},
                    {field: 'address', title: '地址', width: 300},
                    {field: 'version', title: '平台', width: 80},
                    {fixed: 'right', title: '操作', toolbar: '#payer_barTool', width: 120}
                ]],
                done: function(res){
                    this.count = transformedData.length;
                    console.log("表格渲染完成，数据条数：", this.count);
                    
                    if(transformedData.length === 0) {
                        layer.msg('暂无付款人数据', {icon: 0});
                    }
                }
            });
        }
        
        // 显示付款人详情弹窗
        function showPayerDetail(payerData) {
            // 确保业务范围是数组并构建HTML
            const businessScopes = Array.isArray(payerData.business_scopes) ? payerData.business_scopes : [];
            let businessScopesHtml = formatBusinessScopes(businessScopes);
            
            // 判断付款人类型
            const isIndividual = payerData.subject_type === 'INDIVIDUAL';
            
            // 构建详情内容HTML
            var content = '<div class="layui-card">' +
                '<div class="layui-card-body">';
                
            // 付款人基本信息部分
            content += '<div class="layui-card-header" style="font-size: 14px; margin-bottom: 15px; border-left: 2px solid #1E9FFF; padding-left: 10px;">付款人信息</div>';
            content += '<table class="layui-table">' +
                '<colgroup><col width="30%"><col width="70%"></colgroup>' +
                '<tbody>' +
                '<tr><td>付款人类型</td><td>' + (payerData.subject_type_text || '--') + '</td></tr>' +
                '<tr><td>付款人ID</td><td>' + (payerData.payer_id || '--') + '</td></tr>';
                
            // 根据付款人类型显示不同字段
            if (isIndividual) {
                // 个人类型
                content += '<tr><td>名字</td><td>' + (payerData.first_name || '--') + '</td></tr>' +
                    '<tr><td>姓氏</td><td>' + (payerData.last_name || '--') + '</td></tr>' +
                    '<tr><td>证件类型</td><td>' + (certTypeMap[payerData.cert_type] || payerData.cert_type || '--') + '</td></tr>' +
                    '<tr><td>证件号码</td><td>' + (payerData.cert_number || '--') + '</td></tr>' +
                    '<tr><td>出生年月</td><td>' + (payerData.birthday || '--') + '</td></tr>' +
                    '<tr><td>国籍</td><td>' + (payerData.region || '--') + '</td></tr>';
            } else {
                // 企业类型
                content += '<tr><td>公司名称</td><td>' + (payerData.company_name || '--') + '</td></tr>' +
                    '<tr><td>注册号</td><td>' + (payerData.register_number || '--') + '</td></tr>' +
                    '<tr><td>业务范围</td><td>' + businessScopesHtml + '</td></tr>';
            }
            
            content += '</tbody></table>';
            
            // 地址信息部分
            content += '<div class="layui-card-header" style="font-size: 14px; margin: 15px 0; border-left: 2px solid #1E9FFF; padding-left: 10px;">地址信息</div>';
            content += '<table class="layui-table">' +
                '<colgroup><col width="30%"><col width="70%"></colgroup>' +
                '<tbody>' +
                '<tr><td>国家/地区</td><td>' + (payerData.address_country || '--') + '</td></tr>' +
                '<tr><td>州/省</td><td>' + (payerData.address_state || '--') + '</td></tr>' +
                '<tr><td>城市</td><td>' + (payerData.address_city || '--') + '</td></tr>' +
                '<tr><td>详细地址</td><td>' + (payerData.address || '--') + '</td></tr>' +
                '<tr><td>邮编</td><td>' + (payerData.address_postcode || '--') + '</td></tr>' +
                '</tbody></table>';
                
            content += '</div></div>';
                  
            // 显示弹窗
            layer.open({
                type: 1,
                title: '付款人详情',
                area: ['700px', '600px'],
                content: content
            });
        }
        
        // 初始化事件监听
        function initEventListeners() {
            // 监听表格头工具栏事件
            table.on('toolbar(payer-table)', function(obj){  
                switch(obj.event){
                    case 'add':
                        // 弹出添加付款人弹窗（使用iframe加载）
                        layer.open({
                            type: 2,
                            title: '添加付款人',
                            area: ['800px', '600px'],
                            content: '/payers/add_page',
                            end: function(){
                                table.reload('payer-table', {
                                    page: {
                                        curr: 1 // 重新从第一页开始
                                    }
                                });
                            }
                        });
                        break;
                }
            });
            
            // 监听表格行工具事件
            table.on('tool(payer-table)', function(obj){
                var data = obj.data;
                console.log("行工具事件触发，数据：", data);
                
                if(obj.event === 'detail'){
                    // 显示付款人详情
                    showPayerDetail(data);
                } else if(obj.event === 'edit'){
                    layer.msg('编辑功能暂未实现', {icon: 0});
                } else if(obj.event === 'delete'){
                    layer.confirm('确定要删除该付款人吗？', function(index){
                        // 获取version和payer_id
                        var version = data.version;
                        var payer_id = data.payer_id;
                        
                        // 检查必要参数是否存在
                        if (!version || !payer_id) {
                            layer.msg('缺少必要的参数(version或payer_id)', {icon: 2});
                            layer.close(index);
                            return;
                        }
                        
                        // 显示加载中
                        var loadIndex = layer.load(2);
                        
                        // 发送删除请求
                        $.ajax({
                            url: '/payers/delete',
                            type: 'DELETE',
                            contentType: 'application/json',
                            data: JSON.stringify({
                                version: version,
                                payer_id: payer_id
                            }),
                            success: function(res) {
                                layer.close(loadIndex);
                                if (res.code === 0) {
                                    layer.msg(res.msg || '删除成功', {icon: 1});
                                    // 删除成功后重新加载表格
                                    table.reload('payer-table');
                                } else {
                                    layer.msg(res.msg || '删除失败', {icon: 2});
                                }
                            },
                            error: function(xhr) {
                                layer.close(loadIndex);
                                console.error('删除付款人请求失败:', xhr);
                                layer.msg('网络错误，请稍后重试', {icon: 2});
                            },
                            complete: function() {
                                layer.close(index); // 关闭确认框
                            }
                        });
                    });
                }
            });
            
            // 监听搜索表单提交
            form.on('submit(formSearch)', function(data){
                var formData = data.field;
                console.log("搜索表单提交，数据：", formData);
                
                // 根据表单数据筛选付款人记录
                var filteredData = transformedData.filter(function(item) {
                    // 按姓名搜索
                    if (formData.name && item.full_name && !item.full_name.toLowerCase().includes(formData.name.toLowerCase())) {
                        return false;
                    }
                    // 按平台号搜索
                    if (formData.version && item.version && item.version !== '--' && item.version !== formData.version) {
                        return false;
                    }
                    return true;
                });
                
                console.log("筛选后数据条数：", filteredData.length);
                
                // 重新加载表格数据
                table.reload('payer-table', {
                    data: filteredData,
                    url: null,
                    page: {
                        curr: 1
                    }
                });
                
                return false; // 阻止表单默认提交
            });
        }
        
        // 初始化页面
        initForm();
        initPayersTable();
        initEventListeners();
        
    } catch (error) {
        console.error("初始化付款人页面时发生错误:", error);
        layer.msg('页面初始化失败: ' + error.message, {icon: 2});
    }
});
