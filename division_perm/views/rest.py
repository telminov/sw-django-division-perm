# coding: utf-8
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .. import models
from .. import serializers
from .. import authentication


@api_view(['POST'])
def generate_sig(request):
    """
    Отладочный ресурс для формирования подписи, передаваемой в GET-параметре sig в другие ресурсы
    ---
    request_serializer: serializers.GenerateSig
    type:
      sig:
        required: true
        type: string
        description: подпись, которая будет сформирована для проверки в требующих подписи ресурсах.
    """
    serializer = serializers.GenerateSig(data=request.data)
    serializer.is_valid(raise_exception=True)
    sig = authentication.generate_sig(
        ext_id=serializer.validated_data['ext_id'],
        func=serializer.validated_data['func'],
        body=serializer.validated_data.get('body_content', ''),
        secret_key=serializer.validated_data['secret_key'],
    )
    return Response({'sig': sig})


@api_view(['GET'])
@authentication_classes((authentication.SigAuthentication, ))
@permission_classes((IsAuthenticated,))
def hello(request):
    """
    Отладочный ресур. Доступен только при правильной аутентификации с использованием подписи.
    ---
    parameters:
        - name: ext_id
          type: string
          required: true
          paramType: query

        - name: sig
          type: string
          required: true
          paramType: query
    """
    return Response({'message': 'Hello, world!'})
