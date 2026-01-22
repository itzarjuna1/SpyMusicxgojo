# made by itz arjuna copyrighted under us
from pyrogram import filters
from pyrogram.raw.functions.phone import GetGroupCall, GetGroupCallParticipants
from pyrogram.raw.types import InputGroupCall
from pyrogram.enums import ParseMode

from Spy import app


# -------------------- SMALL CAPS -------------------- #
def small_caps(text: str):
    normal = "abcdefghijklmnopqrstuvwxyz"
    small = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
    table = str.maketrans(normal, small)
    return text.lower().translate(table)


# -------------------- GET ACTIVE VC -------------------- #
async def get_group_call(client, chat_id):
    try:
        full_chat = await client.invoke(
            GetGroupCall(
                peer=await client.resolve_peer(chat_id),
                limit=1
            )
        )
        return full_chat.call
    except:
        return None


# -------------------- FETCH VC PARTICIPANTS -------------------- #
async def fetch_vc_participants(client, chat_id):
    call = await get_group_call(client, chat_id)
    if not call:
        return []

    participants = await client.invoke(
        GetGroupCallParticipants(
            call=InputGroupCall(
                id=call.id,
                access_hash=call.access_hash
            ),
            ids=[],
            sources=[],
            offset=0,
            limit=100
        )
    )

    return participants.participants


# -------------------- RESOLVE USERS -------------------- #
async def resolve_users(client, participants):
    users = []

    for p in participants:
        try:
            if hasattr(p.peer, "user_id"):
                user = await client.get_users(p.peer.user_id)
                users.append(user)
        except:
            pass

    return users


# -------------------- FORMAT HTML BLOCKQUOTE -------------------- #
def format_members(users):
    text = f"<blockquote>🎧 <b>{small_caps('vc members')}</b>\n\n"

    for u in users:
        name = u.first_name or "Unknown"
        username = f"@{u.username}" if u.username else "None"

        text += (
            f"➜ <b>{small_caps('name')} :</b> {name}\n"
            f"➜ <b>{small_caps('id')} :</b> <code>{u.id}</code>\n"
            f"➜ <b>{small_caps('username')} :</b> {username}\n\n"
        )

    text += f"✨ <b>{small_caps('powered by upper moon bots')}</b></blockquote>"
    return text


# -------------------- COMMAND HANDLER -------------------- #
@app.on_message(filters.command("vcmembers") & filters.group)
async def vc_members_handler(_, message):
    try:
        participants = await fetch_vc_participants(app, message.chat.id)

        if not participants:
            return await message.reply_text(
                f"<blockquote>❌ <b>{small_caps('no active voice chat found')}</b></blockquote>",
                parse_mode=ParseMode.HTML
            )

        users = await resolve_users(app, participants)
        text = format_members(users)

        await message.reply_text(text, parse_mode=ParseMode.HTML)

    except Exception:
        await message.reply_text(
            f"<blockquote>⚠️ <b>{small_caps('failed to fetch vc members')}</b></blockquote>",
            parse_mode=ParseMode.HTML
        )
