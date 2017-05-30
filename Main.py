# -*- coding: cp936 -*-
"""
Created on Tue Feb 07 14:27:02 2017

@author: 薛凌鸿
"""
# From Python
import sys

# From PyQt
# widget, subsidgets, and utility imports
from PyQt4.Qt import QApplication
from PyQt4.QtGui import QMainWindow

import pandas as pd
from pandas import Series,DataFrame

import numpy as np

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


from lib.ui.MainWindow import Ui_MainWindow

__VERSION__ = '0.1'

# 主页面
class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        # 构建页面
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 构建图片展示区域 有中文出现的情况，需要u'内容'
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        plt.rcParams['legend.fontsize'] = 10 # 设置图例字体大小

        self.dpi = 100
        self.fig = Figure((8.5, 4.5), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.ui.figure_widget)

        self.axes = self.fig.add_subplot(111)
        self.mpl_toolbar = NavigationToolbar(self.canvas,self.ui.figure_widget)

        # 设置标题
        self.setWindowTitle(u"动能/反转效应回测工具 -- Version %s" % __VERSION__)

        # 加载数据
        self.load_data()
        # 计算指数价格数据
        self.cal_index_prices()
        # 添加页面控件处理事件
        self.create_connections()
        # 显示计算结果
        self.on_show()

    # 加载数据
    def load_data(self):
        #加载所有指数信息
        self.df_index_300 = pd.read_csv('data/index_300.csv', header=[0, 1], index_col=None)
        self.df_index_500 = pd.read_csv('data/index_500.csv', header=[0, 1], index_col=None)
        self.df_index_800 = pd.read_csv('data/index_800.csv', header=[0, 1], index_col=None)
        # 全量股价数据
        self.df_price = pd.read_csv('data/price.csv', index_col=0, parse_dates=True)
        self.df_price_origin = pd.read_csv('data/price_origin.csv', index_col=0, parse_dates=True)

    # 计算各指数价格(使用不复权的股票价格）
    def cal_index_prices(self):
        # 转换指数信息的列结构
        index_levels = pd.to_datetime(self.df_index_300.columns.get_level_values(0).unique())
        self.df_index_300.columns.set_levels(index_levels, level=0, inplace=True)
        index_levels = pd.to_datetime(self.df_index_500.columns.get_level_values(0).unique())
        self.df_index_500.columns.set_levels(index_levels, level=0, inplace=True)
        index_levels = pd.to_datetime(self.df_index_800.columns.get_level_values(0).unique())
        self.df_index_800.columns.set_levels(index_levels, level=0, inplace=True)

        #获取成分股信息
        df_code_300 = self.df_index_300.xs(key='code', axis=1, level=1)
        df_code_500 = self.df_index_500.xs(key='code', axis=1, level=1)
        df_code_800 = self.df_index_800.xs(key='code', axis=1, level=1)
        #获取成分股权重信息
        df_weight_300 = self.df_index_300.xs(key='weight', axis=1, level=1)
        df_weight_500 = self.df_index_500.xs(key='weight', axis=1, level=1)
        df_weight_800 = self.df_index_800.xs(key='weight', axis=1, level=1)

        self.index_prices_300 = Series()
        self.index_prices_500 = Series()
        self.index_prices_800 = Series()
        period_list = self.df_price.index
        for i in range(0, len(period_list), 1):
            cal_date = period_list[i]
            # 获取当天成分股股价信息
            index_price_300 = self.df_price_origin[df_code_300[cal_date]].ix[cal_date, :]
            index_price_500 = self.df_price_origin[df_code_500[cal_date]].ix[cal_date, :]
            index_price_800 = self.df_price_origin[df_code_800[cal_date]].ix[cal_date, :]
            # 获取当天成分股权重信息
            index_weight_300 = df_weight_300[cal_date]
            index_weight_500 = df_weight_500[cal_date]
            index_weight_800 = df_weight_800[cal_date]

            index_weight_300.index = index_price_300.index
            index_weight_500.index = index_price_500.index
            index_weight_800.index = index_price_800.index

            # 计算指数加权价格
            self.index_prices_300.set_value(cal_date, index_price_300.dot(index_weight_300))
            self.index_prices_500.set_value(cal_date, index_price_500.dot(index_weight_500))
            self.index_prices_800.set_value(cal_date, index_price_800.dot(index_weight_800))


    #显示/刷新计算结果图片
    def on_show(self):
        # 禁用相关操作
        self.ui.groupBox_type.setDisabled(True)
        self.ui.groupBox_index.setDisabled(True)
        self.ui.groupBox_percent.setDisabled(True)
        self.ui.periodSlider.setDisabled(True)
        self.ui.groupBox_returntype.setDisabled(True)

        # 清空图片
        self.axes.clear()

        # 判断效应类型
        if self.ui.momentumButton.isChecked():
            self.cal_type = 'momentum'
        elif self.ui.crossoversButton.isChecked():
            self.cal_type = 'crossovers'
        else:
            return

        # 判断指数类型
        if self.ui.index300Button.isChecked():
            self.index_type = '300'
        elif self.ui.index500Button.isChecked():
            self.index_type = '500'
        elif self.ui.index800Button.isChecked():
            self.index_type = '800'
        else:
            return

        # 判断收益类型
        if self.ui.periodReturnButton.isChecked():
            self.return_type = 'period'
        elif self.ui.cumReturnButton.isChecked():
            self.return_type = 'cum'
        else:
            return

        # 判断收益率事件长度
        self.cal_cal_period = self.ui.periodSlider.value()

        # 判断组合占比
        self.cal_percent = []
        if self.ui.checkBoxP1.isChecked():
            self.cal_percent.append(0.01)
        if self.ui.checkBoxP5.isChecked():
            self.cal_percent.append(0.05)
        if self.ui.checkBoxP10.isChecked():
            self.cal_percent.append(0.1)
        if self.ui.checkBoxP20.isChecked():
            self.cal_percent.append(0.2)
        if self.ui.checkBoxP30.isChecked():
            self.cal_percent.append(0.3)

        # 计算分期超额收益率
        self.cal_portfolio_returns(self.cal_cal_period, self.cal_type, self.index_type, self.return_type, self.cal_percent)
        # 增加基准收益率s
        self.portfolio_returns['benchmark'] = Series(0,index=self.portfolio_returns.index)
        # 画图，并计算超额累计收益率
        # self.portfolio_cum_returns[name] = (self.portfolio_returns[name]+1).prod()
        names = self.portfolio_returns.columns
        for name in names:
            self.axes.plot(self.portfolio_returns[name].index, self.portfolio_returns[name]*100, label=name)

        # 格式化X 轴标签日期只显示年月，并控制显示的数量
        xfmt = mdates.DateFormatter('%Y-%m')
        self.axes.xaxis.set_major_formatter(xfmt)
        if self.portfolio_returns.index.size > 40:
            self.axes.set_xticks(self.portfolio_returns.index[0::2])
        else:
            self.axes.set_xticks(self.portfolio_returns.index)

        # 格式化Y 轴标签显示数量
        max_y = int(self.portfolio_returns.max().max()*100)
        min_y = int(self.portfolio_returns.min().min()*100)
        step_y = (max_y-min_y)/10
        max_range = np.arange(0, max_y + step_y, step_y)
        min_range = np.arange(0, min_y-step_y, -step_y)
        ticks_y = np.append(min_range, max_range)
        ticks_y = np.unique(np.sort(ticks_y))
        self.axes.set_yticks(ticks_y)

        plt.setp(self.axes.xaxis.get_majorticklabels(), rotation=70)
        self.fig.tight_layout(pad=2.0)

        self.axes.set_xlabel(u'收益日期（月频）')
        if self.return_type == 'period':
            self.axes.set_ylabel(u'相对指数收益率的分期超额收益率（%）')
        elif self.return_type == 'cum':
            self.axes.set_ylabel(u'相对指数收益率的累计超额收益率（%）')
        self.axes.grid(True)
        self.axes.legend()
        self.canvas.draw()

        # 清空累计超额收益率展示框
        self.ui.textReturn.clear()
        # 设置计算超额累计收益率
        if self.return_type == 'cum':
            self.ui.textReturn.append(u'超额累计总收益率：')
            for name in names:
                cum_return = round(self.portfolio_returns[name].tail(1)*100,2)
                self.ui.textReturn.append(name + ' : ' + str(cum_return) + '%')

        # 启用相关操作
        self.ui.groupBox_type.setDisabled(False)
        self.ui.groupBox_index.setDisabled(False)
        self.ui.groupBox_percent.setDisabled(False)
        self.ui.periodSlider.setDisabled(False)
        self.ui.groupBox_returntype.setDisabled(False)

    # 动量效应按钮切换事件
    def on_show_m(self):
        if self.ui.momentumButton.isChecked():
            self.on_show()

    # 反转效应按钮切换事件
    def on_show_c(self):
        if self.ui.crossoversButton.isChecked():
            self.on_show()

    # 沪深300指数按钮切换事件
    def on_show_3(self):
        if self.ui.index300Button.isChecked():
            self.on_show()

    # 中证500指数按钮切换事件
    def on_show_5(self):
        if self.ui.index500Button.isChecked():
            self.on_show()

    # 中证800指数按钮切换事件
    def on_show_8(self):
        if self.ui.index800Button.isChecked():
            self.on_show()

    # 分期超额收益率按钮切换事件
    def on_show_p(self):
        if self.ui.periodReturnButton.isChecked():
            self.on_show()

    # 分期超额收益率按钮切换事件
    def on_show_cu(self):
        if self.ui.cumReturnButton.isChecked():
            self.on_show()

    #控件的事件定义
    def create_connections(self):
        # 增加按钮的事件处理
        #收益率时间长度
        #self.connect(self.ui.periodSlider, SIGNAL('valueChanged()'), self.on_show)
        self.ui.periodSlider.valueChanged.connect(self.on_show)
        # 效应类型
        self.ui.momentumButton.toggled.connect(self.on_show_m)
        self.ui.crossoversButton.toggled.connect(self.on_show_c)
        # 指数类型
        self.ui.index300Button.toggled.connect(self.on_show_3)
        self.ui.index500Button.toggled.connect(self.on_show_5)
        self.ui.index800Button.toggled.connect(self.on_show_8)
        #收益类型
        self.ui.periodReturnButton.toggled.connect(self.on_show_p)
        self.ui.cumReturnButton.toggled.connect(self.on_show_cu)
        # 组合占比
        self.ui.checkBoxP1.stateChanged.connect(self.on_show)
        self.ui.checkBoxP5.stateChanged.connect(self.on_show)
        self.ui.checkBoxP10.stateChanged.connect(self.on_show)
        self.ui.checkBoxP20.stateChanged.connect(self.on_show)
        self.ui.checkBoxP30.stateChanged.connect(self.on_show)

    # 计算组合策略收益率（使用后复权股票价格）
    def cal_portfolio_returns(self, cal_period = 1, cal_type = 'momentum', index_type = '300', return_type = 'period', cal_percent = [0.01]):
        #判定指数类型
        if index_type == '300':
            df_index = self.df_index_300
            index_prices = self.index_prices_300
        elif index_type == '500':
            df_index = self.df_index_500
            index_prices = self.index_prices_500
        elif index_type == '800':
            df_index = self.df_index_800
            index_prices = self.index_prices_800

        #修改指数信息的列的数据类型
        index_levels = pd.to_datetime(df_index.columns.get_level_values(0).unique())
        df_index.columns.set_levels(index_levels, level=0, inplace=True)

        # 计算组合股票数量
        cal_num = [int(float(index_type) * x) for x in cal_percent]

        #获取成分股信息
        df_code = df_index.xs(key='code', axis=1, level=1)

        # 计算各股票收益率
        stock_returns = self.df_price.pct_change(cal_period)
        # 计算指数收益率
        index_total_returns = index_prices.pct_change(cal_period)
        period_list = stock_returns.index
        # 计算策略组合收益情况
        portfolio_returns = DataFrame()
        index_cum_returns = Series()
        for i in range(cal_period, len(period_list) - cal_period, cal_period):
            # 计算收益时间点指数成分股的收益率
            cal_date = period_list[i]
            index_returns = stock_returns[df_code[cal_date]].ix[cal_date, :]
            # 对指数成分股的收益率进行排序
            if cal_type == 'momentum':
                index_returns.sort_values(ascending=False, inplace=True)
            elif cal_type == 'crossovers':
                index_returns.sort_values(ascending=True, inplace=True)

            for num in cal_num:
                # 选取上一期收益高（低）的成分股组合
                portfolio = index_returns[0:num].index
                # 计算组合平均收益率
                return_date = period_list[i + cal_period]
                portfolio_return = Series.mean(stock_returns[portfolio].ix[return_date, :])
                # 计算分期超额收益率
                if return_type == 'period':
                    excess_return = portfolio_return - index_total_returns[return_date]
                # 计算累计超额收益率
                elif return_type == 'cum':
                    if i > cal_period:
                        index_return = index_cum_returns[cal_date] * (1 + index_total_returns[return_date])
                        cum_return = portfolio_returns.get_value(index=cal_date, col=num / float(index_type))
                        portfolio_return = (1 + portfolio_return) * (index_cum_returns[cal_date] + cum_return)
                    else:
                        index_return = 1 + index_total_returns[return_date]
                        portfolio_return = 1 + portfolio_return

                    excess_return = portfolio_return - index_return
                    index_cum_returns.set_value(label=return_date, value=index_return)

                portfolio_returns.set_value(index=return_date, col=num / float(index_type), value=excess_return)
        portfolio_returns.columns=[str(x*100) + '%' for x in cal_percent]
        self.portfolio_returns=portfolio_returns


# setup and run the event loop
app = QApplication(sys.argv)
main = Main()
main.show()
sys.exit(app.exec_())
