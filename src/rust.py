import re

class RustMessageType:
    EVENT = 10
    SAVE = 11
    CONNECT = 12
    LOAD_BEGIN = 14
    MANIFEST_UPDATE = 15
    CHAT = 16
    ENTER_GAME = 17
    DISCONNECT_GAME = 18
    KILLED_BY_PLAYER = 19
    KILLED_BY_ENTITY = 20
    SUICIDE = 21
    UNKNOWN = 22
    JOINED = 23
    DISCONNECT_FAILED = 24
    SERVERVAR = 25
    EXCEPTION = 26

def get_console_message_info(message):
    servervar = r'\[ServerVar\]\ (.*)'
    event = r'\[event\]\ (.*)'
    saved = r'(Saved\ .*ents,\ cache\(.*\), write\(.*\), disk\(.*\)\.)|(Saving\ complete)'
    manifest = r'\[Manifest\]\ URI\ IS\ \"(.*)\"'
    killed_entity = r'(.*)\[([0-9]*)\/([0-9]*)\]\ was\ killed\ by\ ([^\ ]*)(\ \(entity\))$'
    killed_player = r'(.*)\[([0-9]*)\/([0-9]*)\]\ was\ killed\ by\ ([^\ ]*)(?:$|\n)'
    load_begin = r'(.+):([0-9]*)\/([0-9]*)\/([^\ ]*)\ has\ auth\ level\ ([0-9])'
    joined = r'(.+):([0-9]*)\/([0-9]*)\/([^\ ]*)\ joined\ \[([^/]+)\/([0-9]+)\]'
    entered = r'([^\ ]*)\[([0-9]*)\/([0-9]*)\]\ has\ entered\ the\ game'
    disconnect = r'(.+):([0-9]*)\/([0-9]*)\/([^\ ]*)\ disconnecting\:\ closing'
    disconnect_failed = r'(.+):([0-9]*)\/([0-9]*)\/([^\ ]*)\ disconnecting\:\ disconnect'
    chat = r'\[CHAT\]\ ([^[]*)\[([0-9]*)\/([0-9]*)\]\ \:\ (.*)(?:$|\n)'
    exception = r'Exception|exception'
    result = dict()

    try:
        # Save
        m = re.search(saved, message)
        if m is not None:
            result['message_type'] = RustMessageType.SAVE
            return result

        # Exception
        m = re.search(exception, message)
        if m is not None:
            result['message_type'] = RustMessageType.EXCEPTION
            return result

        # Event
        m = re.search(event, message)
        if m is not None:
            result['message_type'] = RustMessageType.EVENT
            result['event_type'] = m.group(1)
            return result

        # ServerVar
        m = re.search(servervar, message)
        if m is not None:
            result['message_type'] = RustMessageType.SERVERVAR
            result['message'] = m.group(1)
            return result

        # Manifest
        m = re.search(manifest, message)
        if m is not None:
            result['message_type'] = RustMessageType.MANIFEST_UPDATE
            result['url'] = m.group(1)
            return result

        # Manifest Update
        m = re.search(manifest, message)
        if m is not None:
            result['message_type'] = RustMessageType.MANIFEST_UPDATE
            return result

        # Killed by entity
        m = re.search(killed_entity, message)
        if m is not None:
            result['message_type'] = RustMessageType.KILLED_BY_ENTITY
            return result

        # Killed by player
        m = re.search(killed_player, message)
        if m is not None:
            result['message_type'] = RustMessageType.KILLED_BY_PLAYER
            return result

        # Begin loading the game resources
        m = re.search(load_begin, message)
        if m is not None:
            return RustMessageType.LOAD_BEGIN

        # Joined loading the game
        m = re.search(joined, message)
        if m is not None:
            assert(m.group(3) == m.group(6)) # For some reason rust puts the steam ID twice. Make sure this doesnt mean something
            result['message_type'] = RustMessageType.JOINED
            result['ip'] = m.group(1)
            result['steam_id'] = m.group(3)
            result['os'] = m.group(5)
            result['player_name'] = m.group(4)
            return result

        # Player Spawn
        m = re.search(entered, message)
        if m is not None:
            result['message_type'] = RustMessageType.ENTER_GAME
            result['player_name'] = m.group(1)
            result['steam_id'] = steam_id = m.group(3)
            return result

        # Disconnect
        m = re.search(disconnect, message)
        if m is not None:
            result['message_type'] = RustMessageType.DISCONNECT_GAME
            result['ip'] = m.group(1)
            result['steam_id'] = m.group(3)
            result['player_name'] = m.group(4)
            return result

        # Disconnect failed
        m = re.search(disconnect_failed, message)
        if m is not None:
            result['message_type'] = RustMessageType.DISCONNECT_FAILED
            result['ip'] = m.group(1)
            result['steam_id'] = m.group(3)
            result['player_name'] = m.group(4)
            return result

        # Chat
        m = re.search(chat, message)
        if m is not None:
            result['message_type'] = RustMessageType.CHAT
            result['player_name'] = m.group(1)
            result['steam_id'] = m.group(3)
            result['message'] = m.group(4)
            return result

    except TypeError as e:
        print("TypeError in console message parsing.")
        print("exception:", e)
        print("message:", message)
    except IndexError as e:
        print("IndexError no such group.")
        print("exception:", e)
        print("message:", message)
        print("reg ex result", m)
        for index, item in enumerate(m):
            print(" #%s: %s" % (index,item))



    result['message_type'] = RustMessageType.UNKNOWN
    return result

    # print('reg:', m)
    # print('groups:', m.groups())

