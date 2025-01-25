from flask import Blueprint, render_template, request, redirect, url_for
import hmac
import requests
import hashlib
from time import time
import os
from werkzeug.security import check_password_hash
from flask_login import current_user, login_required
from . import db
from .models import Base, User, Last_access, Distributionlog
from .settings import monetag_key, binance_api, binance_secret
from .viewers import distribute
current_directory = os.getcwd()
items = os.listdir(current_directory)
if 'VideoBin' in items:
    os.chdir(current_directory+'/VideoBin')


view_pages = Blueprint('view_pages', __name__)



@view_pages.route('/')
def index():
    return render_template('home.html')
@view_pages.route('/upload-policy')
def policy():
    return render_template('policy.html')
@view_pages.route('/archive')
def archive():
    if current_user.is_authenticated == False:
        return render_template('archive.html')
    
    user = db.session.get(User, current_user.id)
    urls = user.bases

    return render_template('archive.html', urls=urls)

@view_pages.route('/profile')
@login_required
def profile():
    user = db.session.query(User).filter_by(id=current_user.id).first()
    logs = user.distribution_logs
    return render_template('profile.html', name=current_user.name, logs=logs)

@view_pages.route('/m/<prefix>')
def show_entries(prefix):
    prefix_info = db.session.get(Base, prefix)
    if not prefix_info or prefix_info.link_type != 1:
        return f'Invalid URL'
    entries = Base.query.filter(Base.baseurl.like(f'{prefix}%')).all()
    return render_template('show_entries.html', prefix = prefix_info, entries=entries)

@view_pages.route('/edit_video/<prefix>')
@login_required
def edit(prefix):
    prefix_info = db.session.query(Base).filter_by(baseurl=prefix, user_id=current_user.id).first()
    if not prefix_info:
        return f'Invalid URL'
    return render_template('edit.html', prefix = prefix_info)


@view_pages.route('/edit_video/<prefix>', methods=['POST'])
@login_required
def edit_post(prefix):
    action = request.form.get('action')
    prefix_info = db.session.query(Base).filter_by(baseurl=prefix, user_id=current_user.id).first()
    if action == 'delete':
        if prefix_info:
            try:
                db.session.query(Base).filter_by(baseurl=prefix).delete()
                db.session.commit()
                #flash('Video deleted successfully!', 'success')
                return redirect(url_for('view_pages.archive'))
            except Exception:
                db.session.rollback()
            except Exception:
                return redirect(url_for('view_pages.edit', prefix=prefix))
        else:
            #flash('Video not found or you don’t have permission to delete it.', 'danger')
            return redirect(url_for('view_pages.edit', prefix=prefix))
    elif action == 'change':
        if not prefix_info:
            return f'Invalid URL'
        prefix_info.name = request.form.get('newName', prefix_info.name)
        prefix_info.ad_percent = request.form.get('percent', prefix_info.ad_percent)
        db.session.commit()
        return redirect(url_for('view_videos.view_video', filename=prefix))

@view_pages.route('/adupdate', methods=['POST'])
def adupdate():
    req = request.json
    key = req['key']
    total_usd = float(req['total_usd'])
    time_now = db.func.current_timestamp()
    if key == monetag_key:
        old_data = db.session.get(Last_access, 1)
        if not old_data:
            success = distribute(0, total_usd)
            if not success:
                return "False"
            new_data = Last_access(access_type=1, access_time=time_now, value=str(total_usd))
            db.session.add(new_data)
            db.session.commit()
            return "True"
        elif abs(total_usd - float(old_data.value)) > 0.01:
            success = distribute(float(old_data.value), total_usd)
            if not success:
                return "False"
            old_data.access_time = time_now
            old_data.value = str(total_usd)
            db.session.commit()
            return "True"
        else:
            return "No Change"
    else:
        return "False"

@view_pages.route('/payout', methods=['GET'])
@login_required
def payout():
    old_data = db.session.get(Last_access, 2)
    if not old_data:
        old_data = Last_access(access_type=2, access_time='1972-01-01', value=None)
        db.session.add(old_data)
        db.session.commit()
    logs = db.session.query(Distributionlog).filter(Distributionlog.date > old_data.access_time, Distributionlog.date < db.func.date_sub(db.func.current_timestamp(), db.text('INTERVAL 2 DAY'))).all()
    for log in logs:
        user = db.session.get(User, log.user_id)
        if user:
            user.payout_balance += log.usd_balance
            old_data.access_time = log.date
            db.session.commit()
    if logs:
        thirty_days_ago = db.func.date_sub(db.func.current_timestamp(), db.text('INTERVAL 30 DAY'))
        db.session.query(Distributionlog).filter(Distributionlog.date < thirty_days_ago).delete()
        db.session.commit()
    return render_template('payout.html')




def submit_withdrawal(address, amount, network):
    url = f'https://api.binance.com/sapi/v1/capital/withdraw/apply'
    params = {
        'coin': "USDT",
        'address': address,
        'amount': amount,
        'network': network,
        'transactionFeeFlag': 'true',
        'timestamp': int(time() * 1000)
    }
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    signature = hmac.new(
        binance_secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    params['signature'] = signature
    
    headers = {
        'X-MBX-APIKEY': binance_api
    }
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 200:
        return [True, "Withdrawal submitted successfully!"]
    else:
        return [False, f"Error: {response.status_code} - {response.json()}"]

@view_pages.route('/payout', methods=['POST'])
@login_required
def payout_POST():
    password = request.form.get('password','')
    amount = float(request.form.get('amount','0'))
    if check_password_hash(current_user.password, password):
        if current_user.payout_balance < amount or amount < 0.2:
            return "Amount must be between 0.2 to" + str(current_user.payout_balance)
        else:
            resp = submit_withdrawal(current_user.wallet.split()[1], amount, current_user.wallet.split()[0])
            if resp[0] == True:
                current_user.usd_balance-=amount
                current_user.payout_balance-=amount
                db.session.commit()
            return resp[1]
    else:
        return "Wrong password"