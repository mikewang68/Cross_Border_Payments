// 密码修改功能
layui.use(['form', 'layer'], function() {
    const form = layui.form;
    const layer = layui.layer;
    
    // 调试信息: 显示当前登录用户
    console.log("当前页面用户账号:", document.querySelector('.layui-input[readonly]').value);
    
    // 检查密码强度
    function checkPasswordStrength(password) {
        // 空密码返回0
        if (!password) return 0;
        
        let score = 0;
        
        // 基础长度分数
        if (password.length >= 6) score += 1;
        if (password.length >= 10) score += 1;
        
        // 包含不同类型字符的分数
        if (/[A-Z]/.test(password)) score += 1;
        if (/[a-z]/.test(password)) score += 1;
        if (/[0-9]/.test(password)) score += 1;
        if (/[^A-Za-z0-9]/.test(password)) score += 1;
        
        // 返回强度等级：0-弱，1-中，2-强
        if (score >= 5) return 2;  // 强
        if (score >= 3) return 1;  // 中
        return 0;  // 弱
    }
    
    // 更新密码强度UI
    function updateStrengthUI(strength) {
        const strengthBars = document.querySelector('.strength-bars');
        const strengthText = document.getElementById('strengthText');
        
        // 重置所有样式
        strengthBars.classList.remove('strength-weak', 'strength-medium', 'strength-strong');
        
        if (strength === 0) {
            strengthBars.classList.add('strength-weak');
            strengthText.textContent = '弱';
            strengthText.style.color = '#ff5252';
        } else if (strength === 1) {
            strengthBars.classList.add('strength-medium');
            strengthText.textContent = '中';
            strengthText.style.color = '#ffa726';
        } else {
            strengthBars.classList.add('strength-strong');
            strengthText.textContent = '强';
            strengthText.style.color = '#4caf50';
        }
    }
    
    // 新密码输入事件监听
    document.getElementById('newPassword').addEventListener('input', function() {
        const strength = checkPasswordStrength(this.value);
        updateStrengthUI(strength);
    });
    
    // 表单提交处理
    document.getElementById('submitBtn').addEventListener('click', function() {
        const oldPassword = document.getElementById('oldPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        // 表单验证
        if (!oldPassword || !newPassword || !confirmPassword) {
            layer.msg('请填写所有必填字段', {icon: 2});
            return;
        }
        
        // 检查密码匹配
        if (newPassword !== confirmPassword) {
            layer.msg('两次输入的新密码不一致', {icon: 2});
            return;
        }
        
        // 检查密码长度
        if (newPassword.length < 6) {
            layer.msg('新密码长度不能少于6位', {icon: 2});
            return;
        }
        
        // 检查密码复杂性
        const strength = checkPasswordStrength(newPassword);
        if (strength === 0) {
            layer.confirm('您的密码强度较弱，是否继续提交？', {
                btn: ['继续提交', '取消'],
                icon: 3
            }, function(index) {
                submitPasswordChange();
                layer.close(index);
            });
        } else {
            submitPasswordChange();
        }
    });
    
    // 提交密码修改请求
    function submitPasswordChange() {
        const loadingIndex = layer.load(1, {
            shade: [0.1, '#fff']
        });
        
        // 获取表单数据
        const data = {
            old_password: document.getElementById('oldPassword').value,
            new_password: document.getElementById('newPassword').value,
            confirm_password: document.getElementById('confirmPassword').value
        };
        
        console.log("正在提交密码修改请求:", data);
        
        // 发送AJAX请求
        fetch('/change_password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(data),
            credentials: 'same-origin' // 确保发送session cookie
        })
        .then(response => {
            console.log("收到响应状态:", response.status);
            return response.json();
        })
        .then(result => {
            console.log("服务器响应:", result);
            layer.close(loadingIndex);
            
            if (result.code === 0) {
                layer.msg(result.msg, {icon: 1, time: 2000}, function() {
                    // 密码修改成功，重置表单
                    document.getElementById('passwordForm').reset();
                    // 重置密码强度指示器
                    updateStrengthUI(0);
                });
            } else {
                layer.msg(result.msg, {icon: 2});
            }
        })
        .catch(error => {
            console.error('请求错误:', error);
            layer.close(loadingIndex);
            layer.msg('网络错误，请稍后重试', {icon: 2});
        });
    }
}); 