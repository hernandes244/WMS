from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Product,Stock,Receipt,Order,Picking,Movement

def dashboard(request):
    stock=Stock.objects.aggregate(total=Sum('quantity'),reserved=Sum('reserved'),blocked=Sum('blocked'))
    context={'products':Product.objects.filter(active=True).count(),'stock_total':stock['total'] or 0,'reserved':stock['reserved'] or 0,'blocked':stock['blocked'] or 0,'receipts':Receipt.objects.exclude(status='DONE').count(),'orders':Order.objects.exclude(status__in=['SHIPPED','CANCELLED']).count(),'pickings':Picking.objects.exclude(status='DONE').count(),'movements':Movement.objects.count(),'orders_by_status':Order.objects.values('status').annotate(total=Count('id')).order_by('status')}
    return render(request,'dashboard.html',context)

def orders(request): return render(request,'orders.html',{'orders':Order.objects.prefetch_related('items').order_by('-created_at')[:100]})
def stock(request): return render(request,'stock.html',{'stocks':Stock.objects.select_related('product','address','lot').order_by('product__code')[:200]})
def receipts(request): return render(request,'receipts.html',{'receipts':Receipt.objects.prefetch_related('items').order_by('-received_at')[:100]})
def pickings(request): return render(request,'pickings.html',{'pickings':Picking.objects.prefetch_related('items').order_by('-created_at')[:100]})
def movements(request): return render(request,'movements.html',{'movements':Movement.objects.select_related('product','source','destination').order_by('-created_at')[:200]})
