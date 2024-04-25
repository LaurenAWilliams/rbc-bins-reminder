# rbc-bins-reminder
I always forget to put the bins out. I set this up on my home server so I don't forget to put the bins out.

I guess this is what it means to be a Software Engineer :shrug:

## Setup

1. `pip install requests`
2. Set the following environment variables: `POSTCODE`, `ADDRESS_LINE`, `TARGET_EMAIL` (where you want the emails to go), `SMTP_EMAIL` (where the emails are coming from), `SMTP_TOKEN`.

## Execution

`python bins-reminder.py` for a one-shot run, but you probably want to run it in a cronjob so  `crontab -e ${USER}` and add `0 10 * * * python bins-reminder.py`.
