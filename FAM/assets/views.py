from django.shortcuts import render
from .models import Stock, Option, Cryptocurrency

def browse_view(request):
    if request.method == 'POST':
        query = request.POST.get('q')
        try:
            query = str(query)
        except ValueError:
            query = None
            asset = None
        if query:
            if Stock.objects.filter(symbol = query.upper()):
                if Stock.objects.filter(symbol = query.lower()):
                    asset = Stock.objects.get(symbol = query.lower())
                else:
                    asset = Stock.objects.get(symbol = query.upper())
                asset.update_data()
                asset_type = "stock"
                return render(request, 'assets/browse.html', {"asset": asset, "type": asset_type})

            elif Cryptocurrency.objects.filter(symbol = query.upper()):
                if Cryptocurrency.objects.filter(symbol = query.lower()):
                    asset = Cryptocurrency.objects.get(symbol = query.lower())
                else:
                    asset = Cryptocurrency.objects.get(symbol = query.upper())
                asset.update_data()
                asset_type = "crypto"
                return render(request, 'assets/browse.html', {"asset": asset, "type": asset_type})

            else:
                return render(request, 'assets/browse.html')

    return render(request, 'assets/browse.html')
