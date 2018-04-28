import datetime
import plotly.offline as opy
import plotly.graph_objs as go
from django.shortcuts import render, redirect
from django.contrib.auth import login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import django
from assets.models import Stock, Option, Cryptocurrency
from .models import StockInvestment, OptionInvestment, CryptoInvestment, Account
from accounts.forms import AddInvestment, SignupForm, LoginForm
from assets.update_data.hitbtc import HitBTC


global hitbtc
hitbtc = HitBTC()

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            account = Account()
            account.user = user
            account.save()
            return redirect('home')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(data = request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            form = LoginForm()
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url="/account/login/")
def add_asset(request):
    if request.method == 'POST':
        form = AddInvestment(data = request.POST)
        symbol = request.POST.get("q")
        account = Account.objects.get(user = request.user)
        if form.is_valid():
            if form.cleaned_data.get('purchase_date') != None:
                purchase_date = form.cleaned_data.get('purchase_date')
            else:
                purchase_date = django.utils.timezone.now
            price = form.cleaned_data.get('purchase_price')
            quantity = form.cleaned_data.get('quantity')
            account.add_investment(symbol, price, quantity, purchase_date)
            account.update_chart()
            account.update_current_balance()

        return redirect('investments')
    else:
        form = AddInvestment()
    return render(request, 'accounts/login.html', {'form': form})


@login_required(login_url="/account/login/")
def delete_asset(request):
    if request.method == 'POST':
        symbol = request.POST.get("q")
        account = Account.objects.get(user = request.user)
        investment = account.get_investment(symbol)
        value = float('%.2f' %(investment.asset.last * investment.quantity))
        account.amount_invested -= value
        account.current_balance -= value
        account.amount_invested = '%.2f' % account.amount_invested
        account.current_balance = '%.2f' % account.current_balance
        account.save()
        investment.delete()
        return redirect('investments')

@login_required(login_url="/account/login/")
def investment_view(request):
    account = Account.objects.get(user=request.user)
    all_investments = account.get_all_investments()
    investments = []
    if all_investments:
        values = []
        labels = []
        for symbol in all_investments:
            holdings = 0
            price = 0
            for investment in all_investments[symbol]:
                if not Cryptocurrency.objects.filter(symbol=investment.asset.symbol):
                    price += investment.asset.last
                    performance = '$%.2f' %(investment.asset.last - investment.purchase_price)
                else:
                    price = investment.asset.get_usd_value()
                    performance = '%.8f BTC' %(price - investment.purchase_price)
                holdings +=  price * investment.quantity
                investments.append({symbol:performance})
            values.append(holdings)
            labels.append(symbol)

        fig = {"data": [ {"values": values,
                          "labels": labels,
                          "domain": {"x": [0, 1]},
                          "hoverinfo":"label+percent+name",
                          "hole": .4,
                          "type": "pie"}],
              "layout": {"title":"Investment Breakdown"}}

        config={"displayModeBar": False, "showLink":False}
        piegraph = opy.plot(fig,auto_open=False,config=config, output_type='div')

        chart = account.get_chart()
        dates = list([item for item in chart.keys()])
        prices = list([item for item in chart.values()])

        trace = go.Scatter(x = dates, y = prices)

        data=go.Data([trace])
        config={"displayModeBar": False, "showLink":False}
        layout=go.Layout(title="Investment Performance", xaxis={'title':'Date'}, yaxis={'title':'Price'})
        figure=go.Figure(data=data,layout=layout)
        linegraph = opy.plot(figure, auto_open=False,config=config, output_type='div')

        return render(request, 'accounts/investments.html', {"investments":investments,'linegraph':linegraph,'piegraph':piegraph,"account":account})
    return render(request, 'accounts/investments.html',{"investments":None,'linegraph': None,'piegraph':None,"account":account})

@login_required(login_url="/account/login/")
def performance_view(request,symbol):
    user_obj = request.user
    user = User.objects.get(username = user_obj.get_username())
    if Stock.objects.filter(symbol=symbol):
        asset = Stock.objects.get(symbol = symbol)
        if StockInvestment.objects.filter(investor = user, asset = asset):
            investment = StockInvestment.objects.get(investor = user, asset = asset)
            asset_type = "stock"
            performance = '$%.2f' %(asset.last - investment.purchase_price)

    elif Cryptocurrency.objects.filter(symbol = symbol):
        asset = Cryptocurrency.objects.get(symbol = symbol)
        if CryptoInvestment.objects.filter(investor = user, asset = asset):
            investment = CryptoInvestment.objects.get(investor = user, asset = asset)
            asset_type = "crypto"
            performance = '%.8f BTC' %(asset.last - investment.purchase_price)

    prices = []
    dates = []
    investment.asset.update_week_chart()
    for data in investment.asset.get_week_chart():
        prices.append(data["close"])
        dates.append(data["time"])

    trace = go.Scatter(x = dates, y = prices)

    data=go.Data([trace])
    layout=go.Layout(title="Investment performance", xaxis={'title':'Date'}, yaxis={'title':'$'})
    figure=go.Figure(data=data,layout=layout)
    config={"displayModeBar": False, "showLink":False}
    graph = opy.plot(figure, auto_open=False,config=config, output_type='div')

    return render(request, 'accounts/performance.html', {"investment":investment, 'graph':graph, "performance":performance,'type':asset_type})
