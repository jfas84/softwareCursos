from functools import wraps
from django.shortcuts import redirect

def responsabilidade_required(*responsabilidades):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Convertendo a queryset de objetos Responsaveis para uma lista de descrições (chaves dos choices)
            user_responsabilidades = [resp.descricao for resp in request.user.responsabilidades.all()]
            # Verificando se alguma das responsabilidades requeridas está na lista de responsabilidades do usuário
            if any(responsabilidade in user_responsabilidades for responsabilidade in responsabilidades):
                return view_func(request, *args, **kwargs)
            return redirect('internaTableauGeral')
        return _wrapped_view
    return decorator