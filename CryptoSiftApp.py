from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from functools import partial
import threading

from CryptoSift import (
    get_us_stock_data,
    get_crypto_prices,
    analyze_single_crypto,
    summarize_results,
    MAX_RETRIES
)

class CryptoSiftUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)
        
        # 标题
        self.add_widget(Label(
            text='CryptoSift 加密货币预测',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(20)
        ))
        
        # 创建滚动视图用于加密货币选择
        scroll = ScrollView(
            size_hint=(1, None),
            height=dp(200)
        )
        
        # 加密货币选择网格
        self.crypto_grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None
        )
        self.crypto_grid.bind(minimum_height=self.crypto_grid.setter('height'))
        
        # 预定义的加密货币列表
        self.crypto_pairs = [
            'BTC-USDT', 'ETH-USDT', 'SOL-USDT',
            'BNB-USDT', 'XRP-USDT', 'ADA-USDT',
            'DOGE-USDT', 'DOT-USDT', 'MATIC-USDT'
        ]
        
        # 复选框字典
        self.checkboxes = {}
        
        # 添加加密货币选择项
        for pair in self.crypto_pairs:
            # 创建水平布局
            row = BoxLayout(size_hint_y=None, height=dp(30))
            
            # 添加复选框
            checkbox = CheckBox(size_hint_x=None, width=dp(30))
            self.checkboxes[pair] = checkbox
            row.add_widget(checkbox)
            
            # 添加标签
            row.add_widget(Label(text=pair))
            
            self.crypto_grid.add_widget(row)
        
        scroll.add_widget(self.crypto_grid)
        self.add_widget(scroll)
        
        # 预测时间输入
        hours_layout = BoxLayout(size_hint_y=None, height=dp(40))
        hours_layout.add_widget(Label(
            text='预测时间（小时）：',
            size_hint_x=None,
            width=dp(120)
        ))
        self.hours_input = TextInput(
            text='8',
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(30)
        )
        hours_layout.add_widget(self.hours_input)
        self.add_widget(hours_layout)
        
        # 开始分析按钮
        self.analyze_btn = Button(
            text='开始分析',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.analyze_btn.bind(on_press=self.start_analysis)
        self.add_widget(self.analyze_btn)
        
        # 结果显示区域
        self.result_label = Label(
            text='请选择加密货币并设置预测时间',
            size_hint_y=None,
            height=dp(200),
            text_size=(Window.width - dp(20), None),
            halign='left',
            valign='top'
        )
        self.add_widget(self.result_label)
    
    def start_analysis(self, instance):
        # 获取选中的加密货币
        selected_pairs = [pair for pair, checkbox in self.checkboxes.items() if checkbox.active]
        
        if not selected_pairs:
            self.result_label.text = '请至少选择一个加密货币'
            return
        
        try:
            hours = int(self.hours_input.text)
            if hours <= 0:
                self.result_label.text = '预测时间必须大于0'
                return
        except ValueError:
            self.result_label.text = '请输入有效的预测时间'
            return
        
        # 禁用按钮
        self.analyze_btn.disabled = True
        self.result_label.text = '正在分析中，请稍候...'
        
        # 在新线程中执行分析
        threading.Thread(target=self.run_analysis, args=(selected_pairs, hours)).start()
    
    def run_analysis(self, crypto_pairs, prediction_hours):
        try:
            # 获取美股数据
            stock_data = get_us_stock_data()
            
            # 获取加密货币价格
            prices = get_crypto_prices(crypto_pairs)
            if not prices:
                Clock.schedule_once(lambda dt: self.update_result('获取价格失败'))
                return
            
            # 分析预测
            all_results = []
            for pair, price in prices.items():
                for attempt in range(MAX_RETRIES):
                    result = analyze_single_crypto(pair, price, prediction_hours, stock_data)
                    if result:
                        all_results.append(result)
                        break
            
            # 生成总结
            summary = summarize_results(all_results)
            
            # 在主线程中更新UI
            Clock.schedule_once(lambda dt: self.update_result(summary))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_result(f'分析过程出错：{str(e)}'))
        finally:
            # 重新启用按钮
            Clock.schedule_once(lambda dt: setattr(self.analyze_btn, 'disabled', False))
    
    def update_result(self, text):
        self.result_label.text = text

class CryptoSiftApp(App):
    def build(self):
        return CryptoSiftUI()

if __name__ == '__main__':
    Window.clearcolor = (0.95, 0.95, 0.95, 1)  # 设置浅灰色背景
    CryptoSiftApp().run()