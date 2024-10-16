# One ip will be counted as one view per 30 minutes
import datetime
from .models import IPAccess, User, countlog, Distributionlog
from . import db
def is_a_new_viewer(ip_address):
    get_ip = db.session.get(IPAccess, ip_address)
    if not get_ip:
        db.session.add(IPAccess(ip=ip_address))
        db.session.commit()
        return True
    else:
        if get_ip.time < datetime.datetime.now() - datetime.timedelta(minutes=12):
            get_ip.time = datetime.datetime.now()
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
            user.usd_balance += viewcount * (current_earnings - old_earnings) / sum_viewcounts
            date_now = datetime.date.today()
            record = db.session.get(Distributionlog, (date_now, user_id))
            if record:
                record.usd_balance += viewcount * (current_earnings - old_earnings) / sum_viewcounts
            else:
                db.session.add(Distributionlog(
                        date=date_now,
                        user_id=user_id,
                        usd_balance=viewcount * (current_earnings - old_earnings) / sum_viewcounts
                    )
                )
        db.session.query(countlog).delete()
        db.session.commit()
        return True
    else:
        return False

