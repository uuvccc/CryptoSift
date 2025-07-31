import requests
import time
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
import json
import re
import yfinance as yf  # 需要安装：pip install yfinance
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --------------------------
# 配置参数（从config.py导入）
# --------------------------
from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    OKX_API_KEY,
    OKX_SECRET_KEY,
    OKX_PASSPHRASE,
    OKX_API_URL,
    SEARCH_API_KEY,
    SEARCH_API_URL,
    COINMARKETCAL_TOKEN
)

# 搜索关键词配置（压缩优化版）
SEARCH_QUERIES = [
    "BTC ETH SOL 价格分析",
    "PEPE DOGE MEME币动态", 
    "加密货币大盘 美联储政策",
    "SOL技术分析 最新升级",
    "加密货币监管最新消息"
]

# 美股指数配置
US_STOCKS = {
    "道琼斯工业平均指数": "^DJI",
    "纳斯达克综合指数": "^IXIC",
    "标普500指数": "^GSPC"
}

# 财经日历API配置
FINANCIAL_CALENDAR_SOURCES = {
    "coinmarketcal": {
        "url": "https://api.coinmarketcal.com/v1/events",
        "params": {
            "max": 5,
            "dateRangeStart": datetime.now().strftime("%Y-%m-%d"),
            "dateRangeEnd": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "access_token": COINMARKETCAL_TOKEN  # 从config导入
        }
    },
    "coingecko": {
        "url": "https://api.coingecko.com/api/v3/events",
        "params": {
            "upcoming_events_only": "true"
        }
    }
}

CRYPTO_LIST = ["SOL-USDT", "BTC-USDT", "ETH-USDT", "PEPE-USDT", "DOGE-USDT"]
PREDICTION_HOURS = 8
REQUEST_DELAY = 3
MAX_RETRIES = 3
TIMEOUT = 60


# --------------------------
# 工具函数：生成UTC时间戳
# --------------------------
def get_utc_timestamp():
    """生成符合OKX要求的UTC时间戳，解决时间警告问题"""
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


# --------------------------
# 工具函数：OKX API签名生成
# --------------------------
def okx_sign(timestamp, method, request_path, secret_key, body=""):
    """生成OKX API所需的签名"""
    message = timestamp + method + request_path + body
    mac = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
    return mac.hexdigest()


# --------------------------
# 工具函数：创建带重试机制的会话
# --------------------------
def create_session_with_retry():
    """创建具有自动重试功能的HTTP会话"""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=2,  # 指数退避：2,4,8秒
        status_forcelist=[429, 500, 502, 503, 504, 599]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    return session


# --------------------------
# 新增：获取加密货币财经日历
# --------------------------
def get_crypto_calendar_events():
    """获取加密货币重要财经日历事件"""
    session = create_session_with_retry()
    calendar_events = []
    
    for source_name, config in FINANCIAL_CALENDAR_SOURCES.items():
        try:
            time.sleep(REQUEST_DELAY)
            response = session.get(
                config["url"],
                params=config.get("params", {}),
                timeout=TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            if source_name == "coinmarketcal" and isinstance(data.get("data"), list):
                for event in data["data"][:5]:
                    title = event.get("title", {}).get("en", "无标题")
                    date = event.get("date_event", "日期未知")
                    coins = ", ".join([c["name"] for c in event.get("coins", [])])
                    calendar_events.append(f"{date} {title} ({coins})")
            
            elif source_name == "coingecko" and isinstance(data.get("data"), dict):
                for event in data["data"].get("upcoming_events", [])[:5]:
                    title = event.get("title", {}).get("en", "无标题")
                    date = event.get("start_date", "日期未知")
                    calendar_events.append(f"{date} {title}")
            
            if calendar_events:
                print(f"✅ 财经日历数据获取成功（{source_name}）")
                break
                
        except Exception as e:
            print(f"❌ 财经日历数据获取失败（{source_name}）：{str(e)}")
            continue
    
    return "；".join(calendar_events) if calendar_events else "未获取到近期重要财经事件"

# --------------------------
# 1. 获取美股数据（使用yfinance）
# --------------------------
def get_us_stock_data():
    """获取美股三大指数的最新价格和涨跌幅"""
    stock_data = {}
    for name, symbol in US_STOCKS.items():
        for attempt in range(MAX_RETRIES):
            try:
                # 使用yfinance获取股票信息
                ticker = yf.Ticker(symbol)
                data = ticker.info
                
                # 提取价格和计算涨跌幅
                price = round(float(data.get('regularMarketPrice', 0)), 2)
                prev_close = float(data.get('regularMarketPreviousClose', price))
                change = round(((price - prev_close) / prev_close) * 100, 2)
                
                stock_data[name] = {
                    "price": price,
                    "change": change
                }
                print(f"✅ 美股数据 - {name}：{price}（{change}%）")
                break
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(REQUEST_DELAY)
                    continue
                print(f"❌ 美股数据 - {name} 获取失败：{str(e)}")
    return stock_data


def get_latest_news():
    """根据博查API调试结果优化的最终版本：单关键词单请求，精准提取资讯"""
    session = create_session_with_retry()
    news_summary = []
    
    # 修改为获取更多结果
    base_payload = {
        "query": "",  # 动态填充搜索关键词
        "count": 5,   # 从2增加到5
        "freshness": "oneDay"     # 只获取1天内的最新资讯
    }
    
    # 经调试确认的有效认证头
    headers = {
        "Authorization": f"Bearer {SEARCH_API_KEY}",
        "Content-Type": "application/json"
    }
    
    for query in SEARCH_QUERIES:
        try:
            # 避免请求过于频繁，添加间隔
            time.sleep(REQUEST_DELAY)
            
            # 填充当前关键词
            base_payload["query"] = query
            
            # 执行单次有效请求
            response = session.post(
                SEARCH_API_URL,
                headers=headers,
                json=base_payload,
                timeout=TIMEOUT
            )
            
            # 确保请求成功（状态码200）
            response.raise_for_status()
            data = response.json()
            
            # 精准匹配博查API的响应结构：data -> webPages -> value
            if ("data" in data and 
                "webPages" in data["data"] and 
                isinstance(data["data"]["webPages"].get("value"), list)):
                
                # 提取更多资讯内容
                for item in data["data"]["webPages"]["value"][:5]:  # 从2增加到5
                    # 提取标题（优先name字段）
                    title = item.get("name", "无标题")
                    # 提取摘要（优先snippet字段）
                    snippet = item.get("snippet", "无摘要")
                    # 拼接并限制长度，避免信息过载
                    news_summary.append(f"{title}：{snippet[:150]}...")
                
                print(f"✅ 资讯获取成功（{query}）：{len(news_summary[-5:])}条结果")  # 从2改为5
        
        except Exception as e:
            print(f"❌ 资讯获取失败（{query}）：{str(e)}")
            continue
    
    # 去除重复资讯（保留首次出现的内容）
    unique_news = list(dict.fromkeys(news_summary))
    
    # 若有有效资讯则返回，否则提示无结果
    return "；".join(unique_news[:20]) if unique_news else "未获取到最新资讯"  # 从100改为20

# --------------------------
# 3. 获取加密货币价格
# --------------------------
def get_crypto_prices(crypto_pairs):
    prices = {}
    session = create_session_with_retry()
    
    for pair in crypto_pairs:
        try:
            timestamp = get_utc_timestamp()
            request_path = "/api/v5/market/ticker"
            sign = okx_sign(timestamp, "GET", request_path, OKX_SECRET_KEY)
            
            headers = {
                "OK-ACCESS-KEY": OKX_API_KEY,
                "OK-ACCESS-SIGN": sign,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": OKX_PASSPHRASE
            }
            
            time.sleep(REQUEST_DELAY)
            response = session.get(
                OKX_API_URL,
                headers=headers,
                params={"instId": pair},
                timeout=TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") == "0" and data.get("data"):
                last_price = round(float(data["data"][0]["last"]), 15)
                prices[pair] = last_price
                print(f"✅ {pair} 价格：{last_price} 美元")
        
        except Exception as e:
            print(f"❌ {pair} 价格获取失败：{str(e)}")
    
    return prices


# --------------------------
# 4. 时间取整工具函数
# --------------------------
def round_time(current_time):
    minute = current_time.minute
    if minute < 15:
        return current_time.replace(minute=0, second=0, microsecond=0)
    elif 15 <= minute < 45:
        return current_time.replace(minute=30, second=0, microsecond=0)
    else:
        return current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)


# --------------------------
# 5. 单个加密货币分析（含AI预测）
# --------------------------
def analyze_single_crypto(crypto_pair, price, prediction_hours, stock_data, latest_news):
    crypto_name = crypto_pair.split('-')[0].lower()
    current_time = datetime.now()
    rounded_time = round_time(current_time)
    time_str = rounded_time.strftime("%Y年%m月%d日%H点") + ("30分" if rounded_time.minute == 30 else "")
    
    # 获取财经日历事件
    calendar_events = get_crypto_calendar_events()
    
    # 构建提示词
    prompt = f"""现在是北京时间{time_str}，{crypto_name}现价{price}美元。
    近期财经日历：{calendar_events}
    美股参考：{"；".join([f"{name} {info['price']}（{'涨' if info['change'] >=0 else '跌'}{abs(info['change'])}%）" for name, info in stock_data.items()])}
    最新市场资讯：{latest_news}
    请综合分析以上所有信息，预测{prediction_hours}小时后{crypto_name}的价格走势。"""
    
    try:
        session = create_session_with_retry()
        time.sleep(REQUEST_DELAY)
        
        # 第一次请求：获取价格预测
        response = session.post(
            DEEPSEEK_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=TIMEOUT
        )
        response.raise_for_status()
        result = json.loads(response.content.decode('utf-8'))["choices"][0]["message"]["content"].strip()
        
        # 第二次请求：获取涨跌概率
        prob_prompt = f"""基于你对{crypto_name}的价格预测，给出：
        1. 上涨（价格高于当前）的概率
        2. 下跌（价格低于当前）的概率
        3. 横盘（价格波动±1%以内）的概率
        要求：总和为100%，格式为"涨xx%，跌xx%，横盘xx%"，只输出结果"""
        
        time.sleep(REQUEST_DELAY)
        prob_response = session.post(
            DEEPSEEK_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": result},
                    {"role": "user", "content": prob_prompt}
                ]
            },
            timeout=TIMEOUT
        )
        prob_response.raise_for_status()
        prob_result = json.loads(prob_response.content.decode('utf-8'))["choices"][0]["message"]["content"].strip()
        
        # 解析概率值
        up_match = re.search(r'涨(\d+)%', prob_result)
        down_match = re.search(r'跌(\d+)%', prob_result)
        flat_match = re.search(r'横盘(\d+)%', prob_result)
        
        if up_match and down_match and flat_match:
            up = int(up_match.group(1))
            down = int(down_match.group(1))
            flat = int(flat_match.group(1))
            
            # 确定主趋势
            trends = [("涨", up), ("跌", down), ("横盘", flat)]
            main_trend, main_prob = max(trends, key=lambda x: x[1])
            
            return {
                "name": crypto_name,
                "current_price": price,
                "predicted_price": result,
                "up": up,
                "down": down,
                "flat": flat,
                "main_trend": main_trend,
                "main_prob": main_prob,
                "prediction_time": rounded_time + timedelta(hours=prediction_hours)
            }
        else:
            print(f"[{crypto_name}] 概率格式错误：{prob_result}")
            return None
    
    except Exception as e:
        print(f"[{crypto_name}] 分析失败：{str(e)}")
        return None


# --------------------------
# 6. 汇总预测结果
# --------------------------
def summarize_results(all_results, latest_news):
    if not all_results:
        return "无有效预测结果"
    
    # 找到概率最大的货币
    max_prob_item = max(all_results, key=lambda x: x["main_prob"])
    
    summary = "===== 预测结果 =====\n"
    for res in all_results:
        summary += f"{res['name']}（当前{res['current_price']}）："
        summary += f"涨{res['up']}%，跌{res['down']}%，横盘{res['flat']}% → "
        summary += f"主趋势：{res['main_trend']}（{res['main_prob']}%），\n"
    
    summary += "\n===== 最大概率货币 =====\n"
    summary += f"{max_prob_item['name']}：{max_prob_item['main_trend']}（{max_prob_item['main_prob']}%）\n"
    summary += f"预测时间点：{max_prob_item['prediction_time'].strftime('%Y-%m-%d %H:%M')}"
    
    return summary


# --------------------------
# 主函数：执行完整流程
# --------------------------
def main():
    print(f"===== 开始分析（{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）=====\n")
    
    # 步骤1：获取实时市场资讯
    print("1. 获取最新市场资讯...")
    latest_news = get_latest_news()
    print(f"   资讯摘要：{latest_news[:100]}...\n")
    
    # 步骤2：获取美股数据
    print("2. 获取美股市场数据...")
    stock_data = get_us_stock_data()
    if not stock_data:
        print("   警告：未获取到任何美股数据\n")
    
    # 步骤3：获取加密货币价格
    print("\n3. 获取加密货币价格...")
    crypto_prices = get_crypto_prices(CRYPTO_LIST)
    if not crypto_prices:
        print("   错误：未获取到任何加密货币价格，程序终止")
        return
    
    # 步骤4：分析并预测
    print("\n4. 开始价格预测分析...")
    all_results = []
    for pair, price in crypto_prices.items():
        print(f"   分析 {pair}...")
        result = None
        for attempt in range(MAX_RETRIES):
            result = analyze_single_crypto(pair, price, PREDICTION_HOURS, stock_data, latest_news)
            if result:
                break
            print(f"   第{attempt + 1}次重试分析 {pair}...")
        if result:
            all_results.append(result)
        else:
            print(f"   无法完成 {pair} 的分析")
    
    # 步骤5：输出结果
    print("\n===== 分析结果汇总 =====")
    print(summarize_results(all_results, latest_news))
    print("\n===== 分析结束 =====")


if __name__ == "__main__":
    main()