# coding=utf-8
# EXIF fix; no diagnostic UI.
_U='/search?'
_T='genre_sort:'
_S='vod_id'
_R='cover_mode'
_Q='Cosplay'
_P='Motion Anime'
_O='User-Agent'
_N='vid'
_M='class'
_L='http'
_K='name'
_J='direct'
_I='最新上市'
_H='/watch?v='
_G='vod_pic'
_F='https'
_E=True
_D='sort'
_C=False
_B=None
_A='/'
import base64,json,re,sys
from html import unescape
from urllib import parse as U
from lxml import etree
sys.path.append('..')
from base.spider import Spider
class Spider(Spider):
	host='https://hanime1.me';headers={_O:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36','Referer':host+_A,'Accept-Language':'zh-TW,zh;q=0.9,zh-CN;q=0.8'};cates=[('最新里番','genre_sort:裏番|最新上市'),(_I,'sort:最新上市'),('最新上传','sort:最新上傳'),('里番','裏番'),('泡面番','泡麵番'),(_P,_P),('3DCG','3DCG'),('2.5D','2.5D'),('2D动画','2D動畫'),('AI生成','AI生成'),('MMD','MMD'),(_Q,_Q),('新番预告','新番預告')];sorts=[dict(n=A,v=B)for(A,B)in((_I,_I),('最新上传','最新上傳'),('本日排行','本日排行'),('本周排行','本週排行'),('本月排行','本月排行'))]
	def getName(self):return'hanime1'
	def init(self,extend=''):
		A=extend;self.cover_mode='auto'
		try:
			B=json.loads(A)if isinstance(A,str)else A
			if isinstance(B,dict)and B.get(_R)==_J:self.cover_mode=_J
		except(ValueError,TypeError):0
	def isVideoFormat(self,url):0
	def manualVideoCheck(self):0
	def destroy(self):0
	def _get(self,url):
		try:return self.fetch(url,headers=self.headers,timeout=15).text
		except Exception:import requests as A;return A.get(url,headers=self.headers,timeout=15).text
	@staticmethod
	def _html(text):A=etree.HTML(text or'<html></html>');return A if A is not _B else etree.Element('html')
	def _meta(self,html,prop):
		for A in self._html(html).iter('meta'):
			if any((A.get(B)or'').lower()==prop.lower()for B in(_K,'property')):
				B=(A.get('content')or'').strip()
				if B:return B
		return''
	def _image_url(self,value):
		A=value;A=unescape(A or'').strip().replace('\\/',_A)
		if not A or A.lower().startswith(('data:','blob:','javascript:')):return''
		C=U.urljoin(self.host+_A,A);B=U.urlsplit(C);D=U.unquote(B.path).rsplit(_A,1)[-1].lower();E='^(?:placeholder|loading|loader|spacer|blank|transparent|pixel|no[-_]?image|default[-_]?image)(?:[._-]|$)';return C if B.scheme in(_L,_F)and B.netloc and not re.search(E,D)else''
	def _srcset_urls(self,value):
		A=[]
		for B in re.finditer('(\\S+)(?:\\s+(\\d+(?:\\.\\d+)?)[wx])?\\s*(?:,|$)',value or''):
			C=self._image_url(B[1].rstrip(','))
			if C:A.append((float(B[2]or 1),C))
		return[A for(B,A)in sorted(A,key=lambda x:x[0],reverse=_E)]
	def _cover(self,node):
		I='style';H='srcset';D=list(node.iter())
		for A in D:
			if A.tag not in('img','source'):continue
			if re.search('(?:^|[\\s_-])(?:avatar|icon|logo)(?:$|[\\s_-])',(A.get(_M)or'')+' '+(A.get('id')or''),re.I):continue
			for B in('data-src','data-original','data-lazy-src','data-url','data-echo','data-lazy','data-original-src','data-srcset','data-lazy-srcset',H,'src'):
				C=self._srcset_urls(A.get(B))if H in B else[self._image_url(A.get(B))]
				if C and C[0]:return C[0]
		for A in D:
			for B in('data-background','data-bg','data-background-image',I):
				E=A.get(B)or'';F=re.search('url\\(\\s*([\'\\"]?)(.*?)\\1\\s*\\)',E,re.I);G=self._image_url(F[2]if F else E if B!=I else'')
				if G:return G
		return''
	def _watch_id(self,href):
		A=U.urlsplit(U.urljoin(self.host+_A,href or''));B=U.parse_qs(A.query).get('v',[''])[0]
		if A.scheme in(_L,_F)and A.hostname==U.urlsplit(self.host).hostname and A.path.rstrip(_A)=='/watch':return B if re.fullmatch('\\d+',B)else''
		return''
	@staticmethod
	def _text(node):return''.join(node.xpath('.//text()[not(ancestor::script or ancestor::style)]')).strip()
	def _card_title(self,node):
		D='title';C='alt';B=list(node.iter())
		for A in B:
			if re.search('title|name',A.get(_M)or'',re.I)and self._text(A):return self._text(A)
		for A in B:
			if A.tag=='img'and A.get(C):return A.get(C).strip()
		return next((A.get(D).strip()for A in B if A.get(D)),'')
	def parse_list(self,html):
		I='href';G='vod_name';H={}
		for B in self._html(html).iter('a'):
			C=self._watch_id(B.get(I))
			if not C:continue
			D=H.setdefault(C,dict(vod_id=C,vod_name='',vod_pic='',vod_remarks=''));E,F=self._card_title(B),self._cover(B);A=B.getparent()
			for K in range(3):
				if E and F or A is _B or A.tag in('html','body','main','section','ul','ol'):break
				J={self._watch_id(A.get(I))for A in A.iter('a')}-{''}
				if J!={C}:break
				E,F=E or self._card_title(A),F or self._cover(A);A=A.getparent()
			D[G]=D[G]or E or self._text(B);D[_G]=D[_G]or F
		return[A for A in H.values()if A[G]]
	def _parse_list_fallback(self,html):return self.parse_list(html)
	@staticmethod
	def _proxy_image_allowed(url):
		try:A=U.urlsplit(url);return A.scheme==_F and A.port in(_B,443)and not A.username and not A.password and A.hostname in('hanime1.me','www.hanime1.me','vdownload.hembed.com','i.imgur.com')
		except(ValueError,TypeError):return _C
	def _client_pic(self,url,vid):
		F='siteKey';B=url;D=getattr(self,'getProxyUrl',_B)
		if getattr(self,_R,'auto')!=_J and callable(D)and(not B or self._proxy_image_allowed(B)):
			try:
				A=U.urlsplit(D());C=dict(U.parse_qsl(A.query,keep_blank_values=_E));E=str(getattr(self,F,'')or C.get(F,'')).strip()
				if E and A.scheme in(_L,_F)and A.netloc:G=base64.urlsafe_b64encode(B.encode()).decode().rstrip('=');C.update(type='cover',vid=str(vid),image=G,cover_rev='6',siteKey=E);return U.urlunsplit((A.scheme,A.netloc,A.path,U.urlencode(C),''))
			except Exception:0
		return B+'@Referer='+self.host+'/@User-Agent='+self.headers[_O]if B else''
	def _client_list(self,videos):return[dict(A,vod_pic=self._client_pic(A[_G],A[_S]))for A in videos]
	@staticmethod
	def _image_mime(data):
		B='gif';A=data
		for(C,D)in((b'\xff\xd8\xff','jpeg'),(b'\x89PNG\r\n\x1a\n','png'),(b'GIF87a',B),(b'GIF89a',B)):
			if A.startswith(C):return'image/'+D
		return'image/webp'if A[:4]==b'RIFF'and A[8:12]==b'WEBP'else''
	@staticmethod
	def _valid_exif_header(payload):
		A=payload[6:]
		if len(A)<8 or A[:4]not in(b'II*\x00',b'MM\x00*'):return _C
		G='little'if A[:2]==b'II'else'big';C=lambda b:int.from_bytes(b,G);B=C(A[4:8])
		if B<8 or B+2>len(A):return _C
		E=C(A[B:B+2])
		if B+2+E*12+4>len(A):return _C
		for F in range(E):
			D=A[B+2+F*12:B+14+F*12]
			if C(D[:2])==274 and(C(D[2:4])!=3 or C(D[4:8])!=1 or not 1<=C(D[8:10])<=8):return _C
		return _E
	@classmethod
	def _sanitize_jpeg(cls,data):
		A=data
		if not A.startswith(b'\xff\xd8'):return A
		E,B,G=[A[:2]],2,_C
		while B<len(A):
			F=B
			if A[B]!=255:return A
			while B<len(A)and A[B]==255:B+=1
			if B>=len(A):return A
			C,B=A[B],B+1
			if C in(218,217):return b''.join(E)+A[F:]if G else A
			if C in(216,1)or 208<=C<=215:E.append(A[F:B]);continue
			if C==0 or B+2>len(A):return A
			H=int.from_bytes(A[B:B+2],'big');D=B+H
			if H<2 or D>len(A):return A
			I=A[B+2:D]
			if C==225 and I.startswith(b'Exif\x00\x00')and not cls._valid_exif_header(I):G=_E
			else:E.append(A[F:D])
			B=D
		return A
	def _prepare_cover(self,result):A=result;return(A[0],self._sanitize_jpeg(A[1])if A[0]=='image/jpeg'else A[1])if A else A
	def _fetch_image(self,url,vid):
		I='Location';A=url;import requests as C;J=dict(self.headers,Referer=self.host+_H+str(vid),Accept='image/webp,image/*;q=0.9,*/*;q=0.5')
		for K in range(4):
			if not self._proxy_image_allowed(A)or U.urlsplit(A).path.lower().endswith('/removed.png'):return
			try:
				with C.get(A,headers=J,timeout=(5,10),allow_redirects=_C,stream=_E)as B:
					if B.status_code in(301,302,303,307,308):
						if not B.headers.get(I):return
						A=U.urljoin(A,B.headers[I]);continue
					if B.status_code!=200:return
					D,E=[],0
					for F in B.iter_content(65536):
						E+=len(F)
						if E>5242880:return
						D.append(F)
					G=b''.join(D);H=self._image_mime(G);return(H,G)if H else _B
			except C.RequestException:return
	def _detail_covers(self,html,vid):A=html;B=[self._meta(A,B)for B in('og:image','og:image:secure_url','twitter:image')];B+=[A.get('poster')for A in self._html(A).iter('video')];B+=[A[_G]for A in self.parse_list(A)if A[_S]==str(vid)];return list(dict.fromkeys(A for A in map(self._image_url,B)if A))
	def localProxy(self,param):
		J='Cache-Control';H='text/plain';F=param;G=[400,H,b'Invalid cover request',{}]
		try:
			E=json.loads(F)if isinstance(F,str)else F
			if not isinstance(E,dict)or E.get('type')!='cover':return G
			B,C=str(E.get(_N,'')),E.get('image','')
			if not re.fullmatch('\\d+',B)or not isinstance(C,str)or len(C)>16384 or not re.fullmatch('[A-Za-z0-9_-]*',C):return G
			D=base64.urlsafe_b64decode(C+'='*(-len(C)%4)).decode()
		except(ValueError,UnicodeError):return G
		if D and not self._proxy_image_allowed(D):return[403,H,b'Cover host not allowed',{}]
		A=self._fetch_image(D,B)if D else _B
		if not A:
			try:
				for I in self._detail_covers(self._get(self.host+_H+B),B):
					if I!=D:
						A=self._fetch_image(I,B)
						if A:break
			except Exception:A=_B
		if not A:return[502,H,b'Cover upstream unavailable',{J:'no-store'}]
		K,L=self._prepare_cover(A);return[200,K,L,{J:'private, max-age=300'}]
	def homeContent(self,filter):A={A:[dict(key=_D,name='排序',value=self.sorts)]for(B,A)in self.cates if not A.startswith(('sort:',_T))};return{_M:[dict(type_name=A,type_id=B)for(A,B)in self.cates],'filters':A}
	def homeVideoContent(self):return{'list':self._client_list(self.parse_list(self._get(self.host))[:30])}
	def categoryContent(self,tid,pg,filter,extend):
		F='genre';C=extend;B=tid;A={'page':str(pg)}
		if B.startswith(_T):D=B[11:].split('|',1);A[F],A[_D]=D[0],D[1]if len(D)>1 else''
		elif B.startswith('sort:'):A[_D]=B[5:]
		else:
			A[F]=B
			if C and C.get(_D):A[_D]=C[_D]
		E=self.parse_list(self._get(self.host+_U+U.urlencode(A)));return dict(list=self._client_list(E),page=int(pg),pagecount=int(pg)+(len(E)>=20),limit=30,total=999999)
	def detailContent(self,ids):A=ids[0];B=self._get(self.host+_H+str(A));C=self._meta(B,'og:title');D=self._detail_covers(B,A);E='#'.join(A[_K].replace('#','＃')+'$'+A[_N]for A in self._extract_playlist(B,A,C));return{'list':[dict(vod_id=A,vod_name=C,vod_pic=self._client_pic(D[0]if D else'',A),vod_content=self._meta(B,'og:description'),vod_play_from='Hanime1',vod_play_url=E)]}
	def _extract_playlist(self,html,current_vid,current_title):
		C=current_vid;B=html;G=''
		for I in('(?:id|class)="[^"]*(?:playlist|episodes?|series|related|同系列|選集)[^"]*"[^>]*>(.*?)(?=<(?:div|section|aside)[^>]+(?:id|class)="[^"]*(?:comment|footer|recommend|sidebar))','(?:playlist|episodes?|series)[^>]*>(.*?)(?=</(?:div|section|ul)>)'):
			H=re.search(I,B,re.S|re.I)
			if H:G=H[1];break
		J=[('href="[^"]*watch\\?v=(\\d+)"[^>]*>([^<]*)<',G),('href="https?://hanime1\\.me/watch\\?v=(\\d+)".*?class="card-mobile-title"[^>]*>\\s*([^<]+?)\\s*<',B),('<a[^>]+href="[^"]*watch\\?v=(\\d+)"[^>]*>\\s*([^<]{1,60}?)\\s*</a>',B),('data-(?:v|id|video-id)="(\\d+)"[^>]*data-(?:title|name)="([^"]+)"',B)];A,E=[],set()
		for(K,L)in J:
			for(F,D)in re.findall(K,L,re.S):
				D=D.strip()
				if D and F not in E:E.add(F);A.append(dict(vid=F,name=D))
			if A:break
		if C not in E:A.insert(0,dict(vid=C,name=current_title or C))
		def M(ep):A=re.search('(\\d+)\\s*$',ep[_K]);return int(A[1])if A else 0
		A.sort(key=M);N=next(A for(A,B)in enumerate(A)if B[_N]==C);A.insert(0,A.pop(N));return A
	def searchContent(self,key,quick,pg='1'):A=self._get(self.host+_U+U.urlencode(dict(query=key,page=pg)));return dict(list=self._client_list(self.parse_list(A)),page=int(pg))
	def playerContent(self,flag,id,vipFlags):
		F=id.split('#')[0].strip();D=self.host+_H+F;C,A=self._get(D),'';E=re.findall('<source[^>]+src="([^"]+)"[^>]*size="(\\d+)"',C)
		if E:A=max(E,key=lambda x:int(x[1]))[0]
		if not A:
			B=re.search('"contentUrl"\\s*:\\s*"([^"]+)"',C)
			if B:A=B[1].replace('\\/',_A)
		if not A:
			B=re.search('(https?://[^\\s\\\'\\"]+\\.(?:m3u8|mp4)[^\\s\\\'\\"]*)',C)
			if B:A=B[1]
		return dict(parse=0 if A else 1,url=A or D,header=self.headers)
