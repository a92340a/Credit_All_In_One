import random

USER_AGENT = [
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36,gzip(gfe)',
    'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-S901U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19A346 Safari/602.1',
    'Mozilla/5.0 (iPhone13,2; U; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/15E148 Safari/602.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'
    ]

TOPICS = ['國內', '海外', '外送', '網購', '行動支付', '保險', '交通', '訂房', '停車', '機場', '影音', '餐廳']
KEYWORD = '信用卡推薦'
BANK_NAME = [
    {'chinese':'台新銀行', 'function':'crawling_taishin'},
    {'chinese':'國泰世華', 'function':'crawling_cathay'},
    {'chinese':'中國信託', 'function':'crawling_ctbc'},
    {'chinese':'滙豐銀行', 'function':'crawling_hsbc'},
    {'chinese':'玉山銀行', 'function':'crawling_esun'},
    {'chinese':'台北富邦', 'function':'crawling_fubon'},
    {'chinese':'兆豐銀行', 'function':'crawling_mega'},
    {'chinese':'永豐銀行', 'function':'crawling_sinopac'},
    {'chinese':'華南銀行', 'function':'crawling_huanan'},
    {'chinese':'第一銀行', 'function':'crawling_first'},
    {'chinese':'土地銀行', 'function':'crawling_land'},
    {'chinese':'渣打銀行', 'function':'crawling_chartered'},
    {'chinese':'星展銀行', 'function':'crawling_dbs'},
    {'chinese':'聯邦銀行', 'function':'crawling_ubot'},
    {'chinese':'美國運通', 'function':'crawling_american'},
    {'chinese':'合作金庫', 'function':'crawling_cooperative'},
    {'chinese':'元大銀行', 'function':'crawling_yuanta'},
    {'chinese':'遠東商銀', 'function':'crawling_fareast'},
    {'chinese':'臺灣企銀', 'function':'crawling_taiwanbusiness'},
    {'chinese':'彰化銀行', 'function':'crawling_changhua'},
    {'chinese':'高雄銀行', 'function':'crawling_kaohsiung'},
    {'chinese':'安泰銀行', 'function':'crawling_entie'},
    {'chinese':'凱基銀行', 'function':'crawling_kgi'},
    {'chinese':'臺灣銀行', 'function':'crawling_taiwan'},
    {'chinese':'台中銀行', 'function':'crawling_taichung'},
    {'chinese':'上海商銀', 'function':'crawling_shanghai'},
    {'chinese':'陽信銀行', 'function':'crawling_sunny'},
    {'chinese':'新光銀行', 'function':'crawling_shinkong'},
    {'chinese':'台灣樂天', 'function':'crawling_rakuten'},
]


if __name__ == '__main__':
    user_agent = random.choice(USER_AGENT)
    print(user_agent)