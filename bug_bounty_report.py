#!/usr/bin/env python3
import os
import requests

print('Creating report...')
report_file = open('bug_report.txt', 'w')
report_file.write('# Bug Bounty Report\n')
report_file.write('# Severity\tDescription\tReward\n')
report_file.write('-----------------\n')

# Define bug categories and rewards
critical_bugs = ['Fund theft, consensus bypass, RCE', '100-200 RTC']
high_bugs = ['Data leak, auth bypass, significant logic error', '50-100 RTC']
medium_bugs = ['DoS, info disclosure, moderate bugs', '15-50 RTC']
low_bugs = ['UI bugs, minor leaks, doc errors', '5-15 RTC']

# Write bug categories and rewards to report file
report_file.write('Critical\t')
for bug in critical_bugs:
report_file.write(bug + '\n')
report_file.write('\nHigh\t')
for bug in high_bugs:
report_file.write(bug + '\n')
report_file.write('\nMedium\t')
for bug in medium_bugs:
report_file.write(bug + '\n')
report_file.write('\nLow\t')
for bug in low_bugs:
report_file.write(bug + '\n')

# Save and close the report file
report_file.close()

