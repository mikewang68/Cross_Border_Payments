class PushLanguage:
    # 表类别
    TABLE_MAPPING = {
        'TRANSACTION_DATA': {
            'CN': '交易數據',
            'JP': '取引データ',
            'US': 'Transaction Data'
        },
        'CARD_INFO': {
            'CN': '卡信息',
            'JP': '卡資訊',
            'US': 'Card Information'
        },
        'ACCOUNTING_INFO': {
            'CN': '賬務明細',
            'JP': '會計明細',
            'US': 'Accounting Details'
        },
        'CUSTOMER_TRANSACTION_STATISTICS': {
            'CN': '客戶交易統計',
            'JP': '顧客取引統計',
            'US': 'Customer Transaction Statistics'
        }

    }


    # 表头
    HEADERS = {
        'transaction_headers': {
            'CN': [
                '交易時間', '交易金額', '入賬金額', '手續費', '業務類型'
            ],
            'JP': [
                '取引時間', '取引金額', '入金額', 'サーチャージ金額', '業務タイプ'
            ],
            'US': [
                'Transaction Time', 'Transaction Amount', 'Accounting Amount', 'Surcharge Amount', 'Biz Type'
            ]
        },
        'card_info_headers': {
            'CN': [
                '卡号', '賬单周期'
            ],
            'JP': [
                'カード番号', '請求期間'
            ],
            'US': [
                'Card Number', 'Billing Cycle'
            ]
        },
        'accounting_info_headers': {
            'CN': [
                '賬戶收入', '賬戶支出'
            ],
            'JP': [
                '口座収入', '口座支出'
            ],
            'US': [
                'Account Income', 'Account Expenses'
            ]
        },
         'customer_transaction_headers': {
            'CN': [
                '客戶收入', '客戶支出'
            ],
            'JP': [
                '顧客収入', '顧客支出'
            ],
            'US': [
                'Customer Income', 'Customer Expenses'
            ]
        }
    }

    # 业务类型
    BIZ_TYPE_MAPPING = {
        'AUTH': {
            'CN': '授权/付款',
            'JP': '承認/支払い',
            'US': 'Authorize/Payment'
        },
        'CORRECTIVE_AUTH': {
            'CN': '付款更正',
            'JP': '承認の修正',
            'US': 'Corrective for AUTH'
        },
        'VERIFICATION': {
            'CN': '验证交易',
            'JP': '検証リクエスト',
            'US': 'Verification request'
        },
        'VOID': {
            'CN': '取消交易',
            'JP': '取引のキャンセル',
            'US': 'Cancelling an AUTH transaction'
        },
        'REFUND': {
            'CN': '交易退款',
            'JP': '取引の返金',
            'US': 'Refund for AUTH transaction'
        },
        'SETTLE': {
            'CN': '付款结算',
            'JP': 'カード決済の決算',
            'US': 'Settlement of card payment'
        },
        'CORRECTIVE_REFUND': {
            'CN': '退款修正',
            'JP': '返金の修正',
            'US': 'Corrective for refunds'
        },
        'CORRECTIVE_REFUND_VOID': {
            'CN': '退款更正取消',
            'JP': '返金の修正取消',
            'US': 'Cancel corrective of refund'
        },
        'REFUND_REVERSAL': {
            'CN': '取消退款',
            'JP': '返金取消',
            'US': 'Cancel refund'
        },
        'SERVICE_FEE': {
            'CN': '卡服务费',
            'JP': 'カードサービス料',
            'US': 'Card service fee'
        }
    }