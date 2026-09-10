# coding=utf-8
# Original crawler + JPEG EXIF repair via site-bound image proxy.
import base64
from html import unescape
import re
import sys
import urllib.parse
sys.path.append('..')
from base.spider import Spider
class Spider(Spider):
  host = 'https://hanime1.me'
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
           '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://hanime1.me/',
    'Accept-Language': 'zh-TW,zh;q=0.9,zh-CN;q=0.8',
  }
  cates = [
    ('最新里番', 'genre_sort:裏番|最新上市'),
    ('最新上市', 'sort:最新上市'),
    ('最新上传', 'sort:最新上傳'),
    ('里番', '裏番'),
    ('泡面番', '泡麵番'),
    ('Motion Anime', 'Motion Anime'),
    ('3DCG', '3DCG'),
    ('2.5D', '2.5D'),
    ('2D动画', '2D動畫'),
    ('AI生成', 'AI生成'),
    ('MMD', 'MMD'),
    ('Cosplay', 'Cosplay'),
    ('新番预告', '新番預告'),
  ]
  sorts = [
    {'n': '最新上市', 'v': '最新上市'},
    {'n': '最新上传', 'v': '最新上傳'},
    {'n': '本日排行', 'v': '本日排行'},
    {'n': '本周排行', 'v': '本週排行'},
    {'n': '本月排行', 'v': '本月排行'},
  ]
  def getName(self):
    return 'hanime1'
  def init(self, extend=''):
    pass
  def isVideoFormat(self, url):
    pass
  def manualVideoCheck(self):
    pass
  def destroy(self):
    pass
  @staticmethod
  def _cover_host(url):
    try:
      parts = urllib.parse.urlsplit(url)
      return (parts.scheme == 'https' and parts.port in (None, 443)
          and not parts.username and not parts.password
          and parts.hostname in ('hanime1.me', 'www.hanime1.me',
                     'vdownload.hembed.com', 'i.imgur.com'))
    except (ValueError, TypeError):
      return False
  def _cover_pic(self, url, vid):
    url = unescape(url or '').strip()
    if not self._cover_host(url):
      return url
    try:
      parts = urllib.parse.urlsplit(self.getProxyUrl())
      query = dict(urllib.parse.parse_qsl(parts.query))
      key = str(getattr(self, 'siteKey', '') or query.get('siteKey', ''))
      if key and parts.scheme in ('http', 'https') and parts.netloc:
        token = base64.urlsafe_b64encode(url.encode()).decode().rstrip('=')
        query.update(type='cover', image=token, vid=str(vid),
              siteKey=key, cover_rev='6')
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc,
          parts.path, urllib.parse.urlencode(query), ''))
    except Exception:
      pass
    return url
  def localProxy(self, param):
    if not isinstance(param, dict) or param.get('type') != 'cover':
      return [400, 'text/plain', b'Invalid cover request', {}]
    try:
      token = param.get('image', '')
      vid = str(param.get('vid', ''))
      if not isinstance(token, str) or len(token) > 16384 or not re.fullmatch(r'[A-Za-z0-9_-]+', token) or not re.fullmatch(r'\d+', vid):
        return [400, 'text/plain', b'Invalid cover request', {}]
      url = base64.urlsafe_b64decode(token + '=' * (-len(token) % 4)).decode()
    except (ValueError, UnicodeError):
      return [400, 'text/plain', b'Invalid cover URL', {}]
    import requests
    headers = dict(self.headers)
    headers['Referer'] = self.host + '/watch?v=' + vid
    try:
      for _ in range(4):
        if not self._cover_host(url):
          return [403, 'text/plain', b'Cover host not allowed', {}]
        with requests.get(url, headers=headers, timeout=(5, 10),
                 allow_redirects=False, stream=True) as response:
          if response.status_code in (301, 302, 303, 307, 308):
            if not response.headers.get('Location'):
              break
            url = urllib.parse.urljoin(url, response.headers['Location'])
            continue
          if response.status_code != 200:
            break
          chunks, size = [], 0
          for chunk in response.iter_content(65536):
            size += len(chunk)
            if size > 5 * 1024 * 1024:
              raise ValueError('Image too large')
            chunks.append(chunk)
          data = self._sanitize_jpeg(b''.join(chunks))
          mime = self._image_mime(data)
          if mime:
            return [200, mime, data, {'Cache-Control': 'private, max-age=300'}]
          break
    except (requests.RequestException, ValueError):
      pass
    return [502, 'text/plain', b'Cover unavailable', {'Cache-Control': 'no-store'}]
  @staticmethod
  def _image_mime(data):
    if data.startswith(b'\xff\xd8\xff'):
      return 'image/jpeg'
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
      return 'image/png'
    if data.startswith((b'GIF87a', b'GIF89a')):
      return 'image/gif'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
      return 'image/webp'
    return ''
  @staticmethod
  def _valid_exif_header(payload):
    tiff = payload[6:]
    if len(tiff) < 8 or tiff[:4] not in (b'II\x2a\x00', b'MM\x00\x2a'):
      return False
    order = 'little' if tiff[:2] == b'II' else 'big'
    offset = int.from_bytes(tiff[4:8], order)
    if offset < 8 or offset + 2 > len(tiff):
      return False
    count = int.from_bytes(tiff[offset:offset + 2], order)
    if offset + 2 + count * 12 + 4 > len(tiff):
      return False
    for index in range(count):
      entry = tiff[offset + 2 + index * 12:offset + 14 + index * 12]
      tag = int.from_bytes(entry[:2], order)
      if tag == 0x0112:
        kind = int.from_bytes(entry[2:4], order)
        components = int.from_bytes(entry[4:8], order)
        orientation = int.from_bytes(entry[8:10], order)
        if kind != 3 or components != 1 or not 1 <= orientation <= 8:
          return False
    return True
  @classmethod
  def _sanitize_jpeg(cls, data):
    if not data.startswith(b'\xff\xd8'):
      return data
    pieces = [data[:2]]
    pos = 2
    changed = False
    while pos < len(data):
      start = pos
      if data[pos] != 0xff:
        return data
      while pos < len(data) and data[pos] == 0xff:
        pos += 1
      if pos >= len(data):
        return data
      marker = data[pos]
      pos += 1
      if marker in (0xda, 0xd9):
        return b''.join(pieces) + data[start:] if changed else data
      if marker in (0xd8, 0x01) or 0xd0 <= marker <= 0xd7:
        pieces.append(data[start:pos])
        continue
      if marker == 0 or pos + 2 > len(data):
        return data
      length = int.from_bytes(data[pos:pos + 2], 'big')
      end = pos + length
      if length < 2 or end > len(data):
        return data
      payload = data[pos + 2:end]
      bad_exif = (marker == 0xe1 and payload.startswith(b'Exif\x00\x00')
            and not cls._valid_exif_header(payload))
      if bad_exif:
        changed = True
      else:
        pieces.append(data[start:end])
      pos = end
    return data
  def _get(self, url):
    try:
      return self.fetch(url, headers=self.headers, timeout=15).text
    except Exception:
      import requests
      return requests.get(url, headers=self.headers, timeout=15).text
  def _meta(self, html, prop):
    m = re.search(r'<meta[^>]+property="%s"[^>]+content="([^"]*)"' % prop, html)
    if not m:
      m = re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="%s"' % prop, html)
    return m.group(1).strip() if m else ''
  def parse_list(self, html):
    videos = []
    seen = set()
    card_pattern = re.compile(
      r'<a[^>]+href=["\'](?:https?://hanime1\.me)?/watch\?v=(\d+)["\'][^>]*>(.*?)</a>',
      re.S
    )
    for m in card_pattern.finditer(html):
      vid = m.group(1)
      if vid in seen:
        continue
      inner = m.group(2)
      title = ''
      t = re.search(
        r'class="[^"]*(?:title|name)[^"]*"[^>]*>\s*([^<]+?)\s*<',
        inner, re.S
      )
      if t:
        title = t.group(1).strip()
      if not title:
        t = re.search(r'<img[^>]+alt="([^"]+)"', inner)
        if t:
          title = t.group(1).strip()
      if not title:
        t = re.search(r'title="([^"]+)"', m.group(0))
        if t:
          title = t.group(1).strip()
      if not title:
        continue
      pic = ''
      for img in re.findall(r'<img[^>]+(?:data-src|src)="(http[^"]+)"', inner):
        if '.gif' in img or 'icon' in img or 'avatar' in img:
          continue
        pic = img
        break
      seen.add(vid)
      videos.append({
        'vod_id': vid,
        'vod_name': title,
        'vod_pic': self._cover_pic(pic, vid),
        'vod_remarks': ''
      })
    if not videos:
      videos = self._parse_list_fallback(html)
    return videos
  def _parse_list_fallback(self, html):
    videos = []
    seen = set()
    for m in re.finditer(
      r'<a[^>]+href=["\'][^"\']*watch\?v=(\d+)["\']([^>]*)>(.*?)</a>',
      html, re.S
    ):
      vid = m.group(1)
      if vid in seen:
        continue
      attrs = m.group(2)
      inner = m.group(3)
      t = re.search(r'title="([^"]+)"', attrs)
      title = t.group(1).strip() if t else ''
      if not title:
        title = re.sub(r'<[^>]+>', '', inner).strip()
      if not title:
        continue
      seen.add(vid)
      videos.append({'vod_id': vid, 'vod_name': title, 'vod_pic': '', 'vod_remarks': ''})
    return videos
  def homeContent(self, filter):
    classes = [{'type_name': n, 'type_id': v} for n, v in self.cates]
    filters = {}
    for _, v in self.cates:
      if not v.startswith('sort:') and not v.startswith('genre_sort:'):
        filters[v] = [{'key': 'sort', 'name': '排序', 'value': self.sorts}]
    return {'class': classes, 'filters': filters}
  def homeVideoContent(self):
    html = self._get(self.host)
    return {'list': self.parse_list(html)[:30]}
  def categoryContent(self, tid, pg, filter, extend):
    if tid.startswith('genre_sort:'):
      parts = tid[len('genre_sort:'):].split('|', 1)
      genre = parts[0]
      sort  = parts[1] if len(parts) > 1 else ''
      url = '{}/search?genre={}&page={}'.format(
        self.host, urllib.parse.quote(genre), pg)
      if sort:
        url += '&sort=' + urllib.parse.quote(sort)
    elif tid.startswith('sort:'):
      sort_val = tid[len('sort:'):]
      url = '{}/search?sort={}&page={}'.format(
        self.host, urllib.parse.quote(sort_val), pg)
    else:
      url = '{}/search?genre={}&page={}'.format(
        self.host, urllib.parse.quote(tid), pg)
      if extend and extend.get('sort'):
        url += '&sort=' + urllib.parse.quote(extend['sort'])
    html = self._get(url)
    videos = self.parse_list(html)
    return {
      'list': videos,
      'page': int(pg),
      'pagecount': int(pg) + (1 if len(videos) >= 20 else 0),
      'limit': 30,
      'total': 999999
    }
  def detailContent(self, ids):
    vid = ids[0]
    html = self._get('{}/watch?v={}'.format(self.host, vid))
    title = self._meta(html, 'og:title')
    pic   = self._meta(html, 'og:image')
    desc  = self._meta(html, 'og:description')
    episodes = self._extract_playlist(html, vid, title)
    def safe_ep_name(name):
      return name.replace('#', '＃')
    play_url = '#'.join(
      '{}${}'.format(safe_ep_name(ep['name']), ep['vid'])
      for ep in episodes
    )
    vod = {
      'vod_id'       : vid,
      'vod_name'     : title,
      'vod_pic'      : self._cover_pic(pic, vid),
      'vod_content'  : desc,
      'vod_play_from': 'Hanime1',
      'vod_play_url' : play_url,
    }
    return {'list': [vod]}
  def _extract_playlist(self, html, current_vid, current_title):
    episodes = []
    seen = set()
    playlist_html = ''
    for block_pat in [
      r'(?:id|class)="[^"]*(?:playlist|episodes?|series|related|同系列|選集)[^"]*"[^>]*>(.*?)(?=<(?:div|section|aside)[^>]+(?:id|class)="[^"]*(?:comment|footer|recommend|sidebar))',
      r'(?:playlist|episodes?|series)[^>]*>(.*?)(?=</(?:div|section|ul)>)',
    ]:
      bm = re.search(block_pat, html, re.S | re.I)
      if bm:
        playlist_html = bm.group(1)
        break
    if playlist_html:
      for m in re.finditer(r'href="[^"]*watch\?v=(\d+)"[^>]*>([^<]*)<', playlist_html):
        ep_vid  = m.group(1)
        ep_name = m.group(2).strip()
        if ep_vid not in seen and ep_name:
          seen.add(ep_vid)
          episodes.append({'name': ep_name, 'vid': ep_vid})
    if not episodes:
      ep_pattern = re.compile(
        r'href="https?://hanime1\.me/watch\?v=(\d+)"'
        r'.*?'
        r'class="card-mobile-title"[^>]*>\s*([^<]+?)\s*<',
        re.S
      )
      for m in ep_pattern.finditer(html):
        ep_vid  = m.group(1)
        ep_name = m.group(2).strip()
        if ep_vid not in seen and ep_name:
          seen.add(ep_vid)
          episodes.append({'name': ep_name, 'vid': ep_vid})
    if not episodes:
      for m in re.finditer(
        r'<a[^>]+href="[^"]*watch\?v=(\d+)"[^>]*>\s*([^<]{1,60}?)\s*</a>',
        html, re.S
      ):
        ep_vid  = m.group(1)
        ep_name = m.group(2).strip()
        if not ep_name or ep_name in ('', '\n'):
          continue
        if ep_vid not in seen:
          seen.add(ep_vid)
          episodes.append({'name': ep_name, 'vid': ep_vid})
    if not episodes:
      for m in re.finditer(
        r'data-(?:v|id|video-id)="(\d+)"[^>]*data-(?:title|name)="([^"]+)"',
        html
      ):
        ep_vid  = m.group(1)
        ep_name = m.group(2).strip()
        if ep_vid not in seen:
          seen.add(ep_vid)
          episodes.append({'name': ep_name, 'vid': ep_vid})
    if not episodes:
      return [{'name': current_title or current_vid, 'vid': current_vid}]
    if not any(e['vid'] == current_vid for e in episodes):
      episodes.insert(0, {'name': current_title or current_vid, 'vid': current_vid})
    def _ep_num(ep):
      m = re.search(r'(\d+)\s*$', ep['name'])
      return int(m.group(1)) if m else 0
    try:
      episodes.sort(key=_ep_num)
    except Exception:
      pass
    cur_idx = next((i for i, e in enumerate(episodes) if e['vid'] == current_vid), None)
    if cur_idx is not None and cur_idx != 0:
      cur_ep = episodes.pop(cur_idx)
      episodes.insert(0, cur_ep)
    return episodes
  def searchContent(self, key, quick, pg='1'):
    url = '{}/search?query={}&page={}'.format(
      self.host, urllib.parse.quote(key), pg)
    html = self._get(url)
    return {'list': self.parse_list(html), 'page': int(pg)}
  def playerContent(self, flag, id, vipFlags):
    vid = id.split('#')[0].strip()
    html = self._get('{}/watch?v={}'.format(self.host, vid))
    play = ''
    sources = re.findall(r'<source[^>]+src="([^"]+)"[^>]*size="(\d+)"', html)
    if sources:
      sources.sort(key=lambda x: int(x[1]), reverse=True)
      play = sources[0][0]
    if not play:
      m = re.search(r'"contentUrl"\s*:\s*"([^"]+)"', html)
      if m:
        play = m.group(1).replace('\\/', '/')
    if not play:
      m = re.search(r'(https?://[^\s\'"]+\.(?:m3u8|mp4)[^\s\'"]*)', html)
      if m:
        play = m.group(1)
    return {
      'parse': 0 if play else 1,
      'url'  : play or '{}/watch?v={}'.format(self.host, vid),
      'header': self.headers
    }
