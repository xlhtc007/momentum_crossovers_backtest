# -*- coding: cp936 -*-
"""
Created on Tue Feb 07 14:27:02 2017

@author: Ѧ���
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

# ��ҳ��
class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        # ����ҳ��
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # ����ͼƬչʾ���� �����ĳ��ֵ��������Ҫu'����'
        plt.rcParams['font.sans-serif'] = ['SimHei']  # ����������ʾ���ı�ǩ
        plt.rcParams['axes.unicode_minus'] = False  # ����������ʾ����
        plt.rcParams['legend.fontsize'] = 10 # ����ͼ�������С

        self.dpi = 100
        self.fig = Figure((8.5, 4.5), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.ui.figure_widget)

        self.axes = self.fig.add_subplot(111)
        self.mpl_toolbar = NavigationToolbar(self.canvas,self.ui.figure_widget)

        # ���ñ���
        self.setWindowTitle(u"����/��תЧӦ�ز⹤�� -- Version %s" % __VERSION__)

        # ��������
        self.load_data()
        # ����ָ���۸�����
        self.cal_index_prices()
        # ���ҳ��ؼ������¼�
        self.create_connections()
        # ��ʾ������
        self.on_show()

    # ��������
    def load_data(self):
        #��������ָ����Ϣ
        self.df_index_300 = pd.read_csv('data/index_300.csv', header=[0, 1], index_col=None)
        self.df_index_500 = pd.read_csv('data/index_500.csv', header=[0, 1], index_col=None)
        self.df_index_800 = pd.read_csv('data/index_800.csv', header=[0, 1], index_col=None)
        # ȫ���ɼ�����
        self.df_price = pd.read_csv('data/price.csv', index_col=0, parse_dates=True)
        self.df_price_origin = pd.read_csv('data/price_origin.csv', index_col=0, parse_dates=True)

    # �����ָ���۸�(ʹ�ò���Ȩ�Ĺ�Ʊ�۸�
    def cal_index_prices(self):
        # ת��ָ����Ϣ���нṹ
        index_levels = pd.to_datetime(self.df_index_300.columns.get_level_values(0).unique())
        self.df_index_300.columns.set_levels(index_levels, level=0, inplace=True)
        index_levels = pd.to_datetime(self.df_index_500.columns.get_level_values(0).unique())
        self.df_index_500.columns.set_levels(index_levels, level=0, inplace=True)
        index_levels = pd.to_datetime(self.df_index_800.columns.get_level_values(0).unique())
        self.df_index_800.columns.set_levels(index_levels, level=0, inplace=True)

        #��ȡ�ɷֹ���Ϣ
        df_code_300 = self.df_index_300.xs(key='code', axis=1, level=1)
        df_code_500 = self.df_index_500.xs(key='code', axis=1, level=1)
        df_code_800 = self.df_index_800.xs(key='code', axis=1, level=1)
        #��ȡ�ɷֹ�Ȩ����Ϣ
        df_weight_300 = self.df_index_300.xs(key='weight', axis=1, level=1)
        df_weight_500 = self.df_index_500.xs(key='weight', axis=1, level=1)
        df_weight_800 = self.df_index_800.xs(key='weight', axis=1, level=1)

        self.index_prices_300 = Series()
        self.index_prices_500 = Series()
        self.index_prices_800 = Series()
        period_list = self.df_price.index
        for i in range(0, len(period_list), 1):
            cal_date = period_list[i]
            # ��ȡ����ɷֹɹɼ���Ϣ
            index_price_300 = self.df_price_origin[df_code_300[cal_date]].ix[cal_date, :]
            index_price_500 = self.df_price_origin[df_code_500[cal_date]].ix[cal_date, :]
            index_price_800 = self.df_price_origin[df_code_800[cal_date]].ix[cal_date, :]
            # ��ȡ����ɷֹ�Ȩ����Ϣ
            index_weight_300 = df_weight_300[cal_date]
            index_weight_500 = df_weight_500[cal_date]
            index_weight_800 = df_weight_800[cal_date]

            index_weight_300.index = index_price_300.index
            index_weight_500.index = index_price_500.index
            index_weight_800.index = index_price_800.index

            # ����ָ����Ȩ�۸�
            self.index_prices_300.set_value(cal_date, index_price_300.dot(index_weight_300))
            self.index_prices_500.set_value(cal_date, index_price_500.dot(index_weight_500))
            self.index_prices_800.set_value(cal_date, index_price_800.dot(index_weight_800))


    #��ʾ/ˢ�¼�����ͼƬ
    def on_show(self):
        # ������ز���
        self.ui.groupBox_type.setDisabled(True)
        self.ui.groupBox_index.setDisabled(True)
        self.ui.groupBox_percent.setDisabled(True)
        self.ui.periodSlider.setDisabled(True)
        self.ui.groupBox_returntype.setDisabled(True)

        # ���ͼƬ
        self.axes.clear()

        # �ж�ЧӦ����
        if self.ui.momentumButton.isChecked():
            self.cal_type = 'momentum'
        elif self.ui.crossoversButton.isChecked():
            self.cal_type = 'crossovers'
        else:
            return

        # �ж�ָ������
        if self.ui.index300Button.isChecked():
            self.index_type = '300'
        elif self.ui.index500Button.isChecked():
            self.index_type = '500'
        elif self.ui.index800Button.isChecked():
            self.index_type = '800'
        else:
            return

        # �ж���������
        if self.ui.periodReturnButton.isChecked():
            self.return_type = 'period'
        elif self.ui.cumReturnButton.isChecked():
            self.return_type = 'cum'
        else:
            return

        # �ж��������¼�����
        self.cal_cal_period = self.ui.periodSlider.value()

        # �ж����ռ��
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

        # ������ڳ���������
        self.cal_portfolio_returns(self.cal_cal_period, self.cal_type, self.index_type, self.return_type, self.cal_percent)
        # ���ӻ�׼������s
        self.portfolio_returns['benchmark'] = Series(0,index=self.portfolio_returns.index)
        # ��ͼ�������㳬���ۼ�������
        # self.portfolio_cum_returns[name] = (self.portfolio_returns[name]+1).prod()
        names = self.portfolio_returns.columns
        for name in names:
            self.axes.plot(self.portfolio_returns[name].index, self.portfolio_returns[name]*100, label=name)

        # ��ʽ��X ���ǩ����ֻ��ʾ���£���������ʾ������
        xfmt = mdates.DateFormatter('%Y-%m')
        self.axes.xaxis.set_major_formatter(xfmt)
        if self.portfolio_returns.index.size > 40:
            self.axes.set_xticks(self.portfolio_returns.index[0::2])
        else:
            self.axes.set_xticks(self.portfolio_returns.index)

        # ��ʽ��Y ���ǩ��ʾ����
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

        self.axes.set_xlabel(u'�������ڣ���Ƶ��')
        if self.return_type == 'period':
            self.axes.set_ylabel(u'���ָ�������ʵķ��ڳ��������ʣ�%��')
        elif self.return_type == 'cum':
            self.axes.set_ylabel(u'���ָ�������ʵ��ۼƳ��������ʣ�%��')
        self.axes.grid(True)
        self.axes.legend()
        self.canvas.draw()

        # ����ۼƳ���������չʾ��
        self.ui.textReturn.clear()
        # ���ü��㳬���ۼ�������
        if self.return_type == 'cum':
            self.ui.textReturn.append(u'�����ۼ��������ʣ�')
            for name in names:
                cum_return = round(self.portfolio_returns[name].tail(1)*100,2)
                self.ui.textReturn.append(name + ' : ' + str(cum_return) + '%')

        # ������ز���
        self.ui.groupBox_type.setDisabled(False)
        self.ui.groupBox_index.setDisabled(False)
        self.ui.groupBox_percent.setDisabled(False)
        self.ui.periodSlider.setDisabled(False)
        self.ui.groupBox_returntype.setDisabled(False)

    # ����ЧӦ��ť�л��¼�
    def on_show_m(self):
        if self.ui.momentumButton.isChecked():
            self.on_show()

    # ��תЧӦ��ť�л��¼�
    def on_show_c(self):
        if self.ui.crossoversButton.isChecked():
            self.on_show()

    # ����300ָ����ť�л��¼�
    def on_show_3(self):
        if self.ui.index300Button.isChecked():
            self.on_show()

    # ��֤500ָ����ť�л��¼�
    def on_show_5(self):
        if self.ui.index500Button.isChecked():
            self.on_show()

    # ��֤800ָ����ť�л��¼�
    def on_show_8(self):
        if self.ui.index800Button.isChecked():
            self.on_show()

    # ���ڳ��������ʰ�ť�л��¼�
    def on_show_p(self):
        if self.ui.periodReturnButton.isChecked():
            self.on_show()

    # ���ڳ��������ʰ�ť�л��¼�
    def on_show_cu(self):
        if self.ui.cumReturnButton.isChecked():
            self.on_show()

    #�ؼ����¼�����
    def create_connections(self):
        # ���Ӱ�ť���¼�����
        #������ʱ�䳤��
        #self.connect(self.ui.periodSlider, SIGNAL('valueChanged()'), self.on_show)
        self.ui.periodSlider.valueChanged.connect(self.on_show)
        # ЧӦ����
        self.ui.momentumButton.toggled.connect(self.on_show_m)
        self.ui.crossoversButton.toggled.connect(self.on_show_c)
        # ָ������
        self.ui.index300Button.toggled.connect(self.on_show_3)
        self.ui.index500Button.toggled.connect(self.on_show_5)
        self.ui.index800Button.toggled.connect(self.on_show_8)
        #��������
        self.ui.periodReturnButton.toggled.connect(self.on_show_p)
        self.ui.cumReturnButton.toggled.connect(self.on_show_cu)
        # ���ռ��
        self.ui.checkBoxP1.stateChanged.connect(self.on_show)
        self.ui.checkBoxP5.stateChanged.connect(self.on_show)
        self.ui.checkBoxP10.stateChanged.connect(self.on_show)
        self.ui.checkBoxP20.stateChanged.connect(self.on_show)
        self.ui.checkBoxP30.stateChanged.connect(self.on_show)

    # ������ϲ��������ʣ�ʹ�ú�Ȩ��Ʊ�۸�
    def cal_portfolio_returns(self, cal_period = 1, cal_type = 'momentum', index_type = '300', return_type = 'period', cal_percent = [0.01]):
        #�ж�ָ������
        if index_type == '300':
            df_index = self.df_index_300
            index_prices = self.index_prices_300
        elif index_type == '500':
            df_index = self.df_index_500
            index_prices = self.index_prices_500
        elif index_type == '800':
            df_index = self.df_index_800
            index_prices = self.index_prices_800

        #�޸�ָ����Ϣ���е���������
        index_levels = pd.to_datetime(df_index.columns.get_level_values(0).unique())
        df_index.columns.set_levels(index_levels, level=0, inplace=True)

        # ������Ϲ�Ʊ����
        cal_num = [int(float(index_type) * x) for x in cal_percent]

        #��ȡ�ɷֹ���Ϣ
        df_code = df_index.xs(key='code', axis=1, level=1)

        # �������Ʊ������
        stock_returns = self.df_price.pct_change(cal_period)
        # ����ָ��������
        index_total_returns = index_prices.pct_change(cal_period)
        period_list = stock_returns.index
        # �����������������
        portfolio_returns = DataFrame()
        index_cum_returns = Series()
        for i in range(cal_period, len(period_list) - cal_period, cal_period):
            # ��������ʱ���ָ���ɷֹɵ�������
            cal_date = period_list[i]
            index_returns = stock_returns[df_code[cal_date]].ix[cal_date, :]
            # ��ָ���ɷֹɵ������ʽ�������
            if cal_type == 'momentum':
                index_returns.sort_values(ascending=False, inplace=True)
            elif cal_type == 'crossovers':
                index_returns.sort_values(ascending=True, inplace=True)

            for num in cal_num:
                # ѡȡ��һ������ߣ��ͣ��ĳɷֹ����
                portfolio = index_returns[0:num].index
                # �������ƽ��������
                return_date = period_list[i + cal_period]
                portfolio_return = Series.mean(stock_returns[portfolio].ix[return_date, :])
                # ������ڳ���������
                if return_type == 'period':
                    excess_return = portfolio_return - index_total_returns[return_date]
                # �����ۼƳ���������
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
