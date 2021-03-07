#import stocker
import pandas as pd
import yfinance as yf
from sklearn import preprocessing
import numpy as np
import altair as alt
import datetime


mystocks=pd.read_csv('Stocks_Example.csv')


cat=pd.DataFrame()
stockframes=[]





class Stock():
    def __init__(self, stocktick,startdate,number):
        self.stock= stocktick
        self.startdate= startdate
        self.number= number
        
    def get_data(stocktick, startdate, number):
        stock=yf.Ticker(stocktick)
        hist = stock.history(start=startdate)
        hist['Date'] = hist.index
        hist['Stock'] = stocktick
        x = hist.Open
        if (x[0] - x[-1]) < 0:
            change = "Increase"
        else:
            change = "Decrease"
        movement= -(((x[0] - x[-1])/x[0])*100)
        x=x.values.reshape(-1,1)
        min_max_scaler = preprocessing.MinMaxScaler()
        x_scaled = min_max_scaler.fit_transform(x)
        hist['Open_Scaled'] = x_scaled
        delta = hist['Open'].tolist()
        difference = [((x/delta[0]*100)-100) for x in delta]
        hist['Percentage Change (%)'] = difference
        hist['Change'] = change
        hist['10-Day']=hist['Percentage Change (%)'].rolling(3).mean()
        hist['30-Day']=hist['Percentage Change (%)'].rolling(10).mean()
        hist['Value (GBP)']= (hist['Open']* number)/100
        x = hist.Open
        hist['Change in Value (GBP)']= (((hist['Open'].diff()*number))/100)
        hist['Civ']= (((hist['Open'].diff()*number))/100)
        movements.append(movement)
        stockids.append(stocktick)
        longnames.append(stock.info['longName'])
        return hist
    
stockids=[]
movements=[]
longnames=[]



n=0

for n in range(0,len(mystocks)):

    x=mystocks.iloc[n,]
    x=x.values.tolist()
    a, b, c= x[0],x[1],x[2]

    test=Stock.get_data(a, b, c)
    test
    stockframes.append(test)
    n+=1

cat=pd.concat(stockframes)
cat
       
        

            
df = pd.DataFrame(list(zip(movements, stockids)), 
               columns =['Change', 'Stock'])


######################################################################
    
final=None
tick=0

for i in df.Stock.values.tolist():

    x=cat.where(cat.Stock==i)
    x=x.dropna()
   
    x=x[['Date','Stock','Change in Value (GBP)']]

    x=x.reset_index(drop=True)
    
    if tick==0:
        final=x
    else:
        final= pd.concat([final, x], axis=1)
    tick += 1
    
length= final.shape[0]
base = datetime.date.today()
date_list = [base - datetime.timedelta(days=x) for x in range(length)]

date_list

final.dates=pd.date_range(date_list[-1], base, freq='D')

final['dates'] = final.dates.values[::-1]


final_2=final[['dates','Change in Value (GBP)']]
final_2['Date']=final_2['dates']
final_2['Sum']=final_2.sum(axis=1)


final_2['Cumsum2'] = final_2.loc[::-1, 'Sum'].cumsum()[::-1]
final_2['Cumsum']=final_2['Sum'].cumsum()
final_2=final_2.iloc[::-1]
final_2=final_2[['Date','Sum','Cumsum2']]

######################################################################





selection = alt.selection_multi(fields=['Stock'], bind='legend')

brush = alt.selection(type='interval', encodings=['x'])

base = alt.Chart(cat).mark_line().encode(
        alt.X('Date:T',axis=alt.Axis(
              format='%m/%d',
              labelAngle=-45
          )),
    alt.Y('Percentage Change (%)', title='Change in Value (%)'),
    alt.Color('Stock:N',legend=alt.Legend(rowPadding=15)),
    tooltip=['Value (GBP):Q'],
    opacity=alt.condition(selection, alt.value(1), alt.value(0))
).add_selection(
    selection
).properties(
    width=600,
    height=250,
).transform_filter(
    selection
)



rules = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule().encode(y='y')

base_2=alt.layer(
    base, rules
)



volume = alt.Chart(cat).mark_bar().encode(
        alt.X('Date:T',axis=alt.Axis(
              format='%m/%d',
              labelAngle=-45
          )),
    alt.Y('Volume:Q'),
    alt.Color('Stock:N',legend=alt.Legend(rowPadding=15)),
    opacity=alt.condition(selection, alt.value(1), alt.value(0))
).add_selection(
    selection
).properties(
    width=600,
    height=250,
).transform_filter(
    selection
)


value = alt.Chart(cat).mark_area().encode(
        alt.X('Date:T',axis=alt.Axis(
              format='%m/%d',
              labelAngle=-45
          )),
    alt.Y('Value (GBP):Q'),
    
    color= alt.Color('Stock:N'),
    tooltip=['Value (GBP):Q'],
    opacity=alt.condition(selection, alt.value(1), alt.value(0))
).add_selection(
    selection
).properties(
    width=600,
    height=150,    
).transform_filter(
    selection
)

valuechange = alt.Chart(cat).mark_bar().encode(
        alt.X('Date:T',axis=alt.Axis(
              format='%m/%d',
              labelAngle=-45
          )),
    alt.Y('Change in Value (GBP):Q'),
    
    color=alt.condition(
        alt.datum.Civ > 0,
        alt.value("#06982d"),  # The positive color
        alt.value("#ae1325")  # The negative color
    ),
    tooltip=['Value (GBP):Q'],
    opacity=alt.condition(selection, alt.value(1), alt.value(0))
).add_selection(
    selection
).properties(
    width=600,
    height=150,    
).transform_filter(
    selection
)


abschange = alt.Chart(final_2).mark_area(
    line={'color':'darkgreen'},
    color=alt.Gradient(
        gradient='linear',
        stops=[alt.GradientStop(color='white', offset=0),
               alt.GradientStop(color='darkgreen', offset=1)],
        x1=1,
        x2=1,
        y1=1,
        y2=0
    )
).encode(
    alt.X('Date:T'),
    alt.Y('Cumsum2:Q', title='Cumulative Change (GBP)')
).add_selection(
    selection
).properties(
    width=1300,
    height=250,    
).transform_filter(
    selection
)


NormChange = base_2.encode(
    alt.X('Date:T' ,axis=alt.Axis(
              format='%m/%d',
              labelAngle=-45), scale=alt.Scale(domain=brush))
    
)

NormChange_rule=alt.layer(
 NormChange, rules
)


AdjustRange = alt.Chart(cat).mark_line().encode(
    alt.X('Date:T', axis=alt.Axis(labels=False,title=None,ticks=False)),
    alt.Y('Percentage Change (%)', axis=alt.Axis(labels=False,ticks=False,title=None)),
    alt.Color('Stock:N',legend=alt.Legend(rowPadding=15)),
    opacity=alt.condition(selection, alt.value(1), alt.value(0))
).add_selection(
    selection
).properties(
    width=1300,
    height=100,).add_selection(brush)

Volume = volume.encode(
    alt.X('Date:T' ,axis=alt.Axis(
              format='%m/%d',
              labelAngle=-45), scale=alt.Scale(domain=brush))
    
)

Value = value.encode(
    alt.X('Date:T' ,axis=alt.Axis(
              format='%m/%d',
              labelAngle=-45), scale=alt.Scale(domain=brush))
    
)

ValueChange = valuechange.encode(
    alt.X('Date:T' ,axis=alt.Axis(
              format='%m/%d',
              labelAngle=-45), scale=alt.Scale(domain=brush))
    
)


AbsChange = abschange.encode(
    alt.X('Date:T' ,axis=alt.Axis(
              format='%m/%d',
              labelAngle=-45), scale=alt.Scale(domain=brush))
    
)


AbsChange_rule=alt.layer(
 AbsChange, rules
)

lower_4=alt.Chart(df).mark_bar().encode(
    x='Stock',
    y='Change'
).properties(
    width=1200,
    height=200,    
)



line1=alt.hconcat(NormChange_rule,Volume )
line2=alt.hconcat(Value, ValueChange)
line3=alt.hconcat(AbsChange_rule)
line4=alt.hconcat(AdjustRange)


chart=alt.vconcat(line1,line2,line3,line4)

#chart= alt.vconcat(NormChange_rule, Volume , Value, ValueChange,AbsChange_rule, AdjustRange)
alt.renderers.enable('altair_viewer')
chart.show()
