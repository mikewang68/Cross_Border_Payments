from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import Update
from utils.logging import logger
from handlers.command import start_command
from handlers.callbacks import language_select_callback,button_callback,binding_email_callback, handle_callback_query
from handlers.message import message_handler
from typing import Final

# 配置
# TOKEN: Final = '7713911597:AAGYtbnzDaiHITabbORksDRSFuWkUUcub_k'
# BOT_USERNAME: Final = "@GsalaryBot"

# 配置 TOKEN
TOKEN: Final = '7784427552:AAHw2OU1VjEskj_jgdoYxQkNIxeJ8yhRvkA'


# 设置代理和超时
PROXY:Final = "http://127.0.0.1:7890"  # 改用 http 代理，端口号要根据你的实际代理软件设置


def main():
    """启动机器人"""

    logger.info("正在启动机器人...")
    try:
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # 如果不设置代理使用这个,且注释掉 PROXY:Final = "http://127.0.0.1:7890"
        # app = Application.builder().token(TOKEN).build()
        # 设置代理请使用这个app
        app = (
            Application.builder()
            .token(TOKEN)
            .proxy(PROXY)
            .get_updates_proxy(PROXY)
            .connect_timeout(30.0)
            .read_timeout(30.0)
            .build()
        )
        
        # 添加处理程序
        app.add_handler(CommandHandler("start", start_command))
   
        app.add_handler(CallbackQueryHandler(
                language_select_callback,
                pattern="^(language_en_button|language_jp_button|language_zhcn_button|language_zhtw_button|back_language_select|proceed)$"
            )
        )

        app.add_handler(CallbackQueryHandler(
                binding_email_callback,
                pattern="^(failed_after_language_selection|verification_after_language_selection)$"
            )
        )

        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        ))

        app.add_handler(CallbackQueryHandler(button_callback, pattern="^(login_button|help_button)$"))

        app.add_handler(CallbackQueryHandler(handle_callback_query))
        
        logger.info("机器人启动成功！")
        app.run_polling(allowed_updates= Update.ALL_TYPES, drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"机器人启动失败！错误信息：{str(e)}")
        raise e

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n检测到 Ctrl+C,正在关闭机器人...")
    except Exception as e:
        print(f"发生错误：{str(e)}")
    finally:
        print("机器人已关闭.") 