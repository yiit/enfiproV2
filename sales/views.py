import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_pos.wsgi import *
from django_pos import settings
from django.template.loader import get_template
from customers.models import Customer
from products.models import Product
from weasyprint import HTML, CSS
from .models import Sale, SaleDetail, PrintLog


import subprocess
from django.http import JsonResponse
import json

def get_products_by_customer(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        if not customer_id:
            return JsonResponse({'error': 'Müşteri ID gönderilmedi.'}, status=400)
        
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Müşteri bulunamadı.'}, status=404)

        # Müşteri kategorisine göre ürünleri filtrele
        products = Product.objects.filter(category=customer.category)
        product_list = [
            {
                'id': product.id,
                'urun_ismi1': product.urun_ismi1,
                'urun_kod': product.urun_kod,
            }
            for product in products
        ]
        return JsonResponse(product_list, safe=False)
    return JsonResponse({'error': 'Geçersiz istek.'}, status=400)



def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url="/accounts/login/")
def sales_list_view(request):
    context = {
        "active_icon": "sales",
        "sales": Sale.objects.all()
    }
    return render(request, "sales/sales.html", context=context)


@login_required(login_url="/accounts/login/")
def sales_add_view(request):
    context = {
        "active_icon": "sales",
        "customers": [c.to_select2() for c in Customer.objects.all()]
    }

    if request.method == 'POST':
        if is_ajax(request=request):
            # Save the POST arguments
            data = json.load(request)

            sale_attributes = {
                "customer": Customer.objects.get(id=int(data['customer'])),
                "sub_total": float(data["sub_total"]),
                "grand_total": float(data["grand_total"]),
                "tax_amount": float(data["tax_amount"]),
                "tax_percentage": float(data["tax_percentage"]),
                "amount_payed": float(data["amount_payed"]),
                "amount_change": float(data["amount_change"]),
            }
            try:
                # Create the sale
                new_sale = Sale.objects.create(**sale_attributes)
                new_sale.save()
                # Create the sale details
                products = data["products"]

                for product in products:
                    detail_attributes = {
                        "sale": Sale.objects.get(id=new_sale.id),
                        "product": Product.objects.get(id=int(product["id"])),
                        "price": product["price"],
                        "quantity": product["quantity"],
                        "total_detail": product["total_product"]
                    }
                    sale_detail_new = SaleDetail.objects.create(
                        **detail_attributes)
                    sale_detail_new.save()

                print("Sale saved")

                messages.success(
                    request, 'Sale created successfully!', extra_tags="success")

            except Exception as e:
                messages.success(
                    request, 'There was an error during the creation!', extra_tags="danger")

        return redirect('sales:sales_list')

    return render(request, "sales/sales_add.html", context=context)


@login_required(login_url="/accounts/login/")
def sales_details_view(request, sale_id):
    """
    Args:
        request:
        sale_id: ID of the sale to view
    """
    try:
        # Get the sale
        sale = Sale.objects.get(id=sale_id)

        # Get the sale details
        details = SaleDetail.objects.filter(sale=sale)

        context = {
            "active_icon": "sales",
            "sale": sale,
            "details": details,
        }
        return render(request, "sales/sales_details.html", context=context)
    except Exception as e:
        messages.success(
            request, 'There was an error getting the sale!', extra_tags="danger")
        print(e)
        return redirect('sales:sales_list')


@login_required(login_url="/accounts/login/")
def receipt_pdf_view(request, sale_id):
    """
    Args:
        request:
        sale_id: ID of the sale to view the receipt
    """
    # Get the sale
    sale = Sale.objects.get(id=sale_id)

    # Get the sale details
    details = SaleDetail.objects.filter(sale=sale)

    template = get_template("sales/sales_receipt_pdf.html")
    context = {
        "sale": sale,
        "details": details
    }
    html_template = template.render(context)

    # CSS Boostrap
    css_url = os.path.join(
        settings.BASE_DIR, 'static/css/receipt_pdf/bootstrap.min.css')

    # Create the pdf
    pdf = HTML(string=html_template).write_pdf(stylesheets=[CSS(css_url)])

    return HttpResponse(pdf, content_type="application/pdf")

"""def print_file(request):
    if request.method == 'POST':
        # Dosya yolunu oluştur
        file_path = os.path.join(settings.BASE_DIR, 'static', 'printer', 'eyz.prn')
        if not os.path.exists(file_path):
            return JsonResponse({'success': False, 'message': 'File not found.'}, status=404)

        try:
            # Yazdırma komutunu çalıştır
            subprocess.run(['lp', file_path], check=True)
            return JsonResponse({'success': True, 'message': 'File sent to the printer successfully.'})
        except subprocess.CalledProcessError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    else:
        return
"""

import os
import time
import json
import usb.core
import usb.util
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import PrintLog  # Yazdırılan etiketleri kaydetmek için model
from django.views.decorators.csrf import csrf_exempt

# Yazıcı Vendor ve Product ID
# RONGTA RP806
"""
VENDOR_ID = 0x0fe6
PRODUCT_ID = 0x8800
OUT_ENDPOINT = 0x02  # Yazıcıya veri göndermek için kullanılan endpoint
STATUS_ENDPOINT = 0x82  # Yazıcı durumu için kullanılan endpoint
MAX_RETRIES = 5
RETRY_DELAY = 2  # Denemeler arası bekleme süresi
"""
# XPRINTER
VENDOR_ID = 0x2d84
PRODUCT_ID = 0x4e7b
OUT_ENDPOINT = 0x01     # Yazıcıya veri göndermek için kullanılan endpoint
STATUS_ENDPOINT = 0x82  # Yazıcı durumu için kullanılan endpoint
MAX_RETRIES = 5
RETRY_DELAY = 2  # Denemeler arası bekleme süresi

import re
import os
import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
from django.conf import settings


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from customers.models import Customer

@csrf_exempt
def get_customer_info(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        if not customer_id:
            return JsonResponse({'success': False, 'message': 'Müşteri ID eksik.'}, status=400)

        try:
            # Müşteri bilgilerini getir
            customer = Customer.objects.get(id=customer_id)
            customer_data = {
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'address': customer.address,
            }
            return JsonResponse({'success': True, 'data': customer_data})
        except Customer.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Müşteri bulunamadı.'}, status=404)
    return JsonResponse({'success': False, 'message': 'Geçersiz istek yöntemi.'}, status=400)

@csrf_exempt
def print_file(request):
    if request.method == 'POST':
        try:
            import json, os, re
            from django.http import JsonResponse
            from django.conf import settings
            from datetime import datetime
            import subprocess

            # JSON verilerini al
            data = json.loads(request.body)
            placeholders = {
                "%net%": data.get('weight', '').strip(),
                "%partino%": data.get('customText', '').strip(),
                "%musteri_ismi1%": data.get('customerName', ''),
                "%musteri_ismi2%": data.get('customerName2', ''),
                "%urun_ismi1%": data.get('productName', ''),
                "%urun_kodu%": data.get('productCode', ''),
                "%sno%": data.get('serialNumber', ''),
                "%musteri_adresi%": data.get('customerAddress', ''),
                "%date%": datetime.now().strftime('%d-%m-%Y')
            }

            minimum_x_position = 0
            line_spacing = 25  # Satırlar arası boşluk
            max_chars_per_line = 25  # Bir satırda maksimum karakter sayısı

            file_path = os.path.join(settings.BASE_DIR, 'static', 'printer', 'eyz.prn')
            yaz_file_path = os.path.join(settings.BASE_DIR, 'static', 'printer', 'yaz_eyz.prn')

            if not os.path.exists(file_path):
                return JsonResponse({'success': False, 'message': 'Template file not found.'}, status=404)

            with open(file_path, 'r', encoding='ISO-8859-9') as file:
                content = file.read()

                # ENDUTEK.TTF yerine 0 koy
                content = content.replace('ENDUTEK.TTF', '0')

                for placeholder, value in placeholders.items():
                    if placeholder not in content:
                        print(f"Placeholder {placeholder} not found in template.")
                        continue

                    match = re.search(
                        rf'TEXT\s+(\d+),(\d+),\"(\d+)\",(\d+),(\d+),(\d+),\".*{re.escape(placeholder)}.*\"',
                        content
                    )
                    if not match:
                        print(f"No match found for placeholder: {placeholder}")
                        continue

                    original_x_position = int(match.group(1))
                    y_position = int(match.group(2))
                    font_type = match.group(3)
                    rotation = int(match.group(4))
                    font_width = int(match.group(5))
                    font_height = int(match.group(6))

                    # Metni 25 karakterlik parçalara ayır
                    def chunk_text(text, chunk_size):
                        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

                    chunks = chunk_text(value, max_chars_per_line)

                    # Her parça için yeni satırlar oluştur
                    new_lines = []
                    for i, chunk in enumerate(chunks):
                        chunk_length = len(chunk)  # Parçanın uzunluğunu öğren
                        total_width = chunk_length * font_width  # Metnin toplam genişliği
                        adjusted_x = max(
                            ((original_x_position // 2) - (total_width // 2)),  # X eksenini ortala
                            minimum_x_position
                        )
                        adjusted_x = max(min(adjusted_x, 700), minimum_x_position)  # Sınırlar içinde tut
                        new_line = f'TEXT {adjusted_x},{y_position - (i * line_spacing)},"{font_type}",{rotation},{font_width},{font_height},"{chunk}"\n'
                        new_lines.append(new_line)

                    # TEXT içinde sadece placeholder'ı değiştir
                    content = re.sub(
                        rf'(TEXT\s+\d+,\d+,\"[^\"]+\",\d+,\d+,\d+,\".*){re.escape(placeholder)}(.*\")',
                        lambda m: f"{m.group(1)}{value}{m.group(2)}",
                        content
                    )

            with open(yaz_file_path, 'w', encoding='ISO-8859-9') as yaz_file:
                yaz_file.write(content)

            subprocess.run(['lp', yaz_file_path], check=True)

            return JsonResponse({'success': True, 'message': 'Etiket başarıyla yazdırıldı.'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            import traceback
            error_message = traceback.format_exc()
            print(error_message)
            return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)



"""
@csrf_exempt
def print_file(request):
    if request.method == 'POST':
        try:
            # JSON body'den weight değerini al
            data = json.loads(request.body)
            weight = data.get('weight', '').strip()  # Ağırlığı al
            custom_text = data.get('customText', '').strip()
            customer_name = data.get('customerName')
            #customer_address = data.get("customerAddress")
            #customer_last_name = data.get("customerLastName")
            product_name = data.get('productName')
            product_code = data.get('productCode')

            # Bugünün tarihi
            today_date = datetime.now().strftime('%d-%m-%Y')  # Gün-Ay-Yıl formatında

            if not weight:
                return JsonResponse({'success': False, 'message': 'Weight value is missing.'}, status=400)

            # Dosya yolları
            file_path = os.path.join(settings.BASE_DIR, 'static', 'printer', 'eyz.prn')
            yaz_file_path = os.path.join(settings.BASE_DIR, 'static', 'printer', 'yaz_eyz.prn')
            if not os.path.exists(file_path):
                return JsonResponse({'success': False, 'message': 'Template file not found.'}, status=404)

            # Dosya içeriğini oku ve %net% ile tartı bilgisini değiştir
            with open(file_path, 'r', encoding='ISO-8859-9') as file:
                content = file.read()
                content = content.replace('%net%', weight)
                content = content.replace('%partino%', custom_text)
                content = content.replace('%musteri_ismi1%', customer_name)
                #content = content.replace('%musteri_ismi2%', customer_last_name)
                #content = content.replace('%musteri_adres%', customer_address)
                content = content.replace('%urun_ismi1%', product_name)
                content = content.replace('%urun_kodu%', product_code)
                content = content.replace('%date%', today_date)
                content = content.replace('ENDUTEK.TTF', '0')

            # Geçici dosyaya yaz
            with open(yaz_file_path, 'w') as yaz_file:
                yaz_file.write(content)

            # Yazıcıya gönder
            subprocess.run(['lp', yaz_file_path], check=True)
            
            """"""
            # Yazıcıya bağlan
            printer = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
            if printer is None:
                return JsonResponse({'success': False, 'message': 'Printer not found.'}, status=404)

            # Kernel sürücüsünü serbest bırak
            if printer.is_kernel_driver_active(0):
                printer.detach_kernel_driver(0)

            # Yazıcıyı yapılandır
            printer.set_configuration()

            # Yazdırma işlemi için deneme mekanizması
            for attempt in range(MAX_RETRIES):
                try:
                    printer.write(OUT_ENDPOINT, content.encode('ISO-8859-9'))

                    # Yazdırma işleminden sonra yazıcıyı serbest bırak
                    release_usb(printer)

                    # Yazdırma bilgilerini SQL'e kaydet
                    save_print_log(weight, file_path)

                    return JsonResponse({'success': True, 'message': f'File sent to printer successfully on attempt {attempt + 1}.'})
                except usb.core.USBError as e:
                    if e.errno == 16:  # Resource Busy
                        reset_usb_port(printer)  # USB portunu resetle
                        time.sleep(RETRY_DELAY)
                    elif e.errno == 13:  # Permission Denied
                        return JsonResponse({'success': False, 'message': 'Permission denied. Check USB permissions.'}, status=403)
                    else:
                        return JsonResponse({'success': False, 'message': f'USB error: {str(e)}'}, status=500)

            # Maksimum deneme sayısına ulaşıldı
            return JsonResponse({'success': False, 'message': 'Printer is busy. Maximum retries reached.'}, status=500)
            """"""
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
    """

@csrf_exempt
def print_label(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            weight = data.get('weight', '').strip()  # Ağırlığı al
            custom_text = data.get('customText', '').strip()
            customer_name = data.get('customerName')
            #customer_address = data.get("customerAddress")
            #customer_last_name = data.get("customerLastName")
            product_name = data.get('productName')
            product_code = data.get('productCode')

            # Bugünün tarihi
            today_date = datetime.now().strftime('%d-%m-%Y')  # Gün-Ay-Yıl formatında

            if not weight:
                return JsonResponse({'success': False, 'message': 'Weight value is missing.'}, status=400)

            file_path = os.path.join(settings.BASE_DIR, 'static', 'printer', 'eyz.prn')
            yaz_file_path = os.path.join(settings.BASE_DIR, 'static', 'printer', 'yaz_eyz.prn')

            if not os.path.exists(file_path):
                return JsonResponse({'success': False, 'message': 'Template file not found.'}, status=404)

            with open(file_path, 'r', encoding='ISO-8859-9') as file:
                content = file.read()
                content = file.read().replace('%net%', weight)
                content = content.replace('%partino%', custom_text)
                content = content.replace('%musteri_ismi1%', customer_name)
                #content = content.replace('%musteri_ismi2%', customer_last_name)
                #content = content.replace('%musteri_adres%', customer_address)
                content = content.replace('%urun_ismi1%', product_name)
                content = content.replace('%urun_kodu%', product_code)
                content = content.replace('%date%', today_date)
                content = content.replace('ENDUTEK.TTF', '0')

            with open(yaz_file_path, 'w') as yaz_file:
                yaz_file.write(content)

            subprocess.run(['lp', yaz_file_path], check=True)

            return JsonResponse({'success': True, 'message': 'Etiket yazdırıldı.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

def reset_usb_port(printer):
    """
    USB portunu resetler ve yazıcıyı serbest bırakır.
    """
    try:
        printer.reset()  # Yazıcıyı sıfırla
        print("USB port has been reset.")
    except usb.core.USBError as e:
        print(f"Error resetting USB port: {str(e)}")

def release_usb(printer):
    """
    Yazıcıyı serbest bırakır ve kernel sürücüsünü yeniden bağlar.
    """
    try:
        usb.util.dispose_resources(printer)  # Kaynakları serbest bırak
        if not printer.is_kernel_driver_active(0):
            printer.attach_kernel_driver(0)  # Kernel sürücüsünü yeniden bağla
        print("USB resources released and kernel driver reattached.")
    except usb.core.USBError as e:
        print(f"Error releasing USB resources: {str(e)}")

def save_print_log(weight, file_path):
    """
    Yazdırılan bilgileri veritabanına kaydeder.
    """
    try:
        PrintLog.objects.create(
            weight=weight,
            file_path=file_path,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        print("Print log saved successfully.")
    except Exception as e:
        print(f"Error saving print log: {str(e)}")

def check_printer_status():
    """
    Yazıcının meşgul olup olmadığını kontrol eder.
    """
    try:
        printer = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        if printer is None:
            return {'status': 'not_found', 'message': 'Printer not found.'}

        if printer.is_kernel_driver_active(0):
            printer.detach_kernel_driver(0)

        printer.set_configuration()

        try:
            status = printer.read(STATUS_ENDPOINT, 64, timeout=1000)
            if status[0] == 0x00:
                return {'status': 'idle', 'message': 'Printer is idle and ready.'}
            elif status[0] == 0x01:
                return {'status': 'busy', 'message': 'Printer is busy.'}
            else:
                return {'status': 'unknown', 'message': 'Unknown printer status.'}
        except usb.core.USBError as e:
            if e.errno == 110:  # Timeout
                return {'status': 'timeout', 'message': 'No response from printer.'}
            else:
                return {'status': 'error', 'message': f'USB error: {str(e)}'}
    except Exception as e:
        return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}


"""
import json
import os
import subprocess
from django.http import JsonResponse
from django.conf import settings

def print_file(request):
    if request.method == 'POST':
        try:
            # JSON body'den weight değerini al
            data = json.loads(request.body)
            weight = data.get('weight')
            if not weight:
                return JsonResponse({'success': False, 'message': 'Weight value is missing.'}, status=400)

            # Dosya yolları
            file_path = os.path.join(settings.BASE_DIR, 'static', 'printer', 'eyz.prn')
            temp_file_path = os.path.join(settings.BASE_DIR, 'static', 'printer', 'temp_eyz.prn')

            if not os.path.exists(file_path):
                return JsonResponse({'success': False, 'message': 'Template file not found.'}, status=404)

            # Dosya içeriğini oku ve %net% ile tartı bilgisini değiştir
            with open(file_path, 'r', encoding='ISO-8859-9') as file:
                # Binary içerik üzerinde %net% yer tutucusunu değiştir
                content = file.read()
            try:
                content = content.replace('%net%', weight)
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Replace error: {str(e)}'}, status=500)

            # Geçici dosyaya yaz
            with open(temp_file_path, 'w') as temp_file:
                temp_file.write(content)

            # Yazıcıya gönder
            subprocess.run(['lp', temp_file_path], check=True)

            # Geçici dosyayı temizle
            os.remove(temp_file_path)

            return JsonResponse({'success': True, 'message': 'File sent to printer successfully.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON format.'}, status=400)
        except subprocess.CalledProcessError as e:
            return JsonResponse({'success': False, 'message': f'Printing error: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
"""