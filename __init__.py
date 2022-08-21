import os
from cudatext import *
import cudatext_cmd as cmds
import requests
import html

GET_TIMEOUT = 5 # in seconds

FORMATS = {
    'Markdown': '[{title}]({url})',
    'reStructuredText': '`{title} <{url}>`__',
}

def dbg(s):
    #print(s)
    pass

def get_title(s, tag):
    n = s.find('<'+tag+'>')
    if n<0:
        dbg('no <title>: '+s)
        return
    s = s[n+len(tag)+2:]
    n = s.find('</'+tag+'>')
    if n<0:
        dbg('no </title>: '+s)
        return
    s = s[:n]
    return html.unescape(s)


class Command:

    def on_paste(self, ed_self, keep_caret, select_then):

        # Shift pressed? don't work
        state = app_proc(PROC_GET_KEYSTATE, '')
        if 's' in state:
            return

        s = app_proc(PROC_GET_CLIP, '')
        if '\n' in s:
            return
        if not s.startswith('http://') and not s.startswith('https://'):
            return

        try:
            r = requests.get(s, verify=False, timeout=GET_TIMEOUT)
        except:
            return

        if not r:
            return
        text = r.content.decode('utf-8', errors='replace')
        if not text:
            return

        title = get_title(text, 'title') or get_title(text, 'TITLE') or 'Title'

        lex = ed.get_prop(PROP_LEXER_CARET)
        fmt = FORMATS.get(lex)
        if not fmt:
            return
        fmt = fmt.replace('{url}', s)
        fmt = fmt.replace('{title}', title)

        ed.cmd(cmds.cCommand_TextInsert, fmt)
        return False #block usual Paste
