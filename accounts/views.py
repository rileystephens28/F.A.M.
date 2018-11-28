import datetime
import json
from threading import Thread
from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import F
from .models import User, Profile, Balance
from currencies.models import CurrencyPair
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

    balances = list(Balance.objects.filter(user=user, usd_value__gt=1))
    usd_values = [item.usd_value for item in balances]
    total_value = float("%.2f"%sum(usd_values))
    colors = ["purple","red","blue","green"]
    symbols = []
    symbol_names = []
    symbol_balances = []

    exchanges = []
    exchange_balances = []

    for balance in balances:
        if balance.currency.name not in symbols:
            symbol_balances.append({"symbol":balance.currency.name,'amount':balance.amount,'usd_value':balance.usd_value,'percent':int((balance.usd_value/total_value)*100)})
            symbols.append(balance.currency)
            symbol_names.append(balance.currency.name)
        else:
            index = symbols.index(balance.currency.name)
            symbol_balances[index]['amount'] += balance.amount
            symbol_balances[index]['usd_value'] += balance.usd_value
            symbol_balances[index]['percent'] = int((symbol_balances[index]['usd_value']/total_value)*100)

        if balance.currency.exchange.name not in exchanges:
            exchanges.append(balance.currency.exchange.name)
            exchange_balances.append({'name':balance.currency.exchange.name,'amount':balance.usd_value,'percent':int((balance.usd_value/total_value)*100),'color':colors[len(exchange_balances)]})
        else:
            index = exchanges.index(balance.currency.exchange.name)
            exchange_balances[index]['amount'] += balance.usd_value
            exchange_balances[index]['percent'] = int((exchange_balances[index]['amount']/total_value)*100)

    symbol_balances = sorted(symbol_balances, key=lambda k: -k['usd_value'])
    symbols = [{'symbol':item.symbol,"price":item.get_usd_value(),'exchange':item.exchange.name} for item in symbols]

    return render(request, 'accounts/dashboard.html',{'balances':symbol_balances,'symbols':symbols,'exchange_balances':exchange_balances,'total':total_value})

@login_required(login_url="/account/login/")
def tax_view(request):
    # user = User.objects.get(email=request.user.email)
    # if request.method == "POST":
    #     form = ApiKeyForm(data=request.POST)
    #     if form.is_valid():
    #         exchange = str(form.cleaned_data.get('exchange'))
    #         api_key = str(form.cleaned_data.get('api_key'))
    #         secret_key = str(form.cleaned_data.get('secret_key'))
    #         if exchange == "Binance":
    #             user.profile.binance_api_key = api_key
    #             user.profile.binance_secret_key = secret_key
    #         elif exchange == "Poloniex":
    #             user.profile.poloniex_api_key = api_key
    #             user.profile.poloniex_secret_key = secret_key
    #         elif exchange == "Coinbase":
    #             user.profile.coinbase_api_key = api_key
    #             user.profile.coinbase_secret_key = secret_key
    #         elif exchange == "HitBTC":
    #             user.profile.hitbtc_api_key = api_key
    #             user.profile.hitbtc_secret_key = secret_key
    #         user.profile.save()
    #         return redirect('profile')
    #     else:
    #         form = ApiKeyForm()
    # else:
    #     form = ApiKeyForm()

    return render(request, 'accounts/tax_docs.html')


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
