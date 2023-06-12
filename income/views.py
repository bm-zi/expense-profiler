from userpreferences.models import UserPreference
from django.http import JsonResponse, HttpResponse
import json
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Source, Income
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
import datetime
import csv
import xlwt
from dateutil.relativedelta import relativedelta
# Create your views here.


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = Income.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Income.objects.filter(
            date__istartswith=search_str, owner=request.user) | Income.objects.filter(
            description__icontains=search_str, owner=request.user) | Income.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/auth/login')
def index(request):
    income = Income.objects.filter(owner=request.user)
    paginator = Paginator(income, 10)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = None
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/auth/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        # get access to previous inputs
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is a required field')
            return render(request, 'income/add_income.html', context)

        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is a required field')
            return render(request, 'income/add_income.html', context)

    Income.objects.create(owner=request.user,
                          amount=amount, description=description, source=source, date=date)
    messages.success(request, 'Income saved successfully')
    return redirect('income')


@login_required(login_url='/auth/login')
def income_edit(request, id):
    income = Income.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }

    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is a required field')
            return render(request, 'income/edit_income.html', context)

        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is a required field')
            return render(request, 'income/edit_income.html', context)

        income.owner = request.user
        income.amount = amount
        income.date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Income updated successfully')
        return redirect('income')


@login_required(login_url='/auth/login')
def income_delete(request, id):
    income = Income.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income removed')
    return redirect('income')


@login_required(login_url='/auth/login')
def income_source_summary(request):
    today_date = datetime.date.today()
    six_months_ago = today_date-datetime.timedelta(days=30*12)
    income_list = Income.objects.filter(owner=request.user,
                                        date__gte=six_months_ago, date__lte=today_date)
    final_rep = {}

    def get_source(income):
        return income.source
    source_list = list(set(map(get_source, income_list)))

    def get_source_amount(source):
        amount = 0
        filtered_by_source = income_list.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    for inc in income_list:
        for y in source_list:
            final_rep[y] = get_source_amount(y)

     # return amount by month
    line_rep = {}

    def get_prev_6_months():
        l = [None]*6
        six_months_prev = datetime.date.today() - relativedelta(months=6)
        five_months_prev = datetime.date.today() - relativedelta(months=5)
        four_months_prev = datetime.date.today() - relativedelta(months=4)
        three_months_prev = datetime.date.today() - relativedelta(months=3)
        two_months_prev = datetime.date.today() - relativedelta(months=2)
        one_month_prev = datetime.date.today() - relativedelta(months=1)
        l[0] = six_months_prev.month
        l[1] = five_months_prev.month
        l[2] = four_months_prev.month
        l[3] = three_months_prev.month
        l[4] = two_months_prev.month
        l[5] = one_month_prev.month
        return l

    date_list = get_prev_6_months()

    def get_month_amount(month):
        amount = 0
        month_first = datetime.date.today().replace(day=1, month=month)
        month_last = month_first+datetime.timedelta(days=30)
        filtered_by_month = income_list.filter(
            date__gte=month_first, date__lte=month_last)
        for item in filtered_by_month:
            amount += item.amount
        return amount

    for inc in income_list:
        for y in date_list:
            line_rep[y] = get_month_amount(y)

    return JsonResponse({'income_source_data': final_rep, 'income_month_data': line_rep}, safe=False)


def stats_view(request):
    return render(request, 'income/stats.html')


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Income' + \
        str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Source', 'Date'])
    income = Income.objects.filter(owner=request.user)
    for i in income:
        writer.writerow([i.amount, i.description,
                        i.source, i.date])
    return response


def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Income' + \
        str(datetime.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Income')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Source', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    rows = Income.objects.filter(owner=request.user).values_list(
        'amount', 'description', 'source', 'date')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response
