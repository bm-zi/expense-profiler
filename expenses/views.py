
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
import datetime
import csv
import xlwt
from dateutil.relativedelta import relativedelta

# Create your views here.


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/auth/login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = None
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/auth/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        # get access to previous inputs
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is a required field')
            return render(request, 'expenses/add_expense.html', context)

        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is a required field')
            return render(request, 'expenses/add_expense.html', context)

    Expense.objects.create(owner=request.user,
                           amount=amount, description=description, category=category, date=date)
    messages.success(request, 'Expense saved successfully')
    return redirect('expenses')


@login_required(login_url='/auth/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }

    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is a required field')
            return render(request, 'expenses/edit_expense.html', context)

        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is a required field')
            return render(request, 'expenses/edit_expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated successfully')
        return redirect('expenses')


@login_required(login_url='/auth/login')
def expense_delete(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')


@login_required(login_url='/auth/login')
# returns amount by category
def expense_category_summary(request):
    today_date = datetime.date.today()
    six_months_ago = today_date-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=today_date)
    final_rep = {}

    def get_category(expense):
        return expense.category
    category_list = list(set(map(get_category, expenses)))

    def get_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    for ex in expenses:
        for y in category_list:
            final_rep[y] = get_category_amount(y)

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
        filtered_by_month = expenses.filter(
            date__gte=month_first, date__lte=month_last)
        for item in filtered_by_month:
            amount += item.amount
        return amount

    for ex in expenses:
        for y in date_list:
            line_rep[y] = get_month_amount(y)

    return JsonResponse({'expense_category_data': final_rep, 'expense_month_data': line_rep}, safe=False)


@login_required(login_url='/auth/login')
def stats_view(request):
    return render(request, 'expenses/stats.html')


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.datetime.now())+'.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    expenses = Expense.objects.filter(owner=request.user)
    for expense in expenses:
        writer.writerow([expense.amount, expense.description,
                        expense.category, expense.date])
    return response


def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    rows = Expense.objects.filter(owner=request.user).values_list(
        'amount', 'description', 'category', 'date')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)
    return response


def CategoryList(request):
    """Expense categories"""
    categories = Category.objects.all()
    return render(request, 'expenses/categories.html', {'categories': categories })


def CreateCategory(request):
    if request.method == 'POST':
        category_name = request.POST['category_name']
        category = Category()
        category.name = category_name
        category.save()
        return redirect('category_list')
    
def CategoryDelete(request):
    if request.method == 'POST':
        category_id = request.POST['category_id']
        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(request, 'Expense removed')
        return redirect('category_list')