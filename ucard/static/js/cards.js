/**
 * 所有卡管理页面专用脚本
 * 用于处理所有卡表格的渲染，搜索，分页功能
 */

layui.use(['table', 'form', 'laydate', 'layer', 'dropdown'], function () {
    var table = layui.table; //表格
    var form = layui.form;  //表单
    var laydate = layui.laydate;  //日期
    var layer = layui.layer;  //弹出层
    var $ = layui.jquery; // jQuery

    try{
        //获取后端数据
        var cardsdataElement = document.getElementById('cards-data');
        var cardholderdataElement = document.getElementById('card-holders-data');
        if (!cardsdataElement && !cardholderdataElement) {
            console.error("找不到数据元素 #cardsdata 或 #card-holders-data");
            layer.msg('数据加载失败：找不到数据元素', {icon: 2});
            return;
        }
        var cardsText = cardsdataElement.textContent;
        var cardholdersText = cardholderdataElement.textContent;
        if (!cardsText || cardsText.trim() === '' || !cardholdersText || cardholdersText.trim() === '') {
            console.error("数据元素内容为空");
            layer.msg('数据加载失败：数据为空', {icon: 2});
            return;
        }
        var cardsData = JSON.parse(cardsText);
        var cardholdersData = JSON.parse(cardholdersText);

        console.log("卡数据:", cardsData);
        console.log("用卡人数据:", cardholdersData);

        if (!cardsData && !cardholdersData) {
            console.warn("数据为null或undefined,初始化为空数组");
            cardsData = [];
            cardholdersData = [];
        }
        
        // 初始化表单组件
        function initForm() {
            // 初始化用卡人下拉菜单
            var cardHolderSelect = document.getElementById('card_holder_select');
            if (cardHolderSelect && cardholdersData && cardholdersData.length > 0) {
                // 清空现有选项（保留全部选项）
                while (cardHolderSelect.options.length > 1) {
                    cardHolderSelect.remove(1);
                }
                
                // 添加用卡人选项
                cardholdersData.forEach(function(holder) {
                    var option = document.createElement('option');
                    option.value = holder.card_holder_id;
                    option.text = holder.first_name + holder.last_name;
                    cardHolderSelect.appendChild(option);
                });
            }
            
            // 重新渲染表单元素
            form.render();
            
            // 监听搜索表单提交
            form.on('submit(formSearch)', function(data) {
                // 获取表单数据
                var formData = data.field; 
                console.log("表单搜索条件:", formData);
                
                // 执行搜索，使用本地数据筛选
                var filteredData = cardsData;
                
                // 按卡号后四位筛选
                if (formData.card_last_digits && formData.card_last_digits.trim() !== '') {
                    filteredData = filteredData.filter(function(item) {
                        var cardNumber = item.mask_card_number || '';
                        // 获取卡号后四位并进行精确匹配
                        var lastFourDigits = cardNumber.slice(-4);
                        return lastFourDigits === formData.card_last_digits;
                    });
                }
                
                // 按平台(version)筛选
                if (formData.version && formData.version !== '') {
                    filteredData = filteredData.filter(function(item) {
                        return item.version === formData.version;
                    });
                }
                
                // 按用卡人筛选
                if (formData.card_holder_id && formData.card_holder_id !== '') {
                    filteredData = filteredData.filter(function(item) {
                        return item.card_holder_id === formData.card_holder_id;
                    });
                }
                
                // 重载表格，使用筛选后的数据
                table.reload('cards-table', {
                    data: filteredData,
                    page: {
                        curr: 1  // 重置到第一页
                    }
                });
                
                // 如果没有找到匹配的数据，显示提示
                if (filteredData.length === 0) {
                    layer.msg('未找到符合条件的数据', {icon: 0});
                } else {
                    layer.msg('找到 ' + filteredData.length + ' 条符合条件的数据', {icon: 1});
                }
                
                return false;  // 阻止表单默认提交
            });
        }

        // 计算剩余有效期（月份）
        function calculateRemainingMonths(expire_year, expire_month) {
            if (!expire_year || !expire_month) return 0;
            const now = new Date();
            const currentYear = now.getFullYear();
            const currentMonth = now.getMonth() + 1; // JavaScript月份从0开始
            return (expire_year - currentYear) * 12 + (expire_month - currentMonth);
        }

        // 初始化表格
        function initCardsTable() {
            // 渲染卡表格
            table.render({
                elem: '#cards-table',
                toolbar: '#toolbar_card_list',
                defaultToolbar: ['filter', 'exports'],
                data: cardsData,
                page: true,
                url: null,
                limit: 10,
                limits: [10, 20, 50, 100],
                height: 'auto',
                cols:[[
                    {
                        field: 'mask_card_number', 
                        title: '卡号', 
                        width: 210,
                        align: 'center',
                        templet: function(d) {
                            var currency = d.card_currency || 'USD';
                            var cardNumber = d.mask_card_number || '5258********9110';
                            var cardName = d.card_name || '--';
                            // 生成卡片模板，模仿图片样式
                            return '<div class="list-card">' +
                                   '<span class="card-number">' + cardNumber + '</span>' +
                                   '<div class="card-currency">' + currency + '</div>' +
                                   '</div>';
                        }
                    },
                    {
                        field: 'limits', 
                        title: '可用余额', 
                        width: 140,
                        align: 'center',
                        templet: function(d) {
                            var singleLimit = d.limit_per_transaction || '0.00';
                            var dayLimit = d.limit_per_day || '0.00';
                            var monthLimit = d.limit_per_month || '0.00';
                            return '<div class="limit-info">' +
                                '<div>单笔限额: ' + singleLimit + '</div>' +
                                '<div>日限额: ' + dayLimit + '</div>' +
                                '<div>月限额: ' + monthLimit + '</div>' +
                                '</div>';
                        }
                    },
                    {
                        field: 'name',
                        title: '姓名',
                        width: 150,
                        align: 'center',
                        templet: function(d){
                            return d.first_name + ' ' + d.last_name;
                        }
                    },
                    {
                        field: 'available_balance', 
                        title: '剩余额度', 
                        width: 150,
                        align: 'center',
                        templet: function(d){
                            var balance = d.available_balance || '0.00';
                            var currency = d.card_currency || 'USD';
                            return balance + ' ' + currency;
                        }
                    },
                    {
                        field: 'expire_date', 
                        title: '有效期', 
                        width: 80,
                        align: 'center',
                        templet: function(d) {
                            var months = calculateRemainingMonths(d.expire_year, d.expire_month);
                            return months + '个月';
                        }
                    },
                    {
                        field: 'cards_status', 
                        title: '状态', 
                        width: 80,
                        align: 'center',
                        templet: function(d){
                            var status = d.cards_status || 'INACTIVE';
                            if (status === 'ACTIVE') {
                                return '<span class="layui-badge layui-bg-green">激活</span>';
                            } else if (status === 'FROZEN') {
                                return '<span class="layui-badge layui-bg-orange">冻结</span>';
                            } else {
                                return '<span class="layui-badge layui-bg-gray">未激活</span>';
                            }
                        }
                    },
                    {field: 'create_time', title: '申请时间', width: 180, align: 'center'},
                    {field: 'brand_code', title: '卡组织', width: 100, align: 'center'},
                    {field: 'version', title: '平台', width: 80, align: 'center'},
                    {title: '操作', toolbar: '#card_barTool', width: 150, align: 'center'},
                ]],
                done: function(res){
                    // 确保分页正确显示
                    this.count = cardsData.length;
                    console.log("表格渲染完成，数据条数：", this.count);
                    
                    // 如果没有数据，显示提示
                    if(cardsData.length === 0) {
                        layer.msg('暂无卡数据', {icon: 0});
                    }
                }
            });
        }

        // 初始化事件监听
        function initEventListeners() {
            // 监听表格工具栏事件
            table.on('toolbar(cards-table)', function(obj){
                if (obj.event === 'add_card') {
                    layer.msg('开卡功能待实现', {icon: 0});
                }
            });
            
            // 监听表格行工具条事件
            table.on('tool(cards-table)', function(obj){
                var data = obj.data; // 获得当前行数据
                var layEvent = obj.event; // 获得 lay-event 对应的值
                
                switch(layEvent) {
                    case 'detail':
                        layer.msg('查看详情功能待实现', {icon: 0});
                        break;
                    case 'adjust':
                        layer.msg('调额功能待实现', {icon: 0});
                        break;
                    case 'set_limit':
                        layer.msg('设置限额功能待实现', {icon: 0});
                        break;
                    case 'cancel':
                        layer.confirm('确定要销卡吗？', function(index){
                            layer.msg('销卡功能待实现', {icon: 0});
                            layer.close(index);
                        });
                        break;
                    case 'freeze':
                        layer.confirm('确定要冻结该卡吗？', function(index){
                            layer.msg('冻结功能待实现', {icon: 0});
                            layer.close(index);
                        });
                        break;
                    case 'edit_nickname':
                        layer.prompt({
                            formType: 0,
                            title: '编辑卡昵称',
                            value: data.card_name || ''
                        }, function(value, index){
                            layer.msg('昵称修改功能待实现', {icon: 0});
                            layer.close(index);
                        });
                        break;
                }
            });
        }

        // 初始化所有功能
        initForm();
        initCardsTable();
        initEventListeners();
        
    } catch (error) {
        console.error("初始化过程中发生错误:", error);
        layer.msg('初始化失败: ' + error.message, {icon: 2});
    };
});

