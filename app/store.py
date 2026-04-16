from .dummy_data import referrers_data, referees_data, referrer_details_data

# In-memory stores — reset on app restart (fine for hackathon)

# Referrer accounts keyed by email
referrers = dict(referrers_data)

# Referee accounts created on form submission, keyed by reference number
referees = dict(referees_data)

# Referrer details keyed by sub
referrer_details = dict(referrer_details_data)
