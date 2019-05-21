#!/usr/bin/env bash

pip install --upgrade pycryptodome -t ./

zip -r sshKeyRotation.zip *.py Crypto pycryptodome*