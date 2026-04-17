def current_user_role(request):
    user = request.user
    if not user.is_authenticated:
        return {'current_user_role': 'guest'}
    if user.is_superuser:
        return {'current_user_role': 'admin'}
    if user.groups.filter(name='manager').exists():
        return {'current_user_role': 'manager'}
    if user.groups.filter(name='client').exists():
        return {'current_user_role': 'client'}
    return {'current_user_role': 'guest'}
