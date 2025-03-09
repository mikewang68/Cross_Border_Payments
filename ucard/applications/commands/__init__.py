def init_commands(app):
    """注册所有CLI命令"""
    # 在这里导入所有命令模块
    from applications.commands import init_db

    # 初始化所有命令
    init_db.init_app(app) 