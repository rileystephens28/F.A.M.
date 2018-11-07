import datetime
import plotly.offline as opy
import plotly.graph_objs as go
from threading import Thread
from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import SignupForm, LoginForm

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(data = request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=user.email, password=raw_password)
            login(request, user)
            profile = Profile()
            profile.user = user
            profile.save()
            return redirect('home')
    else:
        form = SignupForm()

    return render(request, 'accounts/base_site/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(data = request.POST)
        if form.is_valid():
            user_id= form.get_user_id()
            user = auth.get_user()
            login(request, user)
            return redirect('home')
        else:
            form = LoginForm()
    else:
        form = LoginForm()
    return render(request, 'accounts/base_site/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

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
