from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
import django
from assets.models import Stock, Option, Cryptocurrency
from .models import StockInvestment, OptionInvestment, CryptoInvestment
import datetime
import plotly.offline as opy
import plotly.graph_objs as go





def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            form = UserCreationForm()
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


@login_required(login_url="/account/login/")
def add_asset(request):
    if request.method == 'POST':
        asset = request.POST.get("q")
        user = request.user
        if Cryptocurrency.objects.filter(symbol = asset.upper()):
            if not CryptoInvestment.objects.filter(asset=Cryptocurrency.objects.get(symbol=asset.upper()),investor=User.objects.get(username=user.get_username())):
                investment = CryptoInvestment()
                investment.investor = User.objects.get(username = user.get_username())
                investment.asset = Cryptocurrency.objects.get(symbol = request.POST.get("q"))
                investment.purchase_price = (investment.asset.bid + investment.asset.ask)/2
                investment.purchase_date = django.utils.timezone.now
                investment.save()
        elif Stock.objects.filter(symbol = asset.upper()):
            if not StockInvestment.objects.filter(asset=Stock.objects.get(symbol=asset.upper()),investor=User.objects.get(username=user.get_username())):
                investment = StockInvestment()
                investment.investor = User.objects.get(username = user.get_username())
                investment.asset = Stock.objects.get(symbol = request.POST.get("q"))
                investment.purchase_price = (investment.asset.bid + investment.asset.ask)/2
                investment.purchase_date = django.utils.timezone.now
                investment.save()
        return redirect('investments')


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
        return redirect('investments')

@login_required(login_url="/account/login/")
def investment_view(request):
    assets = []
    user_obj = request.user
    user = User.objects.get(username = user_obj.get_username())
    if StockInvestment.objects.filter(investor = user):
        for stock in StockInvestment.objects.filter(investor = user):
            assets.append(stock.asset)

    if CryptoInvestment.objects.filter(investor = user):
        for crypto in CryptoInvestment.objects.filter(investor = user):
            assets.append(crypto.asset)
    print(assets)
    return render(request, 'accounts/investments.html', {"assets":assets})

@login_required(login_url="/account/login/")
def performance_view(request,symbol):
    user_obj = request.user
    user = User.objects.get(username = user_obj.get_username())
    if Stock.objects.filter(symbol = symbol):
        asset = Stock.objects.get(symbol = symbol)
        if StockInvestment.objects.filter(investor = user, asset = asset):
            investment = StockInvestment.objects.get(investor = user, asset = asset)

    elif Cryptocurrency.objects.filter(symbol = symbol):
        asset = CryptoInvestment.objects.get(symbol = symbol)
        if CryptoInvestment.objects.filter(investor = user, asset = asset):
            investment = CryptoInvestment.objects.get(investor = user, asset = asset)

    prices = []
    dates = []
    print(investment.date)
    investment.asset.update_week_chart()
    investment.asset.update_month_chart()

    for data in investment.asset.get_month_chart():
        prices.append(data["price"])
        dates.append(data["time"])

    trace = go.Scatter(x = dates, y = prices)

    data=go.Data([trace])
    layout=go.Layout(title="Investment performance", xaxis={'title':'Date'}, yaxis={'title':'$'})
    figure=go.Figure(data=data,layout=layout)
    graph = opy.plot(figure, auto_open=False, output_type='div')
    #print(graph)

    return render(request, 'accounts/performance.html', {"investment":investment, 'graph':graph})
