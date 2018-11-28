import datetime
import json
from threading import Thread
from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import F
from .models import User, Profile, Balance
from .forms import SignupForm, LoginForm, ApiKeyForm

def signup_view(request):
    """ authenticates user if post request, otherwise returns signup.html"""
    if request.method == 'POST':
        form = SignupForm(data = request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=user.email, password=raw_password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            login(request, user)
            return redirect('dashboard')
        else:
            form = LoginForm()
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required(login_url="/account/login/")
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url="/account/login/")
def dashboard_view(request):
    user = User.objects.get(email=request.user.email)
    # Thread(target=user.profile.total_balance).start()
    # user.profile.total_balance()
    # for balance in Balance.objects.filter(user=user):
    #     balance.get_usd_value()
    balances = list(Balance.objects.filter(user=user, usd_value__gt=0))
    usd_values = [item.usd_value for item in balances]
    total_value = sum(usd_values)
    symbols = []
    symbol_balances = []

    exchanges = []
    exchange_balances = []
    exchange_percent = []

    for balance in balances:
        if balance.currency.name not in symbols:
            symbol_balances.append({"symbol":balance.currency.name,'amount':balance.amount,'usd_value':balance.usd_value,'percent':int((balance.usd_value/total_value)*100)})
            symbols.append(balance.currency.name)
        else:
            index = next((index for (index, d) in enumerate(symbol_balances) if d["symbol"] == balance.currency.name), None)
            symbol_balances[index]['amount'] += balance.amount
            symbol_balances[index]['usd_value'] += balance.usd_value
            symbol_balances[index]['percent'] = int((symbol_balances[index]['usd_value']/total_value)*100)

        if balance.currency.exchange.name not in exchanges:
            exchanges.append(balance.currency.exchange.name)
            exchange_balances.append(balance.usd_value)
            exchange_percent.append(int((balance.usd_value/total_value)*100))

        else:
            index = exchanges.index(balance.currency.exchange.name)
            exchange_balances[index] += balance.usd_value
            exchange_percent[index] = int((exchange_balances[index]/total_value)*100)




    symbol_balances = sorted(symbol_balances, key=lambda k: -k['percent'])
    print(exchanges)
    return render(request, 'accounts/dashboard.html',{'balances':symbol_balances,'exchanges':exchanges,'exchange_balances':exchange_balances,'exchange_percent':exchange_percent,'total':total_value})

@login_required(login_url="/account/login/")
def profile_view(request):
    user = User.objects.get(email=request.user.email)
    if request.method == "POST":
        form = ApiKeyForm(data=request.POST)
        if form.is_valid():
            exchange = str(form.cleaned_data.get('exchange'))
            api_key = str(form.cleaned_data.get('api_key'))
            secret_key = str(form.cleaned_data.get('secret_key'))
            if exchange == "Binance":
                user.profile.binance_api_key = api_key
                user.profile.binance_secret_key = secret_key
            elif exchange == "Poloniex":
                user.profile.poloniex_api_key = api_key
                user.profile.poloniex_secret_key = secret_key
            elif exchange == "Coinbase":
                user.profile.coinbase_api_key = api_key
                user.profile.coinbase_secret_key = secret_key
            elif exchange == "HitBTC":
                user.profile.hitbtc_api_key = api_key
                user.profile.hitbtc_secret_key = secret_key
            user.profile.save()
            return redirect('profile')
        else:
            form = ApiKeyForm()
    else:
        form = ApiKeyForm()

    return render(request, 'accounts/profile.html',{'user': user,'form': form})

def get_graph(request):

    response = JsonResponse(dict())
    # response = JsonResponse(dict(assets=list(Asset.objects.filter(balance__gt = 0).order_by('-balance').values('symbol','base','quote','price','balance','entry'))))
    return response

@login_required(login_url="/account/login/")
def investment_view(request):
    pass
    # account = Account.objects.get(user=request.user)
    # all_investments = .get_all_investments()
    # investments = []
    # values = []
    # labels = []
    # def get_pie_data(symbol):
    #     nonlocal values,labels,investments,all_investments
    #     holdings = 0
    #     price = 0
    #     for investment in all_investments[symbol]:
    #         if not Cryptocurrency.objects.filter(symbol=investment.asset.symbol):
    #             price += investment.asset.last
    #             performance = '$%.2f' %(investment.asset.last - investment.purchase_price)
    #         else:
    #             price = investment.asset.get_usd_value()
    #             performance = '%.8f BTC' %(price - investment.purchase_price)
    #         holdings +=  price * investment.quantity
    #         investments.append({symbol:performance})
    #     values.append(holdings)
    #     labels.append(symbol)
    #
    # threads = []
    # for symbol in all_investments:
    #     process = Thread(target=get_pie_data, args=[symbol])
    #     process.start()
    #     threads.append(process)
    # for process in threads:
    #     process.join()
    #
    # fig = {"data": [ {"values": values,
    #                   "labels": labels,
    #                   "domain": {"x": [0, 1]},
    #                   "hoverinfo":"label+percent+name",
    #                   "hole": .4,
    #                   "type": "pie"}],
    #       "layout": {"title":"Investment Breakdown"}}
    #
    # config={"displayModeBar": False, "showLink":False}
    # piegraph = opy.plot(fig,auto_open=False,config=config, output_type='div')
    #
    # chart = account.get_chart()
    # dates = list([item for item in chart.keys()])
    # prices = list([item for item in chart.values()])
    #
    # trace = go.Scatter(x = dates, y = prices)
    #
    # data=go.Data([trace])
    # config={"displayModeBar": False, "showLink":False}
    # layout=go.Layout(title="Investment Performance", xaxis={'title':'Date'}, yaxis={'title':'Price'})
    # figure=go.Figure(data=data,layout=layout)
    # linegraph = opy.plot(figure, auto_open=False,config=config, output_type='div')
    #
    # return render(request, 'accounts/investments.html', {"investments":investments,'linegraph':linegraph,'piegraph':piegraph,"account":account})
    # return render(request, 'accounts/investments.html',{"investments":None,'linegraph': None,'piegraph':None,"account":account})

@login_required(login_url="/account/login/")
def performance_view(request,symbol):
    pass
    # user_obj = request.user
    # user = User.objects.get(username = user_obj.get_username())
    # if Stock.objects.filter(symbol=symbol):
    #     asset = Stock.objects.get(symbol = symbol)
    #     if StockInvestment.objects.filter(investor = user, asset = asset):
    #         investment = StockInvestment.objects.get(investor = user, asset = asset)
    #         asset_type = "stock"
    #         performance = '$%.2f' %(asset.last - investment.purchase_price)
    #
    # elif Cryptocurrency.objects.filter(symbol = symbol):
    #     asset = Cryptocurrency.objects.get(symbol = symbol)
    #     if CryptoInvestment.objects.filter(investor = user, asset = asset):
    #         investment = CryptoInvestment.objects.get(investor = user, asset = asset)
    #         asset_type = "crypto"
    #         performance = '%.8f BTC' %(asset.last - investment.purchase_price)
    #
    # prices = []
    # dates = []
    # investment.asset.update_week_chart()
    # for data in investment.asset.get_week_chart():
    #     prices.append(data["close"])
    #     dates.append(data["time"])
    #
    # trace = go.Scatter(x = dates, y = prices)
    #
    # data=go.Data([trace])
    # layout=go.Layout(title="Investment performance", xaxis={'title':'Date'}, yaxis={'title':'$'})
    # figure=go.Figure(data=data,layout=layout)
    # config={"displayModeBar": False, "showLink":False}
    # graph = opy.plot(figure, auto_open=False,config=config, output_type='div')
    #
    # return render(request, 'accounts/performance.html', {"investment":investment, 'graph':graph, "performance":performance,'type':asset_type})
