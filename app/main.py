import requests
import dotenv
import pickle
import os
import logging
import time

from sub import parse_schedule
from webhook import send_sub_embed, send_room_change_embed, send_announcement_embed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Load environment variables
dotenv.load_dotenv()

# Load configuration
webhook_url = os.getenv("WEBHOOK_URL")
target_class = os.getenv("TARGET_CLASS")

if not webhook_url:
    logging.error("WEBHOOK_URL environment variable is not set.")
    exit(1)

if not target_class:
    logging.error("TARGET_CLASS environment variable is not set.")
    exit(1)

data_file = "/app/already_sent.pkl"

def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    return [], [], []

def save_data(file_path, subs, room_changes, announcements):
    with open(file_path, 'wb') as f:
        pickle.dump((subs, room_changes, announcements), f)

already_sent_subs, already_sent_room_changes, already_sent_announcements = load_data(data_file)

while True:
    content = requests.get("https://helyettesites.petrik.hu")
    substitutions, room_changes, announcements, summary = parse_schedule(content.text)
    logging.info(f"Schedule covers dates: {', '.join(summary['dates'])}")
    logging.info(f"Total substitutions: {summary['total_substitutions']}")
    logging.info(f"Cancelled lessons: {summary['cancelled_lessons']}")
    logging.info(f"Room changes: {summary['total_room_changes']}")

    class_announcements = [a for a in announcements if target_class in a.content]
    class_announcements = [a for a in class_announcements if a not in already_sent_announcements]
    if class_announcements:
        logging.info(f"New announcements for class: {len(class_announcements)}")
        already_sent_announcements += class_announcements
        send_announcement_embed(webhook_url, class_announcements)
    else:
        logging.info(f"No new announcements for class out of {len(announcements)} total, already sent {len(already_sent_announcements)}.")

    class_subs = [s for s in substitutions if target_class in s.class_group]
    class_subs = [s for s in class_subs if s not in already_sent_subs]
    if class_subs:
        logging.info(f"New substitutions for class: {len(class_subs)}")
        already_sent_subs += class_subs
        send_sub_embed(webhook_url, class_subs)
    else:
        logging.info(f"No new substitutions for class out of {len(substitutions)} total, already sent {len(already_sent_subs)}.")

    class_room_changes = [r for r in room_changes if target_class in r.class_group]
    class_room_changes = [r for r in class_room_changes if r not in already_sent_room_changes]
    if class_room_changes:
        logging.info(f"New room changes for class: {len(class_room_changes)}")
        already_sent_room_changes += class_room_changes
        send_room_change_embed(webhook_url, room_changes)
    else:
        logging.info(f"No new room changes for class out of {len(room_changes)} total, already sent {len(already_sent_room_changes)}.")

    save_data(data_file, already_sent_subs, already_sent_room_changes, already_sent_announcements)
    time.sleep(60)