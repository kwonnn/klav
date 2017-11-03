import discord
import json
import requests

async def show_command_usage(client, command, dest_channel):
    report = '**Help message for**: `.{}`\n'.format(command)
    if command == 'set':
        report += 'Set your last.fm username\n'
        report += 'Usage: `.set <username>`\n'
        report += 'Example: `.set 77davez`'
    elif command == 'compat':
        report += 'Check your compatibility with another user. You need to @ the other user\n'
        report += 'Usage: `.compare @other_user`'
    elif command == 'show':
        report += 'Show your currently-set last.fm username\n'
        report += 'Usage: .show'
    await client.send_message(dest_channel, report)

async def command_help(client, message):
    command = 'help'
    content = message.content.lower().strip()
    if content[1:1+len(command)] != 'help': return
    split = message.content.split()
    if len(split) == 1:
        report = 'Available commands: `help set show compat`\n'
        report += 'Example: `.help compat`'
        await client.send_message(message.channel, report)
    elif len(split) == 2:
        subcommand = split[1].lower()
        await show_command_usage(client, subcommand, message.channel)
    else:
        report = 'Usage: .help OR .help <command>\n'
        report += 'Example: `.help set`'
        await client.send_message(message.channel, report)

async def command_show_username(client, message):
    command = 'show'
    content = message.content.lower().strip()

    if content[1:] != command: return

    if message.author.id not in client.usernames:
        report = ':bangbang: You haven\'t set a username yet. Use the `set` command to do so'
        await client.send_message(message.channel, report)
    else:
        username = client.usernames[message.author.id]
        report = '{} Your username is currently set to: **{}**'
        report = report.format(message.author.mention, sanitize(username))
        await client.send_message(message.channel, report)

async def command_set_username(client, message):
    command = 'set'
    content = message.content.lower().strip()
    if content[1:1+len(command)] != command: return

    split = content.split()
    if len(split) != 2:
        await show_command_usage(client, 'set', message.channel)
        return

    username = split[1].lower()
    client.usernames[message.author.id] = split[1]

    headers = { 'Content-Type': 'application/json; charset=utf-8', 'Data-Type': 'json', }
    r = requests.put(client.bin, data=json.dumps(client.usernames), headers=headers)

    if r is None:
        report = ':no_entry: Failed to make HTTP request'
        await client.send_message(message.channel, report)
        return

    if r.status_code != requests.codes.ok:
        report = ':no_entry: Failed to set username. Error code: **{}**'.format(r.status_code)
        await client.send_message(message.channel, report)
        return

    report = ':white_check_mark: {} your last.fm username has been set to: **{}**'
    report = report.format(message.author.mention, sanitize(username))
    await client.send_message(message.channel, report)

async def command_check_compat(client, message):
    command = 'compat'
    content = message.content.lower().strip()

    if content[1:1+len(command)] != command: return

    if message.author.id not in client.usernames:
        report = ':bangbang: You haven\'t set a username yet. Use the `set` command to do so'
        await client.send_message(message.channel, report)
        return

    if len(message.mentions) != 1:
        await show_command_usage(client, 'compat', message.channel)
        return

    target = message.mentions[0]
    if target.id not in client.usernames:
        report = ':shrug: This user has not set their last.fm username'
        await client.send_message(message.channel, report)
        return

    usernames = (client.usernames[message.author.id], client.usernames[target.id])

    compat, common_artists = check_lastfm_compat(client, usernames)
    report = '{} Your compatibility with **{}** is **{}**\n'.\
             format(message.author.mention, sanitize(usernames[1]), compat)
    report += 'You both listen to {}'.format(', '.join(common_artists))
    await client.send_message(message.channel, report)

def check_lastfm_compat(client, usernames):
    return 'Super', ['1', '2', '3']

def sanitize(s):
    res = s.replace('*', '\*')
    res = res.replace('_', '\_')
    res = res.replace('\\', '\\\\')
    return res