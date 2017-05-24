import pandas as pd
from datetime import datetime

# 读取所有股票价格信息
df_price = pd.read_excel("data/price.xlsx")
df_price_origin = pd.read_excel("data/price_origin.xlsx")
# 读取所有股票基本信息
df_stock = pd.read_excel("data/stock.xlsx")
#读取所有指数信息
df_dict = pd.read_excel("data/index.xlsx", sheetname=[0,1,2], skiprows=[1])
#沪深300指数信息
df_300 = df_dict[0]

# 获取沪深300成分统计信息（月频）
col3 = df_300.columns
# 获取成分股信息
df_300_code = df_300[col3[0::2]]

#对股票价格数据进行简化，只取月底的股价
col3_code = df_300_code.columns
df_subprice = df_price.reindex(index=col3_code)
df_subprice_origin = df_price_origin.reindex(index=col3_code)
#去除股价为空的股票
#df_subprice_nonan = df_subprice.dropna(axis=1)
#筛选退市的股票
df_stock.columns = ['code', 'name', 'start_date', 'end_date']
#将未退市股票结束日期统一替换为2099-01-01
df_stock.replace(to_replace={'end_date': {pd.NaT: datetime(2099, 1, 1)}},inplace=True)
#取出2010-12-31退市的股票
stock_filter = df_stock[df_stock['end_date'] < datetime(2010, 12, 31)]['code']
#筛选股票数据
stock_data = df_stock[df_stock['end_date'] > datetime(2010, 12, 31)]
stock_data = stock_data.drop(labels='name', axis=1)
#对股价信息做对应的筛选
price_data = df_subprice.drop(stock_filter,1)
price_data_origin = df_subprice_origin.drop(stock_filter,1)


#输出至文件
price_data.to_csv('data/price.csv')
price_data_origin.to_csv('data/price_origin.csv')
stock_data.to_csv('data/stock.csv', index=False)


#单独处理股票指数信息
df_index_300 = pd.read_excel("data/index.xlsx", sheetname=0, header=[0,1])
df_index_500 = pd.read_excel("data/index.xlsx", sheetname=1, header=[0,1])
df_index_800 = pd.read_excel("data/index.xlsx", sheetname=2, header=[0,1])

#df_index_300[datetime(2010,12,31)]['weight']['000001.SZ']
df_index_300.to_csv('data/index_300.csv')
df_index_500.to_csv('data/index_500.csv')
df_index_800.to_csv('data/index_800.csv')






