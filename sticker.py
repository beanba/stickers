#!/usr/bin/env python

from pyadb import ADB

import argparse
import json
import os
import re
import shutil

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='clean or pull line stickers')
  parser.add_argument('--clean', action='store_true', help='clean instead')
  parser.add_argument('--keep', action='store_true', help='keep all pulled stickers')
  parser.add_argument('--skipadb', action='store_true', help='skip adb pull, just generate html')
  args = parser.parse_args()

  with open('stickers.json') as jf:
    stickers_json = json.load(jf)

  if not args.skipadb:
    adb = ADB('{0}/platform-tools/adb'.format(os.environ['ANDROID_HOME']))

    if args.clean:
      adb.shell_command('rm -rf /sdcard/Android/data/jp.naver.line.android/stickers')
      exit(0)

    print json.dumps(stickers_json, sort_keys=True, indent=2, separators=(',', ': '))

    adb.get_remote_file('/sdcard/Android/data/jp.naver.line.android/stickers', 'stickers')
    for d in os.listdir('stickers'):
      if d in stickers_json:
        stickers = os.listdir('stickers/{0}'.format(d))
        if len(stickers) == int(stickers_json[d]['count']) + 3:
          print 'keep {0}'.format(d)
          continue
      if not args.keep:
        print 'remove {0}'.format(d)
        shutil.rmtree('{0}/{1}'.format('stickers', d))

  with open('index.html', 'w') as index_html:
    index_html.write('<html><head></head><body>')

    for d in sorted(os.listdir('stickers')):
      with open('{0}.html'.format(d), 'w') as d_html:
        d_html.write('<html><head><title>{0}</title></head><body><a target="_blank" href="https://store.line.me/stickershop/product/{1}"><h1>{0}</h1></a><table><tr>'.format(stickers_json[d]['name'], d))

        for idx, f in enumerate(sorted(os.listdir('stickers/{0}'.format(d)))):
          if re.match('\d+', f):
            d_html.write('<td style="text-align:center;"><img src="stickers/{0}/{1}"></td>'.format(d, f))
            if idx % 4 == 3:
              d_html.write('</tr><tr>')

        d_html.write('</tr></table></body></html>')

        if stickers_json[d]['ani']:
          main_png = 'stickers/{0}/main_ani'.format(d)
        else:
          main_png = 'stickers/{0}/main'.format(d)

        index_html.write('<a target="_blank" href="{0}.html"><img src="{1}"></a>'.format(d, main_png))

    index_html.write('</body></html>')
