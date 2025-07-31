# CryptoSift 加密货币分析工具

## 功能特性

- 多交易所加密货币实时价格获取
- AI驱动的价格走势预测
- 市场资讯整合分析
- 财经日历事件提醒
- 跨平台支持 (Windows/Android)

## 快速开始

### 1. 环境准备

```bash
# 克隆仓库
git clone https://github.com/your-repo/CryptoSift.git
cd CryptoSift

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

#### 基本配置流程
1. **创建配置文件**：
   ```bash
   cp config.py.example config.py
   ```

2. **编辑 `config.py` 文件，填入您的API密钥：
   ```python
   # DeepSeek API
   DEEPSEEK_API_KEY = "your_actual_deepseek_api_key"
   
   # OKX API 
   OKX_API_KEY = "your_actual_okx_api_key"
   OKX_SECRET_KEY = "your_actual_okx_secret_key"
   OKX_PASSPHRASE = "your_actual_okx_passphrase"
   ```

3. **需要配置的API密钥**：
   - DeepSeek API key (用于AI分析)
   - OKX API keys (用于市场数据获取)
   - Search API key (用于新闻搜索)
   - CoinMarketCal token (用于日历事件获取)

#### 安全注意事项
- 🔒 `config.py` 已自动加入.gitignore
- 🔑 建议启用API密钥的IP限制
- ⏱️ 定期轮换密钥(建议每3个月)
- 🛡️ 将API密钥存储在安全的地方，避免泄露

### 3. 运行应用

```bash
python CryptoSift.py
```

## 详细文档

### Android打包指南

[...保留原有的打包指南内容...]

### 故障排除

[...保留原有的故障排除内容...]

## 免责声明

- 本工具仅供技术分析参考
- 加密货币投资有风险
- 预测结果不构成投资建议

## 技术支持

如有问题请提交issue或联系：support@yourdomain.com
