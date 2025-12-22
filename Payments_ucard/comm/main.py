@main_bp.route('/api/get_all_systems', methods=['GET'])
@login_required
def api_get_all_systems():
    try:
        # 查询所有平台数据
        systems = query_all_from_table('system_key')
        
        # 确保返回的数据是列表格式
        if systems is None:
            systems = []
        
        # 调试日志
        print(f"查询到 {len(systems)} 条平台数据")
        
        return jsonify({
            'code': 0,
            'msg': '获取平台列表成功',
            'data': systems
        })
    except Exception as e:
        print(f"获取平台列表时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}',
            'data': []
        })


@main_bp.route('/api/delete_system', methods=['POST'])
@login_required
def api_delete_system():
    try:
        data = request.get_json()
        system_id = data.get('id')
        
        if not system_id:
            return jsonify({
                'code': 1,
                'msg': '平台ID不能为空'
            })
        
        # 删除平台数据
        result = delete_from_table('system_key', {'id': system_id})
        
        if result:
            return jsonify({
                'code': 0,
                'msg': '删除平台成功'
            })
        else:
            return jsonify({
                'code': 1,
                'msg': '删除平台失败'
            })
    except Exception as e:
        print(f"删除平台时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}'
        })


@main_bp.route('/api/update_system', methods=['POST'])
@login_required
def api_update_system():
    try:
        data = request.get_json()
        system_id = data.get('id')
        
        if not system_id:
            return jsonify({
                'code': 1,
                'msg': '平台ID不能为空'
            })
        
        # 更新数据
        update_data = {
            'appid': data.get('appid'),
            'key': data.get('key'),
            'system': data.get('system')
        }
        
        # 更新平台数据
        result = update_database('system_key', {'id': system_id}, update_data)
        
        if result:
            return jsonify({
                'code': 0,
                'msg': '更新平台成功'
            })
        else:
            return jsonify({
                'code': 1,
                'msg': '更新平台失败'
            })
    except Exception as e:
        print(f"更新平台时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}'
        })


@main_bp.route('/api/add_system', methods=['POST'])
@login_required
def api_add_system():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 1,
                'msg': '请求数据为空'
            })
            
        appid = data.get('appid')
        key = data.get('key')
        system = data.get('system')
        
        if not appid or not key or not system:
            return jsonify({
                'code': 1,
                'msg': '平台信息不完整，请填写所有必填项'
            })
        
        # 检查是否已存在相同的平台
        existing_systems = query_all_from_table('system_key', {'system': system})
        if existing_systems and len(existing_systems) > 0:
            return jsonify({
                'code': 1,
                'msg': '该平台名称已存在'
            })
            
        # 检查AppID是否已存在
        existing_appids = query_all_from_table('system_key', {'appid': appid})
        if existing_appids and len(existing_appids) > 0:
            return jsonify({
                'code': 1,
                'msg': '该平台ID已存在'
            })
        
        # 插入新平台数据
        insert_data = {
            'appid': appid,
            'key': key,
            'system': system
        }
        
        print(f"准备插入平台数据: {insert_data}")  # 调试日志
        
        result = insert_database('system_key', insert_data)
        if result:
            print(f"平台数据插入成功: {system}")  # 调试日志
            return jsonify({
                'code': 0,
                'msg': '添加平台成功'
            })
        else:
            print(f"平台数据插入失败: {system}")  # 调试日志
            return jsonify({
                'code': 1,
                'msg': '添加平台失败'
            })
            
    except Exception as e:
        print(f"添加平台时出错: {str(e)}")
        return jsonify({
            'code': 1,
            'msg': f'系统错误: {str(e)}'
        }) 