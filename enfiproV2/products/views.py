from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Category, Product
from products.models import Product

@login_required(login_url="/accounts/login/")
def categories_list_view(request):
    context = {
        "active_icon": "products_categories",
        "categories": Category.objects.all()
    }
    return render(request, "products/categories.html", context=context)

@login_required(login_url="/accounts/login/")
def categories_add_view(request):
    context = {
        "active_icon": "products_categories",
        "category_status": Category.status.field.choices
    }

    if request.method == 'POST':
        data = request.POST
        attributes = {
            "name": data.get('name'),
            "status": data.get('state'),
            "description": data.get('description')
        }

        if Category.objects.filter(**attributes).exists():
            messages.error(request, 'Kategori Zaten Var!', extra_tags="warning")
            return redirect('products:categories_add')

        try:
            Category.objects.create(**attributes)
            messages.success(request, f'Kategori: {attributes["name"]} Oluşturuldu!', extra_tags="success")
            return redirect('products:categories_list')
        except Exception as e:
            messages.error(request, 'Kategori Oluşturulken Hata Oluştu!', extra_tags="danger")
            print(e)
            return redirect('products:categories_add')

    return render(request, "products/categories_add.html", context=context)

@login_required(login_url="/accounts/login/")
def categories_update_view(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        messages.error(request, 'Kategori Bulunamadı!', extra_tags="danger")
        return redirect('products:categories_list')

    context = {
        "active_icon": "products_categories",
        "category_status": Category.status.field.choices,
        "category": category
    }

    if request.method == 'POST':
        data = request.POST
        attributes = {
            "name": data.get('name'),
            "status": data.get('state'),
            "description": data.get('description')
        }

        if Category.objects.filter(**attributes).exclude(id=category_id).exists():
            messages.error(request, 'Bu Kategori Benzeri Zaten Var!', extra_tags="warning")
            return redirect('products:categories_update', category_id=category_id)

        try:
            Category.objects.filter(id=category_id).update(**attributes)
            messages.success(request, f'Category: {attributes["name"]} updated successfully!', extra_tags="success")
            return redirect('products:categories_list')
        except Exception as e:
            messages.error(request, 'Kategori Güncellenirken Hata Oluştu!', extra_tags="danger")
            print(e)
            return redirect('products:categories_update', category_id=category_id)

    return render(request, "products/categories_update.html", context=context)

@login_required(login_url="/accounts/login/")
def categories_delete_view(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(request, f'Kategori: {category.name} silindi!', extra_tags="success")
        return redirect('products:categories_list')
    except Category.DoesNotExist:
        messages.error(request, 'Kategori Bulunamadı!', extra_tags="danger")
        return redirect('products:categories_list')
    except Exception as e:
        messages.error(request, 'Kategori Silinirken Hata Oluştu!', extra_tags="danger")
        print(e)
        return redirect('products:categories_list')

@login_required(login_url="/accounts/login/")
def products_list_view(request):
    context = {
        "active_icon": "products",
        "products": Product.objects.all()
    }
    return render(request, "products/products.html", context=context)

@login_required(login_url="/accounts/login/")
def products_add_view(request):
    # Ürünlerin toplam sayısını al
    last_product = Product.objects.order_by('id').last()
    try:
        if (last_product != None):
          print(last_product.id)
          product = Product.objects.get(id=(last_product.id))
          fields = [
            #{"name": "urun_kod", "label": "Ürün Kodu", "type": "text", "value": str(int(product.urun_kod) + 1)}
            {"name": "urun_kod", "label": "Ürün Kodu", "type": "text", "value": product.urun_kod},
            {"name": "urun_ismi1", "label": "Ürün İsmi 1", "type": "text", "value": product.urun_ismi1},
            {"name": "urun_ismi2", "label": "Ürün İsmi 2", "type": "text", "value": product.urun_ismi2},
            {"name": "urun_grup", "label": "Ürün Grubu", "type": "text", "value": product.urun_grup},
            {"name": "urun_tip", "label": "Ürün Tipi", "type": "text", "value": product.urun_tip},
            {"name": "urun_fiyat", "label": "Ürün Fiyat ₺", "type": "number", "value": product.urun_fiyat},
            {"name": "urun_musteri", "label": "Ürün Müşteri", "type": "text", "value": product.urun_musteri},
            {"name": "urun_barkod", "label": "Ürün Barkod", "type": "number", "value": product.urun_barkod},
            {"name": "urun_qrkod", "label": "Ürün QRkod", "type": "text", "value": product.urun_qrkod},
            {"name": "urun_stt", "label": "Ürün STT", "type": "number", "value": product.urun_stt},
            {"name": "urun_resim", "label": "Ürün Resim", "type": "text", "value": product.urun_resim},
            {"name": "urun_min", "label": "Ürün Min", "type": "number", "value": product.urun_min},
            {"name": "urun_max", "label": "Ürün Max", "type": "number", "value": product.urun_max},
            {"name": "urun_hedef", "label": "Ürün Hedef", "type": "number", "value": product.urun_hedef},
            {"name": "urun_adet_gramaj", "label": "Ürün Adet Gramaj", "type": "number", "value": product.urun_adet_gramaj},
            {"name": "urun_dara", "label": "Ürün Dara", "type": "number", "value": product.urun_dara},
            {"name": "urun_adet", "label": "Ürün Adet", "type": "number", "value": product.urun_adet},
            {"name": "urun_etiket", "label": "Ürün Etiket", "type": "text", "value": product.urun_etiket},
            {"name": "urun_top_etiket", "label": "Ürün Toplam Etiketi", "type": "text", "value": product.urun_top_etiket},
            {"name": "urun_izleme", "label": "Ürün İzleme", "type": "text", "value": product.urun_izleme},
            {"name": "urun_kodtip", "label": "Ürün Kod Tipi", "type": "text", "value": product.urun_kodtip},
            {"name": "urun_tablo", "label": "Ürün Tablo", "type": "text", "value": product.urun_tablo},
            {"name": "urun_mesaj1", "label": "Ürün Mesaj1", "type": "text", "value": product.urun_mesaj1},
            {"name": "urun_mesaj2", "label": "Ürün Mesaj2", "type": "text", "value": product.urun_mesaj2},
            {"name": "urun_mesaj3", "label": "Ürün Mesaj3", "type": "text", "value": product.urun_mesaj3},
            {"name": "urun_mesaj4", "label": "Ürün Mesaj4", "type": "text", "value": product.urun_mesaj4},
            {"name": "urun_mesaj5", "label": "Ürün Mesaj5", "type": "text", "value": product.urun_mesaj5},
            {"name": "urun_mesaj6", "label": "Ürün Mesaj6", "type": "text", "value": product.urun_mesaj6},
            {"name": "urun_mesaj7", "label": "Ürün Mesaj7", "type": "text", "value": product.urun_mesaj7},
            {"name": "urun_mesaj8", "label": "Ürün Mesaj8", "type": "text", "value": product.urun_mesaj8},
            {"name": "urun_mesaj9", "label": "Ürün Mesaj9", "type": "text", "value": product.urun_mesaj9},
            {"name": "urun_tanim", "label": "Ürün Tanımı", "type": "text", "value": product.urun_tanim},
            {"name": "urun_icerik", "label": "Ürün İçeriği", "type": "text", "value": product.urun_icerik},
            {"name": "urun_aciklama", "label": "Ürün Açıklaması", "type": "text", "value": product.urun_aciklama},
            {"name": "urun_mensei", "label": "Ürün Menşei", "type": "text", "value": product.urun_mensei}
          ]
        else:
            product = None
            fields = [
                {"name": "urun_kod", "label": "Ürün Kodu", "type": "text", "value": ""},
                {"name": "urun_ismi1", "label": "Ürün İsmi 1", "type": "text", "value": ""},
                {"name": "urun_ismi2", "label": "Ürün İsmi 2", "type": "text", "value": ""},
                {"name": "urun_grup", "label": "Ürün Grubu", "type": "text", "value": ""},
                {"name": "urun_tip", "label": "Ürün Tipi", "type": "text", "value": ""},
        
                {"name": "urun_fiyat", "label": "Ürün Fiyat ₺", "type": "number", "value": 0},
                {"name": "urun_musteri", "label": "Ürün Müşteri", "type": "text", "value": 0},
                {"name": "urun_barkod", "label": "Ürün Barkod", "type": "number", "value": 0},
                {"name": "urun_qrkod", "label": "Ürün QRkod", "type": "text", "value": ""},
                {"name": "urun_stt", "label": "Ürün STT", "type": "number", "value": 0},
                {"name": "urun_resim", "label": "Ürün Resim", "type": "text", "value": ""},
                {"name": "urun_min", "label": "Ürün Min", "type": "number", "value": 0},
                {"name": "urun_max", "label": "Ürün Max", "type": "number", "value": 0},
                {"name": "urun_hedef", "label": "Ürün Hedef", "type": "number", "value": 0},
                {"name": "urun_adet_gramaj", "label": "Ürün Adet Gramaj", "type": "number", "value": 0},
                {"name": "urun_dara", "label": "Ürün Dara", "type": "number", "value": 0},
                {"name": "urun_adet", "label": "Ürün Adet", "type": "number", "value": 0},
                {"name": "urun_etiket", "label": "Ürün Etiket", "type": "text", "value": ""},
                {"name": "urun_top_etiket", "label": "Ürün Toplam Etiketi", "type": "text", "value": ""},
                {"name": "urun_izleme", "label": "Ürün İzleme", "type": "text", "value": ""},
                {"name": "urun_kodtip", "label": "Ürün Kod Tipi", "type": "text", "value": ""},
                {"name": "urun_tablo", "label": "Ürün Tablo", "type": "text", "value": ""},
                {"name": "urun_mesaj1", "label": "Ürün Mesaj1", "type": "text", "value": ""},
                {"name": "urun_mesaj2", "label": "Ürün Mesaj2", "type": "text", "value": ""},
                {"name": "urun_mesaj3", "label": "Ürün Mesaj3", "type": "text", "value": ""},
                {"name": "urun_mesaj4", "label": "Ürün Mesaj4", "type": "text", "value": ""},
                {"name": "urun_mesaj5", "label": "Ürün Mesaj5", "type": "text", "value": ""},
                {"name": "urun_mesaj6", "label": "Ürün Mesaj6", "type": "text", "value": ""},
                {"name": "urun_mesaj7", "label": "Ürün Mesaj7", "type": "text", "value": ""},
                {"name": "urun_mesaj8", "label": "Ürün Mesaj8", "type": "text", "value":""},
                {"name": "urun_mesaj9", "label": "Ürün Mesaj9", "type": "text", "value": ""},
                {"name": "urun_tanim", "label": "Ürün Tanımı", "type": "text", "value": ""},
                {"name": "urun_icerik", "label": "Ürün İçeriği", "type": "text", "value": ""},
                {"name": "urun_aciklama", "label": "Ürün Açıklaması", "type": "text", "value": ""},
                {"name": "urun_mensei", "label": "Ürün Menşei", "type": "text", "value": ""}
            ]
    except Product.DoesNotExist:
        messages.error(request, 'Ürün Bulunamadı!', extra_tags="danger")
        return redirect('products:products_list')



    context = {
        "active_icon": "products_categories",
        "product": product,
        "fields": fields,
        "product_status": Product.status.field.choices,
        "categories": Category.objects.filter(status="ACTIVE")
    }
        #"general_fields": [
        #    {"name": "urun_kod", "label": "Ürün Kodu", "type": "text", "value": ""},
        #    {"name": "urun_ismi1", "label": "Ürün İsmi 1", "type": "text", "value": ""},
        #    {"name": "urun_ismi2", "label": "Ürün İsmi 2", "type": "text", "value": ""},
        #    {"name": "urun_grup", "label": "Ürün Grubu", "type": "text", "value": ""},
        #    {"name": "urun_tip", "label": "Ürün Tipi", "type": "text", "value": ""},
        #    {"name": "urun_fiyat", "label": "Ürün Fiyat ₺", "type": "number", "value": 0},
        #    {"name": "urun_musteri", "label": "Ürün Müşteri", "type": "text", "value": ""},
        #    {"name": "urun_barkod", "label": "Ürün Barkod", "type": "number", "value": 0},
        #    {"name": "urun_qrkod", "label": "Ürün QRkod", "type": "text", "value": ""},
        #   {"name": "urun_stt", "label": "Ürün STT", "type": "number", "value": 0},
        #    {"name": "urun_resim", "label": "Ürün Resim", "type": "text", "value": ""},
        #    {"name": "urun_min", "label": "Ürün Min", "type": "number", "value": 0},
        #    {"name": "urun_max", "label": "Ürün Max", "type": "number", "value": 0},
        #    {"name": "urun_hedef", "label": "Ürün Hedef", "type": "number", "value": 0},
        #    {"name": "urun_adet_gramaj", "label": "Ürün Adet Gramaj", "type": "number", "value": 0},
        #    {"name": "urun_dara", "label": "Ürün Dara", "type": "number", "value": 0},
        #    {"name": "urun_adet", "label": "Ürün Adet", "type": "number", "value": 0},
        #    {"name": "urun_etiket", "label": "Ürün Etiket", "type": "text", "value": ""},
        #    {"name": "urun_top_etiket", "label": "Ürün Toplam Etiketi", "type": "text", "value": ""},
        #    {"name": "urun_izleme", "label": "Ürün İzleme", "type": "text", "value": ""},
        #    {"name": "urun_kodtip", "label": "Ürün Kod Tipi", "type": "text", "value": ""},
        #    {"name": "urun_tablo", "label": "Ürün Tablo", "type": "text", "value": ""},
        #    {"name": "urun_mesaj1", "label": "Ürün Mesaj1", "type": "text", "value": ""},
        #    {"name": "urun_mesaj2", "label": "Ürün Mesaj2", "type": "text", "value": ""},
        #    {"name": "urun_mesaj3", "label": "Ürün Mesaj3", "type": "text", "value": ""},
        #    {"name": "urun_mesaj4", "label": "Ürün Mesaj4", "type": "text", "value": ""},
        #    {"name": "urun_mesaj5", "label": "Ürün Mesaj5", "type": "text", "value": ""},
        #    {"name": "urun_mesaj6", "label": "Ürün Mesaj6", "type": "text", "value": ""},
        #    {"name": "urun_mesaj7", "label": "Ürün Mesaj7", "type": "text", "value": ""},
        #    {"name": "urun_mesaj8", "label": "Ürün Mesaj8", "type": "text", "value": ""},
        #    {"name": "urun_mesaj9", "label": "Ürün Mesaj9", "type": "text", "value": ""},
        #    {"name": "urun_tanim", "label": "Ürün Tanımı", "type": "text", "value": ""},
        #    {"name": "urun_icerik", "label": "Ürün İçeriği", "type": "text", "value": ""},
        #    {"name": "urun_aciklama", "label": "Ürün Açıklaması", "type": "text", "value": ""},
        #    {"name": "urun_mensei", "label": "Ürün Menşei", "type": "text", "value": ""}

    if request.method == 'POST':
        data = request.POST
        try:
            category = Category.objects.get(id=data.get('category'))
        except Category.DoesNotExist:
            messages.error(request, 'Tanımsız Kategori!', extra_tags="danger")
            return redirect('products:products_add')

        attributes = {
            "status": data.get('state', "TANIMSIZ"),
            "category": category,
            **{key: data.get(key, "TANIMSIZ") for key in [
                "urun_kod", "urun_ismi1", "urun_ismi2", "urun_grup", "urun_tip", "urun_fiyat", "urun_musteri",
                "urun_barkod", "urun_qrkod", "urun_resim", "urun_etiket", "urun_top_etiket",
                "urun_izleme", "urun_kodtip", "urun_tablo", 
                "urun_mesaj1", "urun_mesaj2", "urun_mesaj3", "urun_mesaj4", "urun_mesaj5", "urun_mesaj6", "urun_mesaj7", "urun_mesaj8", "urun_mesaj9",
                "urun_tanim",  "urun_icerik", "urun_aciklama", "urun_mensei"
            ]},
            **{key: data.get(key, 0) for key in [
                "urun_stt", "urun_min", "urun_max", "urun_hedef", "urun_adet_gramaj", "urun_dara", "urun_adet"
            ]},
            "name": data.get('name', "TANIMSIZ"),
            "description": data.get('description', "TANIMSIZ"),
            "price": data.get('price', 0)
        }

        if Product.objects.filter(**attributes).exists():
            messages.error(request, 'Ürün Zaten Var!', extra_tags="warning")
            return redirect('products:products_add')

        try:
            Product.objects.create(**attributes)
            messages.success(request, f'Ürün: {attributes["urun_ismi1"]} Başarıyla Oluşturuldu!', extra_tags="success")
            return redirect('products:products_list')
        except Exception as e:
            messages.error(request, 'ürün Oluşturulurken Hata Oluştu!', extra_tags="danger")
            print(e)
            return redirect('products:products_add')

    return render(request, "products/products_add.html", context=context)

@login_required(login_url="/accounts/login/")
def products_update_view(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Ürün Bulunamadı!', extra_tags="danger")
        return redirect('products:products_list')

    fields = [
        {"name": "urun_kod", "label": "Ürün Kodu", "type": "text", "value": product.urun_kod},
        {"name": "urun_ismi1", "label": "Ürün İsmi 1", "type": "text", "value": product.urun_ismi1},
        {"name": "urun_ismi2", "label": "Ürün İsmi 2", "type": "text", "value": product.urun_ismi2},
        {"name": "urun_grup", "label": "Ürün Grubu", "type": "text", "value": product.urun_grup},
        {"name": "urun_tip", "label": "Ürün Tipi", "type": "text", "value": product.urun_tip},
        {"name": "urun_fiyat", "label": "Ürün Fiyat ₺", "type": "number", "value": product.urun_fiyat},
        {"name": "urun_musteri", "label": "Ürün Müşteri", "type": "text", "value": product.urun_musteri},
        {"name": "urun_barkod", "label": "Ürün Barkod", "type": "number", "value": product.urun_barkod},
        {"name": "urun_qrkod", "label": "Ürün QRkod", "type": "text", "value": product.urun_qrkod},
        {"name": "urun_stt", "label": "Ürün STT", "type": "number", "value": product.urun_stt},
        {"name": "urun_resim", "label": "Ürün Resim", "type": "text", "value": product.urun_resim},
        {"name": "urun_min", "label": "Ürün Min", "type": "number", "value": product.urun_min},
        {"name": "urun_max", "label": "Ürün Max", "type": "number", "value": product.urun_max},
        {"name": "urun_hedef", "label": "Ürün Hedef", "type": "number", "value": product.urun_hedef},
        {"name": "urun_adet_gramaj", "label": "Ürün Adet Gramaj", "type": "number", "value": product.urun_adet_gramaj},
        {"name": "urun_dara", "label": "Ürün Dara", "type": "number", "value": product.urun_dara},
        {"name": "urun_adet", "label": "Ürün Adet", "type": "number", "value": product.urun_adet},
        {"name": "urun_etiket", "label": "Ürün Etiket", "type": "text", "value": product.urun_etiket},
        {"name": "urun_top_etiket", "label": "Ürün Toplam Etiketi", "type": "text", "value": product.urun_top_etiket},
        {"name": "urun_izleme", "label": "Ürün İzleme", "type": "text", "value": product.urun_izleme},
        {"name": "urun_kodtip", "label": "Ürün Kod Tipi", "type": "text", "value": product.urun_kodtip},
        {"name": "urun_tablo", "label": "Ürün Tablo", "type": "text", "value": product.urun_tablo},
        {"name": "urun_mesaj1", "label": "Ürün Mesaj1", "type": "text", "value": product.urun_mesaj1},
        {"name": "urun_mesaj2", "label": "Ürün Mesaj2", "type": "text", "value": product.urun_mesaj2},
        {"name": "urun_mesaj3", "label": "Ürün Mesaj3", "type": "text", "value": product.urun_mesaj3},
        {"name": "urun_mesaj4", "label": "Ürün Mesaj4", "type": "text", "value": product.urun_mesaj4},
        {"name": "urun_mesaj5", "label": "Ürün Mesaj5", "type": "text", "value": product.urun_mesaj5},
        {"name": "urun_mesaj6", "label": "Ürün Mesaj6", "type": "text", "value": product.urun_mesaj6},
        {"name": "urun_mesaj7", "label": "Ürün Mesaj7", "type": "text", "value": product.urun_mesaj7},
        {"name": "urun_mesaj8", "label": "Ürün Mesaj8", "type": "text", "value": product.urun_mesaj8},
        {"name": "urun_mesaj9", "label": "Ürün Mesaj9", "type": "text", "value": product.urun_mesaj9},
        {"name": "urun_tanim", "label": "Ürün Tanımı", "type": "text", "value": product.urun_tanim},
        {"name": "urun_icerik", "label": "Ürün İçeriği", "type": "text", "value": product.urun_icerik},
        {"name": "urun_aciklama", "label": "Ürün Açıklaması", "type": "text", "value": product.urun_aciklama},
        {"name": "urun_mensei", "label": "Ürün Menşei", "type": "text", "value": product.urun_mensei}
    ]

    context = {
        "active_icon": "products",
        "product": product,
        "fields": fields,
        "product_status": Product.status.field.choices,
        "categories": Category.objects.filter(status="ACTIVE"),
    }

    if request.method == 'POST':
        data = request.POST
        try:
            category = Category.objects.get(id=data.get('category'))
        except Category.DoesNotExist:
            messages.error(request, 'Tanımsız Kategori!', extra_tags="danger")
            return redirect('products:products_update', product_id=product_id)

        attributes = {
            "status": data.get('state', "TANIMSIZ"),
            "category": category,
            **{key: data.get(key, "TANIMSIZ") for key in [
                "urun_kod", "urun_ismi1", "urun_ismi2", "urun_grup", "urun_tip", "urun_fiyat", "urun_musteri",
                "urun_barkod", "urun_qrkod", "urun_resim", "urun_etiket", "urun_top_etiket",
                "urun_izleme", "urun_kodtip", "urun_tablo", 
                "urun_mesaj1", "urun_mesaj2", "urun_mesaj3", "urun_mesaj4", "urun_mesaj5", "urun_mesaj6", "urun_mesaj7", "urun_mesaj8", "urun_mesaj9",
                "urun_tanim",  "urun_icerik", "urun_aciklama", "urun_mensei"
            ]},
            **{key: data.get(key, 0) for key in [
                "urun_stt", "urun_min", "urun_max", "urun_hedef", "urun_adet_gramaj", "urun_dara", "urun_adet"
            ]},
            "name": data.get('name', "TANIMSIZ"),
            "description": data.get('description', "TANIMSIZ"),
            "price": data.get('price', 0)
        }

        if Product.objects.filter(**attributes).exclude(id=product_id).exists():
            messages.error(request, 'Bu Ürün Benzeri Zaten Var!', extra_tags="warning")
            return redirect('products:products_update', product_id=product_id)

        try:
            Product.objects.filter(id=product_id).update(**attributes)
            messages.success(request, f'Ürün: {product.urun_ismi1} Başarıyla Güncellendi!', extra_tags="success")
            return redirect('products:products_list')
        except Exception as e:
            messages.error(request, 'Ürün Güncellenirken Hata Oluştu!', extra_tags="danger")
            print(e)
            return redirect('products:products_update', product_id=product_id)

    return render(request, "products/products_update.html", context=context)

@login_required(login_url="/accounts/login/")
def products_delete_view(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        messages.success(request, f'Ürün: {product.urun_ismi1} Silindi!', extra_tags="success")
        return redirect('products:products_list')
    except Product.DoesNotExist:
        messages.error(request, 'Ürün Bulunamadı!', extra_tags="danger")
        return redirect('products:products_list')
    except Exception as e:
        messages.error(request, 'Ürün Silinirken Hata Oluştu!', extra_tags="danger")
        print(e)
        return redirect('products:products_list')

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required(login_url="/accounts/login/")
def get_products_ajax_view(request):
    if request.method == 'POST' and is_ajax(request=request):
        data = []
        term = request.POST.get('term', '')
        products = Product.objects.filter(name__icontains=term)
        for product in products[:10]:
            data.append(product.to_json())
        return JsonResponse(data, safe=False)

@login_required(login_url="/accounts/login/")
def get_products(request):
    term = request.POST.get('term', '').strip()
    all_products = request.POST.get('all', 'false') == 'true'

    if all_products:
        products = Product.objects.all()
    else:
        products = Product.objects.filter(urun_ismi1__icontains=term)

    results = [
        {
            "id": product.id,
            "urun_ismi1": product.urun_ismi1,
            "urun_kod": product.urun_kod,
            "category": product.category.name,
            "urun_barkod": product.urun_barkod,            
            "urun_barkod": product.urun_barkod if product.urun_barkod else "Barkod Yok"
        }
        for product in products
    ]
    return JsonResponse(results, safe=False)

