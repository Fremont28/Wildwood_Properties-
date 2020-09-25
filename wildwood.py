#import libraries 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns 

#read-in csv file 
ww=pd.read_csv("wildwood_high.csv")
ww['ask_price'] = ww['ASKING PRICE'].astype(str).str.replace('\D+', '')
ww['sold_price'] = ww['SOLD PRICE'].astype(str).str.replace('\D+', '')
ww['days_mrkt'] = ww['DAYS ON MARKET'].astype(str).str.replace('\D+', '')   

#convert strings to floats 
ww['ask_price'] = ww['ask_price'].convert_objects(convert_numeric=True)
ww['sold_price'] = ww['sold_price'].convert_objects(convert_numeric=True)
ww['days_mrkt'] = ww['days_mrkt'].convert_objects(convert_numeric=True)

#get counts by group 
def get_stats(group):
    return {'min': group.min(), 'max': group.max(), 'count': group.count(), 'median': group.median()}

stats1=ww['sold_price'].groupby(ww['CITY']).apply(get_stats).unstack()
stats1=stats1.sort_values(by="median",ascending=False)
stats1=stats1[stats1['count']>0]

#price by type of house 
type_casa=ww.groupby('STYLE')[["ask_price","sold_price","days_mrkt"]].median()
type_casa.sort_values(by="sold_price")

#remove motels from dataset 
ww1=ww[~ww.STYLE.str.contains("Mote",na=False)]
ww1=ww1[~ww1.STYLE.str.contains("STYLE",na=False)]

#listings by month 
ww1['Date Copy'] = pd.to_datetime(ww1['SOLD DATE'])
ww1['month'] = pd.DatetimeIndex(ww1['Date Copy']).month 
ww1['year'] = pd.DatetimeIndex(ww1['Date Copy']).year
ww1['day'] = pd.DatetimeIndex(ww1['Date Copy']).day 

#count listings (by year, month, day) 
cnt_mth=ww1['month'].value_counts() 
cnt_mth.sort_values()
cnt_yr=ww1['year'].value_counts() 
cnt_days=ww1['day'].value_counts()
cnt_days.sort_values()

ww1['diff_price']=ww1['ask_price']-ww1['sold_price'] #+ seller loses? 
ww1['diff_price'].median() 
ww1['ask_price'].describe() 

#i. do properties that exist longer on market, sell less than the asking price?
def long_props(x):
    if x>=365000:
        return 3
    if x>=169900 and x<365000:
        return 2
    else:
        return 1
ww1['ask_price_levels']=ww1['ask_price'].apply(long_props)
ww1.ask_price_levels.value_counts()
ww1['ask_price_levels']=ww1['ask_price_levels'].astype(str)
ask_prices=ww1.groupby('ask_price_levels')['diff_price'].median()

#ii. days on market and price differences
ww1['days_mrkt'].describe() 

def days_on(x):
    if x>=215:
        return 3
    if x>=67 and x<215:
        return 2
    else:
        return 1

ww1['days_on_levels']=ww1['days_mrkt'].apply(days_on)
ww1['days_on_levels']=ww1['days_on_levels'].astype(str)
days_onn=ww1.groupby('days_on_levels')['diff_price'].median()
days_onn #less than 67 days on market and seller gets a sold price closer to asking price

#iii. wildwood locations 
def donde(x):
    if x=="West Wildwood":
        return 1
    if x=="Wildwood":
        return 2
    if x=="North Wildwood":
        return 3
    else:
        return 1

ww1['loc']=ww1['CITY'].apply(donde)
ww1.to_csv("ww1.csv") #append to csv 

#counts by the property address
cnt_add=ww1['ADDRESS'].value_counts()
cnt_add=pd.DataFrame(cnt_add)
cnt_add.reset_index(level=0,inplace=True)
cnt_add.columns=['ADDRESS','cnt']

props=ww1.groupby('ADDRESS')[['sold_price','days_mrkt']].median()
props=pd.DataFrame(props)
props.reset_index(level=0,inplace=True)

tot=pd.merge(cnt_add,props,on="ADDRESS")
tot['cnt'].corr(tot['sold_price']) #-0.11 (more listings, lead to cheaper prices?)
tot['cnt'].corr(tot['days_mrkt']) #-0.03 (more listings,a bit less days on market) 

typos=ww1[ww1['ADDRESS'].str.contains('225 E Wildwood Avenue',na=False)]
typos['STYLE'].value_counts() 
tot1=tot[tot.cnt<5]
tot1.days_mrkt.median() 

#time series analysis 
date_rng=pd.date_range(start='5/1/2018',end='9/30/2018',freq='H')
df=pd.DataFrame(date_rng,columns=['date'])

ww1['SOLD DATE']=pd.to_datetime(ww1['SOLD DATE'])
df1=ww1.set_index('SOLD DATE')

#count_months
cntt=df1['month'].value_counts()
cntt=pd.DataFrame(cntt)
cntt.reset_index(level=0,inplace=True)
cntt.columns=['month','count']

fig=plt.figure()
cntt['count'].plot()
plt.savefig('a1.png')

#time-based indexing 
#plot 1 
fig=plt.figure()
df1['sold_price'].plot()
plt.savefig('h1.png')

#plot 2
fig=plt.figure()
cols_plot = ['sold_price', 'ask_price', 'days_mrkt']
axes = df1[cols_plot].plot(marker='.', alpha=0.5, linestyle='None', figsize=(11, 9), subplots=True)
for ax in axes:
    ax.set_ylabel('')
    plt.savefig('h2.png')

#plot 3 seasonality 
fig=plt.figure()
ax = df1.loc['2018', 'sold_price'].plot()
ax.set_ylabel('Sold Price')
plt.savefig('h3.png')

#plot 4 (zoom into june and july)
fig=plt.figure()
ax =df1.loc['2018-06-01':'2018-07-31', 'sold_price'].plot(marker='o', linestyle='-')
ax.set_ylabel('Sold Price')
plt.savefig('h4.png')

#plot 5 (more seasonality)
fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
for name, ax in zip(['sold_price', 'ask_price'], axes):
    sns.boxplot(data=df1, x='month', y=name, ax=ax)
    ax.set_ylabel('Average Sell Price ($USD)')
    ax.set_title(name)
    if ax != axes[-1]:
        ax.set_xlabel('')
        plt.savefig('h5.png')
        
#frequencies 
pd.date_range('2018-06-01','2018-09-30',freq='D')
ww2.index 
date_sample=pd.to_datetime(['2017-05-31','2018-05-31','2019-05-31'])
sampy=ww2.loc[date_sample,['sold_price']].copy()

#resample time series (different time series) 
#i. weekly 
ww2=ww1.set_index('SOLD DATE')
date_cols=['ask_price','sold_price','days_mrkt','diff_price']
ww_weekly=ww2[date_cols].resample('W').median() #median home price per semana 
ww_weekly.head(10)
ww_weekly.shape #108 weeks in the dataset 

wwr=ww_weekly
wwr.reset_index(level=0,inplace=True)
wwr.loc[wwr['sold_price'].idxmin()]
wwr.sold_price.median() 

condos_plus=ww1[ww1['place_type']==2]
condos_plus['sold_price'].median() 

fig, ax = plt.subplots(figsize=(20,10))
ax.plot(ww2.loc[start:end, 'sold_price'],marker='.', linestyle='-', linewidth=0.5, label='Daily')
ax.plot(ww_weekly.loc[start:end, 'sold_price'],
marker='o', markersize=8, linestyle='-', label='Weekly Median Sold Price')
ax.set_ylabel('Sold Price ($USD)')
ax.legend()
plt.title('Wildwood Real Estate Stays Pretty Stable')
plt.savefig('h6.png')

#ii. monthly 
ww_monthly = ww2[date_cols].resample('M').sum(min_count=28)
ww_monthly.head(5)

fig, ax = plt.subplots(figsize=(20,10))
ax.plot(ww_monthly['sold_price'], color='black', label='Sold Price')
ww_monthly['ask_price'].plot.area(ax=ax, linewidth=0)
ax.legend()
ax.set_ylabel('Price ($USD)')
plt.savefig('h7.png')

##rolling window time series----------
ww_7d=ww2[date_cols].rolling(7,center=True).median()
start,end='2017-05','2019-05'
fig, ax = plt.subplots(figsize=(20,10))
ax.plot(ww2.loc[start:end, 'sold_price'],marker='.', linestyle='-', linewidth=0.5, label='Daily')
ax.plot(ww_weekly.loc[start:end, 'sold_price'],marker='o', markersize=8, linestyle='-', label='Sold Price ($USD)')
ax.plot(ww_7d.loc[start:end, 'sold_price'],marker='.', linestyle='-', label='7-day Rolling Mean')
ax.set_ylabel('Sold Price ($USD)')
ax.legend()
plt.savefig('h8.png')

#trends-------------
ww_365d= ww2[date_cols].rolling(window=365, center=True, min_periods=360).median()

fig, ax = plt.subplots(figsize=(20,10))
ax.plot(ww2['sold_price'], marker='.', markersize=2, color='0.6',linestyle='None', label='Daily')
ax.plot(ww_7d['sold_price'], linewidth=2, label='7-d Rolling Median')
ax.plot(ww_365d['sold_price'], color='0.2', linewidth=3,label='Trend (365-d Rolling Median)')
# Set x-ticks to yearly interval and add legend and labels
ax.legend()
ax.set_ylabel('Sold Price ($USD)')
ax.set_title('Trends in Sold Wildwood Properties')
plt.savefig('h9.png')

def style(x):
    if x=="Restaurant" or x=="Vacant Lot" or x=="Commercial/Industrial" or x=="Commercial Vacant Lot":
        return 1
    else:
        return 2

ww1['place_type']=ww1['STYLE'].apply(style)
ww1['place_type'].value_counts() 
wwX=ww1
wwX.to_csv("wildwood.csv") #append to csv 
