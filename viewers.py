# One ip will be counted as one view per 30 minutes
import datetime
from .models import IPAccess, User, countlog, distributionlog
from . import db
def is_a_new_viewer(ip_address):
    if not db.session.get(IPAccess, ip_address):
        db.session.add(IPAccess(ip=ip_address))
        db.session.commit()
        return True
    else:
        ip = db.session.get(IPAccess, ip_address)
        if ip.time < datetime.datetime.now() - datetime.timedelta(minutes=12):
            ip.time = datetime.datetime.now()
            db.session.commit()
            return True
        else:
            return False
def clear_IPAccess():
    db.session.query(IPAccess).delete()

def distribute():
    old_earnings = 0
    current_earnings = 1
    if old_earnings != current_earnings:
        # Distribute earnings to users based on viewcount
        users = db.session.query(countlog).all()
        sum_viewcounts = sum(user.viewcount for user in users)
        for user in users:
            user_id = user.user_id
            viewcount = user.viewcount
            user = db.session.get(User, user_id)
            user.usd_balance += viewcount * (old_earnings - current_earnings) / sum_viewcounts
            db.session.commit()
        # Clear countlog
        db.session.query(countlog).delete()
        db.session.commit()
        # Log distribution
        db.session.add(distributionlog(usd_balance=current_earnings))
        db.session.commit()
        return True
    else:
        return False