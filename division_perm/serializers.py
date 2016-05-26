# coding: utf-8
from rest_framework import serializers


class GenerateSig(serializers.Serializer):
    ext_id = serializers.CharField(help_text='Код внешнего пользователя')
    func = serializers.CharField(help_text='Последняя часть урла. Например, "hello" для урал "/rest/hello?a=1&b=2"')
    body_content = serializers.CharField(required=False)
    secret_key = serializers.CharField()
