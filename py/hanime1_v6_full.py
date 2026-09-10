# coding=utf-8
# hanime1.py —— TVBox / FongMi Python 爬虫
# 封面修复 v6：清理损坏的 JPEG EXIF，避免 Glide 方向解析越界；像素数据不重编码
import base64
import json
import hashlib
import uuid
import re
import sys
import urllib.parse
from html import unescape
from html.parser import HTMLParser

sys.path.append('..')
from base.spider import Spider


class _PageParser(HTMLParser):
    """只用标准库解析属性，兼容单引号、大小写及 HTML 实体。"""
    _void = set(('area', 'base', 'br', 'col', 'embed', 'hr', 'img',
                 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'))

    def __init__(self, text):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.root = {'tag': '', 'attrs': {}, 'children': [], 'parent': None}
        self.stack = [self.root]
        self.nodes = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'children': [],
                'parent': self.stack[-1]}
        self.stack[-1]['children'].append(node)
        self.nodes.append(node)
        if tag not in self._void:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self._void:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1]['children'].append(data)

    @staticmethod
    def walk(node):
        yield node
        for child in node['children']:
            if isinstance(child, dict):
                yield from _PageParser.walk(child)

    @staticmethod
    def text(node):
        if node['tag'] in ('script', 'style'):
            return ''
        return ''.join(_PageParser.text(c) if isinstance(c, dict) else c
                       for c in node['children']).strip()


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

    # ---------- 基础 ----------
    def getName(self):
        return 'hanime1-v6'

    def init(self, extend=''):
        # 默认 auto：有 getProxyUrl 的运行时用图片代理，否则带请求头直连。
        # 可通过 ext 对象 {"cover_mode": "direct"} 手动关闭代理。
        self.cover_mode = 'auto'
        try:
            options = json.loads(extend) if isinstance(extend, str) else extend
            if isinstance(options, dict) and options.get('cover_mode') == 'direct':
                self.cover_mode = 'direct'
        except (ValueError, TypeError):
            pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def _proxy_image_allowed(url):
        # 只代理本站及已知图片 CDN，防止变成任意地址/内网请求代理。
        try:
            parts = urllib.parse.urlsplit(url)
            return (parts.scheme == 'https' and parts.port in (None, 443)
                    and not parts.username and not parts.password
                    and parts.hostname in ('hanime1.me', 'www.hanime1.me',
                                           'vdownload.hembed.com', 'i.imgur.com'))
        except (ValueError, TypeError):
            return False

    def _client_pic(self, url, vid):
        if not url and not vid:
            return ''
        getter = getattr(self, 'getProxyUrl', None)
        if (getattr(self, 'cover_mode', 'auto') != 'direct' and callable(getter)
                and (not url or self._proxy_image_allowed(url))):
            try:
                proxy = getter()
                if isinstance(proxy, str) and proxy.startswith(('http://', 'https://')):
                    # Base64URL 避免嵌套 URL 的 &, +, ==, 逗号被二次拆分。
                    token = base64.urlsafe_b64encode(url.encode('utf-8')).decode('ascii').rstrip('=')
                    parts = urllib.parse.urlsplit(proxy)
                    params = dict(urllib.parse.parse_qsl(parts.query, keep_blank_values=True))
                    site_key = str(getattr(self, 'siteKey', '') or params.get('siteKey', '')).strip()
                    # 默影视无 siteKey 时按 recent 路由，搜索/浏览时可能指向别的源。
                    # 不猜站源 key，也不生成依赖 recent 的图片代理地址。
                    if site_key:
                        params.update({'type': 'cover', 'vid': str(vid), 'image': token,
                                       'cover_rev': '6', 'siteKey': site_key})
                        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path,
                                                       urllib.parse.urlencode(params), ''))
            except Exception:
                pass
        if not url:
            return ''
        return url + '@Referer=' + self.host + '/@User-Agent=' + self.headers['User-Agent']

    def _client_list(self, videos):
        # parse_list 始终保留源站 URL，仅在交给客户端时转换，避免代理套代理。
        return [dict(item, vod_pic=self._client_pic(item['vod_pic'], item['vod_id']))
                for item in videos]

    @staticmethod
    def _image_mime(data):
        # 不能仅判断 HTTP 200：CDN 可能返回 HTML 错误页。
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
        """检查 TIFF 字节序、magic 和第一 IFD 表边界（Glide 读取方向的位置）。"""
        tiff = payload[6:]
        if len(tiff) < 8 or tiff[:4] not in (b'II\x2a\x00', b'MM\x00\x2a'):
            return False
        order = 'little' if tiff[:2] == b'II' else 'big'
        offset = int.from_bytes(tiff[4:8], order)
        if offset < 8 or offset + 2 > len(tiff):
            return False
        count = int.from_bytes(tiff[offset:offset + 2], order)
        # 包含 tag count、每个 tag 的 12 字节及 next-IFD 的 4 字节。
        if offset + 2 + count * 12 + 4 > len(tiff):
            return False
        for index in range(count):
            entry = tiff[offset + 2 + index * 12:offset + 14 + index * 12]
            tag = int.from_bytes(entry[:2], order)
            if tag == 0x0112:  # Orientation
                kind = int.from_bytes(entry[2:4], order)
                components = int.from_bytes(entry[4:8], order)
                orientation = int.from_bytes(entry[8:10], order)
                if kind != 3 or components != 1 or not 1 <= orientation <= 8:
                    return False
        return True

    @classmethod
    def _sanitize_jpeg(cls, data):
        """只移除坏的 EXIF APP1；保留有效方向信息、ICC、XMP 和全部扫描数据。

        已确认本站部分图的 Exif\0\0 后缺少有效 TIFF 头，Glide 将后续
        字节当成负数 IFD 偏移并抛出 IndexOutOfBoundsException。
        此处按 JPEG 段长度解析，绝不全局替换 EXIF 字符串或重编码像素。
        """
        if not data.startswith(b'\xff\xd8'):
            return data
        pieces = [data[:2]]
        pos = 2
        changed = False
        while pos < len(data):
            start = pos
            if data[pos] != 0xff:
                return data  # 结构不明时保守保留，不猜扫描边界。
            while pos < len(data) and data[pos] == 0xff:
                pos += 1
            if pos >= len(data):
                return data
            marker = data[pos]
            pos += 1
            if marker in (0xda, 0xd9):  # SOS / EOI：从此原样保留，含多扫描 JPEG。
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

    def _prepare_cover(self, result):
        if not result:
            return result
        mime, data = result
        if mime == 'image/jpeg':
            data = self._sanitize_jpeg(data)
        return mime, data

    def _fetch_image(self, url, vid, trace=None):
        import requests
        def record(message):
            if trace is not None:
                trace.append(message)
        headers = dict(self.headers)
        headers['Referer'] = self.host + '/watch?v=' + str(vid)
        headers['Accept'] = 'image/webp,image/*;q=0.9,*/*;q=0.5'
        for _ in range(4):
            if not self._proxy_image_allowed(url):
                record('图片域名不在代理许可范围')
                return None
            # Imgur 的 removed.png 是“图片已删除”占位图，不当作成功封面。
            if urllib.parse.urlsplit(url).path.lower().endswith('/removed.png'):
                record('图片已被 Imgur 删除')
                return None
            try:
                with requests.get(url, headers=headers, timeout=(5, 10),
                                  allow_redirects=False, stream=True) as response:
                    record('图片 HTTP {} | {}'.format(response.status_code, urllib.parse.urlsplit(url).hostname))
                    if response.status_code in (301, 302, 303, 307, 308):
                        location = response.headers.get('Location')
                        if not location:
                            return None
                        url = urllib.parse.urljoin(url, location)
                        continue
                    if response.status_code != 200:
                        return None
                    chunks, size = [], 0
                    for chunk in response.iter_content(65536):
                        size += len(chunk)
                        if size > 5 * 1024 * 1024:
                            record('图片超过 5 MB 限制')
                            return None
                        chunks.append(chunk)
                    data = b''.join(chunks)
                    mime = self._image_mime(data)
                    record('图片格式 {} | {} 字节'.format(mime or '不是支持的图片/可能是错误页', len(data)))
                    return (mime, data) if mime else None
            except requests.RequestException as exc:
                # 只记录错误类型，不输出可能含 token 的完整 URL。
                record('图片请求异常：' + type(exc).__name__)
                return None
        return None

    def _detail_covers(self, html, vid):
        urls = []
        def add(value):
            url = self._image_url(value)
            if url and url not in urls:
                urls.append(url)
        for prop in ('og:image', 'og:image:secure_url', 'twitter:image'):
            add(self._meta(html, prop))
        for node in _PageParser(html).nodes:
            if node['tag'] == 'video':
                add(node['attrs'].get('poster'))
        for item in self.parse_list(html):
            if item['vod_id'] == str(vid):
                add(item['vod_pic'])
        return urls

    def localProxy(self, param):
        """FongMi/现代 Python 运行时：状态码、MIME、原始 bytes、响应头。"""
        if isinstance(param, str):
            try:
                param = json.loads(param)
            except ValueError:
                param = {}
        if not isinstance(param, dict) or param.get('type') != 'cover':
            return [400, 'text/plain', b'Unknown proxy request', {}]
        vid = str(param.get('vid', ''))
        token = param.get('image', '')
        if (not re.fullmatch(r'\d+', vid) or not isinstance(token, str)
                or len(token) > 16384 or not re.fullmatch(r'[A-Za-z0-9_-]*', token)):
            return [400, 'text/plain', b'Invalid cover request', {}]
        try:
            url = base64.urlsafe_b64decode(token + '=' * (-len(token) % 4)).decode('utf-8')
        except (ValueError, UnicodeError):
            return [400, 'text/plain', b'Invalid cover URL', {}]
        if url and not self._proxy_image_allowed(url):
            return [403, 'text/plain', b'Cover host not allowed', {}]
        result = self._fetch_image(url, vid) if url else None
        if not result:
            # 签名过期/图片失效时重新读取当前视频，不能猜文件名或删除 secure。
            try:
                html = self._get(self.host + '/watch?v=' + vid)
                for fresh in self._detail_covers(html, vid):
                    if fresh == url:
                        continue
                    result = self._fetch_image(fresh, vid)
                    if result:
                        break
            except Exception:
                result = None
        if not result:
            return [502, 'text/plain', b'Cover upstream unavailable',
                    {'Cache-Control': 'no-store'}]
        mime, data = self._prepare_cover(result)
        return [200, mime, data, {'Cache-Control': 'private, max-age=300'}]

    def _cover_diagnostic(self):
        """在用户设备上检查取图与真实本地 HTTP 路由，不把本机直调冒充客户端验证。"""
        import requests
        vid = '22737'
        key = str(getattr(self, 'siteKey', '') or '')
        report = ['脚本版本 v6 | 视频 ' + vid,
                  'siteKey：' + (key or '运行时未注入，将使用带请求头直链')]
        candidates = []
        self._last_cover_candidates = []
        self._last_cover_image = None
        try:
            response = requests.get(self.host + '/watch?v=' + vid,
                                    headers=self.headers, timeout=(5, 15))
            report.append('详情页面 HTTP ' + str(response.status_code))
            if response.status_code == 200:
                candidates = self._detail_covers(response.text, vid)
            report.append('解析到 {} 个当前视频封面地址'.format(len(candidates)))
        except requests.RequestException as exc:
            report.append('页面请求异常：' + type(exc).__name__)
        if candidates:
            # 先测与详情实际使用相同的图片，再测客户端会请求的本地 HTTP 地址。
            downloaded = self._fetch_image(candidates[0], vid, trace=report)
            if downloaded:
                prepared = self._prepare_cover(downloaded)
                removed = len(downloaded[1]) - len(prepared[1])
                report.append('EXIF 修复：移除 {} 字节损坏元数据；不重编码像素'.format(removed)
                              if removed else 'EXIF 检查：无需清理')
            self._last_cover_image = (candidates[0], downloaded)
            self._last_cover_candidates = candidates
            pic = self._client_pic(candidates[0], vid)
            parts = urllib.parse.urlsplit(pic)
            if dict(urllib.parse.parse_qsl(parts.query)).get('type') == 'cover':
                report.append('代理路由：siteKey 已绑定')
                try:
                    with requests.get(pic, timeout=(3, 30), stream=True) as response:
                        chunks, size = [], 0
                        for chunk in response.iter_content(65536):
                            size += len(chunk)
                            if size > 5 * 1024 * 1024:
                                raise ValueError('代理响应超过 5 MB')
                            chunks.append(chunk)
                        data = b''.join(chunks)
                        mime = self._image_mime(data)
                        report.append('本地代理 HTTP {} | {}'.format(response.status_code, mime or '非图片响应'))
                        if response.status_code == 200 and mime:
                            report.append('本地代理完整读取 {} 字节'.format(len(data)))
                            if downloaded:
                                same = hashlib.sha256(data).digest() == hashlib.sha256(self._prepare_cover(downloaded)[1]).digest()
                                report.append('修复后数据与代理返回：' + ('完全一致' if same else '不一致，需检查截断或 CDN 响应差异'))
                            report.append('HTTP 取图检查结束；实际能否显示请看 A～G 对照卡片')
                        else:
                            report.append('本地代理未返回图片：请反馈本页检测结果')
                except (requests.RequestException, ValueError) as exc:
                    report.append('本地代理异常：' + type(exc).__name__)
            else:
                report.append('使用直链模式；当前未进行本地代理检测')
        else:
            report.append('未解析到封面：请反馈上面的页面状态')
        self._last_cover_report = report
        return report

    def _display_test_cards(self):
        """仅检测分类下载并内嵌图片；正常首页/搜索不增加批量取图开销。"""
        cards = []
        nonce = uuid.uuid4().hex[:12]
        candidates = getattr(self, '_last_cover_candidates', [])[:2]
        saved = getattr(self, '_last_cover_image', None)
        for row, url in enumerate(candidates):
            result = saved[1] if saved and saved[0] == url else self._fetch_image(url, '22737')
            # fragment 不发送给 CDN，不改变 secure 参数；只使显示测试缓存键独立。
            parts = urllib.parse.urlsplit(url)
            direct = urllib.parse.urlunsplit(parts._replace(fragment='cover-test-' + nonce))
            direct += '@Referer=' + self.host + '/@User-Agent=' + self.headers['User-Agent']
            proxy = self._client_pic(url, '22737')
            params = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(proxy).query))
            if params.get('type') == 'cover':
                proxy += '&display_test=' + nonce
            else:
                proxy = ''
            result = self._prepare_cover(result)
            inline = ('data:' + result[0] + ';base64,' + base64.b64encode(result[1]).decode('ascii')) if result else ''
            for column, (label, pic) in enumerate((('原图直链', direct), ('修复代理', proxy), ('修复内嵌', inline))):
                letter = chr(ord('A') + row * 3 + column)
                cards.append({'vod_id': '__cover_diag__:' + letter,
                              'vod_name': letter + ' ' + label,
                              'vod_pic': pic,
                              'vod_remarks': ('封面 {} · {}'.format(row + 1, label) if pic else '未生成图片，请查看检测报告')})
        # 已知有效的绿色白勾 PNG，检查客户端内嵌图片通路，不依赖网络。
        cards.append({'vod_id': '__cover_diag__:G', 'vod_name': 'G PNG基准',
                      'vod_pic': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAACQCAIAAAB4aPl2AAACbUlEQVR4nO3dwW0bMRBA0XFaSbpKCnBHcQEuK8Xk4IsBQfu5JIcaEv+fDMEixAfZ2uUc9Pbz7++w5/149QuonkCQQJBAkECQQJBAkECQQJBAkECQQJBAkECQQJBAkECQQJBAkECQQJBAkECQQJBAkECQQJBAkECQQJBAkECQQJBAkECQQJBAkECQQJBAkECQQJBAkECQQJBAkEDQ4UD/3j8HVzgZ6Etn0OhYoO8uI0ZnAj2KdBsdCPTMos/oNKBrhQ6jo4Ba9n/X6Cigln59/Ln1++cAtbw17urEMUBJOnEGUJ5OHACUqhO7A2XrxNZA4zeiLe0K1Kgz+PaJTYGW6cSOQCt1YjugxTqxF9B6ndgI6CU6sQvQq3RiF6CWMnRiFlDqNduCy+WLJgBNGR5cL35dnk6MA80aHuDiz0rViUGgicODlsUfy9aJEaC5w4OORRboRDfQ9OHBxKfPrQcoY3hw94lr3j7RB9T44jqMqulE959YhlFBnRj5Jz3XqKZODH7MzzIqqxPjF4rjRpV1YsqtxohRcZ2YdbOa97nWvnhS0447OozqXC5fNPM86JbRFjoR8Tb9WxFm3ShU0ImME8UpGyuiE0lHroPbq6MTeWfSpTY5UuKhfZ9RNdncqcbd3VbTiQVjn/Y9F9SJNXOxx523PFKkRYPD7/v/+vnxkZqtm6w+c6msExlX0od1zmw+KYEggSCBIIEggSCBIIEggSCBIIEggSCBIIEggSCBIIEggSCBIIEggSCBIIEggSCBIIEggSCBIIEggSCBIIEggSCBIIEggSCBIIEggSCBIIEggSCBIIEggSCBIIGg/w3YwRW9kXx+AAAAAElFTkSuQmCC',
                      'vod_remarks': '正常应显示绿色白勾'})
        self._last_display_cards = cards
        return cards

    def _diagnostic_list(self):
        report = self._cover_diagnostic()
        cards = self._display_test_cards()
        report.extend(['显示对照说明：A/B/C 使用封面1，D/E/F 使用封面2（如有）。',
                       'A/D 为原始图片（坏 EXIF 未处理）；B/E 为修复代理；C/F 为修复后内嵌图片。',
                       'G 正常应为绿色白勾。请反馈 A～G 哪些真正显示图片。',
                       '下方文字报告卡片不放图片，显示彩色首字是正常的。'])
        self._last_cover_report = report
        cards.extend({'vod_id': '__cover_diag__:report' + str(i), 'vod_name': text,
                      'vod_pic': '', 'vod_remarks': '检测报告 · 点击查看完整结果'}
                     for i, text in enumerate(report))
        return {'list': cards, 'page': 1, 'pagecount': 1, 'limit': len(cards), 'total': len(cards)}

    def _get(self, url):
        try:
            return self.fetch(url, headers=self.headers, timeout=15).text
        except Exception:
            import requests
            return requests.get(url, headers=self.headers, timeout=15).text

    def _meta(self, html, prop):
        for node in _PageParser(html).nodes:
            attrs = node['attrs']
            if node['tag'] == 'meta' and (
                    (attrs.get('property') or '').lower() == prop.lower() or
                    (attrs.get('name') or '').lower() == prop.lower()):
                value = (attrs.get('content') or '').strip()
                if value:
                    return value
        return ''

    def _image_url(self, value):
        """补全地址；只过滤明确的占位图，不误伤 GIF 或带 icon 的 CDN 域名。"""
        value = unescape(value or '').strip().replace('\\/', '/')
        if not value or value.lower().startswith(('data:', 'blob:', 'javascript:')):
            return ''
        url = urllib.parse.urljoin(self.host + '/', value)
        parts = urllib.parse.urlsplit(url)
        if parts.scheme not in ('http', 'https') or not parts.netloc:
            return ''
        basename = urllib.parse.unquote(parts.path).rsplit('/', 1)[-1].lower()
        if re.search(r'^(?:placeholder|loading|loader|spacer|blank|transparent|'
                     r'pixel|no[-_]?image|default[-_]?image)(?:[._-]|$)', basename):
            return ''
        return url

    def _srcset_urls(self, value):
        # 按宽度/倍率从大到小选图；没有描述符时保留原顺序。
        candidates = []
        # 不能按任意逗号切分：部分图片 CDN 的路径本身带逗号。
        pattern = r'(\S+)(?:\s+(\d+(?:\.\d+)?)[wx])?\s*(?:,|$)'
        for m in re.finditer(pattern, value or ''):
            raw = m.group(1).rstrip(',')
            url = self._image_url(raw)
            if url:
                candidates.append((float(m.group(2) or 1), url))
        return [url for _, url in sorted(candidates, key=lambda x: x[0], reverse=True)]

    def _cover(self, node):
        nodes = list(_PageParser.walk(node))
        images = [n for n in nodes if n['tag'] in ('img', 'source')]
        # 懒加载真实地址优先于 src，避免取到 src 中的占位图。
        for n in images:
            attrs = n['attrs']
            role = '{} {}'.format(attrs.get('class') or '', attrs.get('id') or '')
            if re.search(r'(?:^|[\s_-])(?:avatar|icon|logo)(?:$|[\s_-])', role, re.I):
                continue
            for key in ('data-src', 'data-original', 'data-lazy-src', 'data-url',
                        'data-echo', 'data-lazy', 'data-original-src',
                        'data-srcset', 'data-lazy-srcset', 'srcset', 'src'):
                if 'srcset' in key:
                    urls = self._srcset_urls(attrs.get(key))
                    url = urls[0] if urls else ''
                else:
                    url = self._image_url(attrs.get(key))
                if url:
                    return url
        # 部分卡片使用内联背景图而不是 img。
        for n in nodes:
            attrs = n['attrs']
            for key in ('data-background', 'data-bg', 'data-background-image'):
                value = attrs.get(key) or ''
                if value and not value.strip().lower().startswith('url('):
                    url = self._image_url(value)
                    if url:
                        return url
            style = ' '.join(attrs.get(k) or '' for k in
                             ('style', 'data-background', 'data-bg', 'data-background-image'))
            m = re.search(r"url\(\s*(['\"]?)(.*?)\1\s*\)", style, re.I)
            if m:
                url = self._image_url(m.group(2))
                if url:
                    return url
        return ''

    def _watch_id(self, href):
        if not href:
            return ''
        parts = urllib.parse.urlsplit(urllib.parse.urljoin(self.host + '/', href))
        if parts.scheme not in ('http', 'https'):
            return ''
        if parts.hostname != urllib.parse.urlsplit(self.host).hostname:
            return ''
        if parts.path.rstrip('/') != '/watch':
            return ''
        vid = urllib.parse.parse_qs(parts.query).get('v', [''])[0]
        return vid if re.fullmatch(r'\d+', vid) else ''

    def _card_title(self, node):
        nodes = list(_PageParser.walk(node))
        for n in nodes:
            if re.search(r'(?:title|name)', n['attrs'].get('class') or '', re.I):
                title = _PageParser.text(n)
                if title:
                    return title
        for n in nodes:
            if n['tag'] == 'img' and n['attrs'].get('alt'):
                return n['attrs']['alt'].strip()
        for n in nodes:
            if n['attrs'].get('title'):
                return n['attrs']['title'].strip()
        return ''

    # ---------- 列表解析 ----------
    def parse_list(self, html):
        page = _PageParser(html)
        videos = {}
        for node in page.nodes:
            if node['tag'] != 'a':
                continue
            vid = self._watch_id(node['attrs'].get('href'))
            if not vid:
                continue
            item = videos.setdefault(vid, {
                'vod_id': vid, 'vod_name': '', 'vod_pic': '', 'vod_remarks': ''
            })
            title = self._card_title(node)
            pic = self._cover(node)
            # 图片可能在链接旁边。只查看近邻且包含同一视频的容器，
            # 避免从整个列表中误取另一部视频的图片。
            parent = node['parent']
            for _ in range(3):
                if (title and pic) or not parent or parent['tag'] in (
                        '', 'body', 'html', 'main', 'section', 'ul', 'ol'):
                    break
                ids = {self._watch_id(n['attrs'].get('href'))
                       for n in _PageParser.walk(parent) if n['tag'] == 'a'}
                ids.discard('')
                if ids != {vid}:
                    break
                title = title or self._card_title(parent)
                pic = pic or self._cover(parent)
                parent = parent['parent']
            title = title or _PageParser.text(node)
            # 先遇到标题链接时不再丢弃随后出现的封面链接。
            if title and not item['vod_name']:
                item['vod_name'] = title
            if pic and not item['vod_pic']:
                item['vod_pic'] = pic
        return [v for v in videos.values() if v['vod_name']]

    def _parse_list_fallback(self, html):
        # 兼容旧调用入口；兜底也使用统一的封面提取逻辑。
        return self.parse_list(html)

    # ---------- 首页 ----------
    def homeContent(self, filter):
        classes = [{'type_name': n, 'type_id': v} for n, v in self.cates]
        classes.append({'type_name': '封面修复 v6', 'type_id': '__cover_diag__'})
        filters = {}
        for _, v in self.cates:
            if not v.startswith('sort:') and not v.startswith('genre_sort:'):
                filters[v] = [{'key': 'sort', 'name': '排序', 'value': self.sorts}]
        return {'class': classes, 'filters': filters}

    def homeVideoContent(self):
        html = self._get(self.host)
        return {'list': self._client_list(self.parse_list(html)[:30])}

    # ---------- 分类 ----------
    def categoryContent(self, tid, pg, filter, extend):
        if tid == '__cover_diag__':
            return self._diagnostic_list()
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
            'list': self._client_list(videos),
            'page': int(pg),
            'pagecount': int(pg) + (1 if len(videos) >= 20 else 0),
            'limit': 30,
            'total': 999999
        }

    # ---------- 详情 ----------
    def detailContent(self, ids):
        vid = ids[0]
        if str(vid).startswith('__cover_diag__:'):
            report = getattr(self, '_last_cover_report', None) or self._cover_diagnostic()
            pic = next((c['vod_pic'] for c in getattr(self, '_last_display_cards', [])
                        if c['vod_id'] == vid), '')
            return {'list': [{'vod_id': vid, 'vod_name': '封面修复 v6 · 22737',
                              'vod_pic': pic, 'vod_content': '\n'.join(report),
                              'vod_play_from': '', 'vod_play_url': ''}]}
        html = self._get('{}/watch?v={}'.format(self.host, vid))

        title = self._meta(html, 'og:title')
        covers = self._detail_covers(html, vid)
        pic = self._client_pic(covers[0] if covers else '', vid)
        desc  = self._meta(html, 'og:description')

        episodes = self._extract_playlist(html, vid, title)

        # ✅ 修复：将集数名称中的 # 替换为全角 ＃，避免与分隔符冲突
        def safe_ep_name(name):
            return name.replace('#', '＃')

        play_url = '#'.join(
            '{}${}'.format(safe_ep_name(ep['name']), ep['vid'])
            for ep in episodes
        )

        vod = {
            'vod_id'       : vid,
            'vod_name'     : title,
            'vod_pic'      : pic,
            'vod_content'  : desc,
            'vod_play_from': 'Hanime1',
            'vod_play_url' : play_url,
        }
        return {'list': [vod]}

    def _extract_playlist(self, html, current_vid, current_title):
        """
        多策略提取播放列表，兼容 hanime1.me 各种页面结构
        """
        episodes = []
        seen = set()

        # ── 策略1：标准选集区块（playlist / related 区域内的 watch 链接）──
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

        # ── 策略2：原正则（card-mobile-panel 结构）──
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

        # ── 策略3：宽松匹配——找所有 watch?v=xxx 链接，取其最近的文本节点 ──
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

        # ── 策略4：最后兜底——用 data-v 或 data-id 属性 ──
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

        # ── 所有策略失败，返回当前集 ──
        if not episodes:
            return [{'name': current_title or current_vid, 'vid': current_vid}]

        # 确保当前集在列表里
        if not any(e['vid'] == current_vid for e in episodes):
            episodes.insert(0, {'name': current_title or current_vid, 'vid': current_vid})

        # 按集数数字升序排序
        def _ep_num(ep):
            m = re.search(r'(\d+)\s*$', ep['name'])
            return int(m.group(1)) if m else 0

        try:
            episodes.sort(key=_ep_num)
        except Exception:
            pass

        # 把当前集挪到最前面
        cur_idx = next((i for i, e in enumerate(episodes) if e['vid'] == current_vid), None)
        if cur_idx is not None and cur_idx != 0:
            cur_ep = episodes.pop(cur_idx)
            episodes.insert(0, cur_ep)

        return episodes

    # ---------- 搜索 ----------
    def searchContent(self, key, quick, pg='1'):
        url = '{}/search?query={}&page={}'.format(
            self.host, urllib.parse.quote(key), pg)
        html = self._get(url)
        return {'list': self._client_list(self.parse_list(html)), 'page': int(pg)}

    # ---------- 播放 ----------
    def playerContent(self, flag, id, vipFlags):
        # ✅ 修复：清洗 id，防止含有 # 残留导致 URL 构造错误
        vid = id.split('#')[0].strip()

        html = self._get('{}/watch?v={}'.format(self.host, vid))
        play = ''

        # 优先取最高清晰度的 <source>
        sources = re.findall(r'<source[^>]+src="([^"]+)"[^>]*size="(\d+)"', html)
        if sources:
            sources.sort(key=lambda x: int(x[1]), reverse=True)
            play = sources[0][0]

        # JSON-LD contentUrl
        if not play:
            m = re.search(r'"contentUrl"\s*:\s*"([^"]+)"', html)
            if m:
                play = m.group(1).replace('\\/', '/')

        # 裸链接
        if not play:
            m = re.search(r'(https?://[^\s\'"]+\.(?:m3u8|mp4)[^\s\'"]*)', html)
            if m:
                play = m.group(1)

        return {
            'parse': 0 if play else 1,
            'url'  : play or '{}/watch?v={}'.format(self.host, vid),
            'header': self.headers
        }