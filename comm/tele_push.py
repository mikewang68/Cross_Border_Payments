import logging
import requests
from comm.utils import get_tele_token
from comm.push_data import get_last_insert_time,upd_last_insert_time,match_last_insert_time,get_new_ins_data,get_db_last_insert_time
from db_api import query_database
from flat_data import flat_messages

class TelegramPusher:
    def __init__(self, log_file="tele_push.log"):
        # 配置日志记录
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

        # 获取 Telegram 机器人 Token
        self.token_data = get_tele_token()
        if not self.token_data:
            self.logger.error("无法获取 Telegram 机器人 Token，消息发送功能不可用。")
            self.bot_token = None
        else:
            self.bot_token = self.token_data.get("bot_token")

    def push_message(self, info: str, chat_id: str):

        if not self.bot_token:
            self.logger.error("未获取到 BOT_TOKEN，无法发送消息。")
            return {"error": "未获取到 BOT_TOKEN"}

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": info}

        try:
            response = requests.post(url, data=data)
            if response.status_code != 200:
                self.logger.error(f"请求失败，状态码: {response.status_code}, 返回内容: {response.text}")
                return {"error": f"请求失败，状态码: {response.status_code}", "response": response.text}
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求异常: {e}")
            return {"error": f"请求异常: {str(e)}"}

tele_pusher = TelegramPusher()

def push_card_transactions ():
    fun = 'card_transactions'
    # 获取最新数据
    last_insert_time = get_last_insert_time(fun)
    # 获取当前db最新数据
    db_last_insert_time = get_db_last_insert_time(fun)
    # 对比当前数据与最新数据
    match_result= match_last_insert_time(last_insert_time,db_last_insert_time)

    if match_result:
        # 获取新插入数据
        new_ins_data_list = get_new_ins_data(fun,'insert_time',db_last_insert_time,'>')

        for new_ins_data in new_ins_data_list:
            card_id = new_ins_data.get('card_id')
            data_insert_time = new_ins_data.get('insert_time')

            card_info = query_database('cards','card_id',card_id)

            if not card_info:

                logging.warning(f"cards表中未找到 card_id：{card_id}，跳过推送。")
                continue

            for card_data in card_info:

                card_holder_id = card_data.get('card_holder_id')

                card_holder_info = query_database('card_holder','card_holder_id',card_holder_id)

                if not card_holder_info:
                    logging.warning(f"未找到 card_holder_id {card_holder_id} 的 card_holder_info，跳过推送。")
                    continue

                for card_holder_data in card_holder_info:

                    chat_id = card_holder_data.get('telegram_id')
                    user_login = card_holder_data.get('user_login')

                    if not chat_id:
                        logging.warning(f"未找到 card_id {card_id} 的 Telegram chat_id，跳过推送。")
                        continue

                    if user_login != 1:
                        logging.warning(f"用户 {card_id} 处于解绑状态，跳过推送。")
                        continue


                    region = card_holder_data.get('region')

                    push_data = [new_ins_data]

                    info = flat_messages(push_data,region)

                    transaction = info[0]

                    push_message = "\n".join([f"{key}: {value}" for key, value in transaction.items()])

                    # 逐条推送信息
                    response = tele_pusher.push_message(push_message, chat_id)

                    if response.get("ok"):
                        logging.info(f"成功向 {chat_id} 发送交易推送: {info}")
                        # 更新最新推送数据
                        upd_last_insert_time(fun, data_insert_time)
                    else:
                        logging.error(f"向 {chat_id} 发送失败: {response}")





