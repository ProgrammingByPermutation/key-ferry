FROM_KEY_TO_SENDKEY = {
    'BACKSPACE': '{BACKSPACE}',
    'BACK': '{BACKSPACE}',
    'BREAK': '{BREAK}',
    'PAUSE': '{BREAK}',
    'CAPS LOCK': '{CAPSLOCK}',
    'CAPITAL': '{CAPSLOCK}',
    'DELETE': '{DELETE}',
    'DEL': '{DEL}',
    'DOWN ARROW': '{DOWN}',
    'DOWN': '{DOWN}',
    'END': '{END}',
    'ENTER': '{ENTER}',
    'RETURN': '{ENTER}',
    'ESC': '{ESC}',
    'ESCAPE': '{ESC}',
    'HELP': '{HELP}',
    'HOME': '{HOME}',
    'INSERT': '{INSERT}',
    'INS': '{INS}',
    'LEFT ARROW': '{LEFT}',
    'LEFT': '{LEFT}',
    'NUM LOCK': '{NUMLOCK}',
    'NUMLOCK': '{NUMLOCK}',
    'PAGE DOWN': '{PGDN}',
    'NEXT': '{PGDN}',
    'PAGE UP': '{PGUP}',
    'PRIOR': '{PGUP}',
    'PRINT SCREEN': '{PRTSC}',
    'RIGHT ARROW': '{RIGHT}',
    'RIGHT': '{RIGHT}',
    'SCROLL LOCK': '{SCROLLLOCK}',
    'TAB': '{TAB}',
    'UP ARROW': '{UP}',
    'UP': '{UP}',
    'SPACE': ' ',
    'F1': '{F1}',
    'F2': '{F2}',
    'F3': '{F3}',
    'F4': '{F4}',
    'F5': '{F5}',
    'F6': '{F6}',
    'F7': '{F7}',
    'F8': '{F8}',
    'F9': '{F9}',
    'F10': '{F10}',
    'F11': '{F11}',
    'F12': '{F12}',
    'F13': '{F13}',
    'F14': '{F14}',
    'F15': '{F15}',
    'F16': '{F16}',
    '!': '{!}',
    '#': '{#}',
    '+': '{+}',
    '^': '{^}',
    '{': '{{}',
    '}': '{}}',
    'LWIN': '^{ESC}',
    'RWIN': '^{ESC}'
}


def to_send_key(key, ctrl, alt, shift):
    """
    Translates a key stroke to the correct command required by SendKeys.
    :param key: The key to translate.
    :return: The correct key command or None if not found.
    """
    command = FROM_KEY_TO_SENDKEY.get(key.upper(), None)

    if command is not None:
        return command

    result = ''
    if ctrl:
        result += '^'
    if alt:
        result += '%'
    if shift:
        result += '+'

    need_close = False
    if result != '':
        result += '{'
        need_close = True

    result += key.lower()

    if need_close:
        result += '}'

    return result
