import os, pathlib, shutil
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib import messages
from dateutil import parser
from .forms import (
    UserRegistrationForm, 
    ImageForm,
    AddReceiptToExpenseForm
)
from .models import Shopping, Item, Receipt
from .image_processing import scan
from expenses.models import Category, Expense
from django.contrib.auth.decorators import login_required
from django.conf import settings as conf_settings
from django.core.paginator import Paginator
from datetime import datetime


@login_required(login_url='/scanner/upload_receipt')
def receipt_upload_view(request):
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        
        if form.is_valid():
            img = form.cleaned_data.get("receipt_image")
            receipt = Receipt(owner=request.user, img=img)
            receipt.save()

            img_path = receipt.img.path
            context = scan(img_path)

            if not context['company']:
                context['company'] = 'company name required'
            
            if not context['address']:
                context['address'] = 'address required'

            if not context['full_price']:
                context['full_price'] = 0.00
            
            img_file = os.path.basename(img_path)
            current_date = datetime.today().strftime('%Y-%m-%d')
            date = parser.parse(context['date']) if context['date'] else current_date
            new_shop = Shopping(owner=request.user, 
                                shop_name=context['company'], 
                                date=date, 
                                place=context['address'], 
                                full_price=context['full_price'],
                                img_file=img_file
                            )
            new_shop.save()

            if context['items']:
                for item in context['items']:
                    new_item = Item(shopping=new_shop, item=item['description'], price=item['price'])
                    new_item.save()

            # After successful image upload, the image file will be moved to media folder
            image_file_name = os.path.basename(img_path)
            root_dir = pathlib.Path(conf_settings.PROJECT_PATH).parent
            dest_file = os.path.join(root_dir, 'media')
            shutil.move(img_path, dest_file)
            if image_file_name in os.listdir(os.path.join(root_dir, 'receipts')):
                os.remove(os.path.join(root_dir, 'receipts', image_file_name))

            # return render(request, 'scanenr/receipt_detail.html', context)
            return redirect('receipt_edit_view', id=new_shop.id)
    else:
        form = ImageForm()

    receipts = Receipt.objects.filter(owner=request.user).count()
    shoppings = Shopping.objects.filter(owner=request.user).count()
    ctx = {"form": form, 'receipts':receipts, 'shoppings': shoppings}
    return render(request, "scanner/receipt_upload.html", ctx)


@login_required(login_url='/scanner/receipt_table')
def receipt_table_view(request):
    shop = Shopping.objects.filter(owner=request.user).values()
    context = { 'shop': shop }
    return render(request, 'scanner/receipt_table.html', context)


@login_required(login_url='/scanner/addto_expense')
def receipt_addto_expense_view(request, id):
    obj = get_object_or_404(Shopping, pk=id)
    form = AddReceiptToExpenseForm(request.POST, instance=obj)
    categories = Category.objects.all()

    description = obj.shop_name + " : " + obj.place
    date = obj.date
    full_price = obj.full_price

    context = {
        'shopping_id': id,
        'form': form,
        'categories': categories,
        'price': full_price,
        'description': description,
        'date': date,
    }

    if request.method == 'GET':
        return render(request, 'scanner/receipt_addto_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is a required field')
            return render(request, 'scanner/receipt_addto_expense.html', context)

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is a required field')
            return render(request, 'scanner/receipt_addto_expense.html', context)
        

        category = request.POST['category']
        if not category:
            messages.error(request, 'Category is a required field')
            return render(request, 'scanner/receipt_addto_expense.html', context)

        date = request.POST['expense_date']
        if not date:
            messages.error(request, 'Date is a required field')
            return render(request, 'scanner/receipt_addto_expense.html', context)

    Expense.objects.create(owner=request.user,
                           amount=amount, description=description, category=category, date=date)
    obj.delete()
    messages.success(request, 'Expense saved successfully')
    return redirect('expenses')


@login_required(login_url='/scanner/edit_receipt')
def receipt_edit_view(request, id):
    shopping = Shopping.objects.get(pk=id)
    context = {
        'shopping_id': shopping.id,
        'full_price': shopping.full_price,
        'shop_name': shopping.shop_name,
        'place': shopping.place,
        'date': shopping.date
    }
    if request.method == 'GET':
        return render(request, 'scanner/receipt_edit.html', context)
    if request.method == 'POST':
        full_price = request.POST['full_price']
        if not full_price:
            messages.error(request, 'Full price is a required field')
            return render(request, 'scanner/receipt_edit.html', context)

        shop_name = request.POST['shop_name']
        if not shop_name:
            messages.error(request, 'Shop name is a required field')
            return render(request, 'scanner/receipt_edit.html', context)

        date = request.POST['date']
        

        place = request.POST['place']
        if not place:
            messages.error(request, 'Place is a required field')
            return render(request, 'scanner/receipt_edit.html', context)

        shopping.owner = request.user
        shopping.full_price = full_price
        shopping.date = date
        shopping.shop_name = shop_name
        shopping.place = place

        shopping.save()
        messages.success(request, 'Receipt updated successfully')
        return redirect('receipt_table_view')
    # return render(request, 'scanner/receipt_edit.html', context)


@login_required(login_url='/scanner/remove_receipt')
def receipt_remove_view(request, id):
    shopping = Shopping.objects.filter(pk=id)
    shopping.delete()
    messages.success(request, 'Receipt removed')
    return redirect('receipt_table_view')


@login_required(login_url='/scanner/view_receipt_image')
def receipt_photos_view(request):
    objs = Receipt.objects.filter(owner__username=request.user).values_list()
    receipts_images = [ [obj[0], os.path.basename(obj[2])] for obj in objs]
    paginator = Paginator(receipts_images, 3)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = { 'page_obj': page_obj }
    return render(request, 'scanner/receipt_photos.html', context)


@login_required(login_url='/scanner/receipt_photo')
def receipt_photo_view(request, media_name):
    objs = Receipt.objects.filter(owner__username=request.user).values_list()
    receipts_images = [[obj[0], os.path.basename(obj[2])] for obj in objs]
    media_url = 'media/'+ str(media_name)
    paginator = Paginator(receipts_images, 3)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = { 'page_obj': page_obj, 'media_url': media_url}
    return render(request, 'scanner/receipt_photos.html', context)


@login_required(login_url='/scanner/receipt_photo_delete')
def receipt_photo_delete_view(request, id):
    """
    Remove the image path of an scanned receipt from database 
    and also the image file from server directory
    """
    receipt = Receipt.objects.get(pk=id)
    img_path = receipt.img.path
    receipt.delete()
    # os.remove(img_path)
    messages.success(request, 'Receipt image removed')
    return redirect('receipt_photos_view')


def receipt_detail_view(request, id):
    shop = Shopping.objects.filter(id=id).values()
    items = Item.objects.filter(shopping_id=id).values()
    context = { 'shop': shop, 'items': items }
    return render(request, 'scanner/receipt_detail.html', context)


def receipt_table_all_delete_view(request):
    Shopping.objects.filter(owner=request.user).delete()
    return redirect('receipt_table_view')


def receipt_photos_all_delete_view(request):
    Receipt.objects.filter(owner=request.user).delete()
    return redirect('receipt_photos_view')


def receipt_and_photos_all_delete_view(request):
    Shopping.objects.filter(owner=request.user).delete()
    Receipt.objects.filter(owner=request.user).delete()
    return redirect('receipt_upload_view')
