#!/usr/bin/env bash

pip3 install --upgrade pycryptodome -t ./

zip -r sshKeyRotation.zip *.py Crypto pycryptodome*