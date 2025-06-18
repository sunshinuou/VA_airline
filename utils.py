DISPLAY_NAME_MAP = {
    'Departure/Arrival time convenient': 'DEP/ARR time convenient',
    'Ease of Online booking': 'Online booking',
    'Inflight wifi service': 'Inflight wifi',
    'Inflight entertainment': 'Inflight media',
    'On-board service': 'On-board',
    'Leg room service': 'Leg room',
    'Baggage handling': 'Baggage',
    'Departure Delay in Minutes': 'DEP Delay (min)',
    'Arrival Delay in Minutes': 'ARR Delay (min)'
}
def get_display_name(col):
    return DISPLAY_NAME_MAP.get(col, col)

VALUE_DISPLAY_MAP = {
    'loyal customer': 'Loyal',
    'disloyal customer': 'Disloyal',
    'neutral or dissatisfied': 'Neut.<br>or<br>Dissat.',
    'satisfied': 'Sat.'
}
def get_display_value(val):
    if not isinstance(val, str):
        return val
    key = val.strip().lower()
    return VALUE_DISPLAY_MAP.get(key, val) 