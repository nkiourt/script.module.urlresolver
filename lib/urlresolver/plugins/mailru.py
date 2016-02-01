"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import json
from t0mm0.common.net import Net
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class MailRuResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "mail.ru"
    domains = ["mail.ru"]

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        response = self.net.http_GET(web_url)

        html = response.content

        if html:
            js_data = json.loads(html)
            headers = dict(response._response.info().items())

            stream_url = ''
            best_quality = 0
            for video in js_data['videos']:
                if int(video['key'][:-1]) > best_quality:
                    stream_url = video['url']
                    best_quality = int(video['key'][:-1])

                if 'set-cookie' in headers:
                    stream_url += '|Cookie=%s' % (headers['set-cookie'])

            if stream_url:
                return stream_url

        raise UrlResolver.ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        user, media_id = media_id.split('|')
        return 'http://videoapi.my.mail.ru/videos/mail/%s/_myvideo/%s.json?ver=0.2.60' % (user, media_id)

    def get_host_and_id(self, url):
        try: host = re.findall('//(.+?)/', url)[0]
        except: return False
        try: user = re.findall('/mail/(.+?)/', url)[0]
        except: return False
        try: media_id = re.findall('(\d*)[.]html', url)[0]
        except: return False
        return host, '%s|%s' % (user, media_id)

    def valid_url(self, url, host):
        return 'mail.ru' in host
