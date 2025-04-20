from flask import jsonify
from datetime import datetime, timedelta
from comm.db_api import query_all_from_table
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_daily_report(date=None, platform=None):
    """
    获取日报数据的API接口
    
    参数:
    date (str): 日期，格式为 YYYY-MM-DD，不传则返回所有日期的数据
    platform (str): 平台类型，不传则返回所有平台的数据
    
    返回:
    dict: 包含日报数据的字典
    """
    try:
        # 查询数据
        cards = query_all_from_table('cards')
        wallet_transactions = query_all_from_table('wallet_transactions')
        card_transactions = query_all_from_table('card_transactions')
        
        logger.info(f"原始数据: 卡片数量={len(cards) if cards else 0}, 钱包交易数量={len(wallet_transactions) if wallet_transactions else 0}, 卡交易数量={len(card_transactions) if card_transactions else 0}")
        
        # 日期过滤
        if date:
            try:
                target_date = datetime.strptime(date, '%Y-%m-%d').date()
                
                # 过滤卡片数据
                cards = [card for card in cards if card.get('create_time') and 
                         datetime.strptime(card['create_time'].split('T')[0], '%Y-%m-%d').date() == target_date]
                
                # 过滤钱包交易数据
                wallet_transactions = [trans for trans in wallet_transactions if trans.get('transaction_time') and 
                                      datetime.strptime(trans['transaction_time'].split('T')[0], '%Y-%m-%d').date() == target_date]
                
                # 过滤卡交易数据
                card_transactions = [trans for trans in card_transactions if trans.get('transaction_time') and 
                                    datetime.strptime(trans['transaction_time'].split('T')[0], '%Y-%m-%d').date() == target_date]
            except ValueError:
                return jsonify({'error': '日期格式无效，请使用YYYY-MM-DD格式'}), 400
        
        # 平台过滤
        if platform:
            cards = [card for card in cards if card.get('version') == platform]
            wallet_transactions = [trans for trans in wallet_transactions if trans.get('version') == platform]
            card_transactions = [trans for trans in card_transactions if trans.get('version') == platform]
        
        logger.info(f"过滤后数据(日期={date}, 平台={platform}): 卡片数量={len(cards)}, 钱包交易数量={len(wallet_transactions)}, 卡交易数量={len(card_transactions)}")
        
        # 计算开卡数
        card_count = len(cards)
        
        # 计算消费总额（按币种分组）
        total_amount_by_currency = {}
        for trans in card_transactions:
            if trans.get('accounting_amount') and trans.get('accounting_amount_currency'):
                amount = float(trans['accounting_amount'])
                currency = trans['accounting_amount_currency']
                if currency not in total_amount_by_currency:
                    total_amount_by_currency[currency] = 0
                total_amount_by_currency[currency] += amount
        
        # 格式化消费总额
        total_amount = []
        for currency, amount in total_amount_by_currency.items():
            total_amount.append({
                'currency': currency,
                'amount': amount
                
            })
        
        # 确保至少有一个货币的消费总额（即使没有数据）
        if not total_amount:
            total_amount.append({
                'currency': 'USD',
                'amount': 0
            })
        
        # 计算钱包交易笔数
        wallet_trans_count = len(wallet_transactions)
        
        # 计算卡交易笔数
        card_trans_count = len(card_transactions)
        
        # 计算异常交易数和异常交易列表
        error_transactions = [trans for trans in card_transactions 
                              if trans.get('status') in ['FAILED', 'VOID']]
        error_count = len(error_transactions)
        
        # 格式化异常交易列表
        formatted_error_transactions = []
        for trans in error_transactions:
            formatted_error_transactions.append({
                'transaction_time': trans.get('transaction_time'),
                'mask_card_number': trans.get('mask_card_number'),
                'accounting_amount': trans.get('accounting_amount'),
                'accounting_amount_currency': trans.get('accounting_amount_currency'),
                'transaction_amount': trans.get('transaction_amount'),
                'transaction_amount_currency': trans.get('transaction_amount_currency'),
                'biz_type': trans.get('biz_type'),
                'merchant_name': trans.get('merchant_name'),
                'merchant_region': trans.get('merchant_region'),
                'status': trans.get('status'),
                'version': trans.get('version')
            })
        
        # 计算环比数据（与前一天比较）
        trends = {}
        if date:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
            previous_date = target_date - timedelta(days=1)
            previous_date_str = previous_date.strftime('%Y-%m-%d')
            
            # 获取前一天数据
            prev_cards = query_all_from_table('cards')
            prev_wallet_transactions = query_all_from_table('wallet_transactions')
            prev_card_transactions = query_all_from_table('card_transactions')
            
            # 过滤前一天数据
            prev_cards = [card for card in prev_cards if card.get('create_time') and 
                        datetime.strptime(card['create_time'].split('T')[0], '%Y-%m-%d').date() == previous_date]
            
            if platform:
                prev_cards = [card for card in prev_cards if card.get('version') == platform]
            
            prev_wallet_transactions = [trans for trans in prev_wallet_transactions if trans.get('transaction_time') and 
                                    datetime.strptime(trans['transaction_time'].split('T')[0], '%Y-%m-%d').date() == previous_date]
            
            if platform:
                prev_wallet_transactions = [trans for trans in prev_wallet_transactions if trans.get('version') == platform]
            
            prev_card_transactions = [trans for trans in prev_card_transactions if trans.get('transaction_time') and 
                                   datetime.strptime(trans['transaction_time'].split('T')[0], '%Y-%m-%d').date() == previous_date]
            
            if platform:
                prev_card_transactions = [trans for trans in prev_card_transactions if trans.get('version') == platform]
            
            # 计算前一天的消费总额
            prev_total_amount_by_currency = {}
            for trans in prev_card_transactions:
                if trans.get('accounting_amount') and trans.get('accounting_amount_currency'):
                    amount = float(trans['accounting_amount'])
                    currency = trans['accounting_amount_currency']
                    if currency not in prev_total_amount_by_currency:
                        prev_total_amount_by_currency[currency] = 0
                    prev_total_amount_by_currency[currency] += amount
            
            # 计算环比
            prev_card_count = len(prev_cards)
            prev_wallet_trans_count = len(prev_wallet_transactions)
            prev_card_trans_count = len(prev_card_transactions)
            
            # 计算开卡数环比
            card_count_trend = calculate_trend(card_count, prev_card_count)
            
            # 计算钱包交易笔数环比
            wallet_trans_trend = calculate_trend(wallet_trans_count, prev_wallet_trans_count)
            
            # 计算卡交易笔数环比
            card_trans_trend = calculate_trend(card_trans_count, prev_card_trans_count)
            
            # 计算消费总额环比
            amount_trends = []
            for currency, amount in total_amount_by_currency.items():
                prev_amount = prev_total_amount_by_currency.get(currency, 0)
                trend = calculate_trend(amount, prev_amount)
                amount_trends.append({
                    'currency': currency,
                    'trend': trend,
                    'formatted': format_trend(trend)
                })
            
            # 确保至少有一个货币的环比数据
            if not amount_trends:
                amount_trends.append({
                    'currency': 'USD',
                    'trend': 0,
                    'formatted': '0%'
                })
            
            trends = {
                'card_count': {
                    'value': card_count_trend,
                    'formatted': format_trend(card_count_trend)
                },
                'wallet_trans_count': {
                    'value': wallet_trans_trend,
                    'formatted': format_trend(wallet_trans_trend)
                },
                'card_trans_count': {
                    'value': card_trans_trend,
                    'formatted': format_trend(card_trans_trend)
                },
                'total_amount': amount_trends
            }
        
        # 计算消费次数TOP3
        card_stats = {}
        for trans in card_transactions:
            card_number = trans.get('mask_card_number')
            if not card_number:
                continue
                
            if card_number not in card_stats:
                card_stats[card_number] = {
                    'count': 0,
                    'total_amount': 0,
                    'currencies': {}  # 改为空字典，后面会确保不为空
                }
                
            card_stats[card_number]['count'] += 1
            
            if trans.get('accounting_amount'):
                try:
                    amount = float(trans['accounting_amount'])
                    currency = trans.get('accounting_amount_currency', 'USD')  # 如果没有币种，默认使用USD
                    
                    if currency not in card_stats[card_number]['currencies']:
                        card_stats[card_number]['currencies'][currency] = 0
                        
                    card_stats[card_number]['currencies'][currency] += amount
                    card_stats[card_number]['total_amount'] += amount
                except (ValueError, TypeError):
                    # 如果金额转换失败，记录日志但继续处理
                    logger.warning(f"Invalid accounting_amount value: {trans.get('accounting_amount')} for card {card_number}")
        
        # 记录日志，帮助调试
        logger.info(f"根据筛选条件(日期:{date}, 平台:{platform})找到 {len(card_stats)} 张卡的消费数据")
        
        # 转换为列表并排序
        card_stats_list = []
        for card_number, stats in card_stats.items():
            currencies_formatted = []
            # 确保currencies不为空，至少有一个USD币种
            if not stats['currencies']:
                stats['currencies'] = {'USD': 0}
                
            for currency, amount in stats['currencies'].items():
                currencies_formatted.append({
                    'currency': currency,
                    'amount': amount,
                    'formatted': f"{amount:.2f} {currency}"
                })
                
            card_stats_list.append({
                'card_number': card_number,
                'count': stats['count'],
                'total_amount': stats['total_amount'],
                'currencies': currencies_formatted
            })
        
        # 按消费次数排序，取TOP3
        card_stats_list.sort(key=lambda x: x['count'], reverse=True)
        count_top3 = card_stats_list[:3] if card_stats_list else []
        
        # 如果TOP3为空，添加一个默认项以避免前端显示空列表
        if not count_top3 and (date or platform):
            logger.info(f"TOP3为空，添加默认项")
            count_top3 = [{
                'card_number': '默认无数据',
                'count': 0,
                'total_amount': 0,
                'currencies': [{
                    'currency': 'USD',
                    'amount': 0,
                    'formatted': '0.00 USD'
                }]
            }]
        
        # 构造响应数据
        response = {
            'stats': {
                'card_count': card_count,
                'wallet_trans_count': wallet_trans_count,
                'card_trans_count': card_trans_count,
                'error_count': error_count,
                'total_amount': total_amount
            },
            'error_transactions': formatted_error_transactions if formatted_error_transactions else [],
            'count_top3': count_top3
        }
        
        # 添加环比数据（如果有）
        if trends:
            response['trends'] = trends
        
        return response
    
    except Exception as e:
        # 记录错误并返回空结果
        logger.error(f"获取日报数据时出错: {str(e)}")
        return {
            'error': str(e),
            'stats': {
                'card_count': 0,
                'total_amount': [{'currency': 'USD', 'amount': 0, 'formatted': '0.00 USD'}],
                'wallet_trans_count': 0,
                'card_trans_count': 0,
                'error_count': 0
            },
            'trends': {
                'card_count': {'value': 0, 'formatted': '0%'},
                'wallet_trans_count': {'value': 0, 'formatted': '0%'},
                'card_trans_count': {'value': 0, 'formatted': '0%'},
                'total_amount': [{'currency': 'USD', 'trend': 0, 'formatted': '0%'}]
            },
            'error_transactions': [{
                'transaction_time': '-',
                'mask_card_number': '-',
                'accounting_amount': '0',
                'accounting_amount_currency': 'USD',
                'transaction_amount': '0',
                'transaction_amount_currency': 'USD',
                'biz_type': '-',
                'merchant_name': '-',
                'merchant_region': '-',
                'status': '-',
                'version': '-'
            }] if date or platform else [],  # 只有在有筛选条件时才显示默认异常交易
            'count_top3': [{
                'card_number': '****',
                'count': 0,
                'total_amount': 0,
                'currencies': [{
                    'currency': 'USD',
                    'amount': 0,
                    'formatted': '0.00 USD'
                }]
            }]
        }


def calculate_trend(current, previous):
    """计算环比变化百分比"""
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100


def format_trend(trend):
    """格式化环比变化显示"""
    if trend > 0:
        return f"+{trend:.1f}%"
    elif trend < 0:
        return f"{trend:.1f}%"
    else:
        return "0%"


# 可以添加更多辅助函数，如直接获取特定日期的统计数据等
def get_daily_stats_by_date_range(start_date, end_date, platform=None):
    """
    获取指定日期范围内的每日统计数据
    
    参数:
    start_date (str): 开始日期，格式为 YYYY-MM-DD
    end_date (str): 结束日期，格式为 YYYY-MM-DD
    platform (str): 平台类型，不传则返回所有平台的数据
    
    返回:
    list: 包含每日统计数据的列表
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        result = []
        current = start
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            daily_stats = get_daily_report(date_str, platform)
            
            # 移除详细的交易记录列表，只保留统计数据
            if 'error_transactions' in daily_stats:
                daily_stats['error_count'] = len(daily_stats['error_transactions'])
                del daily_stats['error_transactions']
            
            daily_stats['date'] = date_str
            result.append(daily_stats)
            
            current += timedelta(days=1)
        
        return result
    except ValueError:
        return {'error': '日期格式无效，请使用YYYY-MM-DD格式'}
    except Exception as e:
        return {'error': str(e)}
