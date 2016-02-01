'''
divxstage urlresolver plugin
Copyright (C) 2011 t0mm0, DragonWin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import re
from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class DivxstageResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = 'divxstage'
    domains = ['divxstage.eu', 'divxstage.net', 'divxstage.to', 'cloudtime.to']

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        r = re.search('flashvars.filekey=(.+?);', html)
        if r:
            r = r.group(1)

            try: filekey = re.compile('\s+%s="(.+?)"' % r).findall(html)[-1]
            except: filekey = r

            player_url = 'http://www.cloudtime.to/api/player.api.php?key=%s&file=%s' % (filekey, media_id)

            html = self.net.http_GET(player_url).content

            r = re.search('url=(.+?)&', html)

            if r:
                stream_url = r.group(1)
            else:
                raise UrlResolver.ResolverError('File Not Found or removed')

        return stream_url

    def get_url(self, host, media_id):
        return 'http://embed.cloudtime.to/embed.php?v=%s' % media_id

    def get_host_and_id(self, url):
        try: host = re.findall('//(.+?)/', url)[0]
        except: return False
        media_id = re.findall('//.+?/.+?/([\w]+)', url)
        media_id += re.findall('//.+?/.+?v=([\w]+)', url)
        try: media_id = media_id[0]
        except: return False
        return host, media_id

    def valid_url(self, url, host):
        if any(i in host for i in self.domains):
            return True
