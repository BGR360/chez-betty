from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import *
from .models.model import *
from .models.user import User
from .models.item import Item
from .models.transaction import Transaction

import chezbetty.datalayer as datalayer

@view_config(route_name='index', renderer='templates/index.jinja2')
def index(request):
    return {}

@view_config(route_name='about', renderer='templates/about.jinja2')
def about(request):
    return {}

@view_config(route_name='purchase', renderer='templates/purchase.jinja2')
def purchase(request):
    user = User.from_umid(request.matchdict['umid'])
    purchase_info = render('templates/user_info.jinja2', {'user': user,
                                                          'page': 'purchase'})
    return {'purchase_info_block': purchase_info}

@view_config(route_name='purchase_new', request_method='POST', renderer='templates/purchase_complete.jinja2')
def purchase_new(request):
    user = User.from_umid(request.matchdict['umid'])
    transaction = datalayer.purchase(user, request.POST.items())
    return {'transaction': transaction}

@view_config(route_name='items', renderer='templates/items.jinja2')
def items(request):
    items = DBSession.query(Item).all()
    return {'items': items}

@view_config(route_name='item', renderer='json')
def item(request):
    item = Item.from_barcode(request.matchdict['barcode'])
    item_html = render('templates/item_row.jinja2', {'item': item})
    return {'id':item.id, 'item_row_html' : item_html}

@view_config(route_name='users', renderer='templates/users.jinja2')
def users(request):
    users = DBSession.query(User).all()
    return {'users': users}

@view_config(route_name='user', renderer='templates/user.jinja2')
def user(request):
    user = User.from_umid(request.matchdict['umid'])
    return {'user': user}

@view_config(route_name='deposit', renderer='templates/deposit.jinja2')
def deposit(request):
    user = User.from_umid(request.matchdict['umid'])
    user_info_html = render('templates/user_info.jinja2', {'user': user,
                                                           'page': 'deposit'})
    keypad_html = render('templates/keypad.jinja2', {})
    return {'user_info_block': user_info_html, 'keypad': keypad_html}

@view_config(route_name='deposit_new',
             request_method='POST',
             renderer='json')
def deposit_new(request):
    user = User.from_umid(request.POST['umid'])
    amount = float(request.POST['amount'])
    deposit = datalayer.deposit(user, amount)

    # Return a JSON blob of the transaction ID so the client can redirect to
    # the deposit success page
    return {'transaction_id': deposit['transaction'].id}

@view_config(route_name='transaction_deposit',
             renderer='templates/deposit_complete.jinja2')
def transaction_deposit(request):
    transaction = DBSession.query(Transaction).filter(Transaction.id==int(request.matchdict['transaction_id'])).one()
    user = DBSession.query(User).filter(User.id==transaction.to_account_id).one()

    user_info_html = render('templates/user_info.jinja2', {'user': user,
                                                           'page': 'deposit'})
    deposit = {'transaction_id': transaction.id,
               'prev': user.balance - transaction.amount,
               'amount': transaction.amount,
               'new': user.balance}
    return {'deposit': deposit, 'user_info_block': user_info_html}

