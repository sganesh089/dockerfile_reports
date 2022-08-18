#!/bin/bash

exec python3 ./generate_data.py &
exec python3 ./generate_report_2.py

/bin/bash
