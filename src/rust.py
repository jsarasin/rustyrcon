import re

class RustMessageType:
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

def get_console_message_info(message):
    event = r'(\[event\]\ )(.*)'
    saved = r'(Saved\ .*ents,\ cache\(.*\), write\(.*\), disk\(.*\)\.)|(Saving\ complete)'
    manifest = r'\[Manifest\]\ URI\ IS\ \"(.*)\"'
    killed_entity = r'(.*)\[([0-9]*)\/([0-9]*)\]\ was\ killed\ by\ ([^\ ]*)(\ \(entity\))$'
    killed_player = r'(.*)\[([0-9]*)\/([0-9]*)\]\ was\ killed\ by\ ([^\ ]*)$'
    load_begin = r'(.+):([0-9]*)\/([0-9]*)\/([^\ ]*)\ has\ auth\ level\ ([0-9])'
    entered = r'([^\ ]*)\[([0-9]*)\/([0-9]*)\]\ has\ entered\ the\ game'
    disconnect = r'(.+):([0-9]*)\/([0-9]*)\/([^\ ]*)\ disconnecting\:\ closing'

    m = re.search(saved, message)
    if m != None:
        return RustMessageType.SAVE

    m = re.search(manifest, message)
    if m != None:
        return RustMessageType.MANIFEST_UPDATE

    m = re.search(killed_entity, message)
    if m != None:
        return RustMessageType.KILLED_BY_ENTITY

    m = re.search(killed_player, message)
    if m != None:
        return RustMessageType.KILLED_BY_PLAYER

    m = re.search(load_begin, message)
    if m != None:
        return RustMessageType.LOAD_BEGIN

    m = re.search(entered, message)
    if m != None:
        return RustMessageType.ENTER_GAME

    m = re.search(disconnect, message)
    if m != None:
        return RustMessageType.DISCONNECT_GAME

    return None
    # print('reg:', m)
    # print('groups:', m.groups())

