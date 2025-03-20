/**
 * 所有卡管理页面专用脚本
 * 用于处理所有卡表格的渲染，搜索，分页功能
 */

layui.use(['table', 'form', 'laydate'], function () {
    var table = layui.table; //表格
    var form = layui.form;  //表单
    var laydate = layui.laydate;  //日期

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
            // 重新渲染表单元素
            form.render();
        }

        // 初始化表格
        function initCardsTable() {
            // 渲染用卡人表格
            table.render({
                elem: '#cards-table',
                toolbar: 'toolbar_cards',
                defaultToolbar: ['filter', 'exports'],
                data: cardsData,
                page: true,
                url: null,
                limit: 10,
                litmits: [10, 20, 30],
                height: 'full-200',
                cols:[[
                    {field: 'card_id', title: 'ID', width: 250},
                    {field: 'available_balance', title: '剩余额度', width: 120},
                    {field: 'available_balance', title: '剩余额度', width: 120},  
                    {field: 'status', title: '状态', width: 80, templet: function(d){
                        return d.status === 'ACTIVE' ? '<span class="layui-badge layui-bg-green">激活</span>' : '<span class="layui-badge layui-bg-gray">未激活</span>';
                    }},
                    {field: 'holder_id', title: '用卡人ID', width: 120},  
                ]],
            });
        }

        
    } catch (error) {
        console.error("初始化过程中发生错误:", error);
        layer.msg('初始化失败: ' + error.message, {icon: 2});
    }
});
