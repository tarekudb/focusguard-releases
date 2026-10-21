name: FocusGuard Payment Bot

on:
  workflow_dispatch: 
  schedule:
    - cron: '0 */6 * * *' # প্রতি ৬ ঘণ্টায় একবার বট রিস্টার্ট হবে

jobs:
  run-bot:
    runs-on: ubuntu-latest
    timeout-minutes: 350 # সর্বোচ্চ ৫ ঘণ্টা ৫০ মিনিট চলবে
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: pip install requests

    - name: Run Bot
      env:
        TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
        TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        GH_PAT: ${{ secrets.GH_PAT }}
      run: python bot.py
