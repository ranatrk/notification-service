from .celery import app

@app.task
def notify_sms_group(message_id, extra, phone_numbers, language):
  from .notification_messages import English,French
  if language == "English":
    message = English[message_id].value.format(extra)
  elif language == "French":
    message = French[message_id].value.format(extra)
  print(f"GROUP SMS ({language}): {message} , {phone_numbers}")

@app.task
def notify_sms_single(message_id, extra, phone_number, language):
  from .notification_messages import English,French
  if language == "English":
    message = English[message_id].value.format(extra)
  elif language == "French":
    message = French[message_id].value.format(extra)
  print(f"CUSTOM SINGLE SMS ({language}): {message} , {phone_number}")

@app.task
def notify_push_group(message_id, extra, user_ids, language):
  from .notification_messages import English,French
  if language == "English":
    message = English[message_id].value.format(extra)
  elif language == "French":
    message = French[message_id].value.format(extra)
  print(f"GROUP PUSH NOTIFICATION ({language}): {message} , {user_ids}")

@app.task
def notify_push_single(message_id, extra, user_id, language):
  from .notification_messages import English,French
  if language == "English":
    message = English[message_id].value.format(extra)
  elif language == "French":
    message = French[message_id].value.format(extra)
  print(f"CUSTOM SINGLE PUSH NOTIFICATION ({language}): {message} , {user_id}")

