from django.shortcuts import render
import plotly.offline as opy
import plotly.graph_objs as go
from .models import Currency, CurrencyPair

def browse_view(request):
    pass
    # query = None
    # asset = None
    # if request.method == 'POST':
    #     query = request.POST.get('q')
    #     try:
    #         query = str(query)
    #     except ValueError:
    #         pass
    #     if query:
    #
    #
    #         if CurrencyPair.objects.filter() != None:
    #             chart = asset.get_week_chart()
    #             Dates = list([item["time"] for item in chart])
    #             Open = list([item["open"] for item in chart])
    #             Close = list([item["close"] for item in chart])
    #
    #             if asset_type == "stock":
    #                 High = list([item["high"] for item in chart])
    #                 Low = list([item["low"] for item in chart])
    #
    #
    #             else:
    #                 High = list([item["max"] for item in chart])
    #                 Low = list([item["min"] for item in chart])
    #
    #             trace = go.Candlestick(x=Dates,
    #                    open = Open,
    #                    high = High,
    #                    low = Low,
    #                    close = Close)
    #
    #             data = [trace]
    #             layout=go.Layout(title="Week Chart", xaxis={'title':'Date'}, yaxis={'title':'Price($)'})
    #             figure=go.Figure(data=data,layout=layout)
    #             config={"displayModeBar": False, "showLink":False}
    #             graph = opy.plot(figure, auto_open=False, config=config,output_type='div')
    #
    #             form = AddInvestment()
    #
    #             return render(request, 'assets/browse.html', {"asset": asset, "type": asset_type, 'graph':graph, "form":form})
    #
    #     else:
    #         return render(request, 'assets/browse.html')
    #
    # return render(request, 'assets/browse.html')
