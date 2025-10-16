/**
 * PIN安全验证组件
 * 用于处理关键操作的二次验证
 */

// PIN验证管理器
var PinSecurity = {
    // 检查PIN码设置状态
    checkPinStatus: function(callback) {
        $.ajax({
            url: '/api/security/check_pin_status',
            type: 'GET',
            success: function(res) {
                if (res.code === 0) {
                    callback(null, res.data);
                } else {
                    callback(res.msg, null);
                }
            },
            error: function(xhr, status, error) {
                callback('检查PIN状态失败: ' + error, null);
            }
        });
    },

    // 显示PIN设置弹窗
    showSetupPinDialog: function(callback) {
        layer.open({
            type: 1,
            title: '设置安全PIN码',
            area: ['450px', '350px'],
            content: `
                <div class="pin-setup-container" style="padding: 20px;">
                    <div class="layui-form">
                        <div class="pin-info" style="margin-bottom: 20px; padding: 15px; background: #f0f9ff; border-radius: 4px; border-left: 4px solid #1890ff;">
                            <div style="color: #1890ff; font-weight: bold; margin-bottom: 8px;">
                                <i class="layui-icon layui-icon-tips"></i> 安全提示
                            </div>
                            <div style="color: #666; font-size: 13px; line-height: 1.5;">
                                • PIN码用于验证重要操作（调额、设限、销卡、冻结）<br>
                                • 请设置6位数字PIN码<br>
                                • 连续输错5次将锁定账户10分钟
                            </div>
                        </div>
                        
                        <div class="layui-form-item">
                            <label class="layui-form-label">PIN码</label>
                            <div class="layui-input-block">
                                <input type="password" id="pinInput" placeholder="请输入6位数字PIN码" 
                                       maxlength="6" class="layui-input pin-input" autocomplete="off" value="666666">
                            </div>
                        </div>
                        
                        <div class="layui-form-item">
                            <label class="layui-form-label">确认PIN码</label>
                            <div class="layui-input-block">
                                <input type="password" id="confirmPinInput" placeholder="请再次输入PIN码" 
                                       maxlength="6" class="layui-input pin-input" autocomplete="off" value="666666">
                            </div>
                        </div>
                        
                        <div class="layui-form-item" style="text-align: center; margin-top: 30px;">
                            <button type="button" class="layui-btn" id="setupPinBtn">
                                <i class="layui-icon layui-icon-ok"></i> 设置PIN码
                            </button>
                            <button type="button" class="layui-btn layui-btn-primary" id="cancelSetupBtn">
                                <i class="layui-icon layui-icon-close"></i> 取消
                            </button>
                        </div>
                    </div>
                </div>
                <style>
                    .pin-input {
                        text-align: center;
                        font-size: 18px;
                        letter-spacing: 3px;
                        font-family: 'Courier New', monospace;
                    }
                </style>`,
            success: function(layero, index) {
                // 只允许输入数字
                $('.pin-input').on('input', function() {
                    this.value = this.value.replace(/[^0-9]/g, '');
                });

                // 取消按钮
                $('#cancelSetupBtn').on('click', function() {
                    layer.close(index);
                });

                // 设置PIN码按钮
                $('#setupPinBtn').on('click', function() {
                    var pin = $('#pinInput').val();
                    var confirmPin = $('#confirmPinInput').val();

                    if (!pin || pin.length !== 6) {
                        layer.msg('请输入6位数字PIN码', {icon: 2});
                        return;
                    }

                    if (pin !== confirmPin) {
                        layer.msg('两次输入的PIN码不一致', {icon: 2});
                        return;
                    }

                    // 发送设置请求
                    var loadIndex = layer.load(2);
                    $.ajax({
                        url: '/api/security/setup_pin',
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({pin_code: pin}),
                        success: function(res) {
                            layer.close(loadIndex);
                            if (res.code === 0) {
                                layer.msg('PIN码设置成功', {icon: 1, time: 2000}, function() {
                                    layer.close(index);
                                    if (callback) callback(null, true);
                                });
                            } else {
                                layer.msg(res.msg || 'PIN码设置失败', {icon: 2});
                            }
                        },
                        error: function(xhr, status, error) {
                            layer.close(loadIndex);
                            layer.msg('设置PIN码失败: ' + error, {icon: 2});
                        }
                    });
                });

                // 聚焦到第一个输入框
                $('#pinInput').focus();
            }
        });
    },

    // 显示PIN验证弹窗
    showVerifyPinDialog: function(operationType, cardId, callback) {
        var operationNames = {
            'adjust_balance': '调额',
            'set_limit': '设置限额',
            'cancel_card': '销卡',
            'freeze_card': '冻结卡片',
            'unfreeze_card': '解冻卡片'
        };

        var operationName = operationNames[operationType] || '操作';

        layer.open({
            type: 1,
            title: '安全验证 - ' + operationName,
            area: ['400px', '280px'],
            content: `
                <div class="pin-verify-container" style="padding: 20px;">
                    <div class="layui-form">
                        <div class="operation-info" style="margin-bottom: 20px; text-align: center;">
                            <div style="color: #ff4d4f; font-size: 16px; font-weight: bold; margin-bottom: 8px;">
                                <i class="layui-icon layui-icon-password"></i> 安全验证
                            </div>
                            <div style="color: #666; font-size: 14px;">
                                执行【${operationName}】操作需要验证PIN码
                            </div>
                        </div>
                        
                        <div class="layui-form-item">
                            <label class="layui-form-label">PIN码</label>
                            <div class="layui-input-block">
                                <input type="password" id="verifyPinInput" placeholder="请输入6位PIN码" 
                                       maxlength="6" class="layui-input pin-input" autocomplete="off">
                            </div>
                        </div>
                        
                        <div class="layui-form-item" style="text-align: center; margin-top: 25px;">
                            <button type="button" class="layui-btn layui-btn-danger" id="verifyPinBtn">
                                <i class="layui-icon layui-icon-ok"></i> 验证并执行
                            </button>
                            <button type="button" class="layui-btn layui-btn-primary" id="cancelVerifyBtn">
                                <i class="layui-icon layui-icon-close"></i> 取消
                            </button>
                        </div>
                        
                        <div style="text-align: center; margin-top: 15px; border-top: 1px solid #eee; padding-top: 15px;">
                            <a href="javascript:void(0)" id="resetPinLink" style="color: #999; font-size: 12px;">
                                <i class="layui-icon layui-icon-refresh"></i> 忘记PIN码？点击重置
                            </a>
                        </div>
                    </div>
                </div>
                <style>
                    .pin-input {
                        text-align: center;
                        font-size: 18px;
                        letter-spacing: 3px;
                        font-family: 'Courier New', monospace;
                    }
                </style>`,
            success: function(layero, index) {
                // 只允许输入数字
                $('#verifyPinInput').on('input', function() {
                    this.value = this.value.replace(/[^0-9]/g, '');
                });

                // 回车键提交
                $('#verifyPinInput').on('keypress', function(e) {
                    if (e.which === 13) {
                        $('#verifyPinBtn').click();
                    }
                });

                // 取消按钮
                $('#cancelVerifyBtn').on('click', function() {
                    layer.close(index);
                    if (callback) callback('用户取消操作', false);
                });

                // 重置PIN码链接
                $('#resetPinLink').on('click', function() {
                    layer.close(index);
                    PinSecurity.showResetPinDialog(function(resetError, resetSuccess) {
                        if (resetSuccess) {
                            layer.msg('PIN码已重置，请重新设置', {icon: 1});
                        }
                    });
                });

                // 验证PIN码按钮
                $('#verifyPinBtn').on('click', function() {
                    var pin = $('#verifyPinInput').val();

                    if (!pin || pin.length !== 6) {
                        layer.msg('请输入6位数字PIN码', {icon: 2});
                        return;
                    }

                    // 发送验证请求
                    var loadIndex = layer.load(2);
                    $.ajax({
                        url: '/api/security/verify_pin',
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            pin_code: pin,
                            operation_type: operationType,
                            card_id: cardId
                        }),
                        success: function(res) {
                            layer.close(loadIndex);
                            if (res.code === 0) {
                                layer.close(index);
                                if (callback) callback(null, true);
                            } else {
                                layer.msg(res.msg || 'PIN码验证失败', {icon: 2});
                                // 清空输入框
                                $('#verifyPinInput').val('').focus();
                            }
                        },
                        error: function(xhr, status, error) {
                            layer.close(loadIndex);
                            layer.msg('验证PIN码失败: ' + error, {icon: 2});
                            $('#verifyPinInput').val('').focus();
                        }
                    });
                });

                // 聚焦到输入框
                $('#verifyPinInput').focus();
            }
        });
    },

    // 显示PIN重置弹窗
    showResetPinDialog: function(callback) {
        layer.open({
            type: 1,
            title: '重置安全PIN码',
            area: ['450px', '300px'],
            content: `
                <div class="pin-reset-container" style="padding: 20px;">
                    <div class="layui-form">
                        <div class="reset-info" style="margin-bottom: 20px; padding: 15px; background: #fff2e8; border-radius: 4px; border-left: 4px solid #fa8c16;">
                            <div style="color: #fa8c16; font-weight: bold; margin-bottom: 8px;">
                                <i class="layui-icon layui-icon-about"></i> 重置提示
                            </div>
                            <div style="color: #666; font-size: 13px; line-height: 1.5;">
                                • 重置PIN码需要验证当前登录密码<br>
                                • 重置后需要重新设置新的PIN码<br>
                                • 重置会清除失败次数和锁定状态
                            </div>
                        </div>
                        
                        <div class="layui-form-item">
                            <label class="layui-form-label">当前密码</label>
                            <div class="layui-input-block">
                                <input type="password" id="currentPasswordInput" placeholder="请输入当前登录密码" 
                                       class="layui-input" autocomplete="off">
                            </div>
                        </div>
                        
                        <div class="layui-form-item" style="text-align: center; margin-top: 30px;">
                            <button type="button" class="layui-btn layui-btn-danger" id="resetPinBtn">
                                <i class="layui-icon layui-icon-refresh"></i> 重置PIN码
                            </button>
                            <button type="button" class="layui-btn layui-btn-primary" id="cancelResetBtn">
                                <i class="layui-icon layui-icon-close"></i> 取消
                            </button>
                        </div>
                    </div>
                </div>`,
            success: function(layero, index) {
                // 取消按钮
                $('#cancelResetBtn').on('click', function() {
                    layer.close(index);
                });

                // 回车键提交
                $('#currentPasswordInput').on('keypress', function(e) {
                    if (e.which === 13) {
                        $('#resetPinBtn').click();
                    }
                });

                // 重置PIN码按钮
                $('#resetPinBtn').on('click', function() {
                    var password = $('#currentPasswordInput').val();

                    if (!password) {
                        layer.msg('请输入当前登录密码', {icon: 2});
                        return;
                    }

                    // 发送重置请求
                    var loadIndex = layer.load(2);
                    $.ajax({
                        url: '/api/security/reset_pin',
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({current_password: password}),
                        success: function(res) {
                            layer.close(loadIndex);
                            if (res.code === 0) {
                                layer.msg('PIN码重置成功，请重新设置', {icon: 1, time: 2000}, function() {
                                    layer.close(index);
                                    if (callback) callback(null, true);
                                });
                            } else {
                                layer.msg(res.msg || 'PIN码重置失败', {icon: 2});
                            }
                        },
                        error: function(xhr, status, error) {
                            layer.close(loadIndex);
                            layer.msg('重置PIN码失败: ' + error, {icon: 2});
                        }
                    });
                });

                // 聚焦到密码输入框
                $('#currentPasswordInput').focus();
            }
        });
    },

    // 执行需要PIN验证的操作
    executeSecureOperation: function(operationType, cardId, operationCallback) {
        var self = this;
        
        // 首先检查PIN状态
        this.checkPinStatus(function(error, status) {
            if (error) {
                layer.msg('检查安全状态失败: ' + error, {icon: 2});
                return;
            }

            // 检查是否被锁定
            if (status.is_locked) {
                layer.msg('账户已被锁定，请10分钟后再试', {icon: 2});
                return;
            }

            // 如果没有设置PIN码，先设置
            if (!status.has_pin) {
                layer.confirm('您还未设置安全PIN码，是否现在设置？', {
                    icon: 3,
                    title: '安全提示'
                }, function(index) {
                    layer.close(index);
                    self.showSetupPinDialog(function(setupError, setupSuccess) {
                        if (setupSuccess) {
                            // 设置成功后，继续执行验证
                            self.showVerifyPinDialog(operationType, cardId, function(verifyError, verifySuccess) {
                                if (verifySuccess && operationCallback) {
                                    operationCallback();
                                }
                            });
                        }
                    });
                });
                return;
            }

            // 显示PIN验证弹窗
            self.showVerifyPinDialog(operationType, cardId, function(verifyError, verifySuccess) {
                if (verifySuccess && operationCallback) {
                    operationCallback();
                }
            });
        });
    }
};

// 全局暴露PinSecurity对象
window.PinSecurity = PinSecurity;
