#!/usr/bin/env bash


inc=1
while true; do python buyMonitor.py; inc=$(expr $inc + 1); echo "$inc"; done
