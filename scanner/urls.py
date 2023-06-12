from django.urls import path, include
from . import views

urlpatterns = [
    path("receipt_upload/", views.receipt_upload_view, name="receipt_upload_view"),
    path('receipt_edit/<int:id>', views.receipt_edit_view, name="receipt_edit_view"),
    path("receipt_addto_expense/<int:id>", 
         views.receipt_addto_expense_view, 
         name="receipt_addto_expense_view"
     ),
    path("receipt_table/", views.receipt_table_view, name="receipt_table_view"),
    path("receipt_detail/<int:id>", views.receipt_detail_view, name="receipt_detail_view"),
    path("receipt_remove/<int:id>", views.receipt_remove_view, name="receipt_remove_view"),
    path("receipt_photos/", views.receipt_photos_view, name="receipt_photos_view"),
    path("receipt_photo/<path:media_name>", views.receipt_photo_view, name="receipt_photo_view"),
    path("receipt_photo_delete/<int:id>", views.receipt_photo_delete_view, name="receipt_photo_delete_view"),
    
    path("receipt_table_all_delete/", 
         views.receipt_table_all_delete_view, 
         name="receipt_table_all_delete_view"
     ),
    
    path("receipt_photos_all_delete/", 
         views.receipt_photos_all_delete_view, 
         name="receipt_photos_all_delete_view"
     ),
    
    path("receipt_and_photos_all_delete/", 
            views.receipt_and_photos_all_delete_view,
            name="receipt_and_photos_all_delete_view"
     )
]