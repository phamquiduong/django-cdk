import os

import aws_cdk as cdk
from dotenv import load_dotenv

from cdk.stack.django_stack import DjangoStack

if not load_dotenv():
    raise FileNotFoundError('Load environment variables failed')

CONSTRUCT_ID = os.getenv('CONSTRUCT_ID', 'Django')

# Create stack app
app = cdk.App()

# Register stack with app
DjangoStack(app, CONSTRUCT_ID)

# Synth the stack app
app.synth()
