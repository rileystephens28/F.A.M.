from django.shortcuts import render
from .models import Stock, Option, Cryptocurrency
import plotly.offline as opy
import plotly.graph_objs as go
from accounts.forms import AddInvestment

def browse_view(request):
    query = None
    asset = None
    if request.method == 'POST':
        query = request.POST.get('q')
        try:
            query = str(query)
        except ValueError:
            pass
        if query:
            if Stock.objects.filter(symbol = query.upper()):
                if Stock.objects.filter(symbol = query.lower()):
                    asset = Stock.objects.get(symbol = query.lower())
                else:
                    asset = Stock.objects.get(symbol = query.upper())
                asset.update_data()
                asset_type = "stock"

            elif Cryptocurrency.objects.filter(symbol = query.upper()):
                if Cryptocurrency.objects.filter(symbol = query.lower()):
                    asset = Cryptocurrency.objects.get(symbol = query.lower())
                else:
                    asset = Cryptocurrency.objects.get(symbol = query.upper())
                asset.update_data()
                asset_type = "crypto"

            if asset != None:
                asset.update_week_chart()
                chart = asset.get_week_chart()
                Dates = list([item["time"] for item in chart])
                Open = list([item["open"] for item in chart])
                Close = list([item["close"] for item in chart])

                if asset_type == "stock":
                    High = list([item["high"] for item in chart])
                    Low = list([item["low"] for item in chart])


                else:
                    High = list([item["max"] for item in chart])
                    Low = list([item["min"] for item in chart])

                trace = go.Candlestick(x=Dates,
                       open = Open,
                       high = High,
                       low = Low,
                       close = Close)

                data = [trace]
                layout=go.Layout(title="Week Chart", xaxis={'title':'Date'}, yaxis={'title':'Price($)'})
                figure=go.Figure(data=data,layout=layout)
                graph = opy.plot(figure, auto_open=False, output_type='div')

                form = AddInvestment()

                return render(request, 'assets/browse.html', {"asset": asset, "type": asset_type, 'graph':graph, "form":form})

        else:
            return render(request, 'assets/browse.html')

    return render(request, 'assets/browse.html')
