import awsgi

from core.wsgi import application


def handler(event, context):
    return awsgi.response(application, event, context)
