#!/usr/bin/env bash


inc=1
while true; do python sellMonitor.py; echo "$inc"; inc=$(expr $inc + 1); done
