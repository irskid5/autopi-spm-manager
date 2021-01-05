#!/bin/sh

while true; do
    nice --1 python3 spm_manager.py
    # sleep 10 minutes
    sleep $((10 * 60))
done