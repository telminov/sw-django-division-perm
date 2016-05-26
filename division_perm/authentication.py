# coding: utf-8
import hashlib
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from . import models


class SigAuthentication(BaseAuthentication):
    """
        Аутентификация подписью в GET-параметрах:
            ext_id (string): код внешнего пользователя
            sig (string): подпись запроса

        Чтобы удостовериться, что вызов отправлен действительно вами, а не злоумышленниками от лица внешней системы, все вызовы REST API должны быть подписаны. Для этого использует отдельный ключ secret_key. В каждом вызове API необходимо передавать подпись в виде параметра sig. Значение параметра sig рассчитывается следующим образом:
        sig = md5(ext_id + func + body + secret_key)
        Разделитель в конкатенации не используется.

        Для запроса:
        http://server_or_ip/erasignal/apr/api/getBunchStatus&ext_id=Cobra
        с телом:
        {"bunch_id": "43"}

        подпись будет:
        sig = md5(CobragetBunchStatus{"bunch_id": "43"}3dad9cbf9baaa0360c0f2ba372d25716) = 26b3e168b9a902793a39b80a738a5d76
    """

    def authenticate(self, request):
        ext_id = request.GET.get('ext_id')
        if not ext_id:
            msg = 'Invalid GET-parameters: ext_id is not present.' \
                  ' It have to contain identifier of external user/system.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            ext_user = models.Employee.objects.get(user__username=ext_id)
        except models.Employee.DoesNotExist:
            msg = 'Invalid GET-parameters: incorrect ext_id value.'
            raise exceptions.AuthenticationFailed(msg)

        request_sig = request.GET.get('sig')
        if not request_sig:
            msg = 'Invalid GET-parameters: sig is not present.' \
                  ' It have to contain signature by formula:' \
                  ' md5(ext_id + func + body + secret_key)'
            raise exceptions.AuthenticationFailed(msg)

        func = [i for i in request.path.split('/') if i and not i.isdigit()][-1]
        body = request.body.decode()

        return self._check(ext_user,  func, body, request_sig)

    def _check(self, ext_user, func, body, request_sig):
        secret_key = ext_user.get_secret_key()

        sig = generate_sig(
            ext_id=ext_user.user.username,
            func=func,
            body=body,
            secret_key=secret_key,
        )

        if request_sig != sig:
            msg = 'Invalid signature.'
            raise exceptions.AuthenticationFailed(msg)

        return ext_user.user, None


def generate_sig(ext_id, func, body, secret_key):
    input_string = ''.join([ext_id, func, body, secret_key])
    m = hashlib.md5(input_string.encode())
    return m.hexdigest()
