/**
 * 添加付款人页面脚本
 * 处理表单交互、图片上传、数据提交等
 */

layui.use(['form', 'layer', 'upload', 'laydate'], function(){
    var form = layui.form;
    var layer = layui.layer;
    var upload = layui.upload;
    var laydate = layui.laydate;
    var $ = layui.jquery;
    
    // 立即执行表单渲染
    form.render();
    
    // 检查表单是否正确初始化
    console.log("付款人表单初始化...");
    console.log("表单元素是否存在:", $('#payer-form').length > 0);
    console.log("提交按钮是否存在:", $('button[lay-filter="payer-submit"]').length > 0);
    
    // 业务范围映射表 - 用于显示中文标签
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
    
    // 存储上传的证件图片信息
    var certFiles = [];
    var businessFiles = [];
    var selectedScopes = [];
    
    // 查找当前弹窗的上下文
    var $form = $('#payer-form');
    var $container = $form.closest('.payer-add-container');

    // 初始化日期选择器
    laydate.render({
        elem: '#birthday',
        format: 'yyyy-MM-dd'
    });
    
    // 初始化取消按钮事件
    $('#cancel-btn').on('click', function() {
        // 找到当前弹出层的索引并关闭
        var index = parent.layer.getFrameIndex(window.name);
        if (index) {
            parent.layer.close(index);
        } else {
            // 如果不是在iframe中，尝试关闭弹窗
            parent.layer.closeAll();
        }
    });
    
    // 监听付款人类型切换
    form.on('radio(subject_type)', function(data){
        if(data.value === 'INDIVIDUAL') {
            $('#individual-section').show();
            $('#enterprise-section').hide();
            
            // 重置企业相关字段的验证
            $('input[name="company_name"]').attr('lay-verify', '');
            $('input[name="register_number"]').attr('lay-verify', '');
            $('#business-scope-select').attr('lay-verify', '');
            
            // 设置个人相关字段的验证
            $('input[name="first_name"]').attr('lay-verify', 'required');
            $('input[name="last_name"]').attr('lay-verify', 'required');
            $('select[name="cert_type"]').attr('lay-verify', 'required');
            $('input[name="cert_number"]').attr('lay-verify', 'required');
            $('input[name="birthday"]').attr('lay-verify', 'required');
            $('select[name="region"]').attr('lay-verify', 'required');
        } else {
            $('#individual-section').hide();
            $('#enterprise-section').show();
            
            // 重置个人相关字段的验证
            $('input[name="first_name"]').attr('lay-verify', '');
            $('input[name="last_name"]').attr('lay-verify', '');
            $('select[name="cert_type"]').attr('lay-verify', '');
            $('input[name="cert_number"]').attr('lay-verify', '');
            $('input[name="birthday"]').attr('lay-verify', '');
            $('select[name="region"]').attr('lay-verify', '');
            
            // 设置企业相关字段的验证
            $('input[name="company_name"]').attr('lay-verify', 'required');
            $('input[name="register_number"]').attr('lay-verify', 'required');
            $('#business-scope-select').attr('lay-verify', 'required');
        }
        
        form.render(); // 重新渲染表单
    });
    
    // 业务范围选择处理
    $('#business-scope-select').on('change', function() {
        var value = $(this).val();
        if (!value) return;
        
        // 检查是否已经选择了该项
        if (!selectedScopes.includes(value)) {
            selectedScopes.push(value);
            
            // 添加标签到已选择区域
            var tagHtml = `
                <div class="scope-tag" data-value="${value}">
                    <span class="scope-tag-text">${businessScopeMap[value] || value}</span>
                    <i class="layui-icon layui-icon-close scope-tag-close"></i>
                </div>
            `;
            $('#selected-scopes').append(tagHtml);
        }
        
        // 重置选择框
        $(this).val('');
        form.render('select');
    });
    
    // 删除业务范围标签
    $(document).on('click', '.scope-tag-close', function() {
        var tag = $(this).parent();
        var value = tag.data('value');
        
        // 从数组中移除
        selectedScopes = selectedScopes.filter(item => item !== value);
        
        // 移除标签
        tag.remove();
    });
    
    // 个人证件上传
    upload.render({
        elem: '#cert-upload',
        url: '', // 不使用默认上传
        auto: false,
        choose: function(obj) {
            // 判断是否超过限制
            if (certFiles.length >= 2) {
                layer.msg('最多只能上传2张证件图片', {icon: 2});
                return;
            }
            
            obj.preview(function(index, file, result) {
                // 将文件信息添加到数组
                var fileInfo = {
                    file: file,
                    base64: result.replace(/^data:image\/\w+;base64,/, '')
                };
                certFiles.push(fileInfo);
                
                // 添加预览
                var previewHtml = `
                    <div class="cert-item" data-index="${certFiles.length - 1}">
                        <img src="${result}" alt="证件图片" class="cert-img">
                        <div class="cert-delete" data-type="cert" data-index="${certFiles.length - 1}">×</div>
                    </div>
                `;
                $('#cert-preview').append(previewHtml);
                
                // 如果已经上传了两张图片，禁用上传按钮
                if (certFiles.length >= 2) {
                    $('#cert-upload').css('opacity', '0.5').css('cursor', 'not-allowed');
                }
            });
        }
    });
    
    // 企业证明文件上传
    upload.render({
        elem: '#business-upload',
        url: '', // 不使用默认上传
        auto: false,
        choose: function(obj) {
            // 判断是否超过限制
            if (businessFiles.length >= 2) {
                layer.msg('最多只能上传2张注册证明文件', {icon: 2});
                return;
            }
            
            obj.preview(function(index, file, result) {
                // 将文件信息添加到数组
                var fileInfo = {
                    file: file,
                    base64: result.replace(/^data:image\/\w+;base64,/, '')
                };
                businessFiles.push(fileInfo);
                
                // 添加预览
                var previewHtml = `
                    <div class="cert-item" data-index="${businessFiles.length - 1}">
                        <img src="${result}" alt="证明文件" class="cert-img">
                        <div class="cert-delete" data-type="business" data-index="${businessFiles.length - 1}">×</div>
                    </div>
                `;
                $('#business-preview').append(previewHtml);
                
                // 如果已经上传了两张图片，禁用上传按钮
                if (businessFiles.length >= 2) {
                    $('#business-upload').css('opacity', '0.5').css('cursor', 'not-allowed');
                }
            });
        }
    });
    
    // 删除上传的图片
    $(document).on('click', '.cert-delete', function() {
        var type = $(this).data('type');
        var index = $(this).data('index');
        
        if (type === 'cert') {
            certFiles.splice(index, 1);
            // 重新生成预览
            refreshCertPreview();
            // 如果删除后图片数小于2，重新启用上传按钮
            if (certFiles.length < 2) {
                $('#cert-upload').css('opacity', '1').css('cursor', 'pointer');
            }
        } else if (type === 'business') {
            businessFiles.splice(index, 1);
            // 重新生成预览
            refreshBusinessPreview();
            // 如果删除后图片数小于2，重新启用上传按钮
            if (businessFiles.length < 2) {
                $('#business-upload').css('opacity', '1').css('cursor', 'pointer');
            }
        }
    });
    
    // 刷新个人证件预览
    function refreshCertPreview() {
        $('#cert-preview').empty();
        certFiles.forEach(function(item, index) {
            var previewHtml = `
                <div class="cert-item" data-index="${index}">
                    <img src="data:image/png;base64,${item.base64}" alt="证件图片" class="cert-img">
                    <div class="cert-delete" data-type="cert" data-index="${index}">×</div>
                </div>
            `;
            $('#cert-preview').append(previewHtml);
        });
        
        // 根据图片数量更新上传按钮状态
        if (certFiles.length >= 2) {
            $('#cert-upload').css('opacity', '0.5').css('cursor', 'not-allowed');
        } else {
            $('#cert-upload').css('opacity', '1').css('cursor', 'pointer');
        }
    }
    
    // 刷新企业证明文件预览
    function refreshBusinessPreview() {
        $('#business-preview').empty();
        businessFiles.forEach(function(item, index) {
            var previewHtml = `
                <div class="cert-item" data-index="${index}">
                    <img src="data:image/png;base64,${item.base64}" alt="证明文件" class="cert-img">
                    <div class="cert-delete" data-type="business" data-index="${index}">×</div>
                </div>
            `;
            $('#business-preview').append(previewHtml);
        });
        
        // 根据图片数量更新上传按钮状态
        if (businessFiles.length >= 2) {
            $('#business-upload').css('opacity', '0.5').css('cursor', 'not-allowed');
        } else {
            $('#business-upload').css('opacity', '1').css('cursor', 'pointer');
        }
    }
    
    // 上传证件图片文件
    function uploadCertFile(file, version) {
        return new Promise(function(resolve, reject) {
            var fileData = {
                type: "CERT_FILE",
                filename: file.file.name,
                base64: file.base64,
                version: version
            };
            
            console.log("准备上传文件:", fileData.filename);
            
            $.ajax({
                url: '/payers/upload_file',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(fileData),
                success: function(res) {
                    console.log("文件上传响应:", res);
                    if (res.code === 0 && res.data) {
                        // 修正file_id的访问路径
                        const fileId = res.data.data.file_id;
                        console.log("成功获取file_id:", fileId);
                        resolve(fileId);
                    } else {
                        console.error("上传文件成功但未获取到file_id:", res);
                        reject(res.msg || '上传文件成功但未获取到file_id');
                    }
                },
                error: function(xhr) {
                    console.error("上传文件请求失败:", xhr);
                    reject('网络错误，请稍后重试');
                }
            });
        });
    }
    
    // 统一的表单提交处理函数
    function handleFormSubmit(formData) {
        var subject_type = formData.subject_type;
        var version = formData.version;
        
        console.log("开始处理表单提交, 数据:", formData);
        
        // 表单验证
        if (!formData.address_country || !formData.address_state || !formData.address_city || 
            !formData.address_detail || !formData.address_postcode) {
            layer.msg('请填写完整的地址信息', {icon: 2});
            return false;
        }
        
        if (subject_type === 'INDIVIDUAL') {
            if (!formData.first_name || !formData.last_name || !formData.cert_type || 
                !formData.cert_number || !formData.birthday || !formData.region) {
                layer.msg('请填写完整的个人信息', {icon: 2});
                return false;
            }
            
            if (certFiles.length === 0) {
                layer.msg('请上传证件图片', {icon: 2});
                return false;
            }
        } else {
            if (!formData.company_name || !formData.register_number) {
                layer.msg('请填写完整的企业信息', {icon: 2});
                return false;
            }
            
            if (selectedScopes.length === 0) {
                layer.msg('请选择业务范围', {icon: 2});
                return false;
            }
            
            if (businessFiles.length === 0) {
                layer.msg('请上传注册证明文件', {icon: 2});
                return false;
            }
        }
        
        // 显示加载层
        var loadingIndex = layer.load(2, {
            shade: [0.3, '#000'],
            content: '正在提交数据，请稍候...',
            success: function(layero) {
                layero.find('.layui-layer-content').css({
                    'padding-top': '40px',
                    'width': '150px'
                });
            }
        });
        
        // 准备上传图片
        var filesToUpload = subject_type === 'INDIVIDUAL' ? certFiles : businessFiles;
        var uploadPromises = [];
        
        console.log("准备上传", filesToUpload.length, "个文件");
        
        // 上传所有图片文件
        filesToUpload.forEach(function(file) {
            uploadPromises.push(uploadCertFile(file, version));
        });
        
        // 处理所有图片上传
        Promise.all(uploadPromises)
            .then(function(fileIds) {
                console.log('所有文件上传成功，fileIds:', fileIds);
                
                // 检查是否有未定义或null的文件ID
                if (fileIds.some(id => id === undefined || id === null)) {
                    throw new Error('有文件未成功获取ID');
                }
                
                // 构建付款人数据
                var payerData = {
                    subject_type: subject_type,
                    version: version,
                    address: {
                        country: formData.address_country,
                        state: formData.address_state,
                        city: formData.address_city,
                        address: formData.address_detail,
                        postcode: formData.address_postcode
                    }
                };
                
                // 根据付款人类型添加不同字段
                if (subject_type === 'INDIVIDUAL') {
                    // 个人信息
                    payerData.first_name = formData.first_name;
                    payerData.last_name = formData.last_name;
                    payerData.cert_type = formData.cert_type;
                    payerData.cert_number = formData.cert_number;
                    payerData.birthday = formData.birthday;
                    payerData.region = formData.region;
                    payerData.cert_files = fileIds;
                } else {
                    // 企业信息
                    payerData.company_name = formData.company_name;
                    payerData.register_number = formData.register_number;
                    payerData.business_scopes = selectedScopes;
                    payerData.cert_files = fileIds;
                }
                
                console.log("提交付款人数据:", payerData);
                
                // 修改加载提示，使用更明显的加载指示器
                layer.close(loadingIndex);
                loadingIndex = layer.load(1, {
                    shade: [0.5, '#000'],
                    area: ['300px', '200px'],
                    content: '<div style="padding: 40px; line-height: 24px; color: #fff; text-align: center;">正在创建付款人，请耐心等待...<br><br><i class="layui-icon layui-icon-loading layui-anim layui-anim-rotate layui-anim-loop" style="font-size: 30px;"></i></div>',
                    success: function(layero) {
                        layero.find('.layui-layer-content').css({
                            'padding': '20px',
                            'text-align': 'center',
                            'background-color': 'rgba(0,0,0,0.7)',
                            'color': '#fff',
                            'border-radius': '10px',
                            'font-size': '16px'
                        });
                    }
                });
                
                // 提交付款人信息，简化为单一AJAX请求
                $.ajax({
                    url: '/payers/add',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(payerData),
                    // 不设置超时，等待直到服务器响应
                    success: function(res) {
                        layer.close(loadingIndex); // 关闭加载层
                        console.log("提交成功，服务器响应:", res);
                        
                        if (res && res.code === 0) {
                            layer.msg('添加付款人成功', {icon: 1, time: 2000}, function() {
                                // 关闭当前iframe层
                                var index = parent.layer.getFrameIndex(window.name);
                                if (index) {
                                    parent.layer.close(index);
                                } else {
                                    // 如果不是在iframe中，尝试关闭弹窗
                                    parent.layer.closeAll();
                                }
                            });
                        } else {
                            layer.msg(res.msg || '添加付款人失败', {icon: 2});
                        }
                    },
                    error: function(xhr, status, error) {
                        layer.close(loadingIndex); // 关闭加载层
                        console.error("请求发生错误:", xhr, status, error);
                        layer.msg('网络请求错误，请稍后重试', {icon: 2});
                    }
                });
                
                return false; // 防止Promise链继续执行
            })
            .catch(function(error) {
                layer.closeAll(); // 关闭所有加载层
                console.error("处理过程中出错:", error);
                layer.msg(error.message || error || '处理过程中出错', {icon: 2});
            });
            
        return false; // 阻止表单默认提交
    }
    
    // 原始的表单提交事件处理
    form.on('submit(payer-submit)', function(data) {
        console.log("表单提交事件触发");
        return handleFormSubmit(data.field);
    });

    // 添加直接的按钮点击事件，以防layui事件没有正确绑定
    $(document).on('click', '#submit-btn', function() {
        console.log("提交按钮直接点击事件");
        var formData = form.val('payer-form');
        return handleFormSubmit(formData);
    });
}); 