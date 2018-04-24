import datetime
import plotly.offline as opy
import plotly.graph_objs as go
from django.shortcuts import render, redirect
from django.contrib.auth import login,logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
import django
from assets.models import Stock, Option, Cryptocurrency
from .models import StockInvestment, OptionInvestment, CryptoInvestment, Account
from accounts.forms import AddInvestment
from assets.update_data.hitbtc import HitBTC

global hitbtc
hitbtc = HitBTC()

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            account = Account()
            account.user = user
            account.save()
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            form = AuthenticationForm()
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url="/account/login/")
def add_asset(request):
    if request.method == 'POST':
        form = AddInvestment(data = request.POST)
        asset = request.POST.get("q")
        user = request.user
        if form.is_valid():
            if Cryptocurrency.objects.filter(symbol = asset.upper()):
                investment = CryptoInvestment()
                investment.asset = Cryptocurrency.objects.get(symbol = asset)
            elif Stock.objects.filter(symbol = asset.upper()):
                investment = StockInvestment()
                investment.asset = Stock.objects.get(symbol = asset)
            elif Option.objects.filter(symbol = asset.upper()):
                investment = OptionInvestment()
                investment.asset = Option.objects.get(symbol = asset)
            investment.investor = User.objects.get(username = user.get_username())
            if form.cleaned_data.get('purchase_price'):
                investment.purchase_price = form.cleaned_data.get('purchase_price')
            investment.purchase_price = form.cleaned_data.get('purchase_price')
            investment.quantity = form.cleaned_data.get('quantity')
            investment.purchase_date = django.utils.timezone.now
            investment.save()

        return redirect('investments')
    else:
        form = AddInvestment()
    return render(request, 'accounts/login.html', {'form': form})


@login_required(login_url="/account/login/")
def delete_asset(request):
    if request.method == 'POST':
        asset = request.POST.get("q")
        user = request.user
        if Cryptocurrency.objects.filter(symbol = asset.upper()):
            if CryptoInvestment.objects.filter(asset=Cryptocurrency.objects.get(symbol=asset.upper()),investor=User.objects.get(username=user.get_username())):
                investment = CryptoInvestment.objects.get(asset=Cryptocurrency.objects.get(symbol=asset.upper()),investor=User.objects.get(username=user.get_username()))
                investment.delete()
        elif Stock.objects.filter(symbol = asset.upper()):
            if StockInvestment.objects.filter(asset=Stock.objects.get(symbol=asset.upper()),investor=User.objects.get(username=user.get_username())):
                investment = StockInvestment.objects.get(asset=Stock.objects.get(symbol=asset.upper()),investor=User.objects.get(username=user.get_username()))
                investment.delete()
        elif Option.objects.filter(symbol = asset.upper()):
            if OptionInvestment.objects.filter(asset=Option.objects.get(symbol=asset.upper()),investor=User.objects.get(username=user.get_username())):
                investment = StockInvestment.objects.get(asset=Option.objects.get(symbol=asset.upper()),investor=User.objects.get(username=user.get_username()))
                investment.delete()
        return redirect('investments')

@login_required(login_url="/account/login/")
def investment_view(request):
    user_obj = request.user
    user = User.objects.get(username=user_obj.get_username())
    account = Account.objects.get(user=user)
    all_investments = account.get_all_investments()
    values = []
    labels = []
    account.update_current_balance()
    for symbol in all_investments:
        holdings = 0
        price = 0
        print(symbol)
        for investment in all_investments[symbol]:
            if Stock.objects.filter(symbol=investment.asset.symbol) or Option.objects.filter(symbol=investment.asset.symbol):
                price += investment.asset.last
            elif "USD" not in  investment.asset.symbol:
                base = investment.asset.symbol.replace("BTC","")
                usd_ticker = hitbtc.get_ticker(symbol = base + "USD")["last"]
                price += float(usd_ticker)
            else:
                price += investment.asset.last
            holdings +=  price * investment.quantity
        values.append(holdings)
        labels.append(symbol)

    fig = {"data": [ {"values": values,
                      "labels": labels,
                      "domain": {"x": [0, .48]},
                      "hoverinfo":"label+percent+name",
                      "hole": .4,
                      "type": "pie"}],
          "layout": {"title":"Investment Breakdown",
                     "annotations": [{"font": {"size": 20},
                                      "showarrow": False,
                                      "text": "",
                                      "x": 0.20,
                                      "y": 0.5}]
                    }
          }
    piegraph = opy.plot(fig, auto_open=False, output_type='div')

    investments = []
    for symbol in all_investments:
        purchase_price = 0
        current_value = 0
        price = all_investments[symbol][0].asset.update_data()
        for investment in all_investments[symbol]:
            purchase_price += investment.purchase_price * investment.quantity
            current_value += investment.asset.bid * investment.quantity
            chart = investment.asset.get_week_chart()
            prices = list([item["close"] for item in chart])
            dates = list([item["time"] for item in chart])
        performance = '%.8f' %(current_value - purchase_price)
        investments.append({symbol:performance})

    trace = go.Scatter(x = dates, y = prices)

    data=go.Data([trace])
    layout=go.Layout(title="Investment Performance", xaxis={'title':'Date'}, yaxis={'title':'$'})
    figure=go.Figure(data=data,layout=layout)
    linegraph = opy.plot(figure, auto_open=False, output_type='div')

    return render(request, 'accounts/investments.html', {"investments":investments,'linegraph':linegraph,'piegraph':piegraph})

@login_required(login_url="/account/login/")
def performance_view(request,symbol):
    user_obj = request.user
    user = User.objects.get(username = user_obj.get_username())
    if Stock.objects.filter(symbol = symbol):
        asset = Stock.objects.get(symbol = symbol)
        if StockInvestment.objects.filter(investor = user, asset = asset):
            investment = StockInvestment.objects.get(investor = user, asset = asset)
            asset_type = "stock"

    elif Cryptocurrency.objects.filter(symbol = symbol):
        asset = CryptoInvestment.objects.get(symbol = symbol)
        if CryptoInvestment.objects.filter(investor = user, asset = asset):
            investment = CryptoInvestment.objects.get(investor = user, asset = asset)
            asset_type = "crypto"

    prices = []
    dates = []
    investment.asset.update_week_chart()
    for data in investment.asset.get_month_chart():
        prices.append(data["price"])
        dates.append(data["time"])

    trace = go.Scatter(x = dates, y = prices)

    data=go.Data([trace])
    layout=go.Layout(title="Investment performance", xaxis={'title':'Date'}, yaxis={'title':'$'})
    figure=go.Figure(data=data,layout=layout)
    graph = opy.plot(figure, auto_open=False, output_type='div')

    return render(request, 'accounts/performance.html', {"investment":investment, 'graph':graph, 'type':asset_type})
