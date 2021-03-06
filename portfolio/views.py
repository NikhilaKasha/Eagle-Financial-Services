from django.http import HttpResponse
from matplotlib import pylab
from pylab import *
import PIL, PIL.Image
from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.db.models import Sum
from django.core.mail import EmailMessage
from django.views.generic import View
from .serializers import CustomerSerializer
from .serializers import InvestmentSerializer
from .serializers import StockSerializer

try:
    import simplejson as json
except ImportError:
    import json
from rest_framework.views import APIView
from rest_framework.response import Response



from django.http import HttpResponse
from django.views.generic import View
from django.template.loader import render_to_string
# from utils import render_to_pdf
from django.template.loader import get_template
from weasyprint import HTML, CSS

now = timezone.now()


def home(request):
    return render(request, 'portfolio/home.html',
                  {'portfolio': home})


@login_required
def customer_list(request):
    customer = Customer.objects.filter(created_date__lte=timezone.now())
    return render(request, 'portfolio/customer_list.html',
                  {'customers': customer})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        # update
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_date = timezone.now()
            customer.save()
            customer = Customer.objects.filter(created_date__lte=timezone.now())
            return render(request, 'portfolio/customer_list.html',
                          {'customers': customer})
    else:
        # edit
        print("helo")
        form = CustomerForm(instance=customer)
    return render(request, 'portfolio/customer_edit.html', {'form': form})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('portfolio:customer_list')


@login_required
def stock_list(request):
    stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
    return render(request, 'portfolio/stock_list.html', {'stocks': stocks})


@login_required
def stock_new(request):
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html',
                          {'stocks': stocks})
    else:
        form = StockForm()
        # print("Else")
    return render(request, 'portfolio/stock_new.html', {'form': form})


@login_required
def stock_edit(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == "POST":
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save()
            # stock.customer = stock.id
            stock.updated_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
    else:
        # print("else")
        form = StockForm(instance=stock)
    return render(request, 'portfolio/stock_edit.html', {'form': form})


@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.delete()
    return redirect('portfolio:stock_list')


@login_required
def investment_list(request):
    investment = Investment.objects.filter(acquired_date__lte=timezone.now())
    return render(request, 'portfolio/investment_list.html',
                  {'investments': investment})


@login_required
def investment_new(request):
    if request.method == "POST":
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.created_date = timezone.now()
            investment.save()
            investment = Investment.objects.filter(acquired_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html',
                          {'investments': investment})
    else:
        form = InvestmentForm()
        # print("Else")
    return render(request, 'portfolio/investment_new.html', {'form': form})


@login_required
def investment_edit(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == "POST":
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            investment = form.save()
            # stock.customer = stock.id
            investment.updated_date = timezone.now()
            investment.save()
            investments = Investment.objects.filter(acquired_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html', {'investments': investment})
    else:
        # print("else")
        form = InvestmentForm(instance=investment)
    return render(request, 'portfolio/investment_edit.html', {'form': form})


@login_required
def investment_delete(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    investment.delete()
    return redirect('portfolio:investment_list')


@login_required
def portfolio(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
    acquired_total = sum_acquired_value['acquired_value__sum']
    recent_total = sum_recent_value['recent_value__sum']
    overall_investment_results = round(recent_total - acquired_total, 2)


    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()


    sumofinitialprice = float(sum_of_initial_stock_value)
    results = sum_current_stocks_value - sumofinitialprice

    context = {'customer': customer,
               'investments': investments,
               'stocks': stocks,
               'sum_acquired_value': sum_acquired_value,
               'sum_recent_value': sum_recent_value,

               'acquired_total': acquired_total,
               'recent_total': recent_total,
               'results': results,

               'overall_investment_results': overall_investment_results,
               'sum_current_stocks_value': sum_current_stocks_value,
               'sum_of_initial_stock_value': sum_of_initial_stock_value, }

    return render(request, 'portfolio/portfolio.html', context)


@login_required
def portfolioINR(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)

    sum_recent_value = 0
    sum_acquired_value = 0

    for investment in investments:
        sum_recent_value += investment.recent_valueINR()
        sum_acquired_value += investment.acquired_valueINR()

    overall_investment_results = round(sum_recent_value - sum_acquired_value, 2)

    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_valueINR()
        sum_of_initial_stock_value += stock.initial_stock_valueINR()

    results = round(sum_current_stocks_value - sum_of_initial_stock_value, 2)

    contextINR = {'customer': customer,
               'investments': investments,
               'stocks': stocks,
               'sum_acquired_value': sum_acquired_value,
               'sum_recent_value': sum_recent_value,

               'results': results,

               'overall_investment_results': overall_investment_results,
               'sum_current_stocks_value': sum_current_stocks_value,
               'sum_of_initial_stock_value': sum_of_initial_stock_value, }


    return render(request, 'portfolio/portfolioINR.html', contextINR)


class ViewPDF(View):

    def get(self, request, pk, *args, **kwargs):
        customer = get_object_or_404(Customer, pk=pk)
        # customers = Customer.objects.filter(created_date__lte=timezone.now())
        investments = Investment.objects.filter(customer=pk)
        stocks = Stock.objects.filter(customer=pk)

        sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
        sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
        acquired_total = sum_acquired_value['acquired_value__sum']
        recent_total = sum_recent_value['recent_value__sum']

        overall_investment_results = round(recent_total - acquired_total, 2)

        # Initialize the value of the stocks
        sum_current_stocks_value = 0
        sum_of_initial_stock_value = 0

        # Loop through each stock and add the value to the total
        for stock in stocks:
            sum_current_stocks_value += stock.current_stock_value()
            sum_of_initial_stock_value += stock.initial_stock_value()

        results = round(sum_current_stocks_value - float(sum_of_initial_stock_value), 2)

        context = {'customer': customer,
                   'investments': investments,
                   'stocks': stocks,
                   'sum_acquired_value': sum_acquired_value,
                   'sum_recent_value': sum_recent_value,

                   'acquired_total': acquired_total,
                   'recent_total': recent_total,
                   'results': results,

                   'overall_investment_results': overall_investment_results,
                   'sum_current_stocks_value': sum_current_stocks_value,
                   'sum_of_initial_stock_value': sum_of_initial_stock_value, }

        html_string = render_to_string('portfolio/portfolio_summary.html', context)
        html = HTML(string=html_string)
        result = html.write_pdf()
        response = HttpResponse(result, content_type='application/pdf')
        return response


class DownloadPDF(View):

    def get(self, request, pk, *args, **kwargs):
        customer = get_object_or_404(Customer, pk=pk)
        # customers = Customer.objects.filter(created_date__lte=timezone.now())
        investments = Investment.objects.filter(customer=pk)
        stocks = Stock.objects.filter(customer=pk)

        sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
        sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
        acquired_total = sum_acquired_value['acquired_value__sum']
        recent_total = sum_recent_value['recent_value__sum']

        overall_investment_results = round(recent_total - acquired_total, 2)

        # Initialize the value of the stocks
        sum_current_stocks_value = 0
        sum_of_initial_stock_value = 0

        # Loop through each stock and add the value to the total
        for stock in stocks:
            sum_current_stocks_value += stock.current_stock_value()
            sum_of_initial_stock_value += stock.initial_stock_value()

        results = round(sum_current_stocks_value - float(sum_of_initial_stock_value), 2)

        context = {'customer': customer,
                   'investments': investments,
                   'stocks': stocks,
                   'sum_acquired_value': sum_acquired_value,
                   'sum_recent_value': sum_recent_value,

                   'acquired_total': acquired_total,
                   'recent_total': recent_total,
                   'results': results,

                   'overall_investment_results': overall_investment_results,
                   'sum_current_stocks_value': sum_current_stocks_value,
                   'sum_of_initial_stock_value': sum_of_initial_stock_value, }

        html_string = render_to_string('portfolio/portfolio_summary.html', context)
        html = HTML(string=html_string)
        result = html.write_pdf()
        response = HttpResponse(result, content_type='application/pdf')
        filename = "Portfolio.pdf"
        content = "attachment; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response

class EmailPDF(View):

    def get(self, request, pk, *args, **kwargs):
        customer = get_object_or_404(Customer, pk=pk)
        # customers = Customer.objects.filter(created_date__lte=timezone.now())
        investments = Investment.objects.filter(customer=pk)
        stocks = Stock.objects.filter(customer=pk)

        sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
        sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
        acquired_total = sum_acquired_value['acquired_value__sum']
        recent_total = sum_recent_value['recent_value__sum']

        overall_investment_results = round(recent_total - acquired_total, 2)

        # Initialize the value of the stocks
        sum_current_stocks_value = 0
        sum_of_initial_stock_value = 0

        # Loop through each stock and add the value to the total
        for stock in stocks:
            sum_current_stocks_value += stock.current_stock_value()
            sum_of_initial_stock_value += stock.initial_stock_value()

        results = round(sum_current_stocks_value - float(sum_of_initial_stock_value), 2)

        context = {'customer': customer,
                   'investments': investments,
                   'stocks': stocks,
                   'sum_acquired_value': sum_acquired_value,
                   'sum_recent_value': sum_recent_value,

                   'acquired_total': acquired_total,
                   'recent_total': recent_total,
                   'results': results,

                   'overall_investment_results': overall_investment_results,
                   'sum_current_stocks_value': sum_current_stocks_value,
                   'sum_of_initial_stock_value': sum_of_initial_stock_value, }

        html_string = render_to_string('portfolio/portfolio_summary.html', context)
        html = HTML(string=html_string, base_url=settings.MEDIA_ROOT)
        pdf = html.write_pdf()
        cust_email = customer.email
        email = EmailMessage(
            'Your EFS Portfolio Summary', 'This is an automated e-mail from Eagle Financial Services. Please find the attached PDF document containing the details of your portfolio summary. Do not reply to this e-mail.', '', [cust_email])
        email.attach('Portfolio.pdf', pdf, 'application/pdf')
        email.send()
        return render(request, 'portfolio/email_success.html')

class Graphimage(View):
    def get(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        # customers = Customer.objects.filter(created_date__lte=timezone.now())
        investments = Investment.objects.filter(customer=pk)
        stocks = Stock.objects.filter(customer=pk)

        sum_recent_value = 0
        sum_acquired_value = 0

        for investment in investments:
            sum_recent_value += investment.recent_value
            sum_acquired_value += investment.acquired_value

        overall_investment_results = round(sum_recent_value - sum_acquired_value)

        # Initialize the value of the stocks
        sum_current_stocks_value = 0
        sum_of_initial_stock_value = 0

        # Loop through each stock and add the value to the total
        for stock in stocks:
            sum_current_stocks_value += stock.current_stock_value()
            sum_of_initial_stock_value += stock.initial_stock_value()

        results = round(sum_current_stocks_value - float(sum_of_initial_stock_value))

        # Construct the graph
        inv_type = ['Stocks', 'Non-Stock']
        value = ['Initial', 'Current']
        invest_type = ['Stocks', 'Non-Stock']
        inv_value = [sum_of_initial_stock_value, sum_acquired_value]
        cur_value = [sum_current_stocks_value, sum_recent_value]

        plt.bar([1,2.7], inv_value, width=0.35, color='blue')
        plt.bar([1.35,3.05], cur_value, width=0.35, color='red')
        plt.bar(4.4, results, width=0.35, color='green')
        plt.bar(4.75, overall_investment_results, width=0.35, color='yellow')
        plt.xticks([1.175, 2.875, 4.575], ['Stocks', 'Non-Stock', 'Net Return'])
        plt.legend(['Initial', 'Current', 'Stocks', 'Non-Stock'], loc=1)

        ylabel('Value (USD)')
        title('Overall portfolio performance')
        grid(False)

        # Store image in a string buffer
        buffer = BytesIO()
        canvas = pylab.get_current_fig_manager().canvas
        canvas.draw()
        pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
        pilImage.save(buffer, "PNG")
        pylab.close()

        # Send buffer in a http response the the browser with the mime type image/png set
        return HttpResponse(buffer.getvalue(), content_type="image/png")

# List at the end of the views.py
# Lists all customers
class CustomerList(APIView):

    def get(self,request):
        customers_json = Customer.objects.all()
        serializer = CustomerSerializer(customers_json, many=True)
        return Response(serializer.data)

class InvestmentList(APIView):

    def get(self,request):
        investment_json = Investment.objects.all()
        serializer = InvestmentSerializer(investment_json, many=True)
        return Response(serializer.data)

class StockList(APIView):

    def get(self,request):
        stock_json = Stock.objects.all()
        serializer = StockSerializer(stock_json, many=True)
        return Response(serializer.data)