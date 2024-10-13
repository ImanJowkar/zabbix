#!/bin/bash

echo "delete all rules in DOCKER-USER chain"
iptables -F DOCKER-USER