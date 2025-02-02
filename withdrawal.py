import datetime
from random import randint
from flask import Blueprint, request, jsonify
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import json
from time import time
from flask_login import current_user
from . import db
from .models import User, PayoutQueue
from .viewers import distribute

server1_public_key = None

withdrawal = Blueprint('withdrawal', __name__)

def queue_withdrawal(address, amount, network):
    existing_payout = PayoutQueue.query.filter_by(user_id=current_user.id).first()
    if existing_payout:
        return [False, "You already have a pending payout."]
    payout = PayoutQueue(
        withdrawal_id=''.join(["%s" % randint(0, 9) for num in range(0, 12)]),
        user_id=current_user.id,
        address=address,
        amount=round(amount, 2),
        network=network
    )
    db.session.add(payout)
    db.session.commit()
    return [True, "Withdrawal queued successfully!"]


@withdrawal.route('/send_key', methods=['POST'])
def receive_public_key():
    global server1_public_key
    try:
        server1_public_key = RSA.import_key(request.json['public_key'].encode('utf-8'))
    except Exception as e:
        return jsonify({'error': 'No key', 'reason': str(e), 'success': False}), 400
    return jsonify({'message': 'Public key received'})


@withdrawal.route('/withdraw_request', methods=['GET'])
def withdraw_request():
    if not server1_public_key:
        return jsonify({'error': 'No key', 'success': False}), 400
    
    first_payout = PayoutQueue.query.first()
    if not first_payout:
        return jsonify({'error': 'No queue', 'success': False}), 220
    secret_data = json.dumps({
        'id': first_payout.id,
        'withdrawal_id': first_payout.withdrawal_id,
        'user_id': first_payout.user_id,
        'address': first_payout.address,
        'amount': str(first_payout.amount),
        'network': first_payout.network
    })
    try:
        cipher = PKCS1_OAEP.new(server1_public_key)
        encrypted_data = cipher.encrypt(secret_data.encode('utf-8'))
    except Exception as e:
        return jsonify({'error': 'No key', 'reason': str(e), 'success': False}), 500
    return jsonify({'encrypted_data': encrypted_data.hex()})


@withdrawal.route('/withdraw_update', methods=['POST'])
def withdraw_update():
    data = request.json
    payout_data = db.session.get(PayoutQueue, data['id'])
    if payout_data.withdrawal_id == data['withdrawal_id']:
        user = db.session.get(User, data['user_id'])
        if data['success'] == True:
            user.usd_balance -= float(payout_data.amount)
            user.payout_balance -= float(payout_data.amount)
            user.last_payout = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " --- Sent amount: " + str(payout_data.amount) + ", to address: " + payout_data.address +", network: " + payout_data.network + " --- wait till Confirmations"
            db.session.delete(payout_data)
            db.session.commit()
            return jsonify({'message': 'Withdraw successful'})
        else:
            user.last_payout = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " --- Send failed ---" + str(data['reason'])
            db.session.delete(payout_data)
            db.session.commit()
            return jsonify({'message': 'Withdraw failed', 'reason': data['reason']})
    return jsonify({'error': 'Invalid withdraw data'}), 400
