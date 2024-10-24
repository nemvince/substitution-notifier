from datetime import datetime
import pytz

periods = [
  # no period
  {"period": -1, "starttime": "0:00", "endtime": "0:00"},
  {"period": 0, "starttime": "7:10", "endtime": "7:55"},
  {"period": 1, "starttime": "8:00", "endtime": "8:45"},
  {"period": 2, "starttime": "8:55", "endtime": "9:40"},
  {"period": 3, "starttime": "9:55", "endtime": "10:40"},
  {"period": 4, "starttime": "10:50", "endtime": "11:35"},
  {"period": 5, "starttime": "11:45", "endtime": "12:30"},
  {"period": 6, "starttime": "12:50", "endtime": "13:35"},
  {"period": 7, "starttime": "13:45", "endtime": "14:30"},
  {"period": 8, "starttime": "14:35", "endtime": "15:20"},
  {"period": 9, "starttime": "15:20", "endtime": "16:00"},
  {"period": 10, "starttime": "16:00", "endtime": "16:40"},
  {"period": 11, "starttime": "16:45", "endtime": "17:25"},
  {"period": 12, "starttime": "17:30", "endtime": "18:10"},
  {"period": 13, "starttime": "18:15", "endtime": "18:55"},
  {"period": 14, "starttime": "19:00", "endtime": "19:40"},
  {"period": 15, "starttime": "19:45", "endtime": "20:25"},
  {"period": 16, "starttime": "20:30", "endtime": "21:10"},
]

def get_timestamp(period: int, date: str) -> str:
  """Get the timestamp for a given period and date."""
  for p in periods:
    if p["period"] == period:
      date = parse_date(date)[0]
      date = date.replace(hour=int(p["starttime"].split(":")[0]), minute=int(p["starttime"].split(":")[1]))
      date = date.astimezone(pytz.utc)
      return date.strftime("%Y-%m-%d %H:%M")

  return None

def parse_date(date: str):
  # formatted "2020.09.01. - Kedd"
  date = date.split(" - ")[0]
  return [datetime.strptime(date, "%Y.%m.%d"), date[1]]