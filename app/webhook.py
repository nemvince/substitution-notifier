from discord_webhook import DiscordWebhook, DiscordEmbed
from utils import get_timestamp

def make_webhook(url):
    webhook = DiscordWebhook(url=url)
    webhook.username = "Petrik Helyettesítés"
    webhook.avatar_url = "https://helyettesites.petrik.hu/icon.png"
    return webhook

def send_sub_embed(webhook_url, subs):
    for sub in subs:
        webhook = make_webhook(webhook_url)
        title = f"{sub.date.split(" - ")[1]}: {sub.lesson}. óra "
        if sub.status == "Cancelled":
            title += "Elmarad!"
        else:
            title += sub.substitute_teacher + " helyettesít!"
        embed = DiscordEmbed(title=title, color=0x72c3b6)
        embed.add_embed_field(name="Tanár", value=sub.teacher)
        embed.add_embed_field(name="Óra", value=sub.lesson)
        if sub.substitute_teacher:
            embed.add_embed_field(name="Helyettesít", value=sub.substitute_teacher)
        embed.add_embed_field(name="Terem", value=sub.room)
        embed.add_embed_field(name="Osztály", value=sub.class_group)
        if sub.notes:
            embed.add_embed_field(name="Megjegyzés", value=sub.notes)
        embed.set_footer(text="Petrik Helyettesítés")
        embed.timestamp = get_timestamp(sub.lesson, sub.date)
        webhook.add_embed(embed)
        webhook.execute()

def send_room_change_embed(webhook_url, room_changes):
    for room_change in room_changes:
        webhook = make_webhook(webhook_url)
        title = f"{room_change.date.split(" - ")[1]}: {room_change.lesson}. óra teremcsere!"
        embed = DiscordEmbed(title=title, color=0x72c3b6)
        embed.add_embed_field(name="Eredeti terem", value=room_change.original_room)
        embed.add_embed_field(name="Új terem", value=room_change.new_room)
        embed.add_embed_field(name="Osztály", value=room_change.class_group)
        embed.set_footer(text="Petrik Helyettesítés")
        embed.timestamp = get_timestamp(room_change.lesson, room_change.date)
        webhook.add_embed(embed)
        webhook.execute()

def send_announcement_embed(webhook_url, announcements):
    for announcement in announcements:
        webhook = make_webhook(webhook_url)
        title = f"{announcement.date.split(" - ")[1]}: {announcement.content}"
        embed = DiscordEmbed(title=title, color=0x72c3b6)
        embed.set_footer(text="Petrik Helyettesítés")
        embed.timestamp = get_timestamp(-1, announcement.date)
        webhook.add_embed(embed)
        webhook.execute()