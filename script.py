import json
import re
import sys

# based on http://www.bigsoft.co.uk/blog/2008/04/11/configuring-ls_colors
LS_SUPPORT_REGEXP = re.compile('no|fi|di|ln|pi|do|bd|cd|or|so|su|sg|tw|ow|st|ex|mi|lc|rc|ec|(\*\.\w+)')

# 00=none 01=bold 04=underscore 05=blink 07=reverse 08=concealed
DECORATION_CODES = {
  'none': '09',
  'bold': '01',
  'underscore': '04',
  'blink': '05',
  'reverse': '07',
  'concealed': '08'
}

def has_ls_key_support(key):
  if (not LS_SUPPORT_REGEXP.match(key)):
    print("warn: {} is not supported in GNU ls".format(key), file=sys.stderr) 
    return False

  return True


def get_config(path = 'config.json'):
  with open(path, 'r') as f:
    config = json.load(f)

  return config


def hex_to_truecolor(hexcolor):
  r = str(int(hexcolor[1:3], 16))
  g = str(int(hexcolor[3:5], 16))
  b = str(int(hexcolor[5:7], 16))
  return '{};{};{}'.format(r,g,b)


def create_color_escape(bg, fg, decoration):
  bg_part = ''
  fg_part = ''

  dec_code = (';' + DECORATION_CODES[decoration]) if decoration else ''

  if (fg):
    fg_part = '38;2;{}{}'.format(fg, dec_code) 
  if (bg):
    bg_part = '48;2;{}{}'.format(bg, dec_code) 

  delimiter = ';' if fg and bg else '' 

  return '{}{}{}'.format(fg_part, delimiter, bg_part)


def create_datapoints(config):
  lf_icons = ""
  ls_colors = ""
  lf_colors = ""

  for datapoint in config['data']:
    icon = None
    bg = None
    fg = None
    lf_bg = None
    lf_fg = None
    decoration = None

    if ('decoration' in datapoint):
      decoration = datapoint['decoration']
    
    lf_decoration = decoration
    if ('lf_decoration' in datapoint):
      lf_decoration = datapoint['lf_decoration']


    if ('icon' in datapoint): 
      icon = datapoint['icon']

    if ('bg' in datapoint): 
      bg = hex_to_truecolor(datapoint['bg'])

    if ('fg' in datapoint): 
      fg = hex_to_truecolor(datapoint['fg'])
 
    if ('lf_fg' in datapoint): 
      lf_fg = hex_to_truecolor(datapoint['lf_fg'])
 
    if ('lf_bg' in datapoint): 
      lf_bg = hex_to_truecolor(datapoint['lf_bg'])
 
    color = create_color_escape(bg, fg, decoration)
    lf_color = create_color_escape(lf_bg, lf_fg, lf_decoration)

    for pattern in datapoint['patterns']:
      if (icon):
        lf_icons = '{}:{}={}'.format(lf_icons, pattern, icon)
      if (color and has_ls_key_support(pattern)):
        ls_colors = '{}:{}={}'.format(ls_colors, pattern, color)
      if (lf_color):
        lf_colors = '{}:{}={}'.format(lf_colors, pattern, lf_color)

  # remove first :
  lf_icons = lf_icons[1:]
  ls_colors = ls_colors[1:]
  lf_colors = lf_colors[1:]

  return {
    'lf_icons': lf_icons, 
    'ls_colors': ls_colors,
    'lf_colors': lf_colors
  }


def create_env_vars(lists):
  env_vars = ''
  if ('lf_icons' in lists and len(lists['lf_icons']) > 0):
    env_vars = '{}export LF_ICONS=\'{}\';\n'.format(env_vars, lists['lf_icons'])
  if ('ls_colors' in lists and len(lists['ls_colors']) > 0):
    env_vars = '{}export LS_COLORS=\'{}\';\n'.format(env_vars, lists['ls_colors'])
  if ('lf_colors' in lists and len(lists['lf_colors']) > 0):
    env_vars = '{}export LF_COLORS=\'{}\';\n'.format(env_vars, lists['lf_colors'])
  return env_vars


def write_env_script(path, content):
  f = open(path, "w")
  f.write(content)
  f.close()


config = get_config()

lists = create_datapoints(config)

env_vars = create_env_vars(lists)
 

if ('output' in config):
  write_env_script(config['output'], env_vars)
else:
  print(env_vars)

# print(env_vars)

