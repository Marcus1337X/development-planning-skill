from datetime import datetime, timezone, timedelta

print(datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
