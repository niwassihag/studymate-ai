"""Build a small dependency-free Android WebView shell using the documented DEX format.
The application uses only public Android APIs. Testbook result capture uses HTTPS and the INTERNET permission.
"""
from pathlib import Path
import struct as S, hashlib, zlib, zipfile, io, base64, datetime, json
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import pkcs7

ROOT=Path(__file__).resolve().parent; OUT=ROOT/'dist'; WEB=ROOT
OUT.mkdir(exist_ok=True); (ROOT/'work').mkdir(exist_ok=True)
u16=lambda n:S.pack('<H',n&65535)
u32=lambda n:S.pack('<I',n&0xffffffff)
u64=lambda n:S.pack('<Q',n)
def ul(n):
 b=bytearray()
 while n>=128:b.append((n&127)|128);n>>=7
 b.append(n);return bytes(b)
def align(b):
 while len(b)%4:b.append(0)

ACT='Landroid/app/Activity;'; MAIN='Lcom/studymate/ai/MainActivity;'; CLIENT='Lcom/studymate/ai/LocalClient;'; CHROME='Lcom/studymate/ai/LocalChrome;'
WV='Landroid/webkit/WebView;'; WVC='Landroid/webkit/WebViewClient;'; WCC='Landroid/webkit/WebChromeClient;'; SET='Landroid/webkit/WebSettings;'; CB='Landroid/webkit/ValueCallback;'; FP='Landroid/webkit/WebChromeClient$FileChooserParams;'; JSRES='Landroid/webkit/JsPromptResult;'
STR='Ljava/lang/String;'; CTX='Landroid/content/Context;'; INTENT='Landroid/content/Intent;'; URI='Landroid/net/Uri;'; OBJ='Ljava/lang/Object;'; WIN='Landroid/view/Window;'; VIEW='Landroid/view/View;'; BUNDLE='Landroid/os/Bundle;'; EX='Ljava/lang/Exception;'; JSON='Lorg/json/JSONObject;'
types=set();strings=set();methods=set();fields=set();protos=set();definitions=[]
def typ(t):types.add(t);strings.add(t);return t
def method(c,n,r='V',p=()):
 p=tuple(p);typ(c);typ(r)
 for t in p:typ(t)
 short=r[0] if not r.startswith(('L','[')) else 'L'
 short+=''.join(t[0] if not t.startswith(('L','[')) else 'L' for t in p)
 strings.update([n,short]);protos.add((r,p));methods.add((c,n,r,p));return (c,n,r,p)
def field(c,n,t):typ(c);typ(t);strings.add(n);fields.add((c,n,t));return(c,n,t)
SYNC=field(MAIN,'syncResult',STR)
WEBFIELD=field(MAIN,'web',WV); PICK=field(MAIN,'chooser',CB); PENDING=field(MAIN,'pending',STR); HOST=field(CLIENT,'host',MAIN); HOSTC=field(CHROME,'host',MAIN)
class Code:
 def __init__(self,regs,ins):self.regs=regs;self.ins=ins;self.ops=[];self.tries=[];self.outs=0
 def raw(self,*w):self.ops.append(('raw',w));return self
 def label(self,s):self.ops.append(('label',s));return self
 def const(self,r,n):return self.raw(0x14|(r<<8),n&65535,(n>>16)&65535)
 def string(self,r,s):strings.add(s);self.ops.append(('string',r,s));return self
 def new(self,r,t):typ(t);self.ops.append(('new',r,t));return self
 def get(self,r,obj,f):self.ops.append(('field',0x54,r,obj,f));return self
 def put(self,r,obj,f):self.ops.append(('field',0x5b,r,obj,f));return self
 def call(self,kind,m,regs):self.outs=max(self.outs,len(regs));self.ops.append(('call',kind,m,regs));return self
 def result(self,r,obj=False):return self.raw((0x0c if obj else 0x0a)|(r<<8))
 def ret(self,r=None):return self.raw(0x0e if r is None else 0x0f|(r<<8))
 def branch(self,op,a,b,label):self.ops.append(('branch',op,a,b,label));return self
 def eqz(self,a,l):return self.branch(0x38,a,None,l)
 def nez(self,a,l):return self.branch(0x39,a,None,l)
 def eq(self,a,b,l):return self.branch(0x32,a,b,l)
 def ne(self,a,b,l):return self.branch(0x33,a,b,l)
 def jump(self,l):self.ops.append(('jump',l));return self
 def catch(self,start,end,handler):typ(EX);self.tries.append((start,end,handler));return self
def define(c,n,r,p,code,flags=1):definitions.append((method(c,n,r,p),flags,code))
def call(c,kind,owner,name,r,p,regs):return c.call(kind,method(owner,name,r,p),regs)
V='virtual';D='direct';STA='static';SUP='super';INTER='interface'
def ctor(owner,base,hostfield=None):
 c=Code(2 if hostfield else 1,2 if hostfield else 1);call(c,D,base,'<init>','V',(),[0]);
 if hostfield:c.put(1,0,hostfield)
 c.ret();define(owner,'<init>','V',(MAIN,) if hostfield else (),c,0x10001)
ctor(MAIN,ACT);ctor(CLIENT,WVC,HOST);ctor(CHROME,WCC,HOSTC)

c=Code(10,2);call(c,SUP,ACT,'onCreate','V',(BUNDLE,),[8,9]);c.new(0,WV);call(c,D,WV,'<init>','V',(CTX,),[0,8]);c.put(0,8,WEBFIELD)
call(c,V,WV,'getSettings',SET,(),[0]);c.result(1,True);c.const(2,1)
for name in ['setJavaScriptEnabled','setDomStorageEnabled']:call(c,V,SET,name,'V',('Z',),[1,2])
c.const(2,0)
for name in ['setAllowFileAccessFromFileURLs','setAllowUniversalAccessFromFileURLs']:call(c,V,SET,name,'V',('Z',),[1,2])
c.new(1,CLIENT);call(c,D,CLIENT,'<init>','V',(MAIN,),[1,8]);call(c,V,WV,'setWebViewClient','V',(WVC,),[0,1])
c.new(1,CHROME);call(c,D,CHROME,'<init>','V',(MAIN,),[1,8]);call(c,V,WV,'setWebChromeClient','V',(WCC,),[0,1]);call(c,V,ACT,'setContentView','V',(VIEW,),[8,0])
call(c,V,ACT,'getWindow',WIN,(),[8]);c.result(1,True);c.const(2,0xfffaf7f2);call(c,V,WIN,'setStatusBarColor','V',('I',),[1,2]);call(c,V,WIN,'setNavigationBarColor','V',('I',),[1,2]);call(c,V,WIN,'getDecorView',VIEW,(),[1]);c.result(3,True);c.const(2,0x2010);call(c,V,VIEW,'setSystemUiVisibility','V',('I',),[3,2]);c.const(2,16);call(c,V,WIN,'setSoftInputMode','V',('I',),[1,2]);c.string(1,'file:///android_asset/index.html');call(c,V,WV,'loadUrl','V',(STR,),[0,1]);c.ret();define(MAIN,'onCreate','V',(BUNDLE,),c,4)

c=Code(4,2);c.const(0,1);call(c,STA,'Landroid/widget/Toast;','makeText','Landroid/widget/Toast;',(CTX,'Ljava/lang/CharSequence;','I'),[2,3,0]);c.result(0,True);call(c,V,'Landroid/widget/Toast;','show','V',(),[0]);c.ret();define(MAIN,'notice','V',(STR,),c)

c=Code(8,2);c.label('try');c.new(0,JSON);call(c,D,JSON,'<init>','V',(STR,),[0,7]);c.string(1,'data');call(c,V,JSON,'getString',STR,(STR,),[0,1]);c.result(2,True);c.put(2,6,PENDING);c.string(1,'name');call(c,V,JSON,'getString',STR,(STR,),[0,1]);c.result(3,True);c.new(0,INTENT);c.string(1,'android.intent.action.CREATE_DOCUMENT');call(c,D,INTENT,'<init>','V',(STR,),[0,1]);c.string(1,'android.intent.category.OPENABLE');call(c,V,INTENT,'addCategory',INTENT,(STR,),[0,1]);c.string(1,'application/octet-stream');call(c,V,INTENT,'setType',INTENT,(STR,),[0,1]);c.string(1,'android.intent.extra.TITLE');call(c,V,INTENT,'putExtra',INTENT,(STR,STR),[0,1,3]);c.const(1,2);call(c,V,ACT,'startActivityForResult','V',(INTENT,'I'),[6,0,1]);c.label('end');c.ret();c.label('fail');c.raw(0x0d);c.const(0,0);c.put(0,6,PENDING);c.string(1,'Could not open the save dialog.');call(c,V,MAIN,'notice','V',(STR,),[6,1]);c.ret();c.catch('try','end','fail');define(MAIN,'exportFile','V',(STR,),c)

c=Code(12,4);call(c,SUP,ACT,'onActivityResult','V',('I','I',INTENT),[8,9,10,11]);c.const(0,1);c.ne(9,0,'export');c.get(0,8,PICK);c.eqz(0,'return');call(c,STA,FP,'parseResult','[Landroid/net/Uri;',('I',INTENT),[10,11]);c.result(1,True);call(c,INTER,CB,'onReceiveValue','V',(OBJ,),[0,1]);c.const(0,0);c.put(0,8,PICK);c.ret();c.label('export');c.const(0,2);c.ne(9,0,'return');c.const(0,-1);c.ne(10,0,'clear');c.eqz(11,'clear');c.get(3,8,PENDING);c.eqz(3,'clear');c.label('try');call(c,V,ACT,'getContentResolver','Landroid/content/ContentResolver;',(),[8]);c.result(0,True);call(c,V,INTENT,'getData',URI,(),[11]);c.result(1,True);c.eqz(1,'clear');call(c,V,'Landroid/content/ContentResolver;','openOutputStream','Ljava/io/OutputStream;',(URI,),[0,1]);c.result(2,True);c.eqz(2,'clear');c.const(5,0);call(c,STA,'Landroid/util/Base64;','decode','[B',(STR,'I'),[3,5]);c.result(4,True);call(c,V,'Ljava/io/OutputStream;','write','V',('[B',),[2,4]);call(c,V,'Ljava/io/OutputStream;','close','V',(),[2]);c.string(1,'File saved.');call(c,V,MAIN,'notice','V',(STR,),[8,1]);c.label('end');c.jump('clear');c.label('fail');c.raw(0x0d);c.string(1,'Could not save the file. Try another location.');call(c,V,MAIN,'notice','V',(STR,),[8,1]);c.label('clear');c.const(0,0);c.put(0,8,PENDING);c.label('return');c.ret();c.catch('try','end','fail');define(MAIN,'onActivityResult','V',('I','I',INTENT),c,4)

# Only Testbook HTTPS stays inside the app; other web links open externally.
c=Code(8,3);c.string(0,'https://testbook.com/studymate-return');call(c,V,STR,'equals','Z',(OBJ,),[0,7]);c.result(0);c.eqz(0,'check');c.string(0,'file:///android_asset/index.html');call(c,V,WV,'loadUrl','V',(STR,),[6,0]);c.const(0,1);c.ret(0);c.label('check')
for prefix in ['https://testbook.com/','https://www.testbook.com/']:
 c.string(0,prefix);call(c,V,STR,'startsWith','Z',(STR,),[7,0]);c.result(0);c.nez(0,'allow')
c.label('try');c.string(0,'https://');call(c,V,STR,'startsWith','Z',(STR,),[7,0]);c.result(0);c.nez(0,'open');c.string(0,'http://');call(c,V,STR,'startsWith','Z',(STR,),[7,0]);c.result(0);c.eqz(0,'return');c.label('open');call(c,STA,URI,'parse',URI,(STR,),[7]);c.result(1,True);c.new(0,INTENT);c.string(2,'android.intent.action.VIEW');call(c,D,INTENT,'<init>','V',(STR,URI),[0,2,1]);c.get(1,5,HOST);call(c,V,ACT,'startActivity','V',(INTENT,),[1,0]);c.label('end');c.jump('return');c.label('fail');c.raw(0x0d);c.label('return');c.const(0,1);c.ret(0);c.label('allow');c.const(0,0);c.ret(0);c.catch('try','end','fail');define(CLIENT,'shouldOverrideUrlLoading','Z',(WV,STR),c)

# A completed page gets a visible return button and a narrowly scoped DOM reader.
c=Code(8,3);c.string(0,'file:///android_asset/index.html');call(c,V,STR,'equals','Z',(OBJ,),[0,7]);c.result(0);c.eqz(0,'remote');c.get(1,5,HOST);c.get(2,1,SYNC);c.eqz(2,'done');call(c,STA,JSON,'quote',STR,(STR,),[2]);c.result(2,True);c.string(3,'window.receiveTestbook(JSON.parse(');call(c,V,STR,'concat',STR,(STR,),[3,2]);c.result(3,True);c.string(2,'));');call(c,V,STR,'concat',STR,(STR,),[3,2]);c.result(3,True);c.const(2,0);call(c,V,WV,'evaluateJavascript','V',(STR,CB),[6,3,2]);c.put(2,1,SYNC);c.ret();c.label('remote')
for prefix in ['https://testbook.com/','https://www.testbook.com/']:
 c.string(0,prefix);call(c,V,STR,'startsWith','Z',(STR,),[7,0]);c.result(0);c.nez(0,'inject')
c.jump('done');c.label('inject');c.string(1,(ROOT/'testbook-capture.js').read_text(encoding='utf-8'));c.const(2,0);call(c,V,WV,'evaluateJavascript','V',(STR,CB),[6,1,2]);c.label('done');c.ret();define(CLIENT,'onPageFinished','V',(WV,STR),c)

c=Code(4,1);c.get(0,3,WEBFIELD);call(c,V,WV,'getUrl',STR,(),[0]);c.result(1,True);c.string(2,'file:///android_asset/index.html');call(c,V,STR,'equals','Z',(OBJ,),[2,1]);c.result(1);c.nez(1,'exit');call(c,V,WV,'loadUrl','V',(STR,),[0,2]);c.ret();c.label('exit');call(c,SUP,ACT,'onBackPressed','V',(),[3]);c.ret();define(MAIN,'onBackPressed','V',(),c)

c=Code(9,4);c.get(0,5,HOSTC);c.get(1,0,PICK);c.eqz(1,'new');c.const(2,0);call(c,INTER,CB,'onReceiveValue','V',(OBJ,),[1,2]);c.label('new');c.put(7,0,PICK);c.label('try');call(c,V,FP,'createIntent',INTENT,(),[8]);c.result(1,True);c.const(2,1);call(c,V,ACT,'startActivityForResult','V',(INTENT,'I'),[0,1,2]);c.label('end');c.const(0,1);c.ret(0);c.label('fail');c.raw(0x0d|(1<<8));c.const(2,0);call(c,INTER,CB,'onReceiveValue','V',(OBJ,),[7,2]);c.put(2,0,PICK);c.string(1,'No file picker is available.');call(c,V,MAIN,'notice','V',(STR,),[0,1]);c.const(0,1);c.ret(0);c.catch('try','end','fail');define(CHROME,'onShowFileChooser','Z',(WV,CB,FP),c)

# Prompts carry results, never credentials; export bridge is local-origin only.
c=Code(10,6);c.string(0,'StudyMateSync');call(c,V,STR,'equals','Z',(OBJ,),[0,7]);c.result(0);c.eqz(0,'export');
for prefix in ['https://testbook.com/attempted/tests/','https://www.testbook.com/attempted/tests/']:
 c.string(0,prefix);call(c,V,STR,'startsWith','Z',(STR,),[6,0]);c.result(0);c.nez(0,'capture')
c.jump('other');c.label('capture');call(c,V,WV,'getUrl',STR,(),[5]);c.result(1,True);call(c,V,STR,'equals','Z',(OBJ,),[6,1]);c.result(0);c.eqz(0,'other');c.get(0,4,HOSTC);c.put(8,0,SYNC);call(c,V,JSRES,'confirm','V',(),[9]);c.string(1,'file:///android_asset/index.html');call(c,V,WV,'loadUrl','V',(STR,),[5,1]);c.const(0,1);c.ret(0);
c.label('export');c.string(0,'file:///android_asset/index.html');call(c,V,STR,'equals','Z',(OBJ,),[0,6]);c.result(0);c.eqz(0,'other');c.string(0,'StudyMateExport');call(c,V,STR,'equals','Z',(OBJ,),[0,7]);c.result(0);c.eqz(0,'other');call(c,V,JSRES,'confirm','V',(),[9]);c.get(0,4,HOSTC);call(c,V,MAIN,'exportFile','V',(STR,),[0,8]);c.const(0,1);c.ret(0);c.label('other');c.const(0,0);c.ret(0);define(CHROME,'onJsPrompt','Z',(WV,STR,STR,STR,JSRES),c)

classes=[(MAIN,ACT),(CLIENT,WVC),(CHROME,WCC)]
for a,b in classes:typ(a);typ(b)
ss=sorted(strings);si={s:i for i,s in enumerate(ss)};tt=sorted(types,key=si.get);ti={s:i for i,s in enumerate(tt)}
pp=sorted(protos,key=lambda p:(ti[p[0]],tuple(ti[x] for x in p[1])));pi={p:i for i,p in enumerate(pp)}
ff=sorted(fields,key=lambda f:(ti[f[0]],si[f[1]],ti[f[2]]));fi={f:i for i,f in enumerate(ff)}
mm=sorted(methods,key=lambda m:(ti[m[0]],si[m[1]],pi[(m[2],m[3])]));mi={m:i for i,m in enumerate(mm)}

def assemble(c):
 labels={};pc=0
 for op in c.ops:
  if op[0]=='label':labels[op[1]]=pc;continue
  pc+=len(op[1]) if op[0]=='raw' else 3 if op[0]=='call' else 2
 words=[]
 for op in c.ops:
  kind=op[0];pos=len(words)
  if kind=='label':continue
  if kind=='raw':words.extend(op[1])
  elif kind=='string':words.extend([0x1a|(op[1]<<8),si[op[2]]])
  elif kind=='new':words.extend([0x22|(op[1]<<8),ti[op[2]]])
  elif kind=='field':words.extend([op[1]|(op[2]<<8)|(op[3]<<12),fi[op[4]]])
  elif kind=='call':
   regs=op[3];assert len(regs)<=5 and all(0<=r<16 for r in regs)
   padded=regs+[0]*(5-len(regs));words.extend([{'virtual':0x6e,'super':0x6f,'direct':0x70,'static':0x71,'interface':0x72}[op[1]]|(len(regs)<<12)|(padded[4]<<8),mi[op[2]],sum(padded[i]<<(4*i) for i in range(4))])
  elif kind=='branch':
   delta=labels[op[4]]-pos;assert -32768<=delta<32768;words.extend([op[1]|(op[2]<<8)|((op[3] or 0)<<12),delta&65535])
  elif kind=='jump':words.extend([0x29,(labels[op[1]]-pos)&65535])
 assert len(words)==pc
 data=S.pack('<HHHHII',c.regs,c.ins,c.outs,len(c.tries),0,len(words))+b''.join(u16(w) for w in words)
 if c.tries:
  if len(words)%2:data+=b'\0\0'
  handlers=bytearray(ul(len(c.tries)));records=b''
  for start,end,handler in c.tries:
   records+=S.pack('<IHH',labels[start],labels[end]-labels[start],len(handlers));handlers+=b'\x01'+ul(ti[EX])+ul(labels[handler])
  data+=records+handlers
 return data

off=112;sections=[]
def reserve(kind,count,size):
 global off
 here=off;off+=count*size
 if count:sections.append((kind,count,here))
 return here
so=reserve(1,len(ss),4);to=reserve(2,len(tt),4);po=reserve(3,len(pp),12);fo=reserve(4,len(ff),8);mo=reserve(5,len(mm),8);co=reserve(6,len(classes),32);dataoff=off
buf=bytearray(off);str_offsets=[]
for s in ss:str_offsets.append(len(buf));b=s.encode('utf-8');buf+=ul(len(s))+b+b'\0'
sections.append((0x2002,len(ss),str_offsets[0]));align(buf)
params={};plist=[]
for r,p in pp:
 if p and p not in params:
  align(buf);params[p]=len(buf);plist.append(len(buf));buf+=u32(len(p))+b''.join(u16(ti[t]) for t in p)
if plist:sections.append((0x1001,len(plist),plist[0]))
codes={};codeoffs=[]
for m,flags,c in sorted(definitions,key=lambda d:mi[d[0]]):
 align(buf);codes[m]=len(buf);codeoffs.append(len(buf));buf+=assemble(c)
sections.append((0x2001,len(codeoffs),codeoffs[0]));classdata={}
for cls,base in classes:
 classdata[cls]=len(buf);fs=[f for f in ff if f[0]==cls];direct=[d for d in definitions if d[0][0]==cls and d[0][1]=='<init>'];virtual=[d for d in definitions if d[0][0]==cls and d[0][1]!='<init>'];buf+=ul(0)+ul(len(fs))+ul(len(direct))+ul(len(virtual));last=0
 for f in fs:buf+=ul(fi[f]-last)+ul(1);last=fi[f]
 for ds in [direct,virtual]:
  last=0
  for m,flags,c in sorted(ds,key=lambda d:mi[d[0]]):buf+=ul(mi[m]-last)+ul(flags)+ul(codes[m]);last=mi[m]
sections.append((0x2000,len(classes),min(classdata.values())));align(buf);mapoff=len(buf);sections+=[(0,1,0),(0x1000,1,mapoff)];sections.sort(key=lambda x:x[2]);buf+=u32(len(sections))+b''.join(S.pack('<HHII',k,0,n,o) for k,n,o in sections)
for i,x in enumerate(str_offsets):buf[so+i*4:so+i*4+4]=u32(x)
for i,t in enumerate(tt):buf[to+i*4:to+i*4+4]=u32(si[t])
for i,(r,p) in enumerate(pp):
 short=(r[0] if not r.startswith(('L','[')) else 'L')+''.join(t[0] if not t.startswith(('L','[')) else 'L' for t in p);buf[po+i*12:po+i*12+12]=S.pack('<III',si[short],ti[r],params.get(p,0))
for i,(cl,n,t) in enumerate(ff):buf[fo+i*8:fo+i*8+8]=S.pack('<HHI',ti[cl],ti[t],si[n])
for i,(cl,n,r,p) in enumerate(mm):buf[mo+i*8:mo+i*8+8]=S.pack('<HHI',ti[cl],pi[(r,p)],si[n])
for i,(cl,base) in enumerate(classes):buf[co+i*32:co+i*32+32]=S.pack('<IIIIIIII',ti[cl],1,ti[base],0,0xffffffff,0,classdata[cl],0)
buf[:8]=b'dex\n035\0';buf[32:112]=S.pack('<20I',len(buf),112,0x12345678,0,0,mapoff,len(ss),so,len(tt),to,len(pp),po,len(ff),fo,len(mm),mo,len(classes),co,len(buf)-dataoff,dataoff);buf[12:32]=hashlib.sha1(buf[32:]).digest();buf[8:12]=u32(zlib.adler32(buf[12:]));dex=bytes(buf)
(ROOT/'work/classes.dex').write_bytes(dex)

def chunk(t,h,p):return S.pack('<HHI',t,h,8+len(p))+p
def pool(strings):
 data=bytearray();offsets=[]
 for s in strings:offsets.append(len(data));enc=s.encode('utf-16le');data+=u16(len(enc)//2)+enc+b'\0\0'
 align(data);return chunk(1,28,S.pack('<IIIII',len(strings),0,0,28+4*len(strings),0)+b''.join(u32(x) for x in offsets)+data)

# Minimal binary resource table for a density-independent launcher icon.
globalpool=pool(['res/drawable/icon.png']);typepool=pool(['drawable']);keypool=pool(['icon'])
spec=chunk(0x202,16,S.pack('<BBHI',1,0,0,1)+u32(0))
config=u32(64)+b'\0'*60
restype=chunk(0x201,84,S.pack('<BBHII',1,0,0,1,88)+config+u32(0)+S.pack('<HHI',8,0,0)+S.pack('<HBBI',8,0,3,0))
pkgname='com.studymate.ai'.encode('utf-16le').ljust(256,b'\0')
package=chunk(0x200,288,u32(127)+pkgname+S.pack('<IIIII',288,1,288+len(typepool),1,0)+typepool+keypool+spec+restype)
resources=chunk(2,12,u32(1)+globalpool+package)

attrs={'theme':0x01010000,'label':0x01010001,'icon':0x01010002,'name':0x01010003,'exported':0x01010010,'minSdkVersion':0x0101020c,'versionCode':0x0101021b,'versionName':0x0101021c,'targetSdkVersion':0x01010270,'allowBackup':0x01010280}
xs=list(attrs)+['android','http://schemas.android.com/apk/res/android','manifest','package','com.studymate.ai','3.0','uses-sdk','uses-permission','android.permission.INTERNET','application','StudyMate AI','activity','com.studymate.ai.MainActivity','intent-filter','action','android.intent.action.MAIN','category','android.intent.category.LAUNCHER'];xi={s:i for i,s in enumerate(xs)};NS=xi['http://schemas.android.com/apk/res/android'];NO=0xffffffff
def node(t,body):return chunk(t,16,u32(1)+u32(NO)+body)
def attr(n,t,v,android=True):return S.pack('<IIIHBBI',NS if android else NO,xi[n],xi[v] if t==3 else NO,8,0,t,xi[v] if t==3 else v)
def start(n,a=()):return node(0x102,u32(NO)+u32(xi[n])+S.pack('<HHHHHH',20,20,len(a),0,0,0)+b''.join(a))
def end(n):return node(0x103,u32(NO)+u32(xi[n]))
xml=pool(xs)+chunk(0x180,8,b''.join(u32(v) for v in attrs.values()))+node(0x100,u32(xi['android'])+u32(NS))
xml+=start('manifest',[attr('versionCode',0x10,3),attr('versionName',3,'3.0'),attr('package',3,'com.studymate.ai',False)])
xml+=start('uses-sdk',[attr('minSdkVersion',0x10,23),attr('targetSdkVersion',0x10,32)])+end('uses-sdk')
xml+=start('uses-permission',[attr('name',3,'android.permission.INTERNET')])+end('uses-permission')
xml+=start('application',[attr('theme',1,0x01030241),attr('label',3,'StudyMate AI'),attr('icon',1,0x7f010000),attr('allowBackup',0x12,0)])
xml+=start('activity',[attr('name',3,'com.studymate.ai.MainActivity'),attr('exported',0x12,0xffffffff)])+start('intent-filter')+start('action',[attr('name',3,'android.intent.action.MAIN')])+end('action')+start('category',[attr('name',3,'android.intent.category.LAUNCHER')])+end('category')+end('intent-filter')+end('activity')+end('application')+end('manifest')+node(0x101,u32(xi['android'])+u32(NS))
manifest=chunk(3,8,xml)

# Local per-app signing identity; keep it for future updates, never embed the key.
keyfile=ROOT/'work/studymate-signing-key.pem';certfile=ROOT/'work/studymate-signing-cert.pem'
if keyfile.exists():key=serialization.load_pem_private_key(keyfile.read_bytes(),None);cert=x509.load_pem_x509_certificate(certfile.read_bytes())
else:
 key=rsa.generate_private_key(public_exponent=65537,key_size=2048);subject=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'StudyMate AI Personal Build')]);now=datetime.datetime.now(datetime.timezone.utc);cert=x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-datetime.timedelta(days=1)).not_valid_after(now+datetime.timedelta(days=365*30)).sign(key,hashes.SHA256());keyfile.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));certfile.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
files={'AndroidManifest.xml':manifest,'classes.dex':dex,'resources.arsc':resources,'res/drawable/icon.png':(WEB/'icon-192.png').read_bytes()}
for name in ['index.html','style.css','app.js','testbook-sync.js','planner.js','icon.svg','icon-192.png','icon-512.png','manifest.webmanifest']:files['assets/'+name]=(WEB/name).read_bytes()
def digest(b):return base64.b64encode(hashlib.sha256(b).digest()).decode()
mf=b'Manifest-Version: 1.0\r\nCreated-By: StudyMate AI\r\n\r\n';entries=[]
for name,data in files.items():
 block=f'Name: {name}\r\nSHA-256-Digest: {digest(data)}\r\n\r\n'.encode();entries.append((name,block));mf+=block
sf=f'Signature-Version: 1.0\r\nX-Android-APK-Signed: 2\r\nSHA-256-Digest-Manifest: {digest(mf)}\r\n\r\n'.encode()
for name,block in entries:sf+=f'Name: {name}\r\nSHA-256-Digest: {digest(block)}\r\n\r\n'.encode()
sig=pkcs7.PKCS7SignatureBuilder().set_data(sf).add_signer(cert,key,hashes.SHA256()).sign(serialization.Encoding.DER,[pkcs7.PKCS7Options.DetachedSignature,pkcs7.PKCS7Options.Binary])
files.update({'META-INF/MANIFEST.MF':mf,'META-INF/STUDYMAT.SF':sf,'META-INF/STUDYMAT.RSA':sig})
stream=io.BytesIO()
with zipfile.ZipFile(stream,'w') as z:
 for name,data in files.items():
  info=zipfile.ZipInfo(name,(2026,10,12,0,0,0));info.compress_type=zipfile.ZIP_STORED
  # Align uncompressed entries for Android resource loading.
  padding_len=(-(stream.tell()+30+len(name)))%4
  if padding_len:info.extra=S.pack('<HH',0xd935,padding_len)+b'\0'*padding_len
  z.writestr(info,data)
unsigned=stream.getvalue();eo=unsigned.rfind(b'PK\x05\x06');central=S.unpack_from('<I',unsigned,eo+16)[0]
# APK Signature Scheme v2: digest each section in 1 MiB chunks, then sign signed-data.
def content_digest(parts):
 chunks=[]
 for p in parts:
  for i in range(0,len(p),1048576):q=p[i:i+1048576];chunks.append(hashlib.sha256(b'\xa5'+u32(len(q))+q).digest())
 return hashlib.sha256(b'\x5a'+u32(len(chunks))+b''.join(chunks)).digest()
lp=lambda b:u32(len(b))+b
cd=content_digest([unsigned[:central],unsigned[central:eo],unsigned[eo:]])
signed=lp(lp(u32(0x0103)+lp(cd)))+lp(lp(cert.public_bytes(serialization.Encoding.DER)))+lp(b'')
signature=key.sign(signed,padding.PKCS1v15(),hashes.SHA256());public=key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
signer=lp(signed)+lp(lp(u32(0x0103)+lp(signature)))+lp(public);value=lp(lp(signer));pair=u64(4+len(value))+u32(0x7109871a)+value;size=len(pair)+24;block=u64(size)+pair+u64(size)+b'APK Sig Block 42';eocd=bytearray(unsigned[eo:]);S.pack_into('<I',eocd,16,central+len(block));apk=unsigned[:central]+block+unsigned[central:eo]+eocd
(OUT/'StudyMate-AI.apk').write_bytes(apk)
(ROOT/'work/android-build-details.json').write_text(json.dumps({'sha256':hashlib.sha256(apk).hexdigest(),'certificate_sha256':cert.fingerprint(hashes.SHA256()).hex(),'dex_bytes':len(dex),'classes':len(classes),'methods':len(definitions),'apk_bytes':len(apk),'min_sdk':23,'target_sdk':32},indent=2))
print('Built',OUT/'StudyMate-AI.apk',len(apk),'bytes')

