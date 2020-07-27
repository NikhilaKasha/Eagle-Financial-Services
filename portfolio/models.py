from django.db import models
from django.utils import timezone

import urllib, json
from django.core.cache import cache

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    cust_number = models.IntegerField(blank=False, null=False)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=10)
    email = models.EmailField(max_length=200)
    cell_phone = models.CharField(max_length=50)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now_add=True)

    def created(self):
        self.created_date = timezone.now()
        self.save()

    def updated(self):
        self.updated_date = timezone.now()
        self.save()

    def __str__(self):
        return str(self.cust_number)


class Stock(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='stocks')
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    shares = models.DecimalField (max_digits=10, decimal_places=1)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(default=timezone.now, blank=True, null=True)

    def created(self):
        self.recent_date = timezone.now()
        self.save()

    def __str__(self):
        return str(self.customer)

    def USD_INR(self):
        cache_INR = 'INR'
        cache_USD = 'USD'
        cache_time = 86400
        EUR_INR = cache.get(cache_INR)
        EUR_USD = cache.get(cache_USD)
        if not EUR_INR or not EUR_USD:
            url = 'http://data.fixer.io/api/latest?access_key=799b768b1f610aab56d40eee732733a5&format=1'
            response = urllib.request.urlopen(url)
            json_data = json.loads(response.read())
            EUR_INR = json_data.get('rates').get('INR')
            EUR_USD = json_data.get('rates').get('USD')
        cache.set(cache_INR,EUR_INR,cache_time)
        cache.set(cache_USD, EUR_USD, cache_time)
        USD_INR = float(EUR_INR)/float(EUR_USD)
        return USD_INR

    def purchase_priceINR(self):
        return round(float(self.purchase_price) * self.USD_INR(), 2)

    def initial_stock_value(self):
        return self.shares * self.purchase_price

    def initial_stock_valueINR(self):
        return round(float(self.shares) * float(self.purchase_price) * self.USD_INR(), 2)

    def current_stock_price(self): #current stock price in USD
        cache_stockprice = 'stk_price'
        cache_time = 300
        open_price = cache.get(cache_stockprice)
        if not open_price:
            symbol_f = str(self.symbol)
            main_api = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&amp;symbol='
            api_key = '&interval=1min&apikey=08IT8XH58DEISDPP'
            url = main_api + symbol_f + api_key
            response = urllib.request.urlopen(url)
            json_data = json.loads(response.read())
            open_price = json_data.get('Global Quote').get('02. open')
        cache.set(cache_stockprice, open_price, cache_time)
        share_value = float(open_price)
        return share_value

    def current_stock_priceINR(self):
        return round(self.current_stock_price() * self.USD_INR(), 2)

    def current_stock_value(self):
            return self.current_stock_price() * float(self.shares)

    def current_stock_valueINR(self):
            return round(self.current_stock_price() * float(self.shares) * self.USD_INR(), 2)


class Investment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='investments')
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    acquired_value = models.DecimalField(max_digits=10, decimal_places=2)
    acquired_date = models.DateField(default=timezone.now, blank=True, null=True)
    recent_value = models.DecimalField(max_digits=10, decimal_places=2)
    recent_date = models.DateField(default=timezone.now, blank=True, null=True)

    def created(self):
        self.acquired_date = timezone.now()
        self.save()

    def updated(self):
        self.recent_date = timezone.now()
        self.save()

    def __str__(self):
        return str(self.customer)

    def USD_INR(self):
        cache_INR = 'INR'
        cache_USD = 'USD'
        cache_time = 86400
        EUR_INR = cache.get(cache_INR)
        EUR_USD = cache.get(cache_USD)
        if not EUR_INR or not EUR_USD:
            url = 'http://data.fixer.io/api/latest?access_key=799b768b1f610aab56d40eee732733a5&format=1'
            response = urllib.request.urlopen(url)
            json_data = json.loads(response.read())
            EUR_INR = json_data.get('rates').get('INR')
            EUR_USD = json_data.get('rates').get('USD')
        cache.set(cache_INR, EUR_INR, cache_time)
        cache.set(cache_USD, EUR_USD, cache_time)
        USD_INR = float(EUR_INR) / float(EUR_USD)
        return USD_INR

    def acquired_valueINR(self):
        return round(float(self.acquired_value) * self.USD_INR(), 2)

    def recent_valueINR(self):
        return round(float(self.recent_value) * self.USD_INR(), 2)