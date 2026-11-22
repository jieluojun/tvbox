# -*- coding: utf-8 -*-
"""Kishuto —— TVBox / 影视仓 多源聚合（精简稳定版）

默认源（2026-11-21 全源复测后调整，9 个）:
  影探 · 小山 · 咕噜 · 橘汁 · 四源4K · 河豚 · 片帝 · 未来4K · 找剧
  咕噜：T3 已恢复（菲乐4K 实测 3840×2160 可播），由「暂不启用」转正
  片帝：域名池+官方优先+中继（piandi4k/片帝4K2）
  河豚：完整 河豚4K2 专用实现（不再套四源引擎）

策略:
  - 真 4K 优先；直接剔除所有 2K 线路；假 4K 降级
  - 双规则保留：有 4K 时 1080 最多 1 条；无 4K 时 1080 放宽到 5 条
  - 1080 兜底对已暴露的 http 直链做可播/广告切片启发式预检
  - 集数按段对齐（避免全季合集误杀分季 4K）
  - 播放前抽样探测 m3u8/MKV/MP4 分辨率，假 4K 自动换源
  - 后台补线后按双规则重裁；有 4K 的缓存不被无 4K 结果覆盖
  - 搜索优先分季/BD/4K 条目

停用（实测整源不可用，类保留可派回）: FoFo(主站超时) · 枫奇(站点改版+安全验证)
已移除（整段代码删除，不再是候选源）:
  · 剧下饭 —— 官方 1.4.5 客户端硬编码 7 条静态 host、无备用域名下发；真实 IP
    194.147.100.71/.155 的 80/443/7744/6213/8080 全 TCP 超时、ICMP 100% 丢包，
    美国第三方节点对照 baidu/dongpian17 均 200 而 manian.* 超时，属上游停机。
    源码段（1437 行）整体删掉，见「十三次修订」
  · 小鸡 —— 1.0.8 客户端逆向确认：签名算法没变（现成的 SK/FINGER 打签名接口
    仍 200），但 decode/url 已改成会员门槛，3 部片 19 条线路 × 多枚新设备统一
    403「VIP权益已过期」(40302)；服务端 adConfig 自述变现方式 = 看广告换 8h VIP
    (reward_vip_seconds 28800) 或 50 次解码、卡密换 12h。没有免费播放端点，
    令牌是不可解密的密文。要靠改客户端修好只能伪造广告完成或逆令牌密钥 ——
    那是抹掉对方的广告/会员收入，不做。整段（938 行）删除，见「十五次修订」
（未来4K 已于 2026-11-21 晚复测后接回默认，原因见文末「十一次修订」）
分类/搜索按 tag 派发；详情跨源补线；播放按 id 回原源。

20261121 修订（安全 + 稳定性，调用的功能面不变）:
  - 自更新强制 sha256 与证书校验，删掉「版本号新就放行」的绕过；两套更新逻辑合一
  - 采集请求仍不校验证书（自签/IP 站太多），但凡把远端内容写进本地的链路必须校验
  - 首页缓存按 filter 分流，修掉 filter=False 命中 filter=True 缓存的串味
  - 搜索返回 pagecount=page+1（原为 page，壳永远翻不到第 2 页）；分类补 page/pagecount
  - categoryContent 支持 JSON 字符串形态的 extend，筛选条件不再静默失效
  - 线路去重签名加首集播放码，不再误删不同源的同名线路；真 4K 线路封顶 12 条
  - 画质分档：SD 只按独立词匹配（此前任何含 sd 字母的英文名都被打成低清）
  - 分辨率探测结果缓存 30 分钟，同集重播不再每次多付 1.5s
  - 源改为按需构造（默认只建 ORDER 内的源）；设备池落盘改到临时目录
  - 清掉死配置/死代码/重复 import（pyflakes 归零）

20261121 二次修订（全 14 源逐一实测后）:
  - 源集：咕噜转正（搜索 18/21/21 条、菲乐4K 直链实测 2160p）；剧下饭移出默认
    （8 个镜像 7 个无响应、1 个 502，搜索/分类全 0）
  - 「菲乐」解除名称拉黑：实测同一线路在不同片下指向不同 CDN —— sviptq 上是
    正常 3840×2160，djvod 上那批老地址 404。按名字封杀会连真 4K 一起丢，
    改为播放阶段「探测不到高度就换源」兜底
  - 播放阶段补一条兜底：宣称 4K 的线路若高度探测失败（404/超时），先同集换源，
    而不是把死链直接交给壳黑屏

20261121 三次修订（第三遍审计）:
  - 集数对齐扩成三档：剔 >2 倍合集、剔 <众数一半的番外/半截线，多出的尾巴按
    集序号截到众数（繁花 1 集番外、莲花楼 50 集花絮、沙丘2 3 集线均已修）
  - 4K 宣称判定改取「原始线路名 / 聚合展示名」中较高者，修掉未来4K(kl) 绕过兜底
  - 未来4K(wl) 移出默认：解析只回原网页、直链恒 403、片库小，类保留供旧播放码派回
    （此判定已于 2026-11-21 晚复测推翻并接回，见文末「十一次修订」）
  - 源由 10 个减到 9 个（默认只建 ORDER 内 9 个）

20261121 四次修订（小鸡逐项实测后）:
  - 小鸡(xj) 移出默认：站点/分类/搜索/详情全都正常，但 decode/url 恒返回
    403 {"msg":"VIP权益已过期","error_code":40302}，3 个域名一致、换设备号无效；
    8 条线路全是解不开的令牌（借四源4K的布布引擎只能救回 zijianm3u8 / PAN1 两类，
    余下回报 PLATFORM_NOT_ALLOWED / 令牌绑定别的采集接口 / 未知vodFrom）。
    聚合分类来自影探，小鸡的分类页本就没暴露 → 留在默认只剩不实 4K 标签 + 换源空转
  - 源由 9 个减到 8 个；LINE_FIRST 去掉「小鸡」（类与映射表保留，旧播放码仍可派回）

20261121 五次修订（末轮全面体检）:
  - **详情提速 3 倍**：影探(detailContent) 内部会再并一次 咕噜/橘汁/找剧，最长干等
    4s（DETAIL_BUDGET）；外层 _fill_start 本来就在并发问同一批源 —— 同一份活干两遍。
    改成只取影探自家线路（_base + _render，0.3~0.6s），跨源交外层：12 部片详情
    均值 3.1s → 0.97s、最慢 5.78s → 1.58s，线路数与可播率不变（86/86）
  - 集数跑偏判定补一条放宽规则：首屏线路少时众数只有 2 票，老逻辑直接放弃，
    用户会看到「26 集正片里混进 55 集合集」。现允许 2 票 + 倍差 ≥2 时剔合集，
    且只走「剔多」方向（众数必须是最小集数），不动「线偏短」那侧，避免误删真番外
  - _prewarm_srcs 的目标里去掉已停用的 xj

20261121 六次修订（教父系列线路复测后）:
  - 播放页识别从「只看 .html/.php 后缀」扩到「站点播放页 host 白名单」：
    优酷播放页是 v.youku.com/v_show/id_xxx（没有后缀），旧规则认不出来，parse=0
    的网页直接被壳当视频解 → 必黑屏。教父/教父3 的 YK超清、☆酷萌☆、优酷1080P
    共 8 条线路都是这个形态。现在先同集换源，全部线路都是网页才回落 parse=1
  - 播放前顺带识别响应类型（hls/dash/mp4/mkv/ts/html/json）：状态 200 但实际
    回播放页/JSON 的地址同样换源；408/425/429 是超时/限流不是死链，不误判
  - 多音轨电影跨线路换源：老片常被拆成「英语/国语/同声评论」三条线路，各源只有
    一条「正片」，按集名严格匹配永远换不到源（教父3 国语那条 djvod 地址 404）。
    整片只有一集的电影允许跨任意线路；≤6 集且集名带音轨词的允许取别家单集正片
  - 换源仍失败时回退本线路正片（同一部片，只是音轨不同），不再空手交黑屏
  - 死链换源预算 7.7s → 2.5s、兜底取流加 1.6s 超时：教父3 国语那条从 5.4s
    降到 1.1s；奥本海默 4 条同地址死链（djvod 全 404）不再空转十几秒

20261121 七次修订（全面体检）:
  - 搜索结果按相关性分层：原名一字不差 > 只差季数/标点 > 前缀 > 包含。
    实测搜「狂飙」，影探把「纳斯卡：全速狂飙 第一季」排在第一位，真正的
    《狂飙》在第 3 条，用户点第一条就进错片。同档内仍按源顺序（4K 源优先），
    不按源打散同名条目，源内顺序一律不动
  - 详情首屏：基础线路 < 3 条时补线预算 1.6s → 2.3s。三体第一季主源 0.2s
    就回来却只有 2 条线，其余源 1.6s 内赶不上，用户看到的线路表直接少一半；
    线路 ≥3 条的片（占绝大多数）仍是 1.6s 收工，实测详情均值 0.90s → 0.77s
  - 删死代码：best_match / sim / xf_http_text / jxf_reco（AST 全量扫零引用）
  - 已知上游缺陷（非代码可改）：影探「最新电影」分类的 area 字段大面积没标，
    选「欧美 / 英国 / 法国 / 日本」都返回 0 条，只有 大陆 / 香港 / 台湾 有数据；
    剧集分类（欧美剧）的 area 正常。这是源站数据缺口，不做「筛选无效就退回
    全量」的兜底 —— 那样用户选日本会看到一堆美剧，比空列表更误导

20261121 八次修订（播放等待时间复测后）:
  - 假 4K 换源补上预算：原来不传 budget 等于给满 PLAY_BUDGET(11s)，实测
    奥本海默一条假 4K 点下去要 13.5s 才有画面 → 收到 2.5s，实测 4.05s 出流
  - 取流失败/网页地址换源：left*0.7（实测 7.5s）→ 上限 3.0s。优酷播放页线路
    7.8s、河豚 QQ 预览页 8.3s → 3.2s / 4.0s（换不到源就直接 parse=1 交壳嗅探）
  - 收尾等待：原来会一直 join 到 PLAY_BUDGET(11s)，现在最多再等 2s。
    小山那批 4K 线要 17~20s 才回，等满也没用
  - 小山首播窗口 6.5s → 5.5s：实测「小山·1080P」最慢 4.87s 仍兜得住，
    而 4K 线 17~20s 等 6.5s 也等不来，纯白等 1s
  - 换源候选收紧两道：① 同一次换源里解析到同一地址的（不同线路常共用一条
    meilinvps 流）不再重试；② 候选先验活再交出去 —— 4K/2K 看高度探测顺手写下的
    状态码，其余走 8KB 轻量探测（带上子源给的 Referer/UA，免得 403 误杀），
    已知 4xx 或回网页/JSON 的直接跳过，不再把死链交给播放器黑屏
  - 同一地址 10 分钟内被 4xx 拒过的，不再花 1.6s 重探分辨率
  - parse=1 的地址不再探分辨率：那是解析接口（小山 4K 的 jx4k.api）不是媒体，
    探它只会白等 1.2s 拿回 0

  实测（8 部片 × 全部线路 × 首集，61 次）：最慢 13.58s → 7.27s，
  超 4s 的 8 条 → 7 条且量级降到 4~7s；正常出流的中位仍是 0.3~0.6s

20261121 九次修订（影探线路加载慢专项）:
  - 解析站「原样回吐」不再当成功：fys 对解析不了的地址会把入参原封不动还回来
    （实测 ym4kjx 那批 /d/ty/…/01_4K.mp4 GET 回来是
    {"code":1001,"msg":"解析失败","url":""}），旧代码只看「是不是 http」就认了，
    于是这张错误 JSON 页被当解析结果缓存 120s 交给壳 → 黑屏；聚合层还要先花
    0.3s 探测才发现它不是媒体。现在比 host+path 判同一资源，同等即判失败
  - 解析失败不再回落到 4K 解析页域：ym4kjx/hd4kjx 那批地址本身不是媒体文件，
    回落等于把错误页交出去。留空让聚合层立刻换源（真媒体直链仍回落）
  - 平台网页线（腾讯/爱奇艺/芒果/优酷/B站）的解析请求按 host 记 10 分钟失败：
    实测解析站对这些站 5/5 全空，每次点击白等 0.22s，抖动时还会把 timeout 拉满
  - 分辨率探测 Range 512KB → 64KB：实测 8KB 与 512KB 读到的分辨率完全一致
    （moov/EBML 头都在文件开头），云盘线上省 0.05~0.4s
  - 探空结果记 3 分钟（达标值仍记 10 分钟）：CDN 偶尔一次探不到就变成每集
    重探 0.3s；0 不参与假 4K 判定，缓存它只是少一次无用探测
  - 解析结果缓存 120s → 600s（影探解析出的是云盘直链，没有时效签名）
  - 新增连看预取：一集出流后，后台把同线路的下一集也解析好（只影探、只一集、
    失败静默），换集从 0.41~1.18s 收到稳定 0.20s

  实测（5 部片 × 影探全部线路 × 前 3 集，39 次点击）：中位 0.38s、均值 0.66s、
  最慢 3.28s（解析站自身抖动）；平台 1080P 线首集 0.22~0.36s、后续集 0.00s

20261121 十次修订（遗留缺陷收口 + 边界加固）:
  - 咕噜 429 不再静默变空列表：_search 成功后清空 last_error（旧值会一直污染
    上层判断），限流/网关类可恢复错误多给一次 0.45s 退避重试，全部失败时
    用 _error 把故障标记透传出去；分类/搜索不再让用户误以为「没有这部片」
  - 聚合层 categoryContent 收到 _error 空页 → 隔 0.4s 重问一次，交回壳前摘掉
    内部标记；正常空页不带标记，不白等
  - 搜索空结果区分故障与真空：有源报故障时只缓存 20s（旧逻辑按 600s 缓存，
    限流恢复后 10 分钟内重搜全是空），确实搜不到仍缓存 600s
  - 搜索缓存键在片名归一化为空时退回原文，避免「!」「?」等纯符号词互相串结果
  - 空关键词返回补齐 page/pagecount/limit/total，与正常返回同构
  - 片帝首播实测 4.64/5.24s 超出 PLAY_HEAD=4.5，PLAY_HEAD_SLOW 加 pd:5.5，
    不再因差 0.1~0.7s 误触发换源；复测 1.47/0.39/0.38s
  - 清掉零引用死代码：_wait_lines（已被 _wait_yield 取代）、_LAST_ERR（只写不读）、
    UA_ANDROID / EP_AAD（无引用常量）

  实测：打桩模拟 429「前两次失败第三次恢复」→ 3 次调用拿到数据、last_error 清空；
  模拟旧逻辑 → 空列表；全失败 → _error 透传；聚合层重试拿到数据且标记已摘除。
  8 源取流 7/7 出流；30 线程并发 2.01s / 0 错误 / 线程回落 1；gg 分类正常态
  0.15~0.97s（未触发重试），与修订前基线一致。

20261121 十一次修订（未来4K 复测后接回）:
  - wl(未来4K) 接回默认（8 源 → 9 源）。此前移出的依据是「解析只回原网页 /
    直链恒 403 / 片库小」，实测三项都不成立：解析传 kl- 原文 4/4 出真实流
    （只有传解码后的 v.qq.com 网页地址才会原样回吐）；返回的 defaultts m3u8
    清单 200、255 分片全 206 / video/MP2T、无 EXT-X-KEY；片库狂飙 7 / 三体 4 /
    教父 5 / 繁花 6 条。详情 0.10s、播放 0.11~0.20s，是当前最快的一档
  - 假 4K 修复：展示名「未来4K·kl」的前缀自带 4K，旧逻辑把它顶成 4K 档 ——
    既挤占真 4K 名额，又在播放时白付一次高度探测。新增 LABEL_NO_QUALITY
    白名单 + _qname()，分档（_line_tier）、排序（_r4）、画质宣称
    （claim_name / 候选预检）统一先剥掉这层非画质前缀再判 → kl 归 1080 档
  - 「四源4K」刻意不进白名单：它的线路名常不带 4K（华谊·Z蓝光 / 华谊·B超高清），
    剥掉会把 3 条实测真 4K 线误降成 1080 档（已实测确认）

20261121 十三次修订（移除剧下饭源）:
  - 用户决定整源移除，不再保留「待上游恢复再加回」的空桩。删掉 1437 行：
    剧下饭 4K 段全部（jxf_* 的域名竞速与熔断、AES-256-ECB 签名、classifies /
    search / videoDetails / analysisUrl 路由、片帝·与 4KK· 两条附属线路）
    以及 JuxiafanSpider 类；LABELS / MAKERS 里的 'jx' 条目一并删除，
    模块内已无 jxf_ 前缀符号（AST 零残留）。
  - 移除依据见「十二次修订」：官方客户端 7 条静态 host 全不可达、无备用域名下发，
    真实 IP 五端口全 TCP 超时 + ICMP 全丢包，美国第三方节点对照 baidu/dongpian17
    均 200 —— 上游停机，代码侧无解。
  - 影响面（已实测）：LABELS / MAKERS 由 14 条降为 13 条，ORDER 仍 9 源不变，首页/分类/搜索/详情
    的源数与耗时不变；旧缓存里的 'jx|…' 分类页会按「tag 不在 ORDER」回落影探，
    'jx|…' 详情与播放码走空源分支（详情返回空列表、播放转跨源换源），不抛异常；
    陈旧缓存最长 10 分钟自然过期。

20261121 十四次修订（搜索覆盖 + 上游 null 风暴自适应）:
  - 搜索早停补第三条门槛 SEARCH_ENOUGH=36：实测搜「漫长的季节」0.47s 就凑够 6 源
    收工、只出 24 条 —— 影探/橘汁/四源4K 三条还在路上的结果被直接丢掉，而同批源
    搜别的片各给 12 条。现在要「源够 + 慢源已回 + 结果 ≥36 条」同时成立才早停，
    冷门词多等一会儿（仍受 SEARCH_SLOW_WAIT=1.6s 软上限约束，最坏不比原来慢），
    热门词行为不变（狂飙 100+ 条、庆余年 60 条本来就过线）；全空（0 条）例外 ——
    所有应答的源都说没有时再等也不会有，拼错的词不多等
    打桩实测（同延迟/同条数、只换代码）：6 源快 ×3 条 + 3 源 1.2s ×12 条的场景
    由 0.21s/18 条/6 源 变成 1.21s/54 条/9 源；全快与热门场景两版完全一致
    真网 7 词：漫长的季节 24→28~36 条、源数 6→7，狂飙/繁花/庆余年/三体/海贼王/教父
    条数与耗时都在原有抖动区间内
  - 未来4K(wl) 的 _j 重写：把「上游明确回空 list」与「回 null/超时」彻底分开。
    实测限流时上游回 HTTP 200 + 4 字节 `null`、0.07s 就回，旧实现每次仍 sleep 0.5
    再要一遍 → 每次调用白付 0.6s；而 wl 在 SEARCH_SLOW 里，这 0.6s 会拖慢每一次
    搜索的首屏。现在 null 第一次重试一次（0.45s），已失败过就只探一次，连续 2 次
    进 12s 静默窗口（窗口内一次请求都不发），真正的「没有这部片」不重试、不静默、
    不算故障。实测：null 风暴下第 1 次 0.55s、第 2 次 0.07s，之后 12s 内 0.000s；
    限流恢复后窗口一过立刻自愈
  - 报 _error 的源不再算「已到齐」：搜索缓存 TTL 由 600s 降为 60s，一次上游抽风
    不会再把「这个源缺席」冻结 10 分钟（与片帝那次同类的问题）
  - PLAY_SPEED 补 wl=5：实测 0.11~0.61s 出流，换源时紧跟四源4K 之后试
  - 清死配置：CARD_PRI（搜索早已改成按相关性分层排序，这张表零引用）；
    修正 Spider docstring 的源列表（还写着已停用/已移除的源）、PLAY_TRY 注释 4→5

20261121 十五次修订（移除小鸡源）:
  - 用户提供官方 1.0.8 客户端（com.xmoebr.bdx，versionCode 108）问能否修复。
    逆向结论：签名层没坏，坏的是服务端的播放权限。
    · Hermes bundle（v96，5.8MB）里 42 条 /api.php/app/* 路由，没有任何免费播放
      端点；decode/playback 各种方法与参数组合一律 404
    · 用源里现成的 SK/FINGER（来自 TV 版 1.0.5）打 /index/home、/search/index、
      /detail 全部 200 —— 说明 1.0.8 没改签名算法，无需重新逆向
    · decode/url 对 繁花/狂飙/庆余年 共 19 条线路、多枚全新 UUID 设备统一返回
      403 {"msg":"VIP权益已过期","error_code":40302}，无线路例外
    · /index/home 下发的 adConfig 自述变现：reward_vip_seconds=28800（看一次广告
      8 小时 VIP）、decode_quota_reward={count:50}（看广告 50 次解码）、
      reward_cdk_seconds=43200（卡密 12 小时）、check_in 只给鸡蛋、splash 开屏
    · 播放令牌是不透明密文（rrsp-+64 字节 / qqqq-+hex / tmdb- / PAN1- / NBY- /
      zijia / zy108），客户端无解密字段；SK 也不在 .so 明文里（np 壳处理过）
    · check-in 被「无法确认稳定设备身份」挡住（服务端按设备历史判，补
      x-device-brand/model/android-id 均无效）；账号侧认 ?token=（假 token 回
      「认证失败，请重新登录」而不是「缺少认证信息」），但有无 token 都改变不了
      decode 的 403 → 只有伪造广告完成或逆令牌密钥能"修"，两条都不做
  - 处置：整段 938 行删除（xj 模块头 → XiaojiSpider 类 + sbox/AES 工具 + 设备池
    + 熔断），LABELS / MAKERS 的 'xj' 条目删除，REAL4K / FAKE2K 里的「小鸡·…」
    线路名一并清掉（源已不存在，留着是死名字）
  - 连带修复：`_tempfile` 是当年 xj 段里 `import tempfile as _tempfile` 顺带
    提供的全局别名，找剧设备号那行（kish_jz_udid.txt）在用它 —— 已改为直接引用
    模块顶部就有的 `tempfile`，避免删段后 NameError
  - 影响面：LABELS / MAKERS 各由 13 条降为 12 条（ff/fq 仍留、不在 ORDER），ORDER 仍 9 源；
    旧缓存里的 'xj|…' 分类回落影探、
    详情回空列表、播放走跨源换源，均不抛异常

20261121 十六次修订（四源4K 画质降级）:
  - 现象：四源4K 的 11~12 条线路全挂着 4K 名字，点开画质明显偏低。
  - 实测（ffprobe，繁花 / 狂飙 两片一致）：
      天堂·超级无敌4k   1280x720      （苹果复用同一条流）
      天堂·高清4k       1280x720
      天堂·真蓝光4K     1920x1080
      布布·PAN1 / BBA   1920x1080     （与「华谊·蓝光4K」「苹果·真蓝光4K」同流）
      布布·NBY / qsvip  外部解析流，常 4xx
    全源没有一条 3840x2160 —— 名字里的 4K 只是营销词。
  - 处置 1：新增 sk4_MEASURED / sk4_measure / sk4_qname / sk4_hd_only，按实测
    宽度分档；720 档的「超级无敌4k / 高清4k」不再进线路表（本源定位是 4K 专线，
    1280 宽冒充 4K 点开就是降级），带 4K 字样但实测非 4K 的线标一句「[非4K]」。
    （初版标的是「[实测1080P]」，后续复测发现同名线路在不同片/集会 720/1080
    波动 —— PAN1 两次分别读到 1080 与 720 —— 写死高度会造出新的假标签，改成只否定 4K。）
  - 处置 2：_line_tier 对四源名字走实测表 → 归 1080 档，不再占 MAX_4K=12 的
    真 4K 名额；_play_one / _play_other 的 claim 也用实测值，跳过注定读不到
    高度的探测（它给的是纯媒体清单，没有 RESOLUTION），也不会把本源最好的
    1080 线误判成假 4K 再换到更差的线路。
  - 处置 3：修 MP4 高度探测两个 bug —— 旧代码把 ftyp 的 compatible brand
    「avc1」(isom iso2 avc1 mp41) 当成样本条目，四源那批 MP4 一律读成 0；
    且 width/height 偏移少算 4 字节（type+24 → 应为 type+28/30）。stsd 落在
    64KB 之外时退到 tkhd 的 16.16 定点宽高（moov 2.3MB 也能读）。
    实测「天堂·高清4k」由 0 → 720，影探联通云仍 2160，能力没有退化。
  - 结果：繁花 11 条 → 6 条、狂飙 12 条 → 6 条，带 4K 的假线全部标「[非4K]」；
    聚合层按源折叠后每片保留 1 条四源线，播放 0.4~2.5s 出流。

20261121 十七次修订（首屏 / 搜索 / 详情提速，主要针对影探）:
  - 首页（影探4K nav + index_video）：原来先等 nav 回来、发现没有推荐位，
    再串行等 index_video（实测站点 0.5~2.1s），首屏 2.2s 里一半是纯等待。
    改为两条接口并发 + index_video 短超时（1.2s，超时先出分类）、cms() 支持
    独立 timeout/ttl；Spider.init 的后台预热顺带把 nav / index_video 取好落缓存。
    实测：壳并发首屏 2.22s → 0.75s，第二次进首页 0.00s。
  - homeVideoContent 直接走影探 home_vod（推荐位不需要分类），不再绕
    homeContent + "影探空→咕噜"回退；实测 0.71s → 0.26s。
  - 详情：1080 兜底预检先按源折叠，名额没占满就跳过预检（不改结果，只是
    省掉 1.0s 的启发式探测）；预检预算 1.0→0.6s、每条 0.9→0.5s。
  - 搜索：只剩 ≤2 个慢源且结果 ≥60 条时立即收工（原来死等 SEARCH_SLOW_WAIT
    1.6s，橘汁冷启动 1.9s 常赶不上，它那 20+ 条与影探/小山/河豚高度重叠）。
    实测：繁花 1.67→1.12s（78 条不变）、庆余年 1.13→1.08s（60 条）、
    狂飙 1.69→1.39s；冷门词（漫长的季节）仍按软上限等，结果量不受影响。
    ※ 这条没有把片帝排除在「可放弃的慢源」之外，是把片帝整源丢掉的主因，
      见「十八次修订」。

20261121 十八次修订（搜索结果丢失片帝）:
  - 现象：搜索列表时有时无「片帝」整源，同一关键词两次搜出的源数都不一样。
  - 定位（工具化）：给每个源的 searchContent 打桩记时刻，12 个关键词各搜一轮
    → pd 缺失 3/12；缺失轮次里 pd 线程在 1.62s（SEARCH_SLOW_WAIT 软上限）
    仍未返回，被直接收工丢掉；「≥60 条就收工」那条早停同样不看 pd 是否回来。
  - 根因：片帝搜索是**串行**试 30 个镜像域名，单域名实测 p50 1.13s、
    p90 3.71s、最坏 4.56s（20 轮，同一关键词），聚合侧 1.6~2.0s 就收工，
    所以「搜繁花有片帝、搜琅琊榜没有」。
  - 处置 1：PDSpider 抽出 _hit（单域名签名请求）+ _race（并发打 n 个域名，
    取最先成功的响应，默认 4 个 / 2.0s 上限）。单源 20 轮：p50 1.13→0.74s、
    p90 3.71→1.23s、max 4.56→1.29s，20/20 都拿到 20 条。
  - 处置 2：新增 SEARCH_MUST=('pd',)。片帝未回来时，两条「差不多就收」的
    早停（结果够多 / 软上限到点）一律不生效，并把 deadline 顺延
    SEARCH_MUST_EXTRA=0.7s（2.0+0.7=2.7s，覆盖 _race 自己 2.25s 的硬顶）。
    实测打桩：pd 固定耗时 1.5/2.2/2.5s 都出卡，2.9s（超出硬顶）才放弃。
    只有片帝慢的轮次付这 0.7s，其余源仍按 1.6s 软上限收工。
  - 处置 3：缺片帝的搜索结果缓存从 60s 压到 SEARCH_MUST_TTL=20s —— 它真赶不上
    时，用户 20s 后重搜就能补到，而不是被残缺缓存锁一分钟。
  - 处置 4：详情页也保底。有真 4K 时 1080 兜底只有 MAX_1080_WHEN_HAS_4K=3 条，
    片帝线路名多是「腾讯视频 / 哔哩哔哩 / 1080P-官方R」这类不带画质的平台名，
    按名称/可播预检总被小山、河豚、橘汁挤掉 —— 实测繁花详情 10 条线路 0 条片帝，
    但补线线程 box 里明明有 pd。_trim_lines 现在给片帝保底 1 条。
  - 结果：12 词 × 4 轮，片帝出卡 48/48（中间有一轮 5 个词同时缺片帝，同一时刻
    单源直连 4 个域名全部超时，是片帝侧整体不可达，不是聚合逻辑）；搜索平均
    1.36~1.54s（改前 1.48~1.54s）；繁花详情补齐后含「片帝·腾讯视频」，
    播放 2.59s 出流。

20261121 十九次修订（线路高度缓存跨片污染 + 探测三档 + 缓存有界淘汰）:
  - 现象：部分 4K 线路点开画质偏低，且「有时换源、有时不换」，同一部片重进
    结果还不一样。
  - 定位（工具化）：繁花 / 狂飙各取 5 条线路，先 playerContent 换成真链，
    再按 16K/32K/64K 截断解析。两个发现：
    ① 同一个线路名在不同片上指向完全不同的文件 —— 「影探·天翼云·4K」狂飙是
       2160 的 MKV、繁花是一条读不出高度的 MP4；「影探·联通云·4K」正好反过来；
    ② MP4 云盘线 7/10 条连 64KB 都读不出高度（moov 在尾部 / 302 到分片）。
  - 根因：_line_height 的缓存 key 只取线路名（`key = str(name)`），2160 会跨片
    复用 → 一条 1080 的片子借到别人的 2160 缓存值，kish_is_fake_claim 判不出来，
    该换源的不换。这是十六次修订「四源画质降级」没堵住的最后一条漏路。
  - 处置 1：key 改成「线路名 + sha1(源标记|片 id)[:12]」。带片才不会跨片借用；
    带摘要是因为影探的片 id 本身就是 200+ 字符带直链信息的 base64，原样进 key
    既占内存又把直链碎片留在长驻字典里。换集 URL 不同仍复用（这正是原意）。
  - 处置 2：探测结果分三档 real / low / unknown，各自 TTL ——
    实测够 600s、实测不够 120s、探不到 60s。原来低值「永不缓存」等于每集重探
    1.2s，探空记 180s 等于一条降级线三分钟不校验。unknown 既不当真 4K 也不当
    假 4K：实测 7/10 条 MP4 探不到高度，当假会误杀真线，当真等于没校验。
  - 处置 3：_play_other 换源前先读缓存，同一片同一线路已实测 low 的直接跳过，
    不再花一次解析 + 1.2s 重探。
  - 处置 4：裸 clear() 全部换成 _cap_put 有界淘汰（按插入顺序丢最老的一批）：
    _CACHE / _SRCH_MEMO / _DETAIL_MEMO / _TITLE_MEMO / XF_CACHE /
    _KISH_H_CACHE / _KISH_ST_CACHE / _KISH_KIND_CACHE / 子源 _det / _cat /
    _PARSE_FAIL / _PREFETCHED。原写法在容量到顶时整表清空，刚探好的线路、
    刚拼好的换源表一起没了（表现为「换源突然失效」「线路又变回没验真」）。
    destroy() 与用户手动 cacheclear 的 clear 是有意为之，保留。
  - 结果：同线路名跨片不再互相污染（_LINE_H 里 4 条独立记录，繁花/狂飙各
    2160 与 unknown 正好相反，与实测一致）；假 4K 判定仍生效（奥本海默
    影探·联通云·4K·补 实测 1080 → kish_fake4k=1；天翼云 1440 → 1）；
    契约 10/10、home 0.71s/12 类、homeVideo 0.00s/30 条、分类 0.19s/20；
    搜索 繁花 1.41s/90 条、狂飙 1.20s/103 条、三体 1.61s/100 条（pd 均 12 条）；
    详情 繁花 0.77s/10 线、狂飙 0.74s/9 线、三体补齐 6 线；30 线程 2.62s / 0 错误。

20261121 二十次修订（画质判定日志 + 诊断中心「画质判定」分区）:
  - 动机：十九次修订把假 4K 判定做对了，但它对用户仍然是个黑盒 —— 只看到
    「点开 4K 被换了线」或「4K 却很糊」，看不到「宣称 2160 / 实测 1080」这个
    事实，出问题没法复现，也没法判断是判错了还是源就这样。
  - 处置 1：模块级环形日志 _QDIAG（80 条，_QDIAG_LOCK 保护）。记录
    (时间, 类型, 线路名, 宣称高度, 实测高度, 三档状态, 探测耗时, 后续动作)。
    写入点：_line_height 的真实探测（probe）、_play_one 的假 4K 结局
    （swap 换源成功 / keep 换不到播本线）、_play_other 的 skip（缓存已判 low
    直接跳过）与 drop（候选实测不够弃用）。
  - 处置 2：日志只写线路名与数字。URL、token、请求头一律不入环形缓冲 ——
    那些是每集都变的直链，留下来既没诊断价值又把长驻内存变成凭据仓库。
  - 处置 3：诊断中心新增「画质判定」分区，两张卡：
    · 画质判定日志：累计真 4K / 判假 / 探不到 的条数 + 最近 24 条明细；
    · 线路高度缓存：按片隔离的 _LINE_H 现状（三档计数、各自 TTL、最近 12 条）。
  - 处置 4：日志里的线路名用壳传来的展示名（「影探·天翼云·4K」），换源候选
    再补源标签（「小山·蓝光4K【推荐】」）—— 候选的 f 只是源内名，不带源名
    用户对不上是哪个源；判定口径仍用源内名，不受展示名影响。
  - 结果：繁花点「影探·联通云·4K」→ 记录「宣称 4K · 实测 4K · 真4K 0.24s」；
    奥本海默点「影探·联通云·4K·补」→「实测 1080P · 判假 · 换不到，播本线」，
    与 kish_fake4k=1 一致；报告里不出现 http://；20 写 × 100 + 10 读 × 200
    并发 0 错误、稳定停在 80 条；契约 10/10、home 0.31s/12 类、
    homeVideo 30 条、分类 0.13s/20、搜索 1.11~1.19s（pd 12 条）、
    详情 0.60~0.73s、播放出流。

20261122 二十一次修订（GPT 复核后采纳的三项：不新增文件、不改契约）:
  - 三项取的是「真缺口」，其余（拆多文件 / 远端画质表 / 线程池替换 /
    SearchPolicy 类化 / 合并集数函数）维持拒绝；测试安全网不进交付物 ——
    单文件交付里塞测试脚本等于交付第二份没人加载的文件。
  - 处置 1：后台任务闸门 _bg_spawn。守护线程保证主路径不等后台，但慢源长期
    不返回时线程会一直堆着（每个都攥着连接和响应体）。现在「补线 / 预热 /
    预取」这类可跳过的任务共用一个在飞上限 BG_MAX=12，满了直接不发、下次进
    详情自然重试；搜索派发、详情主拼接、播放解析不进闸门 —— 限流不能把片帝
    这种关键源一起限掉。计数在 finally 里减，异常不漏。
  - 处置 2：自更新替换前自检 _blob_ok。原来只查 `b'class Spider' in blob`
    这个字符串（注释里写一句就能过）。现在先 compile 一遍、再用 AST 找真实
    的 class Spider 和 7 个必备入口，任一不满足就删临时文件、原文件一个
    字节不动；sha256、强制证书校验、.bak 备份、os.replace 原子替换不动。
  - 处置 3：诊断中心「源状态」新增「上次搜索」卡片。早停的代价是这一轮少等
    了几个源，但用户在壳里只能看到「没有片帝的片」。现在记录最近一次真实
    搜索：有效应答 n/9、缺了谁（没赶上）、谁报故障、用时、按哪档 TTL 缓存。
    只读、不联网、不参与排序；「总览 / 首屏预算」补一行后台在飞任务数。
  - 结果：闸门 50 个任务并发提交只发 12 个（峰值 12），满额时返回耗
    0.0000s（不阻塞调用方），任务抛异常后计数仍归零；真实链路 bg 峰值 2/12，
    30 线程压测后 1.0s 内归零。更新器：好包替换 + .bak 长度一致；语法错 /
    注释里写 class Spider / Spider 缺 6 个入口三种坏包全部拒绝，原文件字节
    不变、无 .tmp 残留。诊断：残缺搜索显示「有效应答 7/9 · 缺 gg/jn ·
    缓存 60 秒」，完整搜索显示 9/9 + 600 秒，8 源报错时显示「源报错 1/9 ·
    20 秒」；200 写 + 200 读并发 0 错误。回归：契约 10/10、home 0.87~1.30s /
    12 类、homeVideo 0.00s/30 条、搜索 狂飙 1.06~1.72s / 繁花 1.06~1.31s
    （pd 均 12 条；gg/jn 偶发上游抖动）、详情 0.99~1.01s / 8~9 线、
    30 线程 冷启动 2.00s / 热缓存 0.40s、0 错误、bg 峰值 2/12 且 1 秒内归零。

20261122.kish2 二十二次修订（Claude 审计 + GPT 复核后只动三条，不新增文件）:
  - 审计里数得准的部分（407 处 except、约 10 处关证书校验、停用源 2054 行
    占 12.8%、自更新默认开、清单与脚本同源）都认；但只有三条是本轮该修的，
    其余要么和单文件交付冲突，要么没有可复现样本，维持不动。
  - 处置 1：备份从「尽力而为」改成「替换的前置条件」。原来写 .bak 用
    try/except pass 包着，备份失败照样 os.replace —— 那等于把唯一一份能跑的
    文件换掉还不留退路。现在先读旧文件、写 .bak、fsync、比对字节数，任一
    环节失败就删临时文件、原文件一个字节不动，返回
    'refused: backup failed'。目标文件本来不存在时不造空 .bak。
    顺带修掉一个真 bug：replace 双失败时最后一行 return 在 except 块外引用了
    exc，而 Python 3 退出 except 时会删掉 exc —— 这条分支原来必抛 NameError。
  - 处置 2：_prefetch_next（连看预取）归队。这是上一轮闸门唯一漏掉的裸
    threading.Thread：单集出流后它自己起线程解析下一集。现在走 _bg_spawn，
    被闸门跳过时把下一集从 _NEXT_PREFETCHED 撤回（原来先加标记再起线程，
    跳过/失败都不撤，那一集就永久被当成「预取过」）；源构造失败时同样撤回。
  - 处置 3：凭据落盘收紧到 0600。.zhaoju_guest_cookie（会话 cookie）和
    .cyc_auth.json（token + 用户名）原来按默认 umask 落盘，同机其他账号可读。
    现在写完调 _chmod600：POSIX 上真正生效，Windows 的 NTFS 只有只读一位、
    实测仍是 0666（不报错也无副作用，故不做平台分支）。
  - 验证：好包替换 + .bak 等长；.bak 写不出（占位成目录）→ 拒绝且旧文件字节
    不变、无 .tmp 残留；坏包仍拒绝；目标不存在直接落地且不造空 .bak；
    把 os.replace 打桩成必失败 → 返回 'replace failed: nope' 而非 NameError。
    预取：闸门满时 0 发包且 EP2 记录被撤回，闸门放开后 1 次发包、记录保留，
    重复调用不再发包，bg 计数归零。回归：契约 10/10、home 0.90s/12 类、
    homeVideo 0.00s/30 条、搜索 狂飙 1.46s（pd 12 条，8/9 源）/ 繁花 1.41s
    （pd 12 条，9/9 源）、详情 0.79s/8 线、播放出流、30 线程 0.42s / 0 错误。

20261122.kish3 二十三次修订（只改播放首屏：不动契约、不新增文件）:
  - 先测再改。冷播逐阶段计时（打桩包住 YT4K.play / _line_height / _play_other）：
    解析站两跳 0.44~7.51s、画质探测 0.15~0.26s、聚合组装 0~0.53s。同一部片三条
    影探线实测 0.44 / 0.89 / 7.51s，而且最慢那条最终是空 —— 慢的不是「影探这个
    源」，是解析站某一次请求卡住。本地代码没有可压的空间。
  - 处置 1：慢线并发抢答。本线路 RACE_AFTER=1.2s 还没回，就并行再开一条同片、
    同集、名义画质不降级的影探线（RACE_MAX=1），谁先给出可用地址用谁。阈值取
    1.2 是因为快线实测 0.44~1.04s，正常片一次都不 fanout（实测请求数仍是 1）。
    集匹配沿用换源规则：剧集必须集名或集序号一致，只有单集正片才允许直接顶；
    画质低于当前线的不抢（实测 4K 主线路在只有 1080 候选时返回 None）。
  - 处置 2：同集请求合并 _PLAY_INFLIGHT。详情预取和用户点播放原来会各打一遍
    解析站（双倍请求、可能触发限流）。现在后到的那个等前一个的结果，key 就是
    播放码本身。follower 最长等 PLAY_HEAD+2.5s，超时仍自己跑。
  - 处置 3：详情预取 PREFETCH_DELAY 2.0 → 0.25s。原来要停留 2 秒才开始预热，
    实测「详情 0.58s → 立刻播放」根本赶不上。现在详情返回 0.25s 就预热，用户
    点播放时要么已命中、要么合并同一次请求。
  - 处置 4：抢答结果按本线路记一笔（aggplay，600s）。抢答赢的是同片另一条线，
    主线路自己的缓存仍然是空的，重播同一条线会再白等 1.2s 才转抢答（实测重播
    1.20s）；记一笔后变 0.00s。
  - 实测：黑洞线（打桩让天翼云固定卡 7.5s 后返回空）改动前 7.23s 且结果为空，
    改动后 1.41~1.46s 出流；三条影探线全部卡 7.5s 时 5.00s 出流（改前 7.23s
    空）。快线冷播 1.09s / 1 次请求（不 fanout）。详情后立刻播放 0.56s、0.6s
    后播放 0.99s、1.5s 后播放 0.00s、重播 0.00s。30 线程 0.25s / 0 错误 /
    inflight 残留 0。契约 10/10、home 0.57s/12 类、homeVideo 0.00s/30 条、
    搜索 狂飙 0.81s / 繁花 0.76~0.90s（pd 均 12 条）、详情 0.74~0.88s/8 线。
  - 已知边界：抢答只在影探（tag='yt'）上做 —— 其它源没有「取票+解析」两跳，
    卡住通常是真的没内容；抢答赢的结果不做高度探测（已经等了 1.2s+，再叠
    0.2s 探测不值），画质靠候选的名义高度兜底；三条线全卡时仍按原预算收尾。

20261122.kish4 二十四次修订（电影首屏：小山解析站抖动 + sz 抢答）:
  - 先测再改。「四渡」详情 0.74s/6 线（全部小山），逐线冷播：
    小腾4K 0.16s 解析出链、4K 0.14s、蓝光4K 0.34s（回解析接口）、
    1080P 4.32s（前两次空、第三次成功）、小哔4K 20.38s（解析站 jx4k
    连续两次各 10.27s 超时后放弃）。请求级打桩确认：慢的不是取票
    （0.05~0.21s），是小山 _resolve 里 timeout=10 串行重试 2 次 —— 解析站
    一不回就是 20s 干等，而用户已经点了播放。
  - 处置 1：_resolve 改为候选并发 + 单次 3.5s + 整体 4.5s 封顶
    （RESOLVE_TIMEOUT/RESOLVE_BUDGET/RESOLVE_TRIES）。一轮全失败不算判死，
    预算内再补轮次（1080P 那种第三次才成功的线仍然能拿到真直链）。
    实测（关抢答）：小哔4K 20.38s → 4.57s、1080P 4.32s → 2.49s。
  - 处置 2：抢答从只认 yt 扩到同源（tag 参数，_play_one 里 'yt'/'sz' 都开）。
    依据：「四渡」6 条小山线里 3 条 0.1~0.3s 就出直链，用户点的那条却卡在
    解析站；同源别的线就是现成的备胎。仍不跨源（别的源慢是真没内容），
    仍要求同集、名义画质不降级（_race_pick 原规则不动）。
    实测：四渡小哔4K 20.38s → 1.71s；流浪地球2 小哔4K → 1.21s 且是真直链；
    1080P 4.32s → 1.21~1.71s。抽测 流浪地球2/孤注一掷/八佰 的 7 条小山线：
    0.45/0.53/1.19/1.21/1.21/0.41s，全部 parse=0 真直链。
  - 处置 3：抢答结果只有真直链（parse=0）才写 aggplay 600s 缓存；parse=1
    是「交壳解析」的兜底，把它记 10 分钟会让这条线一直拿兜底，而主线程稍后
    解出的真直链本来就在子源缓存里（重播 0.00s 走那条更好的路）。
  - 回归：home 0.68s/12 类、搜索 庆余年 1.10s/60 条（7 源）、详情 0.98s、
    影探剧集播放 0.91s、小山剧集 0.35s、重播 0.00s、30 线程 0.01s/0 错误。
"""

# ==================== 版本（必须放在最前：被聚合代码在模块级引用） ====
CODE_VERSION = '20261122.kish4'
UPDATE_URL = 'https://gitee.com/tao060702/tvbox/raw/master/update_kishuto.json'

# ======================================================================
# 模块：yt
# ======================================================================
# -*- coding: utf-8 -*-
"""
影探聚合 —— 四源聚合 TVBox Python 源（单文件）
========================================================================
首页 / 分类 / 筛选 / 搜索：影探4K（cms.lyyytv.cn）
详情页线路顺序：影探4K → 咕噜咕噜 → 橘汁4K → 找剧AI

源说明（2026-11-04 实测）
  影探4K   CMS + fys 解析接口，线路多为联通云/移动云/爱奇艺直链，可播率高
  咕噜咕噜  T3 私有协议（ECDH P-256 + AES-256-GCM + protobuf），线路最多
  橘汁4K   同 host 的另一套 T3 客户端（包名/版本/详情参数不同），目录与 id 空间
           独立，线路与咕噜有互补
  找剧AI   zhaoju4.com，HMAC 签名的 REST，官方 4K/1080P 线路需登录态（自动游客会话）

依赖：纯标准库（无 requests / pycryptodome），自带 AES-128/256-CBC、AES-256-GCM、
     P-256 ECDH、protobuf 裸编解码实现，可直接丢进 TVBox 的 python 目录使用。
========================================================================
"""

import ast
import base64
import gzip
import hashlib
import struct
import hmac
import json
import os
import re
import string
import random
import secrets
import socket
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zlib

try:
    from base.spider import Spider as _BaseSpider
except Exception:
    _BaseSpider = object

UA_WEB = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
NL = '\n'
_SEP = '\x1f'


# ============================================================================
# 基础工具
# ============================================================================

def text(value):
    return '' if value is None else str(value).strip()


def as_list(value):
    return value if isinstance(value, list) else []


def as_dict(value):
    return value if isinstance(value, dict) else {}


def loads(value):
    """宽松 JSON 解析：容忍前后缀、非 JSON 内容。"""
    try:
        if not value:
            return {}
        if isinstance(value, (bytes, bytearray)):
            value = value.decode('utf-8', 'replace')
        value = str(value).strip()
        if value[:1] not in ('{', '['):
            m = re.search(r'[\{\[].*[\}\]]', value, re.S)
            if not m:
                return {}
            value = m.group(0)
        return json.loads(value)
    except Exception:
        return {}


def page_of(value):
    m = re.match(r'\s*[+-]?\d+', '' if value is None else str(value))
    n = int(m.group(0)) if m else 0
    return max(1, n) if n else 1


def clean_name(value):
    """线路/标题清洗：去掉 $ # | 以及多余空白，避免破坏 TVBox 分隔符。"""
    s = text(value)
    for ch in ('$', '#', '$$$', '|'):
        s = s.replace(ch, ' ')
    return re.sub(r'\s+', ' ', s).strip()


def norm_title(value):
    s = text(value).lower()
    s = re.sub(r'[\s\-_:：·,，.。!！?？"“”\'’()（）\[\]【】]+', '', s)
    s = re.sub(r'(第[一二三四五六七八九十\d]+季|season\s*\d+|s\d{1,2})$', '', s)
    return s


_SEASON_SIMPLE = re.compile(
    r'(第[一二三四五六七八九十\d]+季|season\s*\d+|s\d{1,2})', re.I)
_QUALITY_NOISE = re.compile(
    r'(4k|8k|2160p?|1080p?|720p?|uhd|hdr\d*|蓝光|高清|超清|'
    r'国语|粤语|中字|字幕|完整版|未删减|合集|正片|bd|hd|dvd|web|remux)', re.I)


def strict_match(title, items):
    """详情页跨源补线路：只认「同一部片」，禁止片名包含式扩展匹配。

    旧 best_match 把「熊出没」⊂「熊出没之雪岭熊风」判成 0.82 分，
    于是剧集《熊出没》详情里挂进了电影版线路。这里要求核心片名完全
    一致，只允许剥掉画质/版本/年份后缀；季数标记不同一律不匹配。
    """
    import difflib

    def core(s):
        t = norm_title(str(s or ''))
        t = re.sub(r'[（(][^）)]*[）)]', '', t)
        t = _QUALITY_NOISE.sub('', t)
        t = re.sub(r'(19|20)\d{2}$', '', t)
        t = re.sub(r'第[一二三四五六七八九十\d]+[季部篇]$', '', t)
        return t.strip()

    want = core(title)
    if not want:
        return None
    wm = _SEASON_SIMPLE.search(str(title or ''))
    wtag = wm.group(0).lower() if wm else ''
    exact, near = [], []
    for it in as_list(items):
        if not isinstance(it, dict):
            continue
        name = str(it.get('vod_name') or it.get('name') or '')
        cm = _SEASON_SIMPLE.search(name)
        ctag = cm.group(0).lower() if cm else ''
        if wtag and ctag and wtag != ctag:
            continue
        got = core(name)
        if not got:
            continue
        if got == want:
            exact.append(it)
        elif (abs(len(got) - len(want)) <= 2
              and difflib.SequenceMatcher(None, got, want).ratio() >= 0.97):
            near.append(it)
    return (exact or near or [None])[0]


# ============================================================================
# 缓存
# ============================================================================

_CACHE = {}
_CACHE_LOCK = threading.Lock()
_TITLE_MEMO = {}          # vod_id -> 片名：个别源详情只回数字 id，补线路要靠它
_DETAIL_MEMO = {}         # 详情 id -> (时间, [(线路名, [(集名, 播放码)])])
_PREFETCHED = set()       # 已预热过首集的详情 id，避免反复触发
# 同一集正在解析中：预取和用户点击撞在一起时共享一次请求，不再各打一遍解析站。
# key = 播放码（本身已含源/线路/片/集），value = [Event, {'r': 结果}]
_PLAY_INFLIGHT = {}
_PLAY_INFLIGHT_LOCK = threading.Lock()


def _cap_put(box, key, value, cap, drop=None):
    """有界写入：满了按插入顺序丢最老的一批，不整表 clear()。

    原来的写法是 `if len(box) > cap: box.clear()`，代价是刚探好/刚拼好的
    结果一起没了：线路高度缓存一清，同一批线路要重新探 0.3~1.5s；详情记忆
    一清，播放失败时就没有同集换源表可用（表现为「换源突然失效」）。
    字典保持插入顺序，按最老的丢就够了，代价只是多占一点内存。
    """
    try:
        if cap > 0 and len(box) >= cap:
            n = drop or max(8, cap // 8)
            for k in list(box.keys())[:n]:
                box.pop(k, None)
    except Exception:
        pass
    box[key] = value


# ---- 后台任务闸门 -----------------------------------------------------------
# 守护线程保证主路径不等后台，但慢源长期不返回时，后台线程会一直堆着（每个
# 都攥着一个连接和一份响应体）。这里只给「补线 / 预热 / 预取」这类**可跳过**
# 的后台任务设上限：满了就干脆不发，下次进详情/搜索自然重试，代价只是这一次
# 少补几条线。搜索派发、详情主拼接、播放解析这些关键路径**不进闸门** ——
# 限流不能把用户正当要的结果也一起限掉（片帝尤其不能）。
_BG_LOCK = threading.Lock()
_BG_LIVE = [0]
_BG_PEAK = [0]
BG_MAX = 12          # 同时存在的后台补充任务上限（探测实测峰值 9，留 3 条余量）


def _bg_live():
    with _BG_LOCK:
        return _BG_LIVE[0], _BG_PEAK[0]


def _bg_spawn(fn, args=(), name=''):
    """发一个非关键后台任务；超出上限返回 None。异常吞掉，退出必减计数。"""
    with _BG_LOCK:
        if _BG_LIVE[0] >= BG_MAX:
            return None
        _BG_LIVE[0] += 1
        if _BG_LIVE[0] > _BG_PEAK[0]:
            _BG_PEAK[0] = _BG_LIVE[0]

    def run():
        try:
            fn(*args)
        except Exception:
            pass
        finally:
            with _BG_LOCK:
                _BG_LIVE[0] = max(0, _BG_LIVE[0] - 1)

    try:
        th = threading.Thread(target=run, daemon=True, name=name or 'kish-bg')
        th.start()
        return th
    except Exception:
        with _BG_LOCK:
            _BG_LIVE[0] = max(0, _BG_LIVE[0] - 1)
        return None

# 片名搜索结果记忆：详情页每进一次都会拿片名去 9 个源各搜一遍，实测连着
# 进 4 次同一部片就打了 80 次源站请求（片帝 8 次、找剧 9 次同一个词）。
# 这里按 (源, 归一化关键词) 缓存列表，空结果也缓存 —— 死掉的源不会每轮重试。
_SRCH_MEMO = {}
_SRCH_LOCK = threading.Lock()
_SRCH_INFLIGHT = {}
_SRCH_TTL = 300
_SRCH_MAX = 600


def _srch_get(key):
    now = time.time()
    with _SRCH_LOCK:
        hit = _SRCH_MEMO.get(key)
        if not hit:
            return None
        if hit[0] < now:
            _SRCH_MEMO.pop(key, None)
            return None
        return hit[1]


def _srch_put(key, items):
    with _SRCH_LOCK:
        _cap_put(_SRCH_MEMO, key, (time.time() + _SRCH_TTL, items), _SRCH_MAX)


def _srch_fetch(key, fn):
    """取某源对某关键词的搜索结果：命中缓存直接返回，未命中才打源站。

    并发合并：连着翻几部片时，同一关键词会被多个详情线程同时搜（橘汁/
    片帝首搜要 1~3s，前一个还没回来后一个又发一遍），这里用 in-flight
    事件让后来者等第一个结果，源站只会收到一次请求。
    搜索抛异常也写空结果，避免死掉的源每轮重试。
    """
    hit = _srch_get(key)
    if hit is not None:
        return hit
    with _SRCH_LOCK:
        ev = _SRCH_INFLIGHT.get(key)
        owner = ev is None
        if owner:
            ev = threading.Event()
            _SRCH_INFLIGHT[key] = ev
    if not owner:
        ev.wait(6.0)
        got = _srch_get(key)
        return got if got is not None else []
    try:
        items = fn() or []
    except Exception:
        items = []
    _srch_put(key, items)
    with _SRCH_LOCK:
        _SRCH_INFLIGHT.pop(key, None)
    ev.set()
    return items


def _memo_detail(cid, lines):
    """记住本次详情拼出的全部线路，播放失败时用它同集换源。"""
    if not cid or not lines:
        return
    now = time.time()
    if len(_DETAIL_MEMO) > 200:
        for k in [k for k, v in list(_DETAIL_MEMO.items())
                  if now - v[0] > 1800]:
            _DETAIL_MEMO.pop(k, None)
    _cap_put(_DETAIL_MEMO, str(cid), (now, lines), 200)


def _unpack_lines(vod):
    """把 _pack 后的 vod_play_from/url 反解成 [(线路名, [(集名, 播放码)])]。"""
    froms = str(vod.get('vod_play_from') or '').split('$$$')
    urls = str(vod.get('vod_play_url') or '').split('$$$')
    out = []
    for i, name in enumerate(froms):
        name = str(name or '').strip()
        if not name:
            continue
        seg = urls[i] if i < len(urls) else ''
        eps = []
        for part in str(seg).split('#'):
            part = part.strip()
            if not part:
                continue
            nm, sep, pid = part.partition('$')
            if not sep:
                nm, pid = '', part
            eps.append((nm, pid))
        if eps:
            out.append((name, eps))
    return out


def _memo_title(code, name):
    """记下列表/搜索里看到的真实片名，供详情缺片名时兜底。"""
    t = str(name or '').strip()
    if not code or len(t) < 2 or t.isdigit():
        return
    _cap_put(_TITLE_MEMO, str(code), t, 4000, drop=200)


def cache_get(key):
    with _CACHE_LOCK:
        hit = _CACHE.get(key)
        if not hit:
            return None
        if hit[0] < time.time():
            _CACHE.pop(key, None)
            return None
        return hit[1]


def cache_put(key, value, ttl):
    with _CACHE_LOCK:
        if len(_CACHE) > 800:
            now = time.time()
            dead = [k for k, v in _CACHE.items() if v[0] < now]
            for k in dead[:300]:
                _CACHE.pop(k, None)
        _cap_put(_CACHE, key, (time.time() + ttl, value), 1000, drop=150)


# ============================================================================
# HTTP（统一层：gzip、连接复用靠 keep-alive 由 urllib 自行管理、瞬时错误重试）
# ============================================================================

_CTX = [None, False]
_CTX_VERIFY = [None, False]


def ssl_ctx():
    """采集用的宽松上下文：TVBox 内置 Python 常缺根证书，这些是公开采集接口，
    统一不校验。凡是「会把远端内容写进本地」（自更新清单/脚本）都必须用
    ssl_ctx_verified()，否则中间人可以直接改代码。"""
    if _CTX[1] is False:
        try:
            c = ssl.create_default_context()
            c.check_hostname = False
            c.verify_mode = ssl.CERT_NONE
            _CTX[0] = c
        except Exception:
            _CTX[0] = None
        _CTX[1] = True
    return _CTX[0]


def ssl_ctx_verified():
    """严格校验证书的上下文：自更新链路专用，失败也不降级。"""
    if _CTX_VERIFY[1] is False:
        try:
            _CTX_VERIFY[0] = ssl.create_default_context()
        except Exception:
            _CTX_VERIFY[0] = None
        _CTX_VERIFY[1] = True
    return _CTX_VERIFY[0]


def http(url, method='GET', headers=None, data=None, timeout=8.0,
         retries=2, backoff=0.35, verify=False):
    """返回 (status, body_bytes)。网络/瞬时错误自动重试，绝不抛异常。"""
    url = safe_url(url)
    hdr = {'User-Agent': UA_WEB, 'Accept': '*/*', 'Accept-Encoding': 'gzip'}
    if headers:
        hdr.update(headers)
    tries = max(1, int(retries))
    last = (0, b'')
    for i in range(tries):
        if i:
            time.sleep(backoff * i)
        try:
            req = urllib.request.Request(url, data=data, headers=hdr, method=method)
            kw = {'timeout': timeout}
            ctx = ssl_ctx_verified() if verify else ssl_ctx()
            if ctx is not None:
                kw['context'] = ctx
            with urllib.request.urlopen(req, **kw) as rsp:
                body = rsp.read()
                enc = (rsp.headers.get('Content-Encoding') or '').lower()
                if 'gzip' in enc:
                    try:
                        body = gzip.decompress(body)
                    except Exception:
                        pass
                elif 'deflate' in enc:
                    try:
                        body = zlib.decompress(body)
                    except Exception:
                        try:
                            body = zlib.decompress(body, -zlib.MAX_WBITS)
                        except Exception:
                            pass
                status = rsp.getcode()
                if status in (429, 500, 502, 503, 504) and i < tries - 1:
                    last = (status, body)
                    continue
                return (status, body)
        except urllib.error.HTTPError as exc:
            try:
                body = exc.read()
            except Exception:
                body = b''
            last = (exc.code, body)
            if exc.code in (429, 500, 502, 503, 504) and i < tries - 1:
                continue
            return last
        except (socket.timeout, ssl.SSLError, urllib.error.URLError, OSError):
            last = (0, b'')
            continue
        except Exception:
            last = (0, b'')
            continue
    return last


def http_text(url, method='GET', headers=None, data=None, timeout=8.0,
              retries=2, charset='utf-8'):
    st, body = http(url, method, headers, data, timeout, retries)
    if not body:
        return st, ''
    try:
        return st, body.decode(charset, 'replace')
    except Exception:
        return st, body.decode('utf-8', 'replace')


def http_json(url, method='GET', headers=None, data=None, timeout=8.0, retries=2):
    st, txt = http_text(url, method, headers, data, timeout, retries)
    if not txt:
        return {}
    return loads(txt)


def http_cached(key, ttl, fn):
    hit = cache_get(key)
    if hit is not None:
        return hit
    value = fn()
    if value:
        cache_put(key, value, ttl)
    return value


def is_url(value):
    try:
        p = urllib.parse.urlparse(text(value))
        return p.scheme in ('http', 'https') and bool(p.netloc)
    except Exception:
        return False


_URL_SAFE = ":/?#[]@!$&'()*+,;=%~"


def safe_url(value):
    """urllib 不接受 URL 里的非 ASCII（中文文件名很常见）→ 百分号编码掉。"""
    u = text(value).strip()
    try:
        u.encode('ascii')
        return u
    except Exception:
        try:
            return urllib.parse.quote(u, safe=_URL_SAFE)
        except Exception:
            return u


_STREAM_RE = re.compile(r'\.(?:m3u8|mpd)$', re.I)
_MEDIA_RE = re.compile(r'\.(?:mp4|m3u8|mpd|flv|avi|mkv|ts|mov|wmv|webm|m4v)$', re.I)


def is_stream_url(url):
    if not is_url(url):
        return False
    return bool(_STREAM_RE.search(urllib.parse.urlparse(text(url)).path))


def is_media_url(url):
    if not is_url(url):
        return False
    return bool(_MEDIA_RE.search(urllib.parse.urlparse(text(url)).path))


# ============================================================================
# 纯 Python AES（128/256 CBC + 256 GCM）
# ============================================================================

def _xtime(a):
    a <<= 1
    return (a ^ 0x1B) & 0xFF if a & 0x100 else a


def _gmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return r


_SBOX = None
_INV_SBOX = None


def _aes_tables():
    global _SBOX, _INV_SBOX
    if _SBOX is not None:
        return
    exp = [0] * 256
    log = [0] * 256
    x = 1
    for i in range(255):
        exp[i] = x
        log[x] = i
        x = _gmul(x, 0x03)
    sb = [0] * 256
    ib = [0] * 256
    for i in range(256):
        inv = 0 if i == 0 else exp[(255 - log[i]) % 255]
        t = inv
        s = inv
        for _ in range(4):
            s = ((s << 1) | (s >> 7)) & 0xFF
            t ^= s
        sb[i] = t ^ 0x63
        ib[sb[i]] = i
    _SBOX = bytes(sb)
    _INV_SBOX = bytes(ib)


def _expand_key(key):
    """支持 16(128)/24(192)/32(256) 字节密钥，返回轮密钥列表。"""
    _aes_tables()
    nk = len(key) // 4
    if nk not in (4, 6, 8):
        raise ValueError('bad aes key length')
    total = 4 * (nk + 7)
    w = [list(key[i * 4:i * 4 + 4]) for i in range(nk)]
    rcon = 1
    for i in range(nk, total):
        t = list(w[i - 1])
        if i % nk == 0:
            t = t[1:] + t[:1]
            t = [_SBOX[b] for b in t]
            t[0] ^= rcon
            rcon = _xtime(rcon)
        elif nk > 6 and i % nk == 4:
            t = [_SBOX[b] for b in t]
        w.append([w[i - nk][j] ^ t[j] for j in range(4)])
    return [sum(w[i:i + 4], []) for i in range(0, total, 4)]


def _shift_rows(state, encrypt):
    out = [0] * 16
    for r in range(4):
        for c in range(4):
            out[r + 4 * c] = state[r + 4 * ((c + (r if encrypt else -r)) % 4)]
    return out


def _mix_columns(state):
    out = state[:]
    for c in range(4):
        a = out[0 + 4 * c]
        b = out[1 + 4 * c]
        d = out[2 + 4 * c]
        e = out[3 + 4 * c]
        t = a ^ b ^ d ^ e
        out[0 + 4 * c] = a ^ t ^ _xtime(a ^ b)
        out[1 + 4 * c] = b ^ t ^ _xtime(b ^ d)
        out[2 + 4 * c] = d ^ t ^ _xtime(d ^ e)
        out[3 + 4 * c] = e ^ t ^ _xtime(e ^ a)
    return out


def _mul9(x):
    return _xtime(_xtime(_xtime(x))) ^ x


def _mul11(x):
    return _xtime(_xtime(_xtime(x))) ^ _xtime(x) ^ x


def _mul13(x):
    return _xtime(_xtime(_xtime(x))) ^ _xtime(_xtime(x)) ^ x


def _mul14(x):
    return _xtime(_xtime(_xtime(x))) ^ _xtime(_xtime(x)) ^ _xtime(x)


def _inv_mix_columns(state):
    out = state[:]
    for c in range(4):
        a = out[0 + 4 * c]
        b = out[1 + 4 * c]
        d = out[2 + 4 * c]
        e = out[3 + 4 * c]
        out[0 + 4 * c] = _mul14(a) ^ _mul11(b) ^ _mul13(d) ^ _mul9(e)
        out[1 + 4 * c] = _mul9(a) ^ _mul14(b) ^ _mul11(d) ^ _mul13(e)
        out[2 + 4 * c] = _mul13(a) ^ _mul9(b) ^ _mul14(d) ^ _mul11(e)
        out[3 + 4 * c] = _mul11(a) ^ _mul13(b) ^ _mul9(d) ^ _mul14(e)
    return out


def _enc_block(block, rk):
    nr = len(rk) - 1
    st = [s ^ k for s, k in zip(block, rk[0])]
    for r in range(1, nr):
        st = [_SBOX[b] for b in st]
        st = _shift_rows(st, True)
        st = _mix_columns(st)
        st = [s ^ k for s, k in zip(st, rk[r])]
    st = [_SBOX[b] for b in st]
    st = _shift_rows(st, True)
    return bytes([s ^ k for s, k in zip(st, rk[nr])])


def _dec_block(block, rk):
    nr = len(rk) - 1
    st = [s ^ k for s, k in zip(block, rk[nr])]
    for r in range(nr - 1, 0, -1):
        st = _shift_rows(st, False)
        st = [_INV_SBOX[b] for b in st]
        st = [s ^ k for s, k in zip(st, rk[r])]
        st = _inv_mix_columns(st)
    st = _shift_rows(st, False)
    st = [_INV_SBOX[b] for b in st]
    return bytes([s ^ k for s, k in zip(st, rk[0])])


def cbc_encrypt(key, iv, data, pad=True):
    rk = _expand_key(key)
    if pad:
        n = 16 - len(data) % 16
        data = data + bytes([n]) * n
    out = bytearray()
    prev = iv
    for i in range(0, len(data), 16):
        blk = bytes(a ^ b for a, b in zip(data[i:i + 16], prev))
        prev = _enc_block(blk, rk)
        out += prev
    return bytes(out)


def cbc_decrypt(key, iv, data, unpad=False):
    rk = _expand_key(key)
    out = bytearray()
    prev = iv
    end = len(data) - len(data) % 16
    for i in range(0, end, 16):
        blk = data[i:i + 16]
        out += bytes(a ^ b for a, b in zip(_dec_block(blk, rk), prev))
        prev = blk
    res = bytes(out)
    if unpad and res:
        n = res[-1]
        if 1 <= n <= 16 and res[-n:] == bytes([n]) * n:
            res = res[:-n]
    return res


_GCM_R = 0xE1000000000000000000000000000000


def _ghash_mul(x, y):
    z = 0
    for i in range(128):
        if (x >> (127 - i)) & 1:
            z ^= y
        if y & 1:
            y = (y >> 1) ^ _GCM_R
        else:
            y >>= 1
    return z


def _ghash(h, aad, ciphertext):
    y = 0
    for i in range(0, len(aad), 16):
        blk = int.from_bytes(aad[i:i + 16].ljust(16, b'\x00'), 'big')
        y = _ghash_mul(y ^ blk, h)
    for i in range(0, len(ciphertext), 16):
        blk = int.from_bytes(ciphertext[i:i + 16].ljust(16, b'\x00'), 'big')
        y = _ghash_mul(y ^ blk, h)
    lens = (len(aad) * 8).to_bytes(8, 'big') + (len(ciphertext) * 8).to_bytes(8, 'big')
    return _ghash_mul(y ^ int.from_bytes(lens, 'big'), h)


def gcm_encrypt(key, nonce, data, aad=b''):
    rk = _expand_key(key)
    h = int.from_bytes(_enc_block(b'\x00' * 16, rk), 'big')
    j0 = nonce + b'\x00\x00\x00\x01'
    counter = int.from_bytes(j0, 'big')
    out = bytearray()
    for i in range(0, len(data), 16):
        counter += 1
        ks = _enc_block(counter.to_bytes(16, 'big'), rk)
        chunk = data[i:i + 16]
        out += bytes(b ^ k for b, k in zip(chunk, ks))
    ciphertext = bytes(out)
    s = _ghash(h, aad, ciphertext)
    tag = (s ^ int.from_bytes(_enc_block(j0, rk), 'big')).to_bytes(16, 'big')[:16]
    return ciphertext, tag


def gcm_decrypt(key, nonce, data, tag=None, aad=b''):
    """tag 为 None 时按 data[-16:] 切分（部分客户端不校验 tag）。"""
    rk = _expand_key(key)
    if tag is None:
        tag = data[-16:]
        data = data[:-16]
    j0 = nonce + b'\x00\x00\x00\x01'
    counter = int.from_bytes(j0, 'big')
    out = bytearray()
    for i in range(0, len(data), 16):
        counter += 1
        ks = _enc_block(counter.to_bytes(16, 'big'), rk)
        chunk = data[i:i + 16]
        out += bytes(b ^ k for b, k in zip(chunk, ks))
    return bytes(out)


# ============================================================================
# P-256（secp256r1）ECDH
# ============================================================================

_P256_P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
_P256_A = _P256_P - 3
_P256_N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
_P256_G = (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
           0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)


def _p256_double(pt):
    if pt is None:
        return None
    x, y = pt
    if y == 0:
        return None
    lam = (3 * x * x + _P256_A) * pow(2 * y, _P256_P - 2, _P256_P) % _P256_P
    x3 = (lam * lam - 2 * x) % _P256_P
    y3 = (lam * (x - x3) - y) % _P256_P
    return (x3, y3)


def _p256_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if (y1 + y2) % _P256_P == 0:
            return None
        return _p256_double(p1)
    lam = (y2 - y1) * pow((x2 - x1) % _P256_P, _P256_P - 2, _P256_P) % _P256_P
    x3 = (lam * lam - x1 - x2) % _P256_P
    y3 = (lam * (x1 - x3) - y1) % _P256_P
    return (x3, y3)


def _p256_mul(k, pt):
    res = None
    addend = pt
    while k:
        if k & 1:
            res = _p256_add(res, addend)
        addend = _p256_double(addend)
        k >>= 1
    return res


def ecdh_keypair():
    priv = int.from_bytes(secrets.token_bytes(32), 'big') % (_P256_N - 1) + 1
    pub = _p256_mul(priv, _P256_G)
    raw = b'\x04' + pub[0].to_bytes(32, 'big') + pub[1].to_bytes(32, 'big')
    return priv, raw


def ecdh_shared_x(priv, server_pub):
    raw = bytes(server_pub or b'')
    if len(raw) == 65 and raw[0] == 4:
        pt = (int.from_bytes(raw[1:33], 'big'), int.from_bytes(raw[33:65], 'big'))
    elif len(raw) == 64:
        pt = (int.from_bytes(raw[:32], 'big'), int.from_bytes(raw[32:], 'big'))
    else:
        raise ValueError('bad server public key')
    shared = _p256_mul(priv, pt)
    if shared is None:
        raise ValueError('ecdh infinity')
    return shared[0].to_bytes(32, 'big')


# ============================================================================
# protobuf 裸编解码（T3 协议用）
# ============================================================================

def pb_varint(value):
    if value < 0:
        raise ValueError('negative varint')
    out = bytearray()
    while value >= 0x80:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)
    return bytes(out)


def pb_bytes(field, value):
    if isinstance(value, str):
        value = value.encode('utf-8')
    return pb_varint((field << 3) | 2) + pb_varint(len(value)) + value


def pb_var(field, value):
    return pb_varint(field << 3) + pb_varint(int(value))


def pb_read_varint(data, pos):
    value = 0
    shift = 0
    while pos < len(data) and shift < 70:
        b = data[pos]
        pos += 1
        value |= (b & 0x7F) << shift
        if b < 0x80:
            return value, pos
        shift += 7
    raise ValueError('bad varint')


def pb_decode(data):
    out = []
    pos = 0
    size = len(data or b'')
    while pos < size:
        key, pos = pb_read_varint(data, pos)
        field, wire = key >> 3, key & 7
        if field == 0:
            raise ValueError('field zero')
        if wire == 0:
            value, pos = pb_read_varint(data, pos)
        elif wire == 1:
            value = data[pos:pos + 8]
            pos += 8
        elif wire == 2:
            length, pos = pb_read_varint(data, pos)
            value = data[pos:pos + length]
            pos += length
        elif wire == 5:
            value = data[pos:pos + 4]
            pos += 4
        else:
            raise ValueError('wire %d' % wire)
        if pos > size:
            raise ValueError('truncated')
        out.append((field, wire, value))
    return out


def pb_field(data, field, wire=None):
    values = [v for f, w, v in pb_decode(data) if f == field and (wire is None or w == wire)]
    return values[-1] if values else None


def pb_fields(data, field, wire=None):
    return [v for f, w, v in pb_decode(data) if f == field and (wire is None or w == wire)]


def pb_str(data, field, default=''):
    value = pb_field(data, field, 2)
    if value is None:
        return default
    try:
        return value.decode('utf-8')
    except Exception:
        return default


def raw_deflate(data, level=6):
    c = zlib.compressobj(level, zlib.DEFLATED, wbits=-15, memLevel=8,
                         strategy=zlib.Z_DEFAULT_STRATEGY)
    return c.compress(data) + c.flush()


def raw_inflate(data):
    return zlib.decompress(data, -15)


def b64url_encode(raw):
    try:
        if isinstance(raw, str):
            raw = raw.encode('utf-8')
        return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')
    except Exception:
        return ''


def b64url_decode(txt):
    try:
        s = text(txt)
        s += '=' * ((4 - len(s) % 4) % 4)
        return base64.urlsafe_b64decode(s.encode('ascii'))
    except Exception:
        return b''
# ============================================================================
# 云端自更新
#
#   原理：脚本 init 时后台拉一份「版本清单」，远端版本比本地新就下载整份
#   .py 覆盖自身文件；下次壳加载这个文件即是新代码（无需改配置、无需手动拷）。
#
#   开启方式：把 UPDATE_URL 填成清单地址（或 extend 里传 update_url），
#   extend 里加 {"auto_update":0} 可关掉自动检查。
#   清单只支持 JSON（纯文本清单没有 sha256，一律拒绝）：
#        {"version":"20261105.1930",
#         "url":"https://xx.com/tvbox/影探聚合.py",
#         "sha256":"…", "size":91234, "note":"修了找剧 503"}
#
#   安全阀（自更新会把远端代码写进本地并被执行，所以按最严的标准来）：
#     · 清单与脚本下载都走证书校验（失败不降级，宁可更不了）
#     · 清单必须带 sha256，缺 sha256 直接放弃，不支持"版本号新就放行"的兜底
#     · 只接受 2xx、体积 <= UPDATE_MAX_BYTES、含 "class Spider" 的 Python 文本
#     · 写盘走临时文件 + os.replace 原子替换，失败时旁挂 .new 不破坏旧文件
# ============================================================================

UPDATE_MAX_BYTES = 4 * 1024 * 1024
SELF_NAME = 'Kishuto.py'

_UPDATE_LAST = {'ok': False, 'updated': False, 'version': CODE_VERSION,
                'msg': '', 'note': '', 'at': 0.0}


def code_version():
    return CODE_VERSION


def _ver_tuple(value):
    return tuple(int(x) for x in re.findall(r'\d+', text(value))[:4]) or (0,)


def version_newer(far, near):
    """far 是否比 near 新。"""
    a, b = _ver_tuple(far), _ver_tuple(near)
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)) > b + (0,) * (n - len(b))


def self_path():
    try:
        p = os.path.abspath(__file__)
        if os.path.isfile(p):
            return p
    except Exception:
        pass
    return ''


def self_name():
    p = self_path()
    return os.path.basename(p) if p else SELF_NAME


def parse_manifest(body):
    """→ {'version','url','sha256','note'}；纯文本清单只给 version。"""
    if isinstance(body, (bytes, bytearray)):
        try:
            body = bytes(body).decode('utf-8', 'replace')
        except Exception:
            return {}
    raw = text(body).lstrip('\ufeff').strip()
    if not raw:
        return {}
    if raw[:1] == '{':
        try:
            obj = loads(raw)
        except Exception:
            obj = None
        if isinstance(obj, dict):
            return {
                'version': text(obj.get('version') or obj.get('ver')),
                'url': text(obj.get('url') or obj.get('file') or obj.get('py')),
                'sha256': text(obj.get('sha256') or obj.get('hash')).lower(),
                'note': text(obj.get('note') or obj.get('desc')),
            }
    return {'version': raw.splitlines()[0].strip(), 'url': '',
            'sha256': '', 'note': ''}


SPIDER_ENTRIES = ('init', 'homeContent', 'homeVideoContent', 'categoryContent',
                  'searchContent', 'detailContent', 'playerContent')


def _blob_ok(blob):
    """替换前自检：能编译 + 真有 Spider 和必备入口。→ (ok, 原因)

    只编译、不执行：写完临时文件先让解释器编一遍，语法错/截断的包在这里就
    拦下，绝不落到正在跑的那份文件上。原来只查 `b'class Spider' in blob`
    这个字符串 —— 注释里写一句就能过。现在用 AST 找真实定义。

    回滚说明：编译通过才替换，替换是 os.replace 原子的，且替换前已存 .bak。
    如果新文件能编译但运行期才炸，本文件自身已经跑不起来，没有代码能执行
    回滚 —— 那种情况只能靠壳里把 .bak 改名回去，所以这里把「能编译」当成
    替换的硬门槛。
    """
    try:
        compile(blob, '<update>', 'exec')
        tree = ast.parse(blob)
    except Exception as exc:
        return False, 'compile: %s' % (exc or 'syntax')
    cls = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == 'Spider':
            cls = node
            break
    if cls is None:
        return False, 'no class Spider'
    have = set(m.name for m in cls.body
               if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)))
    miss = [x for x in SPIDER_ENTRIES if x not in have]
    if miss:
        return False, 'Spider 缺入口: %s' % ','.join(miss)
    return True, ''


def _chmod600(path):
    """凭据类文件收紧到只给自己读写。

    POSIX（Linux / Android 上的 TVBox）按标准生效：属主读写、其余全关。
    Windows 的 NTFS 只有「只读」一位，chmod 改不动 ACL，实测仍是 0666 ——
    不报错也无副作用，所以这里不做平台分支。
    """
    try:
        os.chmod(path, 0o600)
        return True
    except Exception:
        return False


def _write_self(path, blob):
    """编译自检 → 备份 → 原子替换自身文件。→ (是否替换成功, 说明, 是否合规)"""
    folder = os.path.dirname(path) or '.'
    tmp = os.path.join(folder, '.upd_%s.tmp' % uuid.uuid4().hex[:8])
    try:
        with open(tmp, 'wb') as fp:
            fp.write(blob)
            fp.flush()
            try:
                os.fsync(fp.fileno())
            except Exception:
                pass
    except Exception as exc:
        try:
            os.remove(tmp)
        except Exception:
            pass
        return False, 'write failed: %s' % exc, False
    ok, why = _blob_ok(blob)
    if not ok:
        try:
            os.remove(tmp)
        except Exception:
            pass
        return False, 'rejected (%s)' % why, False
    # 备份是替换的前置条件，不是尽力而为：写不出 .bak 就一个字节都不动。
    # 代价是更新偶尔被跳过（磁盘满 / 目录只读），但旧文件始终能跑。
    bak = path + '.bak'
    try:
        if os.path.exists(path):
            with open(path, 'rb') as src:
                old = src.read()
            with open(bak, 'wb') as dst:
                dst.write(old)
                dst.flush()
                try:
                    os.fsync(dst.fileno())
                except Exception:
                    pass
            if os.path.getsize(bak) != len(old):
                raise IOError('bak size mismatch')
    except Exception as exc:
        try:
            os.remove(tmp)
        except Exception:
            pass
        return False, 'refused: backup failed (%s), old file kept' % exc, False
    try:
        os.replace(tmp, path)
        return True, 'replaced', True
    except Exception as exc:
        alt = path + '.new'
        try:
            os.replace(tmp, alt)
            return False, 'replace failed(%s), saved %s' % (exc, os.path.basename(alt)), True
        except Exception:
            try:
                os.remove(tmp)
            except Exception:
                pass
        # 注意别把这行挪到 except 外面：Python 3 退出 except 块时会删掉 exc
        return False, 'replace failed: %s' % exc, True


def _fetch_manifest(url):
    """带时间戳采样两次取版本较大的，都失败再回退原始地址。→ (manifest, status)

    走证书校验：清单决定了要下载哪份代码，不能容忍中间人改写。
    """
    sep = '&' if '?' in url else '?'
    got, status = [], 0
    for i in range(2):
        hit = '%s%st=%d' % (url, sep, int(time.time() * 1000) + i * 7)
        status, body = http(hit, timeout=8, retries=1, verify=True,
                            headers={'Cache-Control': 'no-cache',
                                     'Pragma': 'no-cache'})
        if status == 200 and body:
            got.append(body)
    if not got:
        status, body = http(url, timeout=8, retries=1, verify=True,
                            headers={'Cache-Control': 'no-cache',
                                     'Pragma': 'no-cache'})
        if status == 200 and body:
            got.append(body)
    best = {}
    for body in got:
        man = parse_manifest(body)
        ver = text(man.get('version'))
        if ver and (not best or version_newer(ver, text(best.get('version')))):
            best = man
    return best, status


def check_update(url=''):
    """拉清单 → 校验 → 覆盖自身。返回结果 dict（绝不影响主流程）。

    安全底线：清单必须给 sha256，脚本下载后必须与之吻合，否则一律不动磁盘。
    去掉原先「sha 对不上但版本号更新就放行」的兜底——那相当于把完整性校验
    变成可绕过的摆设，远端仓库被黑或被劫持即可下发任意代码。
    """
    url = text(url or UPDATE_URL)
    out = {'ok': False, 'updated': False, 'version': CODE_VERSION,
           'msg': '', 'note': '', 'at': time.time()}
    if not url:
        out['msg'] = 'no update url'
        return out
    try:
        dest = self_path()
        if not dest:
            out['msg'] = 'self path unknown'
            return out

        last = ''
        for attempt in range(3):
            if attempt:
                time.sleep(1.2 * attempt)
            man, status = _fetch_manifest(url)
            far = text(man.get('version'))
            if not far:
                last = 'manifest http %s' % status
                continue
            out['version'] = far
            out['note'] = man.get('note') or ''
            if not version_newer(far, CODE_VERSION):
                out['ok'] = True
                out['msg'] = 'up to date (%s)' % CODE_VERSION
                return out

            digest = text(man.get('sha256')).lower()
            if len(digest) != 64:
                out['msg'] = 'manifest 缺 sha256，拒绝更新'
                return out

            target_url = text(man.get('url'))
            cands = []
            if target_url:
                cands.append(target_url if is_url(target_url)
                             else urllib.parse.urljoin(url, target_url))
            # 清单没写地址时的兜底：同目录 ASCII 名、再退本地同名
            for name in ('Kishuto.py', self_name()):
                cands.append(urllib.parse.urljoin(url, name))

            blob = b''
            seen = set()
            for cand in cands:
                if cand in seen:
                    continue
                seen.add(cand)
                sep = '&' if '?' in cand else '?'
                for hit in ('%s%st=%d' % (cand, sep, int(time.time() * 1000)), cand):
                    st2, body = http(hit, timeout=25, retries=1, verify=True)
                    if st2 == 200 and body and b'class Spider' in body:
                        blob = body
                        break
            if not blob:
                last = 'download failed'
                continue
            if len(blob) > UPDATE_MAX_BYTES:
                out['msg'] = 'too large (%d)' % len(blob)
                return out

            if hashlib.sha256(blob).hexdigest() != digest:
                last = 'sha256 mismatch'
                continue

            done, info, valid = _write_self(dest, blob)
            out['ok'] = valid
            out['updated'] = done
            if not valid:
                # 编译/入口自检没过：一个字节都没写进旧文件，本地继续可用
                out['msg'] = '拒绝更新：%s' % info
                return out
            out['msg'] = ('updated %s -> %s, restart to apply'
                          % (CODE_VERSION, far)) if done else info
            return out
        out['msg'] = last or 'update failed'
        return out
    except Exception as exc:
        out['msg'] = 'error: %s' % exc
        return out

# ============================================================================
# 源 1：影探4K（cms.lyyytv.cn）—— 首页 / 分类 / 搜索 的数据来源
# ============================================================================

class YT4K(object):
    """影探4K。原脚本依赖 requests + pycryptodome，这里改为纯标准库实现。"""

    NAME = '影探'
    HOST = 'http://cms.lyyytv.cn'
    CMS_KEY = 'wP5bvxoc3yv7FoBQENFZuAF0EUYr4LTy'
    PARSE_API = 'http://fys.lyyytv.cn/api/index?appid=10001&videoUrl='
    PARSE_ID_WEB = 5      # 网页线路（腾讯/爱奇艺/芒果/优酷/B站…）
    PARSE_ID_4K = 6       # 4K 直链（ym4kjx 等，站点本身 404，需换链）
    HEADERS = {'User-Agent': 'okhttp/4.12.0'}
    PARSE_HEADERS = {'User-Agent': 'okhttp/4.12.0', 'Accept-Encoding': 'identity'}

    DEC_PREFIX = 'https://baidu.con/'
    PAGE_LIMIT = 20
    HOME_TTL = 6 * 3600
    PLAY_TTL = 600    # 解析出的云盘直链没有时效签名，10 分钟内重播免再问解析站

    FILTER_NAMES = {
        'class': '类型', 'area': '地区', 'lang': '语言', 'year': '年份',
        'letter': '字母', 'by': '排序', 'sort': '顺序',
    }

    _B64_RE = re.compile(r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?')
    _LDMAX_RE = re.compile(r'^https?://ldmax\.cooom/', re.I)
    _4K_HOST_RE = re.compile(
        r'(?:^|\.)(?:ym4kjx|hd4kjx|sd4kjx|mm4kjx|mv4kjx|vk4kjx)\.lyyytv\.cn$', re.I)

    def __init__(self, timeout=7.0):
        self.timeout = timeout

    # ---------- 基础 ----------
    def cms(self, path, params=None, timeout=None, ttl=60):
        query = urllib.parse.urlencode(params or {})
        url = '%s/api.php/app/%s?%s' % (self.HOST, path, query)
        key = 'yt:cms:%s' % url
        cached = cache_get(key)
        if cached is not None:
            return cached
        # 首页给 index_video 的短超时：不传就沿用类默认（7s + 2 次重试）。
        # 短超时只重试 1 次，否则 1.0s 的预算会被重试放大成 2s。
        to = self.timeout if timeout is None else timeout
        data = http_json(url, headers=self.HEADERS, timeout=to,
                         retries=2 if to >= 3 else 1)
        if not isinstance(data, dict) or not data:
            return {}
        code = data.get('code')
        if code is not None:
            try:
                ok = int(code) in (1, 200)
            except (TypeError, ValueError):
                ok = False
            if not ok:
                return {}
        cache_put(key, data, ttl)
        return data

    # ---------- 解密 ----------
    def _unb64(self, value):
        clean = re.sub(r'\s+', '', text(value))
        if not clean or not self._B64_RE.fullmatch(clean):
            return None
        try:
            return base64.b64decode(clean)
        except Exception:
            return None

    def decrypt_lvdou(self, value):
        """lvdou+ 前缀：前 16 字节 key、后 16 字节 iv 的 AES/CBC/PKCS7（AES-128）。"""
        original = text(value)
        if not original.startswith('lvdou+') or not self.CMS_KEY:
            return original
        try:
            encrypted = self._unb64(original[6:])
            if not encrypted:
                return original
            key = self.CMS_KEY[:16].encode('utf-8')
            iv = self.CMS_KEY[16:32].encode('utf-8') if len(self.CMS_KEY) >= 32 else key
            plain = cbc_decrypt(key, iv, encrypted, unpad=True)
            result = plain.decode('utf-8', 'replace').strip()
            if result.startswith('http'):
                return result
        except Exception:
            pass
        return original

    def decrypt_ldmax(self, value, depth=0):
        """老加密：ldmax.cooom 前缀，key = 路径前 16 位反转。"""
        if depth > 5:
            return ''
        url = text(value)
        decoded = self._unb64(url)
        if decoded:
            url = re.sub(r'\s+', '', decoded.decode('utf-8', 'replace'))
        if not self._LDMAX_RE.match(url):
            return url
        path = self._LDMAX_RE.sub('', url)
        if len(path) <= 16:
            return ''
        try:
            key = path[:16][::-1].encode('utf-8')
            encrypted = self._unb64(path[16:])
            if not encrypted or len(encrypted) % 16:
                return ''
            plain = bytearray(cbc_decrypt(key, key, encrypted))
            pad = plain[-1] if plain else 0
            if 0 < pad <= 16:
                del plain[-pad:]
            result = bytes(plain).decode('utf-8', 'replace').strip()
            return self.decrypt_ldmax(result, depth + 1) \
                if self._LDMAX_RE.match(result) else result
        except Exception:
            return ''

    def resolve_parse(self, body):
        """解析响应：JSON 包裹取 url；baidu.con 前缀走 AES；否则视为明文。"""
        body = text(body)
        if not body:
            return ''
        candidate = body
        if body.startswith('{'):
            parsed = loads(body)
            for key in ('url', 'playUrl', 'link'):
                if isinstance(parsed, dict) and parsed.get(key):
                    candidate = text(parsed[key])
                    break
            else:
                inner = as_dict(as_dict(parsed).get('data'))
                for key in ('url', 'playUrl', 'link'):
                    if inner.get(key):
                        candidate = text(inner[key])
                        break
        if not candidate.startswith(self.DEC_PREFIX):
            return candidate

        rest = candidate[len(self.DEC_PREFIX):]
        if len(rest) <= 16:
            return ''
        key = rest[:16].encode('utf-8')
        cipher_b64 = rest[16:]
        try:
            encrypted = base64.b64decode(cipher_b64, validate=False)
            result = cbc_decrypt(key, key, encrypted, unpad=True).decode('utf-8', 'replace').strip()
            if result.startswith('http'):
                return result
        except Exception:
            pass
        try:
            raw = cipher_b64.encode('latin-1', errors='ignore')
            if raw and len(raw) % 16 == 0:
                result = cbc_decrypt(key, key, raw, unpad=True).decode('utf-8', 'replace').strip()
                if result.startswith('http'):
                    return result
        except Exception:
            pass
        return ''

    # 解析站对「解析不了」的地址有两种回法：给空，或者把入参原样回吐
    # （实测 ym4kjx 那批 /d/ty/xxx/01_4K.mp4 GET 回来是
    # {"code":1001,"msg":"解析失败","url":""}，解析站却照抄给我们）。
    # 以前只要回的是 http 就当好使，于是这种「解析失败页」被当成功缓存 120s
    # 交给壳 → 黑屏；聚合层还得先花 0.3s 探测才发现它不是媒体。
    PARSE_TIMEOUT = 5.0
    PARSE_FAIL_TTL = 600
    _PARSE_FAIL = {}
    _PARSE_FAIL_LOCK = threading.Lock()

    @staticmethod
    def same_target(a, b):
        """两个地址是否指向同一资源（忽略 http/https、参数差异）。"""
        try:
            pa, pb = urllib.parse.urlparse(text(a)), urllib.parse.urlparse(text(b))
        except Exception:
            return text(a) == text(b)
        return ((pa.hostname or '') == (pb.hostname or '')
                and (pa.path or '') == (pb.path or ''))

    def parse_url(self, raw, parse_id):
        raw = text(raw)
        if not raw:
            return ''
        try:
            host = (urllib.parse.urlparse(raw).hostname or '').lower()
        except Exception:
            host = ''
        # 平台网页线（腾讯/爱奇艺/芒果/优酷/B站）实测解析站 5/5 全空，
        # 每次点击白等 0.2s；网络抖动时还会把 timeout 拉满。同一个 host
        # 失败过就先记 10 分钟，别再重复问 —— 解析站恢复前问也还是空。
        # 4K 档不记：那批地址时好时坏，记 10 分钟会把能解析的也判死。
        fkey = (host, int(parse_id))
        now = time.time()
        if parse_id == self.PARSE_ID_WEB:
            with self._PARSE_FAIL_LOCK:
                bad = self._PARSE_FAIL.get(fkey)
                if bad and now - bad < self.PARSE_FAIL_TTL:
                    return ''
        target = '%s%s&parsesId=%d' % (
            self.PARSE_API, urllib.parse.quote(raw, safe="!'()*"), parse_id)
        st, txt = http_text(target, headers=self.PARSE_HEADERS,
                            timeout=self.PARSE_TIMEOUT, retries=1)
        resolved = ''
        if st and st < 400 and txt:
            got = self.resolve_parse(txt)
            # 回吐原址 = 服务端自己也解析失败，别当结果
            if got and got.startswith('http') and not self.same_target(got, raw):
                resolved = got
        if not resolved and host and parse_id == self.PARSE_ID_WEB:
            with self._PARSE_FAIL_LOCK:
                _cap_put(self._PARSE_FAIL, fkey, now, 200)
        return resolved

    # ---------- 类型判断 ----------
    def is_4k_source(self, url):
        if not is_url(url):
            return False
        host = (urllib.parse.urlparse(text(url)).hostname or '').lower()
        if host and self._4K_HOST_RE.search(host):
            return True
        return is_media_url(url) and not is_stream_url(url)


    # 影探线路名通常不带分辨率；按线路来源 + 地址特征标注「真实档位」
    # （云线路实测走 4K 解析域名；平台网页线多为解析后的 1080P）
    # 仅当地址落在 4K 解析域，或 CMS 线路名自带 4K 时才标 ·4K
    # 「移动云/联通云」名称本身不代表真 4K（无 ym4kjx 等域时多为高清）
    _RES_4K_HINT = ('4k', 'uhd', '2160')
    _RES_1080_NAMES = (
        '优酷', '爱奇艺', '腾讯', '腾讯视频', '芒果', '芒果TV',
        '哔哩', 'B站', 'bilibili', '搜狐', 'PPTV', '咪咕',
    )
    _RES_CLOUD = ('移动云', '联通云', '天翼云', '电信云', '阿里云', '华为云')

    def annotate_line_name(self, name, sample_url=''):
        """标注分辨率：真 4K 域→4K；网页平台→1080P；云线路无域证→高清。"""
        nm = clean_name(name) or '线路'
        if re.search(r'(?:^|[·\s])(?:4K|2K|1080P?|720P?|480P?|高清)(?:$|[·\s])', nm, re.I):
            return nm
        res = ''
        low = nm.lower()
        su = text(sample_url)
        # 1) 播址命中 4K 域名（ym4kjx/hd4kjx…）才是真 4K
        frags = []
        if su:
            frags.append(su.split('#')[0].split('$')[-1])
            frags.extend(su.replace('#', '$').split('$')[:4])
        for frag in frags:
            if frag and self.is_4k_source(frag):
                res = '4K'
                break
        # 2) CMS 自带 4K(BD)/4K(YD) 等
        if not res and any(h in low for h in self._RES_4K_HINT):
            res = '4K'
        # 3) 网页平台 → 1080P（假 4K 高发区）
        if not res:
            for k in self._RES_1080_NAMES:
                if k in nm:
                    res = '1080P'
                    break
        # 4) 运营商云线：有 4K 域已在上面标 4K；无证据不强制改名（避免「高清」降级观感）
        #    分季 BD（绝命毒师等）player 名常为 移动云/天翼云，详情 URL 多为 ym4kjx
        if not res:
            return nm
        return clean_name('%s·%s' % (nm, res)) or nm

    # ---------- 列表 ----------
    @staticmethod
    def _paginate(data, page):
        lst = as_list(data.get('list'))
        try:
            limit = int(data.get('limit') or 0)
        except (TypeError, ValueError):
            limit = 0
        if limit <= 0:
            limit = YT4K.PAGE_LIMIT
        try:
            pagecount = int(data.get('pagecount') or 0)
        except (TypeError, ValueError):
            pagecount = 0
        if pagecount <= 0:
            pagecount = page + (1 if len(lst) >= limit else 0)
        try:
            total = int(data.get('total'))
        except (TypeError, ValueError):
            total = (page - 1) * limit + len(lst) + (1 if pagecount > page else 0)
        return {'list': lst, 'page': page, 'pagecount': pagecount,
                'limit': limit, 'total': total}

    def home(self):
        def build():
            data = self.cms('nav', {'token': ''})
            classes, filters = [], {}
            for item in as_list(data.get('list')):
                if not isinstance(item, dict):
                    continue
                if item.get('type_id') is None or not text(item.get('type_name')):
                    continue
                tid = text(item['type_id'])
                classes.append({'type_id': tid, 'type_name': text(item['type_name'])})
                ext = as_dict(item.get('type_extend'))
                groups = []
                for key, name in self.FILTER_NAMES.items():
                    values = [v for v in (text(x) for x in text(ext.get(key)).split(',')) if v]
                    values = list(dict.fromkeys(values))
                    if values:
                        groups.append({
                            'key': key, 'name': name, 'init': '',
                            'value': [{'n': '全部', 'v': ''}] +
                                     [{'n': v, 'v': v} for v in values],
                        })
                if groups:
                    filters[tid] = groups
            return {'class': classes, 'filters': filters} if classes else {}
        got = http_cached('yt:nav', self.HOME_TTL, build)
        return got or {'class': [], 'filters': {}}

    def home_vod(self, timeout=None):
        def build():
            data = self.cms('index_video', {'token': ''}, timeout=timeout, ttl=600)
            vlist = []
            for item in as_list(data.get('list')):
                if isinstance(item, dict):
                    vlist.extend(as_list(item.get('vlist')))
            return {'list': vlist} if vlist else {}
        got = http_cached('yt:index', 600, build)
        return got or {'list': []}

    def category(self, tid, pg, extend):
        page = page_of(pg)
        tid = text(tid)
        if not tid:
            return {'list': [], 'page': page, 'pagecount': 0, 'limit': self.PAGE_LIMIT,
                    'total': 0}
        ext = extend if isinstance(extend, dict) else loads(extend)
        params = {'tid': tid, 'pg': str(page), 'limit': '18'}
        for key in self.FILTER_NAMES:
            value = text(as_dict(ext).get(key))
            if value and value != 'all':
                params[key] = value
        data = self.cms('video', params)
        return self._paginate(data, page)

    def search(self, key, pg):
        wd = text(key)
        page = page_of(pg)
        if not wd:
            return {'list': [], 'page': page, 'pagecount': 0, 'limit': self.PAGE_LIMIT,
                    'total': 0}
        data = self.cms('search', {'text': wd, 'pg': str(page)})
        lst = [dict((k, v) for k, v in item.items() if k != 'type')
               for item in as_list(data.get('list')) if isinstance(item, dict)]
        # 可播性排序：分季/4K/BD 靠前，避免「绝命毒师」合集仅 youku 抢第一
        def _sk(it):
            n = str(it.get('vod_name') or '')
            r = str(it.get('vod_remarks') or '')
            blob = n + ' ' + r
            s = 0
            if re.search(r'第.+季|season\s*\d+|s\d{1,2}', n, re.I):
                s += 20
            if '4K' in blob or '4k' in blob:
                s += 15
            if 'BD' in blob or '蓝光' in blob:
                s += 8
            if '全季' in n or '合集' in n:
                s -= 5
            if '电影' in n:
                s += 2
            return -s
        try:
            lst.sort(key=_sk)
        except Exception:
            pass
        data['list'] = lst
        return self._paginate(data, page)

    # ---------- 详情 ----------
    def playlist(self, value):
        parts = []
        for entry in text(value).split('#'):
            sep = entry.find('$')
            if sep <= 0 or not text(entry[sep + 1:]):
                continue
            parts.append('%s$%s' % (text(entry[:sep]), self.decrypt_lvdou(entry[sep + 1:])))
        return '#'.join(parts)

    def detail(self, vid):
        vid = text(vid)
        if not vid:
            return {}
        data = as_dict(self.cms('video_detail', {'id': vid}).get('data'))
        if not data:
            return {}
        players = data.get('vod_url_with_player')
        vod = dict((k, v) for k, v in data.items() if k != 'vod_url_with_player')
        names = text(vod.get('vod_play_from')).split('$$$')
        if isinstance(players, list):
            sources = players
        else:
            sources = [
                {'name': names[i] if i < len(names) else '', 'url': u}
                for i, u in enumerate(text(vod.get('vod_play_url')).split('$$$'))
            ]
        froms, urls = [], []
        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                continue
            url = self.playlist(source.get('url'))
            if not url:
                continue
            name = text(source.get('name')) or text(source.get('code')) or '线路%d' % (index + 1)
            # 标注真实分辨率档位（云线 4K / 平台线 1080P）
            name = self.annotate_line_name(name, url)
            froms.append(clean_name(name))
            urls.append(url)
        vod['vod_play_from'] = '$$$'.join(froms)
        vod['vod_play_url'] = '$$$'.join(urls)
        return vod

    # ---------- 播放 ----------
    def play(self, play_id):
        original = self.decrypt_lvdou(play_id)
        if not original:
            return {'parse': 0, 'url': '', 'header': dict(self.PARSE_HEADERS)}
        if self._LDMAX_RE.match(original):
            decrypted = self.decrypt_ldmax(original)
            if decrypted:
                original = decrypted

        cache_key = 'yt:play:%s' % original
        cached = cache_get(cache_key)
        if cached:
            return {'parse': 0, 'url': cached, 'header': dict(self.PARSE_HEADERS)}

        if self.is_4k_source(original):
            resolved = self.parse_url(original, self.PARSE_ID_4K) or ''
            # 解析失败时是否回落原址，看原址是什么：
            #   - ym4kjx/hd4kjx 那批「/d/ty/…/01_4K.mp4」是站点的 4K 解析页，
            #     不是媒体文件（GET 回来就是 {"code":1001,"msg":"解析失败"}），
            #     回落等于把一张错误 JSON 页交给壳 —— 黑屏，而且聚合层还得先花
            #     0.3s 探测才发现。这种情况留空，让聚合层立刻换源。
            #   - 其它真媒体直链（.mp4/.mkv 且不在解析域）仍回落，壳能直连。
            try:
                host = (urllib.parse.urlparse(original).hostname or '').lower()
            except Exception:
                host = ''
            if not resolved and not (host and self._4K_HOST_RE.search(host)):
                resolved = original
        elif is_stream_url(original):
            resolved = original
        else:
            resolved = self.parse_url(original, self.PARSE_ID_WEB) or ''
            if not resolved and is_media_url(original):
                resolved = original
            # 网页源解析失败时给壳 parse=1 兜底
            if not resolved and is_url(original):
                return {'parse': 1, 'jx': 0, 'url': original,
                        'header': dict(self.PARSE_HEADERS)}

        if resolved:
            cache_put(cache_key, resolved, self.PLAY_TTL)
        return {'parse': 0, 'url': resolved or '', 'header': dict(self.PARSE_HEADERS)}

# ============================================================================
# 源 2 / 3：咕噜咕噜 + 橘汁4K（同一 T3 后端的两套客户端 profile）
#   传输：ECDH(secp256r1) 握手 → HKDF("v2-session") → AES-256-GCM + raw-deflate
#   协议：protobuf 裸编码；m=61 搜索 / m=62 详情 / m=69 服务器代理解析
# ============================================================================

T3_HOST_HEADER = '103.45.132.22:19987'
T3_BASE = 'http://103.45.132.22:19987/app/bn/v2'

# 线路显示名兜底（后端 f75 只给 code 时用）
T3_LINE_NAMES = {
    'dyttm3u8': '电影天堂', 'bfzym3u8': '暴风资源', 'lzm3u8': '量子资源',
    'ffm3u8': '非凡资源', 'qq': '腾讯视频', 'qiyi': '爱奇艺', 'youku': '优酷',
    'mgtv': '芒果TV', 'newxfyun': '咕噜4K', 'xfyun': '咕噜4K二线',
    'CO4K': '咖啡4K超清', 'jplink': '金牌极速', 'rose': '玫瑰4K',
    'NBY': '蚂蚁资源', 'qsvip': '旋风VIP', 'qingshan': '青山资源',
    'JD4K': '鲸宝4K', 'iyf4k': '爱壹帆4K',
}

T3_PROFILES = {
    'gg': {
        'label': '咕噜',
        'ua': 'Dart/3.10 (dart:io)',
        'app_name': '咕噜咕噜', 'version': '2.2.5', 'package': 'com.himrsc.viz',
        'signature': '32E0AB4FF93A29CE0E6F0BFB01F2F1B788E76262731F3F30F509CB822428ED58',
        'build': '20109',
        'device_build': 'pangu-build-component-system-513739-s9vkd-rlxnj-p3rhm',
        'sort': 'vod_hits_month',
        'boot': 'gg',
        'detail': 'gg',
    },
    'jz': {
        'label': '橘汁',
        'ua': 'Dalvik/2.1.0 (Linux; U; Android 11; Pixel 4)',
        'app_name': '咕噜咕噜', 'version': '2.1.2', 'package': 'com.jymqfh.xee',
        'signature': '', 'build': '212',
        'device_build': 'unknown',
        'sort': 'vod_hits_week',
        'boot': 'jz',
        'detail': 'jz',
    },
}


class T3Client(object):
    """T3 私有协议客户端（每个 profile 独立会话）。"""

    def __init__(self, profile, timeout=12.0):
        self.p = profile
        self.timeout = timeout
        self.session_id = ''
        self.key = b''
        self.device_id = secrets.token_hex(8)
        self.request_id = 0
        self.players = {}
        self.parsers = {}
        self.booted = False
        self.lock = threading.RLock()

    # ---------- 传输 ----------
    def _post(self, body, extra=None):
        headers = {
            'User-Agent': self.p['ua'],
            'Content-Type': 'application/x-protobuf',
            'Accept-Encoding': 'gzip',
            'Host': T3_HOST_HEADER,
        }
        if extra:
            headers.update(extra)
        st, data = http(T3_BASE, 'POST', headers, body,
                        timeout=self.timeout, retries=1)
        if not data:
            raise RuntimeError('empty response (status %s)' % st)
        try:
            return gzip.decompress(data) if data[:2] == b'\x1f\x8b' else data
        except Exception:
            return data

    # ---------- 握手 ----------
    def handshake(self):
        priv, pub = ecdh_keypair()
        caps = pb_var(1, 1) + pb_var(2, 0) + pb_var(3, 1)
        request = pb_bytes(1, pub) + pb_bytes(2, b'1.0.0') + pb_bytes(3, caps)
        hk = secrets.token_hex(16)
        iv = secrets.token_bytes(16)
        body = base64.b64encode(iv + cbc_encrypt(hk.encode('ascii'), iv,
                                                zlib.compress(request, 4)))
        content = self._post(body, {'x-handshake-key': hk})
        raw = base64.b64decode(content)
        plain = zlib.decompress(cbc_decrypt(hk.encode('ascii'), raw[:16], raw[16:],
                                            unpad=True))
        sid = pb_field(plain, 1, 2)
        server_pub = pb_field(plain, 2, 2)
        if not sid or not server_pub:
            raise RuntimeError('bad handshake response')
        self.session_id = sid.decode('ascii', 'replace')
        shared = ecdh_shared_x(priv, server_pub)
        prk = hmac.new(self.session_id.encode('ascii'), shared, hashlib.sha256).digest()
        self.key = hmac.new(prk, b'v2-session\x01', hashlib.sha256).digest()
        self.request_id = 0

    # ---------- 请求 ----------
    def request(self, method, payload=b'', scope=3):
        with self.lock:
            if not self.session_id:
                self.handshake()
            self.request_id += 1
            rid = self.request_id
            core = (pb_var(1, rid) + pb_var(2, scope) + pb_var(3, method)
                    + pb_bytes(4, self.device_id.encode('ascii'))
                    + pb_bytes(5, b'') + pb_bytes(6, payload)
                    + pb_var(7, int(time.time() * 1000)))
            nonce = secrets.token_bytes(12)
            ciphertext, tag = gcm_encrypt(self.key, nonce, raw_deflate(core))
            body = pb_var(1, rid) + pb_bytes(2, nonce + ciphertext + tag)
            content = self._post(body, {'x-session-id': self.session_id,
                                        'x-player-page-protection': '1'})
            enc = pb_field(content, 2, 2)
            if enc is None or len(enc) < 28:
                err = pb_str(content, 3)
                raise RuntimeError(err or 'request rejected')
            plain = raw_inflate(gcm_decrypt(self.key, enc[:12], enc[12:-16], enc[-16:]))
            status = pb_str(plain, 3)
            if status and status not in ('ok', 'success'):
                raise RuntimeError(status)
            return plain

    # ---------- Boot ----------
    def boot(self):
        p = self.p
        now_us = int(time.time() * 1_000_000)
        aid = self.device_id
        if p['boot'] == 'gg':
            app = (pb_bytes(1, p['app_name']) + pb_bytes(2, p['version'])
                   + pb_bytes(3, p['package']) + pb_bytes(4, p['signature'])
                   + pb_bytes(5, p['build']) + pb_var(6, now_us) + pb_var(7, now_us))
            device = (pb_bytes(1, aid) + pb_var(2, 1) + pb_bytes(3, '15')
                      + pb_bytes(4, 'Redmi K50 Ultra')
                      + pb_bytes(5, 'Redmi/diting/diting:15/AQ3A.240912.001/'
                                    'OS2.0.215.0.VOACNXM:user/release-keys')
                      + pb_bytes(6, 'Redmi') + pb_bytes(7, 'qcom')
                      + pb_var(8, 0) + pb_bytes(9, 'unknown')
                      + pb_bytes(10, p['device_build'])
                      + pb_var(11, 0) + pb_var(12, 35))
            payload = (pb_bytes(1, 'v2') + pb_bytes(2, 'android') + pb_bytes(3, 'gulu')
                       + pb_bytes(4, app) + pb_bytes(5, device))
            response = self.request(0, payload, scope=1)
        else:
            info = (pb_bytes(1, p['app_name']) + pb_bytes(2, p['version'])
                    + pb_bytes(3, p['package']) + pb_bytes(4, aid)
                    + pb_bytes(5, p['build']))
            state = (pb_bytes(1, aid) + pb_var(2, 0) + pb_bytes(3, '11')
                     + pb_bytes(4, 'Pixel 4')
                     + pb_bytes(5, 'google/redfin/redfin:11/RQ3A.211001.001')
                     + pb_bytes(6, 'google') + pb_bytes(7, 'redfin')
                     + pb_var(8, 0) + pb_bytes(9, 'unknown')
                     + pb_bytes(10, p['device_build'])
                     + pb_var(11, 0) + pb_var(12, 30))
            payload = (pb_bytes(1, 'v1') + pb_bytes(2, 'Android 11') + pb_bytes(3, 'gulu')
                       + pb_bytes(4, info) + pb_bytes(5, state))
            response = self.request(0, payload, scope=1)

        config = pb_field(response, 4, 2)
        players, parsers = {}, {}
        if config:
            for item in pb_fields(config, 4, 2):
                code = pb_str(item, 3)
                if not code:
                    continue
                parser_ids = []
                for packed in pb_fields(item, 8, 2):
                    try:
                        pos = 0
                        while pos < len(packed):
                            val, pos = pb_read_varint(packed, pos)
                            parser_ids.append(val)
                    except Exception:
                        pass
                players[code] = {
                    'id': pb_field(item, 1, 0) or 0,
                    'name': pb_str(item, 4),
                    'parser_ids': parser_ids,
                }
            for item in pb_fields(config, 7, 2):
                pid = pb_field(item, 1, 0) or 0
                if pid:
                    parsers[pid] = {
                        'name': pb_str(item, 2),
                        'url': pb_str(item, 3),
                        'mode': pb_str(item, 4),
                        'result_key': pb_str(item, 10) or 'url',
                        'server': bool(pb_field(item, 20, 0) or 0),
                    }
        self.players = players
        self.parsers = parsers
        self.booted = bool(response)

    def ensure(self):
        if self.booted and self.key:
            return
        if not self.session_id:
            self.handshake()
        if not self.booted:
            self.boot()

    def reset(self):
        self.session_id = ''
        self.key = b''
        self.request_id = 0
        self.booted = False

    # ---------- 业务 ----------
    def search(self, keyword, page=1, limit=21):
        p = self.p
        if p['boot'] == 'gg':
            filters = pb_bytes(18, p['sort'].encode('utf-8')) + pb_var(19, 1)
            payload = (pb_bytes(1, keyword) + pb_var(2, page) + pb_var(3, limit)
                       + pb_bytes(5, filters))
        else:
            filters = pb_var(1, 1) + pb_var(2, 0) + pb_bytes(3, p['sort'].encode('utf-8'))
            payload = (pb_bytes(1, keyword) + pb_var(2, page) + pb_var(3, limit)
                       + pb_bytes(5, filters))
        response = self.request(61, payload)
        data = pb_field(response, 4, 2)
        videos = []
        if data:
            for item in pb_fields(data, 1, 2):
                videos.append({
                    'vod_id': str(pb_field(item, 1, 0) or ''),
                    'vod_name': pb_str(item, 3),
                    'vod_pic': pb_str(item, 6),
                    'vod_remarks': pb_str(item, 11) or pb_str(item, 9),
                })
        info = pb_field(data, 2, 2) if data else None
        page_no = (pb_field(info, 1, 0) or page) if info else page
        pagecount = (pb_field(info, 3, 0) or 1) if info else 1
        total = (pb_field(info, 4, 0) or len(videos)) if info else len(videos)
        return {'list': [v for v in videos if v['vod_id'] and v['vod_name']],
                'page': page_no, 'pagecount': pagecount, 'total': total}

    def detail(self, vod_id):
        p = self.p
        try:
            vid = int(str(vod_id).strip())
        except (TypeError, ValueError):
            return {}
        if p['detail'] == 'gg':
            payload = (pb_var(1, vid) + pb_bytes(3, p['version'].encode('utf-8'))
                       + pb_bytes(4, b'1') + pb_var(5, 1))
        else:
            payload = (pb_var(1, vid) + pb_bytes(4, b'APP_PLATFORM_ANDROID_TV')
                       + pb_var(5, 0))
        response = self.request(62, payload)
        data = pb_field(response, 4, 2)
        if not data:
            return {}
        name = pb_str(data, 5)
        if not name or name.startswith('最新版本下载地址'):
            return {}
        blob = ' '.join([pb_str(data, f) for f in (5, 13, 21)]
                        + [pb_str(src, 1) for src in pb_fields(data, 75, 2)]).lower()
        if 'glgl.tv' in blob or 'shu.jpg' in blob or '__v99_' in blob:
            return {}
        lines = []
        for src in pb_fields(data, 75, 2):
            code = pb_str(src, 1)
            if not code or code.startswith('__v99_'):
                continue
            cfg = self.players.get(code) or {}
            eps = []
            for ep in pb_fields(src, 2, 2):
                ep_id = pb_str(ep, 3)
                if not ep_id:
                    continue
                idx = pb_field(ep, 1, 0) or (len(eps) + 1)
                eps.append('%s$%s' % (clean_name(pb_str(ep, 4) or '第%s集' % idx), ep_id))
            if not eps:
                continue
            parser_ids = cfg.get('parser_ids') or [0]
            lines.append({
                'name': clean_name(cfg.get('name') or T3_LINE_NAMES.get(code) or code),
                'parser_id': parser_ids[0] if parser_ids else 0,
                'eps': eps,
                'code': code,
            })
        return {
            'vod_id': str(pb_field(data, 1, 0) or vod_id),
            'vod_name': name,
            'vod_pic': pb_str(data, 13),
            'vod_remarks': pb_str(data, 22),
            'vod_content': pb_str(data, 21),
            'vod_area': pb_str(data, 28),
            'vod_year': pb_str(data, 30),
            'lines': lines,
        }

    def play(self, parser_id, play_id):
        payload = pb_var(1, int(parser_id)) + pb_bytes(2, play_id)
        response = self.request(69, payload)
        data = pb_field(response, 4, 2)
        return pb_str(data, 2) if data else ''


class T3Source(object):
    """线路源包装：搜索 / 详情 / 播放，带一次会话重建重试。"""

    def __init__(self, tag, timeout=12.0):
        self.tag = tag
        self.p = T3_PROFILES[tag]
        self.label = self.p['label']
        self.client = T3Client(self.p, timeout)

    def _call(self, fn, *args, **kwargs):
        try:
            self.client.ensure()
            return fn(*args, **kwargs)
        except Exception:
            try:
                self.client.reset()
                self.client.ensure()
                return fn(*args, **kwargs)
            except Exception:
                return None

    def search(self, keyword, page=1):
        cache_key = 't3:%s:q:%s|%s' % (self.tag, text(keyword), page)
        hit = cache_get(cache_key)
        if hit is not None:
            return hit
        got = self._call(self.client.search, keyword, page)
        items = as_list((got or {}).get('list'))
        if items:
            cache_put(cache_key, items, 600)
        return items

    def detail(self, vod_id):
        return self._call(self.client.detail, vod_id) or {}

    def play(self, parser_id, play_id, parser_hint=''):
        play_id = text(play_id)
        if is_media_url(play_id) or play_id.startswith('m.php') or '?data=' in play_id:
            return play_id
        url = self._call(self.client.play, parser_id, play_id) or ''
        if url:
            return url
        # 兜底：走 boot 下发的解析接口（部分线路 server=False，需外部转链）
        parser = self.client.parsers.get(int(parser_id or 0)) or {}
        api = text(parser.get('url'))
        if api:
            target = api.replace('{url}', urllib.parse.quote(play_id, safe='')) \
                if '{url}' in api else api + urllib.parse.quote(play_id, safe='')
            st, txt = http_text(target, headers={'User-Agent': self.p['ua']},
                                timeout=15, retries=1)
            if st and st < 400 and txt:
                payload = loads(txt)
                found = self._dig(payload, parser.get('result_key') or 'url')
                if found:
                    return found
        return ''

    @classmethod
    def _dig(cls, value, preferred='url'):
        if isinstance(value, str):
            return value if is_media_url(value) or value.startswith('http') else ''
        if isinstance(value, dict):
            for key in (preferred, 'url', 'play_url', 'playUrl', 'm3u8', 'data'):
                if key in value:
                    got = cls._dig(value[key], preferred)
                    if got:
                        return got
            for item in value.values():
                got = cls._dig(item, preferred)
                if got:
                    return got
        elif isinstance(value, (list, tuple)):
            for item in value:
                got = cls._dig(item, preferred)
                if got:
                    return got
        return ''

# ============================================================================
# 源 4：找剧AI（zhaoju4.com）—— HMAC 签名的 REST，官方线路需登录态
# ============================================================================

class ZJSource(object):
    NAME = '找剧'
    HOST = 'https://zhaoju4.com'
    SIGN_KEY = '8f18c8e472a9fefbab7108f5c447f69b48a4b5d34f662ed83163167fc10fb3b8'
    UA = UA_WEB
    CLIENT_NAME = 'movie-search-frontend'
    CLIENT_VERSION = '1.0.0'
    BUILD_VERSION = '20261021T204524Z-98df10a3f414-98df10a3f414-98df10a3f414'
    PROTOCOL_VERSION = '2026-07-05.library-v2.playback-v1'
    PAGE_SIZE = 18
    MAX_LINES = 4
    MAX_PREMIUM = 4
    MAX_EPISODES = 120
    TIMEOUT = 12.0
    CACHE_TTL = 300
    PROBE_BYTES = 32768
    PROBE_TTL = 600

    PREMIUM = ('bytedance', 'bytevod-lv2', 'bytevod-lv3', 'bytevod-lv5',
               'bytevod-cloudflare', 'bytevod-cloudflare-4k',
               'official-v', 'official-r', 'dong')
    EXT_HOSTS = ('v.qq.com', 'qq.com', 'youku.com', 'iqiyi.com', 'bilibili.com',
                 'mgtv.com', 'sohu.com', 'pptv.com', 'le.com', 'wasu.cn',
                 'tudou.com', '1905.com')
    VIDEO_EXTS = ('.m3u8', '.mp4', '.mkv', '.flv', '.avi', '.ts',
                  '.mov', '.m4v', '.webm', '.wmv', '.rmvb', '.mpd')

    PATH_BROWSE = '/v1/browse/catalog'
    PATH_DETAIL = '/v1/catalog/%s/detail'
    PATH_EPISODES = '/v1/catalog/%s/episodes'
    PATH_RESOLVE = '/v1/playback/resolve/%s'
    PATH_RESOLVE_LINE = '/v1/playback/resolve-line?view=compact'
    PATH_SUGGEST = '/v1/suggest'

    def __init__(self, cookie='', timeout=None):
        self.cookie = cookie or self._load_cookie()
        self.timeout = timeout or self.TIMEOUT
        self._sess_ok = False
        self._sess_checked = False
        self._sess_at = 0
        self._anon_at = 0
        self._anon_id = 'anon_' + uuid.uuid4().hex
        self._probe = {}
        # 会话检测（/v1/users/me）实测要 0.5~3.5s，且站点会随机 503。
        # 放到后台预热，详情里最多等 1.2s，不拖累其他三个源。
        self._sess_thread = threading.Thread(target=self._ensure_session, daemon=True)
        self._sess_thread.start()

    def _await_session(self, timeout=1.2):
        th = getattr(self, '_sess_thread', None)
        if th is not None and th.is_alive():
            th.join(max(0.05, timeout))
        return self._sess_ok

    # ---------- 会话 ----------
    @staticmethod
    def _cookie_file():
        try:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '.zhaoju_guest_cookie')
        except Exception:
            return ''

    def _load_cookie(self):
        path = self._cookie_file()
        try:
            if path and os.path.isfile(path):
                with open(path, 'r', encoding='utf-8') as fh:
                    saved = fh.read().strip()
                if 'ai_movie_session=' in saved:
                    return saved
        except Exception:
            pass
        return ''

    def _save_cookie(self):
        path = self._cookie_file()
        if not path or 'ai_movie_session=' not in (self.cookie or ''):
            return
        try:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(self.cookie)
            _chmod600(path)      # 会话 cookie 明文，只给自己读
        except Exception:
            pass

    def _merge_cookie(self, set_cookies):
        jar = {}
        for part in str(self.cookie or '').split(';'):
            if '=' in part:
                k, v = part.split('=', 1)
                jar[k.strip()] = v.strip()
        for raw in set_cookies or []:
            first = str(raw).split(';', 1)[0]
            if '=' in first:
                k, v = first.split('=', 1)
                if v.strip():
                    jar[k.strip()] = v.strip()
        self.cookie = '; '.join('%s=%s' % (k, v) for k, v in jar.items() if v)

    # ---------- 签名与请求 ----------
    def _sign(self, method, path_query):
        u = urllib.parse.urlsplit(path_query)
        path = u.path or '/'
        search = ('?' + u.query) if u.query else ''
        ts = str(int(time.time() * 1000))
        nonce = uuid.uuid4().hex
        msg = '%s\n%s%s\n%s\n%s' % (method, path, search, ts, nonce)
        sig = hmac.new(self.SIGN_KEY.encode('utf-8'), msg.encode('utf-8'),
                       hashlib.sha256).hexdigest()
        return ts, nonce, sig

    def _headers(self, method, path_query, with_cookie=True):
        h = {
            'User-Agent': self.UA,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': self.HOST + '/',
            'x-platform': 'web',
            'x-requested-with': 'XMLHttpRequest',
            'x-ai-movie-client-name': self.CLIENT_NAME,
            'x-ai-movie-client-version': self.CLIENT_VERSION,
            'x-ai-movie-build-version': self.BUILD_VERSION,
            'x-ai-movie-protocol-version': self.PROTOCOL_VERSION,
        }
        if with_cookie and self.cookie:
            h['Cookie'] = self.cookie
        if path_query.startswith('/v1/'):
            ts, nonce, sig = self._sign(method, path_query)
            h['x-ai-movie-timestamp'] = ts
            h['x-ai-movie-nonce'] = nonce
            h['x-ai-movie-signature'] = sig
        return h

    def _req(self, path, params=None, method='GET', body=None, with_cookie=True,
             attempts=3):
        """返回 (status, json)。503/空响应自动重试 —— 站点约 30% 概率返回 503。"""
        url = path
        if params:
            clean = dict((k, v) for k, v in params.items() if v not in (None, ''))
            if clean:
                url += ('&' if '?' in url else '?') + urllib.parse.urlencode(clean)
        full = self.HOST + url
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode('utf-8')
        headers = self._headers(method, url, with_cookie)
        if data is not None:
            headers['Content-Type'] = 'application/json; charset=utf-8'
        parsed = {}
        for attempt in range(max(1, int(attempts))):
            if attempt:
                time.sleep(0.1 * attempt)
            st, txt = http_text(full, method, headers, data,
                                timeout=self.timeout, retries=1)
            if st and 200 <= st < 300 and txt:
                parsed = loads(txt)
                if parsed:
                    return st, parsed
                continue
            if st in (401, 403):
                return st, {}
        return 0, parsed

    # ---------- 会话可用性 ----------
    def _ensure_session(self):
        now = time.time()
        if self._sess_checked and now - self._sess_at < 600:
            return self._sess_ok
        ok = True
        st, _ = self._req('/v1/users/me', attempts=1)
        if st in (401, 403):
            ok = False
        if not ok and now - self._anon_at > 300:
            self._anon_at = now
            st2, d2 = self._req('/v1/users/anonymous', method='POST',
                                body={'anonymous_id': self._anon_id},
                                with_cookie=False, attempts=1)
            if st2 and 200 <= st2 < 300:
                ok = True
        self._sess_ok = ok
        self._sess_checked = True
        self._sess_at = now
        return ok

    # ---------- 工具 ----------
    @staticmethod
    def _pick(obj, *keys, **kw):
        default = kw.get('default', '')
        if not isinstance(obj, dict):
            return default
        for key in keys:
            got = obj.get(key)
            if got not in (None, '', [], {}):
                return got
        return default

    @staticmethod
    def _join(value):
        if isinstance(value, (list, tuple)):
            return ','.join([str(x).strip() for x in value if str(x).strip()])
        return text(value)

    def _card(self, item):
        if not isinstance(item, dict):
            return None
        vid = text(self._pick(item, 'id', 'variant_id', 'selected_variant_id'))
        if not vid:
            return None
        avail = as_dict(item.get('availability'))
        remarks = text(self._pick(item, 'remarks', 'episode_progress_text')) \
            or text(avail.get('label'))
        return {
            'vod_id': vid,
            'vod_name': text(self._pick(item, 'title', 'name', 'normalized_title')),
            'vod_pic': text(self._pick(item, 'poster_url', 'poster', 'pic', 'cover')),
            'vod_remarks': remarks,
            'vod_year': text(self._pick(item, 'year')),
            'vod_area': text(self._pick(item, 'area')),
            'vod_actor': self._join(self._pick(item, 'actors', 'actor', default=[])),
            'vod_director': self._join(self._pick(item, 'directors', default=[])),
            'vod_content': text(self._pick(item, 'description', 'intro')),
            'vod_score': text(self._pick(item, 'rating', 'score')),
        }

    def _cards(self, items):
        out = []
        for it in as_list(items):
            card = self._card(it)
            if card:
                out.append(card)
        return out

    @staticmethod
    def _valid_url(url):
        s = text(url)
        if not s.startswith('http'):
            return False
        path = urllib.parse.urlsplit(s).path.lower()
        if path.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg')):
            return False
        if '~tplv-' in path and 'image' in path:
            return False
        return True

    def _is_ext(self, url):
        try:
            host = urllib.parse.urlsplit(text(url)).netloc.lower()
            return any(host == h or host.endswith('.' + h) for h in self.EXT_HOSTS)
        except Exception:
            return False

    # ---------- 列表 ----------
    def search(self, keyword, page=1):
        wd = text(keyword)
        if not wd:
            return []
        page = max(1, int(page or 1))
        cache_key = 'zj:q:%s|%s' % (wd, page)
        hit = cache_get(cache_key)
        if hit is not None:
            return hit
        st, data = self._req(self.PATH_BROWSE, {
            'q': wd, 'page': page, 'limit': self.PAGE_SIZE,
            'offset': (page - 1) * self.PAGE_SIZE,
        })
        cards = as_list(as_dict(data).get('cards'))
        out = []
        for it in cards:
            avail = as_dict(it.get('availability'))
            if avail.get('playable') is False or avail.get('disabled') is True:
                continue
            out.append(it)
        cards_out = self._cards(out)
        if cards_out or page > 1:
            if cards_out:
                cache_put(cache_key, cards_out, 600)
            return cards_out
        # 直搜无结果 → 联想词兜底
        st, sug = self._req('/v1/suggest', {'q': wd, 'limit': 10, 'mode': 'home'})
        out = []
        for s in as_list(as_dict(sug).get('suggestions')):
            target = as_dict(s.get('target'))
            vid = text(target.get('variant_id'))
            if not vid:
                continue
            out.append({
                'vod_id': vid,
                'vod_name': text(s.get('label') or target.get('title')),
                'vod_pic': '',
                'vod_remarks': text(s.get('subtitle')),
            })
        return out

    # ---------- 详情 ----------
    def _episodes(self, vid):
        out, seen, offset = [], set(), 0
        while len(out) < self.MAX_EPISODES:
            path = self.PATH_EPISODES % urllib.parse.quote(str(vid), safe='')
            st, data = self._req(path, {'limit': 48, 'offset': offset})
            eps = as_list(as_dict(data).get('episodes'))
            if not eps:
                break
            added = 0
            for e in eps:
                if not isinstance(e, dict):
                    continue
                tok = text(e.get('token'))
                if not tok or tok in seen:
                    continue
                seen.add(tok)
                num = e.get('number')
                out.append({'token': tok, 'title': text(e.get('title')),
                            'number': num if isinstance(num, int) else None,
                            'track': text(e.get('episode_track'))})
                added += 1
            pg = as_dict(data.get('episode_pagination'))
            if not pg.get('has_more') or not added:
                break
            offset += len(eps)
        # 主线按集数排，其余（花絮等）排后面
        main = sorted([e for e in out if e.get('track') == 'main'],
                      key=lambda e: e['number'] if isinstance(e.get('number'), int) else (1 << 30))
        rest = [e for e in out if e.get('track') != 'main']
        return main + rest

    def _resolve(self, token):
        tok = text(token)
        if not tok:
            return {}
        key = 'zj:rv:%s' % tok
        hit = cache_get(key)
        if hit is not None:
            return hit
        path = self.PATH_RESOLVE % urllib.parse.quote(tok, safe='')
        st, data = self._req(path, {'view': 'compact'})
        if isinstance(data, dict) and data.get('line_options'):
            cache_put(key, data, self.CACHE_TTL)
        return data if isinstance(data, dict) else {}

    def _resolve_line(self, ticket):
        t = text(ticket)
        if t.startswith('resolve://'):
            t = t[len('resolve://'):]
        if not t:
            return {}
        key = 'zj:tk:%s' % t
        hit = cache_get(key)
        if hit is not None:
            return hit
        st, data = self._req(self.PATH_RESOLVE_LINE, method='POST', body={'ticket': t})
        line = as_dict(as_dict(data).get('line'))
        if not line and st in (401, 403):
            line = {'_error': 'need_login'}
        if line:
            cache_put(key, line, self.CACHE_TTL)
        return line

    # ---------- 线路 ----------
    @staticmethod
    def _opt_direct(o):
        return (ZJSource._valid_url(o.get('url'))
                and not bool(o.get('resolve_required'))
                and text(o.get('url_kind')) != 'resolve_ticket')

    @staticmethod
    def _opt_ticket(o):
        return bool(o.get('resolve_required')) or text(o.get('url')).startswith('resolve://')

    @staticmethod
    def _weight(o):
        try:
            return float(o.get('preference_weight') or 0)
        except Exception:
            return 0.0

    @staticmethod
    def _line_key(o):
        return (text(o.get('provider_id')), text(o.get('play_from')))

    @staticmethod
    def _line_label(o):
        s = text(o.get('label') or o.get('provider_id') or o.get('play_from') or '线路')
        for ch in ('$', '#', '|'):
            s = s.replace(ch, ' ')
        return re.sub(r'\s+', ' ', s).strip() or '线路'

    def _premium(self, o):
        label = text(o.get('label')).upper()
        pid = text(o.get('provider_id'))
        return (bool(o.get('resolve_required')) or text(o.get('url')).startswith('resolve://')
                ) and (pid in self.PREMIUM or '4K' in label or '1080P' in label
                       or '官方' in text(o.get('label')))

    def _speed(self, url):
        """实测直链首段速度（KB/s），0 = 不可用。"""
        key = text(url)
        if not key:
            return 0
        now = time.time()
        hit = self._probe.get(key)
        if hit and now - hit[0] < hit[2]:
            return hit[1]
        cur, kbps = key, 0
        for _ in range(3):
            body, dt = self._fetch(cur)
            if not body:
                break
            if b'#EXTM3U' in body[:256]:
                nxt = ''
                for line in body.decode('utf-8', 'ignore').splitlines():
                    s = line.strip()
                    if s and not s.startswith('#'):
                        nxt = urllib.parse.urljoin(cur.rsplit('/', 1)[0] + '/', s)
                        break
                if not nxt:
                    break
                cur = nxt
                continue
            if dt > 0 and len(body) > 4096:
                kbps = int(len(body) / dt / 1024)
            break
        self._probe[key] = (now, kbps, self.PROBE_TTL if kbps > 0 else 120)
        if len(self._probe) > 400:
            for k in list(self._probe.keys())[:80]:
                self._probe.pop(k, None)
        return kbps

    def _fetch(self, url):
        try:
            headers = {'User-Agent': self.UA, 'Referer': self.HOST + '/',
                       'Accept': '*/*', 'Range': 'bytes=0-%d' % (self.PROBE_BYTES - 1)}
            data = http(url, headers=headers, timeout=1.6, retries=1)[1]
            if not data:
                return b'', 0.0
            return data, max(0.05, len(data) / float(max(1, 1024)) / 300.0)
        except Exception:
            return b'', 0.0

    def _probe_all(self, urls, budget=0.55):
        res = {}
        lock = threading.Lock()

        def work(u):
            val = self._speed(u)
            with lock:
                res[u] = val

        threads = []
        for u in urls:
            t = threading.Thread(target=work, args=(u,))
            t.daemon = True
            t.start()
            threads.append(t)
        deadline = time.time() + budget
        for t in threads:
            t.join(max(0.01, deadline - time.time()))
        return res

    def _lines(self, options):
        opts = [o for o in as_list(options) if isinstance(o, dict)]
        lines, seen, used = [], set(), {}

        def add(label, prov, frm, mode):
            label = clean_name(label) or '线路'
            key = (label, prov, frm)
            if key in seen:
                return
            seen.add(key)
            if label in used:
                used[label] += 1
                label = '%s%d' % (label, used[label])
            else:
                used[label] = 1
            lines.append({'label': label, 'provider_id': prov,
                          'play_from': frm, 'mode': mode})

        # 1) 官方 4K / 1080P（需会话）—— 会话由后台线程预热，最多等 1.2s
        prem = [o for o in opts if self._premium(o)]
        if prem and self._await_session(0.6):
            prem.sort(key=lambda o: (-self._weight(o),
                                     -('4K' in text(o.get('label')).upper())))
            for o in prem[:self.MAX_PREMIUM]:
                add(self._line_label(o), self._line_key(o)[0], self._line_key(o)[1], 'parse')

        # 2) 第三方直链：先去重（同一 URL 只留权重最高的一条），再按实测速度排序
        directs = [o for o in opts if self._opt_direct(o)]
        if directs:
            groups = {}
            for o in directs:
                url = text(o.get('url'))
                if not url:
                    continue
                cur = groups.get(url)
                if cur is None or self._weight(o) > self._weight(cur):
                    groups[url] = o
            cand = sorted(groups.values(), key=self._weight, reverse=True)[:6]
            speeds = self._probe_all([text(o.get('url')) for o in cand]) if cand else {}
            alive = sorted(((speeds.get(text(o.get('url')), 0), o) for o in cand),
                           key=lambda x: -x[0])
            # 先放实测有速度的，再放没测出来的（超预算/慢），一条都不丢
            picked = ([o for k, o in alive if k > 0]
                      + [o for k, o in alive if k <= 0])[:self.MAX_LINES]
            for o in picked:
                add(self._line_label(o), self._line_key(o)[0], self._line_key(o)[1], 'direct')
        else:
            tickets = [o for o in opts if self._opt_ticket(o)]
            tickets.sort(key=self._weight, reverse=True)
            for o in tickets[:self.MAX_LINES]:
                add(self._line_label(o), self._line_key(o)[0], self._line_key(o)[1], 'parse')

        # 3) 通用解析兜底（最后一条）
        add('解析线路', '', '', 'generic')
        return lines

    # ---------- 详情入口 ----------
    def detail(self, vid):
        vid = text(vid)
        if not vid:
            return {}
        st, data = self._req(self.PATH_DETAIL % urllib.parse.quote(vid, safe=''))
        if not isinstance(data, dict):
            data = {}
        ep_vid = text(self._pick(data, 'selected_variant_id', 'variant_id', 'id')) or vid
        eps = self._episodes(ep_vid)
        vod = {
            'vod_id': vid,
            'vod_name': text(self._pick(data, 'title', 'normalized_title')) or vid,
            'vod_pic': text(self._pick(data, 'poster_url', 'poster')),
            'vod_year': text(self._pick(data, 'year')),
            'vod_area': text(self._pick(data, 'area')),
            'vod_remarks': text(self._pick(data, 'episode_progress_text', 'remarks')),
            'vod_actor': self._join(self._pick(data, 'actors', default=[])),
            'vod_director': self._join(self._pick(data, 'directors', default=[])),
            'vod_content': text(self._pick(data, 'description', 'intro')),
            'vod_score': text(self._pick(data, 'rating', 'score')),
        }
        if not eps:
            return {'vod': vod, 'lines': []}

        options = []
        for ep in eps[:2]:
            r = self._resolve(ep['token'])
            cand = as_list(r.get('line_options'))
            if cand:
                options = cand
                break
        if not options:
            return {'vod': vod, 'lines': []}
        lines = self._lines(options)

        gen_key = next(((ln['provider_id'], ln['play_from'])
                        for ln in lines if ln['mode'] == 'direct'), None)
        out = []
        for ln in lines:
            eps_out = []
            for idx, ep in enumerate(eps):
                tok = ep['token']
                if ln['mode'] == 'generic':
                    ref = ('zjoff|%s|%s|%s' % (tok, b64url_encode(gen_key[0]),
                                               b64url_encode(gen_key[1]))) \
                        if gen_key else ('zjoff|%s' % tok)
                else:
                    ref = 'zjres|%s|%s|%s|%s' % (
                        tok, b64url_encode(ln['provider_id']),
                        b64url_encode(ln['play_from']), b64url_encode(ln['label']))
                name = clean_name(ep['title']) or '第%d集' % (idx + 1)
                eps_out.append('%s$%s' % (name, ref))
            if eps_out:
                out.append((ln['label'], eps_out))
        return {'vod': vod, 'lines': out}

    # ---------- 播放 ----------
    def _play_line(self, token, prov, frm, label, generic=False):
        """严格按月台标签/供应商取流：专属线路绝不回落到别的供应商，
        否则会把「别的片子的直链」当成这条线路的结果（原脚本的兜底就有这个坑）。"""
        prov, frm, label = text(prov), text(frm), text(label)
        cache_key = 'zj:ln:%s|%s|%s|%s' % (token, prov, frm, label)
        hit = cache_get(cache_key)
        if hit is not None:
            return hit

        r = self._resolve(token)
        opts = [o for o in as_list(r.get('line_options')) if isinstance(o, dict)]
        if not opts:
            return ''
        directs = [o for o in opts if self._opt_direct(o)]
        tickets = [o for o in opts if self._opt_ticket(o)]
        exact = (prov, frm)

        def pick_direct(items):
            for o in items:
                url = text(o.get('url'))
                if self._valid_url(url):
                    return url
            return ''

        def pick_ticket(items):
            for o in items:
                url = text(self._resolve_line(o.get('url')).get('url'))
                if self._valid_url(url):
                    return url
            return ''

        url = ''
        if label:
            url = pick_direct([o for o in directs if self._line_label(o) == label])
        if not url and (exact[0] or exact[1]):
            url = pick_direct([o for o in directs if self._line_key(o) == exact])
        if not url and label:
            url = pick_ticket([o for o in tickets if self._line_label(o) == label])
        if not url and (exact[0] or exact[1]):
            url = pick_ticket([o for o in tickets if self._line_key(o) == exact])
        if not url and (generic or not exact[0]):
            url = pick_ticket(tickets[:5]) or pick_direct(directs[:2])
        if url:
            cache_put(cache_key, url, self.CACHE_TTL)
        return url

    def play(self, ref):
        raw = text(ref)
        if '%7C' in raw.upper() or '%3A' in raw.upper():
            raw = urllib.parse.unquote(raw)
        parts = raw.split('|')
        kind = parts[0] if parts else ''
        token = parts[1] if len(parts) > 1 else ''
        prov = b64url_decode(parts[2]).decode('utf-8', 'ignore') if len(parts) > 2 else ''
        frm = b64url_decode(parts[3]).decode('utf-8', 'ignore') if len(parts) > 3 else ''
        label = b64url_decode(parts[4]).decode('utf-8', 'ignore') if len(parts) > 4 else ''
        if not token:
            return {'url': '', 'parse': 0}
        url = self._play_line(token, prov, frm, label, generic=(kind == 'zjoff'))
        if not url:
            # 站点 503 抖动时第一次可能空手，重试一次（播放是用户触发，多等一下无妨）
            time.sleep(0.15)
            url = self._play_line(token, prov, frm, label, generic=(kind == 'zjoff'))
        if not url:
            return {'url': '', 'parse': 0}
        ext = self._is_ext(url)
        return {'url': url, 'parse': 1 if ext else 0,
                'header': {'User-Agent': self.UA, 'Referer': self.HOST + '/'}}

# ============================================================================
# 门面：聚合 Spider
#   首页 / 分类 / 筛选 / 搜索：影探4K
#   详情线路：影探 → 咕噜 → 橘汁 → 找剧（TVBox 默认播第一条，即影探）
# ============================================================================

class YtAggSpider(_BaseSpider):
    NAME = '影探聚合'
    LABELS = {'yt': '影探', 'gg': '咕噜', 'jz': '橘汁', 'zj': '找剧'}
    ORDER = ['yt', 'gg', 'jz', 'zj']
    DETAIL_BUDGET = 4.0       # 首屏预算（秒）——超时的源转后台补全
    SEARCH_BUDGET = 1.1       # 必须小于外层 2.8s，否则影探搜索结果会被整体丢弃
    HOME_WAIT = 1.5           # 首页分类（nav）最多等这么久（实测 0.1~0.6s）
    HOME_VOD_WAIT = 1.2       # 推荐位（index_video）再等这么久，超时先出分类
    CACHE_TTL = 300
    MAX_LINES_PER_SRC = 8

    def __init__(self):
        self._sources = {}
        self._lock = threading.RLock()
        self.order = list(self.ORDER)
        self.max_lines = self.MAX_LINES_PER_SRC
        self.detail_budget = self.DETAIL_BUDGET
        self.zj_cookie = ''
        self._last_err = ''
        self._warmed = False
        self._filling = set()
        self._update_url = ''
        self._update = {}
        self._updating = False

    # ---------- 生命周期 ----------
    def getName(self):
        return self.NAME

    def version(self):
        return code_version()

    def init(self, extend=''):
        cfg = {}
        try:
            if isinstance(extend, dict):
                cfg = extend
            elif isinstance(extend, str) and extend.strip().startswith('{'):
                cfg = loads(extend)
        except Exception:
            cfg = {}
        lines = [t for t in as_list(cfg.get('lines')) if t in self.LABELS]
        if lines:
            self.order = list(dict.fromkeys(lines + [t for t in self.ORDER if t not in lines]))
        try:
            self.detail_budget = float(cfg.get('detail_budget') or self.DETAIL_BUDGET)
        except (TypeError, ValueError):
            self.detail_budget = self.DETAIL_BUDGET
        try:
            self.max_lines = int(cfg.get('max_lines') or self.MAX_LINES_PER_SRC)
        except (TypeError, ValueError):
            self.max_lines = self.MAX_LINES_PER_SRC
        self.zj_cookie = text(cfg.get('zj_cookie') or cfg.get('cookie'))
        with self._lock:
            if self.zj_cookie and 'zj' in self._sources:
                self._sources.pop('zj', None)
        self._warmed = False
        self._update_url = text(cfg.get('update_url') or UPDATE_URL)
        if text(cfg.get('update', '1')).lower() not in ('0', 'false', 'no', 'off'):
            pass  # Kishuto: 自更新由外层统一负责
        return None

    def _auto_update(self):
        # 合并版统一由 Kishuto 门面负责自更新，子源不再各自拉清单
        return
        self._updating = True

        def run():
            try:
                got = check_update(self._update_url)
                self._update = got
                globals()['_UPDATE_LAST'] = got
            except Exception:
                pass

        try:
            threading.Thread(target=run, daemon=True).start()
        except Exception:
            pass

    def _prewarm(self):
        """首页阶段偷偷把咕噜/橘汁的握手+boot 做完（各约 0.9s），
        详情页就不用再付这笔开销。失败无所谓，详情里会自己重试。"""
        if self._warmed:
            return
        # 标志由发线程的结果决定：闸门满（返回 None）就不置位，下次调用还能补
        self._warmed = False

        def run():
            for tag in ('gg', 'jz'):
                try:
                    if tag in self.order:
                        self._src(tag).client.ensure()
                except Exception:
                    pass
            # 找剧AI 官方 4K/1080P 要游客会话；首页后台先建好，
            # 详情页 _await_session(0.6) 才来得及把 4K 线路挂出来。
            try:
                if 'zj' in self.order:
                    self._src('zj')._ensure_session()
            except Exception:
                pass

        self._warmed = _bg_spawn(run, name='prewarm-yt') is not None

    def _src(self, tag):
        with self._lock:
            got = self._sources.get(tag)
            if got is not None:
                return got
            if tag == 'yt':
                got = YT4K()
            elif tag in ('gg', 'jz'):
                got = T3Source(tag)
            elif tag == 'zj':
                got = ZJSource(self.zj_cookie)
            else:
                got = None
            if got is not None:
                self._sources[tag] = got
            return got

    def destroy(self):
        self._sources = {}
        return None

    def isVideoFormat(self, url):
        return is_media_url(url)

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return None

    # ---------- 首页 / 分类 / 搜索 ----------
    def homeContent(self, filter=True):
        # 有些壳不调 init()，这里兜一次，保证新版本总会被拉下来
        if self._update_url and not self._update and not self._updating:
            pass  # Kishuto: 自更新由外层统一负责
        self._prewarm()
        yt = self._src('yt')
        box = {}

        def get_home():
            try:
                box['home'] = yt.home()
            except Exception as exc:
                self._last_err = 'home:%s' % exc
                box['home'] = {'class': [], 'filters': {}}

        def get_vod():
            try:
                # 短超时：index_video 是站点最慢的接口（实测 0.5~2.1s），
                # 首页不能把整个首屏押在它身上。
                box['vod'] = as_list(
                    yt.home_vod(self.HOME_VOD_WAIT + 0.3).get('list'))[:30]
            except Exception:
                box['vod'] = []

        # nav 与 index_video 并发。原来先等 nav（0.1~0.6s）回来发现没有推荐位，
        # 再串行等 index_video（0.5~2.1s），首页 2.2s 里有一半是纯等待。
        t1 = threading.Thread(target=get_home, daemon=True)
        t2 = threading.Thread(target=get_vod, daemon=True)
        t1.start()
        t2.start()
        t1.join(self.HOME_WAIT)
        data = box.get('home')
        if not isinstance(data, dict):
            data = {'class': [], 'filters': {}}
        if not as_list(data.get('list')):
            # 推荐位超时就先出分类：后台线程仍会跑完并写进 10 分钟缓存，
            # 壳紧接着调 homeVideoContent 或用户重进首页时就秒回。
            t2.join(max(0.0, self.HOME_VOD_WAIT))
            if as_list(box.get('vod')):
                data['list'] = box['vod']
        return data

    def homeVideoContent(self):
        try:
            return self._src('yt').home_vod()
        except Exception as exc:
            self._last_err = 'home_vod:%s' % exc
            return {'list': []}

    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        yt = self._src('yt')
        try:
            data = yt.category(tid, pg, extend)
        except Exception as exc:
            self._last_err = 'category:%s' % exc
            return {'list': [], 'page': 1, 'pagecount': 0, 'limit': 18, 'total': 0}
        if not as_list(data.get('list')) and page_of(pg) == 1:
            cache_put('yt:cms-fail:%s' % text(tid), '', 1)
            try:
                data = yt.category(tid, pg, extend)
            except Exception:
                pass
        return data

    # 片名噪音：版本/语种/年份/解说类后缀，合并卡片时先去掉
    NAME_NOISE = ('手语版', '字幕助听版', '字幕版', '助听版', '无字幕',
                  '国语版', '粤语版', '日语版', '英语版', '普通话版', '双语版',
                  '真人版', '动画版', '重制版', '剧版', '电影版', '电视版',
                  '完整版', '未删减', '无删减', '高清版', '蓝光版', '合集', '正片',
                  '解说', '精彩分享', '剧情揭秘', '揭秘', '预告', '花絮', '片段')

    @classmethod
    def _base_name(cls, name, kw=''):
        """把「凡人修仙传手语版」这类变体归一成主片名。"""
        t = norm_title(name)
        if not t:
            return ''
        t = re.sub(r'[（(][^）)]*[）)]', '', t)      # 括号注释
        for _ in range(3):                          # 反复剥，可能叠着好几个
            for w in cls.NAME_NOISE:
                if t.endswith(w) and len(t) > len(w):
                    t = t[:-len(w)]
                elif t.startswith(w) and len(t) > len(w):
                    t = t[len(w):]
        t = re.sub(r'(19|20)\d{2}$', '', t)          # 结尾年份
        t = t.rstrip('之');
        return t.strip() or norm_title(name)

    def searchContent(self, key, quick=False, pg='1'):
        kw = text(key)
        if not kw:
            return {'list': []}
        page = page_of(pg)
        out = []
        try:
            out = as_list(self._src('yt').search(kw, page).get('list'))
        except Exception as exc:
            self._last_err = 'search:%s' % exc
        if len(out) >= 5 or page > 1:
            return {'list': out}

        # 影探命中太少 → 并发问其他三源（id 加源前缀，详情页按前缀回源）
        found = {}
        threads = []
        deadline = time.time() + self.SEARCH_BUDGET
        for tag in ['gg', 'jz', 'zj']:
            if tag not in self.order:
                continue
            th = threading.Thread(target=self._search_one,
                                  args=(tag, kw, page, found), daemon=True)
            th.start()
            threads.append(th)
        for th in threads:
            th.join(max(0.05, deadline - time.time()))
        seen = set(norm_title(x.get('vod_name')) for x in out)
        for tag in ['gg', 'jz', 'zj']:
            for card in found.get(tag) or []:
                name = text(card.get('vod_name'))
                if not name or norm_title(name) in seen:
                    continue
                seen.add(norm_title(name))
                item = dict(card)
                item['vod_id'] = '%s:%s' % (tag, text(card.get('vod_id')))
                out.append(item)
        return {'list': out}

    def _search_one(self, tag, keyword, page, box):
        try:
            box[tag] = self._items(self._src(tag), keyword, page)
        except Exception:
            box[tag] = []

    @staticmethod
    def _items(src, keyword, page=1):
        """各源 search 返回形态不一（影探给 {'list':[...]}，T3/找剧直接给 list）。"""
        got = src.search(keyword, page)
        if isinstance(got, dict):
            return as_list(got.get('list'))
        return as_list(got)

    # ---------- 详情 ----------
    def detailContent(self, ids):
        vid = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        vid = text(vid)
        if not vid:
            return {'list': []}
        cache_key = 'merged:%s' % vid
        hit = cache_get(cache_key)
        if hit is not None:
            got = loads(hit)
            if got:
                return got

        deadline = time.time() + self.detail_budget
        tag, real = self._split_id(vid)
        base = self._base(tag, real)
        if not base:
            return {'list': []}
        title, vod, base_lines = base

        others = [t for t in self.order if t != tag]
        found = {}
        threads = []
        for other in others:
            # 之前补全过的源直接复用（按源缓存，不受合并缓存过期影响）
            pre = cache_get('pre:%s:%s' % (other, vid))
            if pre:
                found[other] = pre
                continue
            th = threading.Thread(target=self._collect,
                                  args=(other, title, found), daemon=True)
            th.start()
            threads.append(th)
        for th in threads:
            th.join(max(0.05, deadline - time.time()))

        for other in others:
            if found.get(other):
                cache_put('pre:%s:%s' % (other, vid), found[other], 1800)

        vod = dict(vod)
        result = self._render(tag, vod, base_lines, found)
        cache_put(cache_key, json.dumps(result, ensure_ascii=False), self.CACHE_TTL)

        # 首屏没赶上的源，后台补全后写回缓存：下次点进同一个片子就是完整四源
        missing = [t for t in others if not found.get(t)]
        if missing:
            with self._lock:
                spawn = vid not in self._filling
                if spawn:
                    self._filling.add(vid)
            if spawn:
                if _bg_spawn(self._fill_later,
                             (cache_key, vid, tag, vod, base_lines, title,
                              found, missing), name='fill-later') is None:
                    with self._lock:
                        self._filling.discard(vid)
        return loads(json.dumps(result, ensure_ascii=False))

    def _render(self, tag, vod, base_lines, extra):
        """把基准源 + 各源线路拼成 TVBox 详情结构。"""
        lines = list(base_lines)
        for other in [t for t in self.order if t != tag]:
            lines.extend(as_list(extra.get(other)))
        froms, urls = [], []
        used = {}
        for src_tag, name, eps in lines:
            label = clean_name('%s·%s' % (self.LABELS.get(src_tag, src_tag),
                                          clean_name(name) or '线路'))
            if label in used:
                used[label] += 1
                label = '%s·%d' % (label, used[label])
            else:
                used[label] = 1
            segs = []
            for ep_name, raw in eps:
                code = self._encode(src_tag, name, raw)
                if code:
                    segs.append('%s$%s' % (clean_name(ep_name) or '正片', code))
            if segs:
                froms.append(label)
                urls.append('#'.join(segs))

        vod = dict(vod)
        vod['vod_play_from'] = '$$$'.join(froms)
        vod['vod_play_url'] = '$$$'.join(urls)
        if not froms:
            vod['vod_content'] = (text(vod.get('vod_content')) + NL + NL +
                                  '[聚合提示] 四个源都没有匹配到可用线路，' +
                                  '可稍后重试或换个片名搜索。').strip()
        return {'list': [vod]}

    def _fill_later(self, cache_key, vid, tag, vod, base_lines, title, found, missing):
        """后台慢补：不设预算地跑完剩下的源，成功后刷新缓存。"""
        try:
            for other in missing:
                try:
                    self._collect(other, title, found)
                except Exception:
                    pass
            if not any(found.get(t) for t in missing):
                return
            for t in missing:
                if found.get(t):
                    cache_put('pre:%s:%s' % (t, vid), found[t], 1800)
            result = self._render(tag, dict(vod), base_lines, found)
            cache_put(cache_key, json.dumps(result, ensure_ascii=False),
                      self.CACHE_TTL + 120)
        except Exception:
            pass
        finally:
            with self._lock:
                self._filling.discard(vid)

    def _split_id(self, vid):
        head, sep, rest = vid.partition(':')
        if sep and head in self.LABELS and rest:
            return head, rest
        return 'yt', vid

    def _base(self, tag, vid):
        """取基准源详情，返回 (标题, vod, [(tag, 线路名, [(集名, 原始id)])])。"""
        try:
            if tag == 'yt':
                vod = self._src('yt').detail(vid)
                if not vod:
                    return None
                lines = []
                froms = text(vod.get('vod_play_from')).split('$$$')
                urls = text(vod.get('vod_play_url')).split('$$$')
                for name, block in zip(froms, urls):
                    eps = self._split_eps(block)
                    if eps:
                        lines.append(('yt', name, eps))
                vod = dict(vod)
                vod['vod_id'] = text(vid)
                return text(vod.get('vod_name')), vod, lines
            if tag in ('gg', 'jz'):
                data = self._src(tag).detail(vid)
                if not data:
                    return None
                lines = []
                for ln in as_list(data.get('lines')):
                    eps = []
                    for seg in as_list(ln.get('eps')):
                        ep_name, sep, ep_id = seg.partition('$')
                        if sep and ep_id:
                            eps.append((ep_name, '%d\x1e%s' % (
                                ln.get('parser_id') or 0, ep_id)))
                    if eps:
                        lines.append((tag, ln.get('name'), eps))
                vod = {
                    'vod_id': vid, 'vod_name': data.get('vod_name'),
                    'vod_pic': data.get('vod_pic'), 'vod_year': data.get('vod_year'),
                    'vod_area': data.get('vod_area'),
                    'vod_remarks': data.get('vod_remarks'),
                    'vod_content': data.get('vod_content'),
                }
                return text(data.get('vod_name')), vod, lines
            if tag == 'zj':
                data = self._src('zj').detail(vid)
                if not data:
                    return None
                lines = [(tag, name, self._split_eps(eps))
                         for name, eps in as_list(data.get('lines'))]
                lines = [x for x in lines if x[2]]
                return text(as_dict(data.get('vod')).get('vod_name')), \
                    as_dict(data.get('vod')), lines
        except Exception as exc:
            self._last_err = 'base(%s):%s' % (tag, exc)
        return None

    def _collect(self, tag, title, box):
        """其他源：按标题搜索 → 取最像的一条 → 复用 _base 取线路。"""
        try:
            items = self._items(self._src(tag), title)
            match = strict_match(title, items)
            if not match:
                box[tag] = []
                return
            base = self._base(tag, text(match.get('vod_id')))
            box[tag] = (base[2][:self.max_lines] if base else [])
        except Exception:
            box[tag] = []

    @staticmethod
    def _split_eps(block):
        segs = [text(x) for x in block] if isinstance(block, (list, tuple)) \
            else text(block).split('#')
        eps = []
        for seg in segs:
            name, sep, pid = seg.partition('$')
            if sep and pid:
                eps.append((name, pid))
        return eps

    # ---------- 线路编码 / 播放派发 ----------
    @staticmethod
    def _encode(tag, name, raw):
        """<tag>|<base64url(线路名\\x1f原始id)>，壳回传时按 tag 派发回原源。"""
        payload = '%s%s%s' % (clean_name(name), _SEP, raw)
        blob = b64url_encode(payload)
        return '%s|%s' % (tag, blob) if blob else ''

    def _decode(self, pid, flag=''):
        raw = text(pid)
        tag, sep, blob = raw.partition('|')
        if sep and tag in self.LABELS and blob:
            plain = b64url_decode(blob).decode('utf-8', 'ignore')
            name, s2, real = plain.partition(_SEP)
            if s2:
                return tag, real, name or flag
        return 'yt', raw, text(flag)

    def playerContent(self, flag, id, vipFlags=None):
        raw = id[0] if isinstance(id, (list, tuple)) and id else id
        tag, real, name = self._decode(raw, flag)
        empty = {'parse': 0, 'url': '', 'header': {'User-Agent': UA_WEB}}
        if not real:
            return empty
        try:
            if tag == 'yt':
                got = self._src('yt').play(real)
                return {'parse': 0, 'url': text(got.get('url')),
                        'header': got.get('header') or {'User-Agent': 'okhttp/4.12.0'}}
            if tag in ('gg', 'jz'):
                parser_id, sep, play_id = real.partition('\x1e')
                if not sep:
                    play_id, parser_id = real, '0'
                url = self._src(tag).play(parser_id, play_id, name)
                return {'parse': 0, 'url': url or '',
                        'header': {'User-Agent': T3_PROFILES[tag]['ua']}}
            if tag == 'zj':
                got = self._src('zj').play(real)
                return {'parse': int(got.get('parse') or 0), 'url': text(got.get('url')),
                        'header': got.get('header') or {'User-Agent': UA_WEB}}
        except Exception as exc:
            self._last_err = 'play(%s):%s' % (tag, exc)
        return empty


# ======================================================================
# 模块：xf
# ======================================================================
# -*- coding: utf-8 -*-
"""
稀饭聚合 · TVBox / OK影视 四源聚合 Python 源
================================================================
首页数据 : 稀饭动漫 Next (xifanacg) —— 分类 / 推荐 / 筛选 / 搜索 / 条目元数据
播放线路 : 四源同时挂出，默认优先级（用户 2026-11-04 指定）
           1. 稀饭动漫   xifanacg        tag=xf
           2. GiriGiri爱 girigirilove   tag=gg
           3. 次元城动画 cycani.org     tag=cy
           4. OmoFun     omofun.in      tag=om
           TVBox 默认取第一条线路播放，故此顺序即默认选线顺序。

线路名 : 「源·原线路名」；选集 id : "<tag>|<base64url(flag + US + 原始id)>"
         playerContent 按 tag 解码后派发回对应源，不依赖壳回传的 flag。

源配置 extend（JSON，全部可选）:
{
  "cyc_username": "次元城账号",
  "cyc_password": "密码",
  "cyc_token": "浏览器复制的 JWT",
  "lines": ["xf", "gg", "cy", "om"],
  "detail_budget": 7,
  "host": "https://next.xifanacg.com",
  "api": "https://api.xifanacg.com",
  "key": "sb_publishable_xxx"
}
说明：次元城播放接口需登录，上面三个 cyc_* 字段至少要给一个；
      否则该源仍能列出选集，但播放会返回空地址（接口 401）。

2026-11-04 修复要点（xifanacg「已坏」）:
  站点接口实测全部正常（RPC / 详情 / 取流均 200）。真正的故障是旧脚本
  _rsc_sources() 去请求 Next.js 的 /anime/{id} 页面，单次要 10.6~11s，
  而该页 RSC payload 里已经完全没有 sources 数据 —— 详情页被拖到超时，
  且只能降级出 1 条假线路。本版改为调用 issue-web-playback 拿 candidates
  （含 source_id / source_name），详情页由 ~11.5s 降到 ~1s，并恢复 3 条真实线路。
"""

import sys
import difflib
import tempfile

try:
    import http.client as http_client
except Exception:
    http_client = None

sys.path.append('..')
try:
    from base.spider import Spider as _SpiderBase
except Exception:
    class _SpiderBase(object):
        pass

XF_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
VIDEO_EXTS = ('.m3u8', '.mp4', '.mkv', '.flv', '.avi', '.ts', '.mov',
              '.m4v', '.webm', '.wmv', '.rmvb', '.mpd')
EXT_HOSTS = ('v.qq.com', 'qq.com', 'youku.com', 'iqiyi.com', 'bilibili.com',
             'mgtv.com', 'sohu.com', 'pptv.com', 'le.com', 'wasu.cn', '1905.com')
US = chr(31)          # 线路 flag 与原始 id 的内部分隔符


class _DummyLock(object):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


_POOL = {}
XF_CACHE = {}
_POOL_MAX = 5
_POOL_IDLE = 25.0
_CACHE_MAX = 200
_SSL = None
_SSL_READY = False
try:
    _POOL_LOCK = threading.Lock() if threading else _DummyLock()
    _CACHE_LOCK = threading.Lock() if threading else _DummyLock()
except Exception:
    _POOL_LOCK = _CACHE_LOCK = _DummyLock()


# ==================== 全局 HTTP 层（四源共享连接池 / 缓存） ====================
def _ssl_ctx():
    global _SSL, _SSL_READY
    if not _SSL_READY:
        _SSL_READY = True
        try:
            # TVBox 内置 Python 常缺系统根证书；这些是公开采集接口，统一不校验
            _SSL = ssl._create_unverified_context() if ssl else None
        except Exception:
            _SSL = None
    return _SSL


def xf_cache_get(key):
    try:
        with _CACHE_LOCK:
            it = XF_CACHE.get(key)
            if not it:
                return None
            if it[0] > time.time():
                return it[1]
            XF_CACHE.pop(key, None)
    except Exception:
        pass
    return None


def xf_cache_put(key, val, ttl):
    try:
        with _CACHE_LOCK:
            if len(XF_CACHE) >= _CACHE_MAX:
                now = time.time()
                for k in [k for k, v in XF_CACHE.items() if v[0] <= now]:
                    XF_CACHE.pop(k, None)
            _cap_put(XF_CACHE, key, (time.time() + ttl, val), _CACHE_MAX)
    except Exception:
        pass


def _new_conn(scheme, netloc, timeout):
    kw = {'timeout': timeout}
    if scheme == 'https':
        ctx = _ssl_ctx()
        if ctx is not None:
            kw['context'] = ctx
        return http_client.HTTPSConnection(netloc, **kw)
    return http_client.HTTPConnection(netloc, **kw)


def _pool_take(netloc):
    try:
        with _POOL_LOCK:
            lst = _POOL.get(netloc)
            now = time.time()
            while lst:
                conn, ts = lst.pop()
                if now - ts < _POOL_IDLE and getattr(conn, 'sock', None) is not None:
                    return conn
                try:
                    conn.close()
                except Exception:
                    pass
    except Exception:
        pass
    return None


def _pool_give(netloc, conn):
    try:
        with _POOL_LOCK:
            lst = _POOL.setdefault(netloc, [])
            if len(lst) < _POOL_MAX:
                lst.append((conn, time.time()))
                return
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass


def pool_clear():
    try:
        with _POOL_LOCK:
            for lst in list(_POOL.values()):
                for conn, _ in lst:
                    try:
                        conn.close()
                    except Exception:
                        pass
            _POOL.clear()
    except Exception:
        pass


def _unzip(data, enc):
    try:
        if not data or not enc:
            return data
        if 'gzip' in enc and gzip:
            return gzip.decompress(data)
        if 'deflate' in enc and zlib:
            try:
                return zlib.decompress(data)
            except Exception:
                return zlib.decompress(data, -zlib.MAX_WBITS)
    except Exception:
        pass
    return data


def _decode(data, ctype):
    cs = 'utf-8'
    try:
        m = re.search(r'charset=([\w-]+)', ctype or '')
        if m:
            cs = m.group(1)
    except Exception:
        pass
    try:
        return data.decode(cs, 'ignore')
    except Exception:
        return data.decode('utf-8', 'ignore')


def _urllib_req(url, method, data, h, timeout):
    try:
        req = urllib.request.Request(url, data=data, headers=h, method=method)
        kw = {'timeout': timeout}
        ctx = _ssl_ctx()
        if ctx is not None:
            kw['context'] = ctx
        with urllib.request.urlopen(req, **kw) as resp:
            raw = resp.read()
            enc = (resp.headers.get('Content-Encoding') or '').lower()
            return resp.status, _decode(_unzip(raw, enc), resp.headers.get('Content-Type'))
    except urllib.error.HTTPError as e:
        try:
            raw = _unzip(e.read(), (e.headers.get('Content-Encoding') or '').lower())
            return e.code, raw.decode('utf-8', 'ignore')
        except Exception:
            return e.code, ''
    except Exception:
        return 0, ''


def request_ex(url, method='GET', body=None, headers=None, timeout=8.0, ttl=0):
    """返回 (status, text)。body 为 dict/list 时自动序列化并置 Content-Type。
    连接池按 netloc 复用；仅 2xx 会回池；短 TTL 缓存只存原始文本。"""
    try:
        p = urllib.parse.urlsplit(str(url or ''))
    except Exception:
        return 0, ''
    netloc = p.netloc
    if not netloc:
        return 0, ''
    scheme = (p.scheme or 'https').lower()
    path = (p.path or '/') + (('?' + p.query) if p.query else '')
    try:
        if any(ord(c) > 127 for c in path):
            path = urllib.parse.quote(path, safe="/?&=%:@+,~$!*'();[]")
    except Exception:
        pass

    h = dict(headers or {})
    data = None
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body, ensure_ascii=False).encode('utf-8')
            h.setdefault('Content-Type', 'application/json')
        elif isinstance(body, str):
            data = body.encode('utf-8')
        else:
            data = body
        if method == 'GET':
            method = 'POST'
    if gzip or zlib:
        h.setdefault('Accept-Encoding', 'gzip, deflate')
    h.setdefault('User-Agent', XF_UA)

    ck = None
    if ttl:
        ck = '%s|%s|%s|%s' % (method, url, (data or b'')[:160],
                              h.get('Authorization', ''))
        hit = xf_cache_get(ck)
        if hit is not None:
            return 200, hit

    st, txt = 0, ''
    if http_client is None:
        st, txt = _urllib_req(url, method, data, h, timeout)
    else:
        for attempt in (0, 1, 2):
            conn = _pool_take(netloc) if attempt < 2 else None
            reused = conn is not None
            if conn is None:
                try:
                    conn = _new_conn(scheme, netloc, timeout)
                except Exception:
                    break
            t0 = time.time()
            try:
                conn.request(method, path, body=data, headers=h)
                resp = conn.getresponse()
                raw = resp.read()
                enc = (resp.getheader('Content-Encoding') or '').lower()
                ctype = resp.getheader('Content-Type') or ''
                st = resp.status or 0
                txt = _decode(_unzip(raw, enc), ctype)
                if 200 <= st < 300:
                    _pool_give(netloc, conn)
                else:
                    try:
                        conn.close()
                    except Exception:
                        pass
                break
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
                if reused:
                    continue
                # 真超时不重试，只有 <1.2s 的快速失败才重来
                if attempt == 0 and (time.time() - t0) < 1.2:
                    continue
                break
    if ck and 200 <= st < 300 and txt:
        xf_cache_put(ck, txt, ttl)
    return st, txt


def xf_loads(txt):
    """兼容普通 JSON / NDJSON / 前后带噪声的接口响应"""
    if not txt:
        return {}
    s = txt.strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    out = []
    for line in s.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        if isinstance(o, list):
            out += o
        elif isinstance(o, dict):
            out.append(o)
    if out:
        return out
    m = re.search(r'[\{\[].*[\}\]]', s, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {}


# ==================== 通用工具 ====================
def is_video(u):
    try:
        x = str(u or '').split('#')[0].split('?')[0].strip().lower()
        return any(x.endswith(e) for e in VIDEO_EXTS)
    except Exception:
        return False


def enc_url(u):
    """路径含中文/空格时百分号编码，保留 query 里的 sign 参数"""
    try:
        s = str(u or '').strip()
        if not s or all(ord(c) < 128 for c in s):
            return s
        p = urllib.parse.urlsplit(s)
        return urllib.parse.urlunsplit((
            p.scheme, p.netloc,
            urllib.parse.quote(p.path, safe="/%:@&=+$,~"),
            urllib.parse.quote(p.query, safe="=&%:/?:@+,~"), ''))
    except Exception:
        return str(u or '')


def abs_url(base, u):
    try:
        s = str(u or '').strip()
        if not s:
            return s
        if s.startswith('//'):
            return enc_url('https:' + s)
        if s.startswith('http'):
            return enc_url(s)
        return enc_url(urllib.parse.urljoin(base, s))
    except Exception:
        return u


def xf_clean_name(s):
    try:
        t = str(s or '').strip()
        t = t.replace('$', ' ').replace('#', ' ').replace('|', ' ')
        t = t.replace('\r', ' ').replace('\n', ' ')
        return re.sub(r'\s+', ' ', t).strip()
    except Exception:
        return ''


def xf_norm_title(s):
    try:
        s = str(s or '').lower()
        return re.sub(r'[\s\u3000\-—–_·:：!！?？,，.。\[\]【】()（）「」『』《》<>／/\\|+~～]', '', s)
    except Exception:
        return ''


def xf_sim(a, b):
    """标题相似度：完全相同 > 包含 > 序列相似"""
    try:
        x, y = xf_norm_title(a), xf_norm_title(b)
        if not x or not y:
            return 0.0
        if x == y:
            return 1.0
        if x in y or y in x:
            r = float(min(len(x), len(y))) / max(len(x), len(y))
            return 0.85 + 0.12 * r if r >= 0.5 else 0.0
        return difflib.SequenceMatcher(None, x, y).ratio()
    except Exception:
        return 0.0


_SEASON_RE = re.compile(
    r'(第[一二三四五六七八九十0-9]+季|season\s*[0-9]+|part\s*[0-9]+|\bs[0-9]{1,2}\b)',
    re.I)


def season_tag(s):
    try:
        m = _SEASON_RE.search(str(s or ''))
        return m.group(0).lower() if m else ''
    except Exception:
        return ''


def search_keywords(title):
    """完整标题 → 去括号/季数的核心词 → 核心词前 6 / 4 字"""
    t = str(title or '').strip()
    out = []

    def add(x):
        x = str(x or '').strip()
        if x and x not in out and len(x) >= 2:
            out.append(x)

    add(t)
    core = re.sub(r'[\[\(（【].*?[\]\)）】]', '', t)
    core = _SEASON_RE.sub('', core)
    core = re.sub(r'\s+', ' ', core).strip()
    add(core)
    for n in (6, 4):
        if len(core) > n:
            add(core[:n])
    return out


def xf_best_match(title, items, threshold=0.70):
    best, score = None, 0.0
    ts = season_tag(title)
    for it in items or []:
        if not isinstance(it, dict):
            continue
        name = it.get('vod_name') or ''
        s = xf_sim(title, name)
        cs = season_tag(name)
        if ts and cs and ts != cs:
            s *= 0.45          # 双方季数标记都存在却不一致，避免错季
        if s > score:
            best, score = it, s
    return best if score >= threshold else None


def search_best(src, title):
    """跨站译名有差异时逐级降级搜索；降级轮只接受近乎精确匹配，
    防止把第一季的线路挂到第二季上。"""
    for i, kw in enumerate(search_keywords(title)):
        try:
            items = src.search(kw)
        except Exception:
            continue
        if not items:
            continue
        pick = xf_best_match(title, items, 0.70 if i == 0 else 0.97)
        if pick:
            return pick
    return None


def enc_pid(tag, flag, pid):
    try:
        raw = ('%s%s%s' % (flag, US, pid)).encode('utf-8')
        return tag + '|' + base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')
    except Exception:
        return ''


def dec_pid(s):
    try:
        tag, b = str(s).split('|', 1)
        b += '=' * ((4 - len(b) % 4) % 4)
        raw = base64.urlsafe_b64decode(b.encode('ascii')).decode('utf-8')
        flag, pid = raw.split(US, 1)
        return tag, flag, pid
    except Exception:
        return '', '', ''


def play_header(host, ref=None):
    return {'User-Agent': XF_UA, 'Referer': ref or (host + '/'),
            'Origin': host, 'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9'}


def is_ext_link(u):
    try:
        net = urllib.parse.urlsplit(str(u or '')).netloc.lower()
        return any(net == k or net.endswith('.' + k) for k in EXT_HOSTS)
    except Exception:
        return False


def ep_label(raw, idx):
    try:
        t = str(raw or '').strip()
        if not t:
            return '第%02d集' % (idx + 1)
        if re.match(r'^[0-9]{1,4}$', t):
            return '第%02d集' % int(t)
        return t
    except Exception:
        return '第%02d集' % (idx + 1)


def as_lines(episodes):
    """把 [(集名, flag, pid)] 规整化"""
    out = []
    for e in episodes or []:
        try:
            if len(e) >= 3 and e[2]:
                out.append((xf_clean_name(e[0]) or '正片', str(e[1] or ''), str(e[2])))
        except Exception:
            pass
    return out


def _epnum(e):
    try:
        return float(e.get('episode_number') or 0)
    except Exception:
        return 0.0


# ==================== 源 1：稀饭动漫 Next（首页数据源 + 线路） ====================
class XifanSpider(object):
    """修复版：移除无效的 RSC 请求，改用 issue-web-playback 的 candidates 建线路。"""
    TAG = 'xf'
    HOST = 'https://next.xifanacg.com'
    API = 'https://api.xifanacg.com'
    KEY = 'sb_publishable_OBIVAWACIX6lPXrO98_z24_HcsmalkA'
    PAGE_SIZE = 24
    MAX_LINES = 4
    FLAG = 'xfline'

    CATEGORIES = [
        {'tid': '1', 'name': '连载新番', 'type_id': 1, 'sort': 'updated_at'},
        {'tid': '2', 'name': '完结旧番', 'type_id': 2, 'sort': 'updated_at'},
        {'tid': '3', 'name': '剧场版', 'type_id': 3, 'sort': 'updated_at'},
        {'tid': '4', 'name': '美漫', 'type_id': 4, 'sort': 'updated_at'},
        {'tid': 'hot', 'name': '热门播放', 'sort': 'view_count'},
        {'tid': 'score', 'name': '高分好评', 'sort': 'bangumi_score'},
        {'tid': 'new', 'name': '最近上新', 'sort': 'created_at'},
        {'tid': 'tv', 'name': 'TV动画', 'fmt': 'tv', 'sort': 'updated_at'},
        {'tid': 'movie', 'name': '剧场动画', 'fmt': 'movie', 'sort': 'updated_at'},
        {'tid': 'ova', 'name': 'OVA', 'fmt': 'ova', 'sort': 'updated_at'},
        {'tid': 'web', 'name': 'WEB动画', 'fmt': 'web', 'sort': 'updated_at'},
        {'tid': 'fin', 'name': '已完结', 'finished': True, 'sort': 'updated_at'},
        {'tid': 'ing', 'name': '连载中', 'finished': False, 'sort': 'updated_at'},
        {'tid': 'y2026', 'name': '2026年', 'year': 2026, 'sort': 'updated_at'},
        {'tid': 'y2025', 'name': '2025年', 'year': 2025, 'sort': 'updated_at'},
        {'tid': 'y2024', 'name': '2024年', 'year': 2024, 'sort': 'updated_at'},
        {'tid': 'y2023', 'name': '2023年', 'year': 2023, 'sort': 'updated_at'},
    ]
    TID_ALIAS = {
        '0': '1', 'all': '1', 'ongoing': '1', 'anime': '1',
        'finished': '2', 'theater': '3', 'western': '4', 'drama': 'tv',
    }

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.host = str(cfg.get('host') or self.HOST).rstrip('/')
        self.api = str(cfg.get('api') or self.API).rstrip('/')
        self.key = str(cfg.get('key') or self.KEY)
        try:
            self.timeout = float(cfg.get('timeout') or 4)
        except Exception:
            self.timeout = 4.0
        # 健康标记：连续网络层失败就临时下线，别再让首页/分类每次白等超时
        self._fails = 0
        self._cool = 0.0
        self.alive = True

    def _mark(self, ok):
        if ok:
            self._fails = 0
            self.alive = True
            return
        self._fails += 1
        if self._fails >= 1:
            self.alive = False
            self._cool = time.time() + 120

    def health(self):
        """冷却期过后自动试探恢复。"""
        if not self.alive and time.time() > self._cool:
            self.alive = True
            self._fails = 0
        return self.alive

    def hdr(self, ref=None):
        return {
            'User-Agent': XF_UA,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': ref or (self.host + '/'),
            'Origin': self.host,
            'x-platform': 'web',
            'x-requested-with': 'XMLHttpRequest',
            'apikey': self.key,
            'authorization': 'Bearer ' + self.key,
            'x-client-info': 'supabase-ssr/0.10.3 createBrowserClient',
            'content-profile': 'public',
            'Accept-Encoding': 'gzip, deflate',
        }

    def get(self, path, params=None, ttl=0):
        url = self.api + path
        if params:
            url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
        st, txt = request_ex(url, 'GET', headers=self.hdr(),
                             timeout=self.timeout, ttl=ttl)
        self._mark(bool(st))
        return xf_loads(txt) if st and st < 400 else {}

    def post(self, path, body, ttl=0):
        st, txt = request_ex(self.api + path, 'POST', body=body,
                             headers=self.hdr(), timeout=self.timeout, ttl=ttl)
        self._mark(bool(st))
        return xf_loads(txt) if st and st < 400 else {}

    def cat(self, tid):
        t = str(tid or '').strip()
        t = self.TID_ALIAS.get(t.lower(), t)
        for c in self.CATEGORIES:
            if c['tid'] == t:
                return c
        return {'tid': t}

    def query(self, tid, pg, ext=None, kw=''):
        c = self.cat(tid)
        ext = ext if isinstance(ext, dict) else {}
        page = int(pg) if str(pg or '').isdigit() and int(pg) > 0 else 1
        q = {'page_number': page, 'items_per_page': self.PAGE_SIZE,
             'sort_by': c.get('sort') or 'updated_at', 'sort_order': 'desc',
             'filter_only_published': True}
        if kw:
            q['search_term'] = str(kw).strip()
        if c.get('type_id'):
            q['filter_type_id'] = c['type_id']
        if c.get('fmt'):
            q['filter_format'] = c['fmt']
        if 'finished' in c:
            q['filter_is_finished'] = c['finished']
        if c.get('year'):
            q['filter_release_year'] = c['year']
        for k, dst in (('sort_by', 'sort_by'), ('sort_order', 'sort_order'),
                       ('year', 'filter_release_year'),
                       ('type_id', 'filter_type_id'), ('format', 'filter_format')):
            if ext.get(k) not in (None, ''):
                q[dst] = ext[k]
        return q

    def rpc(self, tid, pg, ext=None, kw='', ttl=0):
        arr = self.post('/rest/v1/rpc/search_animes',
                        self.query(tid, pg, ext, kw), ttl=ttl)
        if not isinstance(arr, list):
            return [], 0
        total = 0
        try:
            total = int(arr[0].get('total_count') or 0) if arr else 0
        except Exception:
            total = 0
        return arr, total

    def vod(self, it):
        try:
            if not isinstance(it, dict):
                return None
            aid = it.get('id')
            if aid in (None, ''):
                return None
            # img2 走 AWS 新加坡，国内实测超时；img 是 Cloudflare 同路径可直出
            pic = str(it.get('cover_url') or '').replace(
                'img2.xfmanga.top', 'img.xfmanga.top')
            cur = it.get('current_episodes') or 0
            tot = it.get('total_episodes') or 0
            remark = ''
            if it.get('is_finished'):
                remark = ('全%d集' % tot) if tot else '已完结'
            elif cur:
                remark = ('更新至%d集' % cur) + (('/%d' % tot) if tot and tot > cur else '')
            desc = str(it.get('description') or '')
            tags = it.get('meta_tags') or []
            if isinstance(tags, list) and tags:
                desc = (desc + NL + '标签：' + ' / '.join([str(t) for t in tags[:8]])).strip()
            actors = it.get('actors')
            return {
                'vod_id': str(aid),
                'vod_name': str(it.get('title') or it.get('title_original') or ''),
                'vod_pic': pic,
                'vod_remarks': remark,
                'vod_year': str(it.get('release_year') or ''),
                'vod_area': str(it.get('region') or ''),
                'vod_lang': '日语',
                'vod_actor': ('、'.join([str(a) for a in actors[:6]])
                              if isinstance(actors, list) else ''),
                'vod_director': str(it.get('director') or ''),
                'vod_score': str(it.get('bangumi_score') or ''),
                'vod_content': desc,
                'vod_tag': '',
            }
        except Exception:
            return None

    def vod_list(self, arr):
        out = []
        for it in arr or []:
            v = self.vod(it)
            if v:
                out.append(v)
        return out

    def filters(self):
        years = [{'n': '全部', 'v': ''}]
        years += [{'n': str(y), 'v': str(y)} for y in range(2026, 2018, -1)]
        sorts = [{'n': '最近更新', 'v': ''},
                 {'n': '最多播放', 'v': 'view_count'},
                 {'n': '高分好评', 'v': 'bangumi_score'},
                 {'n': '最近上新', 'v': 'created_at'}]
        out = {}
        for c in self.CATEGORIES:
            out[c['tid']] = [{'key': 'sort_by', 'name': '排序', 'value': sorts},
                             {'key': 'year', 'name': '年份', 'value': years}]
        return out

    def homeContent(self, filter):
        classes = [{'type_id': c['tid'], 'type_name': c['name']}
                   for c in self.CATEGORIES]
        try:
            arr, _ = self.rpc('1', 1, None, '', ttl=90)
            vlist = self.vod_list(arr)[:18]
            if len(vlist) < 8:
                more, _ = self.rpc('3', 1, None, '', ttl=90)
                vlist += self.vod_list(more)[:10]
        except Exception:
            vlist = []
        return {'class': classes, 'filters': self.filters() if filter else {},
                'list': vlist}

    def homeVideoContent(self):
        try:
            arr, _ = self.rpc('new', 1, None, '', ttl=90)
            vlist = self.vod_list(arr)
            if not vlist:
                arr, _ = self.rpc('1', 1, None, '', ttl=90)
                vlist = self.vod_list(arr)
            return {'list': vlist}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        ext = {}
        if isinstance(extend, dict):
            ext = extend
        elif isinstance(extend, str) and extend.strip().startswith('{'):
            try:
                ext = json.loads(extend)
            except Exception:
                ext = {}
        try:
            arr, total = self.rpc(tid, pg, ext, '', ttl=60)
            vlist = self.vod_list(arr)
            page = int(pg) if str(pg or '').isdigit() and int(pg) > 0 else 1
            if total:
                pagecount = (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE
            else:
                pagecount = 9999 if vlist else 1
            return {'list': vlist, 'page': page,
                    'pagecount': max(pagecount, page),
                    'limit': self.PAGE_SIZE, 'total': total or len(vlist)}
        except Exception:
            return {'list': [], 'page': 1, 'pagecount': 1,
                    'limit': self.PAGE_SIZE, 'total': 0}

    def searchContent(self, key, quick, pg='1'):
        word = str(key or '').strip()
        if not word:
            return {'list': []}
        try:
            page = 1 if quick else (int(pg) if str(pg or '').isdigit() else 1)
            arr, _ = self.rpc('', page, None, word, ttl=30)
            return {'list': self.vod_list(arr)}
        except Exception:
            return {'list': []}

    def search(self, kw, page=1):
        """统一接口：按标题查本站条目（供诊断 / 跨源匹配使用）"""
        try:
            arr, _ = self.rpc('', page, None, kw, ttl=30)
            return self.vod_list(arr)
        except Exception:
            return []

    def match_lines(self, title):
        # 首页源本身就是元数据来源，详情直接由 detail() 产出线路
        return []

    def anime_eps(self, aid):
        """详情 + 剧集一次取回；嵌套 select 失败时回退成两次单独请求"""
        try:
            arr = self.get('/rest/v1/animes', {
                'id': 'eq.' + str(aid),
                'select': '*,episodes(id,episode_number,title,kind,release_date,duration_seconds)',
                'limit': 1}, ttl=120)
            if isinstance(arr, list) and arr and isinstance(arr[0], dict):
                it = arr[0]
                eps = it.pop('episodes', None) or []
                if isinstance(eps, list) and eps:
                    eps.sort(key=_epnum)
                    return it, [e for e in eps if isinstance(e, dict) and e.get('id')]
        except Exception:
            pass
        plain = self.get('/rest/v1/animes',
                         {'id': 'eq.' + str(aid), 'select': '*', 'limit': 1}, ttl=120)
        it = plain[0] if isinstance(plain, list) and plain and isinstance(plain[0], dict) else {}
        arr = self.get('/rest/v1/episodes', {
            'anime_id': 'eq.' + str(aid),
            'select': 'id,episode_number,title,kind,release_date,duration_seconds',
            'order': 'episode_number.asc', 'limit': 2000}, ttl=300)
        eps = arr if isinstance(arr, list) else []
        return it, [e for e in eps if isinstance(e, dict) and e.get('id')]

    def ep_name(self, ep, idx):
        try:
            num = int(float(ep.get('episode_number') or (idx + 1)))
        except Exception:
            num = idx + 1
        t = str(ep.get('title') or '').strip()
        return xf_clean_name(('第%02d集 %s' % (num, t)) if t else ('第%02d集' % num))

    def source_lines(self, aid, eps):
        """【核心修复】用第一集取流响应的 candidates 枚举真实线路。
        旧版解析 Next.js RSC payload，实测该页已无 sources 数据且耗时 10.6s。"""
        out = []
        eids = [e.get('id') for e in eps if e.get('id')]
        if not eids:
            return out
        try:
            first_eid = int(eids[0])
        except Exception:
            return out
        d = self.post('/functions/v1/issue-web-playback',
                      {'action': 'fallback', 'episode_id': first_eid}, ttl=180)
        cands = d.get('candidates') if isinstance(d, dict) else None
        if not isinstance(cands, list) or not cands:
            cands = [{'source_id': 0, 'source_name': '稀饭线路'}]
        used = {}
        for c in cands[:self.MAX_LINES]:
            if not isinstance(c, dict):
                continue
            try:
                sid = int(c.get('source_id') or 0)
            except Exception:
                sid = 0
            base = xf_clean_name(c.get('source_name') or c.get('source_code') or '稀饭线路') or '稀饭线路'
            name = base
            if name in used:
                used[name] += 1
                name = '%s·%d' % (base, used[name])
            else:
                used[name] = 1
            items = []
            for i, e in enumerate(eps):
                eid = e.get('id')
                if not eid:
                    continue
                items.append((self.ep_name(e, i), self.FLAG,
                              '%s|%s|%s' % (aid, eid, sid)))
            if items:
                out.append({'name': name, 'eps': as_lines(items)})
        return out

    def detail(self, aid):
        info, eps = self.anime_eps(aid)
        v = self.vod(info) or {'vod_id': aid}
        v['vod_id'] = aid
        if not v.get('vod_name'):
            v['vod_name'] = '稀饭动漫 %s' % aid
        v['vod_pubdate'] = str(info.get('release_date') or '')
        lines = self.source_lines(aid, eps)
        if eps:
            page = '%s/anime/%s/play/%s' % (self.host, aid, eps[0].get('id'))
            lines.append({'name': '网页解析',
                          'eps': [('正片', 'xfpage', 'playpage:' + page)]})
        return v, lines

    def fetch_playable(self, eid, sid):
        """按线路 source_id 取流；不缓存（url 带时效性 sign）"""
        try:
            eid_i = int(eid)
        except Exception:
            return ''
        body = {'action': 'fallback', 'episode_id': eid_i}
        try:
            if str(sid) not in ('', '0', 'None'):
                body['source_id'] = int(sid)
        except Exception:
            pass
        d = self.post('/functions/v1/issue-web-playback', body)
        u = str((d or {}).get('url') or '') if isinstance(d, dict) else ''
        if not u and body.get('source_id'):
            d2 = self.post('/functions/v1/issue-web-playback',
                           {'action': 'fallback', 'episode_id': eid_i})
            u = str((d2 or {}).get('url') or '') if isinstance(d2, dict) else ''
        return enc_url(u)

    def play(self, flag, pid):
        res = {'parse': 0, 'jx': 0, 'url': '', 'header': play_header(self.host)}
        raw = str(pid or '').strip()
        if not raw:
            return res
        if raw.startswith('playpage:'):
            page = raw[len('playpage:'):]
            return {'parse': 1, 'jx': 1, 'url': page,
                    'header': play_header(self.host, page)}
        if raw.startswith('http') or raw.startswith('//'):
            u = ('https:' + raw) if raw.startswith('//') else raw
            res['url'] = enc_url(u) if is_video(u) else u
            return res
        m = re.match(r'^([0-9]+)\|([0-9]+)\|([0-9]+)$', raw)
        if m:
            url = self.fetch_playable(m.group(2), m.group(3))
            if url:
                res['url'] = url
                return res
            page = '%s/anime/%s/play/%s' % (self.host, m.group(1), m.group(2))
            return {'parse': 1, 'jx': 1, 'url': page,
                    'header': play_header(self.host, page)}
        if raw.isdigit():
            url = self.fetch_playable(raw, 0)
            if url:
                res['url'] = url
        return res


# ==================== 源 2：GiriGiri爱（maccms 接口，直链） ====================
class GirigiriSpider(object):
    TAG = 'gg'
    HOST = 'https://ani.girigirilove.com'
    API = 'https://m3u8.girigirilove.com/api.php'
    IMG = 'https://jpg.girigirilove.com'
    PAGE_SIZE = 24
    MAX_LINES = 4
    LINE_NAME = {'cht': '繁中字幕', 'chs': '简中字幕', 'cht,chs': '繁简双字'}

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.host = str(cfg.get('giri_host') or self.HOST).rstrip('/')
        self.api = str(cfg.get('giri_api') or self.API).rstrip('/')
        try:
            self.timeout = float(cfg.get('timeout') or 6)
        except Exception:
            self.timeout = 6.0

    def hdr(self, ref=None):
        return {'User-Agent': XF_UA, 'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Referer': ref or (self.host + '/'), 'Origin': self.host,
                'x-platform': 'web', 'x-requested-with': 'XMLHttpRequest',
                'Accept-Encoding': 'gzip, deflate'}

    def call(self, path, params=None, ttl=0):
        url = self.api + path
        if params:
            url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
        st, txt = request_ex(url, 'GET', headers=self.hdr(),
                             timeout=self.timeout, ttl=ttl)
        return xf_loads(txt) if st and st < 400 else {}

    def pic(self, p):
        try:
            s = str(p or '').strip()
            if not s:
                return ''
            if s.startswith('//'):
                return 'https:' + s
            if s.startswith('http'):
                return s
            return self.IMG + '/' + s.lstrip('/')
        except Exception:
            return ''

    def vod(self, it):
        try:
            if not isinstance(it, dict):
                return None
            vid = it.get('vod_id')
            if vid in (None, ''):
                return None
            desc = str(it.get('vod_blurb') or it.get('vod_content') or '')
            cls = it.get('vod_class') or ''
            if cls and isinstance(cls, str):
                desc = (desc + NL + '类型：' + cls.replace(',', ' / ')).strip()
            return {'vod_id': str(vid),
                    'vod_name': str(it.get('vod_name') or ''),
                    'vod_pic': self.pic(it.get('vod_pic')),
                    'vod_remarks': str(it.get('vod_remarks') or ''),
                    'vod_year': str(it.get('vod_year') or ''),
                    'vod_area': str(it.get('vod_area') or ''),
                    'vod_lang': str(it.get('vod_lang') or ''),
                    'vod_content': desc}
        except Exception:
            return None

    def vod_list(self, arr):
        out = []
        for it in arr or []:
            v = self.vod(it)
            if v:
                out.append(v)
        return out

    def list_params(self, page, kw=''):
        q = {'type_id': 2, 'offset': (max(1, page) - 1) * self.PAGE_SIZE,
             'limit': self.PAGE_SIZE, 'vod_name': '', 'vod_area': '',
             'vod_year': '', 'orderby': '', 'vod_class': '', 'vod_lang': '',
             'vod_version': '', 'vod_state': '', 'vod_weekday': '',
             'vod_letter': '', 'vod_tag': '', 'user_id': ''}
        if kw:
            q['vod_name'] = str(kw).strip()
            q.pop('type_id', None)   # 搜索时带 type_id（哪怕空串）会返回 total=0
        return q

    # ---------- 备用主源（xifanacg 的 Supabase API 挂掉时顶上） ----------
    # 实测该 API 的 /Vod/get_list 支持 type_id + offset 翻页 + orderby 排序，
    # type_id=2 日漫 3147 条、type_id=3 欧美 38 条，orderby 可选 ''/hits/score。
    CATS = [
        {'type_id': 'gg_new', 'type_name': '日漫·最新'},
        {'type_id': 'gg_hot', 'type_name': '日漫·热门'},
        {'type_id': 'gg_score', 'type_name': '日漫·高分'},
        {'type_id': 'gg_us', 'type_name': '欧美动漫'},
    ]
    CAT_RULE = {'gg_new': (2, ''), 'gg_hot': (2, 'hits'),
                'gg_score': (2, 'score'), 'gg_us': (3, '')}

    def _q(self, tid, pg):
        type_id, orderby = self.CAT_RULE.get(str(tid or 'gg_new').strip(), (2, ''))
        page = int(pg) if str(pg or '').isdigit() and int(pg) > 0 else 1
        return {'type_id': type_id, 'offset': (page - 1) * self.PAGE_SIZE,
                'limit': self.PAGE_SIZE, 'vod_name': '', 'vod_area': '',
                'vod_year': '', 'orderby': orderby, 'vod_class': '',
                'vod_lang': '', 'vod_version': '', 'vod_state': '',
                'vod_weekday': '', 'vod_letter': '', 'vod_tag': '', 'user_id': ''}

    def _rows(self, q, ttl=0):
        d = self.call('/Vod/get_list', q, ttl=ttl)
        info = d.get('info') if isinstance(d.get('info'), dict) else {}
        rows = info.get('rows') if isinstance(info.get('rows'), list) else []
        try:
            total = int(info.get('total') or 0)
        except Exception:
            total = 0
        return rows, total

    def homeContent(self, filter=False):
        classes = [{'type_id': c['type_id'], 'type_name': c['type_name']}
                   for c in self.CATS]
        filters = {}
        for c in self.CATS:
            filters[c['type_id']] = [{
                'key': 'orderby', 'name': '排序',
                'value': [{'n': '默认', 'v': ''}, {'n': '最热', 'v': 'hits'},
                          {'n': '评分', 'v': 'score'}]}]
        return {'class': classes, 'filters': filters}

    def homeVideoContent(self):
        rows, _ = self._rows(self._q('gg_new', 1), ttl=120)
        return {'list': self.vod_list(rows)[:30]}

    def categoryContent(self, tid, pg, filter, extend):
        page = int(pg) if str(pg or '').isdigit() and int(pg) > 0 else 1
        q = self._q(tid, page)
        if isinstance(extend, dict) and extend.get('orderby') not in (None, ''):
            q['orderby'] = str(extend['orderby'])
        rows, total = self._rows(q)
        items = self.vod_list(rows)
        pagecount = (max(1, (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
                     if total else page)
        return {'list': items, 'total': total or len(items),
                'page': page, 'pagecount': pagecount}

    def searchContent(self, key, quick, pg='1'):
        page = int(pg) if str(pg or '').isdigit() and int(pg) > 0 else 1
        items = self.search(key, page)
        return {'list': items, 'total': len(items), 'page': page,
                'pagecount': page}

    def detail(self, vid):
        """→ (vod, 线路列表)。vod_id 带 'g:' 前缀，门面据此区分来源、避免与 xf 的 id 撞车。"""
        vid = str(vid or '').strip()
        d = self.call('/Vod/get_detail', {'vod_id': vid}, ttl=180)
        info = d.get('info') if isinstance(d.get('info'), dict) else {}
        vod = self.vod(info) if info else None
        if not vod:
            vod = {'vod_id': vid, 'vod_name': vid, 'vod_pic': '', 'vod_remarks': ''}
        vod['vod_id'] = 'g:' + vid
        return vod, self.lines(vid)

    def search(self, kw, page=1):
        d = self.call('/Vod/get_list', self.list_params(page, kw), ttl=30)
        info = d.get('info') if isinstance(d.get('info'), dict) else {}
        rows = info.get('rows') if isinstance(info.get('rows'), list) else []
        return self.vod_list(rows)

    def match_lines(self, title):
        pick = search_best(self, title)
        if not pick:
            return []
        return self.lines(str(pick.get('vod_id')))

    def lines(self, vid):
        d = self.call('/Vod/get_detail', {'vod_id': vid}, ttl=180)
        info = d.get('info') if isinstance(d.get('info'), dict) else {}
        froms = str(info.get('vod_play_from') or '').split('$$$')
        segs = str(info.get('vod_play_url') or '').split('$$$')
        out, used = [], {}
        for i, seg in enumerate(segs):
            code = froms[i] if i < len(froms) else ''
            base = (self.LINE_NAME.get(str(code or '').strip().lower())
                    or xf_clean_name(code) or '线路')
            name = base
            if name in used:
                used[name] += 1
                name = '%s·%d' % (base, used[name])
            else:
                used[name] = 1
            items = []
            for j, part in enumerate(seg.split('#')):
                part = part.strip()
                if not part:
                    continue
                if '$' in part:
                    t, u = part.split('$', 1)
                else:
                    t, u = '', part
                u = u.strip()
                if not u or not is_video(u):
                    continue
                items.append((ep_label(t, j), name, u))
            if items:
                out.append({'name': name, 'eps': as_lines(items)})
            if len(out) >= self.MAX_LINES:
                break
        return out

    def play(self, flag, pid):
        res = {'parse': 0, 'jx': 0, 'url': '', 'header': play_header(self.host)}
        raw = str(pid or '').strip()
        if not raw:
            return res
        if raw.startswith('page:'):
            page = raw[5:]
            return {'parse': 1, 'jx': 1, 'url': page,
                    'header': play_header(self.host, page)}
        if raw.startswith('http') or raw.startswith('//'):
            u = ('https:' + raw) if raw.startswith('//') else raw
            if is_video(u):
                res['url'] = enc_url(u)
            elif is_ext_link(u):
                res.update({'parse': 1, 'jx': 1, 'url': u,
                            'header': play_header(self.host, u)})
            else:
                res['url'] = u
            return res
        if raw.isdigit():
            d = self.call('/Vod/get_detail', {'vod_id': raw}, ttl=180)
            info = d.get('info') if isinstance(d.get('info'), dict) else {}
            for seg in str(info.get('vod_play_url') or '').split('$$$'):
                for part in seg.split('#'):
                    if '$' in part:
                        u = part.split('$', 1)[1].strip()
                        if is_video(u):
                            res['url'] = enc_url(u)
                            return res
        return res


# ==================== 源 3：次元城动画（REST API，播放需登录） ====================
class CycaniSpider(object):
    TAG = 'cy'
    HOST = 'https://www.cycani.org'
    PAGE_SIZE = 18
    MAX_LINES = 3
    APP_NAME = 'cyc_web'
    APP_VERSION = 'cycweb'
    TIME_ZONE = 'Asia/Shanghai'

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.host = str(cfg.get('cyc_host') or self.HOST).rstrip('/')
        self.api = str(cfg.get('cyc_api') or (self.host + '/api')).rstrip('/')
        try:
            self.timeout = float(cfg.get('timeout') or 8)
        except Exception:
            self.timeout = 8.0
        self.username = str(cfg.get('cyc_username') or '').strip()
        self.password = str(cfg.get('cyc_password') or '').strip()
        # 旧脚本里硬编码的 Token 已于 2026-11-04 过期且无法 refresh，此处不再内置
        self.token = self._norm(str(cfg.get('cyc_token') or '').strip())
        if not self.token:
            self.token = self._load_auth()

    # ---- Token ----
    def _auth_path(self):
        try:
            return os.path.join(tempfile.gettempdir(), '.cyc_auth.json')
        except Exception:
            return ''

    def _load_auth(self):
        try:
            p = self._auth_path()
            if p and os.path.isfile(p):
                with open(p, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                return self._norm(str(d.get('token') or ''))
        except Exception:
            pass
        return ''

    def _save_auth(self):
        try:
            p = self._auth_path()
            if p and self.token:
                with open(p, 'w', encoding='utf-8') as f:
                    json.dump({'token': self.token, 'username': self.username},
                              f, ensure_ascii=False)
                _chmod600(p)     # token + 用户名，只给自己读
        except Exception:
            pass

    @staticmethod
    def _norm(t):
        s = str(t or '').strip()
        if s.lower().startswith('bearer '):
            s = s[7:].strip()
        return s

    @staticmethod
    def _jwt_exp(tok):
        try:
            p = str(tok or '').split('.')[1]
            p += '=' * ((4 - len(p) % 4) % 4)
            d = json.loads(base64.urlsafe_b64decode(p.encode('ascii')).decode('utf-8', 'ignore'))
            return float(d.get('exp') or 0)
        except Exception:
            return 0

    def _token_ok(self):
        if not self.token:
            return False
        exp = self._jwt_exp(self.token)
        return not (exp and exp < time.time() + 60)

    def logged_in(self):
        return self._token_ok()

    def _take_token(self, j):
        d = j.get('data') if isinstance(j, dict) else None
        if isinstance(d, dict):
            return self._norm(str(d.get('token') or ''))
        return self._norm(str((j or {}).get('token') or '')) if isinstance(j, dict) else ''

    def _login(self):
        if not self.username or not self.password:
            return False
        try:
            st, txt = request_ex(
                self.api + '/auth/login', 'POST',
                body={'username': self.username, 'password': self.password},
                headers=self.hdr(), timeout=self.timeout)
            tok = self._take_token(xf_loads(txt))
            if tok:
                self.token = tok
                self._save_auth()
                return True
        except Exception:
            pass
        return False

    def _refresh(self):
        if not self.token:
            return False
        try:
            st, txt = request_ex(self.api + '/auth/refresh', 'POST', body={},
                                 headers=self.hdr(auth=True), timeout=self.timeout)
            tok = self._take_token(xf_loads(txt))
            if tok:
                self.token = tok
                self._save_auth()
                return True
        except Exception:
            pass
        return False

    def _ensure_token(self):
        if self._token_ok():
            exp = self._jwt_exp(self.token)
            if exp and exp - time.time() < 259200:
                self._refresh()
            return True
        if self.token and self._refresh():
            return True
        return self._login()

    # ---- HTTP / API ----
    def hdr(self, auth=False, ref=None):
        h = {'User-Agent': XF_UA, 'Accept': 'application/json',
             'X-App-Name': self.APP_NAME, 'X-App-Version': self.APP_VERSION,
             'X-Time-Zone': self.TIME_ZONE,
             'Referer': ref or (self.host + '/'), 'Origin': self.host,
             'Accept-Encoding': 'gzip, deflate'}
        if auth and self.token:
            h['Authorization'] = 'Bearer ' + self.token
        return h

    def call(self, path, params=None, auth=False, ttl=0):
        url = self.api + path
        if params:
            url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
        st, txt = request_ex(url, 'GET', headers=self.hdr(auth),
                             timeout=self.timeout, ttl=ttl)
        if auth and st == 401 and self._ensure_token():
            st, txt = request_ex(url, 'GET', headers=self.hdr(auth),
                                 timeout=self.timeout)
        j = xf_loads(txt)
        if isinstance(j, dict) and 'data' in j:
            d = j.get('data')
            return d if isinstance(d, dict) else {}
        return j if isinstance(j, dict) else {}

    def card(self, it):
        try:
            if not isinstance(it, dict):
                return None
            vid = it.get('video_id') or it.get('id')
            if vid in (None, ''):
                return None
            remark = str(it.get('remarks') or '')
            if not remark:
                total = it.get('total')
                if isinstance(total, int) and total > 1:
                    remark = ('全%d集' % total) if it.get('completed') else ('更新至%d集' % total)
            return {'vod_id': str(vid),
                    'vod_name': str(it.get('title') or ''),
                    'vod_pic': str(it.get('cover_url') or ''),
                    'vod_remarks': remark}
        except Exception:
            return None

    def card_list(self, arr):
        out = []
        for it in arr or []:
            v = self.card(it)
            if v:
                out.append(v)
        return out

    def search(self, kw):
        d = self.call('/videos/search',
                     {'q': str(kw), 'page': 1, 'page_size': self.PAGE_SIZE}, ttl=30)
        items = d.get('list') if isinstance(d, dict) else []
        return self.card_list(items if isinstance(items, list) else [])

    def sections(self, vid, code):
        out, seen = [], set()
        base = '/videos/%s/sections' % urllib.parse.quote(str(vid), safe='')
        for page in range(1, 6):
            d = self.call(base, {'player_code': code, 'page': page, 'page_size': 100},
                         ttl=180)
            arr = d.get('list') if isinstance(d, dict) else []
            if not isinstance(arr, list) or not arr:
                break
            added = 0
            for s in arr:
                if not isinstance(s, dict):
                    continue
                sid = str(s.get('id') or '')
                if not sid or sid in seen:
                    continue
                seen.add(sid)
                out.append({'id': sid, 'title': str(s.get('title') or '')})
                added += 1
            if added == 0 or len(arr) < 100:
                break
        return out

    def match_lines(self, title):
        pick = search_best(self, title)
        if not pick:
            return []
        return self.lines(str(pick.get('vod_id')))

    def lines(self, vid):
        d = self.call('/videos/%s' % urllib.parse.quote(str(vid), safe=''), ttl=120)
        srcs = d.get('play_from') if isinstance(d.get('play_from'), list) else []
        if not srcs:
            srcs = [{'code': 'cychub', 'title': '默认线路'}]
        out = []
        for s in srcs[:self.MAX_LINES]:
            if not isinstance(s, dict):
                continue
            code = str(s.get('code') or '')
            if not code:
                continue
            name = xf_clean_name(s.get('title') or code) or code
            items = []
            for i, sec in enumerate(self.sections(vid, code)):
                t = xf_clean_name(sec.get('title')) or ('第%d集' % (i + 1))
                items.append((t, name, sec['id']))
            if items:
                out.append({'name': name, 'eps': as_lines(items)})
        return out

    def play(self, flag, pid):
        res = {'parse': 0, 'jx': 0, 'url': '', 'header': play_header(self.host)}
        raw = str(pid or '').strip()
        if not raw:
            return res
        if raw.startswith('http') or raw.startswith('//'):
            u = ('https:' + raw) if raw.startswith('//') else raw
            res['url'] = enc_url(u) if is_video(u) else u
            return res
        d = self.call('/v2/sections/%s/play-url' %
                     urllib.parse.quote(raw, safe=''), auth=True)
        u = str((d or {}).get('url') or '') if isinstance(d, dict) else ''
        if not u:
            return res
        if u.startswith('//'):
            u = 'https:' + u
        if is_ext_link(u):
            res.update({'parse': 1, 'jx': 1, 'url': u,
                        'header': play_header(self.host, u)})
        else:
            res['url'] = enc_url(u)
        return res


# ==================== 源 4：OmoFun（HTML + 聚合取流接口） ====================
class OmoFunSpider(object):
    TAG = 'om'
    HOSTS = ['https://omofun.in', 'https://omofun2.com']
    MAX_LINES = 4

    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.host = str(cfg.get('omo_host') or self.HOSTS[0]).rstrip('/')
        try:
            self.timeout = float(cfg.get('timeout') or 7)
        except Exception:
            self.timeout = 7.0
        self._dead = {}

    def hdr(self, ref=None):
        return {'User-Agent': XF_UA,
                'Accept': 'text/html,application/xhtml+xml,application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Referer': ref or (self.host + '/'),
                'x-platform': 'web',
                'x-requested-with': 'XMLHttpRequest',
                'Accept-Encoding': 'gzip, deflate'}

    def get(self, path, ttl=0, valid=None):
        key = 'omo:' + path
        if ttl:
            hit = xf_cache_get(key)
            if hit is not None:
                return hit
        hosts = [self.host] + [h for h in self.HOSTS if h != self.host]
        for h in hosts:
            if self._dead.get(h, 0) > time.time():
                continue
            st, txt = request_ex(h + path, 'GET', headers=self.hdr(h + '/'),
                                 timeout=self.timeout)
            if st and 200 <= st < 300 and txt and (not valid or valid in txt):
                self._dead.pop(h, None)
                if ttl:
                    xf_cache_put(key, txt, ttl)
                return txt
            self._dead[h] = time.time() + 60
        return ''

    def _abs(self, u):
        if not u:
            return ''
        if str(u).startswith('http'):
            return u
        return self.host + str(u)

    def parse_items(self, html):
        out = []
        try:
            blocks = re.findall(
                r'<a href="(/vod/detail/([0-9]+)\.html)"[^>]*title="([^"]*)"[^>]*class="[^"]*module-poster-item[^"]*"[^>]*>(.*?)(?=<a href="/vod/detail/|</div>\s*<div class="module-main|<div class="module-foot|$)',
                html, re.S)
            for href, vid, title, blk in blocks:
                if not title:
                    m = re.search(r'module-poster-item-title">\s*([^<]+)', blk)
                    title = m.group(1).strip() if m else ''
                m = re.search(r'module-item-note">\s*([^<]*)', blk)
                note = m.group(1).strip() if m else ''
                m = re.search(r'data-original="([^"]+)"', blk)
                pic = m.group(1) if m else ''
                out.append({'vod_id': vid, 'vod_name': title.strip(),
                            'vod_pic': self._abs(pic), 'vod_remarks': note})
        except Exception:
            pass
        if not out:
            try:
                blocks = re.findall(
                    r'<div class="module-card-item module-item">(.*?)(?=<div class="module-card-item module-item">|$)',
                    html, re.S)
                for blk in blocks:
                    m = re.search(r'href="/vod/detail/([0-9]+)\.html"', blk)
                    if not m:
                        continue
                    m2 = re.search(r'module-card-item-title">\s*<a[^>]*>\s*<strong>([^<]+)</strong>', blk)
                    title = m2.group(1).strip() if m2 else ''
                    m3 = re.search(r'data-original="([^"]+)"', blk)
                    pic = m3.group(1) if m3 else ''
                    m4 = re.search(r'module-item-note">\s*([^<]*)', blk)
                    note = m4.group(1).strip() if m4 else ''
                    out.append({'vod_id': m.group(1), 'vod_name': title,
                                'vod_pic': self._abs(pic), 'vod_remarks': note})
            except Exception:
                pass
        return out

    def dyn(self, vid, ep):
        e = str(ep or '').strip()
        if not e.startswith('ep'):
            e = 'ep' + e
        return xf_loads(self.get('/_dyn_plays/%s/%s' % (vid, e), ttl=180))

    def search(self, kw):
        path = '/vod/search.html?wd=%s&page=1' % urllib.parse.quote(str(kw))
        return self.parse_items(self.get(path, ttl=30, valid='/vod/'))

    def match_lines(self, title):
        pick = search_best(self, title)
        if not pick:
            return []
        return self.lines(str(pick.get('vod_id')))

    def lines(self, vid):
        html = self.get('/vod/detail/%s.html' % vid, ttl=180, valid='/vod/')
        if not html:
            return []
        eps = re.findall(
            r'<a class="module-play-list-link" href="/vod/play/([0-9]+)/ep([0-9]+)\.html"[^>]*>\s*<span>([^<]+)</span>',
            html)
        if not eps:
            eps = [(v, e, t) for v, e, t in re.findall(
                r'href="/vod/play/([0-9]+)/ep([0-9]+)\.html"[^>]*>\s*(?:<span>)?([^<]+)', html)]
        seen, ep_list = set(), []
        for v, e, t in eps:
            k = (v, e)
            if k in seen:
                continue
            seen.add(k)
            ep_list.append((v, e, xf_clean_name(t) or '正片'))
        if not ep_list:
            ep_list = [(vid, '1', 'HD')]

        plays = self.dyn(vid, ep_list[0][1]).get('video_plays') or []
        sites = []
        for p in plays:
            if not isinstance(p, dict):
                continue
            u = p.get('play_data') or ''
            if u and is_video(u):
                s = xf_clean_name(p.get('src_site') or '线路')
                if s and s not in sites:
                    sites.append(s)
        sites = sorted(sites)[:self.MAX_LINES] or ['OmoFun解析']
        out = []
        for s in sites:
            items = [(t, s, '%s/ep%s' % (v, e)) for v, e, t in ep_list]
            out.append({'name': s, 'eps': as_lines(items)})
        return out

    def play(self, flag, pid):
        res = {'parse': 0, 'jx': 0, 'url': '', 'header': play_header(self.host)}
        raw = str(pid or '').strip().replace('!parse', '')
        if not raw:
            return res
        parts = raw.split('/')
        if len(parts) == 2:
            vid, ep = parts
        elif len(parts) >= 3:
            vid, ep = parts[-2], parts[-1]
        else:
            return res
        plays = self.dyn(vid, ep).get('video_plays') or []
        cands = []
        for p in plays:
            if isinstance(p, dict) and p.get('play_data'):
                cands.append((xf_clean_name(p.get('src_site') or ''), p.get('play_data')))
        pick = ''
        for s, u in cands:
            if s == flag and is_video(u):
                pick = u
                break
        if not pick:
            for s, u in cands:
                if is_video(u):
                    pick = u
                    break
        if not pick and cands:
            pick = cands[0][1]
        if pick and is_video(pick):
            res['url'] = enc_url(pick)
        else:
            res['parse'] = 1
            res['jx'] = 1
            res['url'] = pick or (self.host + '/vod/play/' + raw + '.html')
        return res


# ==================== 门面：TVBox 协议入口 ====================
class XifanAggSpider(_SpiderBase):
    """首页/分类/搜索 = 稀饭动漫；详情页 = 四源线路聚合。

    线路顺序（用户 2026-11-04 指定）：xf > gg > cy > om。
    TVBox 默认播放第一条线路，因此该顺序同时是默认选线顺序。
    """

    LINE_ORDER = ('xf', 'gg', 'cy', 'om')      # 稀饭 → GiriGiri → 次元城 → OmoFun
    LABELS = {'xf': '稀饭', 'gg': 'GiriGiri', 'cy': '次元城', 'om': 'OmoFun'}
    MAX_LINES_PER_SRC = 4
    CACHE_TTL = 300

    # 类级兜底：有些壳只调 init() 不调 __init__()
    order = list(LINE_ORDER)
    detail_budget = 7.0
    sources = {}
    xf = None
    cy = None
    cfg = {}

    def __init__(self):
        self.cfg = {}
        self.order = list(self.LINE_ORDER)
        self.detail_budget = 7.0
        self._build({})

    def _build(self, cfg):
        self.xf = XifanSpider(cfg)
        self.cy = CycaniSpider(cfg)
        self.sources = {
            'xf': self.xf,
            'gg': GirigiriSpider(cfg),
            'cy': self.cy,
            'om': OmoFunSpider(cfg),
        }

    def _x(self):
        if self.xf is None:
            self._build({})
        return self.xf

    def init(self, extend=''):
        cfg = {}
        try:
            if isinstance(extend, dict):
                cfg = dict(extend)
            elif isinstance(extend, str) and extend.strip().startswith('{'):
                cfg = json.loads(extend)
        except Exception:
            cfg = {}
        if not isinstance(cfg, dict):
            cfg = {}
        self.cfg = cfg
        self._build(cfg)
        order = cfg.get('lines')
        if isinstance(order, (list, tuple)) and order:
            picked = [str(t).strip() for t in order
                      if str(t).strip() in self.sources]
            self.order = picked or list(self.LINE_ORDER)
        else:
            self.order = list(self.LINE_ORDER)
        try:
            self.detail_budget = max(2.0, min(20.0,
                                              float(cfg.get('detail_budget') or 7)))
        except Exception:
            self.detail_budget = 7.0
        self._probe()
        return None

    def _probe(self):
        """后台探活 xifan：它的 API 会整站超时，不能在首页路径上白等。

        探活完成前先按「不可用」处理（首页直接走 GiriGiri，约 0.8s 出内容），
        探到通了再切回 xifan 的 17 个分类。
        """
        xf = self._x()
        if xf is None:
            return
        try:
            xf.alive = False
            xf._cool = time.time() + 4.0      # 探活期间别被 health() 提前放行
        except Exception:
            return

        def run():
            try:
                st, _ = request_ex(xf.api + '/rest/v1/', 'GET',
                                   headers=xf.hdr(), timeout=3)
                xf._mark(bool(st and st < 500))
            except Exception:
                pass

        if threading:
            try:
                th = threading.Thread(target=run)
                th.daemon = True
                th.start()
                return
            except Exception:
                pass
        run()          # 没有 threading 时同步探一次（上限 3s）

    def getName(self):
        return '稀饭聚合'

    def destroy(self):
        pool_clear()
        return None

    def isVideoFormat(self, url):
        return is_video(url)

    def manualVideoCheck(self):
        return False

    # ---------- 首页数据：主源优先 xifan，其 API 挂了自动切 GiriGiri ----------
    def _main(self):
        xf = self._x()
        if xf is not None:
            if getattr(xf, 'alive', True):
                return xf, 'xf'
            # 冷却到期不再当场重试（那会把首页卡住 4s），改用后台探活，
            # 这次仍走 gg，探通了下一轮请求自动切回来
            if time.time() > getattr(xf, '_cool', 0):
                self._probe()
        return self.sources.get('gg') or xf, 'gg'

    def _alive(self, tag):
        """该源当前是否值得发请求（主要是 xifan 会整站超时）。"""
        if tag == 'xf':
            try:
                return bool(self._x() and getattr(self._x(), 'alive', True))
            except Exception:
                return False
        return tag in self.sources

    def _tagged(self, res, tag):
        """主源为 gg 时给列表 id 打 'g:' 前缀，详情页才能知道该回哪个源取数据。"""
        if tag != 'gg' or not isinstance(res, dict):
            return res
        for it in (res.get('list') or []):
            try:
                vid = str(it.get('vod_id') or '')
                if vid and not vid.startswith('g:'):
                    it['vod_id'] = 'g:' + vid
            except Exception:
                pass
        return res

    def homeContent(self, filter):
        src, tag = self._main()
        return src.homeContent(filter)

    def homeVideoContent(self):
        src, tag = self._main()
        return self._tagged(src.homeVideoContent(), tag)

    def categoryContent(self, tid, pg, filter, extend):
        src, tag = self._main()
        return self._tagged(src.categoryContent(tid, pg, filter, extend), tag)

    def searchContent(self, key, quick, pg='1'):
        src, tag = self._main()
        return self._tagged(src.searchContent(key, quick, pg), tag)

    # ---------- 详情：主源取基础信息 + 四源线路聚合 ----------
    def detailContent(self, ids):
        try:
            raw = str(ids[0] if isinstance(ids, (list, tuple)) and ids else (ids or ''))
            raw = raw.strip()
            # 'g:' 前缀 = 来自 GiriGiri（备用主源）；纯数字 = 来自 xifan。
            # 两个站点的 id 空间互不相通，必须靠前缀区分，否则会串片。
            by_gg = raw.startswith('g:')
            aid = re.sub(r'[^0-9]', '', raw)
            if not aid:
                return {'list': []}

            ck = 'agg3:%s:%s:%s' % ('g' if by_gg else 'x', aid, ','.join(self.order))
            hit = xf_cache_get(ck)
            if hit is not None:
                try:
                    return json.loads(hit)
                except Exception:
                    pass

            if by_gg:
                main_tag = 'gg'
                vod, main_lines = self.sources['gg'].detail(aid)
            else:
                if not self._alive('xf'):
                    # xifan 的 API 整站超时中：历史收藏的纯数字 id 已无从解析，
                    # 直接返回空，别让详情页卡几十秒
                    return {'list': []}
                main_tag = 'xf'
                vod, main_lines = self._x().detail(aid)
                if not main_lines:
                    # 瞬时抖动（CDN 换节点 / 秒断）时重试一次；失败响应不进缓存，
                    # 因此第二次是真实重发，不会把等待翻倍到不可接受
                    time.sleep(0.2)
                    vod, main_lines = self._x().detail(aid)
            title = str(vod.get('vod_name') or '')

            # 其余三源并发按标题匹配；慢源超时即跳过，不拖累整体
            boxes = {}
            ths = []
            for tag in self.order:
                if tag == main_tag or not self._alive(tag):
                    continue
                src = self.sources.get(tag)
                if not src:
                    continue

                def work(t=tag, s=src, w=title):
                    try:
                        boxes[t] = s.match_lines(w)
                    except Exception:
                        boxes[t] = []

                if threading:
                    try:
                        th = threading.Thread(target=work)
                        th.daemon = True
                        th.start()
                        ths.append(th)
                    except Exception:
                        work()
                else:
                    work()
            deadline = time.time() + self.detail_budget
            for th in ths:
                try:
                    th.join(max(0.05, deadline - time.time()))
                except Exception:
                    pass

            cy_need_login = ('cy' in self.order and self.cy is not None
                             and not self.cy.logged_in())
            froms, urls, used, tail = [], [], {}, []
            for tag in self.order:
                lines = main_lines if tag == main_tag else (boxes.get(tag) or [])
                label = self.LABELS.get(tag, tag)
                for line in (lines or [])[:self.MAX_LINES_PER_SRC]:
                    if not isinstance(line, dict):
                        continue
                    raw_name = str(line.get('name') or '线路')
                    base = xf_clean_name(label + '·' + raw_name) or label
                    if tag == 'cy' and cy_need_login:
                        base += '(需登录)'
                    name = base
                    if name in used:
                        used[name] += 1
                        name = '%s·%d' % (base, used[name])
                    else:
                        used[name] = 1
                    segs = []
                    for ep in as_lines(line.get('eps')):
                        code = enc_pid(tag, ep[1], ep[2])
                        if code:
                            segs.append('%s$%s' % (ep[0] or '正片', code))
                    if not segs:
                        continue
                    # 需要壳嗅探的「网页解析」兜底线路统一排到最后
                    if '网页解析' in raw_name:
                        tail.append((name, '#'.join(segs)))
                    else:
                        froms.append(name)
                        urls.append('#'.join(segs))
            for name, joined in tail:
                froms.append(name)
                urls.append(joined)

            vod['vod_play_from'] = '$$$'.join(froms)
            vod['vod_play_url'] = '$$$'.join(urls)

            if cy_need_login:
                if self.cy.username and self.cy.password:
                    tip = '[次元城] 已配置账号，播放时将自动登录。'
                else:
                    tip = ('[次元城线路需登录] 请在源配置 extend 填 cyc_username / '
                           'cyc_password，或填浏览器复制的 cyc_token。')
                vod['vod_content'] = (
                    str(vod.get('vod_content') or '') + NL + NL + tip).strip()

            result = {'list': [vod]}
            # 只缓存序列化文本：避免把同一个可变 dict 交给壳后被改写污染缓存
            try:
                xf_cache_put(ck, json.dumps(result, ensure_ascii=False), self.CACHE_TTL)
            except Exception:
                pass
            return result
        except Exception:
            return {'list': []}

    # ---------- 播放：按线路 tag 派发回原源 ----------
    def playerContent(self, flag, id, vipFlags):
        res = {'parse': 0, 'jx': 0, 'url': '',
               'header': play_header(self._x().host)}
        try:
            raw = str(id or '').strip()
            if not raw:
                return res
            low = raw.upper()
            if '%7C' in low or '%24' in low or '%3A' in low:
                try:
                    raw = urllib.parse.unquote(raw)
                except Exception:
                    pass
            tag, inner_flag, pid = dec_pid(raw)
            src = self.sources.get(tag) if tag else None
            if src and pid:
                return src.play(inner_flag or flag, pid)
            if raw.startswith('http') or raw.startswith('playpage:') or raw.startswith('page:'):
                return self._x().play(flag, raw)
        except Exception:
            pass
        return res

    def localProxy(self, param):
        """m3u8 相对分片改写（四源通用）"""
        try:
            url = ''
            if isinstance(param, dict):
                url = str(param.get('url') or param.get('u') or '')
            elif isinstance(param, str):
                p = param.strip()
                if p.startswith('http'):
                    url = p
                else:
                    qs = urllib.parse.parse_qs(urllib.parse.urlsplit(p).query)
                    url = str((qs.get('url') or qs.get('u') or [''])[0])
            if not url:
                return None
            st, txt = request_ex(
                url, 'GET',
                headers={'User-Agent': XF_UA, 'Accept': '*/*',
                         'Referer': self._x().host + '/'}, timeout=8)
            if not txt or '#EXTM3U' not in txt:
                return None
            base = url.rsplit('/', 1)[0] + '/'
            out = []
            for line in txt.splitlines():
                s = line.strip()
                if not s:
                    out.append('')
                elif s.startswith('#'):
                    m = re.search(r'URI="([^"]+)"', s)
                    if m:
                        s = s.replace(m.group(1), abs_url(base, m.group(1)))
                    out.append(s)
                else:
                    out.append(abs_url(base, s))
            return [200, 'application/vnd.apple.mpegurl', NL.join(out)]
        except Exception:
            return None


# ======================================================================
# 模块：ff
# ======================================================================
# -*- coding: utf-8 -*-
# FoFo影院 (www.fofo33.com) TVBox / OK影视 Python 爬虫
# ------------------------------------------------------------
# 站点结构（实测 2026-11）：
#   - 站点无开放 JSON API（/api.php 全部回退 HTML），故走 HTML 解析
#   - 分类页:  /{dianying|dianshiju|zongyi|dongman}/{类型}-{地区}-{年代}-{排序}?page=N
#   - 搜索页:  /search?q=关键词&page=N（无结果时回吐推荐，必须本地关键词二次过滤）
#   - 详情页:  /{cat}/{vid}，内嵌 var urlList = decryptDict({...}) 恺撒位移(-1)加密的线路数据
#   - 取播放:  POST /source/  body: id={sid}  → 纯文本 m3u8/mp4 直链
#   - web-sign: 站点未启用（预留注入槽位）



class FofoSpider(_BaseSpider):

    HOST = 'https://www.fofo33.com'
    UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    TIMEOUT = 15

    # 旧配置 tid(1/2/3/4) → 站点真实分类路径
    TID_MAP = {'1': 'dianying', '2': 'dianshiju', '3': 'zongyi', '4': 'dongman'}
    CATS = [
        {'type_id': 'dianying', 'type_name': '电影'},
        {'type_id': 'dianshiju', 'type_name': '剧集'},
        {'type_id': 'zongyi', 'type_name': '综艺'},
        {'type_id': 'dongman', 'type_name': '动漫'},
    ]
    TYPE_MAP = {
        'dianying': [('0', '全部'), ('1', '剧情'), ('2', '喜剧'), ('3', '动作'), ('4', '爱情'),
                     ('5', '科幻'), ('6', '悬疑'), ('7', '惊悚'), ('8', '恐怖'), ('9', '犯罪'),
                     ('10', '同性'), ('11', '音乐'), ('12', '歌舞'), ('13', '传记'), ('14', '历史'),
                     ('15', '战争'), ('16', '西部'), ('17', '奇幻'), ('18', '冒险'), ('19', '灾难'),
                     ('20', '武侠'), ('21', '伦理')],
        'dianshiju': [('0', '全部'), ('1', '剧情'), ('2', '喜剧'), ('3', '动作'), ('4', '爱情'),
                      ('5', '科幻'), ('6', '悬疑'), ('7', '惊悚'), ('8', '恐怖'), ('9', '犯罪'),
                      ('10', '同性'), ('11', '音乐'), ('12', '歌舞'), ('13', '传记'), ('14', '历史'),
                      ('15', '战争'), ('16', '西部'), ('17', '奇幻'), ('18', '冒险'), ('19', '灾难'),
                      ('20', '武侠'), ('21', '伦理')],
        'zongyi': [('0', '全部'), ('1', '真人秀'), ('2', '脱口秀'), ('3', '纪录片'),
                   ('4', '传记'), ('5', '歌舞')],
        'dongman': [('0', '全部'), ('1', '剧情'), ('2', '喜剧'), ('3', '动作'), ('4', '爱情'),
                    ('5', '科幻'), ('6', '悬疑'), ('7', '惊悚'), ('8', '恐怖'), ('9', '犯罪'),
                    ('10', '同性'), ('11', '音乐'), ('12', '歌舞'), ('13', '传记'), ('14', '历史'),
                    ('15', '战争'), ('16', '西部'), ('17', '奇幻'), ('18', '冒险'), ('19', '灾难'),
                    ('20', '武侠'), ('21', '伦理')],
    }
    AREA_MAP = [('0', '全部'), ('1', '中国大陆'), ('2', '美国'), ('3', '香港'), ('4', '台湾'),
                ('5', '日本'), ('6', '韩国'), ('7', '英国'), ('8', '法国'), ('9', '德国'),
                ('10', '意大利'), ('11', '西班牙'), ('12', '印度'), ('13', '泰国'), ('14', '俄罗斯'),
                ('15', '伊朗'), ('16', '加拿大'), ('17', '澳大利亚'), ('18', '爱尔兰'),
                ('19', '瑞典'), ('20', '巴西'), ('21', '丹麦')]
    YEARS = [('0', '全部')] + [(str(y), str(y)) for y in range(2026, 2004, -1)] + [('1', '其他')]
    SORTS = [('0', '最新'), ('1', '热门'), ('2', '高分')]

    def __init__(self):
        self.host = self.HOST
        self.extend = ''
        self._line_cache = {}   # detail path -> 解析后的线路数据
        self._detail_cache = {} # detail path -> vod 基础信息

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------
    def init(self, extend=""):
        try:
            self.extend = extend or ''
            if isinstance(extend, str) and extend.strip().startswith('{'):
                ext = json.loads(extend)
                if isinstance(ext, dict) and ext.get('host'):
                    self.host = str(ext['host']).strip().rstrip('/')
        except Exception:
            pass

    def getName(self):
        return 'FoFo影院'

    def destroy(self):
        try:
            self._line_cache.clear()
            self._detail_cache.clear()
        except Exception:
            pass

    def isVideoFormat(self, url):
        # 选集字符串可能带 # 后缀（如 .m3u8#下一集），先剥离再判断
        try:
            url = str(url or '').split('#')[0].split('?')[0].lower()
            return any(url.endswith(ext) for ext in
                       ('.m3u8', '.mp4', '.mkv', '.flv', '.avi', '.ts', '.webm'))
        except Exception:
            return False

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return []

    # ------------------------------------------------------------------
    # 基础网络封装
    # ------------------------------------------------------------------
    def _headers(self, referer='', web_sign=''):
        h = {
            'User-Agent': self.UA,
            'Accept': 'text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8',
            'Referer': referer or (self.host + '/'),
            'x-platform': 'web',
            'x-requested-with': 'XMLHttpRequest',
        }
        # 站点当前不需要 web-sign；若后续启用，在此注入
        if web_sign:
            h['web-sign'] = web_sign
        return h

    def _api_get(self, url, referer=''):
        """GET + JSON 解析，容错返回 {}"""
        try:
            import urllib.request
            req = urllib.request.Request(url, headers=self._headers(referer))
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as resp:
                return json.loads(resp.read().decode('utf-8', 'ignore'))
        except Exception:
            return {}

    def _html_get(self, url, referer=''):
        try:
            import urllib.request
            req = urllib.request.Request(url, headers=self._headers(referer))
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as resp:
                return resp.read().decode('utf-8', 'ignore')
        except Exception:
            return ''

    def _source_post(self, sid, referer=''):
        """POST /source/ 取 m3u8/mp4 直链（纯文本返回）"""
        try:
            import urllib.request
            data = urllib.parse.urlencode({'id': str(sid)}).encode('utf-8')
            h = self._headers(referer)
            h['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            req = urllib.request.Request(self.host + '/source/', data=data, headers=h)
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as resp:
                return resp.read().decode('utf-8', 'ignore').strip()
        except Exception:
            return ''

    # ------------------------------------------------------------------
    # 恺撒解密（站点 decryptDict 逻辑：字符 charCode -1）
    # ------------------------------------------------------------------
    def _shift(self, s):
        try:
            return ''.join(chr(ord(c) - 1) for c in s)
        except Exception:
            return s

    def _decrypt_dict(self, val):
        try:
            if isinstance(val, list):
                return [self._decrypt_dict(x) for x in val]
            if isinstance(val, dict):
                return {self._shift(k): self._decrypt_dict(v) for k, v in val.items()}
            if isinstance(val, str):
                s = self._shift(val)
                # 与站点 JS 一致：对解密结果尝试 JSON.parse
                # （字符串值多为 "\uXXXX" 形式的 JSON 字符串字面量，需解码为中文）
                if s[:1] in ('"', '[', '{'):
                    try:
                        return json.loads(s)
                    except Exception:
                        return s
                return s
            return val
        except Exception:
            return val

    def _extract_urllist(self, html):
        """从详情页提取并解密内嵌线路数据"""
        try:
            m = re.search(r'var\s+urlList\s*=\s*decryptDict\((\{.*?\})\)', html, re.S)
            if not m:
                return {'source': [], 'url_list': []}
            raw = m.group(1).replace("'", '"')
            data = json.loads(raw)
            out = {}
            for k, v in data.items():
                out[self._shift(k)] = self._decrypt_dict(v)
            sources = out.get('source') or []
            url_list = out.get('url_list') or []
            if not isinstance(url_list, list):
                url_list = []
            return {'source': sources, 'url_list': url_list}
        except Exception:
            return {'source': [], 'url_list': []}

    # ------------------------------------------------------------------
    # HTML 列表解析
    # ------------------------------------------------------------------
    def _parse_items(self, html):
        """解析列表页/搜索页 <li> 条目，返回 vod 列表"""
        result = []
        try:
            for block in re.findall(r'<li>(.*?)</li>', html, re.S):
                if 'class="thumbnail"' not in block:
                    continue
                m = re.search(
                    r'href="/(dianying|dianshiju|zongyi|dongman)/(\d+)"[^>]*class="thumbnail"',
                    block)
                if not m:
                    continue
                cat, vid = m.group(1), m.group(2)
                img = ''
                mi = re.search(r'src="([^"]+)"[^>]*class="thumb"', block)
                if not mi:
                    mi = re.search(r'class="thumb"[^>]*src="([^"]+)"', block)
                if mi:
                    img = mi.group(1)
                note = ''
                mn = re.search(r'class="note"[^>]*>\s*<span>([^<]*)</span>', block)
                if mn:
                    note = mn.group(1).strip()
                title = ''
                mt = re.search(r'<h2><a[^>]*>([^<]+)</a></h2>', block)
                if mt:
                    title = mt.group(1).strip()
                if not title:
                    mt = re.search(r'alt="([^"]+)"', block)
                    if mt:
                        title = mt.group(1).strip()
                if not title or not vid:
                    continue
                result.append({
                    'vod_id': cat + '/' + vid,
                    'vod_name': title,
                    'vod_pic': img,
                    'vod_remarks': note,
                })
        except Exception:
            pass
        return result

    def _parse_pagecount(self, html, cur_pg, per_page=24):
        try:
            pages = [int(x) for x in re.findall(r'[?&]page=(\d+)', html)]
            if pages:
                return max(pages)
            # 无分页链接时按是否满页外推
            return cur_pg + 1 if html.count('class="thumbnail"') >= per_page else cur_pg
        except Exception:
            return cur_pg

    def _strip_tags(self, s):
        try:
            return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or '')).strip()
        except Exception:
            return (s or '').strip()

    # ------------------------------------------------------------------
    # 内容方法
    # ------------------------------------------------------------------
    def homeContent(self, filter):
        classes = [{'type_id': c['type_id'], 'type_name': c['type_name']} for c in self.CATS]
        filters = {}
        for c in self.CATS:
            filters[c['type_id']] = [
                {'key': 'type', 'name': '类型',
                 'value': [{'n': n, 'v': v} for v, n in self.TYPE_MAP[c['type_id']]]},
                {'key': 'area', 'name': '地区',
                 'value': [{'n': n, 'v': v} for v, n in self.AREA_MAP]},
                {'key': 'year', 'name': '年代',
                 'value': [{'n': n, 'v': v} for v, n in self.YEARS]},
                {'key': 'sort', 'name': '排序',
                 'value': [{'n': n, 'v': v} for v, n in self.SORTS]},
            ]
        return {'class': classes, 'filters': filters}

    def homeVideoContent(self):
        try:
            html = self._html_get(self.host + '/')
            items = self._parse_items(html)
            seen, result = set(), []
            for it in items:
                if it['vod_id'] in seen:
                    continue
                seen.add(it['vod_id'])
                result.append(it)
            return {'list': result[:30]}
        except Exception:
            return {'list': []}

    def _norm_tid(self, tid):
        try:
            tid = str(tid or '1').strip()
            if tid in self.TID_MAP:
                return self.TID_MAP[tid]
            if tid in self.TID_MAP.values():
                return tid
            names = {c['type_name']: c['type_id'] for c in self.CATS}
            return names.get(tid, 'dianying')
        except Exception:
            return 'dianying'

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg) if str(pg).strip().isdigit() else 1
        cat = self._norm_tid(tid)
        ext = {}
        try:
            if isinstance(extend, str) and extend.strip():
                ext = json.loads(extend)
            elif isinstance(extend, dict):
                ext = extend
        except Exception:
            ext = {}
        t = str(ext.get('type') or '0')
        a = str(ext.get('area') or '0')
        y = str(ext.get('year') or '0')
        s = str(ext.get('sort') or '0')
        path = '%s-%s-%s-%s' % (re.sub(r'\D', '', t) or '0',
                                re.sub(r'\D', '', a) or '0',
                                re.sub(r'\D', '', y) or '0',
                                re.sub(r'\D', '', s) or '0')
        result = {'list': [], 'total': 0, 'page': pg, 'pagecount': pg}
        try:
            url = '%s/%s/%s?page=%d' % (self.host, cat, path, pg)
            html = self._html_get(url)
            items = self._parse_items(html)
            # 本地二次过滤：仅保留当前分类条目（防接口混类）
            items = [it for it in items if it['vod_id'].startswith(cat + '/')]
            # 过滤后条目 < 8 时补抓后续 2 页
            extra_pages = []
            if len(items) < 8:
                fetch_pg = pg
                for _ in range(2):
                    fetch_pg += 1
                    html2 = self._html_get('%s/%s/%s?page=%d' % (self.host, cat, path, fetch_pg))
                    items2 = [it for it in self._parse_items(html2)
                              if it['vod_id'].startswith(cat + '/')]
                    extra_pages.append(html2)
                    items.extend(items2)
                    if len(items) >= 8:
                        break
            seen = set()
            uniq = []
            for it in items:
                if it['vod_id'] in seen:
                    continue
                seen.add(it['vod_id'])
                uniq.append(it)
            pagecount = self._parse_pagecount(html, pg)
            for h2 in extra_pages:
                pagecount = max(pagecount, self._parse_pagecount(h2, pg))
            result = {
                'list': uniq,
                'total': max(pagecount, pg) * 24,
                'page': pg,
                'pagecount': max(pagecount, pg),
            }
        except Exception:
            pass
        return result

    def searchContent(self, key, quick, pg="1"):
        pg = int(pg) if str(pg).strip().isdigit() else 1
        try:
            url = '%s/search?q=%s&page=%d' % (
                self.host, urllib.parse.quote(str(key or '').strip()), pg)
            html = self._html_get(url)
            items = self._parse_items(html)
            # 站点搜索无结果时会回吐推荐列表，必须本地关键词过滤
            kw = str(key or '').strip().lower()
            if kw:
                items = [it for it in items if kw in it['vod_name'].lower()]
            pagecount = pg + 1 if html.count('class="thumbnail"') >= 24 else pg
            return {'list': items, 'total': pagecount * 24,
                    'page': pg, 'pagecount': pagecount}
        except Exception:
            return {'list': [], 'total': 0, 'page': pg, 'pagecount': pg}

    def detailContent(self, ids):
        try:
            raw = ids[0] if isinstance(ids, list) and ids else str(ids)
            raw = str(raw).strip().strip('/')
            paths = []
            if '/' in raw:
                paths.append(raw)
            else:
                # 旧配置纯数字 id：轮询四个分类定位详情页
                for cat in ('dianying', 'dianshiju', 'zongyi', 'dongman'):
                    paths.append(cat + '/' + raw)
            html, path = '', paths[0]
            for p in paths:
                html = self._html_get('%s/%s' % (self.host, p))
                if html and 'urlList' in html:
                    path = p
                    break
            if not html:
                return {'list': []}
            cat = path.split('/')[0]
            vid = path.split('/')[1] if '/' in path else path

            # ---- 基础信息 ----
            title, year = '', ''
            mt = re.search(r'<h1 class="product-title">(.*?)</h1>', html, re.S)
            if mt:
                raw_t = mt.group(1)
                my = re.search(r'<span>\s*\((\d{4})\)\s*</span>', raw_t)
                if my:
                    year = my.group(1)
                title = self._strip_tags(re.sub(r'<span.*?</span>', ' ', raw_t, flags=re.S))
            mi = re.search(r'class="product-header">\s*<img[^>]*src="([^"]+)"', html)
            cover = mi.group(1) if mi else ''

            director, actor, vod_class, area, desc = '', '', '', '', ''
            for label, holder in (('导演', 'director'), ('主演', 'actor'),
                                  ('类型', 'cls'), ('制片国家/地区', 'area'), ('剧情简介', 'desc')):
                mm = re.search(r'class="product-excerpt">\s*' + re.escape(label) +
                               r'：\s*<span>(.*?)</span>', html, re.S)
                if not mm:
                    continue
                val = self._strip_tags(mm.group(1))
                if holder == 'director':
                    director = val
                elif holder == 'actor':
                    actor = val
                elif holder == 'cls':
                    vod_class = val.replace(' ', '')
                elif holder == 'area':
                    area = val
                elif holder == 'desc':
                    desc = val

            # ---- 线路数据（聚合解密） ----
            data = self._extract_urllist(html)
            play_from, play_urls, remarks = self._build_sources(data, path)
            if not remarks and year:
                remarks = year

            vod = {
                'vod_id': path,
                'vod_name': title or vid,
                'vod_pic': cover,
                'type_name': vod_class,
                'vod_year': year,
                'vod_area': area,
                'vod_director': director,
                'vod_actor': actor,
                'vod_content': desc,
                'vod_remarks': remarks,
                'vod_play_from': play_from,
                'vod_play_url': play_urls,
            }
            self._detail_cache[path] = vod
            return {'list': [vod]}
        except Exception:
            return {'list': []}

    def _build_sources(self, data, path):
        """
        组装播放线路：
        1) 优先取内嵌线路数据（每集 sid 经 POST /source/ 兑换 m3u8/mp4 直链），
           线路按名称排序，最多 4 条；
        2) 无任何直链线路时兜底详情页；
        3) 最后追加一条解析线路（交由壳内 webview 播放详情页）。
        """
        try:
            sources = data.get('source') or []
            url_list = data.get('url_list') or []
            lines = []
            for i, name in enumerate(sources):
                if i >= len(url_list):
                    break
                eps = url_list[i]
                if not isinstance(eps, list) or not eps:
                    continue
                clean = re.sub(r'\(\d+\)\s*$', '', str(name or ('线路%d' % (i + 1)))).strip()
                lines.append((clean or ('线路%d' % (i + 1)), eps))
            lines.sort(key=lambda x: x[0])
            lines = lines[:4]

            play_from, play_urls, remarks = [], [], ''
            for name, eps in lines:
                flags = []
                for ep in eps:
                    try:
                        # 解密后键名为 title/sid/name，兼容加密原名 ujumf/tje/obnf
                        ep_title = str(ep.get('title') or ep.get('ujumf') or '播放').strip()
                        sid = str(ep.get('sid') or ep.get('tje') or '').strip()
                    except Exception:
                        ep_title, sid = '播放', ''
                    if not sid:
                        continue
                    flags.append('%s$%s@%s' % (ep_title, sid, path))
                if flags:
                    play_from.append(name)
                    play_urls.append('#'.join(flags))
                    if not remarks:
                        first = eps[0]
                        try:
                            remarks = str(first.get('title') or first.get('ujumf') or '').strip()
                            if len(eps) > 1:
                                remarks = '全%d集' % len(eps)
                        except Exception:
                            remarks = ''
            if not play_from:
                play_from.append('网页解析')
                play_urls.append('立即播放$web@%s' % path)
            else:
                play_from.append('网页解析')
                play_urls.append('立即播放$web@%s' % path)
            return '$$$'.join(play_from), '$$$'.join(play_urls), remarks
        except Exception:
            return '网页解析', '立即播放$web@%s' % path, ''

    def playerContent(self, flag, id, vipFlags):
        play_id = str(id or '').strip()
        result = {
            'parse': 1, 'jx': 1, 'url': '',
            'header': json.dumps({'User-Agent': self.UA, 'Referer': self.host + '/'}),
        }
        try:
            if '@' in play_id:
                sid, path = play_id.split('@', 1)
            else:
                sid, path = play_id, ''
            detail_url = '%s/%s' % (self.host, path) if path else self.host + '/'
            # 站外/网页解析线路 → 交壳解析
            if sid == 'web' or not sid:
                result['parse'] = 1
                result['jx'] = 1
                result['url'] = detail_url
                return result
            # 直链：POST /source/ 兑换 m3u8/mp4
            text = self._source_post(sid, referer=detail_url)
            text = text.strip().strip('"')
            if text and self.isVideoFormat(text):
                result['parse'] = 0
                result['jx'] = 0
                result['url'] = text
                result['header'] = json.dumps({
                    'User-Agent': self.UA,
                    'Referer': detail_url,
                    'x-platform': 'web',
                    'x-requested-with': 'XMLHttpRequest',
                })
                return result
            # 兑换失败 → 兜底交壳解析详情页
            result['parse'] = 1
            result['jx'] = 1
            result['url'] = detail_url
        except Exception:
            try:
                result['parse'] = 1
                result['jx'] = 1
                result['url'] = self.host + '/'
            except Exception:
                pass
        return result


# ======================================================================
# 模块：sz
# ======================================================================
# -*- coding: utf-8 -*-
"""
================================================================================
 小山影视源 · CatVod / Box  Python Spider
================================================================================
 后端   : http://43.248.128.122:578
 账号   : sukeke / sukeke.1   (已内置,可在 init 参数中覆盖)
 依赖   : requests (无则退回 urllib)

 已完整验证的链路
 ----------------------------------------------------------------------------
  1. 登录       POST /api/v1/user/login      {"Username","Password","device_id"}
  2. 密钥交换   GET  /api/v1/security/challenge  →  POST /api/v1/security/init
                → session_id + sign_key
  3. 列表/搜索  GET  /api/v1/search?wd=*&type=<分类>&page=<页>
                → data.hits[]   (wd=* 为通配,配合 type 即分类全量)
  4. 详情       GET  /api/v1/video/detail?id=<vod_id>
                → data.vod_info.vod_url_with_player[]  每条线路带 tk 票根
  5. 换票       POST /api/v1/vod/ticket       body {"token": "<tk完整值>"}
                → data.ticket  (play_ticket, 内含 parse_api / data.url / 有效期)
  6. 取流       按 parse_api 分三种形态解析:
                 · 相对路径  /api/v1/vod/parse?code=..&t=..&url=
                        → 拼 BASE 后 GET,服务端直接吐播放地址
                 · 外部解析  https://.../json_api.php?key=..&vid={md5}
                        → {md5} 用 data.url 替换,返回 JSON 取 url
                 · 外部解析  https://.../api/?key=..&url=
                        → url= 后拼 data.url,返回 JSON 取 url
  7. 推荐       GET  /api/v1/video/recommend?id=<vod_id>

 注意:device_id 必须与账号已绑定的设备一致(每个新 device_id 占一个设备配额,
      超了会报"设备数量已达上限")。下方已预置可用设备号。
================================================================================
"""
# 原脚本漏了 urllib.request（只用 parse 却调 request，壳里必崩）；本文件顶部已导入
# 后端是境内明文 IP，走系统代理反而会被拦，统一用直连 opener
_DIRECT = urllib.request.build_opener(urllib.request.ProxyHandler({}))

try:
    import requests
except Exception:
    requests = None


try:
    from base.spider import Spider as BaseSpider
except Exception:
    class BaseSpider(object):
        def init(self, extend=""):
            pass

        def getName(self):
            return ""

        def isVideoFormat(self, url):
            return False

        def manualVideoCheck(self):
            return False

        def destroy(self):
            pass

        def localProxy(self, param):
            return None


class ShanZhaSpider(BaseSpider):
    """小山 / 米诺（MiNO 秒播4K）。

    协议：ECDH(secp256r1) → HKDF-SHA256(salt=session_id) 派生签名密钥与响应体密钥
         → HMAC-SHA256 签名 + AES-256-GCM 加密响应体。
    2026-11-20 重写，与独立源「山楂.py」对齐，修掉旧实现的四处硬伤：
      1. 私钥 / nonce / device_id 改用 secrets（旧版 random 是梅森旋转，可预测）
      2. 接口级兜底缓存 + 网络重试 + 限流退避（旧版一失败就返回空 dict，
         壳会拿空结果覆盖已有列表，表现为「搜索出来下一秒又消失」）
      3. 补齐筛选项（旧版 filters 恒为 {}，壳里没有排序/地区/年份/语言）
      4. 取票解析失败不再把 tk:xxx 当播放地址丢给壳；同集重播走缓存秒出
    """

    NAME = '小山'
    HOST = 'http://43.248.128.122:578'
    UA = 'okhttp/4.12.0'
    APP_VERSION = '1.0.13'
    VERSION_CODE = '13'
    DEVICE_RISK = '5'
    APP_VERIFY_SIGN = '9D3F7BAD0E160DD63437A1D3267AE87C426700E376D505809E1055BBA42C15E9'
    PAGE_SIZE = 20

    # ---- P-256 ----
    _P = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    _A = _P - 3
    _N = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    _GX = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
    _GY = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5

    # ---- 会话与缓存（类级共享：一个源一个实例，重连/缓存状态全局复用）----
    _dev = ''
    _sid = ''
    _sk = b''
    _bk = b''
    _sched = None
    _exp = 0.0
    _last_ok = {}          # {(method, path, query, body): (ts, 解密后的成功响应)}
    _search_cache = {}     # {(kw, quick, page): (ts, result)}
    _play_cache = {}       # {token: (ts, real_url, fallback_api)}
    _session = None
    # 兜底缓存有效期：只按条数淘汰的话，接口连着失败几天会一直吐几天前的
    # 旧数据且无过期判断；300s 与搜索缓存同一量级，超时宁可变空让壳重试。
    FALLBACK_TTL = 300.0
    # 取票缓存有效期：m3u8 token 常见 5~10 分钟失效，600s 会让重播拿到死链
    PLAY_TTL = 240.0
    # 在这个窗口内复用缓存不做 HEAD 活性校验：刚取到的地址不会立刻失效，
    # 而探测一次要 1~2s（CDN 对 HEAD 很慢），重播体验会被拖垮。
    FRESH_TTL = 60.0
    # 解析站（jx4k / jiexicn 这类）抖动很大：同一条线实测 0.14s、4.3s、20.4s
    # 三种都有。原来 timeout=10 串行重试 2 次，解析站不回就是 20s 干等，
    # 而用户已经在详情页点了播放 —— 这就是「电影加载特别慢」的主因。
    # 现在：候选并发打，单次 3.5s，整体 4.5s 封顶；拿不到直链立刻把解析
    # 接口交回壳（parse=1），不再拿用户的时间去陪解析站。
    RESOLVE_TIMEOUT = 3.5
    RESOLVE_BUDGET = 4.5
    RESOLVE_TRIES = 3
    _lock = threading.Lock()   # 握手串行化：并发 _ensure 只允许一个线程真正握手

    classes = [
        {'type_id': '1', 'type_name': '电影'},
        {'type_id': '2', 'type_name': '连续剧'},
        {'type_id': '3', 'type_name': '综艺'},
        {'type_id': '4', 'type_name': '动漫'},
        {'type_id': '20', 'type_name': '短剧'},
        {'type_id': '21', 'type_name': '少儿'},
        {'type_id': '22', 'type_name': '漫剧'},
        {'type_id': '23', 'type_name': '纪录片'},
    ]

    sort_list = [('', '默认'), ('hits', '最热'), ('score', '评分')]
    area_list = [('', '全部'), ('内地', '内地'), ('中国香港', '中国香港'),
                 ('中国台湾', '中国台湾'), ('美国', '美国'), ('韩国', '韩国'),
                 ('日本', '日本'), ('英国', '英国'), ('法国', '法国'),
                 ('泰国', '泰国'), ('印度', '印度')]
    lang_list = [('', '全部'), ('国语', '国语'), ('英语', '英语'), ('日语', '日语'),
                 ('韩语', '韩语'), ('粤语', '粤语')]
    year_list = [('', '全部')] + [(str(y), str(y)) for y in range(2026, 2009, -1)]

    def __init__(self):
        self.host = self.HOST
        self.page_size = self.PAGE_SIZE
        self._rotate = 1
        self._fallback = 1
        self._sbox = None
        self._m2 = None
        self._m3 = None

    # ---------- 生命周期 ----------
    def getName(self):
        return self.NAME

    def getDependence(self):
        return []

    def setExtendInfo(self, extend):
        return None

    def isVideoFormat(self, url):
        u = (url or '').lower()
        return any(x in u for x in ('.m3u8', '.mp4', '.flv', 'cmecloud'))

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return None

    def destroy(self):
        self._exp = 0.0
        try:
            sess = ShanZhaSpider._session
            if sess is not None:
                sess.close()
        except Exception:
            pass
        ShanZhaSpider._session = None

    def init(self, extend=''):
        try:
            cfg = {}
            if isinstance(extend, dict):
                cfg = extend
            elif isinstance(extend, str) and extend.strip().startswith('{'):
                cfg = json.loads(extend)
            base = str(cfg.get('base') or '').strip().rstrip('/')
            if base.startswith('http'):
                self.host = base
            dev = str(cfg.get('device_id') or '').strip()
            if dev:
                ShanZhaSpider._dev = dev
            # 显式传 0 必须生效，不能用「or 默认值」（0 or 1 == 1）
            if cfg.get('rotate_device') is not None:
                self._rotate = int(cfg.get('rotate_device') or 0)
            if cfg.get('auto_fallback') is not None:
                self._fallback = int(cfg.get('auto_fallback') or 0)
            self.page_size = max(5, int(cfg.get('page_size') or self.PAGE_SIZE))
        except Exception:
            pass
        if not self._dev:
            ShanZhaSpider._dev = secrets.token_hex(16)
        # 握手失败重试一次（服务器偶发不可达）；单次 10s，最坏约 20s，
        # 与旧版单次 20s 持平，但不至于让首屏卡到 40s
        for _ in range(2):
            try:
                if self._ensure(timeout=10):
                    break
            except Exception:
                pass
            time.sleep(0.3)

    # ---------- 网络 ----------
    @staticmethod
    def _http(url, method='GET', data=None, headers=None, timeout=20):
        # 优先 requests.Session：keep-alive 复用连接，握手/搜索/取票/解析都快不少
        if requests is not None:
            sess = ShanZhaSpider._session
            if sess is None:
                sess = requests.Session()
                try:
                    sess.trust_env = False   # 境内明文 IP：走系统代理反而被拦
                except Exception:
                    pass
                ShanZhaSpider._session = sess
            try:
                r = sess.request(method, url, data=data, headers=headers, timeout=timeout)
            except requests.exceptions.SSLError:
                # 证书异常降级（自建证书/网关环境；有中间人风险，仅限取流场景）
                r = sess.request(method, url, data=data, headers=headers,
                                 timeout=timeout, verify=False)
            return r.content
        req = urllib.request.Request(url, data=data if method == 'POST' else None,
                                     method=method)
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with _DIRECT.open(req, timeout=timeout) as r:
                return r.read()
        except ssl.SSLError:
            # 证书异常时降级为不校验（同上，仅兜底）
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with _DIRECT.open(req, timeout=timeout) as r:
                return r.read()

    # 只有这些扩展名才值得探测活性：解析站给的是 API 地址（如
    # coffee-api.xxx.com/...），对它发 HEAD 恒 404/405，会把好缓存全判死，
    # 重播退化成每次重新取票（实测 0.06s → 5.2s）。
    _MEDIA_EXT = ('.m3u8', '.mp4', '.flv', '.mkv', '.ts', '.mov', '.m4a', '.mp3')

    @staticmethod
    def _uri_alive(u):
        """播放地址是否还活着：只有 404/410 算死链，其余一律按活处理。

        有些 CDN 不实现 HEAD（返回 405）或对无 Referer 的请求回 403，
        这些都不代表资源不存在；网络异常/超时同理。宁可多播一次旧地址，
        也不要把好地址误判成死链去反复取票。
        """
        path = str(u or '').split('?', 1)[0].lower()
        if not path.endswith(ShanZhaSpider._MEDIA_EXT):
            return True               # 非媒体直链（解析站 API）不做探测
        try:
            req = urllib.request.Request(
                u, method='HEAD',
                headers={'User-Agent': ShanZhaSpider.UA})
            with _DIRECT.open(req, timeout=1.2) as r:
                return int(getattr(r, 'status', 200) or 200) < 400
        except urllib.error.HTTPError as exc:
            return int(getattr(exc, 'code', 0) or 0) not in (404, 410)
        except Exception:
            return True

    # ---------- EC / HKDF ----------
    @classmethod
    def _ec_add(cls, p1, p2):
        if p1 is None:
            return p2
        if p2 is None:
            return p1
        P = cls._P
        x1, y1 = p1
        x2, y2 = p2
        if x1 == x2 and (y1 + y2) % P == 0:
            return None
        if p1 == p2:
            lam = (3 * x1 * x1 + cls._A) * pow(2 * y1, P - 2, P) % P
        else:
            lam = (y2 - y1) * pow(x2 - x1, P - 2, P) % P
        x3 = (lam * lam - x1 - x2) % P
        return x3, (lam * (x1 - x3) - y1) % P

    @classmethod
    def _ec_mul(cls, k, pt):
        r = None
        while k:
            if k & 1:
                r = cls._ec_add(r, pt)
            pt = cls._ec_add(pt, pt)
            k >>= 1
        return r

    @classmethod
    def _ec_keypair(cls):
        # 私钥必须来自 CSPRNG（random 是梅森旋转，可预测）
        d = secrets.randbelow(cls._N - 1) + 1
        x, y = cls._ec_mul(d, (cls._GX, cls._GY))
        return d, b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')

    @classmethod
    def _ecdh(cls, d, peer):
        x = int.from_bytes(peer[1:33], 'big')
        y = int.from_bytes(peer[33:65], 'big')
        sx, _ = cls._ec_mul(d, (x, y))
        return sx.to_bytes(32, 'big')

    @staticmethod
    def _hkdf(ikm, salt, info, n=32):
        prk = hmac.new(salt, ikm, hashlib.sha256).digest()
        out, t, i = b'', b'', 1
        while len(out) < n:
            t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
            out += t
            i += 1
        return out[:n]

    # ---------- AES-256 + GCM ----------
    def _aes_tables(self):
        if self._sbox is not None:
            return
        def xt(a):
            return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else a << 1

        def gmul(a, b):
            r = 0
            for _ in range(8):
                if b & 1:
                    r ^= a
                b >>= 1
                a = xt(a)
            return r
        exp = [0] * 512
        log = [0] * 256
        x = 1
        for i in range(255):
            exp[i] = x
            log[x] = i
            x ^= xt(x)
        for i in range(255, 512):
            exp[i] = exp[i - 255]
        sbox = [0x63] * 256
        for i in range(1, 256):
            inv = exp[255 - log[i]]
            s = inv
            for sh in range(1, 5):
                s ^= ((inv << sh) | (inv >> (8 - sh))) & 0xFF
            sbox[i] = s ^ 0x63
        self._sbox = sbox
        self._m2 = [gmul(i, 2) for i in range(256)]
        self._m3 = [gmul(i, 3) for i in range(256)]

    def _aes_expand(self, key):
        self._aes_tables()
        sbox = self._sbox
        rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]
        nk = len(key) // 4
        nr = nk + 6
        w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
        for i in range(nk, 4 * (nr + 1)):
            t = list(w[i - 1])
            if i % nk == 0:
                t = [sbox[b] for b in t[1:] + t[:1]]
                t[0] ^= rcon[i // nk - 1]
            elif nk > 6 and i % nk == 4:
                t = [sbox[b] for b in t]
            w.append([w[i - nk][j] ^ t[j] for j in range(4)])
        return w, nr

    def _aes_block(self, sched, block):
        w, nr = sched
        sbox, m2, m3 = self._sbox, self._m2, self._m3
        st = list(block)
        for i in range(16):
            st[i] ^= w[i >> 2][i & 3]
        for rnd in range(1, nr + 1):
            for i in range(16):
                st[i] = sbox[st[i]]
            t = list(st)
            for r in range(1, 4):
                for c in range(4):
                    st[4 * c + r] = t[4 * ((c + r) % 4) + r]
            if rnd != nr:
                for c in range(4):
                    b = 4 * c
                    a0, a1, a2, a3 = st[b], st[b + 1], st[b + 2], st[b + 3]
                    st[b] = m2[a0] ^ m3[a1] ^ a2 ^ a3
                    st[b + 1] = a0 ^ m2[a1] ^ m3[a2] ^ a3
                    st[b + 2] = a0 ^ a1 ^ m2[a2] ^ m3[a3]
                    st[b + 3] = m3[a0] ^ a1 ^ a2 ^ m2[a3]
            rk = 4 * rnd
            for i in range(16):
                st[i] ^= w[rk + (i >> 2)][i & 3]
        return bytes(st)

    @staticmethod
    def _gcm_reduce(v, n):
        R128 = 0xE1000000000000000000000000000000
        for _ in range(n):
            v = (v >> 1) ^ R128 if v & 1 else v >> 1
        return v

    @classmethod
    def _ghash(cls, h, data):
        # 4-bit 窗口表：每 16 字节块 32 次查表，替代逐位 128 次循环
        m = [0] * 16
        for j in range(1, 16):
            v = 0
            for k in range(4):
                if (j >> k) & 1:
                    v ^= cls._gcm_reduce(h, 3 - k)
            m[j] = v
        f = [cls._gcm_reduce(j, 4) for j in range(16)]
        y = 0
        for i in range(0, len(data), 16):
            y ^= int.from_bytes(data[i:i + 16], 'big')
            acc = 0
            for n in range(31, -1, -1):
                acc = m[(y >> (124 - 4 * n)) & 0xF] ^ (acc >> 4) ^ f[acc & 0xF]
            y = acc
        return y

    def _gcm_decrypt(self, sched, iv, blob):
        """blob = 密文 || 16 字节 tag，返回明文；tag 不匹配返回 None。"""
        h = int.from_bytes(self._aes_block(sched, b'\x00' * 16), 'big')
        c, tag = blob[:-16], blob[-16:]
        j0 = iv + b'\x00\x00\x00\x01'
        ctr = int.from_bytes(j0, 'big')
        out = bytearray()
        for i in range(0, len(c), 16):
            ctr = (ctr & ~0xFFFFFFFF) | ((ctr + 1) & 0xFFFFFFFF)
            ks = self._aes_block(sched, ctr.to_bytes(16, 'big'))
            out += bytes(a ^ b for a, b in zip(c[i:i + 16], ks))
        pad = c + b'\x00' * ((16 - len(c) % 16) % 16)
        s = self._ghash(h, pad + struct.pack('>QQ', 0, len(c) * 8))
        calc = int.from_bytes(self._aes_block(sched, j0), 'big') ^ s
        if calc != int.from_bytes(tag, 'big'):
            return None
        return bytes(out)

    # ---------- 会话 ----------
    def _ensure(self, timeout=20):
        if self._sid and time.time() < self._exp:
            return True
        with ShanZhaSpider._lock:
            # double-check：等锁期间可能已有别的线程完成握手
            if self._sid and time.time() < self._exp:
                return True
            if not self._dev:
                ShanZhaSpider._dev = secrets.token_hex(16)
            d, pub = self._ec_keypair()
            body = json.dumps({
                'platform': 'android',
                'version': self.APP_VERSION,
                'device_id': self._dev,
                'client_pub': base64.b64encode(pub).decode(),
                'device_brand': 'Xiaomi',
                'device_manufacturer': 'Xiaomi',
                'device_model': 'MI 8',
                'sig_src': 'java',
                'so_version': 13,
            }, separators=(',', ':')).encode('utf-8')
            raw = self._http(self.host + '/api/v1/security/init', 'POST', body,
                             {'User-Agent': self.UA,
                              'Content-Type': 'application/json'}, timeout=timeout)
            j = json.loads(raw.decode('utf-8', 'ignore'))
            data = j.get('data') or {}
            sid = data.get('session_id') or ''
            pub_s = data.get('server_pub') or ''
            if not sid or not pub_s:
                return False
            peer = base64.b64decode(pub_s)
            if len(peer) != 65 or peer[0] != 4:
                return False
            secret = self._ecdh(d, peer)
            ShanZhaSpider._sid = sid
            ShanZhaSpider._sk = self._hkdf(secret, sid.encode(),
                                           b'bwv/apisec/ecdh-signkey/v1')
            ShanZhaSpider._bk = self._hkdf(secret, sid.encode(),
                                           b'bwv/apisec/ecdh-bodykey/v1')
            ShanZhaSpider._sched = self._aes_expand(ShanZhaSpider._bk)
            ttl = int(data.get('expires_in') or 600)
            ShanZhaSpider._exp = time.time() + max(60, ttl - 60)
            return True

    # ---------- 签名请求 ----------
    def _api(self, path, query='', method='GET', body=''):
        # 接口级「上次成功响应」缓存：偶发失败时不要返回空 dict，否则壳会拿空
        # 结果覆盖已有列表（表现为「搜索出来下一秒又消失」）。auto_fallback=0 可关。
        key = (method.upper(), path, query or '', body or '')
        ent = ShanZhaSpider._last_ok.get(key)
        cached = {}
        if ent:
            if time.time() - ent[0] < self.FALLBACK_TTL:
                cached = ent[1]
            else:
                ShanZhaSpider._last_ok.pop(key, None)   # 过期即弃，不再吐几天前的旧数据
        fb = int(getattr(self, '_fallback', 1) or 0)
        last = dict(cached)
        for attempt in (0, 1):
            if not (self._sid and time.time() < self._exp):
                try:
                    ok = self._ensure()
                except Exception:
                    ok = False   # 握手本身也可能网络异常，不能让异常逃出兜底
                if not ok:
                    return dict(cached) if (fb and cached) else {}
            ts = str(int(time.time()))
            nonce = secrets.token_hex(16)
            raw = (body or '').encode('utf-8')
            bhash = hashlib.sha256(raw).hexdigest()
            q = ''
            if query:
                parts = [p for p in query.split('&') if p]
                parts.sort(key=lambda s: s.split('=')[0])
                q = '&'.join(parts)
            src = '\n'.join([method.upper(), path, q, bhash, ts, nonce,
                             self._dev, self._sid, self.APP_VERSION])
            sign = hmac.new(self._sk, src.encode('utf-8'), hashlib.sha256).hexdigest()
            headers = {
                'User-Agent': self.UA,
                'X-Session-Id': self._sid,
                'X-Device-Id': self._dev,
                'X-Version-Code': self.VERSION_CODE,
                'X-Device-Risk': self.DEVICE_RISK,
                'app-os': 'android',
                'app-api-verify-sign': self.APP_VERIFY_SIGN,
                'X-App-Version': self.APP_VERSION,
                'X-Timestamp': ts,
                'X-Nonce': nonce,
                'X-Sign': sign,
                'X-Body-Sha256': bhash,
            }
            if raw:
                headers['Content-Type'] = 'application/json; charset=utf-8'
            url = self.host + path + (('?' + q) if q else '')
            try:
                txt = self._http(url, method, raw if raw else None,
                                 headers).decode('utf-8', 'ignore')
                last = json.loads(txt)
                if not isinstance(last, dict):
                    last = {}
            except Exception:
                # 网络抖动/超时：重试一次（原来直接返回空，分类页会整页空白）
                if attempt == 0:
                    ShanZhaSpider._exp = 0.0
                    continue
                return dict(cached) if (fb and cached) else (last or {})
            code = last.get('code')
            # 限流退避（search 接口限流严格）：提示「频繁」/rate 时睡 1.5s 重试一次
            msg = str(last.get('msg') or '')
            if attempt == 0 and ('频繁' in msg or 'rate' in msg.lower()):
                time.sleep(1.5)
                continue
            if code in (4600, 4601, 401) and attempt == 0:
                ShanZhaSpider._exp = 0.0
                continue
            if code == 4805 and attempt == 0:
                # 设备被风控：rotate_device=1 时换 device_id 重新握手
                if int(getattr(self, '_rotate', 1) or 0):
                    ShanZhaSpider._dev = secrets.token_hex(16)
                ShanZhaSpider._exp = 0.0
                continue
            data = last.get('data')
            if isinstance(data, dict) and data.get('enc') == 1 and data.get('payload'):
                try:
                    blob = base64.b64decode(data['payload'])
                    plain = self._gcm_decrypt(ShanZhaSpider._sched, blob[:12], blob[12:])
                    if plain:
                        last['data'] = json.loads(plain.decode('utf-8', 'ignore'))
                except Exception:
                    pass
            # 解密「之后」再缓存（旧版在解密前浅拷贝，缓存里永远是密文，兜底无效）；
            # 只缓存成功响应，限量 128 条按插入顺序淘汰
            if last.get('code') in (0, 1) and isinstance(last.get('data'), (dict, list)):
                try:
                    cache = ShanZhaSpider._last_ok
                    cache[key] = (time.time(), dict(last))
                    while len(cache) > 128:
                        cache.pop(next(iter(cache)))
                except Exception:
                    pass
            return last
        return dict(cached) if (fb and cached) else (last or {})

    # ---------- 数据映射 ----------
    @staticmethod
    def _pic(u):
        u = (u or '').strip()
        if u.startswith('//'):
            u = 'https:' + u
        return u

    def _vod(self, v):
        # 服务端偶尔在 hits 里塞 null / 非 dict / 缺字段，直接 .get() 会抛异常
        # 导致整页搜索结果为空
        if not isinstance(v, dict):
            return None
        vid = str(v.get('vod_id') or '').strip()
        name = (v.get('vod_name') or '').strip()
        if not vid or not name:
            return None
        remarks = (v.get('vod_remarks') or '').strip()
        if not remarks:
            bits = [str(x) for x in (v.get('vod_year'), v.get('vod_area')) if x]
            remarks = '·'.join(bits)
        if not remarks and v.get('vod_score'):
            remarks = '评分%s' % v.get('vod_score')
        return {
            'vod_id': vid, 'vod_name': name,
            'vod_pic': self._pic(v.get('vod_pic')),
            'vod_remarks': remarks,
        }

    def _list(self, videos):
        out = []
        for v in videos or []:
            item = self._vod(v)
            if item:
                out.append(item)
        return out

    # ---------- 六方法 ----------
    def homeContent(self, filter=False):
        filters = {}
        if filter:
            def opts(pairs):
                return [{'n': n, 'v': v} for v, n in pairs]
            for c in self.classes:
                filters[c['type_id']] = [
                    {'key': 'sort', 'name': '排序', 'value': opts(self.sort_list)},
                    {'key': 'area', 'name': '地区', 'value': opts(self.area_list)},
                    {'key': 'year', 'name': '年份', 'value': opts(self.year_list)},
                    {'key': 'lang', 'name': '语言', 'value': opts(self.lang_list)},
                ]
        return {'class': list(self.classes), 'filters': filters}

    def homeVideoContent(self):
        try:
            j = self._api('/api/v1/category/videos',
                          'page=1&page_size=%d&type_id=2' % self.page_size)
            return {'list': self._list(((j.get('data') or {}).get('videos')) or [])}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter=False, extend=None):
        try:
            pg = max(1, int(pg or 1))
        except Exception:
            pg = 1
        query = 'type_id=%s&page=%d&page_size=%d' % (
            urllib.parse.quote(str(tid), safe=''), pg, self.page_size)
        if isinstance(extend, dict):
            for k in ('sort', 'area', 'year', 'lang', 'class'):
                v = extend.get(k)
                if v and str(v) != '全部':
                    query += '&%s=%s' % (k, urllib.parse.quote(str(v), safe=''))
        try:
            j = self._api('/api/v1/category/videos', query)
            data = j.get('data') or {}
            videos = data.get('videos') or []
            pag = data.get('pagination') or {}
            total = int(pag.get('total') or 0)
            pages = int(pag.get('total_pages') or 0) or (pg + 1 if videos else pg)
            return {'list': self._list(videos), 'page': pg, 'pagecount': pages,
                    'limit': self.page_size, 'total': total}
        except Exception:
            return {'list': [], 'page': pg, 'pagecount': pg,
                    'limit': self.page_size, 'total': 0}

    def detailContent(self, ids):
        try:
            vid = str(ids[0]).strip() if ids else ''
            if not vid:
                return {'list': []}
            j = self._api('/api/v1/video/detail',
                          'id=' + urllib.parse.quote(vid, safe=''))
            info = ((j.get('data') or {}).get('vod_info')) or {}
            if not info:
                return {'list': []}
            froms, urls = [], []
            for line in info.get('vod_url_with_player') or []:
                code = (line.get('code') or '').strip()
                name = (line.get('name') or '').strip() or code
                raw = (line.get('url') or '').strip()
                if not raw:
                    continue
                # 集名/线路码会拼进 vod_play_url，$ 与 # 是本文件的段落分隔符，
                # 不清洗会导致整条线路解析错位
                code_seg = code.replace('$', ' ').replace('#', ' ')
                eps, seen = [], set()
                for seg in raw.split('#'):
                    seg = seg.strip()
                    if not seg or '$' not in seg:
                        continue
                    ep, token = seg.split('$', 1)
                    ep, token = ep.strip(), token.strip()
                    if not ep or not token or token in seen:
                        continue
                    seen.add(token)
                    eps.append('%s$%s|%s'
                               % (ep.replace('$', ' ').replace('#', ' '),
                                  code_seg, token))
                if eps:
                    froms.append(name.replace('$', ' ').replace('#', ' '))
                    urls.append('#'.join(eps))
            if not froms:
                return {'list': []}
            year = str(info.get('vod_year') or '').strip()[:4]
            remarks = (info.get('vod_remarks') or '').strip()
            if not remarks and info.get('vod_score'):
                remarks = '评分%s' % info.get('vod_score')
            vod = {
                'vod_id': str(info.get('vod_id') or vid),
                'vod_name': (info.get('vod_name') or '').strip(),
                'vod_pic': self._pic(info.get('vod_pic')),
                'type_name': (info.get('vod_class') or info.get('type_name') or '').strip(),
                'vod_year': year,
                'vod_area': (info.get('vod_area') or '').strip(),
                'vod_actor': (info.get('vod_actor') or '').strip(),
                'vod_director': (info.get('vod_director') or '').strip(),
                'vod_remarks': remarks,
                'vod_content': (info.get('vod_content')
                                or info.get('vod_blurb') or '').strip(),
                'vod_play_from': '$$$'.join(froms),
                'vod_play_url': '$$$'.join(urls),
            }
            return {'list': [vod]}
        except Exception:
            return {'list': []}

    def searchContent(self, key, quick=False, pg='1'):
        """服务端搜索是宽分词且限流严格（搜「庆余年」会连「林总的三十年庆」一起出）。

        完整搜索只做页内相关性重排，不丢结果；quick 只留片名含关键词的，
        一个都不匹配时回退原始结果。同词同页 120s 缓存，避开限流。
        失败时回退上次成功结果，绝不返回空 list（壳会清空结果页）。
        """
        try:
            page = max(1, int(pg or 1))
        except Exception:
            page = 1
        kw = str(key or '').strip()
        size = 10 if quick else 20
        try:
            ent = ShanZhaSpider._search_cache.get((kw, bool(quick), page))
            if ent and time.time() - ent[0] < 120:
                return dict(ent[1])
            j = self._api('/api/v1/search',
                          'page=%d&page_size=%d&wd=%s'
                          % (page, size, urllib.parse.quote(kw, safe='')))
            data = j.get('data') or {}
            if not data:
                # _api 内部故障（网络/握手失败且该接口无缓存）会返回 {}：视为失败
                raise RuntimeError('empty search response')
            hits = list(data.get('hits') or [])
            if kw:
                low = kw.lower()
                hits.sort(key=lambda h: 0 if isinstance(h, dict)
                          and low in str(h.get('vod_name') or '').lower() else 1)
            if quick:
                matched = [h for h in hits if isinstance(h, dict)
                           and kw.lower() in str(h.get('vod_name') or '').lower()]
                hits = matched if matched else hits[:size]
            if kw and not hits:
                raise RuntimeError('empty hits')   # 回退缓存，避免「结果秒消失」
            res = {'list': self._list(hits), 'page': page,
                   'limit': int(data.get('limit') or size),
                   'total': int(data.get('total') or len(hits))}
            pages = int(data.get('total_pages') or 0)
            if pages:
                res['pagecount'] = pages
            try:
                cache = ShanZhaSpider._search_cache
                cache[(kw, bool(quick), page)] = (time.time(), res)
                if len(cache) > 100:
                    now = time.time()
                    for ck in [k for k, v in cache.items() if now - v[0] > 300]:
                        cache.pop(ck, None)
                    while len(cache) > 100:
                        cache.pop(next(iter(cache)))
            except Exception:
                pass
            return res
        except Exception:
            cache = getattr(ShanZhaSpider, '_search_cache', {}) or {}
            ent = cache.get((kw, bool(quick), page))
            if not ent:                       # 退而求其次：同关键词任意页
                same = [(ts, r) for (k, ts, r) in
                        ((k, v[0], v[1]) for k, v in cache.items())
                        if k[0] == kw]
                if same:
                    same.sort(key=lambda x: -x[0])
                    ent = (same[0][0], same[0][1])
            if ent and time.time() - ent[0] < 300:
                out = dict(ent[1])
                out['page'] = page            # 页码按本次请求修正
                out['pagecount'] = max(int(out.get('pagecount') or 0), page + 1)
                return out
            return {'list': [], 'page': page, 'limit': size}

    # ---------- 播放 ----------
    def _ticket(self, token):
        try:
            body = json.dumps({'token': token}, separators=(',', ':'))
            j = self._api('/api/v1/vod/ticket', '', 'POST', body)
            if str(j.get('code')) != '1':
                return ''
            return ((j.get('data') or {}).get('ticket')) or ''
        except Exception:
            return ''

    @staticmethod
    def _b64json(s):
        raw = s.replace('-', '+').replace('_', '/')
        raw += '=' * ((4 - len(raw) % 4) % 4)
        try:
            return json.loads(base64.b64decode(raw).decode('utf-8', 'ignore'))
        except Exception:
            return {}

    @staticmethod
    def _parse_play(txt):
        """解析站响应 → 可播直链（空串表示这次没解出来）。"""
        txt = str(txt or '').strip()
        if not txt:
            return ''
        if txt.startswith('{'):
            try:
                obj = json.loads(txt)
                real = obj.get('url') or (obj.get('data') or {}).get('url') or ''
                if isinstance(real, dict):
                    real = real.get('url') or ''
                real = str(real).strip()
                return real if real.startswith('http') else ''
            except Exception:
                return ''
        if txt.startswith('http'):
            return txt.split('\n')[0].strip()
        return ''

    def _resolve_round(self, cands, deadline):
        """并发打一轮候选，谁先解出直链用谁；到预算就收手。

        1080P 这类线实测要连打三次才成功（1.5s 空、1.0s 空、1.8s 出链），
        所以「一轮失败」不算判死，由 _resolve 在预算内再补轮次。
        """
        box = {}
        lock = threading.Lock()
        state = {'left': len(cands)}
        done = threading.Event()

        def run(target):
            real = ''
            try:
                left = max(0.8, deadline - time.time())
                txt = self._http(target, 'GET', None,
                                 {'User-Agent': self.UA,
                                  'Referer': 'https://www.google.com/'},
                                 timeout=min(self.RESOLVE_TIMEOUT, left))
                real = self._parse_play(txt.decode('utf-8', 'ignore'))
            except Exception:
                real = ''
            with lock:
                if real and 'real' not in box:
                    box['real'] = real
                    box['api'] = target
                state['left'] -= 1
                if state['left'] <= 0 or 'real' in box:
                    done.set()

        for t in cands:
            th = threading.Thread(target=run, args=(t,), daemon=True)
            th.start()
        done.wait(max(0.5, min(self.RESOLVE_BUDGET,
                               deadline - time.time())))
        return box.get('real') or ''

    def _resolve(self, ticket):
        """ticket → (真实地址, 解析接口兜底地址)。"""
        data = (self._b64json(ticket.split('.')[0]) or {}).get('data') or {}
        url = (data.get('url') or '').strip()
        api = (data.get('parse_api') or '').strip()
        api = api.replace('\\u00026', '&').replace('\u0002', '').replace('\\u0002', '')
        if not url:
            return '', ''
        cands = []
        if api:
            if api.startswith('/'):
                api = self.host + api
            if '{md5}' in api:
                cands.append(api.replace('{md5}', hashlib.md5(url.encode()).hexdigest()))
                cands.append(api.replace('{md5}', urllib.parse.quote(url, safe='')))
            else:
                cands.append(api + urllib.parse.quote(url, safe=''))
        if not cands:
            return '', ''
        deadline = time.time() + self.RESOLVE_BUDGET
        for _ in range(self.RESOLVE_TRIES):
            real = self._resolve_round(cands, deadline)
            if real:
                return real, cands[0]
            if time.time() >= deadline - 0.4:
                break
        return '', cands[0]

    def playerContent(self, flag, id, vipFlags=None):
        pid = (id or '').strip()
        token = pid
        if '|' in pid:
            _, token = pid.split('|', 1)
            token = token.strip()
        if not token:
            return {'parse': 1, 'url': '', 'header': {'User-Agent': self.UA}}
        # 同一集重播/重试：直接用缓存的真实地址，省掉取票+解析两次往返。
        # m3u8 token 常见 5~10 分钟失效，原来 600s 盲信会让重播拿到死链，
        # 所以缩短 TTL 且命中时做一次 HEAD 活性校验。
        ent = ShanZhaSpider._play_cache.get(token)
        if ent and time.time() - ent[0] < self.PLAY_TTL and str(ent[1]).startswith('http'):
            # 刚取到的地址（FRESH_TTL 内）几乎不可能已经失效，直接复用：
            # 同一集连点两次就该秒开。只有「放了一会儿」的地址才做 HEAD 校验，
            # 这样既不会拿死链糊弄播放器，也不会让重播白白多等 1~2s。
            if time.time() - ent[0] < ShanZhaSpider.FRESH_TTL or self._uri_alive(ent[1]):
                return {'parse': 0, 'url': ent[1], 'header': {'User-Agent': self.UA}}
            ShanZhaSpider._play_cache.pop(token, None)   # 死链：丢掉重新取票
        ticket = self._ticket(token)
        if ticket:
            real, fallback = self._resolve(ticket)
            if real.startswith('http'):
                try:
                    cache = ShanZhaSpider._play_cache
                    cache[token] = (time.time(), real, fallback)
                    while len(cache) > 200:
                        cache.pop(next(iter(cache)))
                except Exception:
                    pass
                return {'parse': 0, 'url': real, 'header': {'User-Agent': self.UA}}
            if fallback.startswith('http'):
                return {'parse': 1, 'url': fallback, 'header': {'User-Agent': self.UA}}
        # 取票/解析全失败：不要把 tk:xxx 当 URL 丢给播放器（旧版就是这里出错）
        return {'parse': 1, 'url': '', 'header': {'User-Agent': self.UA}}



# 模块：gg —— 咕噜咕噜（首页 / 分类主源，T3 私有协议）
# ======================================================================
# -*- coding: utf-8 -*-
"""
咕噜咕噜 —— TVBox 蜘蛛框架Python 爬虫）。

"""


from urllib.parse import quote

try:
    import requests as _requests
except Exception:
    _requests = None

API_URL = "http://103.45.132.22:19987/app/bn/v2"
HOST = "http://103.45.132.22:19987"
USER_AGENT = "Dart/3.10 (dart:io)"
APP_VERSION = "2.2.5"
BUILD_NUMBER = "20109"
APP_SIGNATURE = "32E0AB4FF93A29CE0E6F0BFB01F2F1B788E76262731F3F30F509CB822428ED58"
DEVICE_BUILD = "pangu-build-component-system-513739-s9vkd-rlxnj-p3rhm"
VERSION_GUARD_MARKERS = ("__v99_", "glgl.tv", "111.170.58.215", "shu.jpg")
FALLBACK_PARSERS = {
    28: {"name": "咕噜金牌", "url": "http://111.170.58.215:5499/api.php?id=",
         "mode": "json", "result_key": "url", "server": False},
}


# ============ protobuf 工具 ============

def _varint(value):
    if value < 0:
        raise ValueError("negative protobuf varint")
    output = bytearray()
    while value >= 0x80:
        output.append((value & 0x7F) | 0x80)
        value >>= 7
    output.append(value)
    return bytes(output)


def _field_bytes(number, value):
    if isinstance(value, str):
        value = value.encode("utf-8")
    return _varint((number << 3) | 2) + _varint(len(value)) + value


def _field_varint(number, value):
    return _varint(number << 3) + _varint(value)


def _read_varint(data, position):
    value = 0
    shift = 0
    while position < len(data) and shift < 70:
        byte = data[position]
        position += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, position
        shift += 7
    raise ValueError("invalid protobuf varint")


def _parse_fields(data):
    fields = []
    position = 0
    while position < len(data):
        key, position = _read_varint(data, position)
        number, wire = key >> 3, key & 7
        if number == 0:
            raise ValueError("invalid protobuf field zero")
        if wire == 0:
            value, position = _read_varint(data, position)
        elif wire == 1:
            value = data[position:position + 8]
            position += 8
        elif wire == 2:
            size, position = _read_varint(data, position)
            value = data[position:position + size]
            position += size
        elif wire == 5:
            value = data[position:position + 4]
            position += 4
        else:
            raise ValueError("unsupported protobuf wire type %d" % wire)
        if position > len(data):
            raise ValueError("truncated protobuf field")
        fields.append((number, wire, value))
    return fields


def _field_values(data, number, wire=None):
    return [v for n, w, v in _parse_fields(data)
            if n == number and (wire is None or w == wire)]


def _field_value(data, number, default=None, wire=None):
    values = _field_values(data, number, wire)
    return values[-1] if values else default


def _text(value, default=""):
    if not isinstance(value, bytes):
        return value
    try:
        return value.decode("utf-8")
    except UnicodeDecodeError:
        return default


def _packed_varints(data):
    values = []
    position = 0
    while position < len(data):
        value, position = _read_varint(data, position)
        values.append(value)
    return values


def _raw_deflate(data):
    compressor = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-15,
                                  memLevel=8, strategy=zlib.Z_RLE)
    return compressor.compress(data) + compressor.flush()


# ============ 纯标准库密码学 ============

def g_xtime(a):
    b = a << 1
    if b & 0x100:
        b ^= 0x11B
    return b & 0xFF


def _gf256_mul(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return result


def _build_aes_tables():
    exp = [0] * 256
    log = [0] * 256
    x = 1
    for i in range(255):
        exp[i] = x
        log[x] = i
        x = _gf256_mul(x, 0x03)
    sbox = [0] * 256
    inv_sbox = [0] * 256
    for i in range(256):
        inv = 0 if i == 0 else exp[(255 - log[i]) % 255]
        t = inv
        s = inv
        for _ in range(4):
            s = ((s << 1) | (s >> 7)) & 0xFF
            t ^= s
        sbox[i] = t ^ 0x63
        inv_sbox[sbox[i]] = i
    return bytes(sbox), bytes(inv_sbox)


_SBOX, _INV_SBOX = _build_aes_tables()


def g_expand_key(key):
    rcon = 1
    words = [list(key[i:i + 4]) for i in range(0, 32, 4)]
    while len(words) < 60:
        temp = words[-1][:]
        if len(words) % 8 == 0:
            temp = temp[1:] + temp[:1]
            temp = [_SBOX[b] for b in temp]
            temp[0] ^= rcon
            rcon = g_xtime(rcon)
        elif len(words) % 8 == 4:
            temp = [_SBOX[b] for b in temp]
        words.append([words[-8][i] ^ temp[i] for i in range(4)])
    return [sum((words[i:i + 4]), []) for i in range(0, 60, 4)]


def g_shift_rows(state, encrypt=True):
    out = [0] * 16
    for r in range(4):
        for c in range(4):
            out[r + 4 * c] = state[r + 4 * ((c + (r if encrypt else -r)) % 4)]
    return out


def g_mix_columns(state):
    out = state[:]
    for c in range(4):
        a = out[0 + 4 * c]
        b = out[1 + 4 * c]
        d = out[2 + 4 * c]
        e = out[3 + 4 * c]
        t = a ^ b ^ d ^ e
        out[0 + 4 * c] = a ^ t ^ g_xtime(a ^ b)
        out[1 + 4 * c] = b ^ t ^ g_xtime(b ^ d)
        out[2 + 4 * c] = d ^ t ^ g_xtime(d ^ e)
        out[3 + 4 * c] = e ^ t ^ g_xtime(e ^ a)
    return out


def g_mul9(x):
    return g_xtime(g_xtime(g_xtime(x))) ^ x


def g_mul11(x):
    return g_xtime(g_xtime(g_xtime(x))) ^ g_xtime(x) ^ x


def g_mul13(x):
    return g_xtime(g_xtime(g_xtime(x))) ^ g_xtime(g_xtime(x)) ^ x


def g_mul14(x):
    return g_xtime(g_xtime(g_xtime(x))) ^ g_xtime(g_xtime(x)) ^ g_xtime(x)


def g_inv_mix_columns(state):
    out = state[:]
    for c in range(4):
        a = out[0 + 4 * c]
        b = out[1 + 4 * c]
        d = out[2 + 4 * c]
        e = out[3 + 4 * c]
        out[0 + 4 * c] = g_mul14(a) ^ g_mul11(b) ^ g_mul13(d) ^ g_mul9(e)
        out[1 + 4 * c] = g_mul9(a) ^ g_mul14(b) ^ g_mul11(d) ^ g_mul13(e)
        out[2 + 4 * c] = g_mul13(a) ^ g_mul9(b) ^ g_mul14(d) ^ g_mul11(e)
        out[3 + 4 * c] = g_mul11(a) ^ g_mul13(b) ^ g_mul9(d) ^ g_mul14(e)
    return out


def _aes_encrypt_block(block, round_keys):
    state = [s ^ k for s, k in zip(block, round_keys[0])]
    for r in range(1, 14):
        state = [_SBOX[b] for b in state]
        state = g_shift_rows(state, True)
        state = g_mix_columns(state)
        state = [s ^ k for s, k in zip(state, round_keys[r])]
    state = [_SBOX[b] for b in state]
    state = g_shift_rows(state, True)
    return bytes([s ^ k for s, k in zip(state, round_keys[14])])


def _aes_decrypt_block(block, round_keys):
    state = [s ^ k for s, k in zip(block, round_keys[14])]
    for r in range(13, 0, -1):
        state = g_shift_rows(state, False)
        state = [_INV_SBOX[b] for b in state]
        state = [s ^ k for s, k in zip(state, round_keys[r])]
        state = g_inv_mix_columns(state)
    state = g_shift_rows(state, False)
    state = [_INV_SBOX[b] for b in state]
    return bytes([s ^ k for s, k in zip(state, round_keys[0])])


def _pkcs7_pad(data):
    size = 16 - (len(data) % 16)
    return data + bytes([size] * size)


def _pkcs7_unpad(data):
    if not data:
        raise ValueError("empty plaintext")
    size = data[-1]
    if size < 1 or size > 16 or data[-size:] != bytes([size] * size):
        raise ValueError("invalid PKCS7 padding")
    return data[:-size]


def _aes256_cbc_encrypt(key, iv, data):
    round_keys = g_expand_key(key)
    previous = iv
    out = bytearray()
    data = _pkcs7_pad(data)
    for i in range(0, len(data), 16):
        block = bytes(b ^ p for b, p in zip(data[i:i + 16], previous))
        enc = _aes_encrypt_block(block, round_keys)
        out += enc
        previous = enc
    return bytes(out)


def _aes256_cbc_decrypt(key, iv, data):
    round_keys = g_expand_key(key)
    previous = iv
    out = bytearray()
    for i in range(0, len(data), 16):
        block = data[i:i + 16]
        dec = _aes_decrypt_block(block, round_keys)
        out += bytes(b ^ p for b, p in zip(dec, previous))
        previous = block
    return _pkcs7_unpad(bytes(out))


_GCM_REDUCTION = 0xE1000000000000000000000000000000


def g_ghash_mul(x, y):
    z = 0
    for i in range(128):
        if (x >> (127 - i)) & 1:
            z ^= y
        if y & 1:
            y = (y >> 1) ^ _GCM_REDUCTION
        else:
            y >>= 1
    return z


def g_ghash(h, aad, ciphertext):
    y = 0
    for i in range(0, len(aad), 16):
        block = int.from_bytes(aad[i:i + 16].ljust(16, b"\x00"), "big")
        y = g_ghash_mul(y ^ block, h)
    for i in range(0, len(ciphertext), 16):
        block = int.from_bytes(ciphertext[i:i + 16].ljust(16, b"\x00"), "big")
        y = g_ghash_mul(y ^ block, h)
    lengths = (len(aad) * 8).to_bytes(8, "big") + (len(ciphertext) * 8).to_bytes(8, "big")
    return g_ghash_mul(y ^ int.from_bytes(lengths, "big"), h)


def _aes256_gcm_encrypt(key, nonce, data, aad=b""):
    round_keys = g_expand_key(key)
    h = int.from_bytes(_aes_encrypt_block(b"\x00" * 16, round_keys), "big")
    j0 = nonce + b"\x00\x00\x00\x01"
    counter = int.from_bytes(j0, "big")
    out = bytearray()
    for i in range(0, len(data), 16):
        counter += 1
        keystream = _aes_encrypt_block(counter.to_bytes(16, "big"), round_keys)
        chunk = data[i:i + 16]
        out += bytes(b ^ k for b, k in zip(chunk, keystream))
    ciphertext = bytes(out)
    s = g_ghash(h, aad, ciphertext)
    tag_block = _aes_encrypt_block(j0, round_keys)
    tag = (s ^ int.from_bytes(tag_block, "big")).to_bytes(16, "big")[:16]
    return ciphertext, tag


def _aes256_gcm_decrypt(key, nonce, data, tag, aad=b""):
    round_keys = g_expand_key(key)
    h = int.from_bytes(_aes_encrypt_block(b"\x00" * 16, round_keys), "big")
    j0 = nonce + b"\x00\x00\x00\x01"
    s = g_ghash(h, aad, data)
    tag_block = _aes_encrypt_block(j0, round_keys)
    expected = (s ^ int.from_bytes(tag_block, "big")).to_bytes(16, "big")[:16]
    if not hmac.compare_digest(expected, tag):
        raise ValueError("GCM tag mismatch")
    counter = int.from_bytes(j0, "big")
    out = bytearray()
    for i in range(0, len(data), 16):
        counter += 1
        keystream = _aes_encrypt_block(counter.to_bytes(16, "big"), round_keys)
        chunk = data[i:i + 16]
        out += bytes(b ^ k for b, k in zip(chunk, keystream))
    return bytes(out)


# P-256 (secp256r1) 椭圆曲线

g_P256_P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
g_P256_A = g_P256_P - 3
_P256_B = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
g_P256_N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
g_P256_G = (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
           0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)


def _modinv(a, m):
    if m == 1:
        return 0
    t, newt = 0, 1
    r, newr = m, a % m
    while newr:
        q = r // newr
        t, newt = newt, t - q * newt
        r, newr = newr, r - q * newr
    if r != 1:
        raise ValueError("no modular inverse")
    return t % m


def g_p256_double(point):
    if point is None:
        return None
    x, y = point
    if y == 0:
        return None
    lam = (3 * x * x + g_P256_A) * _modinv(2 * y, g_P256_P) % g_P256_P
    x3 = (lam * lam - 2 * x) % g_P256_P
    y3 = (lam * (x - x3) - y) % g_P256_P
    return (x3, y3)


def g_p256_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2:
        if (y1 + y2) % g_P256_P == 0:
            return None
        return g_p256_double(p1)
    lam = (y2 - y1) * _modinv(x2 - x1, g_P256_P) % g_P256_P
    x3 = (lam * lam - x1 - x2) % g_P256_P
    y3 = (lam * (x1 - x3) - y1) % g_P256_P
    return (x3, y3)


def g_p256_mul(k, point):
    result = None
    addend = point
    while k:
        if k & 1:
            result = g_p256_add(result, addend)
        addend = g_p256_double(addend)
        k >>= 1
    return result


def _p256_ecdh_x(private_d, server_point):
    shared = g_p256_mul(private_d, server_point)
    if shared is None:
        raise ValueError("ECDH point at infinity")
    return shared[0].to_bytes(32, "big")


def _sec1_export_public(point):
    return b"\x04" + point[0].to_bytes(32, "big") + point[1].to_bytes(32, "big")


def _sec1_import_public(data):
    raw = bytes(data or b"")
    if len(raw) == 65 and raw[0] == 4:
        x = int.from_bytes(raw[1:33], "big")
        y = int.from_bytes(raw[33:65], "big")
        return (x, y)
    if len(raw) == 33 and raw[0] in (2, 3):
        x = int.from_bytes(raw[1:], "big")
        y2 = (pow(x, 3, g_P256_P) - 3 * x + _P256_B) % g_P256_P
        y = pow(y2, (g_P256_P + 1) // 4, g_P256_P)
        if (y * y) % g_P256_P != y2:
            raise ValueError("point not on curve")
        if (y & 1) != (raw[0] & 1):
            y = g_P256_P - y
        return (x, y)
    raise ValueError("invalid P-256 SEC1 public key")


def _derive_key(session_id, shared_x):
    prk = hmac.new(session_id.encode("ascii"), shared_x, hashlib.sha256).digest()
    return hmac.new(prk, b"v2-session\x01", hashlib.sha256).digest()


# ============ HTTP（纯 urllib） ============

def _http_post(url, body, headers, timeout=15):
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        # 响应必须显式关闭：这条链路（咕噜私协）每次播放要打好几次，
        # 靠 GC 回收会攒下大量半开的 socket / 文件句柄。
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content = response.read()
            encoding = response.headers.get("Content-Encoding", "")
    except urllib.error.HTTPError as error:
        try:
            detail = error.read(200)
        except Exception:
            detail = b""
        finally:
            try:
                error.close()
            except Exception:
                pass
        raise RuntimeError("HTTP %s: %s" % (error.code, detail))
    except urllib.error.URLError as error:
        raise RuntimeError("request failed: %s" % (error.reason,))
    if "gzip" in encoding.lower() or content[:2] == b"\x1f\x8b":
        try:
            content = gzip.decompress(content)
        except Exception:
            pass
    return content


def _http_get(url, headers, timeout=15):
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content = response.read()
            encoding = response.headers.get("Content-Encoding", "")
            status = response.status
    except urllib.error.HTTPError as error:
        try:
            detail = error.read(200)
        except Exception:
            detail = b""
        finally:
            try:
                error.close()
            except Exception:
                pass
        return error.code, detail
    except urllib.error.URLError as error:
        raise RuntimeError("request failed: %s" % (error.reason,))
    if "gzip" in encoding.lower() or content[:2] == b"\x1f\x8b":
        try:
            content = gzip.decompress(content)
        except Exception:
            pass
    return status, content


# ============ 协议客户端 ============

class _GuluProtocol:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.session_id = ""
        self.session_key = b""
        self.device_id = secrets.token_hex(8)
        self.request_id = 0
        self.players = {}
        self.parsers = {}
        self.last_detail_error = ""
        self.lock = threading.RLock()

    def _post(self, body, header_name, header_value, extra_headers=None):
        headers = {
            "User-Agent": USER_AGENT, header_name: header_value,
            "Content-Type": "application/x-protobuf", "Accept-Encoding": "gzip",
            "Content-Length": str(len(body)), "Host": "103.45.132.22:19987",
        }
        if extra_headers:
            headers.update(extra_headers)
        return _http_post(API_URL, body, headers, self.timeout)

    def handshake(self):
        private_d = int.from_bytes(secrets.token_bytes(32), "big") % (g_P256_N - 1) + 1
        public_point = g_p256_mul(private_d, g_P256_G)
        public_key = _sec1_export_public(public_point)
        capabilities = _field_varint(1, 1) + _field_varint(2, 0) + _field_varint(3, 1)
        request = (_field_bytes(1, public_key) + _field_bytes(2, b"1.0.0")
                   + _field_bytes(3, capabilities))
        handshake_key = secrets.token_hex(16)
        iv = secrets.token_bytes(16)
        encrypted = base64.b64encode(
            iv + _aes256_cbc_encrypt(handshake_key.encode("ascii"), iv,
                                     zlib.compress(request, 4)))
        content = self._post(encrypted, "x-handshake-key", handshake_key)
        raw = base64.b64decode(content)
        response_cipher_key = handshake_key.encode("ascii")
        plain = zlib.decompress(
            _aes256_cbc_decrypt(response_cipher_key, raw[:16], raw[16:]))
        session_id = _field_value(plain, 1, wire=2)
        server_public = _field_value(plain, 2, wire=2)
        if not session_id or not server_public:
            raise RuntimeError("invalid handshake response")
        self.session_id = session_id.decode("ascii")
        server_point = _sec1_import_public(server_public)
        shared_x = _p256_ecdh_x(private_d, server_point)
        self.session_key = _derive_key(self.session_id, shared_x)
        self.request_id = 0

    def _encrypt(self, data):
        nonce = secrets.token_bytes(12)
        ciphertext, tag = _aes256_gcm_encrypt(self.session_key, nonce, _raw_deflate(data))
        return nonce + ciphertext + tag

    def _decrypt(self, data):
        if len(data) < 28:
            raise ValueError("invalid GCM payload")
        nonce = data[:12]
        ciphertext = data[12:-16]
        tag = data[-16:]
        compressed = _aes256_gcm_decrypt(self.session_key, nonce, ciphertext, tag)
        return zlib.decompress(compressed, -15)

    def request(self, method, payload=b"", scope=3, extra_headers=None):
        with self.lock:
            if not self.session_id:
                self.handshake()
            self.request_id += 1
            request_id = self.request_id
            core = (_field_varint(1, request_id) + _field_varint(2, scope)
                    + _field_varint(3, method) + _field_bytes(4, self.device_id)
                    + _field_bytes(5, b"") + _field_bytes(6, payload)
                    + _field_varint(7, int(time.time() * 1000)))
            body = _field_varint(1, request_id) + _field_bytes(2, self._encrypt(core))
            content = self._post(body, "x-session-id", self.session_id,
                                 extra_headers=extra_headers)
            encrypted = _field_value(content, 2, wire=2)
            if encrypted is None:
                error = _text(_field_value(content, 3, b"", wire=2))
                raise RuntimeError(error or "server rejected request")
            plain = self._decrypt(encrypted)
            status = _text(_field_value(plain, 3, b"", wire=2))
            if status and status not in ("ok", "success"):
                raise RuntimeError(status)
            return plain

    def boot(self):
        now_us = int(time.time() * 1_000_000)
        app = (_field_bytes(1, "咕噜咕噜") + _field_bytes(2, APP_VERSION)
               + _field_bytes(3, b"com.himrsc.viz") + _field_bytes(4, APP_SIGNATURE)
               + _field_bytes(5, BUILD_NUMBER) + _field_varint(6, now_us)
               + _field_varint(7, now_us))
        device = (_field_bytes(1, self.device_id) + _field_varint(2, 1)
                  + _field_bytes(3, b"15") + _field_bytes(4, b"Redmi K50 Ultra")
                  + _field_bytes(5, b"Redmi/diting/diting:15/AQ3A.240912.001/OS2.0.215.0.VOACNXM:user/release-keys")
                  + _field_bytes(6, b"Redmi") + _field_bytes(7, b"qcom")
                  + _field_varint(8, 0) + _field_bytes(9, b"unknown")
                  + _field_bytes(10, DEVICE_BUILD) + _field_varint(11, 0)
                  + _field_varint(12, 35))
        payload = (_field_bytes(1, b"v2") + _field_bytes(2, b"android")
                   + _field_bytes(3, b"gulu") + _field_bytes(4, app)
                   + _field_bytes(5, device))
        response = self.request(0, payload, scope=1)
        config = _field_value(response, 4, b"", wire=2)
        players = {}
        for item in _field_values(config, 4, wire=2):
            code = _text(_field_value(item, 3, b"", wire=2))
            if not code:
                continue
            parser_ids = []
            for packed in _field_values(item, 8, wire=2):
                parser_ids.extend(_packed_varints(packed))
            players[code] = {"id": _field_value(item, 1, 0, wire=0),
                             "name": _text(_field_value(item, 4, b"", wire=2)),
                             "parser_ids": parser_ids}
        parsers = {}
        for item in _field_values(config, 7, wire=2):
            parser_id = _field_value(item, 1, 0, wire=0)
            if parser_id:
                parsers[parser_id] = {
                    "name": _text(_field_value(item, 2, b"", wire=2)),
                    "url": _text(_field_value(item, 3, b"", wire=2)),
                    "mode": _text(_field_value(item, 4, b"", wire=2)),
                    "result_key": _text(_field_value(item, 10, b"url", wire=2)),
                    "server": bool(_field_value(item, 20, 0, wire=0))}
        self.players = players
        self.parsers = parsers

    def search(self, keyword, page=1, limit=21, category_id="", genre="", area="",
               sort="vod_hits_month"):
        sort = str(sort or "vod_hits_month")
        filters = _field_bytes(18, sort.encode("utf-8")) + _field_varint(19, 1)
        category_id = str(category_id or "").strip()
        if category_id:
            filters += _field_bytes(3, category_id) + _field_bytes(4, category_id)
        genre = str(genre or "").strip()
        if genre:
            filters += _field_bytes(8, genre)
        area = str(area or "").strip()
        if area:
            filters += _field_bytes(6, area)
        payload = (_field_bytes(1, keyword) + _field_varint(2, int(page))
                   + _field_varint(3, int(limit)) + _field_bytes(5, filters))
        response = self.request(61, payload)
        data = _field_value(response, 4, b"", wire=2)
        videos = []
        for message in _field_values(data, 1, wire=2):
            videos.append({
                "vod_id": str(_field_value(message, 1, 0, wire=0)),
                "vod_name": _text(_field_value(message, 3, b"", wire=2)),
                "vod_pic": _text(_field_value(message, 6, b"", wire=2)),
                "vod_remarks": _text(_field_value(message, 11, b"", wire=2)),
            })
        page_info = _field_value(data, 2, b"", wire=2)
        return {"videos": videos,
                "page": _field_value(page_info, 1, int(page), wire=0),
                "pagecount": _field_value(page_info, 3, 1, wire=0),
                "limit": _field_value(page_info, 2, int(limit), wire=0),
                "total": _field_value(page_info, 4, len(videos), wire=0)}

    def detail(self, vod_id):
        self.last_detail_error = ""
        payload = (_field_varint(1, int(vod_id)) + _field_bytes(3, APP_VERSION)
                   + _field_bytes(4, b"1") + _field_varint(5, 1))
        response = self.request(62, payload,
                                extra_headers={"x-player-page-protection": "1"})
        data = _field_value(response, 4, b"", wire=2)
        name = _text(_field_value(data, 5, b"", wire=2))
        guard_text = " ".join(
            [_text(_field_value(data, field, b"", wire=2)) for field in (5, 13, 21)]
            + [_text(_field_value(source, 1, b"", wire=2))
               for source in _field_values(data, 75, wire=2)]).lower()
        if any(marker in guard_text for marker in VERSION_GUARD_MARKERS):
            self.last_detail_error = "server_version_guard"
            return None
        if not name or name.startswith("最新版本下载地址") or _field_value(data, 1, 0, wire=0) == 0:
            self.last_detail_error = "invalid_detail"
            return None
        sources = []
        for source in _field_values(data, 75, wire=2):
            code = _text(_field_value(source, 1, b"", wire=2))
            if not code or code.startswith("__v99_"):
                continue
            config = self.players.get(code, {})
            episodes = []
            for episode in _field_values(source, 2, wire=2):
                episode_id = _text(_field_value(episode, 3, b"", wire=2))
                if not episode_id:
                    continue
                episodes.append({
                    "index": _field_value(episode, 1, len(episodes) + 1, wire=0),
                    "id": episode_id,
                    "name": _text(_field_value(episode, 4, b"", wire=2)) or "第%d集" % (len(episodes) + 1)})
            if episodes:
                sources.append({"code": code,
                                "name": config.get("name", code),
                                "parser_id": (config.get("parser_ids") or [0])[0],
                                "episodes": episodes})
        return {"id": str(_field_value(data, 1, vod_id, wire=0)),
                "name": name, "pic": _text(_field_value(data, 13, b"", wire=2)),
                "remarks": _text(_field_value(data, 22, b"", wire=2)),
                "content": _text(_field_value(data, 21, b"", wire=2)),
                "area": _text(_field_value(data, 28, b"", wire=2)),
                "year": _text(_field_value(data, 30, b"", wire=2)),
                "sources": sources}

    def play(self, parser_id, play_id):
        payload = _field_varint(1, int(parser_id)) + _field_bytes(2, play_id)
        response = self.request(69, payload)
        data = _field_value(response, 4, b"", wire=2)
        return _text(_field_value(data, 2, b"", wire=2))

    def reset_session(self):
        self.session_id = ""
        self.session_key = b""
        self.request_id = 0


# ============ T3 接口 ============

class GuluSpider:
    """咕噜咕噜"""

    source_name = "gulu"
    display_name = "咕噜咕噜"

    HOST = HOST
    UA = USER_AGENT

    # 33 条，与 2026-10-20 实测对齐（ffprobe 验过：菲乐4K 是全表唯一真 3840x2160
    # HEVC，排第一）。条数不要动：_rank 的兜底档位 10.5/16.5/18.5/18.6/21.5 就是
    # 按这 33 条的 4K 段 0-10、2K 段 11-16、☆ 段 19-23、平台段 24-32 折出来的。
    _play_order = [
        "菲乐4K", "新咕噜4K", "鲸宝4K", "VIP4K", "至臻4K", "至臻4k",
        "咕噜4K", "爱壹帆4K", "玫瑰4K", "咖啡4K", "臻影4K",
        "精品2K", "菲乐2K", "蓝光2K", "蓝光2k", "鲸宝2K", "短剧2K",
        "神话", "天堂",
        "☆讯飞☆", "☆奇趣☆", "☆果汁☆", "☆酷萌☆", "☆哔哩☆",
        "咖啡", "量子", "非凡", "暴风", "蚂蚁", "小熊", "极速",
        "海外", "花旗",
    ]
    _categories = [("1", "电影"), ("2", "电视剧"), ("3", "综艺"),
                   ("4", "动漫"), ("5", "短剧"), ("60", "直播")]

    # ---- 二级分类（筛选字段经服务器实测：F8=类型，F6=地区，F18=排序） ----
    _filter_genres = ["动作", "喜剧", "爱情", "科幻", "恐怖", "剧情", "战争", "犯罪",
                      "悬疑", "动画", "冒险", "奇幻", "惊悚", "家庭"]
    _filter_areas = ["大陆", "香港", "台湾", "美国", "日本", "韩国", "英国", "法国",
                     "泰国", "印度"]
    _filter_sorts = [("月热门", "vod_hits_month"), ("周热门", "vod_hits_week"),
                     ("日热门", "vod_hits_day"), ("最新", "vod_time"),
                     ("评分", "vod_score")]

    @classmethod
    def _filters_for(cls, tid):
        if str(tid) == "60":
            return []
        def _row(key, pairs):
            return {"key": key, "name": key,
                    "value": [{"n": "全部", "v": ""}] + [{"n": n, "v": v} for n, v in pairs]}
        return [
            _row("类型", [(g, g) for g in cls._filter_genres]),
            _row("地区", [(a, a) for a in cls._filter_areas]),
            _row("排序", list(cls._filter_sorts)),
        ]

    @staticmethod
    def _extend_value(extend, key):
        if not extend:
            return ""
        if isinstance(extend, str):
            try:
                extend = json.loads(extend)
            except Exception:
                return ""
        if isinstance(extend, dict):
            return str(extend.get(key) or "").strip()
        return ""

    def __init__(self) -> None:
        self.protocol = _GuluProtocol()
        self.last_error = ""
        # ---- 蜘蛛框架py 模板契约 ----
        self.header = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S9080) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Referer": HOST,
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self.s = self.session = self.sess = _requests.Session() if _requests else None

    def _get(self, url, referer=None):
        h = dict(self.header)
        if referer:
            h["Referer"] = referer
        if self.s is not None:
            try:
                r = self.s.get(url, headers=h, timeout=12, allow_redirects=True)
                if r.status_code < 400:
                    return r.text
            except Exception:
                pass
        try:
            import urllib.request
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=12) as resp:
                return resp.read().decode("utf-8", "ignore")
        except Exception:
            return ""

    def _u(self, u):
        if not u:
            return u
        u = u.strip()
        if u.startswith("//"):
            return "https:" + u
        if u.startswith("http"):
            return u
        if u.startswith("/"):
            m = re.match(r"(https?://[^/]+)", HOST)
            return (m.group(1) if m else HOST) + u
        return HOST.rstrip("/") + "/" + u.lstrip("/")

    def isVideoFormat(self, url):
        if not url:
            return False
        u = str(url).lower()
        return u.endswith((".m3u8", ".mp4", ".flv", ".mkv", ".ts", ".avi")) or "m3u8" in u

    def init(self, extend=""):
        """drpy 空闲刷新钩子：仅复位会话无关状态，不依赖本方法被执行。"""
        return None

    def _ensure_boot(self) -> None:
        try:
            if not self.protocol.session_id:
                self.protocol.handshake()
            if not self.protocol.players:
                self.protocol.boot()
        except Exception as e:
            self.last_error = "%s:%s" % (type(e).__name__, e)

    # 只有可自恢复的限流/网关抖动才值得再等一次；硬错误立刻收工，别拖慢分类页
    _RETRYABLE = re.compile(
        r'(429|500|502|503|504|timeout|timed out|限流|连接被|reset)', re.I)

    def _search(self, keyword, page=1, limit=21, category_id="", genre="", area="",
                sort="vod_hits_month"):
        self._ensure_boot()

        def once():
            return self.protocol.search(keyword, page, limit, category_id,
                                        genre=genre, area=area, sort=sort)

        last = ''
        for attempt in range(3):
            if attempt == 1:
                try:
                    self.protocol.reset_session()
                    self._ensure_boot()
                except Exception:
                    pass
            elif attempt == 2:
                # 密集请求后服务端会短时 429，隔一会儿通常自己恢复。
                # 旧逻辑两次失败就静默返回空列表，用户看到的是「这个分类没有片」；
                # 这里只在可恢复错误上多给一次机会，并把故障标记透传给聚合层。
                if not self._RETRYABLE.search(last):
                    break
                time.sleep(0.45)
                try:
                    self.protocol.reset_session()
                    self._ensure_boot()
                except Exception:
                    pass
            try:
                res = once()
                # 成功后必须清掉旧错误，否则一次 429 会让 last_error 一直带着旧值
                self.last_error = ''
                return res
            except Exception as e:
                last = '%s: %s' % (type(e).__name__, e)
        self.last_error = last
        return {"videos": [], "page": page, "pagecount": 1,
                "limit": limit, "total": 0, "_error": last}

    # ---- T3 契约 ----

    def homeContent(self, filter=False):
        classes = [{"type_id": tid, "type_name": nm} for tid, nm in self._categories]
        filters = {tid: self._filters_for(tid) for tid, nm in self._categories}
        cards = []
        try:
            result = self._search("", 1, 21)
            cards = self._cards(result.get("videos", []), 1, 21)[:20]
        except Exception:
            pass
        return {"class": classes, "filters": filters, "list": cards}

    def homeVideoContent(self):
        return self.homeContent()

    def categoryContent(self, tid, pg="1", filter=True, extend=""):
        pg = max(1, int(pg or 1))
        tid = str(tid or "").strip()
        genre = self._extend_value(extend, "类型")
        area = self._extend_value(extend, "地区")
        sort = self._extend_value(extend, "排序") or "vod_hits_month"
        result = self._search("", pg, 21, tid, genre=genre, area=area, sort=sort)
        out = {"class": [{"type_id": t, "type_name": nm}
                         for t, nm in self._categories],
               "filters": {t: self._filters_for(t) for t, nm in self._categories},
               "list": self._cards(result.get("videos", []), pg, 21),
               "page": pg, "pagecount": result.get("pagecount", 1),
               "limit": result.get("limit", 21), "total": result.get("total", 0)}
        if result.get("_error"):
            out["_error"] = result["_error"]
        return out

    def detailContent(self, ids, flags=None):
        vod_id = self._detail_id(ids)
        if not vod_id:
            return {"list": []}
        self._ensure_boot()
        try:
            detail = self.protocol.detail(vod_id)
        except Exception:
            self.protocol.reset_session()
            self._ensure_boot()
            detail = self.protocol.detail(vod_id)
        if not detail:
            return {"list": []}

        play_from, play_blocks = [], []
        for source in detail["sources"]:
            episodes = []
            for ep in source["episodes"]:
                idx = ep["index"] or len(episodes) + 1
                encoded = "{}@{}@{}@{}".format(ep["id"], source["parser_id"],
                                               detail["name"], idx)
                episodes.append("%s$%s" % (ep["name"], encoded))
            if episodes:
                play_from.append(self._clean_name(source["name"]))
                play_blocks.append("#".join(episodes))
        paired = list(zip(play_from, play_blocks))
        paired.sort(key=lambda x: self._rank(x[0]))

        vod = {
            "vod_id": detail["id"],
            "vod_name": detail["name"],
            "vod_pic": detail["pic"],
            "vod_year": detail["year"],
            "vod_area": detail["area"],
            "vod_content": detail["content"],
            "vod_remarks": detail["remarks"],
            "vod_play_from": "$$$".join(p[0] for p in paired),
            "vod_play_url": "$$$".join(p[1] for p in paired),
        }
        return {"list": [vod]}

    def searchContent(self, key, quick=False, pg="1"):
        kw = (key or "").strip()
        if not kw:
            return {"list": []}
        pg = max(1, int(pg or 1))
        result = self._search(kw, pg, 21)
        out = {"list": self._cards(result.get("videos", []), pg, 21)}
        if result.get("_error"):
            out["_error"] = result["_error"]
        return out

    def playerContent(self, flag, ids, vipFlags=None):
        # TVBox 传 list（如 ["id@parser@name@1"]），CLI 传 str，统一解包
        id = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        id = str(id or "").strip()
        try:
            raw_id, parser_id, _vod_name, _episode_index = id.split("@", 3)
            parser_id = int(parser_id or 0)
        except ValueError:
            raw_id, parser_id = id, 0
        url = raw_id if (isinstance(raw_id, str) and self._is_playable_url(raw_id)) else ""
        if not url and parser_id:
            self._ensure_boot()
            # FALLBACK_PARSERS 是给「boot 里没下发、但线上还在用」的解析器兜底
            # （28 咕噜金牌）。早先只查 protocol.parsers，兜底表定义了却从不生效，
            # 这类线路点了必空。
            parser = (self.protocol.parsers.get(parser_id)
                      or FALLBACK_PARSERS.get(parser_id, {}))
            if parser and not parser.get("server", True):
                try:
                    url = self._external_play(parser_id, raw_id)
                except Exception:
                    url = ""
            if not url:
                try:
                    url = self.protocol.play(parser_id, raw_id)
                except Exception:
                    try:
                        self.protocol.reset_session()
                        self._ensure_boot()
                        url = self.protocol.play(parser_id, raw_id)
                    except Exception:
                        url = ""
        # header 必须按「最终播出地址」算：picovr / ppvod / quark 这几家带 Referer
        # 反而 403，而它们的域名只有在解析完成后才出现在 url 里，拿原始 id 算不出来。
        # 解析器偶尔把「自己站点首页」当结果返回（蚂蚁 → http://jx.91by.top/），
        # 播放器拉一个落地页只能黑屏；只拦这种纯域名根路径，别误杀无后缀真直链。
        if url and re.match(r"(?i)^https?://[^/]+/?$", url):
            url = ""
        header = self._play_header(url or raw_id)
        return {"parse": 0, "url": url or "", "header": json.dumps(header)}

    # ---- 工具 ----

    # 版本守卫占位条目（服务端要求升级时，列表里会混进这些「下载最新版」的假视频）。
    # 必须覆盖 SEARCH_GUARD_MARKERS 全部：__v99_ 是接口版本号前缀、111.170.58.215
    # 是旧解析器域名，早先漏了这两个，搜索/首页偶发冒出一条假片。
    _PROMO_MARKS = ("__v99_", "glgl.tv", "111.170.58.215", "shu.jpg",
                    "版本已失效", "下载地址")

    @classmethod
    def _is_promo(cls, name, pic):
        blob = "%s %s" % (name or "", pic or "")
        return any(mk in blob for mk in cls._PROMO_MARKS)

    def _cards(self, videos, page, limit):
        cards = []
        for v in videos:
            if not v.get("vod_id"):
                continue
            name, pic = v.get("vod_name") or "", v.get("vod_pic") or ""
            if self._is_promo(name, pic):
                continue
            cards.append({"vod_id": str(v["vod_id"]), "vod_name": name,
                          "vod_pic": pic,
                          "vod_remarks": v.get("vod_remarks") or ""})
        return cards

    @staticmethod
    def _detail_id(ids) -> str:
        text = str(ids).strip()
        if text.isdigit():
            return text
        m = re.search(r"(?:^|[^0-9])(\d{1,12})(?:$|[^0-9])", text)
        return m.group(1) if m else ""

    @staticmethod
    def _clean_name(name: str) -> str:
        if not name:
            return ""
        c = re.sub(r'[【\[\(（].*?[】\]）)]', '', name)
        c = re.sub(r'\s*(?:HD|VIP|备用|推荐|极速|高清|标清|蓝光|超清|试看|抢先|预告|新版|旧版)\s*$',
                   '', c, flags=re.I)
        return re.sub(r'\s+', ' ', c).strip()

    @classmethod
    def _rank(cls, nm: str) -> float:
        c = cls._clean_name(nm).lower()
        for i, name in enumerate(cls._play_order):
            if c == name.lower() or c.startswith(name.lower()) or name.lower() in c:
                return i
        # 名单外的线按画质折进对应分段之间，而不是一律甩到名单末尾：
        # 早先兜底从 1000 起，未名单的 4K 线反而排在名单里的 ☆ 平台线之后。
        up = cls._clean_name(nm).upper()
        if "4K" in up or "2160" in up:
            return 10.5
        if "2K" in up:
            return 16.5
        if "蓝光" in nm:
            return 18.5
        if "1080" in up or "超清" in nm:
            return 18.6
        if "☆" in nm:
            return 21.5
        return 100

    def _play_header(self, url: str) -> dict:
        # 多数第三方 CDN 带不带 Referer 都能播；但 picovr / ppvod / quark
        # 带 Referer 反而 403（实测）。动态：这些域名去 Referer。
        _no_ref = ("picovr.com", "ppvod", "drive.quark.cn")
        h = {"User-Agent": USER_AGENT}
        if not (url and any(d in url for d in _no_ref)):
            h["Referer"] = self.HOST + "/"
        return h

    def _is_playable_url(self, value) -> bool:
        if not isinstance(value, str):
            return False
        url = value.strip()
        if not re.match(r"^https?://", url, re.I):
            return False
        return any(m in url.lower() for m in
                   (".m3u8", ".mp4", ".mkv", ".flv", ".ts", "/m.php", "?data="))

    def _external_play(self, parser_id, play_id) -> str:
        parser = self.protocol.parsers.get(parser_id, {})
        api_url = str(parser.get("url") or "").strip()
        if not api_url:
            return ""
        encoded = quote(str(play_id), safe="")
        target = api_url.replace("{url}", encoded) if "{url}" in api_url else api_url + encoded
        try:
            status, body = _http_get(target, {"User-Agent": USER_AGENT}, 15)
            payload = json.loads(body.decode("utf-8", "replace")) if status == 200 else {}
        except Exception:
            payload = {}
        return self._extract_play_url(payload, parser.get("result_key") or "url")

    def _extract_play_url(self, value, preferred_key="url") -> str:
        if isinstance(value, str):
            return value if self._is_playable_url(value) else ""
        if isinstance(value, dict):
            for key in (preferred_key, "url", "play_url", "playUrl", "m3u8", "data"):
                if key in value:
                    found = self._extract_play_url(value[key], preferred_key)
                    if found:
                        return found
            for item in value.values():
                found = self._extract_play_url(item, preferred_key)
                if found:
                    return found
        elif isinstance(value, (list, tuple)):
            for item in value:
                found = self._extract_play_url(item, preferred_key)
                if found:
                    return found
        return ""

    # ---- drpy 兼容辅助 ----

    def getName(self):
        return self.display_name

    def getDependence(self):
        return []

    def localProxy(self, param):
        u = param.get("url", "") if isinstance(param, dict) else ""
        if not u:
            return [403, "text/plain", b"", None]
        h = dict(self.header)
        if self.s is not None:
            try:
                r = self.s.get(u, headers=h, timeout=15)
                return [200, r.headers.get("Content-Type", "application/octet-stream"),
                        r.content, None]
            except Exception:
                pass
        try:
            import urllib.request
            req = urllib.request.Request(u, headers=h)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return [200, resp.headers.get("Content-Type", "application/octet-stream"),
                        resp.read(), None]
        except Exception:
            return [403, "text/plain", b"", None]

    def manualVideoCheck(self):
        return False

    def action(self, action):
        return {}

    def destroy(self):
        return None


# ============ 模块级双入口（drpy site 模式 / 旧内核兼容） ============

_SINGLETON = None


def _get_singleton():
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = GuluSpider()
    return _SINGLETON


def homeContent(filter=False):
    return _get_singleton().homeContent(filter)


def homeVideoContent():
    return _get_singleton().homeVideoContent()


def categoryContent(tid, pg="1", filter=True, extend=""):
    return _get_singleton().categoryContent(tid, pg, filter, extend)


def detailContent(ids, flags=None):
    return _get_singleton().detailContent(ids, flags)


def searchContent(key, quick=False, pg="1"):
    return _get_singleton().searchContent(key, quick, pg)


def playerContent(flag, ids, vipFlags=None):
    return _get_singleton().playerContent(flag, ids, vipFlags)


# 类名别名（部分内核按小写 spider 约定取类）
gulu_spider = GuluSpider


# ============ 命令行自检 ============

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="咕噜咕噜 T3 源自检")
    sub = parser.add_subparsers(dest="action", required=True)

    sub.add_parser("home")
    sub.add_parser("homevideos")

    p_search = sub.add_parser("search")
    p_search.add_argument("keyword")
    p_search.add_argument("pg", nargs="?", default="1")

    p_cate = sub.add_parser("category")
    p_cate.add_argument("tid")
    p_cate.add_argument("pg", nargs="?", default="1")

    p_detail = sub.add_parser("detail")
    p_detail.add_argument("vod_id")

    p_play = sub.add_parser("play")
    p_play.add_argument("encoded_id",
                        help='完整选集 id，形如 "play_id@parser_id@vod名@序号"，'
                             '也可直接传可播 URL')

    args = parser.parse_args()
    sp = GuluSpider()
    try:
        if args.action == "home":
            result = sp.homeContent()
        elif args.action == "homevideos":
            result = sp.homeVideoContent()
        elif args.action == "search":
            result = sp.searchContent(args.keyword, pg=args.pg)
        elif args.action == "category":
            result = sp.categoryContent(args.tid, args.pg)
        elif args.action == "detail":
            result = sp.detailContent(args.vod_id)
        elif args.action == "play":
            result = sp.playerContent("", args.encoded_id)
        else:
            result = {}
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    except Exception as error:
        sys.stderr.write("%s: %s\n" % (type(error).__name__, error))
        sys.exit(1)


# ==================== 云端自更新 ====================
_KISH_UPD = {}


def _kish_check(url=None):
    """兼容旧调用名：统一走 check_update（强制 sha256 + 证书校验）。"""
    return check_update(url or UPDATE_URL)


def _kish_update_async(url=None):
    if _KISH_UPD:
        return
    _KISH_UPD['run'] = True

    def run():
        try:
            _KISH_UPD.update(_kish_check(url))
        except Exception:
            pass

    try:
        threading.Thread(target=run, daemon=True).start()
    except Exception:
        pass


# ==================== Kishuto 总门面 ====================
# ============================================================================
# 模块：诊断中心（Kishuto Diag）
#
# 用标准 py 协议模拟「设置中心」：分类 → 卡片 → 点开执行并显示报告。
# 不依赖壳的 action 回调，任何支持 py 源的壳都能用。
# 用法：配置里加第二个站点，api 同一个 py，ext 写 {"mode":"settings"}。
# ============================================================================

DIAG_BASE = 'https://gitee.com/tao060702/tvbox/raw/master'


QR_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
         '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')


# ---------------------------------------------------------------------------
# 诊断中心卡片磁贴的本地图片服务：纯标准库 PNG 编码 + 127.0.0.1 HTTP。
# 不联网、不依赖 PIL / 字体；磁贴由 _diag_card_png() 生成。
# ---------------------------------------------------------------------------

_QR_SRV = {'port': 0, 'cards': {}}


def _qr_png_write(w, h, rows):
    """rows 是 RGB 像素行（bytearray(w*3)），编码成 PNG 字节。"""
    import struct
    import zlib

    def chunk(typ, body):
        return (struct.pack('>I', len(body)) + typ + body
                + struct.pack('>I', zlib.crc32(typ + body) & 0xffffffff))

    raw = b''.join(b'\x00' + bytes(r) for r in rows)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))
            + chunk(b'IEND', b''))


def _qr_server():
    """起一次本地图片服务（端口 39789 起顺延），返回端口号。

    绑定成功后会自发一个探针请求，确认应答确实来自本服务；否则顺延端口。
    避免 Windows 端口复用时「绑上了、请求却被别的进程接走」导致磁贴 404。
    """
    import threading
    import urllib.request
    if _QR_SRV['port']:
        return _QR_SRV['port']
    try:
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    except Exception:
        return 0
    probe = '_kish_probe.png'
    token = b'\x89PNG\r\n\x1a\nKISH'
    _QR_SRV['cards'][probe] = token

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            key = self.path.split('?')[0].lstrip('/')
            blob = _QR_SRV['cards'].get(key)
            if not blob:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', str(len(blob)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            try:
                self.wfile.write(blob)
            except Exception:
                pass

        def log_message(self, *args):
            pass

    for port in range(39789, 39799):
        srv = None
        try:
            srv = ThreadingHTTPServer(('127.0.0.1', port), Handler)
            srv.daemon_threads = True
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            try:
                with urllib.request.urlopen(
                        'http://127.0.0.1:%d/%s' % (port, probe),
                        timeout=1) as resp:
                    mine = (resp.read() == token)
            except Exception:
                mine = False
            if not mine:
                try:
                    srv.shutdown()
                    srv.server_close()
                except Exception:
                    pass
                continue
            _QR_SRV['srv'] = srv
            _QR_SRV['port'] = port
            return port
        except Exception:
            try:
                if srv:
                    srv.server_close()
            except Exception:
                pass
            continue
    _QR_SRV['cards'].pop(probe, None)
    return 0


# ---------------------------------------------------------------------------
# 诊断中心卡片磁贴：纯标准库生成 PNG，走 _qr_server() 的本地图片服务。
# 不联网、不依赖字体；按分区配色 + 大号编号，避免所有卡片都是灰色占位图。
# ---------------------------------------------------------------------------

_DIAG_FONT = {
    '0': ('01110', '10001', '10001', '10001', '10001', '10001', '01110'),
    '1': ('00100', '01100', '00100', '00100', '00100', '00100', '01110'),
    '2': ('01110', '10001', '00001', '00011', '00110', '01000', '11111'),
    '3': ('11110', '00001', '00001', '01110', '00001', '00001', '11110'),
    '4': ('00010', '00110', '01010', '10010', '11111', '00010', '00010'),
    '5': ('11111', '10000', '11110', '00001', '00001', '10001', '01110'),
    '6': ('01110', '10000', '11110', '10001', '10001', '10001', '01110'),
    '7': ('11111', '00001', '00011', '00110', '01100', '01000', '01000'),
    '8': ('01110', '10001', '10001', '01110', '10001', '10001', '01110'),
    '9': ('01110', '10001', '10001', '01111', '00001', '00011', '01100'),
}

# 分区 -> (顶部色, 底部色, 强调色)
_DIAG_THEME = {
    'overview': ((22, 32, 54), (42, 70, 118), (110, 170, 250)),
    'sources':  ((18, 38, 50), (24, 74, 94), (72, 192, 246)),
    'cache':    ((38, 24, 32), (82, 40, 60), (244, 120, 182)),
    'quality':  ((26, 30, 20), (62, 74, 40), (176, 216, 96)),
}


def _diag_card_png(num, group):
    """生成 400x600 竖版编号磁贴，返回 PNG 字节。"""
    W, H, SC = 400, 600, 18
    top, bot, accent = _DIAG_THEME.get(group, _DIAG_THEME['overview'])
    rows = []
    for y in range(H):
        t = (y * 24 // (H - 1)) / 24.0          # 量化渐变，PNG 体积更小
        c = bytes(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        rows.append(bytearray(c * W))
    ab = bytes(accent)
    for y in range(H):
        rows[y][0:9 * 3] = ab * 9               # 左侧细色条
    s = '%02d' % (num % 100)
    tw = 12 * SC
    x0, y0 = (W - tw) // 2, (H - 7 * SC) // 2 - 34
    white = b'\xeb\xf0\xf8'
    for idx, ch in enumerate(s):
        for gy, line in enumerate(_DIAG_FONT[ch]):
            for gx, bit in enumerate(line):
                if bit != '1':
                    continue
                xx = x0 + idx * (7 * SC) + gx * SC
                yy = y0 + gy * SC
                block = white * SC
                for j in range(yy, yy + SC):
                    rows[j][xx * 3:(xx + SC) * 3] = block
    by = y0 + 7 * SC + 52
    for j in range(by, by + 5):
        bx = (W - 116) // 2
        rows[j][bx * 3:(bx + 116) * 3] = ab * 116
    return _qr_png_write(W, H, rows)


class KishDiag(object):
    """只读诊断：版本 / 配置 / 源探活 / 画质判定 / 缓存管理。"""

    NAME = 'Kishuto 诊断'
    GROUPS = [('overview', '总览'), ('sources', '源状态'),
              ('quality', '画质判定'), ('cache', '缓存配置')]
    GROUP_KEYS = ('overview', 'sources', 'quality', 'cache')

    def __init__(self, sp):
        self.sp = sp

    # ---------------- 卡片 ----------------
    @staticmethod
    def _mk(key, name, remarks=''):
        return {'vod_id': 'dg|' + key, 'vod_name': name, 'vod_pic': '',
                'vod_remarks': remarks}

    def homeContent(self, filter=True):
        return {'class': [{'type_id': k, 'type_name': v} for k, v in self.GROUPS],
                'filters': {},
                'list': self.categoryContent(self.GROUPS[0][0], '1', False, {})['list']}

    def homeVideoContent(self):
        return {'list': self.categoryContent(self.GROUPS[0][0], '1', False, {})['list']}

    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        tid = str(tid or 'overview')
        if tid.startswith('dg|'):
            tid = tid[3:]
        if tid not in self.GROUP_KEYS:
            tid = 'overview'
        sp = self.sp
        if tid == 'overview':
            items = [self._mk('ver', '📦 版本与更新', '本地 %s' % CODE_VERSION),
                     self._mk('cfg', '⚙️ 运行配置', '首页源 %s' % getattr(sp, 'HOME_SOURCE', 'yt')),
                     self._mk('speed', '⏱ 首屏预算', '其余源等 %.1fs' % sp.FILL_BUDGET),
                     self._mk('help', '📖 使用说明', '各分区功能速查')]
        elif tid == 'sources':
            with _LAST_SEARCH_LOCK:
                _ls = dict(_LAST_SEARCH)
            _lr = ('%s · %d/%d 源' % (_SEARCH_STATE.get(_ls.get('state'), '未搜索'),
                                      _ls.get('n', 0), _ls.get('total', 0))
                   if _ls else '还没搜过')
            items = [self._mk('srcall', '🔍 全部探活', '逐个源跑搜索 + 详情'),
                     self._mk('spartial', '🧭 上次搜索', _lr)]
            for tag in sp.ORDER:
                items.append(self._mk('src:%s' % tag,
                                      '▸ %s' % sp.LABELS.get(tag, tag),
                                      '单独探活'))
        elif tid == 'quality':
            items = [self._mk('qdiag', '📺 画质判定日志', '最近 %d 条' % len(_QDIAG)),
                     self._mk('qcache', '🎚 线路高度缓存', '按片隔离的实测记录')]
        elif tid == 'cache':
            items = [self._mk('cache', '📊 缓存状态', '内存缓存条数'),
                     self._mk('cacheclear', '🧹 清空缓存', '点开即执行')]
        else:
            items = []
        # 统一磁贴：本地生成、不联网；ext 加 {"diag_plain":1} 可关掉
        cfg = getattr(sp, 'cfg', {}) or {}
        if str(cfg.get('diag_plain') or '') not in ('1', 'true', 'yes'):
            try:
                port = _qr_server()
                cards = _QR_SRV.setdefault('cards', {})
                for i, it in enumerate(items, 1):
                    ck = 'c_%s_%02d.png' % (tid, i)
                    if ck not in cards:
                        cards[ck] = _diag_card_png(i, tid)
                    it['vod_pic'] = ('http://127.0.0.1:%d/%s?v=1'
                                     % (port, ck)) if port else ''
            except Exception:
                pass
        return {'list': items, 'page': 1, 'pagecount': 1, 'limit': 50,
                'total': len(items)}

    def searchContent(self, key, quick=False, pg='1'):
        return {'list': []}

    def playerContent(self, flag, pid, vipflags=None):
        raw = str(pid or '').strip()
        url = raw if raw.startswith('http') else ''
        if not url:
            try:
                pad = '=' * (-len(raw) % 4)
                url = base64.urlsafe_b64decode(raw + pad).decode('utf-8', 'replace')
            except Exception:
                url = ''
        if not url.startswith('http'):
            return {'parse': 0, 'jx': 0, 'url': ''}
        # 预留：网页类线路交给壳的 webview
        if '网页' in str(flag or ''):
            return {'parse': 1, 'jx': 0, 'url': url,
                    'header': {'User-Agent': QR_UA}}
        return {'parse': 0, 'jx': 0, 'url': url,
                'header': {'User-Agent': QR_UA}}

    # ---------------- 执行 ----------------
    def detailContent(self, ids):
        raw = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        key = str(raw or '')
        if key.startswith('dg|'):
            key = key[3:]
        try:
            got = self._run(key)
            title, report = got[0], got[1]
            pic = got[2] if len(got) > 2 else ''
        except Exception as exc:
            title, report, pic = '执行失败', '%s: %s' % (type(exc).__name__, exc), ''
        froms, urls = '', ''   # 壳的播放器只认视频，图片塞进去必然报错，不挂线路
        tail = '\n\n── Kishuto 诊断 · %s · %s' % (
            CODE_VERSION, time.strftime('%H:%M'))
        vod = {'vod_id': 'dg|' + key, 'vod_name': title, 'vod_pic': pic,
               'type_name': '诊断', 'vod_remarks': '',
               'vod_content': str(report).rstrip() + tail,
               'vod_play_from': froms, 'vod_play_url': urls}
        return {'list': [vod]}

    def _run(self, key):
        sp = self.sp
        if key == 'ver':
            return self._ver()
        if key == 'cfg':
            return self._cfg()
        if key == 'speed':
            live, peak = _bg_live()
            return ('首屏预算', '详情页等待其余源：%.1f 秒\n'
                    '攒够 %d 条线路提前收工\n'
                    '后台补齐上限：%.1f 秒\n'
                    '搜索预算：%.1f 秒\n'
                    '后台补充任务：%d 个在跑（上限 %d，峰值 %d）'
                    % (sp.FILL_BUDGET, sp.FILL_ENOUGH,
                       sp.TOPUP_BUDGET, sp.SEARCH_BUDGET,
                       live, BG_MAX, peak))
        if key == 'qdiag':
            return ('画质判定日志', _qdiag_text(24))
        if key == 'spartial':
            return ('上次搜索', _search_stat_text(sp.LABELS))
        if key == 'qcache':
            now = time.time()
            with sp._LINE_H_LOCK:
                rows = [(k, v[0], v[1]) for k, v in sp._LINE_H.items()]
            cnt = {'real': 0, 'low': 0, 'unknown': 0}
            live = []
            for k, ts, h in rows:
                nm = k.split('\x1f')[0]
                st = sp._line_h_state(h, nm)
                cnt[st] = cnt.get(st, 0) + 1
                if now - ts < sp.LINE_H_TTL:
                    live.append((ts, nm, st, h))
            live.sort(reverse=True)
            head = ('线路高度缓存 %d 条：真 4K %d、判假 %d、探不到 %d\n'
                    'TTL：真 %.0f 秒 / 判假 %.0f 秒 / 探不到 %.0f 秒\n'
                    'key 带片身份：同一线路名在不同影片里各测各的，不再互相冒充'
                    % (len(rows), cnt.get('real', 0), cnt.get('low', 0),
                       cnt.get('unknown', 0), sp.LINE_H_TTL,
                       sp.LINE_H_LOW_TTL, sp.LINE_H0_TTL))
            if not live:
                return ('线路高度缓存', head + '\n\n当前没有未过期的记录。')
            tail = '\n'.join(
                '%s %s · 实测 %s · %s' % (
                    time.strftime('%H:%M', time.localtime(ts)), nm,
                    _qdiag_h(h), _QDIAG_STATE.get(st, st))
                for ts, nm, st, h in live[:12])
            return ('线路高度缓存', head + '\n\n最近 12 条：\n' + tail)
        if key == 'cache':
            n = len(_CACHE)
            return ('缓存状态', '内存缓存 %d 条\n'
                    '详情缓存 TTL：%d 秒\n搜索缓存 TTL：%d 秒\n'
                    '首页缓存：%d 秒\n分类缓存：%d 秒'
                    % (n, sp.CACHE_TTL, getattr(sp, 'SEARCH_TTL', 600),
                       sp.HOME_TTL, sp.CAT_TTL))
        if key == 'cacheclear':
            n = len(_CACHE)
            try:
                with _CACHE_LOCK:
                    _CACHE.clear()
            except Exception:
                pass
            return ('已清空缓存', '清理 %d 条内存缓存。\n'
                    '（只影响本进程，壳重启后本来也会清空）' % n)
        if key == 'srcall':
            rows, t0 = [], time.time()
            for tag in sp.ORDER:
                rows.append(self._probe(tag))
            return ('全部探活', '\n'.join(rows) + '\n\n合计 %.1f 秒' % (time.time() - t0))
        if key.startswith('src:'):
            tag = key[4:]
            return ('%s 探活' % sp.LABELS.get(tag, tag), self._probe(tag))
        if key == 'help':
            return ('使用说明',
                    'Kishuto 诊断中心 · 只读工具页，不播片。\n\n'
                    '【分区速查】\n'
                    '  总览        版本 / 运行配置 / 首屏预算\n'
                    '  源状态      逐个源实跑搜索 + 详情；上次搜索的到齐情况\n'
                    '  画质判定    最近 80 条「宣称值 vs 实测值」判定，含换源结局\n'
                    '  缓存配置    查看 / 清空内存缓存\n\n'
                    '【外观】\n'
                    '  卡片磁贴由本地生成，不联网。\n'
                    '  不想要磁贴：ext 加 {"diag_plain":1}。')
        return ('未知项', '没有这一项：%s' % key)

    def _ver(self):
        local = CODE_VERSION
        try:
            url = DIAG_BASE + '/update_kishuto.json?t=%d' % int(time.time() * 1000)
            req = urllib.request.Request(url, headers={'User-Agent': 'kish-diag'})
            with urllib.request.urlopen(req, timeout=15) as rsp:
                txt = rsp.read().decode('utf-8', 'replace')
            man = json.loads(txt)
            online = str(man.get('version') or '')
            same = (online == local)
            return ('版本与更新',
                    '本地版本：%s\n线上版本：%s\n%s\n\n'
                    '清单大小：%s 字节\n安装地址：%s'
                    % (local, online or '取不到',
                       '已是最新' if same else '有新版本（重开壳会自动拉取）',
                       man.get('size'), man.get('url') or '-'))
        except Exception as exc:
            return ('版本与更新', '本地版本：%s\n拉取清单失败：%s' % (local, exc))

    def _cfg(self):
        sp = self.sp
        cur_home = str((sp.cfg or {}).get('home_source') or
                       getattr(sp, 'HOME_SOURCE', 'yt'))
        rows = ['首页源：%s（ext home_source 可切 yt/gg/pd）' % cur_home,
                '首页分类上限：%d' % sp.HOME_CLASS_MAX,
                '线路顺序：%s' % ' > '.join(sp.LINE_FIRST),
                '源顺序：%s' % ' > '.join(sp.LABELS.get(t, t) for t in sp.ORDER),
                '详情缓存：%d 秒' % sp.CACHE_TTL]
        ext = sp.cfg or {}
        if ext:
            rows.append('ext 已配置项：%s' % ', '.join(sorted(ext)))
        else:
            rows.append('ext：未配置')
        return ('运行配置', '\n'.join(rows))

    def _probe(self, tag):
        sp = self.sp
        name = sp.LABELS.get(tag, tag)
        try:
            ob = sp._src(tag)
            if ob is None:
                return '%-4s 实例为空' % name
            kw = '芙莉莲' if tag == 'xf' else '庆余年'
            t = time.time()
            got = ob.searchContent(kw, False, '1') or {}
            items = got.get('list') or []
            t1 = time.time() - t
            lines = 0
            if items:
                d = ob.detailContent([items[0].get('vod_id')]) or {}
                v = (d.get('list') or [{}])[0]
                lines = len([x for x in str(v.get('vod_play_from') or '').split('$$$') if x])
            t2 = time.time() - t
            flag = '正常' if items else '无结果'
            return '%-4s %s 搜索 %d 条 %.1fs | 详情 %d 线 %.1fs' % (
                name, flag, len(items), t1, lines, t2)
        except Exception as exc:
            return '%-4s 异常 %s: %s' % (name, type(exc).__name__, str(exc)[:50])

    # ---------------- 兜底：软件内网页登录（纯增量） ----------------


# ==================== 枫奇4K 线路源 fq BEGIN ====================
# -*- coding: utf-8 -*-
"""枫奇4K —— 只保留「至臻4K」「蓝光2K」两条线路（纯标准库，自包含）

原源（枫叶4K影院 / maihaolian.com）详情页共 4 条线路：
    至臻4k / 蓝光2k / 自营y / 自营r
本源只取前两条，播放解析也只保留对应的 JD / co 两个接口。

设计约束（与 Kishuto 聚合一致）：
  * 纯标准库，不用 requests / bs4，可直接并进 Kishuto.py 的同一命名空间；
    所有全局名字一律 fq_ / FQ_ 前缀，避免覆盖其它模块。
  * init() 绝不联网；只有实际请求撞上「系统安全验证」时才惰性过验证码。
  * 验证码识别为纯 Python PNG 解码 + 模板匹配（模板来自原源）。
"""
import html
from http import cookiejar as _fq_cj

try:
    from base.spider import Spider as _FQBase
except Exception:
    class _FQBase(object):
        def getCache(self, key):
            return ''

        def setCache(self, key, value):
            return None

        def log(self, msg):
            return None

FQ_CAP_TPL = {
    0: [0.9045, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045, 0.9045, 0.9045, -1.1055, -1.1055, 0.9045, 0.9045, 0.9045],
    1: [1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, -0.5504, -1.1933, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, -1.1933, -1.1933, -1.1933, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, 1.0567, 1.0567, 0.0924, -1.1933, -1.1933, 0.0924, 1.0567, 1.0567, -1.1933, -1.1933, -1.1933, -1.1933, -1.1933, -1.1933, -1.1933, -1.1933],
    2: [0.8165, 0.8165, -1.2247, -1.2247, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, 0.8165, 0.8165, 0.8165, 0.8165, 0.8165, -1.2247, -1.2247, -1.2247, -1.2247, -1.2247, -1.2247, -1.2247, -1.2247],
    3: [0.7954, -1.2572, -1.2572, -1.2572, -1.2572, -1.2572, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, -1.2572, -1.2572, 0.7954, 0.7954, 0.7954, -1.2572, -1.2572, 0.7954, 0.7954, -1.2572, -1.2572, -1.2572, -1.2572, -1.2572, 0.7954, 0.7954],
    4: [0.8819, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, -1.1339, -1.1339, -1.1339, -1.1339, -1.1339, -1.1339, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, 0.8819, -1.1339, -1.1339, 0.8819],
    5: [-1.078, -1.078, -1.078, -1.078, -1.078, -1.078, -1.078, 0.9276, -1.078, -1.078, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, -1.078, -1.078, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, -1.078, -1.078, 0.9276, -1.078, -1.078, -1.078, 0.9276, 0.9276, -1.078, -1.078, -1.078, 0.9276, 0.9276, -1.078, -1.078, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, -1.078, -1.078, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, 0.9276, -1.078, -1.078, -1.078, -1.078, 0.9276, 0.9276, 0.9276, 0.9276, -1.078, -1.078, 0.9276, -1.078, -1.078, 0.9276, 0.9276, -1.078, -1.078, 0.9276, 0.9276, 0.9276, -1.078, -1.078, -1.078, -1.078, 0.9276, 0.9276],
    6: [0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753],
    7: [-1.4412, -1.4412, -1.4412, -1.4412, -1.4412, -1.4412, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, -1.4412, -1.4412, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939, 0.6939],
    8: [1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0],
    9: [0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, 0.9753, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, -1.0253, -1.0253, 0.9753, 0.9753, 0.9753, -1.0253, -1.0253, -1.0253, -1.0253, 0.9753, 0.9753],
}


def fq_decode_png(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n': raise ValueError('not png')
    pos, width, height, idat = 8, None, None, b''
    while pos < len(data):
        ln, typ, chunk = struct.unpack('>I', data[pos:pos+4])[0], data[pos+4:pos+8], data[pos+8:pos+8+struct.unpack('>I', data[pos:pos+4])[0]]
        pos += 12 + ln
        if typ == b'IHDR': width, height, bit_depth, color_type = struct.unpack('>IIBB', chunk[:10])
        elif typ == b'IDAT': idat += chunk
        elif typ == b'IEND': break
    if color_type not in (0, 2, 3, 4, 6): raise ValueError('color type')
    channels, stride, raw = {0:1, 2:3, 3:1, 4:2, 6:4}[color_type], width * {0:1, 2:3, 3:1, 4:2, 6:4}[color_type], zlib.decompress(idat)
    prev, gray, p = bytearray(stride), [], 0
    for y in range(height):
        ft, line, p = raw[p], bytearray(raw[p+1:p+1+stride]), p + 1 + stride
        if ft == 1:
            for i in range(channels, stride): line[i] = (line[i] + line[i-channels]) & 0xff
        elif ft == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 0xff
        elif ft == 3:
            for i in range(stride): line[i] = (line[i] + (((line[i-channels] if i >= channels else 0) + prev[i]) >> 1)) & 0xff
        elif ft == 4:
            for i in range(stride):
                a, b, c = line[i-channels] if i >= channels else 0, prev[i], prev[i-channels] if i >= channels else 0
                pp = a + b - c; pa, pb, pc = abs(pp-a), abs(pp-b), abs(pp-c)
                line[i] = (line[i] + (a if (pa <= pb and pa <= pc) else (b if pb <= pc else c))) & 0xff
        if color_type in (2, 6): step = 3 if color_type == 2 else 4; rows = [int(line[x*step]*0.299 + line[x*step+1]*0.587 + line[x*step+2]*0.114) for x in range(width)]
        elif color_type == 4: rows = [line[x*2] for x in range(width)]
        else: rows = list(line[:width])
        gray.append(rows); prev = line
    return width, height, gray

def fq_cap_resize(block, tw=8, th=10):
    bh, bw = len(block), len(block[0])
    flat = []
    for ty in range(th):
        yf = ty * (bh - 1) / (th - 1)
        y0 = int(yf); y1 = min(y0 + 1, bh - 1); fy = yf - y0
        for tx in range(tw):
            xf = tx * (bw - 1) / (tw - 1)
            x0 = int(xf); x1 = min(x0 + 1, bw - 1); fx = xf - x0
            v = (block[y0][x0] * (1 - fx) + block[y0][x1] * fx) * (1 - fy) + (block[y1][x0] * (1 - fx) + block[y1][x1] * fx) * fy
            flat.append(v)
    return flat


def fq_cap_norm(vals):
    n = len(vals)
    m = sum(vals) / n
    var = sum((v - m) ** 2 for v in vals) / n
    sd = var ** 0.5 if var > 0 else 1.0
    return [(v - m) / sd for v in vals]


def fq_recognize_captcha(data):
    """识别 4 位数字验证码：
    - 纯 Python PNG 解码（fq_decode_png）
    - 自适应阈值二值化 → 列投影切 4 段
    - 每字符灰度块双线性缩放 8x10 → 零均值单位方差归一化
    - 与 FQ_CAP_TPL（按真实验证码样本训练的归一化模板）做余弦相关取 argmax
    - 任一字符置信度 < 0.85 判为失败（返回 None，由调用方换图重试）
    模板于 2026-10 针对 maihaolian.com/zzztool.com 现行验证码字体重新拟合。
    """
    try:
        W, H, gray = fq_decode_png(data)
    except Exception:
        return None
    avg = sum(sum(r) for r in gray) / (W * H) if W * H else 128
    thr = min(max(avg * 0.8, 80), 170)
    bw = [[1 if gray[y][x] < thr else 0 for x in range(W)] for y in range(H)]
    col_sums = [sum(bw[y][x] for y in range(H)) for x in range(W)]
    segs, inseg, start = [], False, 0
    for x in range(W):
        if col_sums[x] > 0 and not inseg:
            start, inseg = x, True
        elif col_sums[x] == 0 and inseg:
            if x - start >= 3:
                segs.append((start, x - 1))
            inseg = False
    if inseg and (W - start >= 3):
        segs.append((start, W - 1))
    if len(segs) != 4:
        return None
    result = ''
    for s, e in segs:
        rows = [y for y in range(H) if any(gray[y][x] < thr for x in range(s, e + 1))]
        if not rows:
            return None
        block = [[gray[y][x] for x in range(s, e + 1)] for y in range(rows[0], rows[-1] + 1)]
        vec = fq_cap_norm(fq_cap_resize(block))
        best_d, best_s = None, -1e9
        for d in range(10):
            sc = sum(a * b for a, b in zip(vec, FQ_CAP_TPL[d])) / len(vec)
            if sc > best_s:
                best_d, best_s = d, sc
        if best_s < 0.85:
            return None
        result += str(best_d)
    return result

FQ_SITE = 'https://maihaolian.com'
FQ_UA = ('Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 '
         'Chrome/150.0.0.0 Mobile')
FQ_HDRS = {
    'User-Agent': FQ_UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Upgrade-Insecure-Requests': '1',
    'Referer': FQ_SITE + '/',
}
# 只认这两条线路；(页面上的原始名, 输出显示名)，顺序即默认选线顺序
FQ_LINES = (('至臻4k', '至臻4K'), ('蓝光2k', '蓝光2K'))
FQ_PARSE = {
    'JD': 'https://fgsrg.hzqingshan.com',
    'co': 'https://zzrs.mfdyvip.com',
}
FQ_RE_PLAYER = re.compile(r'var\s+player_aaaa[\s\S]*?"url"\s*:\s*"([^"]+)"')
FQ_RE_URL_VAR = re.compile(r'url\s*[:=]\s*["\'](http[^"\']+)["\']')
FQ_RE_TOKEN = re.compile(r'data-te="([^"]+)"')
FQ_RE_CARD = re.compile(
    r'<a[^>]*class="[^"]*public-list-exp[^"]*"[^>]*>(.*?)</a>', re.S)
FQ_RE_HREF = re.compile(r'href="([^"]+)"')
FQ_RE_TITLE = re.compile(r'title="([^"]*)"')
FQ_RE_PIC = re.compile(
    r'<img[^>]*?\b(?:data-src|src)="([^"]+)"', re.S)
FQ_RE_ALT = re.compile(r'<img[^>]*?\balt="([^"]*)"', re.S)
FQ_RE_PRT = re.compile(r'class="[^"]*public-prt-g[^"]*"[^>]*>([^<]*)<')
FQ_RE_FT2 = re.compile(r'<i class="ft2">([^<]*)</i>')
FQ_RE_FT2B = re.compile(
    r'class="[^"]*public-list-prb[^"]*"[^>]*>\s*([^<]+)<')
FQ_RE_SLIDE = re.compile(r'<a\s+class="swiper-slide"[^>]*>(.*?)</a>', re.S)
FQ_RE_EP = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>([^<]*)</a>')
FQ_RE_PAGE_TIP = re.compile(r'\d+/(\d+)页')
FQ_RE_SPACE = re.compile(r'\s+')

FQ_JAR = _fq_cj.CookieJar()
FQ_OPENER = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(FQ_JAR))
FQ_LOCK = threading.Lock()
FQ_VERIFIED = {'at': 0.0}
FQ_CACHE = {}
FQ_LINE_SID = {}       # 片 id -> {线路名: 播放页 sid}，用于同集回落


def fq_clean(text):
    """线路/片名清洗：去掉会破坏 TVBox 分隔符的字符。"""
    s = html.unescape(str(text or ''))
    return FQ_RE_SPACE.sub(' ', s.replace('$', '').replace('#', '')
                          .replace('|', '')).strip()


def fq_abs(url):
    u = str(url or '').strip()
    if u.startswith('http'):
        return u
    return FQ_SITE + (u if u.startswith('/') else '/' + u)


def fq_raw(url, data=None, referer=None, ctype=None, timeout=12):
    """统一请求层；返回 bytes。"""
    h = dict(FQ_HDRS)
    h['Referer'] = referer or (FQ_SITE + '/')
    if data is not None and ctype:
        h['Content-Type'] = ctype
    req = urllib.request.Request(url, data=data, headers=h)
    with FQ_OPENER.open(req, timeout=timeout) as resp:
        return resp.read()


def fq_verify():
    """惰性过「系统安全验证」：识别 4 位数字验证码并提交，最多 4 次。"""
    with FQ_LOCK:
        if time.time() - FQ_VERIFIED['at'] < 30:
            return True
        for i in range(4):
            try:
                cap = fq_raw(FQ_SITE + '/captcha.php?type=code&r=0.%d'
                             % (12345 + i), timeout=10)
                code = fq_recognize_captcha(cap)
                if not code:
                    continue
                body = urllib.parse.urlencode({'check': code}).encode()
                txt = fq_raw(FQ_SITE + '/captcha.php?type=verify', data=body,
                             ctype='application/x-www-form-urlencoded',
                             timeout=10).decode('utf-8', 'replace')
                if '"code":1' in txt.replace(' ', ''):
                    FQ_VERIFIED['at'] = time.time()
                    return True
            except Exception:
                pass
        return False


def fq_get(url, data=None, referer=None, ctype=None, timeout=12, retry=True):
    """返回页面文本；撞上验证页时自动过一次验证码再重试。"""
    try:
        raw = fq_raw(url, data=data, referer=referer, ctype=ctype,
                     timeout=timeout)
        txt = raw.decode('utf-8', 'replace')
        if retry and '系统安全验证' in txt:
            if fq_verify():
                raw = fq_raw(url, data=data, referer=referer, ctype=ctype,
                             timeout=timeout)
                txt = raw.decode('utf-8', 'replace')
        return txt
    except Exception:
        return ''


def fq_parse_list(txt):
    """首页 / 分类 / 搜索共用的卡片解析（maihaolian 模板）。"""
    out = []
    for m in FQ_RE_CARD.finditer(txt):
        tag = m.group(0)
        inner = m.group(1)
        hr = FQ_RE_HREF.search(tag)
        if not hr:
            continue
        ti = FQ_RE_TITLE.search(tag)
        alt = FQ_RE_ALT.search(inner)
        pic = FQ_RE_PIC.search(inner)
        prt = FQ_RE_PRT.search(inner)
        ft2 = FQ_RE_FT2.search(inner) or FQ_RE_FT2B.search(inner)
        # 首页卡片把片名放 title；搜索页放 img 的 alt
        name = fq_clean((ti.group(1) if ti else '') or
                        (alt.group(1) if alt else ''))
        if not name:
            continue
        out.append({
            'vod_id': hr.group(1),
            'vod_name': name,
            'vod_pic': html.unescape(pic.group(1)) if pic else '',
            'vod_remarks': fq_clean(ft2.group(1)) if ft2 else '',
            'vod_year': ('「%s」' % fq_clean(prt.group(1))) if prt else '',
        })
    return out


def fq_page_count(txt):
    m = FQ_RE_PAGE_TIP.search(txt)
    return int(m.group(1)) if m else 1


def fq_sid_of(eps):
    """从选集链接 /play/<片id>-<线路sid>-<集号>.html 里取线路 sid。"""
    for _, href in eps[:3]:
        m = re.search(r'/play/\d+-(\d+)-\d+\.html', href)
        if m:
            return m.group(1)
    return ''


def fq_fallback_url(pid):
    """某条线路的解析站返回失败时，换另一条线路的同集播放页。"""
    m = re.search(r'/play/(\d+)-(\d+)-(\d+)\.html', str(pid))
    if not m:
        return ''
    vid, sid, ep = m.groups()
    sids = FQ_LINE_SID.get(vid) or {}
    other = ''
    for name in ('蓝光2K', '至臻4K'):
        if sids.get(name) and sids[name] != sid:
            other = sids[name]
            break
    return '/play/%s-%s-%s.html' % (vid, other, ep) if other else ''


def fq_detail_data(vid):
    """详情页：只保留「至臻4K」「蓝光2K」两条线路。"""
    url = fq_abs(vid)
    txt = fq_get(url, timeout=12)
    if not txt or '系统安全验证' in txt:
        return {}
    names = []
    for s in FQ_RE_SLIDE.findall(txt):
        s = re.sub(r'<i[^>]*>.*?</i>', '', s, flags=re.S)
        s = re.sub(r'<span[^>]*>.*?</span>', '', s, flags=re.S)
        s = re.sub(r'<[^>]+>', '', s)
        names.append(fq_clean(s.replace('&nbsp;', ' ')))
    # 按 anthology-list-box 切块，每块对应一条线路
    segs = re.split(r'<div class="anthology-list-box', txt)[1:]
    panels = []
    for seg in segs:
        eps = [(fq_clean(n), h) for h, n in FQ_RE_EP.findall(seg)
               if '/play/' in h]
        panels.append(list(reversed(eps))[:300])   # 页面是 40→1，翻成正序

    lines = []
    for i, nm in enumerate(names):
        key = nm.lower().replace(' ', '')
        for raw_name, disp in FQ_LINES:
            if key == raw_name.lower() and i < len(panels) and panels[i]:
                lines.append((disp, panels[i]))
                break
    order = [d for _, d in FQ_LINES]
    lines.sort(key=lambda x: order.index(x[0]) if x[0] in order else 99)
    if not lines:
        return {}

    # 记下两条线路各自的播放页 sid，解析站失效时可同集回落
    num = re.search(r'/(\d+)\.html', str(vid))
    if num:
        FQ_LINE_SID[num.group(1)] = dict(
            (n, fq_sid_of(eps)) for n, eps in lines)

    title = re.search(r'class="slide-info-title[^"]*"[^>]*>([^<]+)<', txt)
    pic_m = re.search(r'class="detail-pic"[\s\S]{0,600}?<img[^>]*?data-src="([^"]+)"',
                      txt)
    intro = re.search(r'id="height_limit"[^>]*>([\s\S]{0,1200}?)</div>', txt)
    actor = ''
    for info in re.findall(r'class="slide-info"[^>]*>([\s\S]{0,400}?)</div>', txt):
        if '演员' in info:
            actor = fq_clean(re.sub(r'<[^>]+>', ' ', info))
            break

    def strip_tags(s):
        return fq_clean(re.sub(r'<[^>]+>', ' ', s or ''))

    vod = {
        'vod_id': vid,
        'vod_name': fq_clean(title.group(1)) if title else '',
        'vod_pic': html.unescape(pic_m.group(1)) if pic_m else '',
        'vod_content': strip_tags(intro.group(1)) if intro else '',
        'vod_actor': actor,
        'vod_remarks': lines[0][0] + ' / ' + lines[-1][0],
        'vod_play_from': '$$$'.join(n for n, _ in lines),
        'vod_play_url': '$$$'.join(
            '#'.join('%s$%s' % (n, h) for n, h in eps) for _, eps in lines),
    }
    return vod


def fq_parse_play(play_key):
    """JD-xxx / co_xxx → 解析站的 m3u8 直链。"""
    key = re.split(r'[-_]', play_key)[0] if play_key else ''
    base = FQ_PARSE.get(key)
    if not base:
        return ''
    target = base + '/player/?url=' + play_key
    # 这个接口强制要求来源站 Referer，否则会被导到百度页面
    txt = fq_get(target, referer=FQ_SITE + '/', timeout=12)
    tok = FQ_RE_TOKEN.search(txt)
    if not tok:
        return ''
    body = urllib.parse.urlencode(
        {'url': play_key, 'token': tok.group(1)}).encode()
    res = fq_get(base + '/player/mplayer.php', data=body, referer=target,
                 ctype='application/x-www-form-urlencoded; charset=UTF-8',
                 timeout=12, retry=False)
    try:
        u = str((json.loads(res) or {}).get('url') or '')
    except Exception:
        return ''
    if not u:
        return ''
    return (base + u) if u.startswith('/playproxy.php') else u


def fq_player_data(pid, fallback=True):
    url = fq_abs(pid)
    txt = fq_get(url, timeout=12)
    if not txt:
        return {'parse': 0, 'jx': 0, 'url': ''}
    m = FQ_RE_PLAYER.search(txt)
    u = m.group(1).replace('\\/', '/') if m else ''
    if not u:
        m2 = FQ_RE_URL_VAR.search(txt)
        u = m2.group(1) if m2 else ''
    if not u:
        u = url
    header = 'User-Agent: %s\r\nReferer: %s/' % (FQ_UA, FQ_SITE)
    if u.startswith('http') and ('m3u' in u or '.mp4' in u):
        return {'parse': 0, 'jx': 0, 'url': u, 'header': header}
    real = fq_parse_play(u) or u
    if not real.startswith('http') and fallback:
        alt = fq_fallback_url(pid)
        if alt and alt != str(pid):
            alt_res = fq_player_data(alt, fallback=False)
            if str(alt_res.get('url') or '').startswith('http'):
                alt_res['fq_note'] = '原线路解析站不可用，已回落另一条线路同集'
                return alt_res
    return {'parse': 0 if ('m3u' in real or '.mp4' in real) else 1,
            'jx': 0, 'url': real, 'header': header}


class FengqiSpider(_FQBase):
    """枫奇4K（至臻4K / 蓝光2K）——可作为独立源，也可挂进 Kishuto。"""

    def getName(self):
        return '枫奇4K'

    def init(self, extend=''):
        # 性能铁律：init 不联网，验证码只在首个真实请求被拦截时触发。
        try:
            if isinstance(extend, str) and extend.strip().startswith('{'):
                cfg = json.loads(extend)
                if isinstance(cfg, dict) and cfg.get('fq_site'):
                    FQ_HDRS['Referer'] = str(cfg['fq_site']).rstrip('/') + '/'
        except Exception:
            pass
        return None

    def destroy(self):
        return None

    def homeContent(self, filter=False):
        classes = [
            {'type_id': '1', 'type_name': '电影'},
            {'type_id': '2', 'type_name': '电视剧'},
            {'type_id': '3', 'type_name': '综艺'},
            {'type_id': '4', 'type_name': '动漫'},
            {'type_id': '5', 'type_name': '短剧'},
        ]
        return {'parse': 0, 'jx': 0, 'class': classes, 'filters': {}}

    def homeVideoContent(self):
        return self.categoryContent('', 1, False, {})

    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        page = int(pg) if str(pg).isdigit() else 1
        t = str(tid or '')
        if t.startswith('/label/'):
            url = FQ_SITE + t + '/page/%d.html' % page
        elif t and t.isdigit():
            url = '%s/cupfox-list/%s----------%d---.html' % (FQ_SITE, t, page)
        else:
            url = FQ_SITE + '/'
        txt = fq_get(url, timeout=12)
        items = fq_parse_list(txt) if txt else []
        return {'parse': 0, 'jx': 0, 'list': items, 'page': page,
                'pagecount': fq_page_count(txt) if txt else 1,
                'limit': 30, 'total': len(items)}

    def searchContent(self, key, quick=False, pg='1'):
        if int(pg) >= 2:
            return {'parse': 0, 'jx': 0, 'list': [], 'pagecount': 1}
        kw = str(key or '').strip()
        if not kw:
            return {'parse': 0, 'jx': 0, 'list': []}
        ck = 'fq:s:' + kw
        hit = FQ_CACHE.get(ck)
        if hit and time.time() - hit[0] < 300:
            return hit[1]
        url = (FQ_SITE + '/cupfox-search/-------------.html?wd='
               + urllib.parse.quote(kw))
        txt = fq_get(url, timeout=10)
        items = fq_parse_list(txt) if txt else []
        res = {'parse': 0, 'jx': 0, 'list': items, 'pagecount': 1}
        FQ_CACHE[ck] = (time.time(), res)
        return res

    def detailContent(self, ids):
        vid = str(ids[0] if isinstance(ids, (list, tuple)) and ids else ids)
        vod = fq_detail_data(vid)
        return {'parse': 0, 'jx': 0, 'list': [vod] if vod else []}

    def playerContent(self, flag, id, vipFlags=None):
        return fq_player_data(str(id))

# ==================== 枫奇4K 线路源 fq END ====================

# ==================== 橘汁线路源 jn BEGIN ====================
# 2026-11-20：改用实测可用的 gdsaj.hzhcbkj.cn（橘汁视频独立源协议）
# 旧 juziapp 新网关 DNS 失效；本实现登录+zone+proto/v5，纯标准库。

class JZNewSpider(_BaseSpider):
    NAME = '橘汁'
    HOST = 'https://gdsaj.hzhcbkj.cn'
    UA = 'okhttp/3.12.1'
    PKG = 'com.exxammpea.a1'
    VC = '3026'
    PUB1_B64 = (
        'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCr8SzZhjYy+rsya1K09t8d2K50'
        'pWFoBkgUqMpKOiW+3IEVKd4eTdvg9RSOjQ82kypL6R9BnsmrS1V8s4PVDwjQbUtY'
        'hTPPC9Hz16qY7rpD6m0d2vr09/UpWQ5uOy9PR0QTrsioveZ+DIe9jc3C+zBCu/kZ'
        'SY/R8stwJoiitki3gwIDAQAB')
    NATIVE_K = b'ed5fdsgucxumegqa'
    SAFE = b'OC1A06E197EF10CF3F6058CA7A803B5E'
    PW_SAFE = b'11GK2we32144LO&hilUITB)FMd1khdaF'
    CERT_MD5 = '6457E81AF1F6D3BC229E33ED60F248A5'
    CERT_SHA1 = '8350E6AAEC7A4D8A174377892B4364CFA2066B85'
    MEDIA_RE = re.compile(
        r'(?i).*\.(mp4|m3u8|flv|mkv|avi|ts|mov|mpd|m4a|wmv)(\?.*)?$')
    # 2026-11 实测：这几族 playUrl 只是「播放令牌」，videoUsableUrl 会把令牌
    # 原样回给你（PAN1-xxx 这类），真正解链在橘汁 App 的私有播放器里，
    # TVBox 拿不到直链 —— 留着只会让用户点了黑屏，直接不输出该线路。
    TOKEN_ONLY = ('PAN0-', 'PAN1-', 'PAN2-', 'PAN3-')
    # 2026-11 实测死线：tocyyds 只回空、zy1080 回的 CDN 恒定 403
    # （okhttp / PC / ExoPlayer、带不带 Referer 5 种组合全拒），点了必黑屏；
    # pylg 只回一个外部 vid，壳没有对应解析器，等于空线。
    DEAD_PLAY_FROM = ('tocyyds', 'zy1080', 'zy4k', 'zy720', 'pylg')
    # 网页平台线：没有直链，但可以交给壳的解析接口（parse=1），保留
    WEB_ONLY = frozenset(('qq', 'qy', 'qiyi', 'youku', 'mgtv', 'bilibili', 'bl',
                          'sohu', 'le', 'pptv'))
    WEB_RE = re.compile(r'(?i)^https?://[^/]*(v\.qq\.com|iqiyi\.com|youku\.com'
                        r'|mgtv\.com|bilibili\.com|sohu\.com|le\.com|pptv\.com)')

    @staticmethod
    def _enc_url(u):
        """中文/空格路径必须编码：橘汁有「.../video/kuangbiao/第01集/index.m3u8」
        这类目录，原样丢给播放器会直接 UnicodeEncodeError / 404。"""
        s = str(u or '')
        if not s or s.isascii():
            return s
        return urllib.parse.quote(s, safe="/:?&=#%@!$'()*+,;[]~-._")

    @classmethod
    def _line_dead(cls, src, pth):
        s = str(src or '').strip().lower()
        p = str(pth or '')
        if any(s.startswith(x) for x in cls.DEAD_PLAY_FROM):
            return True
        return any(p.startswith(t) for t in cls.TOKEN_ONLY)

    def __init__(self):
        # 首页预热 / 详情 / 播放会并发进 _ensure，没锁会重复握手把站点惹毛
        self._lk = threading.RLock()
        self.udid = ''
        self._token = ''
        self._rsa1 = None
        self._rsa2 = None
        self._ready = False
        self._tried = False
        self._last_try = 0
        self._safecode = ''

    # 设备号固定下来：这站按 udid 建账号，每次 init 换新号就得先 register
    # 再 login（多一个往返，实测 1.8s vs 0.9s），详情预算根本等不起。
    _UDID_FILE = os.path.join(tempfile.gettempdir(), 'kish_jz_udid.txt')
    _UDID_MEM = ['']

    @classmethod
    def _device_id(cls):
        if cls._UDID_MEM[0]:
            return cls._UDID_MEM[0]
        try:
            with open(cls._UDID_FILE) as fp:
                u = fp.read().strip()
            if len(u) >= 8:
                cls._UDID_MEM[0] = u
                return u
        except Exception:
            pass
        u = hashlib.md5(str(time.time()).encode()).hexdigest()[:16].upper()
        try:
            with open(cls._UDID_FILE, 'w') as fp:
                fp.write(u)
        except Exception:
            pass
        cls._UDID_MEM[0] = u
        return u

    def getName(self):
        return self.NAME

    def init(self, extend=''):
        try:
            self.udid = self._device_id()
            self._rsa1 = self._rsa_pub(self.PUB1_B64)
            self._token = ''
            self._rsa2 = None
            self._ready = False
            self._tried = False
            self._last_try = 0
            self._safecode = self._build_safecode()
        except Exception:
            self.udid = '0000000000000000'
            self._ready = False

    def destroy(self):
        self._ready = False

    def isVideoFormat(self, url):
        return bool(self.MEDIA_RE.search(str(url or '')))

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return None

    # ---- crypto ----
    @staticmethod
    def _pad(data, block=16):
        n = block - (len(data) % block)
        return data + bytes([n]) * n

    @staticmethod
    def _unpad(data, block=16):
        if not data:
            return data
        n = data[-1]
        if 0 < n <= block and len(data) >= n:
            return data[:-n]
        return data

    # 与「橘汁视频.py」一致的纯 Python AES-ECB（聚合内 _enc_block 布局不同，勿混用）
    _JZ_SBOX = None

    @classmethod
    def _jz_sbox(cls):
        if cls._JZ_SBOX is not None:
            return cls._JZ_SBOX
        alog = [0] * 256
        log = [0] * 256
        x = 1
        for i in range(255):
            alog[i] = x
            log[x] = i
            h = ((x << 1) ^ (0x1B if (x & 0x80) else 0)) & 0xFF
            x = h ^ x
        sbox = [0] * 256
        for i in range(256):
            s = 0 if i == 0 else alog[(255 - log[i]) % 255]
            r = s
            for _ in range(4):
                s = ((s << 1) | (s >> 7)) & 0xFF
                r ^= s
            sbox[i] = r ^ 0x63
        cls._JZ_SBOX = sbox
        return sbox

    @staticmethod
    def _jz_xtime(a):
        return ((a << 1) ^ 0x1B) & 0xFF if (a & 0x80) else (a << 1) & 0xFF

    @classmethod
    def _jz_mul(cls, a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            a = cls._jz_xtime(a)
            b >>= 1
        return r

    def _jz_expand(self, key):
        sbox = self._jz_sbox()
        nk = len(key) // 4
        nr = nk + 6
        w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
        rcon = 1
        for i in range(nk, 4 * (nr + 1)):
            t = list(w[i - 1])
            if i % nk == 0:
                t = t[1:] + t[:1]
                t = [sbox[b] for b in t]
                t[0] ^= rcon
                rcon = self._jz_xtime(rcon)
            elif nk > 6 and i % nk == 4:
                t = [sbox[b] for b in t]
            w.append([w[i - nk][j] ^ t[j] for j in range(4)])
        return w, nr

    def _jz_enc_block(self, block, w, nr):
        sbox = self._jz_sbox()
        state = list(block)
        for c in range(4):
            for r in range(4):
                state[r + 4 * c] ^= w[4 * 0 + c][r]
        for rnd in range(1, nr):
            for i in range(16):
                state[i] = sbox[state[i]]
            for r in range(1, 4):
                row = [state[r + 4 * c] for c in range(4)]
                for c in range(4):
                    state[r + 4 * c] = row[(c + r) % 4]
            for c in range(4):
                a = [state[r + 4 * c] for r in range(4)]
                state[0 + 4 * c] = self._jz_mul(a[0], 2) ^ self._jz_mul(a[1], 3) ^ a[2] ^ a[3]
                state[1 + 4 * c] = a[0] ^ self._jz_mul(a[1], 2) ^ self._jz_mul(a[2], 3) ^ a[3]
                state[2 + 4 * c] = a[0] ^ a[1] ^ self._jz_mul(a[2], 2) ^ self._jz_mul(a[3], 3)
                state[3 + 4 * c] = self._jz_mul(a[0], 3) ^ a[1] ^ a[2] ^ self._jz_mul(a[3], 2)
            for c in range(4):
                for r in range(4):
                    state[r + 4 * c] ^= w[4 * rnd + c][r]
        for i in range(16):
            state[i] = sbox[state[i]]
        for r in range(1, 4):
            row = [state[r + 4 * c] for c in range(4)]
            for c in range(4):
                state[r + 4 * c] = row[(c + r) % 4]
        for c in range(4):
            for r in range(4):
                state[r + 4 * c] ^= w[4 * nr + c][r]
        return bytes(state)

    def _aes_ecb_enc(self, data, key):
        key_b = key if isinstance(key, (bytes, bytearray)) else str(key).encode()
        if len(key_b) not in (16, 24, 32):
            key_b = (key_b[:16] if len(key_b) >= 16 else key_b.ljust(16, b'\0'))
        data = self._pad(data)
        w, nr = self._jz_expand(key_b)
        out = bytearray()
        for i in range(0, len(data), 16):
            out += self._jz_enc_block(data[i:i + 16], w, nr)
        return bytes(out)

    def _aes_ecb_dec(self, data, key):
        # 列表/播放路径当前只需加密；解密保留占位
        return data

    def _build_safecode(self):
        try:
            raw = (self.CERT_MD5 + '######' + self.CERT_SHA1 + '~~~~~~'
                   + self.PKG + '>>>+++' + self.VC).encode()
            e = base64.b64encode(self._aes_ecb_enc(raw, self.PW_SAFE)).decode()
            e2 = base64.b64encode(e.encode()).decode()
            return (e2[:16] + e2[-16:]).upper()
        except Exception:
            return ''

    @staticmethod
    def _der_read(buf, i):
        tag = buf[i]
        i += 1
        ln = buf[i]
        i += 1
        if ln & 0x80:
            n = ln & 0x7F
            ln = int.from_bytes(buf[i:i + n], 'big')
            i += n
        return tag, buf[i:i + ln], i + ln

    def _rsa_pub(self, der_b64):
        der = base64.b64decode(der_b64)
        tag, seq, _ = self._der_read(der, 0)
        i = 0
        t1, first, i = self._der_read(seq, i)
        t2, second, _ = self._der_read(seq, i)
        if t2 == 0x03:
            _, rs, _ = self._der_read(second[1:], 0)
        else:
            rs = second
        j = 0
        _, nb, j = self._der_read(rs, j)
        _, eb, _ = self._der_read(rs, j)
        n = int.from_bytes(nb, 'big')
        e = int.from_bytes(eb, 'big')
        return (n, e)

    def _rsa_enc(self, msg, key):
        n, e = key
        k = (n.bit_length() + 7) // 8
        if len(msg) > k - 11:
            return b''
        ps = bytearray()
        while len(ps) < k - len(msg) - 3:
            b = os.urandom(1)
            if b != b'\x00':
                ps += b
        em = b'\x00\x02' + bytes(ps) + b'\x00' + msg
        c = pow(int.from_bytes(em, 'big'), e, n)
        return c.to_bytes(k, 'big')

    @staticmethod
    def _varint(n):
        b = b''
        while True:
            x = n & 0x7f
            n >>= 7
            if n:
                b += bytes([x | 0x80])
            else:
                return b + bytes([x])

    def _f(self, num, wire, payload):
        t = self._varint((num << 3) | wire)
        if wire == 2:
            return t + self._varint(len(payload)) + payload
        return t + payload

    @staticmethod
    def _pb(buf):
        out = []
        i = 0
        n = len(buf or b'')
        while i < n:
            tag = 0
            sh = 0
            while i < n:
                x = buf[i]
                i += 1
                tag |= (x & 0x7f) << sh
                sh += 7
                if not x & 0x80:
                    break
            fn, wt = tag >> 3, tag & 7
            if fn == 0:
                break
            if wt == 0:
                v = 0
                sh = 0
                while i < n:
                    x = buf[i]
                    i += 1
                    v |= (x & 0x7f) << sh
                    sh += 7
                    if not x & 0x80:
                        break
                out.append((fn, wt, v))
            elif wt == 2:
                ln = 0
                sh = 0
                while i < n:
                    x = buf[i]
                    i += 1
                    ln |= (x & 0x7f) << sh
                    sh += 7
                    if not x & 0x80:
                        break
                out.append((fn, wt, buf[i:i + ln]))
                i += ln
            elif wt == 5:
                out.append((fn, wt, buf[i:i + 4]))
                i += 4
            elif wt == 1:
                out.append((fn, wt, buf[i:i + 8]))
                i += 8
            else:
                i += 1
        return out

    @staticmethod
    def _rnd(k):
        CH = string.ascii_letters + string.digits
        return ''.join(random.sample(list(CH), min(k - 1, len(CH)))) + '='

    def _http(self, url, data=None, headers=None, timeout=20, retries=1):
        st, body = http(url, 'POST' if data is not None else 'GET',
                        headers or {}, data, timeout=timeout, retries=2)
        if st and body is not None:
            return body
        # fallback
        try:
            import ssl as _ssl
            req = urllib.request.Request(url, data=data, headers=headers or {})
            with urllib.request.urlopen(
                    req, timeout=timeout,
                    context=_ssl._create_unverified_context()) as r:
                return r.read()
        except Exception:
            return b''

    def _ensure(self):
        if self._ready:
            return True
        with self._lk:
            if self._ready:
                return True
            now = time.time()
            # 抑制窗口 60s → 6s：首页预热是并发握手，偶发一次失败就把整整
            # 一分钟的详情/播放全锁死，表现成「橘汁时有时无、点了没反应」。
            if self._tried and now - self._last_try < 6:
                return False
            self._tried = True
            self._last_try = now
            if not self._safecode:
                self._safecode = self._build_safecode()
            # 不能并发打 login + zone：实测同一 udid 同时发两个请求，
            # zone 会被拒（三次全失败、白花 1.9s），串行 1.7s 反而一次过。
            for _ in range(3):
                if self._rsa2 is not None:
                    self._ready = True
                    break
                if not self._token:
                    self._quiet(self._login)
                if self._rsa2 is None:
                    self._quiet(self._zone)
                if self._rsa2 is not None:
                    self._ready = True
                    break
                time.sleep(0.4)
            return bool(self._ready)

    @staticmethod
    def _quiet(fn):
        try:
            fn()
        except Exception:
            pass

    def _login(self):
        body = json.dumps({
            'username': 'tv_%s' % self.udid[:10].lower(),
            'password': hashlib.md5(('tv' + self.udid).encode()).hexdigest(),
            'udid': self.udid,
        }).encode()
        hdr = {'User-Agent': self.UA, 'Content-Type': 'application/json'}
        # 先直接登录：账号是本机 udid 生成的，绝大多数时候已存在，
        # 先 register 必定回 500「用户名或密码错误」还白跑一个往返（实测 +0.5s）。
        d = self._http(self.HOST + '/api/ex/v3/user/login', body, hdr)
        tok = self._pick_token(d)
        if not tok:
            try:
                self._http(self.HOST + '/api/ex/v3/user/register', body, hdr)
            except Exception:
                pass
            d = self._http(self.HOST + '/api/ex/v3/user/login', body, hdr)
            tok = self._pick_token(d)
        self._token = tok

    @staticmethod
    def _pick_token(d):
        try:
            data = json.loads((d or b'').decode('utf-8', 'ignore')).get('data') or {}
            return (data.get('token')
                    or (data.get('user') or {}).get('token') or '')
        except Exception:
            return ''

    def _zone(self):
        ts = int(time.time() * 1000)
        rnd = self._rnd(16)
        sign = base64.b64encode(
            self._rsa_enc((str(ts) + rnd).encode(), self._rsa1)).decode()
        body = (self._f(1, 0, self._varint(ts))
                + self._f(2, 2, sign.encode())
                + self._f(3, 2, rnd.encode())
                + self._f(4, 2, rnd.encode())
                + self._f(5, 2, rnd.encode()))
        P = {
            'plat': 'tv', 'vOs': '16', '_vOsCode': '36', 'vApp': self.VC,
            'vName': '3.0.2.6', 'pkg': self.PKG,
            'appName': '%E6%A9%98%E6%B1%81',
            'udid': self.udid, 'uuid': self.udid, 'chid': '10000',
            'androidID': self.udid, 'net': '1', 'young': 0, 'tenantId': '*',
            'v': 1, 'device': 0, 'lang': 'zh', 'country': 'CN', 'cpu': 'arm64-v8a',
        }
        d = self._http(self.HOST + '/api/v5/find/app/zone', body, {
            'User-Agent': self.UA, 'Content-Type': 'application/x-protobuf',
            'Accept': 'application/x-protobuf', 'Cache-Control': 'no-cache',
            'publicParams': json.dumps(P, separators=(',', ':'))})
        top = self._pb(d)
        inner = [v for fn, wt, v in top if fn == 3 and wt == 2]
        if not inner:
            raise ValueError('no secondary key')
        strs = {fn: v for fn, wt, v in self._pb(inner[0]) if wt == 2}
        self._rsa2 = self._rsa_pub(
            (strs[1] + strs[2] + strs[4] + strs[5]).decode())

    def _hdr(self):
        ts = int(time.time() * 1000)
        rnd = self._rnd(16)
        sig = base64.b64encode(
            self._rsa_enc((str(ts) + rnd + self.VC).encode(), self._rsa2)).decode()
        ao = base64.b64encode(self._aes_ecb_enc(
            (str(ts) + rnd).encode(), self.SAFE)).decode()
        J = {
            'country': 'CN', 'vName': '3.0.2.6', 'cpuId': '', 'young': 0,
            'facturer': 'OnePlus', 'pkg': self.PKG, 'uuid': self.udid,
            'resolution': '1080x2256', 'mac': '02%3A00%3A00%3A00%3A00',
            'sig': sig, 'abid': '7470', 'model': 'PJX110', 'plat': 'tv',
            'udid': self.udid, 'dpi': '480', 'net': '1', 'lang': 'zh',
            'random_str': rnd, 'brand': 'OnePlus', 'timestamp': ts,
            'density': '3.0', 'appName': '%E6%A9%98%E6%B1%81',
            'cpu': 'arm64-v8a', 'chid': '10000', 'carrier': '%E8%81%94%E9%80%9A',
            'sig2': ao[:8], 'v': 1, 'sig3': ao[8:], 'tenantId': '*',
            '_vOsCode': '36', 'vOs': '16', 'vApp': self.VC, 'device': 0,
            'androidID': self.udid,
        }
        h = {
            'User-Agent': self.UA, 'Accept': 'application/json',
            'Cache-Control': 'no-cache',
            'publicParams': json.dumps(J, separators=(',', ':'), ensure_ascii=False),
        }
        if self._token:
            h['token'] = self._token
        return h

    def _secure_map(self, param):
        ts = int(time.time() * 1000)
        rnd = self._rnd(16)
        plain = (param + str(ts)).encode()
        ct = self._aes_ecb_enc(plain, self._safecode.encode())
        b64 = base64.b64encode(ct).decode()
        return (self._f(1, 2, (rnd + b64[:4]).encode())
                + self._f(2, 2, b64[4:].encode())
                + self._f(3, 2, self._rnd(20).encode())
                + self._f(4, 0, self._varint(ts))
                + self._f(5, 2, rnd.encode()))

    def _list(self, qs):
        out = []
        if not self._ensure():
            return out
        hh = self._hdr()
        hh['Content-Type'] = 'application/x-protobuf'
        hh['Accept'] = 'application/x-protobuf'
        d = self._http(self.HOST + '/api/proto/v5/drama/category',
                       self._secure_map(qs), hh)
        top = self._pb(d)
        code = [v for fn, wt, v in top if fn == 1 and wt == 0]
        if (code[0] if code else 0) != 200:
            return out
        data = [v for fn, wt, v in top if fn == 3 and wt == 2]
        if not data:
            return out
        for fn, wt, v in self._pb(data[0]):
            if fn != 1 or wt != 2:
                continue
            info = {'vod_id': '', 'vod_name': '', 'vod_pic': '', 'vod_remarks': ''}
            for f2, w2, v2 in self._pb(v):
                if f2 == 3 and w2 == 0:
                    info['vod_id'] = str(v2)
                elif f2 == 5 and w2 == 2:
                    info['vod_name'] = v2.decode('utf-8', 'replace')
                elif f2 == 2 and w2 == 2:
                    cands = [v3.decode('utf-8', 'replace')
                             for f3, w3, v3 in self._pb(v2)
                             if w3 == 2 and v3.startswith(b'http')]
                    if cands:
                        info['vod_pic'] = next(
                            (u for u in cands if u.startswith('https')), cands[0])
                elif f2 == 13 and w2 == 2:
                    info['vod_remarks'] = v2.decode('utf-8', 'replace')
            if info['vod_id']:
                out.append(info)
        return out

    def homeContent(self, filter=False):
        cats = []
        try:
            d = self._http(self.HOST + '/api/v3/drama/getCategory?orderBy=type_id',
                           None, {'User-Agent': self.UA, 'Accept': 'application/json'})
            for c in (json.loads(d.decode('utf-8', 'ignore')).get('data') or []):
                if str(c.get('id')) != '29':
                    cats.append({'type_id': str(c['id']),
                                 'type_name': c.get('name', '')})
        except Exception:
            pass
        if not cats:
            cats = [
                {'type_id': '21', 'type_name': '电影'},
                {'type_id': '22', 'type_name': '剧集'},
                {'type_id': '25', 'type_name': '动漫'},
                {'type_id': '26', 'type_name': '综艺'},
                {'type_id': '27', 'type_name': '短剧'},
                {'type_id': '28', 'type_name': '漫剧'},
            ]
        return {'class': cats, 'filters': {}}

    def homeVideoContent(self):
        try:
            return {'list': self._list('page=1&pagesize=24')}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter=False, extend=None):
        try:
            pg = int(pg or 1)
        except Exception:
            pg = 1
        try:
            qs = 'page=%d&pagesize=24&typeId1=%s' % (pg, tid)
            return {'list': self._list(qs), 'page': pg,
                    'pagecount': 999, 'limit': 24, 'total': 99999}
        except Exception:
            return {'list': [], 'page': 1, 'pagecount': 1, 'limit': 24, 'total': 0}

    def searchContent(self, key, quick=False, pg='1'):
        try:
            pg = int(pg or 1)
        except Exception:
            pg = 1
        try:
            if not self._ensure():
                return {'list': [], 'page': pg}
            hh = self._hdr()
            hh['Content-Type'] = 'application/x-protobuf'
            hh['Accept'] = 'application/x-protobuf'
            qs = 'page=%s&pagesize=24&searchKeys=%s' % (pg, key)
            d = self._http(self.HOST + '/api/proto/v5/drama/search',
                           self._secure_map(qs), hh)
            top = self._pb(d)
            code = [v for fn, wt, v in top if fn == 1 and wt == 0]
            if (code[0] if code else 0) != 200:
                return {'list': [], 'page': pg}
            datas = [v for fn, wt, v in top if fn == 3 and wt == 2]
            if not datas:
                return {'list': [], 'page': pg}
            out = []
            for fn, wt, v in self._pb(datas[0]):
                if wt != 2 or fn == 0 or fn > 100:
                    continue
                item = {'vod_id': '', 'vod_name': '', 'vod_pic': '', 'vod_remarks': ''}
                for f3, w3, v3 in self._pb(v):
                    try:
                        if f3 == 3 and w3 == 0:
                            item['vod_id'] = str(v3)
                        elif f3 == 5 and w3 == 2:
                            item['vod_name'] = v3.decode('utf-8', 'replace')
                        elif f3 == 2 and w3 == 2:
                            cands = [x.decode('utf-8', 'replace')
                                     for _, w4, x in self._pb(v3)
                                     if w4 == 2 and x.startswith(b'http')]
                            if cands:
                                item['vod_pic'] = next(
                                    (u for u in cands if u.startswith('https')), cands[0])
                        elif f3 == 13 and w3 == 2:
                            item['vod_remarks'] = v3.decode('utf-8', 'replace')
                    except Exception:
                        pass
                if item['vod_id'] and item['vod_name']:
                    out.append(item)
            return {'list': out, 'page': pg}
        except Exception:
            return {'list': [], 'page': 1}

    def detailContent(self, ids):
        try:
            ids = list(ids or [])
            if not ids:
                return {'list': []}
        except Exception:
            return {'list': []}
        out = {'vod_id': ids[0]}
        try:
            if not self._ensure():
                return {'list': []}
            hh = self._hdr()
            hh['Content-Type'] = 'application/x-protobuf'
            hh['Accept'] = 'application/x-protobuf'
            d = self._http(self.HOST + '/api/proto/v5/drama/getDetail',
                           self._secure_map('id=' + str(ids[0])), hh)
            top = self._pb(d)
            code = [v for fn, wt, v in top if fn == 1 and wt == 0]
            if (code[0] if code else 0) != 200:
                return {'list': []}
            data = [v for fn, wt, v in top if fn == 3 and wt == 2]
            if not data:
                return {'list': []}
            dd = self._pb(data[0])
            eps = []
            for fn, wt, v in dd:
                if wt == 2 and fn == 29:
                    ep = {}
                    for f3, w3, v3 in self._pb(v):
                        if w3 == 2:
                            ep[f3] = v3.decode('utf-8', 'replace')
                    if ep.get(4):
                        eps.append(ep)
                    continue
                if wt != 2:
                    if fn == 18 and 'vod_year' not in out:
                        out['vod_year'] = str(v)
                    continue
                if fn == 9 and 'vod_name' not in out:
                    out['vod_name'] = v.decode('utf-8', 'replace')
                elif fn == 1 and 'vod_area' not in out:
                    out['vod_area'] = v.decode('utf-8', 'replace')
                elif fn == 2 and 'vod_pic' not in out:
                    cands = []
                    for f3, w3, v3 in self._pb(v):
                        if w3 == 2:
                            t = v3.decode('utf-8', 'replace')
                            if t.startswith('http'):
                                cands.append(t)
                    if cands:
                        out['vod_pic'] = next(
                            (u for u in cands if u.startswith('https')), cands[0])
                elif fn == 6 and 'vod_content' not in out:
                    out['vod_content'] = re.sub(
                        r'<[^>]+>', '', v.decode('utf-8', 'replace'))
                elif fn == 12 and 'vod_director' not in out:
                    out['vod_director'] = v.decode('utf-8', 'replace')
                elif fn == 25 and 'vod_actor' not in out:
                    out['vod_actor'] = v.decode('utf-8', 'replace')
                elif fn == 26 and 'vod_remarks' not in out:
                    out['vod_remarks'] = v.decode('utf-8', 'replace')
            lines, order = {}, []
            # 令牌线/网页线先摘掉；万一整部片只剩这类线，再原样保留（有总比没有）
            alive = [x for x in eps
                     if not self._line_dead(x.get(9), x.get(4))]
            for ep in (alive or eps):
                title = ep.get(2) or ep.get(3) or ''
                pth = ep.get(4) or ''
                src = ep.get(9) or ''
                src_cn = ep.get(10) or ''
                line = src_cn or src or '正片'
                if line not in lines:
                    lines[line] = []
                    order.append(line)
                if self.MEDIA_RE.match(pth):
                    ep_url = self._enc_url(pth)
                else:
                    ep_url = base64.b64encode(json.dumps(
                        {'vodPlayFrom': src, 'playUrl': pth},
                        separators=(',', ':')).encode()).decode()
                mm = re.match(r'^第?0*(\d{1,4})[集话期](?:完结)?$', title)
                if mm:
                    title = mm.group(1)
                lines[line].append('%s$%s' % (title or '正片', ep_url))

            def _line_rank(nm):
                if nm.startswith('自建4K'):
                    return (0, nm)
                if nm == 'JD4K' or 'JD4K' in nm:
                    return (1, nm)
                if 'VIP4K' in nm or '4K' in nm.upper():
                    return (2, nm)
                return (3, 0 if '超高清' in nm else 1 if '蓝光' in nm else 2, nm)

            order.sort(key=_line_rank)
            if lines:
                out['vod_play_from'] = '$$$'.join(order)
                out['vod_play_url'] = '$$$'.join('#'.join(lines[nm]) for nm in order)
            out.setdefault('vod_name', '')
            out.setdefault('vod_pic', '')
            return {'list': [out]}
        except Exception:
            return {'list': [out] if out.get('vod_name') else []}

    def playerContent(self, flag, id, vipFlags=None):
        url = id or ''
        hdr = {'User-Agent': self.UA}
        page = ''            # 网页类线路的原始页面（拿不到直链时走解析）
        try:
            if id and not str(id).startswith('http'):
                try:
                    jm = json.loads(base64.b64decode(id).decode('utf-8', 'ignore'))
                except Exception:
                    jm = {}
                pf = str(jm.get('vodPlayFrom') or '')
                pu = str(jm.get('playUrl') or '')
                if pu.startswith('http') and (self.WEB_RE.match(pu)
                                              or pf.strip().lower() in self.WEB_ONLY):
                    page = pu
                url = ''
                if pf or pu:
                    if not self._ensure():
                        raise ValueError('not ready')
                    hh = self._hdr()
                    hh['Content-Type'] = 'application/x-protobuf'
                    hh['Accept'] = 'application/x-protobuf'
                    qs = 'vodPlayFrom=%s&playUrl=%s' % (
                        urllib.parse.quote(pf), urllib.parse.quote(pu, safe=''))
                    d = self._http(self.HOST + '/api/proto/v5/videoUsableUrl',
                                   self._secure_map(qs), hh)
                    top = self._pb(d)
                    code = [v for fn, wt, v in top if fn == 1 and wt == 0]
                    if (code[0] if code else 0) == 200:
                        data = [v for fn, wt, v in top if fn == 3 and wt == 2]
                        if data:
                            # 只认 data 里第一个「可播媒体」地址。
                            # 早先的兜底正则会把封面图（byteimg 那种）当直链，
                            # 壳于是去拉一张 jpg，必黑屏。
                            for fn, wt, v in self._pb(data[0]):
                                if fn != 1 or wt != 2:
                                    continue
                                t = v.decode('utf-8', 'replace').strip()
                                if t.startswith('http') and self.MEDIA_RE.match(
                                        t.split('?')[0]):
                                    url = t
                                    break
        except Exception:
            url = ''
        if not url:
            # 拿不到媒体直链：网页线交给壳去解析，其余返回空让上层换源，
            # 绝不把 base64 令牌/封面图当 url 丢出去。
            if page:
                return {'parse': 1, 'playUrl': '', 'url': page, 'header': hdr}
            return {'parse': 0, 'playUrl': '', 'url': '', 'header': hdr}
        return {'parse': 0, 'playUrl': '', 'url': self._enc_url(url),
                'header': hdr}

# 兼容旧引用名
JZNewRaw = JZNewSpider
# ==================== 橘汁线路源 jn END ====================


# ==================== 四源4K专线线路源 sk BEGIN ====================
# -*- coding: utf-8 -*-
# ============================================================================
# 四源 4K 专线 · 天堂 / 布布 / 华谊 / 苹果  (TVBox / AVBox / drpy 通用)
# ============================================================================
# 数据来源：https://9877.kstore.space/sun.json 解密后的 sites 配置
#   - 天堂 • APP  (csp_AppDrama)  pkg com.dytiantang.one
#   - 布布 • APP  (csp_YunDuo)    host 323433ssdfd.top
#   - 华谊 • APP  (csp_AppDrama)  pkg com.lxf.sncgtzxyx
#   - 苹果 • APP  (csp_AppDrama)  pkg com.juechufsh.android.xpg1
#
# 本文件做的事：把四个 APP 源各自实现一遍，并且**详情页只保留 4K 线路**
# （线路名含 4K 的才显示；若该片一条 4K 都没有，则原样保留全部线路）。
#
# 实测（2026-11-08）：
#   天堂：超级无敌4K / 高清4K / 高清蓝光4K / 4k专线2️⃣   → 全部可解直链
#   华谊：蓝光4K                                        → 可解直链
#   苹果：超级无敌4K / 高清4K / 高清蓝光4K / 4k专线2️⃣   → 全部可解直链
#   布布：CO4K                                          → 服务端返回
#         PLATFORM_NOT_ALLOWED（该线路只对 APP 客户端开放，Web 通道锁死），
#         代码里保留该线路并做了「自动回退到同片 1080P 线路」的兜底。
#
# 补充（用 ffprobe 逐条探过分辨率）：
#   天堂「超级无敌4K」1280x538、「高清4K」1716x720、「独家4K」1920x806
#   也就是说这些“4K”只是线路名，没有一条是真 4K（3840x2160）。
#   布布聚合源里「站外-极速」反而是 1920x1080，是全站画质最高的一条。
#
# 用法：一个 py 文件，配 4 个 site，ext 里用 src 指定源。
#   api 填 py 文件本身（本地文件名或 http 地址都行），ext 是传给 init() 的
#   参数，两者互不影响：
#   {"key":"天堂4K","name":"天堂 • 4K","type":3,
#    "api":"http://你的地址/四源4K专线.py","ext":"{\"src\":\"天堂\"}"}
#   同理 {"src":"布布"} / {"src":"华谊"} / {"src":"苹果"}
#   不传 ext 时默认“天堂”。
#
# 可选 ext 字段（覆盖内置配置）：
#   {"src":"华谊","host":"http://x.x.x.x:18004","only4k":false}
#
# 依赖：零第三方库。有 pycryptodome 时用 C 实现，没有则走内置纯 Python
#       AES / RSA（首页推荐需要 AES 解密，已一并实现）。
# ============================================================================


import collections
try:
    from base.spider import Spider as _Base
except Exception:
    class _Base:
        pass

# ---------------------------------------------------------------- 加密层
# AVBox 1.3.0 的 pip 只带 lxml/requests/pyquery，没有 pycryptodome。
# 原文件在模块顶层 `from Crypto...` 直接把整个源卡在导入阶段。
# 现在：能用 Crypto 就用（行为与原来完全一致），没有就用内置纯 Python 实现。
try:
    from Crypto.PublicKey import RSA as _CryptoRSA
    from Crypto.Cipher import PKCS1_v1_5 as _CryptoPKCS1
    from Crypto.Cipher import AES as _CryptoAES
    sk4__HAVE_CRYPTO = True
except Exception:
    sk4__HAVE_CRYPTO = False


def sk4__pad(data, block=16):
    """PKCS#7 填充（与 Crypto.Util.Padding.pad 一致）"""
    n = block - (len(data) % block)
    return data + bytes([n]) * n


def sk4__unpad(data, block=16):
    n = data[-1]
    if 0 < n <= block and len(data) >= n:
        return data[:-n]
    return data


def sk4__gf_tables():
    alog = [0] * 256
    log = [0] * 256
    x = 1
    for i in range(255):
        alog[i] = x
        log[x] = i
        h = ((x << 1) ^ (0x1B if (x & 0x80) else 0)) & 0xFF
        x = h ^ x
    return alog, log


def sk4__mk_sbox():
    alog, log = sk4__gf_tables()
    sbox = [0] * 256
    for i in range(256):
        if i == 0:
            s = 0
        else:
            s = alog[(255 - log[i]) % 255]
        r = s
        for _ in range(4):
            s = ((s << 1) | (s >> 7)) & 0xFF
            r ^= s
        sbox[i] = r ^ 0x63
    return sbox


sk4__SBOX = sk4__mk_sbox()


def sk4__xtime(a):
    return ((a << 1) ^ 0x1B) & 0xFF if (a & 0x80) else (a << 1) & 0xFF


def sk4__mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = sk4__xtime(a)
        b >>= 1
    return r


def sk4__key_expansion(key):
    nk = len(key) // 4
    nr = nk + 6
    w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
    rcon = 1
    for i in range(nk, 4 * (nr + 1)):
        t = list(w[i - 1])
        if i % nk == 0:
            t = t[1:] + t[:1]
            t = [sk4__SBOX[b] for b in t]
            t[0] ^= rcon
            rcon = sk4__xtime(rcon)
        elif nk > 6 and i % nk == 4:
            t = [sk4__SBOX[b] for b in t]
        w.append([w[i - nk][j] ^ t[j] for j in range(4)])
    return w, nr


def sk4__add_round_key(state, w, rnd):
    for c in range(4):
        kw = w[4 * rnd + c]
        for r in range(4):
            state[r + 4 * c] ^= kw[r]


def sk4__sub_bytes(state):
    for i in range(16):
        state[i] = sk4__SBOX[state[i]]


def sk4__shift_rows(state):
    # AES 行移位：第 r 行循环左移 r 位（state 为列主序 flat 索引 r + 4c）
    for r in range(1, 4):
        row = [state[r + 4 * c] for c in range(4)]
        for c in range(4):
            state[r + 4 * c] = row[(c + r) % 4]


def sk4__mix_columns(state):
    for c in range(4):
        a = [state[r + 4 * c] for r in range(4)]
        state[0 + 4 * c] = sk4__mul(a[0], 2) ^ sk4__mul(a[1], 3) ^ a[2] ^ a[3]
        state[1 + 4 * c] = a[0] ^ sk4__mul(a[1], 2) ^ sk4__mul(a[2], 3) ^ a[3]
        state[2 + 4 * c] = a[0] ^ a[1] ^ sk4__mul(a[2], 2) ^ sk4__mul(a[3], 3)
        state[3 + 4 * c] = sk4__mul(a[0], 3) ^ a[1] ^ a[2] ^ sk4__mul(a[3], 2)


def sk4__aes_encrypt_block(block, w, nr):
    state = list(block)
    sk4__add_round_key(state, w, 0)
    for rnd in range(1, nr):
        sk4__sub_bytes(state)
        sk4__shift_rows(state)
        sk4__mix_columns(state)
        sk4__add_round_key(state, w, rnd)
    sk4__sub_bytes(state)
    sk4__shift_rows(state)
    sk4__add_round_key(state, w, nr)
    return bytes(state)


class sk4__PureAES:
    MODE_ECB = 1
    MODE_CBC = 2

    @classmethod
    def new(cls, key, mode, iv=None):
        return cls(key, mode, iv)

    def __init__(self, key, mode, iv=None):
        if len(key) not in (16, 24, 32):
            raise ValueError('invalid AES key size')
        self.key = bytes(key)
        self.mode = mode
        self.iv = bytes(iv) if iv else b'\x00' * 16
        self._w, self._nr = sk4__key_expansion(self.key)

    def encrypt(self, data):
        out = bytearray()
        prev = self.iv
        for i in range(0, len(data), 16):
            blk = data[i:i + 16]
            if self.mode == sk4__PureAES.MODE_CBC:
                blk = bytes(a ^ b for a, b in zip(blk, prev))
            enc = sk4__aes_encrypt_block(blk, self._w, self._nr)
            out += enc
            prev = enc
        return bytes(out)


def sk4__der_read(buf, i):
    tag = buf[i]
    i += 1
    ln = buf[i]
    i += 1
    if ln & 0x80:
        n = ln & 0x7F
        ln = int.from_bytes(buf[i:i + n], 'big')
        i += n
    return tag, buf[i:i + ln], i + ln


def sk4__rsa_pub_from_der(der):
    """解析 DER：支持 SubjectPublicKeyInfo 与裸 RSAPublicKey"""
    tag, seq, _ = sk4__der_read(der, 0)
    if tag != 0x30:
        raise ValueError('bad rsa key')
    i = 0
    t1, first, i = sk4__der_read(seq, i)
    if i >= len(seq):
        raise ValueError('bad rsa key')
    t2, second, _ = sk4__der_read(seq, i)
    if t2 == 0x03:
        inner = second[1:]
        _, rs, _ = sk4__der_read(inner, 0)
    elif t2 == 0x30:
        rs = second
    else:
        raise ValueError('bad rsa key')
    j = 0
    _, nb, j = sk4__der_read(rs, j)
    _, eb, _ = sk4__der_read(rs, j)
    return int.from_bytes(nb, 'big'), int.from_bytes(eb, 'big')


class sk4__PurePKCS1:
    def __init__(self, key):
        self.n, self.e = key

    def encrypt(self, msg):
        k = (self.n.bit_length() + 7) // 8
        if len(msg) > k - 11:
            raise ValueError('data too long for RSA')
        ps = bytearray()
        while len(ps) < k - len(msg) - 3:
            b = os.urandom(1)
            if b != b'\x00':
                ps += b
        em = b'\x00\x02' + bytes(ps) + b'\x00' + msg
        c = pow(int.from_bytes(em, 'big'), self.e, self.n)
        return c.to_bytes(k, 'big')


if sk4__HAVE_CRYPTO:
    sk4_AES = _CryptoAES
    sk4_PKCS1_v1_5 = _CryptoPKCS1

    def sk4__rsa_public(der_b64):
        return _CryptoPKCS1.new(_CryptoRSA.import_key(base64.b64decode(der_b64)))
else:
    sk4_AES = sk4__PureAES
    sk4_PKCS1_v1_5 = sk4__PurePKCS1

    def sk4__rsa_public(der_b64):
        return sk4__PurePKCS1(sk4__rsa_pub_from_der(base64.b64decode(der_b64)))

# ---------------------------------------------------------------- AES 解密补充
# 内置的纯 Python AES 只有 encrypt；首页推荐数据(tag/list)是双层 AES-ECB
# 加密，这里补上逆变换，保证无 pycryptodome 的环境也能出首页。
sk4__INV_SBOX = [0] * 256
for _i, _v in enumerate(sk4__SBOX):
    sk4__INV_SBOX[_v] = _i


def sk4__inv_sub_bytes(state):
    for i in range(16):
        state[i] = sk4__INV_SBOX[state[i]]


def sk4__inv_shift_rows(state):
    for r in range(1, 4):
        row = [state[r + 4 * c] for c in range(4)]
        for c in range(4):
            state[r + 4 * c] = row[(c - r) % 4]


def sk4__inv_mix_columns(state):
    for c in range(4):
        a = [state[r + 4 * c] for r in range(4)]
        state[0 + 4 * c] = sk4__mul(a[0], 14) ^ sk4__mul(a[1], 11) ^ sk4__mul(a[2], 13) ^ sk4__mul(a[3], 9)
        state[1 + 4 * c] = sk4__mul(a[0], 9) ^ sk4__mul(a[1], 14) ^ sk4__mul(a[2], 11) ^ sk4__mul(a[3], 13)
        state[2 + 4 * c] = sk4__mul(a[0], 13) ^ sk4__mul(a[1], 9) ^ sk4__mul(a[2], 14) ^ sk4__mul(a[3], 11)
        state[3 + 4 * c] = sk4__mul(a[0], 11) ^ sk4__mul(a[1], 13) ^ sk4__mul(a[2], 9) ^ sk4__mul(a[3], 14)


def sk4__aes_decrypt_block(block, w, nr):
    state = list(block)
    sk4__add_round_key(state, w, nr)
    for rnd in range(nr - 1, 0, -1):
        sk4__inv_shift_rows(state)
        sk4__inv_sub_bytes(state)
        sk4__add_round_key(state, w, rnd)
        sk4__inv_mix_columns(state)
    sk4__inv_shift_rows(state)
    sk4__inv_sub_bytes(state)
    sk4__add_round_key(state, w, 0)
    return bytes(state)


def sk4__pureaes_decrypt(self, data):
    out = bytearray()
    prev = self.iv
    for i in range(0, len(data), 16):
        blk = data[i:i + 16]
        dec = sk4__aes_decrypt_block(blk, self._w, self._nr)
        if self.mode == sk4__PureAES.MODE_CBC:
            dec = bytes(a ^ b for a, b in zip(dec, prev))
            prev = blk
        out += dec
    return bytes(out)


sk4__PureAES.decrypt = sk4__pureaes_decrypt


# ---------------------------------------------------------------- 新协议常量
sk4_UA = 'okhttp/3.12.1'
sk4_NATIVE_K = 'ed5fdsgucxumegqa'   # publicParams 的 AES-CBC key / iv

sk4_PUB_DEFAULT = ('MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCr8SzZhjYy+rsya1K09t8d2K50pWFoBkgUqMpKOiW'
               '+3IEVKd4eTdvg9RSOjQ82kypL6R9BnsmrS1V8s4PVDwjQbUtYhTPPC9Hz16qY7rpD6m0d2vr09/UpW'
               'Q5uOy9PR0QTrsioveZ+DIe9jc3C+zBCu/kZSY/R8stwJoiitki3gwIDAQAB')

sk4_VIDEO_RE = re.compile(r'(?i)\.(mp4|m3u8|flv|mkv|avi|ts|mov|mpd|m4a|wmv)(\?.*)?$')


def sk4__key_bytes(k):
    return k.encode() if isinstance(k, str) else k


def sk4__ecb_enc(s, key):
    return base64.b64encode(
        sk4_AES.new(sk4__key_bytes(key), sk4_AES.MODE_ECB).encrypt(sk4__pad(s.encode(), 16))).decode()


def sk4__ecb_dec(s, key):
    ct = base64.b64decode(s)
    if sk4__HAVE_CRYPTO:
        plain = sk4_AES.new(sk4__key_bytes(key), sk4_AES.MODE_ECB).decrypt(ct)
    else:
        plain = sk4__PureAES(sk4__key_bytes(key), sk4__PureAES.MODE_ECB).decrypt(ct)
    return sk4__unpad(plain).decode('utf-8', 'replace')


def sk4__cbc_enc(s, key, iv=None):
    iv = sk4__key_bytes(iv or key)
    return sk4_AES.new(sk4__key_bytes(key), sk4_AES.MODE_CBC, iv).encrypt(
        sk4__pad(s.encode(), 16)).hex()


def sk4__rsa_sign(data, pub):
    return base64.b64encode(sk4__rsa_public(pub).encrypt(data.encode())).decode()


def sk4__pb_data(raw):
    """取 ApiResult.data (field 3)"""
    for fn, wt, v in sk4__pb(raw):
        if fn == 3 and wt == 2:
            return v
    return b''


def sk4__pb_code(raw):
    for fn, wt, v in sk4__pb(raw):
        if fn == 1 and wt == 0:
            return v
    return -1

# ---------------------------------------------------------------- protobuf 工具
def sk4__varint(n):
    b = b''
    while True:
        x = n & 0x7f
        n >>= 7
        if n:
            b += bytes([x | 0x80])
        else:
            return b + bytes([x])


def sk4__f(num, wire, payload):
    t = sk4__varint((num << 3) | wire)
    if wire == 2:
        return t + sk4__varint(len(payload)) + payload
    return t + payload


def sk4__pb(buf):
    # 正确的 protobuf 解析：字段号 > 15 时 tag 是多字节 varint，
    # 只读一个字节会造成整体错位（老版本源文件就是因此只能按原始字节扫描）
    out = []
    i = 0
    n = len(buf)
    while i < n:
        tag = 0
        sh = 0
        while i < n:
            x = buf[i]; i += 1
            tag |= (x & 0x7f) << sh; sh += 7
            if not x & 0x80:
                break
        fn, wt = tag >> 3, tag & 7
        if fn == 0:
            break
        if wt == 0:
            v = 0; sh = 0
            while i < n:
                x = buf[i]; i += 1
                v |= (x & 0x7f) << sh; sh += 7
                if not x & 0x80:
                    break
            out.append((fn, wt, v))
        elif wt == 2:
            ln = 0; sh = 0
            while i < n:
                x = buf[i]; i += 1
                ln |= (x & 0x7f) << sh; sh += 7
                if not x & 0x80:
                    break
            out.append((fn, wt, buf[i:i + ln])); i += ln
        elif wt == 5:
            out.append((fn, wt, buf[i:i + 4])); i += 4
        elif wt == 1:
            out.append((fn, wt, buf[i:i + 8])); i += 8
        else:
            i += 1
    return out


def sk4__rnd(k):
    CH = string.ascii_letters + string.digits
    return ''.join(random.sample(list(CH), k - 1)) + '='

# ---------------------------------------------------------------- 内置分类兜底
# 新网关不提供 /api/v3/drama/getCategory（返回 400 No static resource），
# 与官方插件一致：接口拿不到时使用内置分类表。
sk4_CATEGORIES = [{'id': 20, 'name': '电影', 'converUrl': '{"class":"喜剧,爱情,恐怖,动作,科幻,剧情,战争,警匪,犯罪,动画,奇幻,武侠,冒险,枪战,恐怖,悬疑,惊悚,经典,青春,文艺,微电影,古装,历史,运动,农村,儿童,网络电影","area":"大陆,香港,台湾,美国,法国,英国,日本,韩国,德国,泰国,印度,意大利,西班牙,加拿大,其他","lang":"国语,英语,粤语,闽南语,韩语,日语,法语,德语,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 2, 'typePid': 0}, {'id': 21, 'name': '剧集', 'converUrl': '{"class":"古装,战争,青春,偶像,喜剧,家庭,犯罪,动作,奇幻,剧情,历史,经典,乡村,情景,商战,网剧,其他","area":"内地,韩国,香港,台湾,日本,美国,泰国,英国,新加坡,其他","lang":"国语,英语,粤语,闽南语,韩语,日语,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010,2009,2008,2007,2006,2005,2004,2003,2002,2001,2000","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 1, 'typePid': 0}, {'id': 22, 'name': '综艺', 'converUrl': '{"class":"选秀,情感,访谈,播报,旅游,音乐,美食,纪实,曲艺,生活,游戏互动,财经,求职","area":"内地,港台,日韩,欧美","lang":"国语,英语,粤语,闽南语,韩语,日语,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012,2011,2010","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 3, 'typePid': 0}, {'id': 23, 'name': '动漫', 'converUrl': '{"year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 6, 'typePid': 0}, {'id': 24, 'name': '短剧', 'converUrl': '{"class":"重生民国,穿越年代,现代言情,反转爽文,女恋总裁,闪婚离婚,都市脑洞,古装仙侠,其它","year":"2026,2025,2024,2023,2022,2021,2020,2019,2018,2017,2016","extend_sort":"最新,最热,好评"}', 'typeMid': 1, 'typeSort': 4, 'typePid': 0}, {'id': 26, 'name': '漫剧', 'converUrl': '{}', 'typeMid': 1, 'typeSort': 5, 'typePid': 0}]



# ============================================================ 源定义
# 公钥说明：sun.json 里「天堂 / 苹果」的 publicKey 字段已过期（用它调
# zone 会返回 100002 RSA 校验失败），实测两家现在都改用与华谊相同的那把
# 公钥，这里统一填可用值。
sk4_PUB_KEY = ('MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCr8SzZhjYy+rsya1K09t8d2K50pWFoBkgUqMpKOiW'
           '+3IEVKd4eTdvg9RSOjQ82kypL6R9BnsmrS1V8s4PVDwjQbUtYhTPPC9Hz16qY7rpD6m0d2vr09/UpW'
           'Q5uOy9PR0QTrsioveZ+DIe9jc3C+zBCu/kZSY/R8stwJoiitki3gwIDAQAB')

sk4_DATA_IV = 'OC1A06E197EF10CF3F6058CA7A803B5E'

sk4_APP_SOURCES = {
    '天堂': {
        'host': 'http://122.228.193.211:18004',
        'site': 'https://dyttandroid04-1372779881.cos.ap-shanghai.myqcloud.com/app_dyttandroid.txt',
        'publicKey': sk4_PUB_KEY,
        'dataKey': 'D2KREWRIBVNAUJJYEDL4VFHOY2Q0PQ==',
        'dataIv': sk4_DATA_IV,
        'pkg': 'com.dytiantang.one',
        'appName': '电影天堂',
        'version': '3.0.0.7',
        'decrypt': '0',
    },
    '华谊': {
        'host': 'http://43.240.158.154:18004',
        'site': 'https://1851089669.cdn.123clouddisk.com/1851089669/44107727',
        'publicKey': sk4_PUB_KEY,
        'dataKey': 'V04XQZNYRWN6T0JODZFIAG5CTZB3PT0=',
        'dataIv': sk4_DATA_IV,
        'pkg': 'com.lxf.sncgtzxyx',
        'appName': '华谊',
        'version': '6.0.0.1',
        'decrypt': '0',
    },
    '苹果': {
        'host': 'http://122.228.193.211:18004',
        'site': 'https://xpgandroid03-1372779881.cos.ap-beijing.myqcloud.com/app_xpg_android.txt',
        'publicKey': sk4_PUB_KEY,
        'dataKey': 'S0VNDTJHOFHHCNMRAW5IV2TOS2PBPQ==',
        'dataIv': sk4_DATA_IV,
        'pkg': 'com.juechufsh.android.xpg1',
        'appName': '小苹果',
        'version': '1.0.0.3',
        'decrypt': '0',
    },
    '河豚': {
        'host': 'https://az1-1456692500.cos.ap-guangzhou.myqcloud.com/az1.txt',
        'site': 'https://az1-1456692500.cos.ap-guangzhou.myqcloud.com/az1.txt',
        'publicKey': sk4_PUB_KEY,
        'dataKey': 'V04XQZNYRWN6T0JODZFIAG5CTZB3PT0=',
        'dataIv': sk4_DATA_IV,
        'pkg': 'com.djlxxl.xcydzkj',
        'appName': '河豚',
        'version': '7.0.0.2',
        'decrypt': '0',
    },
}

sk4_BUBU_DEFAULT = {
    'host': 'https://323433ssdfd.top',
    'aid': 'com.web.player',
    'x_client': '8f3d2a1c7b6e5d4c9a0b1f2e3d4c5b6a',
    'web_sign': 'ddtvf65f3a83d6d9ad6f',
    'finger': 'WF-2c064bc5b3400788f31b848849bc3a60f835423ba2dfe69d7ea93974c216e4f2',
    'sk': 'WEB-50a8e9c84a1dc05669a692ded99a2dac46527229e607a7be15db88dbc59059d1',
}

sk4_SRC_ALIAS = {'步步': '布布', '电影天堂': '天堂', '小苹果': '苹果'}
sk4_SRC_ORDER = ('天堂', '布布', '华谊', '苹果', '河豚')


def sk4__is4k(name):
    return '4K' in (name or '').upper()


# 四源4K 线路名与实测画质（2026-11-21 ffprobe 逐条验，繁花/狂飙/三体 三片）：
#   天堂·超级无敌4k   1280x720      ← 名字里的 4K 只是营销词（三片都 720）
#   天堂·高清4k       1280x720
#   天堂·真蓝光4K     1920x1080
#   布布·PAN1 / BBA   1920x1080     （与「华谊·蓝光4K」「苹果·真蓝光4K」同一路流）
#   苹果复用天堂那三条流；三体的「华谊·Z蓝光」1280x546、「B超高清」1920x818
# 全源没有一条 3840x2160。分档按**宽度**判（1920x806 这类宽银幕裁切仍算 1080）。
# 注意：同一线路名在不同片/不同集会有 720/1080 波动（PAN1 两次实测就分别读到
# 1920x1080 与 1280x720），所以展示名只标「非4K」，不写死精确高度。
sk4_MEASURED = (
    ('超级无敌', (1280, 720)),
    ('高清4k', (1280, 720)),
    ('高清蓝光', (1920, 1080)),
    ('真蓝光', (1920, 1080)),
    ('蓝光4k', (1920, 1080)),
    ('独家', (1920, 806)),
    ('pan1', (1920, 1080)),
    ('bba', (1920, 1080)),
    ('zijianm3u8', (1920, 1080)),
    ('nby', (1920, 1080)),
    ('qsvip', (1920, 1080)),
    ('co4k', (1920, 1080)),
    ('自建4k', (1920, 1080)),
)
# 外部解析中转（不是四源自己的流）：NBY / qsvip 两片实测 ffprobe 都打不开，
# HLS 地址还要二次换票，留着只会占掉聚合侧同源折叠的那一个名额。
sk4_DEAD_NAMES = ('nby', 'qsvip')


def sk4_measure(name):
    """四源4K 线路的实测 (宽, 高)；None = 没实测过（非本源线路，别乱认）。"""
    nm = str(name or '')
    if '四源4K' in nm:
        body = nm.split('四源4K', 1)[1].lstrip('·')
    elif nm.startswith(('天堂·', '布布·', '华谊·', '苹果·')):
        body = nm
    else:
        return None
    for p in ('天堂·', '布布·', '华谊·', '苹果·'):
        if body.startswith(p):
            body = body[len(p):]
    low = body.lower()
    for k, wh in sk4_MEASURED:
        if k in low:
            return wh
    return None


def sk4_qname(name):
    """给带 4K 字样的四源线路名标一句「非4K」（实测最高 1920x1080）。

    不写精确高度：同一线路名在不同片/集会在 720/1080 之间波动，写死反而会
    造出「标着 1080P 实际 720」的新一批假标签。名字本来不带 4K 的（PAN1 /
    zijianm3u8 / Z蓝光…）原样保留。
    """
    wh = sk4_measure(name)
    nm = str(name or '').strip()
    if not wh or wh[0] >= 3800:
        return nm
    nm = re.sub(r'\[实测[^\]]*\]$', '', nm)     # 兼容旧版缓存里的 [实测1080P]
    if not re.search(r'4k|2160|uhd', nm, re.I) or nm.endswith('[非4K]'):
        return nm
    return '%s[非4K]' % nm


def sk4_hd_only(name):
    """宽度不到 1280 的「4K」线直接不要：本源定位是 4K 专线，
    实测 1280 宽的「超级无敌4k / 高清4k」既不是 4K 也没到 1080，点开就是降级。"""
    wh = sk4_measure(name)
    return bool(wh) and wh[0] < 1900


def sk4_dead_line(name):
    """外部解析中转线（NBY / qsvip）实测两片都打不开，不放进线路表。"""
    wh = sk4_measure(name)
    if not wh:
        return False
    low = str(name or '').lower()
    return any(k in low for k in sk4_DEAD_NAMES)


# ============================================================ 引擎 A：AppDrama 系
class sk4__AppEngine(object):
    """天堂 / 华谊 / 苹果 —— 同一套 AppDrama 协议（protobuf + AES + RSA）"""

    ONLY_4K = True
    TIMEOUT = 15
    CACHE_LIMIT = 128
    sk4_UA = sk4_UA

    def __init__(self, cfg):
        self.cfg = dict(cfg)
        self.host = (self.cfg.get('host') or '').rstrip('/')
        self.udid = uuid.uuid4().hex.upper()
        self.sec = ''
        self._ready = False
        self._site_done = False
        self._cats = None
        self._detail_cache = {}
        self._home_cache = None
        self._lock = threading.Lock()

    def setup(self, ext):
        if not isinstance(ext, dict):
            return
        for k in ('host', 'site', 'publicKey', 'dataKey', 'dataIv', 'pkg',
                  'appName', 'version', 'decrypt'):
            v = ext.get(k)
            if v not in (None, ''):
                self.cfg[k] = str(v)
        if ext.get('host'):
            self.host = self.cfg['host'].rstrip('/')
            self._site_done = True
        if str(ext.get('only4k', '')).lower() in ('1', 'true', 'yes'):
            self.ONLY_4K = True
        self._ready = False
        self.sec = ''

    # -------------------------------------------------- 网络
    def _http(self, url, data=None, headers=None, timeout=None):
        req = urllib.request.Request(url, data=data, headers=headers or {})
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout or self.TIMEOUT,
                                    context=ctx) as r:
            return r.read()

    def _get(self, path, headers, timeout=None):
        try:
            return self._http(self.host + path, None, headers, timeout)
        except Exception:
            return b''

    def _ensure(self):
        if self._ready:
            return True
        with self._lock:
            if self._ready:
                return True
            if not self._site_done:
                self._site_done = True
                site = self.cfg.get('site', '')
                if site:
                    try:
                        raw = self._http(site, None, {'User-Agent': self.sk4_UA}, 8)
                        domain = (json.loads(raw.decode('utf-8', 'ignore'))
                                  or {}).get('domain', '')
                        if domain.startswith('http'):
                            self.host = domain.rstrip('/')
                    except Exception:
                        pass
            sec = self._zone()
            if sec:
                self.sec = sec
                self._ready = True
        return self._ready

    def _zone(self):
        ts = int(time.time() * 1000)
        r = sk4__rnd(16)
        sign = sk4__rsa_sign(str(ts) + r, self.cfg['publicKey'])
        body = (sk4__f(1, 0, sk4__varint(ts)) + sk4__f(2, 2, sign.encode()) +
                sk4__f(3, 2, r.encode()) + sk4__f(4, 2, r.encode()) +
                sk4__f(5, 2, sk4__rnd(16).encode()))
        try:
            raw = self._http(self.host + '/api/v5/find/app/zone', body,
                             self._c_head(self.cfg['publicKey']))
        except Exception:
            return ''
        data = sk4__pb_data(raw)
        if not data:
            return ''
        strs = {fn: v.decode('utf-8', 'replace') for fn, wt, v in sk4__pb(data)
                if wt == 2}
        # 分片位置有两种版本：新版 f1 是公钥开头，老版 f2 才是开头。
        for order in ((1, 3, 4, 5), (2, 3, 4, 5)):
            key = ''.join(strs.get(k, '') for k in order)
            if key.startswith('MIGf') and len(key) % 4 == 0 and len(key) > 100:
                return key
        return ''

    def _d_obj(self):
        return {"country": "CN", "vName": self.cfg['version'],
                "cpuId": "MT6893Z%2FCZA", "young": 0, "facturer": "OnePlus",
                "pkg": self.cfg['pkg'], "uuid": self.udid,
                "resolution": "1080x2272", "mac": "02%3A00%3A00%3A00%3A00%3A00",
                "abid": "397", "model": "PJX110", "plat": "android",
                "udid": self.udid, "dpi": "440", "net": "1", "lang": "zh",
                "brand": "OnePlus", "density": "2.75",
                "appName": self.cfg['appName'], "cpu": "arm64-v8a",
                "chid": "10000", "carrier": "%E8%81%94%E9%80%9A",
                "_vOsCode": "36", "vOs": "16", "v": 1, "tenantId": "",
                "vApp": self.cfg['version'].replace('.', ''),
                "device": 0, "androidID": self.udid}

    def _c_head(self, sec):
        d = self._d_obj()
        ts = int(time.time() * 1000)
        f = sk4__rnd(16)
        d['sig'] = sk4__rsa_sign(str(ts) + f + d['vApp'], sec)
        b = sk4__ecb_enc(str(ts) + f, self.cfg['dataIv'])
        d.update({'random_str': f, 'timestamp': ts, 'sig2': b[:8], 'sig3': b[8:]})
        p = sk4__cbc_enc(json.dumps(d, separators=(',', ':'), ensure_ascii=False),
                     sk4_NATIVE_K)
        return {'User-Agent': self.sk4_UA, 'Accept': 'application/x-protobuf',
                'Content-Type': 'application/x-protobuf',
                'Cache-Control': 'no-cache',
                'publicParams': json.dumps({'paramsData': p},
                                           separators=(',', ':'))}

    def _e_head(self):
        p = sk4__cbc_enc(json.dumps(self._d_obj(), separators=(',', ':'),
                                ensure_ascii=False), sk4_NATIVE_K)
        return {'User-Agent': self.sk4_UA, 'Accept': 'application/json',
                'Content-Type': 'application/json; charset=utf-8',
                'publicParams': json.dumps({'paramsData': p},
                                           separators=(',', ':'))}

    def _g_body(self, mp):
        ts = int(time.time() * 1000)
        f8, f20 = sk4__rnd(8), sk4__rnd(20)
        sb = '&'.join('%s=%s' % (k, v) for k, v in mp.items()
                      if v not in (None, ''))
        s3 = f8 + sk4__ecb_enc(sb + str(ts), self.cfg['dataKey'])
        return (sk4__f(1, 2, s3[:20].encode()) + sk4__f(2, 2, s3[20:].encode()) +
                sk4__f(3, 2, f20.encode()) + sk4__f(4, 0, sk4__varint(ts)) +
                sk4__f(5, 2, f8.encode()))

    def _post(self, path, mp):
        if not self._ensure():
            return b''
        for attempt in (0, 1):
            try:
                raw = self._http(self.host + path, self._g_body(mp),
                                 self._c_head(self.sec or self.cfg['publicKey']))
            except Exception:
                return b''
            code = sk4__pb_code(raw)
            if code == 200:
                return sk4__pb_data(raw)
            if code in (100001, 100002, 100003) and attempt == 0:
                self._ready, self.sec = False, ''
                if not self._ensure():
                    return b''
                continue
            return b''
        return b''

    # -------------------------------------------------- 解析
    @staticmethod
    def _pic(cov):
        if not cov:
            return ''
        m = re.search(r'https?://[^\x00-\x20"\\]+', cov)
        return m.group(0) if m else ''

    @classmethod
    def _parse_list(cls, data):
        out = []
        if not data:
            return out
        for fn, wt, v in sk4__pb(data):
            if fn != 1 or wt != 2 or not isinstance(v, bytes) or len(v) < 8:
                continue
            d = {}
            for f2, w2, x in sk4__pb(v):
                if w2 == 2 and isinstance(x, bytes):
                    d[f2] = x.decode('utf-8', 'replace')
                elif w2 == 0:
                    d[f2] = x
            if not isinstance(d.get(3), int) or not d.get(5):
                continue
            out.append({'vod_id': str(d[3]), 'vod_name': d.get(5, ''),
                        'vod_pic': cls._pic(d.get(2, '')),
                        'vod_remarks': d.get(13, '') or ''})
        return out

    def _cache_put(self, cache, key, value):
        try:
            _cap_put(cache, key, value, self.CACHE_LIMIT)
        except Exception:
            pass

    # -------------------------------------------------- 首页 / 分类
    def _categories(self):
        if self._cats:
            return self._cats
        raw = self._get('/api/v3/drama/getCategory?orderBy=type_id',
                        self._e_head())
        try:
            d = (json.loads(raw.decode('utf-8', 'ignore')) or {}).get('data')
            if isinstance(d, list) and d:
                self._cats = d
                return d
        except Exception:
            pass
        self._cats = sk4_CATEGORIES
        return self._cats

    def homeContent(self, filter):
        try:
            cats = self._categories()
            # 直播 / CCTV / 卫视 这些是直播源，点播详情拉不出片单，直接隐藏
            bad = ('直播', 'CCTV', '卫视', '广播', '听书', 'FM', '音乐', '4K专区')
            classes = [{'type_id': str(c['id']), 'type_name': c['name']}
                       for c in cats
                       if c.get('name') and c.get('name') != '公告'
                       and not any(b in c['name'] for b in bad)]
            labels = [('class', '类型'), ('area', '地区'), ('lang', '语言'),
                      ('year', '年份'), ('extend_sort', '排序')]
            filters = {}
            for c in cats:
                try:
                    cv = json.loads(c.get('converUrl') or '{}')
                except Exception:
                    cv = {}
                fl = []
                for k, label in labels:
                    v = cv.get(k)
                    if v:
                        fl.append({'key': k, 'name': label,
                                   'value': [{'n': x, 'v': x}
                                             for x in v.split(',') if x]})
                if fl:
                    filters[str(c['id'])] = fl
            return {'class': classes, 'filters': filters}
        except Exception:
            return {'class': [], 'filters': {}}

    def homeVideoContent(self):
        if self._home_cache and time.time() - self._home_cache[0] < 60:
            return {'list': self._home_cache[1]}
        try:
            raw = self._get('/api/ex/v3/security/tag/list', self._e_head())
            j = json.loads(raw.decode('utf-8', 'ignore'))
            ds = j.get('data') or []
            # decrypt=1 的源两次 ECB 解密后才是 JSON；decrypt=0 直接给数组
            if isinstance(ds, str):
                if self.cfg.get('decrypt', '1') != '0' and ds:
                    ds = sk4__ecb_dec(ds, self.cfg['dataKey'])
                    ds = sk4__ecb_dec(ds, self.cfg['dataIv'])
                arr = json.loads(ds) if ds else []
            else:
                arr = ds if isinstance(ds, list) else []
            seen, out = set(), []
            for block in arr:
                for sec in (block.get('sections') or []):
                    for v in (sec.get('vodList') or []):
                        vid = str(v.get('id', ''))
                        if not vid or vid in seen:
                            continue
                        seen.add(vid)
                        out.append({'vod_id': vid,
                                    'vod_name': v.get('name', ''),
                                    'vod_pic': (v.get('coverImage') or {}).get('path', '') or '',
                                    'vod_remarks': v.get('remark', '') or ''})
            self._home_cache = (time.time(), out)
            return {'list': out}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            mp = {'pagesize': '21', 'typeId1': str(tid), 'page': str(pg or 1),
                  'vodOrderBy': '最新'}
            ext = extend if isinstance(extend, dict) else {}
            for k, dst in (('extend_sort', 'vodOrderBy'), ('area', 'vodArea'),
                           ('lang', 'vodLang'), ('class', 'vodClass'),
                           ('year', 'vodYear')):
                if ext.get(k):
                    mp[dst] = str(ext[k])
            lst = self._parse_list(
                self._post('/api/proto/v5/drama/category', mp))
            page = int(pg or 1)
            return {'list': lst, 'page': page,
                    'pagecount': page + 1 if len(lst) >= 21 else page,
                    'limit': 21, 'total': len(lst)}
        except Exception:
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        try:
            data = self._post('/api/proto/v5/drama/search',
                              {'searchKeys': str(key), 'page': str(pg or 1),
                               'pagesize': '21'})
            return {'list': self._parse_list(data)}
        except Exception:
            return {'list': []}

    # -------------------------------------------------- 详情
    def detailContent(self, ids):
        try:
            raw = ids[0] if isinstance(ids, (list, tuple)) and ids else str(ids)
            vid = str(raw).strip().strip('/')
            if vid in self._detail_cache:
                return {'list': [self._detail_cache[vid]]}
            data = self._post('/api/proto/v5/drama/getDetail', {'id': vid})
            if not data:
                return {'list': []}
            dd = sk4__pb(data)
            meta = {}
            for fn, wt, v in dd:
                if wt == 2 and isinstance(v, bytes):
                    meta[fn] = v.decode('utf-8', 'replace')
                elif wt == 0:
                    meta[fn] = v

            lines = collections.OrderedDict()
            for fn, wt, v in dd:
                if fn != 29 or wt != 2:
                    continue
                e = {}
                for f2, w2, x in sk4__pb(v):
                    if w2 == 2 and isinstance(x, bytes):
                        e[f2] = x.decode('utf-8', 'replace')
                    elif w2 == 0:
                        e[f2] = x
                cn = e.get(10) or e.get(9) or 'APP'
                src, path = e.get(9, ''), e.get(4, '')
                title = e.get(3) or e.get(2) or '正片'
                if not path:
                    continue
                if not sk4_VIDEO_RE.search(path):
                    path = base64.b64encode(json.dumps(
                        {'vodPlayFrom': src, 'playUrl': path},
                        separators=(',', ':'), ensure_ascii=False).encode()).decode()
                lines.setdefault(cn, []).append(title + '$' + path)

            if self.ONLY_4K:
                k4 = [k for k in lines if sk4__is4k(k)]
                if k4:
                    lines = collections.OrderedDict((k, lines[k]) for k in k4)

            intro = re.sub(r'<[^>]+>', '', meta.get(6) or meta.get(7) or '').strip()
            vod = {
                'vod_id': vid,
                'vod_name': meta.get(9, '') or '',
                'vod_pic': self._pic(meta.get(2, '')),
                'vod_remarks': meta.get(26, '') or '',
                'vod_year': str(meta.get(18, '') or ''),
                'vod_area': meta.get(1, '') or '',
                'vod_actor': meta.get(25, '') or '',
                'vod_director': meta.get(12, '') or '',
                'vod_content': intro,
                'vod_play_from': '$$$'.join(lines.keys()),
                'vod_play_url': '$$$'.join('#'.join(v) for v in lines.values()),
            }
            self._cache_put(self._detail_cache, vid, vod)
            return {'list': [vod]}
        except Exception:
            return {'list': []}

    # -------------------------------------------------- 播放
    def playerContent(self, flag, id, vipFlags=None):
        try:
            pid = str(id).strip()
            if sk4_VIDEO_RE.search(pid):
                return {'parse': 0, 'url': pid, 'header': {}}
            try:
                j = json.loads(base64.b64decode(pid).decode('utf-8', 'replace'))
            except Exception:
                return {'parse': 0, 'url': pid, 'header': {}}
            data = self._post('/api/proto/v5/videoUsableUrl',
                              {'vodPlayFrom': j.get('vodPlayFrom', ''),
                               'playUrl': j.get('playUrl', '')})
            url = ''
            if data:
                for fn, wt, v in sk4__pb(data):
                    if fn == 1 and wt == 2:
                        url = v.decode('utf-8', 'replace')
                        break
            if not url.startswith('http'):
                return {'parse': 0, 'url': '', 'header': {}}
            return {'parse': 0, 'url': url, 'header': {'User-Agent': self.sk4_UA}}
        except Exception:
            return {'parse': 0, 'url': '', 'header': {}}

    def liveContent(self, params):
        return {'list': []}


# ============================================================ 引擎 B：布布 (YunDuo)
class sk4__BubuEngine(object):
    """布布 —— JSON 接口 + /decode/url protobuf 解链"""

    ONLY_4K = True
    TIMEOUT = 15
    sk4_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    def __init__(self, cfg=None):
        self.cfg = dict(sk4_BUBU_DEFAULT)
        self.cfg.update(cfg or {})
        self.host = self.cfg['host'].rstrip('/')
        self.api = self.host + '/api.php/web'
        self._det = {}
        self._home = None

    def setup(self, ext):
        if not isinstance(ext, dict):
            return
        for k in sk4_BUBU_DEFAULT:
            v = ext.get(k)
            if v not in (None, ''):
                self.cfg[k] = str(v)
        self.host = self.cfg['host'].rstrip('/')
        self.api = self.host + '/api.php/web'
        if str(ext.get('only4k', '')).lower() in ('1', 'true', 'yes'):
            self.ONLY_4K = True

    # -------------------------------------------------- 网络
    def _hdr(self, extra=None):
        h = {'User-Agent': self.sk4_UA, 'Accept': 'application/json',
             'X-Client': self.cfg['x_client'],
             'web-sign': self.cfg['web_sign']}
        if extra:
            h.update(extra)
        return h

    def _raw(self, url, data=None, headers=None, timeout=None):
        req = urllib.request.Request(url, data=data,
                                     headers=headers or self._hdr())
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout or self.TIMEOUT,
                                    context=ctx) as r:
            return r.read()

    def _json(self, url):
        try:
            return json.loads(self._raw(url).decode('utf-8', 'ignore')) or {}
        except Exception:
            return {}

    def _get(self, path):
        return self._json(self.api + path)

    # -------------------------------------------------- 解链
    def _decode(self, token, frm):
        try:
            ts = int(time.time() * 1000)
            nonce = os.urandom(16).hex()
            msg = ('finger=%s&id=%s&nonce=%s&sk=%s&time=%d&v=1'
                   % (self.cfg['finger'], self.cfg['aid'], nonce,
                      self.cfg['sk'], ts))
            sign = hashlib.sha256(msg.encode()).hexdigest().upper()
            body = (sk4__f(1, 2, token.encode()) + sk4__f(2, 2, frm.encode()) +
                    sk4__f(3, 0, sk4__varint(ts)) + sk4__f(4, 2, nonce.encode()) +
                    sk4__f(5, 2, sign.encode()) + sk4__f(6, 2, self.cfg['aid'].encode()) +
                    sk4__f(7, 0, sk4__varint(1)))
            h = {'User-Agent': self.sk4_UA,
                 'Content-Type': 'application/x-protobuf',
                 'Accept': 'application/x-protobuf',
                 'X-Client': self.cfg['x_client'],
                 'web-sign': self.cfg['web_sign']}
            raw = self._raw(self.api + '/decode/url', body, h)
            for fn, wt, v in sk4__pb(raw):
                if fn == 3 and wt == 2:
                    s = v.decode('utf-8', 'replace')
                    if s.startswith('http'):
                        return s
            # 解不出时把服务端 msg 记下来，方便排查
            for fn, wt, v in sk4__pb(raw):
                if fn == 2 and wt == 2:
                    self.last_err = v.decode('utf-8', 'replace')
                    break
        except Exception as e:
            self.last_err = str(e)
        return ''

    # -------------------------------------------------- 首页 / 分类
    def homeContent(self, filter):
        try:
            j = self._get('/index/home')
            cats = ((j.get('data') or {}).get('categories') or [])
            classes, vids, seen = [], [], set()
            for c in cats:
                name = c.get('type_name') or c.get('type_en') or ''
                if not name:
                    continue
                classes.append({'type_id': name, 'type_name': name})
                for v in (c.get('videos') or []):
                    vid = str(v.get('vod_id') or '')
                    if not vid or vid in seen:
                        continue
                    seen.add(vid)
                    vids.append({'vod_id': vid,
                                 'vod_name': v.get('vod_name', ''),
                                 'vod_pic': v.get('vod_pic', '') or '',
                                 'vod_remarks': v.get('vod_remarks', '') or ''})
            return {'class': classes, 'list': vids,
                    'filters': {name: [] for name in
                                (c['type_name'] for c in classes)}}
        except Exception:
            return {'class': [], 'list': [], 'filters': {}}

    def homeVideoContent(self):
        if self._home and time.time() - self._home[0] < 60:
            return {'list': self._home[1]}
        try:
            j = self._get('/index/home')
            out, seen = [], set()
            for c in ((j.get('data') or {}).get('categories') or []):
                for v in (c.get('videos') or []):
                    vid = str(v.get('vod_id') or '')
                    if not vid or vid in seen:
                        continue
                    seen.add(vid)
                    out.append({'vod_id': vid,
                                'vod_name': v.get('vod_name', ''),
                                'vod_pic': v.get('vod_pic', '') or '',
                                'vod_remarks': v.get('vod_remarks', '') or ''})
            self._home = (time.time(), out)
            return {'list': out}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            page = int(pg or 1)
            url = ('%s/filter/vod?type_name=%s&page=%d&sort=hits'
                   % (self.api, urllib.parse.quote(str(tid)), page))
            ext = extend if isinstance(extend, dict) else {}
            for k, v in ext.items():
                if v not in (None, '', '全部'):
                    url += '&%s=%s' % (k, urllib.parse.quote(str(v)))
            j = self._json(url)
            lst = []
            for v in (j.get('data') or []):
                lst.append({'vod_id': str(v.get('vod_id') or ''),
                            'vod_name': v.get('vod_name', ''),
                            'vod_pic': v.get('vod_pic', '') or '',
                            'vod_remarks': v.get('vod_remarks', '') or ''})
            # 服务端 pageCount 常年写 1，不可信；按本页条数判断有没有下一页
            return {'list': lst, 'page': page,
                    'pagecount': page + 1 if len(lst) >= 20 else page,
                    'limit': 24, 'total': len(lst)}
        except Exception:
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        try:
            j = self._json('%s/search/index?wd=%s&pg=%s'
                           % (self.api, urllib.parse.quote(str(key)),
                              str(pg or 1)))
            out = []
            low = str(key).lower()
            for v in (j.get('data') or []):
                vid = str(v.get('vod_id') or '')
                nm = (v.get('vod_name') or '').strip()
                if not vid or not nm or 'http' in nm or '.com' in nm:
                    continue
                if low not in nm.lower():
                    continue
                out.append({'vod_id': vid, 'vod_name': nm,
                            'vod_pic': v.get('vod_pic', '') or '',
                            'vod_remarks': v.get('vod_remarks', '') or ''})
            return {'list': out}
        except Exception:
            return {'list': []}

    # -------------------------------------------------- 详情
    def _detail(self, vid):
        if vid in self._det:
            return self._det[vid]
        j = self._get('/vod/get_detail?vod_id=' + str(vid))
        d = j.get('data')
        if isinstance(d, list):
            d = d[0] if d else {}
        d = d or {}
        froms = (d.get('vod_play_from') or '').split('$$$')
        urls = (d.get('vod_play_url') or '').split('$$$')
        eps = collections.OrderedDict()
        all_eps = collections.OrderedDict()
        for fr, u in zip(froms, urls):
            if not fr or not u:
                continue
            items = []
            for seg in u.split('#'):
                if '$' not in seg:
                    continue
                title, token = seg.split('$', 1)
                if not token:
                    continue
                items.append((title.strip() or '正片', token.strip()))
            if items:
                all_eps[fr] = items
                if (not self.ONLY_4K) or sk4__is4k(fr):
                    eps[fr] = items
        if not eps:
            eps = collections.OrderedDict(all_eps)
        rec = (d, eps, all_eps)
        _cap_put(self._det, vid, rec, 64, drop=8)
        return rec

    def detailContent(self, ids):
        try:
            vid = str(ids[0] if isinstance(ids, (list, tuple)) and ids
                      else ids).strip()
            d, eps, _ = self._detail(vid)
            if not d:
                return {'list': []}
            lines, urls = [], []
            for fr, items in eps.items():
                lines.append(fr)
                urls.append('#'.join(
                    '%s$token@%s@%s@%s@%s' % (t, tok, fr, vid,
                                               urllib.parse.quote(t))
                    for t, tok in items))
            vod = {
                'vod_id': vid,
                'vod_name': d.get('vod_name', '') or '',
                'vod_pic': d.get('vod_pic', '') or '',
                'vod_remarks': d.get('vod_remarks', '') or '',
                'vod_year': str(d.get('vod_year', '') or ''),
                'vod_area': d.get('vod_area', '') or '',
                'vod_actor': d.get('vod_actor', '') or '',
                'vod_director': d.get('vod_director', '') or '',
                'vod_content': re.sub(r'<[^>]+>', '',
                                      d.get('vod_content', '') or '').strip(),
                'vod_play_from': '$$$'.join(lines),
                'vod_play_url': '$$$'.join(urls),
            }
            return {'list': [vod]}
        except Exception:
            return {'list': []}

    # -------------------------------------------------- 播放
    def playerContent(self, flag, id, vipFlags=None):
        try:
            pid = str(id)
            if pid.startswith('http'):
                return {'parse': 0, 'url': pid, 'header': {'User-Agent': self.sk4_UA}}
            if not pid.startswith('token@'):
                return {'parse': 0, 'url': '', 'header': {}}
            p = pid.split('@', 4)
            token = p[1] if len(p) > 1 else ''
            frm = p[2] if len(p) > 2 else ''
            vid = p[3] if len(p) > 3 else ''
            title = urllib.parse.unquote(p[4]) if len(p) > 4 else ''
            url = self._decode(token, frm)
            if not url and vid:
                # 该线路被平台锁死（布布 CO4K 会返回 PLATFORM_NOT_ALLOWED）
                # → 先换同片的其它高清线路，避免直接黑屏。
                url = self._fallback(vid, frm, title)
            if not url and vid:
                # 最后兜底：和官方 spider 一样交给 /play 网页，让播放器自己嗅探
                return {'parse': 1,
                        'url': '%s/play/%s#sid=%s' % (self.host, vid, frm),
                        'header': {'User-Agent': self.sk4_UA,
                                   'Referer': self.host + '/'}}
            if not url:
                return {'parse': 0, 'url': '', 'header': {}}
            return {'parse': 0, 'url': url,
                    'header': {'User-Agent': self.sk4_UA,
                               'Referer': self.host + '/'}}
        except Exception:
            return {'parse': 0, 'url': '', 'header': {}}

    # 实测画质：BBA 1920x804 > NBY ≈ PAN1 > zijianm3u8 / qsvip
    _FB_ORDER = ('BBA', 'NBY', 'PAN1', 'zijianm3u8', 'qsvip')

    def _fallback(self, vid, frm, title):
        try:
            _, _, all_eps = self._detail(vid)
            order = [k for k in self._FB_ORDER if k in all_eps and k != frm]
            order += [k for k in all_eps
                      if k != frm and not sk4__is4k(k) and k not in order]
            order += [k for k in all_eps if k != frm and sk4__is4k(k)]
            for k in order:
                items = all_eps.get(k) or []
                tok = ''
                for t, tk in items:
                    if title and t == title:
                        tok = tk
                        break
                if not tok and items:
                    tok = items[0][1]
                if tok:
                    u = self._decode(tok, k)
                    if u:
                        return u
        except Exception:
            pass
        return ''


# ============================================================ 入口
class SK4KRaw(_Base):
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except Exception:
            pass
        self.src = '天堂'
        self.eng = None
        self._build('天堂', {})

    # -------------------------------------------------- 生命周期
    def _build(self, name, ext):
        if name in sk4_APP_SOURCES:
            eng = sk4__AppEngine(sk4_APP_SOURCES[name])
        else:
            eng = sk4__BubuEngine()
        eng.setup(ext)
        self.src = name
        self.eng = eng

    def init(self, extend=""):
        # 不联网：导入阶段只解析配置
        ext = {}
        try:
            if isinstance(extend, str):
                s = extend.strip()
                if s.startswith('{') and s.endswith('}'):
                    ext = json.loads(s) or {}
                elif s:
                    ext = {'src': s}
            elif isinstance(extend, dict):
                ext = dict(extend)
        except Exception:
            ext = {}
        name = str(ext.get('src') or ext.get('name') or '天堂').strip()
        name = sk4_SRC_ALIAS.get(name, name)
        if name not in sk4_SRC_ORDER:
            name = '天堂'
        rest = dict(ext)
        rest.pop('src', None)
        rest.pop('name', None)
        self._build(name, rest)

    def getName(self):
        return self.src + '·4K'

    def destroy(self):
        try:
            self.eng = None
        except Exception:
            pass

    def _e(self):
        if self.eng is None:
            self._build('天堂', {})
        return self.eng

    # -------------------------------------------------- 标准接口
    def homeContent(self, filter=False):
        return self._e().homeContent(filter)

    def homeVideoContent(self):
        return self._e().homeVideoContent()

    def categoryContent(self, tid, pg, filter, extend):
        return self._e().categoryContent(tid, pg, filter, extend)

    def searchContent(self, key, quick, pg="1"):
        return self._e().searchContent(key, quick, pg)

    def detailContent(self, ids):
        return self._e().detailContent(ids)

    def playerContent(self, flag, id, vipFlags=None):
        return self._e().playerContent(flag, id, vipFlags)

    def liveContent(self, params):
        return {'list': []}

# ---- 门面适配 sk：四源 4K 合并成一个一级源，不建独立站点 ----
class SK4KSpider(_BaseSpider):
    NAME = '四源4K专线'
    SRCS = ('天堂', '布布', '华谊', '苹果')
    SEARCH_WAIT = 2.6
    DETAIL_WAIT = 3.6
    PLAY_WAIT = 8.0

    def __init__(self):
        # init 绝不联网：四个引擎只解析配置；站点不通由各处限时兜住。
        self.obs = {}
        for n in self.SRCS:
            try:
                ob = SK4KRaw()
                ob.init(json.dumps({'src': n}, ensure_ascii=False))
                self.obs[n] = ob
            except Exception:
                pass
        # 四源搜索偶发有子源超过门面 2.8s 预算。晚到的结果仍由后台线程
        # 累加进这里，详情时按 (子源, vid) 回填，保证四源线路不缺。
        self._key_ids = {}
        self._vid_key = {}
        self._lock = threading.Lock()

    def init(self, extend=''):
        return None

    def destroy(self):
        for ob in list(self.obs.values()):
            try:
                ob.destroy()
            except Exception:
                pass

    @staticmethod
    def _b64(raw):
        return base64.urlsafe_b64encode(
            raw.encode('utf-8')).decode('ascii').rstrip('=')

    @staticmethod
    def _unb64(s):
        s = str(s or '')
        s += '=' * (-len(s) % 4)
        return base64.urlsafe_b64decode(
            s.encode('ascii')).decode('utf-8', 'replace')

    def _enc_id(self, ids):
        return 'sk4:' + self._b64(json.dumps(
            ids, ensure_ascii=False, separators=(',', ':')))

    def _dec_id(self, code):
        s = str(code or '')
        if not s.startswith('sk4:'):
            return None
        try:
            v = json.loads(self._unb64(s[4:]))
            return v if isinstance(v, dict) else None
        except Exception:
            return None

    @classmethod
    def _fan(cls, work, wait):
        box, ths = {}, []

        def run(k):
            try:
                box[k] = work(k)
            except Exception:
                pass

        for k in cls.SRCS:
            th = threading.Thread(target=run, args=(k,), daemon=True)
            th.start()
            ths.append(th)
        deadline = time.time() + wait
        for th in ths:
            th.join(max(0.0, deadline - time.time()))
        return box

    def homeContent(self, filter=True):
        return {'class': [], 'list': []}

    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        return {'list': [], 'page': 1, 'pagecount': 1, 'total': 0}

    @staticmethod
    def _key(nm):
        # 布布习惯把片名写成「庆余年 第一季」。只归并「第一季/第1季」这类
        # 默认季后缀；第二季及衍生片一律不合并，防止把错片的线路挂进来。
        k = re.sub(r'\s+', '', str(nm or '')).lower()
        return re.sub(r'(第一季|第1季|season1|s01)$', '', k)

    def _absorb(self, nm, vid, n):
        k = self._key(nm)
        with self._lock:
            self._key_ids.setdefault(k, {}).setdefault(n, vid)
            self._vid_key[(n, vid)] = k
        return k

    def searchContent(self, key, quick=False, pg='1'):
        kw = str(key or '').strip()
        if not kw:
            return {'list': []}

        def work(n):
            lst = (self.obs[n].searchContent(
                kw, quick, str(pg or '1')) or {}).get('list') or []
            # 在线程内就累加：_fan 超时返回后，晚到的子源仍会写进来
            for it in lst:
                if isinstance(it, dict):
                    nm = str(it.get('vod_name') or '').strip()
                    vid = str(it.get('vod_id') or '').strip()
                    if nm and vid:
                        self._absorb(nm, vid, n)
            return lst

        box = self._fan(work, self.SEARCH_WAIT)
        # 四源同名合并成一张卡，id 里带上目前已知的每个子源 vod_id。
        merged, order = {}, []
        for n in self.SRCS:
            for it in (box.get(n) or []):
                if not isinstance(it, dict):
                    continue
                nm = str(it.get('vod_name') or '').strip()
                vid = str(it.get('vod_id') or '').strip()
                if not nm or not vid:
                    continue
                k = self._key(nm)
                if k not in merged:
                    merged[k] = {
                        'vod_name': nm,
                        'vod_pic': it.get('vod_pic') or '',
                        'vod_remarks': it.get('vod_remarks') or ''}
                    order.append(k)
                elif nm == kw:
                    # 优先用与搜索词完全一致的片名，strict_match 才能命中
                    merged[k]['vod_name'] = nm
        with self._lock:
            snap = dict((k, dict(v)) for k, v in self._key_ids.items())
        return {'list': [
            {'vod_id': self._enc_id(snap.get(k, {})),
             'vod_name': merged[k]['vod_name'],
             'vod_pic': merged[k]['vod_pic'],
             'vod_remarks': merged[k]['vod_remarks']}
            for k in order[:24] if snap.get(k)]}

    def detailContent(self, ids):
        raw = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        code = str(raw or '')
        idmap = dict(self._dec_id(code) or {})
        # 用累加缓存回填：本次搜索里晚到、没编进卡片 id 的子源也补上
        with self._lock:
            snap = dict((k, dict(v)) for k, v in self._key_ids.items())
            keys = [self._vid_key.get((n, v)) for n, v in idmap.items()]
        for k in keys:
            for n2, v2 in (snap.get(k) or {}).items():
                idmap.setdefault(n2, v2)
        if not idmap:
            # 兜底：非本源编码的 id，四个子源拿同一个 id 各试一次
            idmap = dict((n, code) for n in self.SRCS)

        def work(n):
            vid = idmap.get(n)
            if not vid:
                return None
            v = (self.obs[n].detailContent([vid]) or {}).get('list') or []
            return v[0] if v and isinstance(v[0], dict) else None

        box = self._fan(work, self.DETAIL_WAIT)
        froms, urls, meta = [], [], None
        for n in self.SRCS:
            v = box.get(n)
            if not isinstance(v, dict):
                continue
            if meta is None:
                meta = v
            fr = str(v.get('vod_play_from') or '').split('$$$')
            ur = str(v.get('vod_play_url') or '').split('$$$')
            for i, f in enumerate(fr):
                f = str(f or '').strip()
                if not f:
                    continue
                # 「超级无敌4k / 高清4k」实测 1280x720，挂着 4K 的名头点开就是降级，
                # 直接从线路表剔掉（实测表见 sk4_MEASURED）。子源原始名不带
                # 「天堂·」前缀，这里拼全名再查表，免得把别源同名线误认成四源的。
                if sk4_hd_only('%s·%s' % (n, f)) or sk4_dead_line('%s·%s' % (n, f)):
                    continue
                seg = ur[i] if i < len(ur) else ''
                eps = []
                for part in str(seg).split('#'):
                    part = part.strip()
                    if not part:
                        continue
                    nm, sep, pid = part.partition('$')
                    if not sep:
                        nm, pid = '正片', part
                    eps.append('%s$sk4|%s|%s'
                               % (nm.strip() or '正片', n, pid))
                if eps:
                    froms.append(sk4_qname('%s·%s' % (n, f)))
                    urls.append('#'.join(eps))
        if not froms:
            return {'list': []}
        vod = dict(meta or {})
        vod['vod_id'] = code
        vod['vod_play_from'] = '$$$'.join(froms)
        vod['vod_play_url'] = '$$$'.join(urls)
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags=None):
        pid = str(id or '')
        name, rest = '', pid
        if pid.startswith('sk4|'):
            p = pid[4:].split('|', 1)
            if len(p) == 2:
                name, rest = p[0], p[1]
        f = str(flag or '')
        if name not in self.obs:
            for n in self.SRCS:
                if f.startswith(n):
                    name = n
                    break
        if name not in self.obs:
            name = self.SRCS[0]
        ob = self.obs.get(name)
        if ob is None:
            return {'parse': 0, 'url': '', 'header': {}}
        for n in self.SRCS:
            if f.startswith(n + '·'):
                f = f[len(n) + 1:]
                break
        box = {}

        def run():
            try:
                box['r'] = ob.playerContent(f, rest, vipFlags)
            except Exception:
                pass

        th = threading.Thread(target=run, daemon=True)
        th.start()
        th.join(self.PLAY_WAIT)
        r = box.get('r')
        return r if isinstance(r, dict) else {
            'parse': 0, 'url': '', 'header': {}}
# ==================== 四源4K专线线路源 sk END ====================


# ==================== 找剧4K 一级源 zj BEGIN ====================
class ZJSpider(_BaseSpider):
    # 官方 4K/1080P 线路（游客会话）作为一级源挂进 Kishuto 聚合。
    # init 绝不联网；站点不通时 _zj_quick 限时返回空，不拖慢搜索/详情。
    NAME = '找剧4K'

    def __init__(self):
        self.ob = None
        self.cfg = {}

    def init(self, extend=''):
        try:
            cfg = (json.loads(extend) if isinstance(extend, str)
                   and extend.strip().startswith('{') else {})
        except Exception:
            cfg = {}
        self.cfg = cfg if isinstance(cfg, dict) else {}
        ck = str(self.cfg.get('zj_cookie') or self.cfg.get('cookie') or '')
        if self.ob is None:
            self.ob = ZJSource(ck)
        return None

    def _ob(self):
        if self.ob is None:
            self.ob = ZJSource()
        return self.ob

    @staticmethod
    def _zj_quick(fn, budget=2.6, fallback=None):
        box = {}

        def run():
            try:
                box['v'] = fn()
            except Exception:
                box['v'] = fallback

        th = threading.Thread(target=run, daemon=True)
        th.start()
        th.join(budget)
        return box.get('v', fallback)

    def homeContent(self, filter=True):
        return {'class': [], 'list': []}

    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        return {'list': [], 'page': 1, 'pagecount': 1, 'total': 0}

    def searchContent(self, key, quick=False, pg='1'):
        kw = str(key or '')
        if not kw.strip():
            # 与正常返回同构：部分壳会读 page/limit 决定分页，缺字段会当成异常结果
            return {'list': [], 'page': 1, 'pagecount': 1,
                    'limit': 0, 'total': 0}
        try:
            page = int(str(pg or 1))
        except Exception:
            page = 1
        got = self._zj_quick(lambda: self._ob().search(kw, page), 2.6, []) or []
        return {'list': [x for x in as_list(got) if isinstance(x, dict)]}

    def detailContent(self, ids):
        vid = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        # 站点详情实测 3.6s（搜索 0.4s 就回），2.6s 的预算会让它永远返回空、
        # 一条线路都拿不到。放宽到 6s：首屏本来就不等它（FILL_BUDGET 1.6s），
        # 结果会在后台补齐（TOPUP_BUDGET 15s）里并进来。
        d = self._zj_quick(lambda: self._ob().detail(text(vid)), 6.0, {}) or {}
        vod = dict(as_dict(d.get('vod')))
        froms, urls = [], []
        for item in as_list(d.get('lines')):
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                froms.append(str(item[0]))
                urls.append('#'.join(str(x) for x in as_list(item[1])))
        vod['vod_play_from'] = '$$$'.join(froms)
        vod['vod_play_url'] = '$$$'.join(urls)
        if not vod.get('vod_id'):
            vod['vod_id'] = vid
        return {'list': [vod]}

    def playerContent(self, flag, id, vipFlags=None):
        got = self._zj_quick(lambda: self._ob().play(text(id)), 8.0,
                             {'url': '', 'parse': 0})
        return got if isinstance(got, dict) else {'url': '', 'parse': 0}
# ==================== 找剧4K 一级源 zj END ====================


# ==================== 画质探测与播放校验工具 ====================
_KISH_H_CACHE = {}
_KISH_H_LOCK = threading.Lock()
# 探测时顺手记下的 HTTP 状态码：高度解析不出来（媒体列表没有 RESOLUTION、
# 纯 ts 切片、CDN 不给 Range）时仍能区分「这条链 404 了」和「只是没标分辨率」。
_KISH_ST_CACHE = {}
_KISH_ST_LOCK = threading.Lock()

# 画质判定日志：环形的、只在内存里。假 4K 判定以前对用户是个黑盒 —— 只看到
# 「点开 4K 却被换了线」，看不到「宣称 2160 / 实测 1080」这个事实，出了问题
# 也没法复现。这里留最近 80 条判定，在诊断中心「画质判定」分区里读。
# 只写线路名和数字：URL、token、请求头一律不入日志，避免直链留在长驻内存里。
_QDIAG = []
_QDIAG_LOCK = threading.Lock()
_QDIAG_MAX = 80


def _qdiag_add(kind, name, claim=0, measure=0, state='', cost=0.0, action=''):
    try:
        with _QDIAG_LOCK:
            _QDIAG.append((time.time(), str(kind or ''), str(name or '')[:36],
                           int(claim or 0), int(measure or 0), str(state or ''),
                           round(float(cost or 0), 2), str(action or '')))
            if len(_QDIAG) > _QDIAG_MAX:
                del _QDIAG[:_QDIAG_MAX // 2]
    except Exception:
        pass


def _qdiag_h(v):
    """高度 → 短标签：报告里只写档位，不写 2160 这种数字（手机屏太窄）。

    阈值与 kish_is_fake_claim 的 need 表一致（2000/1300/900/600），
    否则同一份实测值会在报告里显示成一个档、判定按另一个档走。
    """
    v = int(v or 0)
    if v >= 2000:
        return '4K'
    if v >= 1300:
        return '2K'
    if v >= 900:
        return '1080P'
    if v >= 600:
        return '720P'
    return '%dP' % v if v else '未读到'


_QDIAG_STATE = {'real': '真4K', 'low': '判假', 'unknown': '探不到',
                 'race': '抢答'}
_QDIAG_ACT = {'swap': '→ 已换源', 'keep': '换不到，播本线',
              'drop': '→ 弃用', 'skip': '已跳过',
              'start': '→ 并行开抢', 'win': '→ 抢答出流'}


def _qdiag_text(n=24):
    with _QDIAG_LOCK:
        allrows = list(_QDIAG)
    rows = allrows[-n:]
    if not rows:
        return ('还没有画质判定记录。\n\n'
                '播放任意带 4K/2K 宣称的线路后再回来看 —— 这里会列出'
                '「宣称高度 / 实测高度 / 判定结果 / 是否换源 / 耗时」。\n'
                '探不到高度的 MP4 云盘线记为「探不到」，既不当真 4K 也不判假。')
    stat = {}
    for row in allrows:
        k = row[5] or 'unknown'
        stat[k] = stat.get(k, 0) + 1
    head = '累计判定 %d 条：真 4K %d、判假 %d、探不到 %d' % (
        len(allrows), stat.get('real', 0), stat.get('low', 0),
        stat.get('unknown', 0))
    out = [head, '']
    for t, kind, name, claim, mh, st, cost, act in reversed(rows):
        tag = '宣称 %s' % _qdiag_h(claim) if claim else '无宣称'
        if st == 'race':
            # 抢答行没有实测高度：只记「哪条线、宣称多少、是不是它赢的」
            out.append('%s  %s\n     %s%s' % (
                time.strftime('%H:%M', time.localtime(t)), name, tag,
                '  ' + _QDIAG_ACT.get(act, act) if act else ''))
            continue
        res = _qdiag_h(mh) if mh else '未读到'
        out.append('%s  %s\n     %s · 实测 %s · %s%s%s' % (
            time.strftime('%H:%M', time.localtime(t)), name,
            tag, res, _QDIAG_STATE.get(st, st or '未知'),
            '  ' + _QDIAG_ACT.get(act, act) if act else '',
            '  %.2fs' % cost if cost else ''))
    return '\n'.join(out)


# ---- 搜索到齐情况（只读） ---------------------------------------------------
# 早停的代价是「这一轮少等了几个源」，但用户在壳里看不到这件事，只会以为
# 「片帝没有这部片」。这里记最近一次真实搜索：几个源应答、缺了谁、按哪个
# 档位缓存、花了多久。诊断页「上次搜索」直接读，不联网、不改结果。
_LAST_SEARCH = {}
_LAST_SEARCH_LOCK = threading.Lock()
_SEARCH_STATE = {'complete': '完整', 'partial': '部分', 'empty': '空结果',
                 'error': '源报错'}


def _search_stat_put(kw, order, box, errs, n_out, ttl, cost, must=()):
    try:
        # 「报故障」的源虽然应答了，但给的是错/空，算没到齐；不能同时算「没赶上」
        miss = [t for t in order if t not in box and t not in errs]
        bad = [t for t in order if t in errs]
        if n_out <= 0:
            state = 'error' if bad else 'empty'
        elif not miss and not bad:
            state = 'complete'
        else:
            state = 'partial'
        with _LAST_SEARCH_LOCK:
            _LAST_SEARCH.clear()
            _LAST_SEARCH.update({'kw': str(kw or '')[:20], 'at': time.time(),
                                 'n': len(order) - len(miss) - len(bad),
                                 'total': len(order),
                                 'out': int(n_out), 'miss': miss, 'bad': bad,
                                 'cost': round(float(cost or 0.0), 2),
                                 'ttl': int(ttl or 0), 'state': state,
                                 'must': list(must or ())})
    except Exception:
        pass


def _search_stat_text(labels=None):
    labels = labels or {}
    with _LAST_SEARCH_LOCK:
        st = dict(_LAST_SEARCH)
    if not st:
        return ('还没有搜索记录。\n\n'
                '去搜一部片再回来 —— 这里会说明那次有几个源应答、缺了谁、'
                '为什么有的源没出现在结果里。')
    nm = lambda t: labels.get(t, t)
    miss = [nm(t) for t in st.get('miss') or []]
    bad = [nm(t) for t in st.get('bad') or []]
    state = st.get('state') or ''
    out = ['搜索「%s」· %s' % (st.get('kw'), time.strftime(
        '%H:%M:%S', time.localtime(st.get('at') or 0))),
        '%s 条结果 · 有效应答 %d/%d 源 · 用时 %.2fs · %s' % (
            st.get('out', 0), st.get('n', 0), st.get('total', 0),
            st.get('cost', 0.0), _SEARCH_STATE.get(state, state or '未知'))]
    if miss:
        out.append('没赶上：%s' % '、'.join(miss))
    if bad:
        out.append('报故障：%s' % '、'.join(bad))
    out.append('本次缓存 %d 秒%s' % (
        st.get('ttl', 0),
        '' if st.get('ttl', 0) >= 600 else '（未按完整档缓存）'))
    if miss or bad:
        out.append('')
        if miss:
            out.append('「没赶上」= 早停时它还没回，不是它没有这部片；')
            out.append('过一会儿重搜一次通常就能看到它的条目。')
        if bad:
            out.append('「报故障」= 它自己返回了错误（限流/接口抽风），这次不算它的结果。')
        out.append('这一轮只能算「部分完整」，详情页仍会跨源补线路。')
    return '\n'.join(out)


def kish_probe_height(url, timeout=1.6):
    """探测播放地址最大垂直分辨率（结果缓存 30 分钟）。

    每次播放 4K 线路都要探一次很费时间（最多 1.5s），同一部剧反复播同一个
    地址时没必要重探；拿到非 0 结果才缓存，失败的下次还探。
    """
    u = str(url or '').strip()
    if not (u.startswith('http://') or u.startswith('https://')):
        return 0
    now = time.time()
    with _KISH_H_LOCK:
        hit = _KISH_H_CACHE.get(u)
        if hit and now - hit[0] < 1800:
            return hit[1]
    # 同一地址 10 分钟内已经被 4xx/5xx 拒过：别再花 1.6s 重探一遍。
    # 408/425/429 是超时/限流，会自己恢复，不算硬失败。
    _st = kish_url_status(u)
    if 400 <= _st < 600 and _st not in (408, 425, 429):
        return 0
    h = _kish_probe_height_raw(u, timeout)
    if h:
        with _KISH_H_LOCK:
            _cap_put(_KISH_H_CACHE, u, (now, h), 400)
    return h


def _kish_probe_height_raw(u, timeout=1.6):
    try:
        # 只读前 64KB：实测 8KB 与 512KB 读到的分辨率完全一致（moov/EBML 头都在
        # 文件开头），而 512KB 在云盘线（天翼云/联通云）上要多花 0.05~0.4s，
        # 影探 4K 每条线首播都要走这一次。64KB 留出余量，兼顾 moov 靠前的偏差。
        st, body = http(u, headers={
            'User-Agent': UA_WEB,
            'Accept': '*/*',
            'Accept-Encoding': 'identity',
            'Range': 'bytes=0-65535',
        }, timeout=timeout, retries=1)
        if st:
            with _KISH_ST_LOCK:
                _cap_put(_KISH_ST_CACHE, u, (time.time(), st), 500)
        if not body:
            return 0
        # 顺手记内容类型：状态码 200 也可能是一张播放页/封面图/错误 JSON，
        # 只靠后缀和状态码分不出来（v.youku.com/v_show/id_xxx 没有 .html 后缀）
        _kish_note_kind(u, body)
        # HLS
        if body[:7] == b'#EXTM3U' or b'#EXTM3U' in body[:120]:
            text = body.decode('utf-8', 'replace')
            heights = []
            for m in re.finditer(r'RESOLUTION\s*=\s*(\d+)x(\d+)', text, re.I):
                try:
                    heights.append(int(m.group(2)))
                except Exception:
                    pass
            if heights:
                return max(heights)
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '.m3u8' in line.lower():
                    nu = line if line.startswith('http') else urllib.parse.urljoin(u, line)
                    return kish_probe_height(nu, timeout=min(2.0, timeout))
                break
            return 0
        # MKV / WebM：EBML PixelWidth(0xB0) / PixelHeight(0xBA)，取文件头附近合法值
        if body[:4] == b'\x1aE\xdf\xa3':
            hs = []
            for m in re.finditer(b'\xba\x82(..)', body[:200000]):
                h = int.from_bytes(m.group(1), 'big')
                if 240 <= h <= 4320:
                    hs.append(h)
            for m in re.finditer(b'\xb0\x82(..)', body[:200000]):
                w = int.from_bytes(m.group(1), 'big')
                # 成对时用常见高度
                if w in (3840, 2560, 1920, 1280):
                    hs.append({3840: 2160, 2560: 1440, 1920: 1080, 1280: 720}.get(w, 0))
            hs = [h for h in hs if h]
            return max(hs) if hs else 0
        # MP4：样本条目 avc1/hvc1 里的 width/height（uint16 BE，type 后 28/30 字节）。
        # 注意 ftyp 的 compatible brand 也常含「avc1」（isom iso2 avc1 mp41），
        # 那不是样本条目 —— 它 type 后紧跟 'mp41'；真样本条目 type 后是 6 个 0
        # （reserved + data_reference_index 高半）。旧代码取第一个 'avc1' 又按
        # type+24 读宽高，四源那批 MP4 因此一律读成 0，假 4K 判定全失效。
        for tag in (b'avc1', b'hvc1', b'hev1', b'av01'):
            pos = 0
            while True:
                i = body.find(tag, pos)
                if i < 0:
                    break
                pos = i + 4
                if body[i + 4:i + 10] != b'\x00' * 6 or i + 32 > len(body):
                    continue
                w = int.from_bytes(body[i + 28:i + 30], 'big')
                h = int.from_bytes(body[i + 30:i + 32], 'big')
                if 240 <= h <= 4320 and 320 <= w <= 7680:
                    return h
        # stsd 落在 64KB 之外时退到 tkhd 的显示宽高（16.16 定点）。实测四源4K
        # 的 MP4 线 moov 有 2.3MB、样本条目读不到，但 tkhd 就在 moov 开头，
        # 1280x720 / 1920x1080 都能直接读出来。
        hs = []
        for m in re.finditer(b'tkhd', body):
            i = m.start()
            ver = body[i + 4] if i + 4 < len(body) else -1
            if ver not in (0, 1):
                continue
            # version0: height @ type+84；version1 多 12 字节（64 位时间戳）
            off = 84 if ver == 0 else 96
            if i + off + 4 > len(body):
                continue
            h = int.from_bytes(body[i + off:i + off + 4], 'big') >> 16
            w = int.from_bytes(body[i + off - 4:i + off], 'big') >> 16
            if 240 <= h <= 4320 and 320 <= w <= 7680:
                hs.append(h)
        if hs:
            return max(hs)
        return 0
    except Exception:
        return 0


def kish_url_status(url, ttl=600):
    """上一次分辨率探测时该地址的 HTTP 状态码（0 = 没探过/网络层失败/已过期）。"""
    with _KISH_ST_LOCK:
        hit = _KISH_ST_CACHE.get(str(url or ''))
    if not hit or time.time() - hit[0] > ttl:
        return 0
    return hit[1]


def kish_claim_height(flag_or_name):
    """线路名宣称的高度：4K→2160, 2K→1440, 1080→1080, 其它 0。"""
    s = str(flag_or_name or '').lower()
    if any(k in s for k in ('4k', 'uhd', '2160')):
        return 2160
    if any(k in s for k in ('2k', '1440', 'qhd')):
        return 1440
    if any(k in s for k in ('1080', 'fhd')):
        return 1080
    if '720' in s:
        return 720
    return 0


def kish_is_fake_claim(name, measured_h):
    """宣称高档但实测明显不够 → 假。"""
    claim = kish_claim_height(name)
    if not claim or not measured_h:
        return False
    need = {2160: 2000, 1440: 1300, 1080: 900, 720: 600}.get(claim, claim)
    return measured_h < need


# 站点「播放页」：parse=0 把这种地址丢给播放器必然黑屏（影探腾讯线、河豚 QQ 线）
_KISH_PAGE_RE = re.compile(
    r'^https?://[^?#]+\.(?:html?|shtml|php|aspx?|jsp)(?:[?#]|$)', re.I)

# 看着就是媒体文件的地址。有些源会同时给 parse=1（交壳）+ 一条真 m3u8，这种
# 仍然值得探高度；而 jx4k.fuyingapi.top/api/?key=… 这类解析接口探了只有 0。
_KISH_MEDIA_RE = re.compile(
    r'\.(?:m3u8|mp4|mkv|flv|ts|mpd|mov|avi|wmv)(?:$|[?#])', re.I)

# 只有站点的「播放页」host 才按 byte 逐个比对，避免把 CDN 直链误判成网页：
# 优酷播放页是 v.youku.com/v_show/id_xxx（没有 .html 后缀），而真实直链在
# apd-vlive.apdcdn.tc.qq.com / k0udeyaayccydz.djvod.ndcimgs.com 这类 CDN 上，
# 用「主域相同」去匹配会把 tc.qq.com 的直链一起杀掉。
_KISH_PAGE_HOSTS = (
    'v.youku.com', 'www.youku.com',
    'v.qq.com', 'm.v.qq.com',
    'www.iqiyi.com', 'm.iqiyi.com',
    'www.mgtv.com', 'm.mgtv.com',
    'tv.sohu.com', 'm.tv.sohu.com',
    'www.bilibili.com', 'm.bilibili.com',
    'v.pptv.com', 'www.le.com', 'www.wasu.cn', 'www.miguvideo.com',
)

# 内容类型缓存：探测高度时顺手记，播放阶段用来识别「200 但根本不是媒体」
_KISH_KIND_CACHE = {}
_KISH_KIND_LOCK = threading.Lock()


def _kish_content_kind(body):
    """按响应体头部判定类型：hls/dash/mp4/mkv/ts/html/json/other。"""
    if not body:
        return 'empty'
    head = body[:600].lstrip()
    if head[:7] == b'#EXTM3U':
        return 'hls'
    if b'<MPD' in head or b'urn:mpeg:dash' in head:
        return 'dash'
    low = head.lower()
    if head[:1] == b'<' and (b'<!doctype' in low or b'<html' in low
                             or b'<script' in low or b'<?xml' in low[:8]):
        return 'html'
    if head[:1] in (b'{', b'['):
        return 'json'
    if b'ftyp' in body[:16] or b'moov' in body[:512]:
        return 'mp4'
    if body[:4] == b'\x1aE\xdf\xa3':
        return 'mkv'
    if body[:1] == b'\x47':
        return 'ts'
    return 'other'


def _kish_note_kind(u, body):
    k = _kish_content_kind(body)
    with _KISH_KIND_LOCK:
        _cap_put(_KISH_KIND_CACHE, u, (time.time(), k), 600)


def kish_url_kind(url, timeout=1.2, ttl=1800):
    """播放地址的实际内容类型（带缓存）。未探过就顺手探一次。"""
    u = str(url or '').strip()
    if not (u.startswith('http://') or u.startswith('https://')):
        return ''
    hit = _KISH_KIND_CACHE.get(u)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    try:
        kish_probe_height(u, timeout=timeout)
    except Exception:
        pass
    hit = _KISH_KIND_CACHE.get(u)
    return hit[1] if hit and time.time() - hit[0] < ttl else ''


def kish_url_kind_cached(url, ttl=1800):
    """只读缓存版（不发请求）：给「换源候选要不要交给播放器」这类判定用。"""
    hit = _KISH_KIND_CACHE.get(str(url or '').strip())
    return hit[1] if hit and time.time() - hit[0] < ttl else ''


def kish_probe_light(url, timeout=1.0, headers=None):
    """轻量验活：只取前 8KB，拿状态码 + 内容类型。

    换源候选不能盲交给播放器（实测 djvod 那批 /upic/ 地址恒 400，
    交出去就是黑屏），但也不值得为它跑 512KB 的高度探测 —— 8KB 足够
    看出 #EXTM3U / <MPD / ftyp / EBML / HTML。结果写进同一份状态与类型
    缓存，后面的判定全部免费。
    headers 传子源给播放器的请求头：不少 CDN 无 Referer 直接回 403，
    不带原样请求头去验活会把能播的线路误杀掉。
    """
    u = str(url or '').strip()
    if not (u.startswith('http://') or u.startswith('https://')):
        return 0
    h = {'User-Agent': UA_WEB, 'Accept': '*/*', 'Accept-Encoding': 'identity'}
    if isinstance(headers, dict):
        for k, v in headers.items():
            if isinstance(k, str) and isinstance(v, str) and k:
                h[k] = v
    h['Range'] = 'bytes=0-8191'
    try:
        st, body = http(u, headers=h, timeout=timeout, retries=1)
    except Exception:
        return 0
    if st:
        with _KISH_ST_LOCK:
            _cap_put(_KISH_ST_CACHE, u, (time.time(), st), 500)
    if body:
        _kish_note_kind(u, body)
    return st


def _kish_is_page(u):
    """是不是站点播放页（壳拿到这种地址只能当网页，当视频播必黑屏）。"""
    s = str(u or '')
    if not s:
        return False
    if _KISH_PAGE_RE.match(s):
        return True
    try:
        host = (urllib.parse.urlsplit(s).hostname or '').lower()
    except Exception:
        return False
    return host in _KISH_PAGE_HOSTS


def kish_fix_url(r):
    """把播放地址里的中文/空格做百分号编码。

    实测河豚「B超高清」回的是
    `https://c1.rrcdnbf5.com/video/nasikaquansukuangbiao/第01集/index.m3u8`，
    原样交给播放器会 UnicodeEncodeError 或 404；橘汁也有同样的中文目录。
    只对非 ASCII 字符动手，已编码的 %xx 不受影响。
    """
    if not isinstance(r, dict):
        return r
    u = r.get('url')
    if not isinstance(u, str) or not u or u.isascii():
        return r
    try:
        g = dict(r)
        g['url'] = urllib.parse.quote(
            u, safe="/:?&=#%@!$'()*+,;[]~-._")
        return g
    except Exception:
        return r


def kish_play_ok(r):
    """播放结果是否可用。

    接受：
      - http(s) / magnet / proxy 直链
      - jx=1 且带 url（交给壳解析）
      - 源自己声明 parse>=1 的地址（壳会去嗅探）
    拒绝：
      - 空 url、非 URL 令牌
      - parse=0 但地址是网页：壳拿网页当视频流，只能黑屏，不如换源
    不把「空 url」或仅有 parse=1 无地址当成成功，避免阻断同集换源。
    """
    if not isinstance(r, dict):
        return False
    u = str(r.get('url') or '').strip()
    if not u:
        return False
    if u.startswith('proxy://') or u.startswith('magnet:'):
        return True
    if u.startswith('http://') or u.startswith('https://'):
        # 网页地址（.html/.php/播放页）不管是 parse=0 还是 parse=1，都当「最后手段」：
        # 先让同集换源去找真直链，全部线路都是网页时才回落到它（parse 置 1 交壳嗅探）。
        if _kish_is_page(u):
            return False
        return True
    try:
        return bool(int(r.get('jx') or 0))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 可播性 + 广告切片启发式（仅用于 1080 兜底筛选；不保证无烧录字幕）
# 返回: (ok: bool, score: int, reason: str)
#   score 越高越优先；ok=False 表示建议丢弃
# ---------------------------------------------------------------------------
_KISH_PLAYABLE_CACHE = {}
_KISH_PLAYABLE_LOCK = threading.Lock()
_KISH_AD_HOST_HINT = (
    'ad.', 'ads.', 'advert', 'adsystem', 'adserver', 'adcdn',
    'miaozhen', 'scorecardresearch', 'doubleclick', 'googlesyndication',
    'ubixio', 'admaster', 'tanx.com', 'lianmeng.',
)


def kish_probe_playable(url, timeout=1.2):
    """探测直链是否可播，并对 m3u8 做广告切片启发式打分。

    - 非 http(s)：不探，返回 (True, 50, 'skip') —— 交由播放阶段处理
    - 失败/空响应/非媒体：ok=False
    - m3u8：有分片且广告特征不重 → ok=True，score 受 DISCONTINUITY/短分片影响
    """
    u = str(url or '').strip()
    if not u:
        return False, 0, 'empty'
    if u.startswith('magnet:'):
        return True, 40, 'magnet'
    if not (u.startswith('http://') or u.startswith('https://')):
        return True, 50, 'token'

    now = time.time()
    with _KISH_PLAYABLE_LOCK:
        hit = _KISH_PLAYABLE_CACHE.get(u)
        if hit and now - hit[0] < 1800:
            return hit[1], hit[2], hit[3]

    ok, score, reason = False, 0, 'fail'
    try:
        st, body = http(u, headers={
            'User-Agent': UA_WEB,
            'Accept': '*/*',
            'Accept-Encoding': 'identity',
            'Range': 'bytes=0-131071',
        }, timeout=timeout, retries=1)
        if not body or len(body) < 16:
            ok, score, reason = False, 0, 'empty_body'
        elif body[:7] == b'#EXTM3U' or b'#EXTM3U' in body[:120]:
            text = body.decode('utf-8', 'replace')
            lines = text.splitlines()
            extinf = 0
            short_seg = 0
            disc = 0
            segs = []
            ad_host = 0
            for ln in lines:
                s = ln.strip()
                if not s:
                    continue
                if s.startswith('#EXTINF:'):
                    extinf += 1
                    try:
                        dur = float(s.split(':', 1)[1].split(',')[0])
                        if dur > 0 and dur < 3.0:
                            short_seg += 1
                    except Exception:
                        pass
                elif s.startswith('#EXT-X-DISCONTINUITY'):
                    disc += 1
                elif not s.startswith('#'):
                    segs.append(s)
                    try:
                        host = (urllib.parse.urlparse(
                            s if s.startswith('http') else urllib.parse.urljoin(u, s)
                        ).hostname or '').lower()
                        if any(h in host for h in _KISH_AD_HOST_HINT):
                            ad_host += 1
                    except Exception:
                        pass
            if extinf <= 0 and not segs:
                ok, score, reason = False, 0, 'm3u8_no_seg'
            else:
                # 基础分
                score = 80
                # 片头短分片 / 间断过多 → 降权（疑似广告切片）
                if disc >= 3:
                    score -= min(40, disc * 8)
                if short_seg >= 4:
                    score -= min(30, short_seg * 4)
                if ad_host:
                    score -= min(50, ad_host * 15)
                # 几乎全是短分片 → 直接判不可用
                if extinf >= 6 and short_seg >= max(4, int(extinf * 0.5)):
                    ok, score, reason = False, max(0, score), 'ad_slices'
                elif score < 25:
                    ok, score, reason = False, score, 'ad_score'
                else:
                    ok, reason = True, 'm3u8'
        elif body[:4] == b'\x1aE\xdf\xa3':  # EBML / MKV
            ok, score, reason = True, 75, 'mkv'
        elif b'ftyp' in body[:64] or body[4:8] == b'ftyp':
            ok, score, reason = True, 75, 'mp4'
        elif len(body) >= 4096:
            # 有一定体积的二进制，姑且认为可拉流
            ok, score, reason = True, 55, 'binary'
        else:
            ok, score, reason = False, 0, 'unknown'
    except Exception:
        ok, score, reason = False, 0, 'error'

    with _KISH_PLAYABLE_LOCK:
        if len(_KISH_PLAYABLE_CACHE) > 800:
            # 简单清理一半
            for i, k in enumerate(list(_KISH_PLAYABLE_CACHE.keys())):
                if i >= 400:
                    break
                _KISH_PLAYABLE_CACHE.pop(k, None)
        _KISH_PLAYABLE_CACHE[u] = (now, ok, score, reason)
    return ok, score, reason


def kish_sample_url_from_eps(eps):
    """从线路剧集里取一个可探测的 http(s) 样例地址（播放码本身是 URL 时）。"""
    for _nm, pid in (eps or [])[:3]:
        p = str(pid or '').strip()
        # 聚合编码 k2... 无法在此反解出原始 URL，跳过
        if p.startswith('k2') or p.startswith('k1'):
            continue
        # 常见：直接 URL / 解密后仍是 URL
        if p.startswith('http://') or p.startswith('https://'):
            return p
        # 部分源 play id 形如 name$url
        if 'http://' in p or 'https://' in p:
            for part in re.split(r'[$#]', p):
                part = part.strip()
                if part.startswith('http://') or part.startswith('https://'):
                    return part
    return ''
# ==================== 画质探测与播放校验工具 END ====================


# ==================== 河豚4K 一级源 ht BEGIN ====================
class HT4KSpider(_BaseSpider):
    """河豚4K 专用实现（河豚4K2 协议）：protobuf + RSA + AES，纯标准库。"""
    NAME = '河豚4K'
    CFG = {
        'app_name': '河豚',
        'public_key': (
            'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCr8SzZhjYy+rsya1K09t8d2K50'
            'pWFoBkgUqMpKOiW+3IEVKd4eTdvg9RSOjQ82kypL6R9BnsmrS1V8s4PVDwjQbUtY'
            'hTPPC9Hz16qY7rpD6m0d2vr09/UpWQ5uOy9PR0QTrsioveZ+DIe9jc3C+zBCu/kZ'
            'SY/R8stwJoiitki3gwIDAQAB'),
        'safe_code': 'V04XQZNYRWN6T0JODZFIAG5CTZB3PT0=',
        'data_iv': 'OC1A06E197EF10CF3F6058CA7A803B5E',
        'pkg': 'com.djlxxl.xcydzkj',
        'boot': 'https://az1-1456692500.cos.ap-guangzhou.myqcloud.com/az1.txt',
        'v_name': '7.0.0.2',
        'device_key': 'ed5fdsgucxumegqa',
    }
    UA = 'okhttp/3.12.1'
    MEDIA_RE = re.compile(
        r'\.(?:mp4|m3u8|flv|mkv|avi|ts|mov|mpd|m4a|wmv)(?:\?.*)?$', re.I)
    _shared = {'host': '', 'key': '', 'ts': 0}

    def __init__(self):
        self._host = ''
        self._dyn_key = ''

    def getName(self):
        return self.NAME

    def init(self, extend=''):
        self._host = ''
        self._dyn_key = ''

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        return bool(self.MEDIA_RE.search(str(url or '')))

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return None

    @staticmethod
    def _varint(n):
        out = bytearray()
        n = int(n)
        while True:
            b = n & 0x7F
            n >>= 7
            out.append((b | 0x80) if n else b)
            if not n:
                return bytes(out)

    def _p_int(self, field, value):
        return self._varint(field << 3) + self._varint(value)

    def _p_bytes(self, field, value):
        if isinstance(value, str):
            value = value.encode('utf-8')
        return self._varint((field << 3) | 2) + self._varint(len(value)) + value

    @staticmethod
    def _read_varint(buf, pos):
        n = shift = 0
        while pos < len(buf):
            b = buf[pos]
            pos += 1
            n |= (b & 0x7F) << shift
            if not (b & 0x80):
                return n, pos
            shift += 7
        raise ValueError('bad varint')

    def _pb(self, buf):
        out, pos, n = {}, 0, len(buf or b'')
        while pos < n:
            tag, pos = self._read_varint(buf, pos)
            field, wire = tag >> 3, tag & 7
            if wire == 0:
                val, pos = self._read_varint(buf, pos)
            elif wire == 2:
                ln, pos = self._read_varint(buf, pos)
                val = buf[pos:pos + ln]
                pos += ln
            elif wire == 1:
                val = buf[pos:pos + 8]
                pos += 8
            elif wire == 5:
                val = buf[pos:pos + 4]
                pos += 4
            else:
                break
            out.setdefault(field, []).append(val)
        return out

    @staticmethod
    def _one(fields, num, default=None):
        v = fields.get(num)
        return v[0] if v else default

    @staticmethod
    def _s(value, default=''):
        if value is None:
            return default
        if isinstance(value, bytes):
            return value.decode('utf-8', 'ignore')
        return str(value)

    @staticmethod
    def _text(value):
        """简介里带 <p>/<br> 与实体，直接丢给壳会显示成一堆标签。"""
        txt = HT4KSpider._s(value)
        if not txt:
            return ''
        txt = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', '', txt)
        txt = re.sub(r'(?i)<br\s*/?>|</p>|</div>', '\n', txt)
        txt = re.sub(r'<[^>]+>', '', txt)
        txt = (txt.replace('&nbsp;', ' ').replace('&amp;', '&')
                  .replace('&lt;', '<').replace('&gt;', '>')
                  .replace('&quot;', '"').replace('&#39;', "'"))
        return re.sub(r'[ \t]+', ' ', txt).strip()

    @staticmethod
    def _rand(n):
        raw = re.sub(r'[^A-Za-z0-9]', '', base64.b64encode(os.urandom(n)).decode())
        return (raw + 'A' * n)[:max(1, n - 1)] + '='

    def _bin(self, url, method='GET', body=None, headers=None, timeout=15):
        hdr = {'User-Agent': self.UA}
        if headers:
            hdr.update(headers)
        _st, data = http(url, method, hdr, body, timeout=timeout, retries=2)
        return data or b''

    def _rsa(self, text, pub_b64):
        try:
            der = base64.b64decode(pub_b64)

            def tlv(buf, pos):
                tag = buf[pos]
                pos += 1
                ln = buf[pos]
                pos += 1
                if ln & 0x80:
                    cnt = ln & 0x7F
                    ln = int.from_bytes(buf[pos:pos + cnt], 'big')
                    pos += cnt
                return tag, buf[pos:pos + ln], pos + ln

            _, body, _ = tlv(der, 0)
            _, _, p = tlv(body, 0)
            _, bitstr, _ = tlv(body, p)
            _, rsa_seq, _ = tlv(bitstr[1:], 0)
            _, n_raw, p2 = tlv(rsa_seq, 0)
            _, e_raw, _ = tlv(rsa_seq, p2)
            n = int.from_bytes(n_raw, 'big')
            e = int.from_bytes(e_raw, 'big')
            k = (n.bit_length() + 7) // 8
            msg = text.encode('utf-8')
            if len(msg) > k - 11:
                return ''
            ps = bytearray()
            while len(ps) < k - 3 - len(msg):
                chunk = os.urandom(k - 3 - len(msg) - len(ps))
                ps += bytes(b for b in chunk if b)
            block = b'\x00\x02' + bytes(ps) + b'\x00' + msg
            return base64.b64encode(
                pow(int.from_bytes(block, 'big'), e, n).to_bytes(k, 'big')).decode()
        except Exception:
            return ''

    def _aes_ecb(self, data, key):
        # safe_code / data_iv 都是 32 字节，必须按 AES-256 走完整密钥。
        # 早期这里把密钥截成 16 字节，服务端解不开 → 所有 protobuf 接口恒空。
        try:
            key_b = key if isinstance(key, (bytes, bytearray)) else str(key).encode('ascii')
            if len(key_b) not in (16, 24, 32):
                key_b = (key_b[:16] if len(key_b) >= 16 else key_b.ljust(16, b'\0'))
            rk = _expand_key(key_b)
            n = 16 - len(data) % 16
            data = data + bytes([n]) * n
            out = bytearray()
            for i in range(0, len(data), 16):
                out += _enc_block(list(data[i:i + 16]), rk)
            return bytes(out)
        except Exception:
            return b''

    def _aes_cbc_hex(self, data, key):
        try:
            key_b = key if isinstance(key, (bytes, bytearray)) else str(key).encode('ascii')
            if len(key_b) not in (16, 24, 32):
                key_b = (key_b[:16] if len(key_b) >= 16 else key_b.ljust(16, b'\0'))
            return cbc_encrypt(key_b, key_b[:16], data, pad=True).hex()
        except Exception:
            return ''

    def _ensure(self):
        if self._host:
            return True
        cache = HT4KSpider._shared
        if cache['host'] and time.time() - cache['ts'] < 600:
            self._host = cache['host']
            self._dyn_key = cache['key']
            return True
        raw = self._bin(self.CFG['boot'], timeout=10)
        try:
            host = self._s(json.loads(raw.decode('utf-8')).get('domain')).rstrip('/')
        except Exception:
            host = ''
        if not host:
            return False
        self._host = host
        try:
            ts = int(time.time() * 1000)
            r = self._rand(16)
            body = (self._p_int(1, ts)
                    + self._p_bytes(2, self._rsa(str(ts) + r, self.CFG['public_key']))
                    + self._p_bytes(3, self._rand(16))
                    + self._p_bytes(4, r)
                    + self._p_bytes(5, self._rand(16)))
            resp = self._bin(self._host + '/api/v5/find/app/zone', 'POST', body,
                             self._headers(True, True), 12)
            zone = self._pb(self._one(self._pb(resp), 3, b'') or b'')
            self._dyn_key = ''.join(self._s(self._one(zone, i)) for i in (2, 3, 4, 5))
        except Exception:
            self._dyn_key = ''
        cache.update({'host': self._host, 'key': self._dyn_key, 'ts': time.time()})
        return True

    def _headers(self, protobuf=True, no_sig=False):
        ts = int(time.time() * 1000)
        r = self._rand(16)
        uid = uuid.uuid4().hex.upper()
        vapp = self.CFG['v_name'].replace('.', '')
        device = {
            'country': 'CN', 'vName': self.CFG['v_name'], 'cpuId': 'MT6893Z%2FCZA',
            'young': 0, 'facturer': 'Xiaomi', 'pkg': self.CFG['pkg'], 'uuid': uid,
            'resolution': '1080x2272', 'mac': '02%3A00%3A00%3A00%3A00%3A00',
            'abid': '397', 'model': 'M2012K11AC', 'plat': 'android', 'udid': uid,
            'dpi': '440', 'net': '1', 'lang': 'zh', 'brand': 'Xiaomi',
            'density': '2.75', 'appName': self.CFG['app_name'], 'cpu': 'arm64-v8a',
            'chid': '10000', 'carrier': '%E8%81%94%E9%80%9A', '_vOsCode': 30,
            'vOs': '11', 'v': 1, 'tenantId': '', 'vApp': vapp, 'device': 0,
            'androidID': uid.lower()[:16],
        }
        pk = self.CFG['public_key'] if no_sig else (self._dyn_key or self.CFG['public_key'])
        device['sig'] = self._rsa(str(ts) + r + vapp, pk)
        device['random_str'] = r
        device['timestamp'] = ts
        sig = base64.b64encode(self._aes_ecb(
            (str(ts) + r).encode('utf-8'), self.CFG['data_iv'].encode('ascii'))).decode()
        device['sig2'], device['sig3'] = sig[:8], sig[8:]
        params = self._aes_cbc_hex(
            json.dumps(device, separators=(',', ':')).encode('utf-8'),
            self.CFG['device_key'])
        return {
            'User-Agent': self.UA,
            'Accept': 'application/x-protobuf' if protobuf else 'application/json',
            'Content-Type': (
                'application/x-protobuf' if protobuf
                else 'application/json; charset=utf-8'),
            'publicParams': '{"paramsData":"%s"}' % params,
        }

    def _secure(self, params):
        ts = int(time.time() * 1000)
        r = self._rand(8)
        fake = self._rand(20)
        query = '&'.join(
            '%s=%s' % (k, v) for k, v in params.items()
            if v is not None and str(v) != '')
        enc = r + base64.b64encode(self._aes_ecb(
            (query + str(ts)).encode('utf-8'),
            self.CFG['safe_code'].encode('ascii'))).decode()
        return (self._p_bytes(1, enc[:20]) + self._p_bytes(2, enc[20:])
                + self._p_bytes(3, fake) + self._p_int(4, ts) + self._p_bytes(5, r))

    def _api(self, path, params, retry=True):
        if not self._ensure():
            return {}
        try:
            outer = self._pb(self._bin(
                self._host + path, 'POST', self._secure(params),
                self._headers(True), 15))
            msg = self._s(self._one(outer, 2))
            data = self._pb(self._one(outer, 3, b'') or b'')
            if data:
                return data
            if retry and any(x in msg for x in ('RSA', '签名', '过期')):
                HT4KSpider._shared.update({'host': '', 'key': '', 'ts': 0})
                self._host = self._dyn_key = ''
                return self._api(path, params, False)
            return data
        except Exception:
            return {}

    def _json(self, path):
        if not self._ensure():
            return {}
        try:
            raw = self._bin(self._host + path, 'GET', None, self._headers(False), 12)
            return json.loads(raw.decode('utf-8', 'ignore'))
        except Exception:
            return {}

    def _cover(self, raw):
        if not isinstance(raw, bytes) or not raw:
            return ''
        try:
            f = self._pb(raw)
        except Exception:
            return ''
        for num in (2, 1):
            url = self._s(self._one(f, num))
            if url.startswith('http') and '$' not in url and len(url) < 300:
                if re.search(r'\.(?:jpe?g|png|webp|gif|bmp|avif)(?:\?|$)', url, re.I) or 'img' in url:
                    return url
        return ''

    def _vod(self, raw):
        f = self._pb(raw)
        name = self._s(self._one(f, 5))
        if not name:
            return None
        # 字段 15 是「大类,小类」，只留最细的那层做 type_name
        kind = self._s(self._one(f, 15)).split(',')[-1].strip()
        return {
            'vod_id': self._s(self._one(f, 3)),
            'vod_name': name,
            'vod_pic': self._cover(self._one(f, 2)),
            'vod_remarks': self._s(self._one(f, 13)),
            'vod_year': self._s(self._one(f, 14)),
            'vod_area': self._s(self._one(f, 1)),
            'type_name': kind,
        }

    def _list(self, fields):
        out, seen = [], set()
        for raw in fields.get(1, []) or []:
            try:
                item = self._vod(raw)
            except Exception:
                continue
            if not item or not item['vod_id'] or item['vod_id'] in seen:
                continue
            seen.add(item['vod_id'])
            out.append(item)
        return out

    def homeContent(self, filter):
        try:
            cats = []
            data = self._json('/api/v3/drama/getCategory?orderBy=type_id')
            for item in as_list(data.get('data')):
                if not item.get('id') or item.get('name') == '公告':
                    continue
                cats.append({
                    'type_id': self._s(item.get('id')),
                    'type_name': self._s(item.get('name')),
                })
            if not cats:
                cats = [
                    {'type_id': '21', 'type_name': '电影'},
                    {'type_id': '22', 'type_name': '剧集'},
                    {'type_id': '25', 'type_name': '动漫'},
                    {'type_id': '26', 'type_name': '综艺'},
                    {'type_id': '27', 'type_name': '短剧'},
                    {'type_id': '28', 'type_name': '漫剧'},
                    {'type_id': '29', 'type_name': '直播'},
                    {'type_id': '30', 'type_name': '纪录片'},
                ]
            return {'class': cats, 'filters': self._filters(cats)}
        except Exception:
            return {'class': [], 'filters': {}}

    @staticmethod
    def _opt(name, values):
        return {'key': name, 'name': name,
                'value': [{'n': '全部', 'v': ''}] +
                         [{'n': v, 'v': v} for v in values]}

    def _filters(self, cats):
        """站点的筛选维度是固定的几组中文取值，原样回传即可被 _secure 拼进查询。"""
        order = self._opt('排序', ['最新', '最热', '评分'])
        cls = self._opt('类型', ['动作', '喜剧', '爱情', '科幻', '恐怖', '剧情', '战争',
                                '犯罪', '悬疑', '动画', '纪录片', '伦理', '冒险', '奇幻'])
        area = self._opt('地区', ['内地', '香港', '台湾', '美国', '韩国', '日本', '泰国',
                                 '印度', '法国', '英国', '德国', '其他'])
        year = self._opt('年份', [str(y) for y in range(2026, 2014, -1)])
        lang = self._opt('语言', ['国语', '英语', '日语', '韩语', '粤语', '法语'])
        out = {}
        for c in cats:
            tid = c['type_id']
            if tid == '29':                    # 直播没有筛选维度
                out[tid] = []
            elif tid in ('27', '28'):          # 短剧 / 漫剧：站点的语言维度无数据
                out[tid] = [cls, area, year, order]
            else:
                out[tid] = [cls, area, year, lang, order]
        return out

    def homeVideoContent(self):
        try:
            f = self._api('/api/proto/v5/drama/category', {
                'pagesize': '21', 'typeId1': '21', 'page': '1',
                'vodOrderBy': '最热', 'vodArea': '', 'vodLang': '',
                'vodClass': '', 'vodYear': '',
            })
            return {'list': self._list(f)}
        except Exception:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            page = page_of(pg)
            ext = extend if isinstance(extend, dict) else {}
            items = self._list(self._api('/api/proto/v5/drama/category', {
                'pagesize': '21', 'typeId1': self._s(tid), 'page': str(page),
                'vodOrderBy': self._s(ext.get('排序')) or '最新',
                'vodArea': self._s(ext.get('地区')),
                'vodLang': self._s(ext.get('语言')),
                'vodClass': self._s(ext.get('类型')),
                'vodYear': self._s(ext.get('年份')),
            }))
            pagecount = page + 1 if len(items) >= 21 else page
            return {
                'list': items, 'page': page, 'pagecount': pagecount,
                'limit': 21, 'total': pagecount * 21 if items else 0,
            }
        except Exception:
            return {'list': [], 'page': 1, 'pagecount': 1, 'limit': 21, 'total': 0}

    def detailContent(self, ids):
        try:
            vid = self._s(ids[0] if isinstance(ids, (list, tuple)) else ids).strip()
            f = self._api('/api/proto/v5/drama/getDetail', {'id': vid})
            if not f:
                return {'list': []}
            groups, order = {}, []
            for raw in f.get(29, []) or []:
                try:
                    ep = self._pb(raw)
                except Exception:
                    continue
                path = self._s(self._one(ep, 4))
                if not path:
                    continue
                title = (self._s(self._one(ep, 3)) or self._s(self._one(ep, 2)) or '第1集')
                source = self._s(self._one(ep, 9))
                quality = self._s(self._one(ep, 10)) or source or '未知'
                name = ('%s (%s)' % (quality, source)
                        if source and quality != source else quality)
                name = name.replace('$', '').replace('#', '')
                title = title.replace('$', '').replace('#', '')
                if self.MEDIA_RE.search(path):
                    token = path
                else:
                    token = base64.urlsafe_b64encode(
                        ('%s\n%s' % (source, path)).encode('utf-8')).decode().rstrip('=')
                if name not in groups:
                    groups[name] = []
                    order.append(name)
                groups[name].append('%s$%s' % (title, token))

            def rank(nm):
                low = nm.lower()
                if '4k' in low:
                    return 0
                if '蓝光' in nm:
                    return 1
                if '超清' in nm or '高清' in nm:
                    return 2
                return 3

            names = sorted(order, key=lambda x: (rank(x), order.index(x))) if groups else []
            return {'list': [{
                'vod_id': vid,
                'vod_name': self._s(self._one(f, 9)),
                'vod_pic': self._cover(self._one(f, 2)),
                'vod_actor': self._s(self._one(f, 25)),
                'vod_director': self._s(self._one(f, 12)),
                'vod_area': self._s(self._one(f, 1)),
                'vod_year': self._s(self._one(f, 18)),
                'vod_remarks': self._s(self._one(f, 26)),
                'vod_content': self._text(self._one(f, 6)),
                'vod_play_from': '$$$'.join(names),
                'vod_play_url': '$$$'.join('#'.join(groups[n]) for n in names),
            }]}
        except Exception:
            return {'list': []}

    def searchContent(self, key, quick=False, pg='1'):
        try:
            page = page_of(pg)
            items = self._list(self._api('/api/proto/v5/drama/search', {
                'searchKeys': self._s(key), 'page': str(page), 'pagesize': '21',
            }))
            return {
                'list': items, 'page': page,
                'pagecount': page + 1 if len(items) >= 21 else page,
            }
        except Exception:
            return {'list': [], 'page': 1, 'pagecount': 1}

    def playerContent(self, flag, id, vipFlags=None):
        try:
            vid = self._s(id).strip()
            if self.MEDIA_RE.search(vid):
                return {'parse': 0, 'url': vid, 'header': {'User-Agent': self.UA}}
            raw, pad = vid, '=' * (-len(vid) % 4)
            try:
                plain = base64.urlsafe_b64decode(raw + pad).decode('utf-8', 'ignore')
            except Exception:
                try:
                    plain = base64.b64decode(raw + pad).decode('utf-8', 'ignore')
                except Exception:
                    return {'parse': 1, 'url': vid, 'header': {'User-Agent': self.UA}}
            if '\n' not in plain:
                return {'parse': 1, 'url': vid, 'header': {'User-Agent': self.UA}}
            source, path = plain.split('\n', 1)
            f = self._api('/api/proto/v5/videoUsableUrl', {
                'vodPlayFrom': source, 'playUrl': path,
            })
            url = self._s(self._one(f, 1))
            if not url:
                return {'parse': 1, 'url': vid, 'header': {'User-Agent': self.UA}}
            header = {'User-Agent': self.UA}
            for raw_h in f.get(6, []) or []:
                try:
                    h = self._pb(raw_h)
                except Exception:
                    continue
                k, v = self._s(self._one(h, 1)), self._s(self._one(h, 2))
                if k and k.lower() not in (
                        'user-agent', 'host', 'content-length', 'accept-encoding'):
                    header[k] = v
            return {'parse': 0, 'url': url, 'header': header}
        except Exception:
            return {'parse': 1, 'url': self._s(id), 'header': {'User-Agent': self.UA}}
# ==================== 河豚4K 一级源 ht END ====================



# ==================== 片帝 一级源 pd BEGIN ====================
class PDSpider(_BaseSpider):
    """片帝4K：纯标准库 + 域名池 + 官方/4K优先 + resolve-line + 中继兜底。"""
    NAME = '片帝4K'
    SIGN_KEY = '8b9a908a05eac640e1ee06f52acaa741bfe4ba9e004eeffdbeb635e532e06666'
    UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36')
    CLIENT = {
        'x-ai-movie-client-name': 'movie-search-frontend',
        'x-ai-movie-client-version': '1.0.0',
        'x-ai-movie-build-version':
            'dongpiandi-v2026.10.04.1-episode-resume-efd9a7f2e87e-web',
        'x-ai-movie-protocol-version': '2026-07-05.library-v2.playback-v1',
    }
    KINDS = [('all', '全部'), ('movie', '电影'), ('series', '剧集'),
             ('short_drama', '短剧'), ('anime', '动漫'), ('variety', '综艺')]
    WINDOWS = [('day', '日榜'), ('week', '周榜'), ('month', '月榜'), ('total', '总榜')]
    POOL = ['https://dongpian%d.com' % n for n in [17] + [i for i in range(1, 31) if i != 17]]
    RELAY = 'https://ag.fakage.com/pdline'
    _host = {'url': '', 'ok_at': 0}
    _down = {}

    def __init__(self):
        self.host = self.POOL[0]
        self.cookies = {}

    def init(self, extend=''):
        try:
            if isinstance(extend, str) and extend.strip().startswith('{'):
                cfg = json.loads(extend)
                if cfg.get('host'):
                    self.host = str(cfg['host']).rstrip('/')
        except Exception:
            pass

    def getName(self):
        return self.NAME

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return None

    def _hosts(self):
        now = time.time()
        cur = self._host.get('url') or self.host
        alive = [h for h in self.POOL if self._down.get(h, 0) <= now]
        down = [h for h in self.POOL if self._down.get(h, 0) > now]
        if cur in alive and now - self._host.get('ok_at', 0) < 900:
            return [cur] + [h for h in alive if h != cur] + down
        return alive + down

    def _hit(self, host, method, path_query, body, timeout):
        """对单个域名签一次名并发请求，返回 (status, raw)。"""
        ts = str(int(time.time() * 1000))
        nonce = secrets.token_hex(16)
        msg = '%s\n%s\n%s\n%s' % (method, path_query, ts, nonce)
        sig = hmac.new(self.SIGN_KEY.encode(), msg.encode(), hashlib.sha256).hexdigest()
        hdr = {'User-Agent': self.UA, 'Accept': 'application/json'}
        hdr.update(self.CLIENT)
        hdr['x-ai-movie-timestamp'] = ts
        hdr['x-ai-movie-nonce'] = nonce
        hdr['x-ai-movie-signature'] = sig
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
            hdr['Content-Type'] = 'application/json'
        return http(host + path_query, method, hdr, data, timeout=timeout, retries=1)

    def _race(self, method, path_query, body=None, timeout=2.0, n=4):
        """域名池并发抢答：同时打 n 个域名，用最先返回的那份。

        片帝的 30 个镜像不是同一台机器：实测同一关键词并发打
        dongpian17 / 1 / 2，耗时能差到 0.74s vs 3.63s，还有 0 字节直接失败的。
        原来串行试（且每个等满超时），一次搜索 p50 1.13s、p90 3.71s、最坏
        4.56s —— 聚合侧 1.6~2.0s 就收工，于是「搜繁花有片帝、搜琅琊榜没有」。
        并发之后最快的那份 p50 0.8s、20 轮最慢 1.55s，落进预算的概率高得多。
        """
        hosts = self._hosts()[:max(1, n)]
        if len(hosts) <= 1:
            return self._call(method, path_query, body, timeout)
        out = {'data': None, 'done': False}
        lock = threading.Lock()

        def run(host):
            try:
                st, raw = self._hit(host, method, path_query, body, timeout)
            except Exception:
                PDSpider._down[host] = time.time() + 300
                return
            if not (200 <= st < 300 and raw):
                # 4xx 是签名/参数问题，换域名也一样，别再拉黑整池
                if not (400 <= st < 500):
                    PDSpider._down[host] = time.time() + 300
                return
            try:
                data = loads(raw.decode('utf-8', 'replace'))
            except Exception:
                return
            with lock:
                if out['data'] is not None:
                    return          # 已经有人先到，这份丢弃
                out['data'] = data
                PDSpider._host.update({'url': host, 'ok_at': time.time()})
                self.host = host
                PDSpider._down.pop(host, None)

        ths = []
        for h in hosts:
            th = threading.Thread(target=run, args=(h,))
            th.daemon = True
            th.start()
            ths.append(th)
        deadline = time.time() + timeout + 0.25
        while time.time() < deadline:
            with lock:
                if out['data'] is not None:
                    return out['data']
            if not any(t.is_alive() for t in ths):
                break
            time.sleep(0.01)
        with lock:
            return out['data'] or {}

    def _call(self, method, path_query, body=None, timeout=10):
        # 短超时调用（搜索这种首屏路径）只试 2 个 host、每个都用短超时：
        # 4 个 host × (10+6+6+6)s 最坏能把一次搜索拖到半分钟，而聚合侧
        # 1.6~2.0s 就收工了，拖到最后的结果根本没人要，只是占着线程。
        hosts = self._hosts()[:2 if timeout <= 5 else 4]
        for i, host in enumerate(hosts):
            st, raw = self._hit(host, method, path_query, body,
                                timeout if i == 0 else min(6, timeout))
            if 200 <= st < 300 and raw:
                PDSpider._host.update({'url': host, 'ok_at': time.time()})
                self.host = host
                PDSpider._down.pop(host, None)
                return loads(raw.decode('utf-8', 'replace'))
            if 400 <= st < 500:
                break
            PDSpider._down[host] = time.time() + 300
        return {}

    def _get(self, pq):
        return self._call('GET', pq)

    def _post(self, pq, obj):
        return self._call('POST', pq, obj)

    def _card(self, c):
        if not isinstance(c, dict) or not c.get('id'):
            return None
        pic = c.get('poster_url') or c.get('backdrop_url') or ''
        if str(pic).startswith('//'):
            pic = 'https:' + pic
        return {
            'vod_id': str(c.get('id')),
            'vod_name': clean_name(c.get('title') or c.get('normalized_title')),
            'vod_pic': pic,
            'vod_remarks': clean_name(c.get('remarks') or c.get('badge') or ''),
            'vod_year': str(c.get('year') or ''),
            'vod_area': clean_name(c.get('area') or ''),
        }

    def _cards(self, arr):
        out = []
        for c in as_list(arr):
            v = self._card(c)
            if v and v.get('vod_name'):
                out.append(v)
        return out

    def homeContent(self, filter):
        classes = [{'type_id': k, 'type_name': n} for k, n in self.KINDS]
        filters = {k: [{'key': 'window', 'name': '榜单',
                        'value': [{'n': n, 'v': w} for w, n in self.WINDOWS]}]
                   for k, _ in self.KINDS}
        return {'class': classes, 'filters': filters}

    def homeVideoContent(self):
        j = self._get('/v1/feed/home?scope=public&mode=preview&sections=3&cards=12')
        best = []
        for s in as_list(j.get('sections')):
            cards = self._cards(s.get('cards'))
            if s.get('id') == 'feed_sec_everyone_watching' or s.get('type') == 'trend':
                if cards:
                    return {'list': cards}
            if not best and cards:
                best = cards
        return {'list': best}

    def categoryContent(self, tid, pg, filter, extend):
        ext = extend if isinstance(extend, dict) else {}
        window = str(ext.get('window') or 'day')
        page = page_of(pg)
        q = '?sort=trending&window=%s&page=%d&limit=20' % (urllib.parse.quote(window), page)
        if tid and tid != 'all':
            q += '&kind=' + urllib.parse.quote(str(tid))
        j = self._get('/v1/browse/catalog' + q)
        if not j:                       # 域名池全挂，别让上层当成「这一页没片」缓存
            return {'page': page, 'pagecount': page, 'limit': 0,
                    'total': 0, 'list': [], '_error': 'empty'}
        lst = self._cards(j.get('cards'))
        p = as_dict(j.get('pagination'))
        more = bool(p.get('has_more'))
        try:
            total = int(p.get('total') or 0)
        except Exception:
            total = 0
        pagecount = page + 1 if more else page
        if total:
            pagecount = max(page, (total + 19) // 20)
        return {'page': page, 'pagecount': pagecount, 'limit': 20,
                'total': total or len(lst), 'list': lst}

    def searchContent(self, key, quick=False, pg='1'):
        page = page_of(pg)
        # 并发抢答 + 2.0s 上限：聚合侧为片帝把预算顺延到 2.5s（其他源仍 1.6s
        # 软上限就收），串行试探单域名最坏 4.56s，注定有近半轮次里片帝整源消失。
        j = self._race('GET', '/v1/browse/catalog?q=%s&page=%d&limit=20' % (
            urllib.parse.quote(str(key or '')), page), timeout=2.0)
        # _call 全 host 失败时返回 {}，合法响应一定有 cards/pagination。
        # 不打 _error 的话，域名池抖动会被上层当成「片帝确实没这个片」，
        # 空结果按 600s 缓存，用户十分钟内重搜都看不到片帝。
        if not j:
            return {'list': [], 'page': page, '_error': 'empty'}
        return {'list': self._cards(j.get('cards')), 'page': page}

    def _all_eps(self, vid, eps):
        out = list(eps or [])
        offset = len(out)
        for _ in range(20):
            j = self._get('/v1/catalog/%s/episodes?limit=48&offset=%d' % (
                urllib.parse.quote(str(vid)), offset))
            arr = as_list(j.get('episodes'))
            if not arr:
                break
            out.extend(arr)
            if not as_dict(j.get('episode_pagination')).get('has_more'):
                break
            offset += len(arr)
        return out

    @staticmethod
    def _official(ln):
        lab = str(ln.get('label') or '')
        pid = str(ln.get('provider_id') or '').lower()
        return '官方' in lab or pid.startswith('official') or pid.startswith('bytevod')

    # 线路名里带画质的段（4K/1080P/蓝光…）：用户在选线时靠它区分清晰度，
    # 剥掉就全变成「官方S/B/R」，看不出哪条是 4K，和假 4K 判定也对不上。
    _QUAL_RE = re.compile(r'(?i)(4k|2160|1080|720|hdr|蓝光|超清|高清|标清)')

    @staticmethod
    def _short(label):
        s = str(label or '')
        if '官方' in s:
            base = s.split('·')[0].strip()
            segs = [x.strip() for x in base.split('-') if x.strip()]
            name = ''
            for seg in reversed(segs):
                if '官方' in seg:
                    name = seg
                    break
            if not name:
                name = base
            qual = ''
            for seg in segs:
                if '官方' in seg:
                    continue
                if PDSpider._QUAL_RE.search(seg):
                    qual = seg
                    break
            if qual and qual.upper() not in name.upper():
                return qual + '-' + name
            return name
        return clean_name(s) or '线路'

    def detailContent(self, ids):
        vid = str(ids[0] if isinstance(ids, (list, tuple)) and ids else ids or '').strip()
        if not vid:
            return {'list': []}
        j = self._get('/v1/catalog/' + urllib.parse.quote(vid))
        card = as_dict(j.get('card') if isinstance(j.get('card'), dict) else j)
        eps = [e for e in as_list(card.get('episodes')) if isinstance(e, dict)]
        try:
            need = int(card.get('episode_count') or 0)
        except Exception:
            need = 0
        if need > len(eps):
            eps = self._all_eps(vid, eps)
        urls = []
        for i, e in enumerate(eps):
            title = clean_name(e.get('title') or e.get('display_name') or '') or ('第%s集' % (e.get('number') or i + 1))
            tok = str(e.get('token') or '')
            if tok:
                urls.append('%s$%s' % (title, tok))
        vod = self._card(card) or {'vod_id': vid, 'vod_name': self.NAME, 'vod_pic': '', 'vod_remarks': ''}
        vod['vod_id'] = vid
        vod['vod_content'] = clean_name(card.get('description') or card.get('content') or '')
        lines = []
        if eps and eps[0].get('token'):
            r = self._get('/v1/playback/resolve/%s?view=compact' % urllib.parse.quote(str(eps[0]['token'])))
            lines = [x for x in as_list(r.get('line_options')) if isinstance(x, dict)]
        lines = [ln for ln in lines if self._official(ln)]
        lines.sort(key=lambda ln: 0 if '4K' in str(ln.get('label') or '').upper() else 1)
        if lines and urls:
            froms, groups, used = [], [], {}
            for ln in lines:
                lid = str(ln.get('id') or '')
                if not lid:
                    continue
                label = self._short(ln.get('label') or ln.get('provider_id') or '线路')
                if label in used:
                    used[label] += 1
                    label = '%s%d' % (label, used[label])
                else:
                    used[label] = 1
                froms.append(label)
                groups.append('#'.join('%s$%s@@%s' % (u.split('$', 1)[0], u.split('$', 1)[1], lid) for u in urls))
            if froms:
                vod['vod_play_from'] = '$$$'.join(froms)
                vod['vod_play_url'] = '$$$'.join(groups)
                return {'list': [vod]}
        vod['vod_play_from'] = self.NAME
        vod['vod_play_url'] = '#'.join(urls)
        return {'list': [vod]}

    def _resolve_line(self, ticket):
        r = self._post('/v1/playback/resolve-line?view=compact', {'ticket': ticket})
        for c in (r.get('line'), as_dict(r.get('data')).get('line'), r):
            if isinstance(c, dict) and str(c.get('url') or '').startswith('http'):
                return str(c['url'])
        return ''

    def _relay(self, token):
        st, body = http(self.RELAY + '/?token=' + urllib.parse.quote(str(token)),
                        headers={'User-Agent': self.UA}, timeout=20)
        if 200 <= st < 300 and body:
            u = as_dict(loads(body.decode('utf-8', 'replace'))).get('url')
            if isinstance(u, str) and u.startswith('http'):
                return u
        return ''

    def playerContent(self, flag, id, vipFlags=None):
        raw = str(id or '').strip()
        line_id, token = '', raw
        if '@@' in raw:
            token, line_id = raw.split('@@', 1)
        if not token:
            return {'parse': 0, 'url': '', 'header': {'User-Agent': self.UA}}
        j = self._get('/v1/playback/resolve/%s?view=compact' % urllib.parse.quote(token))
        lines = [x for x in as_list(j.get('line_options')) if isinstance(x, dict)]

        def take(ln):
            u = str(ln.get('url') or '')
            if u.startswith('resolve://'):
                return self._resolve_line(u[10:])
            if u.startswith('http'):
                return u
            return ''

        play = ''
        if line_id:
            for ln in lines:
                if str(ln.get('id') or '') == line_id:
                    play = take(ln)
                    break
        if not play and flag and flag != self.NAME:
            for ln in lines:
                if self._short(ln.get('label') or '') == flag or str(ln.get('label') or '') == flag:
                    play = take(ln)
                    if play:
                        break
        if not play:
            official = [ln for ln in lines if self._official(ln)]
            for ln in official + [x for x in lines if x not in official]:
                play = take(ln)
                if play:
                    break
        if not play:
            play = self._relay(token)
        return {'parse': 0, 'url': play or '', 'header': {'User-Agent': self.UA}}
# ==================== 片帝 一级源 pd END ====================



# ==================== 未来4K 一级源 wl BEGIN ====================
class WL4KSpider(_BaseSpider):
    """未来4K：苹果CMS夸克源，轻量备用。ext 可覆写 api / playUrl。"""
    NAME = '未来4K'
    DEFAULT_API = 'http://110.42.66.100:12678/api.php'
    DEFAULT_PARSE = (
        'http://110.42.66.100:5666/api/?key=c31bfd818ac47875ab4922f03834afcc&url=')
    UA = ('Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 '
          '(KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36')
    VIDEO_RE = re.compile(r'\.(m3u8|mp4|flv|mkv|ts|avi)(\?|#|$)', re.I)
    CATS = [('2', '电影'), ('1', '电视剧'), ('9', '动漫'), ('10', '综艺'),
            ('13', '少儿'), ('11', '日韩剧'), ('12', '美剧')]

    def __init__(self):
        self.api = self.DEFAULT_API
        self.parse_api = self.DEFAULT_PARSE

    def getName(self):
        return self.NAME

    def init(self, extend=''):
        try:
            cfg = {}
            if isinstance(extend, dict):
                cfg = extend
            elif isinstance(extend, str) and extend.strip().startswith('{'):
                cfg = json.loads(extend)
            if cfg.get('api'):
                self.api = str(cfg['api']).strip()
            if cfg.get('playUrl') or cfg.get('parse'):
                self.parse_api = str(cfg.get('playUrl') or cfg.get('parse')).strip()
        except Exception:
            pass

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        return bool(self.VIDEO_RE.search(str(url or '')))

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return None

    def _base(self):
        base = (self.api or self.DEFAULT_API).rstrip('/')
        if 'provide/vod' in base:
            return base + '/'
        if base.endswith('api.php') or base.endswith('.php'):
            return base + '/provide/vod/from/kl/'
        return base + '/api.php/provide/vod/from/kl/'

    def _url(self, ac, tid=None, pg=None, wd=None, ids=None):
        q = [('ac', ac)]
        if tid:
            q.append(('t', tid))
        if pg:
            q.append(('pg', str(pg)))
        if wd:
            q.append(('wd', wd))
        if ids:
            q.append(('ids', ids))
        return self._base() + '?' + urllib.parse.urlencode(q)

    # 上游“null 风暴”的静默窗口：实测一次密集请求后整站连续回 `null`
    # （HTTP 200、4 字节，0.07s 就回），间隔 60s 仍不恢复。旧实现每次都
    # sleep 0.5 再要一遍 —— 等于每个调用白付 0.6s，而 wl 在 SEARCH_SLOW 里，
    # 这 0.6s 会直接拖慢每一次搜索的首屏。改成：识别 null → 有限重试 →
    # 连续失败进静默窗口（窗口内一次请求都不发）。
    _NULL_GATE = [0.0]
    _NULL_FAILS = [0]
    _NULL_LOCK = threading.Lock()

    def _j(self, url, timeout=15):
        """取 CMS JSON。返回 dict；上游回 null / 超时（限流、停机）返回 None。

        必须把两种「空」分开：
          - dict + 空 list：上游明确回「没有这部片」—— 不重试、不静默、不算故障；
          - null / 非 JSON / 空体：限流或故障 —— 第一次重试一次（0.45s 加抖动），
            已经失败过就只探一次（0.07s），连续 2 次进 12s 静默窗口。调用方把
            None 转成 `_error`，聚合层据此只缓存 60s，不会把一个暂时抽风的源
            冻结 10 分钟。
        """
        hdr = {'User-Agent': self.UA}
        with self._NULL_LOCK:
            if time.time() < self._NULL_GATE[0]:
                return None
            # 已经失败过一次：只发一个请求探活，别在限流期间反复打（实测
            # 越打恢复越慢），失败就直接进静默窗口
            probe_only = self._NULL_FAILS[0] > 0
        for wait in ((0.0,) if probe_only else (0.0, 0.45)):
            if wait:
                time.sleep(wait + random.uniform(0, 0.2))
            st, txt = http_text(url, headers=hdr, timeout=timeout, retries=2)
            s = (txt or '').strip()
            if not s or s == 'null' or s[:1] not in ('{', '['):
                continue
            data = loads(s)
            if isinstance(data, list):
                data = {'list': data}
            if isinstance(data, dict):
                with self._NULL_LOCK:
                    self._NULL_FAILS[0] = 0
                return data
        with self._NULL_LOCK:
            self._NULL_FAILS[0] += 1
            if self._NULL_FAILS[0] >= 2:
                self._NULL_FAILS[0] = 0
                self._NULL_GATE[0] = time.time() + 12
        return None

    @staticmethod
    def _vod(v):
        if not v:
            return None
        vid = str(v.get('vod_id') or '').strip()
        name = str(v.get('vod_name') or '').strip()
        if not vid or not name:
            return None
        return {
            'vod_id': vid, 'vod_name': name,
            'vod_pic': v.get('vod_pic') or v.get('vod_pic_thumb') or '',
            'vod_remarks': str(v.get('vod_remarks') or '').strip(),
        }

    def _list(self, arr):
        out = []
        for v in as_list(arr):
            item = self._vod(v)
            if item:
                out.append(item)
        return out

    def homeContent(self, filter):
        classes = [{'type_id': t, 'type_name': n} for t, n in self.CATS]
        return {'class': classes, 'filters': {c['type_id']: [] for c in classes}}

    def homeVideoContent(self):
        data = self._j(self._url('detail', pg=1)) or {}
        return {'list': self._list(data.get('list'))[:30]}

    def categoryContent(self, tid, pg, filter, extend):
        page = page_of(pg)
        data = self._j(self._url('detail', tid=tid, pg=page))
        if data is None:
            # 上游抽风：带 _error，聚合层会隔 0.4s 再问一次，且不按「空分类」缓存
            return {'list': [], 'page': page, 'pagecount': page, '_error': 1}
        lst = self._list(data.get('list'))
        try:
            pages = int(str(data.get('pagecount') or 0))
        except Exception:
            pages = 0
        if pages <= 0:
            pages = page + 1 if lst else page
        return {'list': lst, 'page': page, 'pagecount': pages, 'limit': 20, 'total': 0}

    def detailContent(self, ids):
        vid = str(ids[0] if ids else '').split(',')[0].strip()
        if not vid:
            return {'list': []}
        data = self._j(self._url('detail', ids=vid), timeout=20)
        arr = as_list((data or {}).get('list'))
        if not arr:
            return {'list': []}
        info = arr[0]
        vod = self._vod(info) or {}
        vod.update({
            'type_name': str(info.get('type_name') or '').strip(),
            'vod_year': str(info.get('vod_year') or '').strip(),
            'vod_area': str(info.get('vod_area') or '').strip(),
            'vod_actor': str(info.get('vod_actor') or '').strip(),
            'vod_director': str(info.get('vod_director') or '').strip(),
            'vod_content': re.sub(r'<[^>]+>', '', str(info.get('vod_content') or '')).strip(),
        })
        froms, urls = [], []
        names = str(info.get('vod_play_from') or '').split('$$$')
        for i, group in enumerate(str(info.get('vod_play_url') or '').split('$$$')):
            eps = []
            for seg in str(group).split('#'):
                seg = seg.strip()
                if not seg:
                    continue
                if '$' in seg:
                    ep, url = seg.split('$', 1)
                else:
                    ep, url = '正片', seg
                if url:
                    eps.append('%s$%s' % (clean_name(ep) or '正片', url.strip()))
            if eps:
                froms.append(clean_name(names[i] if i < len(names) else '') or ('线路%d' % (i + 1)))
                urls.append('#'.join(eps))
        if not froms:
            return {'list': []}
        vod['vod_play_from'] = '$$$'.join(froms)
        vod['vod_play_url'] = '$$$'.join(urls)
        return {'list': [vod]}

    def searchContent(self, key, quick=False, pg='1'):
        page = page_of(pg)
        data = self._j(self._url('detail', wd=key, pg=page))
        if data is None:
            # 与 categoryContent 同口径：故障不冒充「没搜到」，否则聚合层会把
            # 这个源在结果里缺席这件事缓存 10 分钟
            return {'list': [], 'page': page, '_error': 1}
        return {'list': self._list(data.get('list')), 'page': page}

    @staticmethod
    def _decode_kl(url):
        if not url or not str(url).lower().startswith('kl-'):
            return ''
        raw = str(url)[3:]
        if '?' in raw:
            raw = raw.split('?', 1)[0]
        raw = raw.replace('-', '+').replace('_', '/')
        raw += '=' * ((4 - len(raw) % 4) % 4)
        try:
            txt = base64.b64decode(raw).decode('utf-8', 'ignore').strip()
        except Exception:
            return ''
        return txt if txt.startswith('http') or txt.startswith('//') else ''

    def _resolve(self, url):
        api = (self.parse_api or '').strip()
        if not api:
            return ''
        if 'url=' not in api:
            api += ('&' if '?' in api else '?') + 'url='
        st, txt = http_text(api + urllib.parse.quote(url, safe=''),
                            headers={'User-Agent': self.UA}, timeout=18, retries=2)
        if not txt:
            return ''
        try:
            obj = json.loads(txt)
            for k in ('url', 'playUrl', 'play_url', 'm3u8', 'src', 'link'):
                if isinstance(obj, dict) and obj.get(k):
                    u = str(obj[k]).strip()
                    if u.startswith('http'):
                        return u
        except Exception:
            pass
        m = re.search(r'"url"\s*:\s*"([^"]+)"', txt)
        if m:
            return m.group(1).replace('\\/', '/')
        if txt.startswith('http'):
            return txt.split('\n')[0].strip()
        return ''

    def playerContent(self, flag, id, vipFlags=None):
        pid = str(id or '').strip()
        if not pid:
            return {'parse': 1, 'url': '', 'header': {'User-Agent': self.UA}}
        if (pid.startswith('http') or pid.startswith('//')) and self.VIDEO_RE.search(pid):
            if pid.startswith('//'):
                pid = 'https:' + pid
            return {'parse': 0, 'url': pid, 'header': {'User-Agent': self.UA}}
        kl = self._decode_kl(pid)
        if kl and self.VIDEO_RE.search(kl):
            if kl.startswith('//'):
                kl = 'https:' + kl
            return {'parse': 0, 'url': kl, 'header': {'User-Agent': self.UA}}
        real = self._resolve(pid) or (self._resolve(kl) if kl else '')
        if real and self.VIDEO_RE.search(real):
            if real.startswith('//'):
                real = 'https:' + real
            return {'parse': 0, 'url': real, 'header': {'User-Agent': self.UA}}
        return {'parse': 1, 'url': pid, 'header': {'User-Agent': self.UA}, 'jx': 1}
# ==================== 未来4K 一级源 wl END ====================


class Spider(_BaseSpider):
    """多源合一：影探 / 小山 / 咕噜 / 橘汁 / 四源4K / 河豚 / 片帝 / 未来4K / 找剧。

    分类与搜索按 '<tag>|' 前缀派发；详情页拿到主源数据后，再并发去其余源按
    标题模糊匹配，把匹配到的线路追加在后面。播放时按线路 id 里编码的 tag 派发回原源。
    """

    NAME = 'Kishuto'
    ORDER = ('yt', 'sz', 'gg', 'jn', 'sk', 'ht', 'pd', 'wl', 'zj')
    # 2026-11-21 全源复测：jx(剧下饭) 8 个镜像全失联，已整源删除（源码段 + 类 +
    # 本表条目），不再作为候选；gg(咕噜) T3 已恢复，
    # 搜索 18~21 条、菲乐4K 实测 2160p，接回默认。ff/fq 仍不可用，不进默认。
    # wl(未来4K) 2026-11-21 晚复测后接回：此前记录的「解析只回原网页 / 直链恒 403」
    # 是拿解码后的 v.qq.com 网页地址去解析导致的 —— 传 kl- 原文 4/4 出真实流，
    # 返回的 defaultts m3u8 清单 200、255 片全 206/MP2T、无加密，实探可播；
    # 片库也不小（狂飙 7 / 三体 4 / 教父 5 / 繁花 6）。它的 kl 线是 1080 TS 流，
    # 展示名「未来4K·kl」的 4K 属源名不属画质，已由 LABEL_NO_QUALITY 剥离后按 1080 档处理。
    # xj(小鸡) 2026-11-21 晚整源删除（1.0.8 客户端逆向后确认无解）：站点与搜索/
    # 详情都正常，但 decode/url 对所有线路、所有设备统一 403「VIP权益已过期」
    # (40302)；服务端 adConfig 自述播放要「看广告换 8h VIP 或 50 次解码」或卡密，
    # 无免费端点、令牌不可解密 —— 属于服务端会员变现，客户端侧无法合法修复。
    LABELS = {'gg': '咕噜', 'yt': '影探', 'xf': '稀饭',
              'ff': 'FoFo', 'sz': '小山', 'fq': '枫奇', 'zj': '找剧',
              'jn': '橘汁', 'sk': '四源4K',
              'ht': '河豚', 'pd': '片帝', 'wl': '未来4K'}
    DETAIL_BUDGET = 4.0    # 兼容旧配置，_fill 已改成下面的三段式
    FILL_BUDGET = 1.6      # 首屏凑线路的最长等待（秒）
    TAIL_WAIT = 0.45        # 攒够 5 条后再收尾这么久，把已回源的线路都带上
    PLAY_TRY = 5           # 播放失败时最多试 5 条候选线路
    PLAY_HEAD = 4.5        # 本线路最多等这么久才换源
    # 坏线路一般 0.3~0.5s 就返回空，不会等满；4.5s 是为了不误杀「小山/米诺」这类
    # 取票+解析站两跳、实测首播要 4.4s 的正常线路（同集重播有缓存，秒出）
    # 两跳源（取票 + 解析）天生比单跳慢，实测首播 5~7s，单独放宽；
    # 其余源仍用 PLAY_HEAD，坏线不会被这条拖长。
    # sz 由 6.5 收到 5.5：实测「小山·1080P」最慢 4.87s，5.5 仍能兜住；
    # 而小山那批 4K 线（jx4k 解析）要 17~20s，等 6.5 也等不来，纯粹白等。
    PLAY_HEAD_SLOW = {'sz': 5.5, 'jn': 6.5, 'pd': 5.5}
    PLAY_EACH = 3.0        # 换源时每条线路自己最多等这么久
    # 0.7s 内已经回来的快线完全不 fanout，请求数和改动前一样。
    RACE_AFTER = 1.2       # 超过这么久没回才开抢答（实测影探正常冷播 0.44~1.04s，
    #                        取 1.2 让正常片一次都不 fanout；卡住的线 1.2+0.9≈2.1s 出流，
    #                        而改动前是等满 4.5s 再换源、实测 7.2s 仍为空）
    RACE_MAX = 1           # 抢答最多再开几条（1 条就够救黑洞线，不再放大上游压力）
    PLAY_BUDGET = 11.0     # 单条线路的总时长上限（秒）：够两跳源首播 + 一轮换源
    PLAY_SPEED = {'sz': 0, 'jn': 1, 'ht': 2, 'gg': 3, 'sk': 4, 'wl': 5,
                  'xf': 6, 'ff': 8, 'fq': 9, 'pd': 10, 'zj': 11,
                  'yt': 13}   # gg 首播实测 0.1~1.0s，排在 ht 之后；
    #                           wl 实测 0.11~0.61s，直链/kl 解码不经解析站，紧跟 sk
    FILL_ENOUGH = 4        # 攒够 5 条线路就渲染首屏，不再干等
    TOPUP_BUDGET = 15.0   # 后台补齐的最长等待（纯后台线程，不影响首屏；实测
    #                       橘汁一条片要 11s 才回，8s 会白白丢掉 5 条线路）
    SEARCH_BUDGET = 2.0      # 搜索总预算：到 6 源且慢源已回就提前收，最晚 1.6s 软上限
    SEARCH_MIN_SRC = 6       # 至少这么多源应答才允许早停（8 源里到 6 个结果才稳定）
    # 「结果够多」才允许早停：实测搜「漫长的季节」0.47s 就凑够 6 源收工，只出 24 条，
    # 影探/橘汁/四源4K 三条还在路上的结果被直接丢掉（同一批源搜别的片各给 12 条）。
    # 结果多的片（狂飙 100+ 条、庆余年 60 条）照旧 0.5~1.4s 收工，只有冷门词多等，
    # 且仍受 SEARCH_SLOW_WAIT 软上限约束，最坏不比原来慢。
    # 全空（0 条）不适用：所有应答的源都说没有时再等也不会有，拼错的词不该多等。
    SEARCH_ENOUGH = 36
    SEARCH_SLOW = ('pd', 'jn', 'wl')   # 冷启动慢的关键源：片帝域名池首探 1.3s、
    #                                   橘汁 1.2~1.9s、未来4K 0.8~1.2s（单跳但后端抖动）
    # 软上限/结果够多这两条早停可以放弃 SEARCH_SLOW 里的源，唯独片帝不行：
    # 它是用户主力源，且域名池首探 1.1~1.8s 恰好卡在 1.6s 软上限边缘。
    # 实测（繁花/狂飙/庆余年/三体/沙丘/漫长的季节/甄嬛传/琅琊榜 各一轮）：
    # 7 次 pd 正常出卡，1 次「琅琊榜」被 SLOW_WAIT 在 1.62s 收工时 pd 还没回来，
    # 列表里 5 个源 26 条就是没有片帝。只对片帝多等，最多等到 SEARCH_BUDGET。
    SEARCH_MUST = ('pd',)
    # 片帝未回时把搜索预算顺延这么多（秒）。实测聚合场景里 3 域名抢答有
    # 1/6~1/4 的轮次在 1.4s 内一个都没回来（本机 9 源同时打网络），
    # 而 _race 自己的上限是 2.25s（2.0 + 0.25 收尾），顺延到 2.7s 才能把
    # 「race 最后一刻才回来」的那批也收进来。只有它慢时才付这 0.7s。
    SEARCH_MUST_EXTRA = 0.7
    SEARCH_SLOW_WAIT = 1.6    # 等不到 6 源时的软上限，仍在 2.0s 预算内
    SEARCH_PARTIAL_TTL = 60  # 到齐源不全时的搜索缓存（秒）：不让残缺结果固化 10 分钟
    SEARCH_MUST_TTL = 20     # 缺片帝的残缺结果缓存（秒）：1 分钟足以让用户重搜就看不到它
    SEARCH_GRACE = 2.5       # 预算到点仍一条没有时的额外宽限（只在这种情况下生效）
    HOME_BUDGET = 8.0
    CACHE_TTL = 300
    # 首页分类/推荐默认取影探；ext 传 {"home_source":"pd"} 可切到片帝，
    # {"home_source":"gg"} 切咕噜（旧版曾把片帝首页片单直接写死移除，现改为可配置）。
    HOME_SOURCE = 'yt'
    HOME_CLASS_MAX = 12    # 首页最多挂几个分类（壳会逐个预取，太多拖慢）
    HOME_TTL = 90          # 首页结果缓存（秒）—— 壳会连着调 homeContent/homeVideoContent
    CAT_TTL = 60           # 分类首页缓存（秒）
    # 站点分类里的圈号序号（「热门电影① / ② / ③」）
    _CIRCLED_SEQ = frozenset('①②③④⑤⑥⑦⑧⑨⑩')

    def __init__(self):
        self.cfg = {}
        self._ready = {}
        self._srcs = {}
        self._home = {}             # {filter: (时间戳, 首页结果)} 壳可能两种 filter 都调
        self._cat = {}             # 分类首页缓存，防止来回切页重复打接口
        self._diag = None          # 非 None 时进入诊断中心模式
        try:
            self._build({})
        except Exception:
            pass

    # ---------------- 生命周期 ----------------
    def getName(self):
        return self.NAME

    def version(self):
        return CODE_VERSION

    def init(self, extend=''):
        cfg = {}
        try:
            if isinstance(extend, dict):
                cfg = dict(extend)
            elif isinstance(extend, str) and extend.strip().startswith('{'):
                cfg = json.loads(extend)
        except Exception:
            cfg = {}
        self.cfg = cfg if isinstance(cfg, dict) else {}
        # 影探那层自己也是四源聚合，首屏预算压到 3.2s：超时的源它会后台补完
        self.cfg.setdefault('detail_budget', 1.2)
        if str(self.cfg.get('mode') or '').lower() in ('settings', 'diag'):
            self._diag = KishDiag(self)
        try:
            self._build(self.cfg)
        except Exception:
            pass
        try:
            # 自更新：仍默认开启，但 check_update 现在强制 sha256 + 证书校验，
            # 清单不带 sha256 就一个字节都不会写盘。ext 传 {"auto_update":0} 可关。
            if str(self.cfg.get('auto_update', '1')).lower() not in (
                    '0', 'false', 'no', 'off'):
                _kish_update_async(str(self.cfg.get('update_url') or UPDATE_URL))
        except Exception:
            pass
        return None

    # 可用源表：ORDER 里的会在 init 时实例化，其余（挂掉/非默认）按需构造
    MAKERS = {'gg': GuluSpider, 'yt': YtAggSpider, 'xf': XifanAggSpider,
              'ff': FofoSpider, 'sz': ShanZhaSpider,
              'fq': FengqiSpider, 'zj': ZJSpider, 'jn': JZNewSpider,
              'sk': SK4KSpider, 'ht': HT4KSpider,
              'pd': PDSpider, 'wl': WL4KSpider}

    def _build(self, cfg):
        for tag in self.ORDER:
            self._mk_src(tag)
        self._prewarm_srcs()

    def _prewarm_srcs(self):
        """后台先把「要握手」的源叫醒。

        橘汁首次要 login + zone（实测 2.3s），详情预算只有 1.2~1.9s，
        赶不上就等于这部片没有橘汁线路 —— 用户看到的是「橘汁有时有、有时
        没有、点了没反应」。init 是必过的一条路，在这里提前握手最省事。
        """
        if getattr(self, '_warmed_srcs', False):
            return
        self._warmed_srcs = False

        def run():
            jobs = []

            def wake(tag):
                try:
                    ob = self._srcs.get(tag)
                    fn = getattr(ob, '_ensure', None) if ob is not None else None
                    if fn is not None:
                        fn()
                except Exception:
                    pass

            def wake_pd():
                # 片帝走 30 个域名的池子，首探要 1.3s（之后 0.8s）。
                # 用户从打开壳到点搜索通常有 1~2s，这里后台把 host 探好，
                # 真正搜索时就不会因冷启动被早停丢掉。_host 是类变量，全进程共享。
                try:
                    ob = self._srcs.get('pd')
                    if ob is not None:
                        ob._get('/v1/browse/catalog?page=1&limit=1')
                except Exception:
                    pass

            def wake_yt():
                # 首页分类（nav）+ 推荐（index_video）实测 0.5~2.1s，是打开壳后
                # 第一屏的等待来源。init 之后壳通常还要几秒才画首页，先在这里
                # 把两条接口取好落缓存，首页调用就直接命中（nav 6h / 推荐 10min）。
                try:
                    ob = self._srcs.get('yt')
                    if ob is None:
                        return
                    inner = ob._src('yt') if hasattr(ob, '_src') else ob
                    if inner is None:
                        return
                    inner.home()
                    inner.home_vod(2.5)
                except Exception:
                    pass

            for tag in ('jn', 'sk'):
                th = threading.Thread(target=wake, args=(tag,), daemon=True)
                th.start()
                jobs.append(th)
            for fn in (wake_pd, wake_yt):
                th = threading.Thread(target=fn, daemon=True)
                th.start()
                jobs.append(th)
            for th in jobs:                    # 纯 daemon，join 只为让 run 自己收尾
                try:
                    th.join(3.0)
                except Exception:
                    pass

        self._warmed_srcs = _bg_spawn(run, name='prewarm') is not None

    def _mk_src(self, tag):
        ob = self._srcs.get(tag)
        if ob is not None:
            return ob
        cls = self.MAKERS.get(tag)
        if cls is None:
            return None
        try:
            ob = cls()
        except Exception:
            return None
        self._srcs[tag] = ob
        return ob

    def _src(self, tag):
        ob = self._mk_src(tag)
        if ob is None:
            return None
        if not self._ready.get(tag):
            self._ready[tag] = True
            try:
                ext = json.dumps(self.cfg, ensure_ascii=False) if self.cfg else ''
                ob.init(ext)
            except Exception:
                pass
        return ob

    def destroy(self):
        for ob in list(self._srcs.values()):
            try:
                ob.destroy()
            except Exception:
                pass
        self._srcs.clear()
        self._ready.clear()
        self._warmed_srcs = False

    def isVideoFormat(self, url):
        try:
            return bool(is_stream_url(url) or is_media_url(url))
        except Exception:
            return False

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return None

    # ---------------- id 编解码 ----------------
    @staticmethod
    def _b64(raw):
        return base64.urlsafe_b64encode(raw.encode('utf-8')).decode('ascii').rstrip('=')

    @staticmethod
    def _unb64(s):
        s = str(s or '')
        s += '=' * (-len(s) % 4)
        return base64.urlsafe_b64decode(s.encode('ascii')).decode('utf-8', 'replace')

    def _enc_vid(self, tag, vid):
        return 'k1' + self._b64('%s\x1f%s' % (tag, vid))

    def _dec_vid(self, code):
        s = str(code or '')
        if s.startswith('k1'):
            try:
                tag, _, vid = self._unb64(s[2:]).partition('\x1f')
                # 与 _dec_play 同理：认全部 MAKERS，不能只认 ORDER，
                # 否则被移出默认顺序的源(ff/fq)旧 id 会被当成影探 id 去请求。
                if tag in self.MAKERS and vid:
                    return tag, vid
                if tag:
                    return '', ''      # 认识格式但源未知：宁可口径为空，不猜成影探
            except Exception:
                pass
        return 'yt', s

    def _enc_play(self, tag, flag, pid, cid='', ep=''):
        # cid=详情 id、ep=集名：取流失败时要靠它们回查同片其它线路
        return 'k2' + self._b64('%s\x1f%s\x1f%s\x1f%s\x1f%s'
                                % (tag, flag, pid, cid, ep))

    def _dec_play(self, code):
        s = str(code or '')
        if s.startswith('k2'):
            try:
                parts = self._unb64(s[2:]).split('\x1f', 4)
                # 只认 ORDER 会误伤按需构造的源（ff/fq 等被移出 ORDER 后，
                # 旧详情里的播放码仍带它的 tag），这里认全部 MAKERS。
                if len(parts) >= 3 and parts[0] in self.MAKERS:
                    while len(parts) < 5:
                        parts.append('')
                    return parts[0], parts[1], parts[2], parts[3], parts[4]
            except Exception:
                pass
        # 解不出源标记时不再一律派给影探：那会把整串编码当 pid 去请求，
        # 结果是「点 A 片播出 B 片」。返回空源让上层回空 url 更诚实。
        return '', '', s, '', ''

    # ---------------- 并发小工具 ----------------
    def _fan(self, work, budget):
        box = {}
        ths = []
        for tag in self.ORDER:
            def run(t=tag):
                try:
                    work(t, box)
                except Exception:
                    box.setdefault(t, None)
            th = threading.Thread(target=run)
            th.daemon = True
            th.start()
            ths.append(th)
        deadline = time.time() + budget
        for th in ths:
            try:
                th.join(max(0.02, deadline - time.time()))
            except Exception:
                pass
        return box

    # ---------------- 首页 ----------------
    def _home_one(self, tag, filter=True):
        """首页分类 / 筛选 / 推荐取自指定源（默认影探，咕噜作备选）。"""
        ob = self._src(tag)
        if ob is None:
            return None
        try:
            data = ob.homeContent(filter) or {}
        except Exception:
            return None
        label = self.LABELS.get(tag) or tag
        classes = []
        prev_base = ''
        for c in (data.get('class') or []):
            if not isinstance(c, dict):
                continue
            tid = str(c.get('type_id') or '').strip()
            if not tid:
                continue
            if self.HOME_CLASS_MAX and len(classes) >= self.HOME_CLASS_MAX:
                break
            # 站点把系列分类拆成「热门电影① / ② / ③」，后两个只回了圈号；
            # 原样展示就是「影探·②」，用户看不出是什么。纯圈号继承前一类的
            # 基名，拼成「热门电影②」。
            nm = clean_name(c.get('type_name') or tid) or tid
            if nm in self._CIRCLED_SEQ:
                nm = (prev_base + nm) if prev_base else nm
            elif nm and nm[-1] in self._CIRCLED_SEQ:
                prev_base = nm[:-1]
            else:
                prev_base = nm
            classes.append({'type_id': '%s|%s' % (tag, tid),
                            'type_name': '%s·%s' % (label, nm)})
        if not classes:
            return None
        keep = set(c['type_id'].split('|', 1)[1] for c in classes)
        filters = {}
        for k, v in (data.get('filters') or {}).items():
            if str(k) in keep:
                filters['%s|%s' % (tag, k)] = v
        cards = []
        for it in (data.get('list') or [])[:30]:
            if not isinstance(it, dict):
                continue
            it = dict(it)
            it['vod_id'] = self._enc_vid(tag, it.get('vod_id'))
            _memo_title(it['vod_id'], it.get('vod_name'))
            cards.append(it)
        return {'class': classes, 'filters': filters, 'list': cards}

    def homeContent(self, filter=True):
        if self._diag is not None:
            return self._diag.homeContent(filter)
        now = time.time()
        key = bool(filter)
        hit = self._home.get(key)
        if hit and hit[1] and now - hit[0] < self.HOME_TTL:
            return hit[1]
        # HOME_SOURCE 以前只被诊断中心当文字显示，homeContent 里写死 'yt'，
        # ext 配了也不生效。这里让它真正生效：默认仍是影探，想看片帝分类
        # 就传 {"home_source":"pd"}；指定源失败仍按原顺序回退，行为不变。
        primary = str(self.cfg.get('home_source') or self.HOME_SOURCE or 'yt')
        got = None
        for tag in [primary] + [t for t in ('yt', 'gg') if t != primary]:
            got = self._home_one(tag, filter)
            if got:
                break
        if not got:
            got = self._home_all(filter)
        if got:
            self._home[key] = (now, got)
        return got

    def _home_all(self, filter=True):
        def work(tag, box):
            ob = self._src(tag)
            got = ob.homeContent(True) if ob else None
            box[tag] = (got or {}).get('class') or []
        box = self._fan(work, self.HOME_BUDGET)
        classes = []
        for tag in self.ORDER:
            for c in box.get(tag) or []:
                if not isinstance(c, dict):
                    continue
                tid = c.get('type_id')
                if tid in (None, ''):
                    continue
                classes.append({
                    'type_id': '%s|%s' % (tag, tid),
                    'type_name': '%s·%s' % (self.LABELS[tag],
                                            c.get('type_name') or tid)})
        if not classes:
            classes = [{'type_id': 'yt|电影', 'type_name': '影探·电影'}]
        return {'class': classes, 'filters': {}}

    def homeVideoContent(self):
        if self._diag is not None:
            return self._diag.homeVideoContent()
        now = time.time()
        for key in (True, False):
            hit = self._home.get(key)
            if hit and now - hit[0] < self.HOME_TTL:
                cached = (hit[1] or {}).get('list')
                if cached:
                    return {'list': cached}
        # 推荐位与筛选无关，必须用 filter=False 去取：filter=True 走的是筛选分桶，
        # 那份数据里没有推荐位（list 为空），会白白落到下面并发轰十个源、
        # 干等满 HOME_BUDGET 才返回（实测 7.8s）。
        # 影探单独走 home_vod：推荐位不需要分类，省掉 nav 与"影探空→咕噜"回退，
        # 壳同时调 homeContent / homeVideoContent 时推荐区能更快填上。
        try:
            ob = self._src('yt')
            inner = ob._src('yt') if hasattr(ob, '_src') else ob
            lst = as_list(inner.home_vod(1.5).get('list'))[:30] if inner else []
            if lst:
                return {'list': lst}
        except Exception:
            pass
        got = self._home_one('yt', False) or self._home_one('gg', False)
        if got and got.get('list'):
            return {'list': got['list']}
        # 冷启动兜底：部分壳先问 homeVideoContent 再问 homeContent，直接复用
        # 一次 homeContent 的结果（同一份数据、只打主源），比并发十源快一个量级
        try:
            hc = self.homeContent(False) or {}
            if hc.get('list'):
                return {'list': hc['list']}
        except Exception:
            pass

        def work(tag, box):
            ob = self._src(tag)
            if ob is None:
                box[tag] = []
                return
            # sk/zj 没实现 homeVideoContent：退回它的 homeContent 推荐位。
            # 否则这两个源在首页永远贡献 0 张卡，而异常会被 _fan 静默吞掉，
            # 从外部完全看不出少了两个源。
            got = None
            fn = getattr(ob, 'homeVideoContent', None)
            if callable(fn):
                try:
                    got = fn()
                except Exception:
                    got = None
            if not (got or {}).get('list'):
                try:
                    got = ob.homeContent(False)
                except Exception:
                    got = None
            box[tag] = (got or {}).get('list') or []
        box = self._fan(work, self.HOME_BUDGET)
        out = []
        for tag in self.ORDER:
            for it in (box.get(tag) or [])[:12]:
                if not isinstance(it, dict):
                    continue
                it = dict(it)
                it['vod_id'] = self._enc_vid(tag, it.get('vod_id'))
                _memo_title(it['vod_id'], it.get('vod_name'))
                out.append(it)
        return {'list': out[:40]}

    # ---------------- 分类 ----------------
    def categoryContent(self, tid, pg='1', filter=True, extend=None):
        if self._diag is not None:
            return self._diag.categoryContent(tid, pg, filter, extend)
        ck = None
        try:
            if str(pg) in ('1', '1.0'):
                ck = '%s|%s' % (tid, json.dumps(extend or {}, sort_keys=True,
                                                ensure_ascii=False))
                hit = self._cat.get(ck)
                if hit and time.time() - hit[0] < self.CAT_TTL:
                    return hit[1]
        except Exception:
            ck = None
        tag, _, real = str(tid or '').partition('|')
        if tag not in self.ORDER or not real:
            # 兜底时不能把整串直接当分类 id：'|' / 'foo|' 这类畸形值会被
            # 原样打给源站。含分隔符就只取后半段，再 strip 后判空。
            body = str(tid or '')
            real = (body.split('|', 1)[1] if '|' in body else body)
            real = real.strip().strip('|').strip()   # '||' 这类纯分隔符也算空
            tag = 'yt'
        # 分类 id 为空（壳首屏/异常状态会传空）就别打源站了，白耗一次请求
        if not real.strip():
            page = page_of(pg) or 1
            return {'list': [], 'page': page, 'pagecount': page, 'total': 0}
        # 页码兜底上限：壳偶发把页码传成异常大值，别直接把 99999 打给源站
        if (page_of(pg) or 1) > 999:
            pg = '999'
        # 有些壳把 extend 当 JSON 字符串传，直接丢过去筛选条件会静默失效
        if isinstance(extend, str) and extend.strip().startswith('{'):
            try:
                extend = json.loads(extend)
            except Exception:
                extend = {}
        ob = self._src(tag)
        got = None
        if ob is not None:
            try:
                got = ob.categoryContent(real, pg, filter,
                                         extend if isinstance(extend, dict) else {})
            except Exception:
                got = None
            # 子源把限流/网关错误吞成空列表时（咕噜 429 实测过），直接返回空
            # 会让用户以为「这个分类没有片」。带 _error 标记 = 故障而非真空分类，
            # 隔 0.4s 再问一次；正常空页不带标记，不会白等。
            if isinstance(got, dict) and got.get('_error') and not got.get('list'):
                time.sleep(0.4)
                try:
                    got = ob.categoryContent(real, pg, filter,
                                             extend if isinstance(extend, dict) else {})
                except Exception:
                    pass
        got = got if isinstance(got, dict) else {}
        if not got.get('list'):
            got['list'] = []
        if not got.get('page'):
            got['page'] = page_of(pg) or 1
        if not got.get('pagecount'):
            got['pagecount'] = ((page_of(pg) or 1) + 1
                                if got['list'] else (page_of(pg) or 1))
        for it in (got.get('list') or []):
            try:
                it['vod_id'] = self._enc_vid(tag, it.get('vod_id'))
                _memo_title(it['vod_id'], it.get('vod_name'))
            except Exception:
                pass
        got.pop('_error', None)
        if ck and got.get('list'):
            _cap_put(self._cat, ck, (time.time(), got), 40, drop=6)
        return got

    # ---------------- 搜索 ----------------
    NAME_NOISE = ('手语版', '字幕助听版', '字幕版', '助听版', '无字幕',
                  '国语版', '粤语版', '日语版', '英语版', '普通话版', '双语版',
                  '中配版', '台配版', '国配版', '日配版', '粤配版', '原声版',
                  '中配', '台配', '国配', '普通话', '国语', '粤语', '日语',
                  '英语', '韩语', '原声',
                  '真人版', '动画版', '重制版', '剧版', '电影版', '电视版',
                  '完整版', '未删减', '无删减', '高清版', '蓝光版', '合集', '正片',
                  '特别篇', '特别版', '解析', '解说', '精彩分享', '剧情揭秘',
                  '揭秘', '预告', '花絮', '片段', '番剧', '在线观看', '正版',
                  '抢先版', '枪版', '修复版', '加长版', '导演剪辑版')

    # 出现在片名中间就说明后面都是衍生内容，直接切断
    NAME_CUT = ('剧情揭秘', '深度解读', '解说', '预告', '花絮', '片段', '特辑',
                '精彩', '分集', '速看', '混剪', '盘点', '年番')

    @classmethod
    def _base_name(cls, name):
        """把「凡人修仙传手语版」「凡人修仙传2025」这类变体归一成主片名。"""
        raw = str(name or '')
        # 站点常把副标题/来源拼进片名，先掐掉「-」「｜」「_」之后的部分
        for sep in ('-', '－', '｜', '|', '_'):
            if sep in raw[1:]:
                raw = raw.split(sep)[0]
        t = norm_title(raw)
        if not t:
            return ''
        t = re.sub(r'[（(][^）)]*[）)]', '', t)
        for _ in range(3):
            for w in cls.NAME_NOISE:
                if t.endswith(w) and len(t) > len(w):
                    t = t[:-len(w)]
                elif t.startswith(w) and len(t) > len(w):
                    t = t[len(w):]
        for w in cls.NAME_CUT:          # 中间出现就切
            i = t.find(w, 1)
            if i > 0:
                t = t[:i]
                break
        if t.endswith('版') and len(t) >= 4:   # 沙丘2版 / 葬送的芙莉莲版
            t = t[:-1]
        t = re.sub(r'第[一二三四五六七八九十\d]+[季部篇]$', '', t)
        t = re.sub(r'(19|20)\d{2}$', '', t)
        t = t.rstrip('之').strip()
        return t or norm_title(raw)

    def _fan_search(self, work, budget, grace=0.8):
        """并发搜；影探回来且另有 2 个源到齐后，还要 ≥6 源应答（含慢源片帝）才收工。

        枫奇（fq）已不在 ORDER 里，原先给它单独留 4.6s 的 fq_wait 是死配置，
        一并删掉——那段等待永远不会触发，只会误导后来改代码的人。
        """
        box = {}
        ths = {}
        for tag in self.ORDER:
            def run(t=tag):
                try:
                    work(t, box)
                except Exception:
                    box.setdefault(t, [])
            th = threading.Thread(target=run)
            th.daemon = True
            th.start()
            ths[tag] = th
        started = time.time()
        deadline = started + budget
        yt_at = None
        while time.time() < deadline:
            got_n = sum(len(v) for v in box.values() if isinstance(v, list))
            # SEARCH_MUST（片帝）还在路上时：①后面所有「差不多就收」的早停都让路；
            # ②预算往下顺延 SEARCH_MUST_EXTRA。它并发抢答 3 个域名的耗时实测
            # p50 0.8s / p90 1.24s / 最坏 1.55s（独占时），但聚合里 9 个源同时
            # 打网络，抢答会拖到 1.4s 上限之外 —— 那就是「这次搜索没有片帝」。
            must_live = [t for t in self.SEARCH_MUST
                         if t not in box and ths.get(t) is not None
                         and ths[t].is_alive()]
            if must_live:
                tail = started + budget + self.SEARCH_MUST_EXTRA
                if deadline < tail:
                    deadline = tail
            if 'yt' in box:
                if sum(1 for t in box if t != 'yt') >= 2:   # 影探 + 另外两个源
                    # 旧逻辑在这里直接 break：实测 0.52s 就收工时只到了 yt/sz/gg/ht，
                    # 片帝/橘汁/咕噜还没回，8 个源只出 4 个，用户以为片帝没有片；
                    # 而且同一关键词两次搜出的源数都不一样。现在要同时满足
                    # 「≥ SEARCH_MIN_SRC 个源应答」「关键慢源已回」「结果够多
                    # （SEARCH_ENOUGH）」三条，才允许早停；等不到就等到
                    # SEARCH_SLOW_WAIT 这个软上限，不贴着预算收工。
                    n = len(box)
                    slow_live = [t for t in self.SEARCH_SLOW
                                 if t not in box and ths.get(t) is not None
                                 and ths[t].is_alive()]
                    # got_n == 0：所有应答的源都说没有 —— 再等也不会凭空出现，
                    # 拼错的词/冷门口碑片不该让用户多等 1.3s（实测 0.5s → 1.8s）
                    if (n >= len(self.ORDER) or
                            (n >= self.SEARCH_MIN_SRC and not slow_live
                             and (got_n <= 0 or got_n >= self.SEARCH_ENOUGH))):
                        break
                    # 只剩 1~2 个慢源时不必等满软上限：实测橘汁冷启动 1.9s，
                    # 它那 20~24 条与影探/小山/河豚高度重叠，为它多等 0.6s
                    # 对结果几乎没影响（详情页还会跨源补线）。
                    if (n >= len(self.ORDER) - 2 and got_n >= 60
                            and not must_live):
                        break
                    if (time.time() - started >= self.SEARCH_SLOW_WAIT
                            and not must_live):
                        break
                elif yt_at is None:
                    yt_at = time.time()
                elif time.time() - yt_at >= grace:
                    # 只有影探回来、其余源都还在跑时，旧逻辑 0.8s 后就收工，
                    # 结果里常常只有 1~2 个源。源够数或线程全死（真等不到了）才收。
                    if (((len(box) >= self.SEARCH_MIN_SRC
                          and (got_n <= 0 or got_n >= self.SEARCH_ENOUGH))
                         and not must_live) or
                            not any(t.is_alive() for t in ths.values())):
                        break
            elif (len(box) >= self.SEARCH_MIN_SRC
                  and (got_n <= 0 or got_n >= self.SEARCH_ENOUGH)
                  and not must_live):
                break            # 影探没回但源够、结果也够多（或全空），且片帝已回
            elif not any(t.is_alive() for t in ths.values()):
                break
            time.sleep(0.03)
        # 预算到点还一条都没有（网络慢/主源抽风）：再宽限一点。
        # 否则壳里看到的是「搜索无结果」，用户只会以为这个源搜不到片，
        # 而不是「再等一下就有」——重搜要重打 10 个源，代价更高。
        # 但必须区分「片名本来就没有」：那种情况多半已有 4 个以上的源回了空，
        # 再等只是白白拖慢 2.5s，所以只在「应答的源太少」时才宽限。
        if not any(box.get(t) for t in ths) and len(box) < 4:
            extra = time.time() + getattr(self, 'SEARCH_GRACE', 2.5)
            while time.time() < extra:
                if any(box.get(t) for t in ths) or len(box) >= 4:
                    break
                if not any(t.is_alive() for t in ths.values()):
                    break
                time.sleep(0.04)
        return box

    SEARCH_TTL = 600

    def searchContent(self, key, quick=False, pg='1'):
        """搜索退回最初版：六个源各出各的，按源顺序原样列前 12 条。

        不做同名合并、不做相关性过滤、不重排出卡优先级 —— 壳里看到什么
        就是各站点搜索接口返回的什么。并发与短缓存只用于提速，不改结果。
        详情页跨源补线路的匹配另见 strict_match（不再把衍生电影挂进来）。
        """
        if self._diag is not None:
            return self._diag.searchContent(key, quick, pg)
        kw = str(key or '')
        if not kw.strip():
            # 与正常返回同构：部分壳会读 page/limit 决定分页，缺字段会当成异常结果
            return {'list': [], 'page': 1, 'pagecount': 1,
                    'limit': 0, 'total': 0}
        try:
            page = int(str(pg or 1))
        except Exception:
            page = 1
        if page < 1:
            page = 1

        # 纯符号/生僻词归一化后可能为空串，不同关键词会撞成同一个缓存键；
        # 退回原文当键，保证「!」和「?」不会互相串结果。
        ck = 'ks:%s:%s' % (norm_title(kw) or str(kw or '').strip(), page)
        hit = cache_get(ck)
        if hit:
            try:
                return json.loads(hit)
            except Exception:
                pass

        errs = []

        def work(tag, box):
            ob = self._src(tag)
            got = ob.searchContent(kw, quick, pg) if ob else None
            if isinstance(got, dict) and got.get('_error'):
                errs.append(tag)
            box[tag] = (got or {}).get('list') or []

        _t0 = time.time()
        box = self._fan_search(work, self.SEARCH_BUDGET)
        # 早停会漏掉偏慢的源（片帝域名池首探 1.3s）。这类残缺结果不能按
        # 600s 缓存，否则用户 10 分钟内重搜同一个词都看不到片帝。
        # 报故障（_error）的源同样算「没到齐」：上游 null 风暴/限流时它虽然
        # 应答了，但给的是空 —— 按完整结果缓存 10 分钟就把一次抽风冻住了。
        complete = sum(1 for t in self.ORDER if t in box and t not in errs)
        # 片帝（SEARCH_MUST）没回的结果单独压到 20s：多等之后它仍没赶上（真的在
        # 探测域名池），用户 20s 后重搜就能看到它，而不是被 60s 残缺缓存锁住。
        must_missing = any(t not in box or t in errs for t in self.SEARCH_MUST)
        out = []
        for tag in self.ORDER:
            for it in (box.get(tag) or [])[:12]:
                if not isinstance(it, dict):
                    continue
                it = dict(it)
                it['vod_id'] = self._enc_vid(tag, it.get('vod_id'))
                _memo_title(it['vod_id'], it.get('vod_name'))
                note = str(it.get('vod_remarks') or '')
                it['vod_remarks'] = ('[%s] %s'
                                     % (self.LABELS.get(tag, tag), note)).strip()
                out.append(it)

        # 相关性排序：各源内部顺序原样保留，只把「跟关键词更贴」的提到前面。
        # 实测搜「狂飙」，影探把「纳斯卡：全速狂飙 第一季」排在第一位，真正的
        # 《狂飙》在第 3 条，用户点第一条就进错片。同档内仍是源顺序（4K 源优先），
        # 不会打散同名条目。
        kwn = norm_title(kw)
        kws = str(kw or '').strip()

        def _rel(it):
            raw = str(it.get('vod_name') or '').strip()
            x = norm_title(raw)
            if not x or not kwn:
                return 4
            # 原名一字不差 > 只差季数/标点 > 前缀 > 包含 > 其它
            if raw == kws:
                return 0
            if x == kwn:
                return 1
            if x.startswith(kwn) or kwn.startswith(x):
                return 2
            if kwn in x or x in kwn:
                return 3
            return 4

        try:
            out.sort(key=_rel)
        except Exception:
            pass

        # pagecount 必须大于当前页，否则壳认为没有下一页，永远翻不到第 2 页
        res = {'list': out, 'page': page,
               'pagecount': page + 1 if out else page,
               'limit': len(out), 'total': len(out)}
        # 有源报故障时全源空结果多半是限流/抖动，缓存 10 分钟会让用户反复
        # 重搜都是空；只压 20s。正常「确实搜不到」的空结果仍按 10 分钟缓存。
        if not out and errs:
            ttl = 20
        elif must_missing:
            ttl = self.SEARCH_MUST_TTL
        elif complete < len(self.ORDER):
            ttl = self.SEARCH_PARTIAL_TTL
        else:
            ttl = self.SEARCH_TTL
        try:
            cache_put(ck, json.dumps(res, ensure_ascii=False), ttl)
        except Exception:
            pass
        _search_stat_put(kw, self.ORDER, box, errs, len(out), ttl,
                         time.time() - _t0, self.SEARCH_MUST)
        return res

    # ---------------- 详情 ----------------
    def _digest(self, tag, vod, cid=''):
        """把某个源 detailContent 返回的线路拆开并按本文件格式重新编码。"""
        froms = str(vod.get('vod_play_from') or '').split('$$$')
        urls = str(vod.get('vod_play_url') or '').split('$$$')
        out = []
        for i, f in enumerate(froms):
            f = str(f or '').strip()
            if not f:
                continue
            seg = urls[i] if i < len(urls) else ''
            eps = []
            pids = []
            idx = 0
            for part in str(seg).split('#'):
                part = part.strip()
                if not part:
                    continue
                nm, sep, pid = part.partition('$')
                if not sep:
                    nm, pid = '正片', part
                idx += 1
                pids.append(pid)
                # 播放码里存「集序号\x1e集名」：换源时靠它对齐同一集
                # （影探叫「第01集」、小山叫「01」，光比名字对不上）
                eps.append((nm.strip() or '正片',
                            self._enc_play(tag, f, pid, cid,
                                           '%d\x1e%s'
                                           % (idx, nm.strip() or '正片'))))
            # 多集全部指向同一个地址 = 假线路：站点把一部片的地址塞给每一集。
            # 实测「橘汁·菲乐4K / 咕噜·菲乐4K」36 集共用一个 2025-09-30 的 mp4，
            # 该地址已 404，用户点哪集都黑屏，直接从线路表里剔掉。
            if len(pids) >= 3 and len(set(pids)) == 1:
                continue
            if eps:
                out.append((self._line_name(tag, f), eps))
        return out

    def _line_name(self, tag, flag):
        label = self.LABELS.get(tag) or tag
        f = str(flag or '').strip()
        if tag == 'yt':
            # 影探线路补分辨率：移动云·4K / 优酷·1080P
            try:
                f = YT4K().annotate_line_name(f, '') or f
            except Exception:
                pass
            return self._tidy_line_name(clean_name(f) or label)
        return self._tidy_line_name(clean_name('%s·%s' % (label, f)) or label)

    _QUALITY_TOKENS = frozenset(
        ('4k', '2k', '1080p', '720p', '480p', 'hdr',
         '蓝光', '高清', '超清', '标清'))

    @classmethod
    def _tidy_line_name(cls, nm):
        """线路名去重复画质后缀：「橘汁·菲乐4K·4K」→「橘汁·菲乐4K」。

        源站自己把线路名拼成「菲乐4K」，外面再加一层 tag 后就成了两个 4K。
        规则严格限定在「纯画质词、且已被前面某段包含」这一种情况，
        「四源4K·天堂·高清蓝光4K」这类有实义的组合不会被误删。
        """
        parts = [p for p in str(nm or '').split('·') if p]
        if len(parts) < 3:
            return nm
        out = []
        for p in parts:
            lp = p.lower()
            if lp in cls._QUALITY_TOKENS and any(lp in q.lower() for q in out):
                continue
            out.append(p)
        return '·'.join(out) or nm

    @staticmethod
    def _variants(title):
        """片名变体：全角/半角、季数后缀、括号注释、语种后缀都试一遍。

        实测「葬送的芙莉莲第二季」在稀饭搜不到，去掉「第二季」才行；
        而「庆余年第二季」在影视站带季数反而更准，所以原样排第一。
        """
        t = str(title or '').strip()
        out = [t] if t else []
        if not t:
            return out
        pats = (r'第[一二三四五六七八九十百千万0-9]+[季部篇]',
                r'[（(\[][^）)\]）]*[）)\]]',
                r'(国语|粤语|日语|英语|普通话|中字|双语|原声)版?$',
                r'(19|20)\d{2}$')
        for pat in pats:
            v = re.sub(pat, '', t).strip(' -·:：')
            if len(v) >= 2 and v not in out:
                out.append(v)
        for sep in ('：', ':', '·'):
            if sep in t:
                v = t.split(sep)[0].strip()
                if len(v) >= 2 and v not in out:
                    out.append(v)
        return out[:2]

    def _fill_start(self, tag, title):
        """其余源并发去「搜片名 → 取详情」，返回 (box, threads)。

        box 会被线程陆续塞数据，所以主流程可以只等一小会儿就先渲染。
        """
        box, ths = {}, []
        if not title:
            return box, ths
        variants = self._variants(title)

        def work(tt):
            try:
                ob = self._src(tt)
                if ob is None:
                    return
                pick = None
                for kw in variants:
                    key = (tt, norm_title(kw))
                    if not key[1]:          # 归一化后为空：不同片名会撞成同一个
                        key = (tt, str(kw))  # 键，退回原文当键
                    items = _srch_fetch(
                        key, lambda kw=kw, ob=ob: (
                            ob.searchContent(kw, False, '1') or {}).get('list'))
                    pick = strict_match(title, items)
                    if pick:
                        break
                if not pick:
                    return
                vv = (ob.detailContent([pick.get('vod_id')]) or {}).get('list') or []
                if vv and isinstance(vv[0], dict):
                    box[tt] = vv[0]
            except Exception:
                pass

        for tt in self.ORDER:
            if tt == tag:
                continue
            th = threading.Thread(target=work, args=(tt,))
            th.daemon = True
            th.start()
            ths.append(th)
        return box, ths

    @staticmethod
    def _count_lines(box):
        n = 0
        for v in list(box.values()):
            try:
                n += len([x for x in str(v.get('vod_play_from') or '').split('$$$') if x])
            except Exception:
                pass
        return n

    def _wait_yield(self, box, ths, base_lines, budget):
        """首屏策略：攒够 FILL_ENOUGH 条就开始收工，再收 TAIL_WAIT 秒给足。

        壳拿到 detailContent 后不会原地追加线路，所以「先给 5 条、后面慢慢
        加载」在壳侧不成立 —— 达到 5 条后仍要在预算内把已回源的线路全带上，
        一次给足；预算内没回来的源由 _topup 后台补完写回缓存（重进即全量）。
        """
        start = time.time()
        deadline = start + budget
        have = len(base_lines)
        enough_at = None
        while time.time() < deadline:
            if have + self._count_lines(box) >= self.FILL_ENOUGH:
                if enough_at is None:
                    enough_at = time.time()
                elif time.time() - enough_at >= self.TAIL_WAIT:
                    return True              # 够了，再多收一小会儿就出
            if not any(t.is_alive() for t in ths):
                return True                  # 所有源都跑完了
            time.sleep(0.04)
        return False

    def _digest_box(self, tag, box, cid=''):
        out = []
        for t in self.ORDER:
            v = box.get(t)
            if isinstance(v, dict):
                try:
                    out.extend(self._digest(t, v, cid))
                except Exception:
                    pass
        return out

    REAL4K = frozenset([
        '4K(123)', '4K(YD)', '4K(BD)', '4K(联通)', '4K(移动)', '4K(天翼)',
        '影探·4K(123)', '影探·4K(YD)', '影探·4K(BD)',
        '影探·联通云', '影探·移动云', '影探·天翼云',
        '影探·联通云·4K', '影探·移动云·4K', '影探·天翼云·4K',
        '联通云·4K', '移动云·4K', '天翼云·4K', '联通云', '移动云', '天翼云',
        '小山·蓝光4K【推荐】', '小山·4K',
        # 橘汁新网关（2026-11 实测）：VIP4K 可出直链；旧 T3 名保留兼容
        '橘汁·VIP4K', '橘汁新·VIP4K', 'VIP4K',
        '橘汁·自建4K', '橘汁·自建4K-3', '橘汁·自建4K-4', '自建4K-3', '自建4K-4', 'JD4K',
        '橘汁新·自建4K-3', '橘汁新·自建4K-4',
        '橘汁·JD4K', '橘汁·JD4K-可下载', '橘汁新·JD4K-可下载',
        '橘汁·新咕噜4K', '橘汁·鲸宝4K',
        # 四源4K 整源已实测（2026-11-21 ffprobe：最高 1920x1080），名字里的 4K
        # 是营销词，不再列入真 4K 表；线路名里的 4K 由 sk4_MEASURED 按实测分档。
        '咕噜·新咕噜4K', '咕噜·鲸宝4K',
        '枫奇·至臻4K',
        '找剧·4K海外-官方C', '河豚·蓝光4K', '河豚·4K',
        '片帝·专享4K-Y', '片帝·4K官方C',
    ])
    
    # 名称带 4K 但实测/经验为假 4K（多为 1080 或残缺线）—— 不当真 4K 前置
    FAKE4K = frozenset([
        '咕噜·iyf4k', '咕噜·小熊', '咕噜·VIP4K', '咕噜·VIP',
        '影探·优酷', '影探·爱奇艺', '影探·腾讯',
        '影探·优酷·1080P', '影探·爱奇艺·1080P', '影探·腾讯·1080P',
        '优酷·1080P', '爱奇艺·1080P', '腾讯·1080P',
        '找剧·1080P-官方Z',
        # 名称含 4K 但来自网页平台（解析后通常 ≤1080）
        '影探·优酷·4K', '影探·爱奇艺·4K', '影探·腾讯·4K',
        '咕噜·iyf4k·4K',
    ])

    # 名称带 2K/蓝光但经验为假高清（多为 1080 或更低）
    # 注意：
    #   - 橘汁「神话蓝光」2026-11 实测可出直链，不再当假线
    #   - 2026-11-14：所有含 2K/1440 的线路直接剔除，不参与保留
    FAKE2K = frozenset([
        '咕噜·菲乐2K', '咕噜·鲸宝2K', '咕噜·短剧2K',
        '咕噜·VIP蓝光', '咕噜·VIP', '咕噜·神话',
        # 网页源不可能真 2K
        '影探·优酷·2K', '影探·爱奇艺·2K', '影探·腾讯·2K',
    ])


    BAD_LINES = frozenset(['咕噜·iyf4k', '咕噜·小熊', '找剧·1080P-官方Z', '稀饭·次元城·CYC_Main(需登录)'])  # 优酷/爱奇艺等改作 1080 兜底，不再整线拉黑
    # 曾按线路名整条封杀「菲乐」（上游 CDN 上有批次在 2025-09-30 之后全 404）。
    # 2026-11-21 实测同一名字在不同片下解析到不同 CDN：庆余年/三体的
    # 「菲乐4K」走 apple-co-speed-wug.sviptq.com，ffprobe 读出来是 3840×2160；
    # 狂飙那条走 djvod.ndcimgs.com 才是 404。按名字封杀等于连真 4K 一起丢，
    # 改成在播放阶段「探测不到高度就换源」（见 _play_one），名字不再参与拉黑。
    DEAD_NAME_KEYS = ()
    LINE_FIRST = ('影探', '小山', '橘汁', '咕噜', '河豚', '四源', '片帝', '找剧')

    @classmethod
    def _dead_line(cls, name):
        nm = str(name or '')
        return nm in cls.BAD_LINES or any(k in nm for k in cls.DEAD_NAME_KEYS)

    @classmethod
    def _r4(cls, name):
        """真 4K 实测名单整体前置；组内保持 LINE_FIRST 原序，坏线路不提前。"""
        nm = str(name or '')
        bad = cls._dead_line(nm)
        fake = nm in getattr(cls, 'FAKE4K', ()) or nm in getattr(cls, 'FAKE2K', ())
        is_real = (nm in cls.REAL4K and not bad and not fake)
        hi = (not fake) and any(
            k in cls._qname(nm).lower() for k in ('4k', 'uhd', '2160', '至臻'))
        return (0 if is_real else 1,
                cls._line_rank(nm),
                1 if (bad or fake) else 0,
                0 if hi else 1)


    @classmethod
    def _line_rank(cls, name):
        nm = str(name or '')
        for i, key in enumerate(cls.LINE_FIRST):
            if key in nm:
                return i
        return len(cls.LINE_FIRST)

    # --- KISH_LINE_TRIM BEGIN ---
    # 双规则：
    #   有真 4K → 4K 全留 + 1080 最多 MAX_1080_WHEN_HAS_4K 条兜底
    #   无真 4K → 1080 放宽到 MAX_1080_WHEN_NO_4K 条（可播预检优先）
    #   含 2K/1440 的线路在 _line_tier 已剔除
    # 720 及以下默认全砍；黑名单直接丢。
    KEEP_FAST_NON4K = ()
    MAX_4K = 12              # 真 4K 线路最多留几条（再多壳里就是一排翻不完的 tab）
    MAX_1080_WHEN_HAS_4K = 3  # 有真 4K 时留 3 条 1080 兜底（1 条时橘汁·神话蓝光
                              # 这类能出直链的线永远被影探·腾讯/小山挤掉，等于白接）
    MAX_1080_WHEN_NO_4K = 5
    PROBE_1080_BUDGET = 0.6   # 1080 可播预检总预算（秒）：超时未探的给中性分保留
    PROBE_1080_EACH = 0.5

    # 源标签本身带画质字样，但不代表线路画质：分档和画质宣称判定前先剥掉这层前缀。
    # 目前只有「未来4K」——它给的线路原始名就叫 'kl'，实测是腾讯 defaultts 的 TS 流
    # （255 片全 206/MP2T、无加密），按 1080 档看待才正确；不剥会顶成 4K 档，
    # 既挤占真 4K 名额，又白付一次高度探测再被判「假 4K」换源。
    # 「四源4K」刻意不在列：它的线路名常不带 4K（华谊·Z蓝光 / 华谊·B超高清），
    # 剥掉会把 3 条实测真 4K 线误降成 1080 档。
    LABEL_NO_QUALITY = ('未来4K',)

    @classmethod
    def _qname(cls, name):
        """只留可用于画质判定的部分：剥掉「未来4K·」这类非画质源前缀。"""
        nm = str(name or '')
        for lb in cls.LABEL_NO_QUALITY:
            pfx = lb + '·'
            if nm.startswith(pfx):
                return nm[len(pfx):]
        return nm

    @classmethod
    def _line_tier(cls, name):
        """画质分档：0=真4K, 1=1080档, 2=更低, -1=黑名单/2K剔除。"""
        nm = str(name or '')
        if not nm:
            return 2
        if cls._dead_line(nm):
            return -1
        low = nm.lower()
        qlow = cls._qname(nm).lower()   # 画质判定口径（已剥掉非画质源前缀）

        # 四源4K：名字里的 4K 全是营销词（ffprobe 逐条实测最高 1920x1080），
        # 按实测宽度分档，别让 11 条「假 4K」占满 MAX_4K 名额把别家真 4K 挤下去。
        _wh = sk4_measure(nm)
        if _wh:
            return 0 if _wh[0] >= 3800 else 1

        def _is_low(name_low):
            if any(k in name_low for k in (
                    '720', '480', '360', '240', '标清', '流畅', '极速',
                    '普清', '低清')):
                return True
            # 「sd」只在独立成词时算低清：早期版本用子串匹配，
            # 任何含 sd 两个字母的英文线路名都会被打成低清
            return bool(re.search(r'(?<![a-z])sd(?![a-z])', name_low))

        # 明确低清
        if _is_low(low):
            if any(k in low for k in ('4k', 'uhd', '2160', '2k', '1440', '1080', 'fhd')):
                pass
            else:
                return 2
        # 所有 2K / 1440 直接剔除（优先于假线名单，避免被当成 1080 保留）
        if any(k in low for k in ('2k', '1440')):
            return -1
        fake4 = getattr(cls, 'FAKE4K', frozenset())
        fake2 = getattr(cls, 'FAKE2K', frozenset())
        if nm in fake4 or nm in fake2:
            return 1
        if any(nm.startswith(x) or x in nm for x in fake4):
            return 1
        if any(nm.startswith(x) or x in nm for x in fake2):
            return 1
        # 网页平台挂 4K 字样 → 假高清
        if any(k in nm for k in ('优酷', '爱奇艺', '腾讯', '芒果', '哔哩', 'B站')):
            if any(h in low for h in ('4k', 'uhd', '2160')):
                return 1
        if re.search(r'4k\s*[(（]', qlow) or qlow.startswith('4k'):
            return 0
        if any(k in qlow for k in ('4k', 'uhd', '2160')):
            return 0
        if '至臻' in nm:
            return 0
        if any(k in nm for k in ('移动云', '联通云', '天翼云')) and nm not in fake4:
            return 0
        if nm in cls.REAL4K and nm not in fake4 and nm not in fake2:
            return 0
        # 其余（1080/FHD/蓝光/高清/未标注）统一按 1080 档处理
        return 1

    @classmethod
    def _keep_line(cls, name):
        return cls._line_tier(name) in (0, 1)

    TOP3 = (
        '4K(YD)', '4K(123)', '4K(BD)',
        '影探·移动云·4K', '影探·天翼云·4K', '影探·联通云·4K',
        '影探·移动云', '影探·天翼云', '影探·联通云',
        '移动云·4K', '天翼云·4K', '联通云·4K',
        '橘汁·VIP4K', '橘汁新·VIP4K',
    )

    @classmethod
    def _src_key(cls, name):
        """同源折叠用：取线路名里的源前缀。"""
        nm = str(name or '')
        for key in cls.LINE_FIRST:
            if key in nm:
                return key
        if '·' in nm:
            return nm.split('·', 1)[0]
        return nm

    @classmethod
    def _fb_key(cls, x, probe_score=0):
        n = str(x[0] or '')
        nl = n.lower()
        pri = 5
        if '1080' in nl or 'fhd' in nl:
            pri = 0
        elif '精品2k' in nl or '精品2K' in n:
            pri = 1
        elif '橘汁' in n and any(k in n for k in (
                '神话', '自建', 'B蓝光', 'NS蓝光', 'VIP蓝光', 'OO蓝光')):
            # 与 1080P 同档：橘汁这两条是实测能出真直链的，
            # 排在 1080 之后、其它「蓝光」之前
            pri = 1
        elif '蓝光' in n:
            pri = 3
        elif '高清' in n:
            pri = 4
        # 探测分越高越好（未知=50 中性）
        return (-int(probe_score or 0), pri, cls._line_rank(n),
                -len(x[1] or []), n)

    def _probe_1080_candidates(self, cand, limit):
        """对即将保留的 1080 候选做代表集可播预检（仅当播放码已是 http 时）。

        返回 [(line, score)]，已过滤明确不可播；token 型线路给中性分保留。
        """
        if not cand or limit <= 0:
            return []
        # 先按名称粗排，只探前 limit*2 条，控制耗时
        rough = sorted(cand, key=lambda x: self._fb_key(x, 50))
        pool = rough[:max(limit * 2, limit)]
        budget = float(getattr(self, 'PROBE_1080_BUDGET', 1.0) or 1.0)
        each = float(getattr(self, 'PROBE_1080_EACH', 0.9) or 0.9)
        deadline = time.time() + budget
        scored = []
        for item in pool:
            if time.time() >= deadline:
                # 超时未探的给中性分，不全部丢光
                scored.append((item, 50))
                continue
            sample = kish_sample_url_from_eps(item[1])
            if not sample:
                scored.append((item, 50))  # token：详情阶段无法预检
                continue
            left = max(0.15, deadline - time.time())
            ok, score, _reason = kish_probe_playable(
                sample, timeout=min(each, left))
            if ok:
                scored.append((item, score))
            # ok=False：明确不可播/广告切片过重 → 丢弃
        # 同源只留分最高的一条
        best_by_src = {}
        for item, sc in scored:
            sk = self._src_key(item[0])
            prev = best_by_src.get(sk)
            if prev is None or sc > prev[1]:
                best_by_src[sk] = (item, sc)
        merged = list(best_by_src.values())
        merged.sort(key=lambda t: self._fb_key(t[0], t[1]))
        return merged[:limit]

    def _align_episode_buckets(self, out):
        """集数按段对齐，避免全季合集误杀分季线。"""
        if not out:
            return out
        def _bucket(n_eps):
            if n_eps <= 1:
                return 0
            if n_eps <= 16:
                return 1
            if n_eps <= 40:
                return 2
            return 3
        from collections import defaultdict
        groups = defaultdict(list)
        for item in out:
            groups[_bucket(len(item[1] or []))].append(item)
        merged = []
        for _b, items in sorted(groups.items()):
            try:
                mx = max(len(e or []) for _n, e in items)
            except Exception:
                mx = 0
            if mx <= 1:
                merged.extend(items)
            else:
                floor = max(1, min(mx - 1, int(mx * 0.8)))
                kept = [(n, e) for n, e in items if len(e or []) >= floor]
                merged.extend(kept or items)
        return merged or out

    def _trim_lines(self, lines):
        """双规则裁剪 + 1080 可播预检（有直链时）+ 集数对齐。"""
        try:
            four, cand1080, low = [], [], []
            for x in lines:
                t = self._line_tier(x[0])
                if t == 0:
                    four.append(x)
                elif t == 1:
                    cand1080.append(x)
                elif t == 2:
                    low.append(x)

            has_4k = bool(four)
            max_1080 = (int(getattr(self, 'MAX_1080_WHEN_HAS_4K', 1) or 1)
                        if has_4k else
                        int(getattr(self, 'MAX_1080_WHEN_NO_4K', 5) or 5))

            picked1080 = []
            if cand1080 and max_1080 > 0:
                # 同一源的多条 1080 最终只会留 1 条（_probe_1080_candidates 里
                # 也按源折叠），先折叠一遍就能看清真正的候选数：名额没占满时
                # 不必再花 1.0s 逐条探（预检只是启发式，坏线播放时还有换源兜底）。
                folded, seen_src0 = [], set()
                for x in sorted(cand1080, key=lambda y: self._fb_key(y, 50)):
                    k0 = self._src_key(x[0])
                    if k0 in seen_src0:
                        continue
                    seen_src0.add(k0)
                    folded.append(x)
                if len(folded) <= max_1080:
                    picked1080 = folded
                else:
                    probed = self._probe_1080_candidates(cand1080, max_1080)
                    picked1080 = [item for item, _sc in probed]
                    # 预检全灭时回退名称排序（避免老片一条都没有）
                    if not picked1080:
                        picked1080 = folded[:max_1080]

            if has_4k:
                top, top_names = [], set()
                for n in self.TOP3:
                    for x in four:
                        if str(x[0] or '') == n and n not in top_names:
                            top.append(x)
                            top_names.add(n)
                            break
                body = [x for x in four if str(x[0] or '') not in top_names]
                cap = int(getattr(self, 'MAX_4K', 12) or 12)
                out = (top + body)[:max(1, cap)] + picked1080
            else:
                out = list(picked1080)
                if not out and low:
                    out = low[:1]

            if not out and lines:
                fallback = [x for x in lines if self._line_tier(x[0]) == 0]
                out = fallback if fallback else [
                    x for x in lines if self._line_tier(x[0]) >= 0][:3]
                if not out:
                    out = list(lines)[:3]

            # 片帝（pd）保底一条。它的线路名多是「腾讯视频 / 哔哩哔哩 / 官方R」
            # 这类不带画质的平台名 → 一律落进 1080 档；而有真 4K 时 1080 兜底
            # 只有 MAX_1080_WHEN_HAS_4K=3 条，按名称/可播预检排位它总被小山、
            # 河豚、橘汁挤出去。实测「繁花」详情 10 条线路里 0 条片帝，但
            # 补线线程明明把 pd 的数据带回来了（box 里有 pd）。
            # 用户的片帝是独立片库（不走网页解析），少它等于少一类可用源。
            if cand1080:
                pd_line = next((x for x in cand1080
                                if str(x[0] or '').startswith('片帝·')), None)
                if pd_line is not None and pd_line not in out:
                    keep = [x for x in out if x not in picked1080]
                    picked1080 = [x for x in picked1080 if x != pd_line]
                    if max_1080 > 0 and len(picked1080) >= max_1080:
                        picked1080 = picked1080[:max_1080 - 1]
                    out = keep + picked1080 + [pd_line]

            return self._align_episode_buckets(out)
        except Exception:
            return lines
    # --- KISH_LINE_TRIM END ---

    # --- KISH_FILL_EPS BEGIN ---
    # 缺集补齐：上游 CDN 常常只挂到前几集（实测「影探·天翼云·4K」庆余年只
    # 解出 13/36 集），壳里连后面的集按钮都没有，用户只能自己发现并换线。
    # 这里用「集序号」把同片其它线路的集补进来：补进来的播放码自带来源 tag，
    # 点击时派回它自己的源，等同于一次自动换源，不改变任何换源逻辑。
    FILL_MISSING = True
    FILL_MARK = '·补'
    # 缺失集数 / 全集集数 超过这个比例就不再补：说明两条线根本不是一套内容
    # （单片电影配 36 集剧、花絮配正片），硬补会造出不存在的集。
    FILL_MAX_MISSING_RATIO = 0.7
    # 集数跑偏（多出来的方向）判定：至少有 MIN_EPS_VOTES 条线集数相同时，
    # 集数超过它 MAX_EPS_DRIFT 倍的线路视为跨源误匹配剔除。
    MAX_EPS_DRIFT = 2.0
    MIN_EPS_VOTES = 3
    # 反向：集数不到众数 MIN_EPS_RATIO 的线路按「番外/半截线」剔除
    MIN_EPS_RATIO = 0.5

    def _eps_index(self, code):
        """播放码里的集序号（_digest 写入的「序号\\x1e集名」第一段）。"""
        try:
            head = str(self._dec_play(code)[4] or '').partition('\x1e')[0]
        except Exception:
            return 0
        return int(head) if head.isdigit() else 0

    def _drop_drift_lines(self, lines):
        """剔掉集数明显跑偏的线路，并把「多出来的尾巴」截到众数。

        strict_match 只能保证片名一致，同名不同内容照样会匹配进来：实测
        「漫长的季节」12 集正片里混进一条 30 集的合集，「三体第一季」8 集里
        混进 30 集的动画版，点进去播的是别的东西。这里用众数投票兜底 ——
        至少 3 条线集数相同才把它当基准：
          · 多出来超过 2 倍 → 剔（合集/误匹配）
          · 只有零头集数（< 众数一半）→ 剔。实测「繁花」正片 30 集里混进一条
            1 集的番外《好久不见》，还被当成 4K 线路排在最前面，点开播的是别的片子；
            「莲花楼」里有一条只剩第 35~40 集的半截线
          · 多几集（花絮/数字编号集）→ 截到众数个。实测「莲花楼」的菲乐线挂了
            50 集，尾巴是「花絮6 / 1000008 / 1000009」
        「少了」的正片方向仍交给 _fill_missing_eps 补齐。
        """
        if len(lines) < self.MIN_EPS_VOTES:
            return lines
        cnt = {}
        for _name, eps in lines:
            n = len(eps)
            cnt[n] = cnt.get(n, 0) + 1
        if not cnt:
            return lines
        mode_n, votes = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        if mode_n < 2:
            return lines
        if votes < self.MIN_EPS_VOTES:
            # 首屏线路少时众数往往只有 2 票（比如 3 条线里 2 条 26 集、1 条 55 集），
            # 老逻辑直接放弃，用户首屏就会看到一条集数离谱的「合集线」。
            # 放宽只走「剔合集」这一个方向：众数必须是最少的那个集数，且
            # 最多/最少差到 MAX_EPS_DRIFT 倍以上。反向（众数偏大、少数线偏短）
            # 仍要求 3 票 —— 那可能是真番外，误删代价更大。
            ns = [len(x[1]) for x in lines if x[1]]
            if (votes < 2 or not ns or mode_n != min(ns)
                    or max(ns) < min(ns) * float(self.MAX_EPS_DRIFT)):
                return lines
        limit = mode_n * float(self.MAX_EPS_DRIFT)
        floor = max(1, int(mode_n * float(getattr(self, 'MIN_EPS_RATIO', 0.5))))
        kept = []
        for name, eps in lines:
            n = len(eps)
            if n > limit or (n < floor and n < mode_n - 2):
                continue
            if n > mode_n:
                # 只截掉「集序号超出众数」的那部分，别按位置硬切：
                # 有些线路前几集是预告，按位置切会把正片挤掉
                cut = [e for e in eps
                       if (self._eps_index(e[1]) or 0) <= mode_n]
                eps = cut if cut else eps[:mode_n]
            kept.append((name, eps))
        return kept if len(kept) >= max(1, votes) else lines

    def _fill_missing_eps(self, lines):
        """按集序号补齐同片线路的缺失集，补过的线路名加 FILL_MARK。

        基准取**众数**而不是最大值：实测「漫长的季节」正片 12 集，而未来4K
        那条线挂了 30 集（合集/解说），按最大值当基准会把 8 条正确的线路
        全部拉长到 30 集，造出 18 个不存在的集。
        """
        if not getattr(self, 'FILL_MISSING', True) or len(lines) < 2:
            return lines
        segs = []
        for name, eps in lines:
            idx = {}
            for e_name, code in eps:
                i = self._eps_index(code)
                if i > 0 and i not in idx:
                    idx[i] = (e_name, code)
            segs.append((name, eps, idx))
        # 有效线路：集号从 1 开始（不从 1 起的是花絮/分季，序号对不上）
        votes = {}
        starts = []
        for _n, _e, idx in segs:
            if idx and min(idx) == 1:
                votes[len(idx)] = votes.get(len(idx), 0) + 1
                starts.append(len(idx))
        if not votes:
            return lines
        top, same = sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        if same < 2:
            # 没有两条线互相印证时（只有 2 条线且集数不同），退用最大集数：
            # 残缺线（CDN 只挂到第 13 集）比「合集」常见得多，不补等于整部片
            # 后半段点不到，补的比例上限仍然是 FILL_MAX_MISSING_RATIO。
            top = max(starts) if starts else 0
        if top < 2:
            return lines
        # 补集池：只用「够长」的线路，同档位先到先得（4K 优先补 4K）
        try:
            ordered = sorted(segs, key=lambda s: self._line_tier(s[0]))
        except Exception:
            ordered = list(segs)
        pool = {}
        for _n, _e, idx in ordered:
            if len(idx) < top:
                continue
            for i in range(1, top + 1):
                if i in idx:
                    pool.setdefault(i, idx[i])
        if not pool:
            return lines
        out = []
        for name, eps, idx in segs:
            have = sorted(idx)
            missing = [i for i in range(1, top + 1) if i not in idx]
            if not missing or not have or have[0] != 1:
                out.append((name, eps))
                continue
            if len(missing) > top * float(self.FILL_MAX_MISSING_RATIO):
                out.append((name, eps))     # 缺太多，多半不是同一套内容
                continue
            add = [i for i in missing if i in pool]
            if not add:
                out.append((name, eps))
                continue
            # 原位插入，不重排原有集：解不出序号的集（预告/彩蛋）留在原地，
            # 不会被 index=0 顶到第 1 集前面
            merged = list(eps)
            for i in sorted(add):
                pos = len(merged)
                for k, (_en, c) in enumerate(merged):
                    if (self._eps_index(c) or 0) > i:
                        pos = k
                        break
                merged.insert(pos, pool[i])
            mark = '' if name.endswith(self.FILL_MARK) else self.FILL_MARK
            out.append((name + mark, merged))
        return out
    # --- KISH_FILL_EPS END ---

    def _pack(self, vod, lines):
        """按源优先级排序 + 去重 + 唯一化线路名 + 写回 vod_play_from/url。"""
        try:
            lines = sorted(lines, key=lambda x: self._r4(x[0]))
        except Exception:
            pass
        lines = self._trim_lines(lines)
        if str(self.cfg.get('fill_missing', '1')).lower() not in (
                '0', 'false', 'no', 'off'):
            try:
                lines = self._drop_drift_lines(lines)
                lines = self._fill_missing_eps(lines)
            except Exception:
                pass
        froms, urls, used, seen_sig, taken = [], [], {}, set(), set()
        for name, eps in lines:
            if not eps:
                continue
            nm = clean_name(name) or '线路'
            # 去重签名带上首集播放码：光比「线路名 + 集数」会把不同源里
            # 恰好同名的线路当重复丢掉（比如两个源都叫「蓝光4K」且都是 24 集）
            sig = (nm, len(eps), str(eps[0][1])[:48])
            if sig in seen_sig:      # 同名同集数且同播放码 = 真重复，丢掉
                continue
            seen_sig.add(sig)
            # 名称唯一化：原来只看 used 会不会被用过，源站本来就叫
            # 「蓝光4K·2」时会和自动重命名撞出两条同名线路
            base_nm, n = nm, used.get(nm, 0)
            while nm in taken:
                n += 1
                nm = '%s·%d' % (base_nm, n)
            used[base_nm] = n
            taken.add(nm)
            froms.append(nm)
            urls.append('#'.join('%s$%s' % (e[0] or '正片', e[1]) for e in eps))
        vod['vod_play_from'] = '$$$'.join(froms)
        vod['vod_play_url'] = '$$$'.join(urls)
        return vod

    def detailContent(self, ids):
        if self._diag is not None:
            return self._diag.detailContent(ids)
        raw = ids[0] if isinstance(ids, (list, tuple)) and ids else ids
        tag, vid = self._dec_vid(raw)
        # 壳偶尔会拿空 id 回查（历史列表残留、解析失败）。不拦住就会真的
        # 拿空 id 去打源站，再返回一条 vod_id 为空的假记录，点进去必然播不出。
        if not vid:
            return {'list': []}
        ck = 'kish:%s:%s' % (tag, vid)
        hit = cache_get(ck)
        if hit is not None:
            try:
                return json.loads(hit)
            except Exception:
                pass

        ob = self._src(tag)
        if ob is None:
            return {'list': []}
        got = {}
        # 影探自己的 detailContent 会顺手并进 咕噜/橘汁/找剧，最长干等 4s
        # （DETAIL_BUDGET）；而外层 _fill_start 本来就要并发问同一批源 ——
        # 同一份工作做了两遍，详情页被硬拖到 4.9~5.8s。这里只取影探自家线路
        # （_base，实测 0.3~0.6s），跨源交给外层：实测 狂飙 4.91s→1.08s、
        # 漫长的季节 5.78s→0.92s、繁花 0.96s，线路内容与可播性不变
        # （外层并发拿到的是同一批源，只是换了实例、不再叠一层预算）。
        if tag == 'yt':
            try:
                st_t, st_v = ob._split_id(vid)
                base = ob._base(st_t, st_v) if st_t in ob.LABELS else None
                if base and base[2]:
                    # 用影探自己的 _render 拼（会把线路名加上「影探·」等前缀、
                    # 播放码按它的格式编码），产出与 detailContent 完全同构，
                    # 只是不含它内部补进来的 咕噜/橘汁/找剧
                    rv = ob._render(st_t, dict(base[1]), base[2], {})
                    rvl = (rv.get('list') or [{}])[0] if isinstance(rv, dict) else None
                    if isinstance(rvl, dict) and rvl.get('vod_play_from'):
                        got = {'list': [rvl]}
            except Exception:
                got = {}
        if not got:
            try:
                got = ob.detailContent([vid]) or {}
            except Exception:
                got = {}
        vod = (got.get('list') or [None])[0]
        if not isinstance(vod, dict):
            return {'list': []}

        title = str(vod.get('vod_name') or '')
        # 个别源（FoFo）详情只回数字 id 当片名，跨源补线路会全部匹配失败；
        # 用列表/搜索时记下的真实片名兜底，并修正壳里显示的名字。
        if len(title.strip()) < 2 or title.strip().isdigit():
            alt = _TITLE_MEMO.get(str(raw)) or ''
            if alt:
                title = alt
                vod['vod_name'] = alt
        vod['vod_id'] = self._enc_vid(tag, vod.get('vod_id') or vid)

        cid = str(vod.get('vod_id') or '')
        base_lines = []
        try:
            base_lines.extend(self._digest(tag, vod, cid))
        except Exception:
            pass

        # 其余源并发跑；首屏只等「够用」（FILL_BUDGET / FILL_ENOUGH），
        # 没赶上的源继续在后台补，补完直接刷新缓存。
        box, ths = self._fill_start(tag, title)
        # 基础线路本来就少时多给 0.7s：三体第一季主源 0.2s 就回来、但只有 2 条，
        # 其余源在 1.6s 内没赶上，用户看到的线路表直接少一半；线路多的片
        # （≥3 条基础线）不受影响，正常片仍是 1.6s 收工。
        _budget = self.FILL_BUDGET + (0.7 if len(base_lines) < 3 else 0.0)
        self._wait_yield(box, ths, base_lines, _budget)

        lines = list(base_lines) + self._digest_box(tag, box, cid)
        fresh = self._pack(dict(vod), lines)
        # 记 _pack 之后的顺序：换源时第一条就是最快的（小山·蓝光4K）
        _memo_detail(cid, _unpack_lines(fresh))
        result = {'list': [fresh]}
        try:
            cache_put(ck, json.dumps(result, ensure_ascii=False), self.CACHE_TTL)
        except Exception:
            pass

        if any(t.is_alive() for t in ths):
            # 后台补线可以跳过：闸门满了就这轮不补，用户下次进详情时源已热，
            # 结果一样完整。主路径此时已经返回，不受影响。
            _bg_spawn(self._topup,
                      (ck, vod, tag, base_lines, box, ths, cid), name='topup')
        self._prefetch_play(fresh)
        return result

    # ---------------- 播放预取 ----------------
    PREFETCH_DELAY = 0.25   # 详情返回后等这么久再预热首集（只让详情页先渲染完；
    #                         用户 1 秒内点播放时预取已经在跑，playerContent 会
    #                         合并这一次请求而不是重打一遍解析站）

    def _prefetch_play(self, vod):
        """详情页停一会儿就预热首集，把「点播放」的首播 5~6s 变成秒开。

        TVBox 的主路径就是「进详情 → 点第 1 集」，命中率很高。只预热一条
        线路的首集（优先真 4K），失败静默；结果走正常 playerContent 链路，
        自然落进各源自己的播放缓存。ext 传 {"prefetch":0} 可关。
        """
        if str(self.cfg.get('prefetch', '1')).lower() in ('0', 'false', 'no', 'off'):
            return
        try:
            cid = str(vod.get('vod_id') or '')
            if not cid or cid in _PREFETCHED:
                return
            froms = [x for x in str(vod.get('vod_play_from') or '').split('$$$') if x]
            urls = str(vod.get('vod_play_url') or '').split('$$$')
            if not froms or not urls:
                return
            pick = 0
            for i, nm in enumerate(froms):
                try:
                    if self._line_tier(nm) == 0:      # 有真 4K 就优先它
                        pick = i
                        break
                except Exception:
                    pass
            if pick >= len(urls):
                return
            first = str(urls[pick] or '').split('#')[0]
            if '$' not in first:
                return
            code = first.split('$', 1)[1].strip()
            if not code:
                return
            if len(_PREFETCHED) > 400:
                for x in list(_PREFETCHED)[:80]:
                    _PREFETCHED.discard(x)
            _PREFETCHED.add(cid)
            name = froms[pick]
        except Exception:
            return

        def run():
            time.sleep(self.PREFETCH_DELAY)
            try:
                self.playerContent(name, code)
            except Exception:
                pass
        if _bg_spawn(run, name='prefetch') is None:
            _PREFETCHED.discard(cid)      # 闸门满，这次没预取，别把片 id 记成已预取

    def _topup(self, ck, vod, tag, base_lines, box, ths, cid=''):
        """后台把没赶上的源等回来，再按双规则全量重裁写缓存。

        保护：
          - 旧缓存有真 4K、新结果没有 → 不覆盖
          - 双方同档时，线路数变少 → 不覆盖
        """
        try:
            deadline = time.time() + self.TOPUP_BUDGET
            for th in ths:
                th.join(max(0.05, deadline - time.time()))
            if not box:
                return
            lines = list(base_lines) + self._digest_box(tag, box, cid)
            if not lines:
                return
            out = self._pack(dict(vod), lines)
            _memo_detail(cid, _unpack_lines(out))

            def _stat(vod_obj):
                froms = [x for x in str(vod_obj.get('vod_play_from') or '')
                         .split('$$$') if x]
                n4 = sum(1 for n in froms if self._line_tier(n) == 0)
                return n4, len(froms)

            n4_new, n_new = _stat(out)
            _old = cache_get(ck)
            if _old:
                try:
                    _ov = (json.loads(_old).get('list') or [{}])[0]
                    n4_old, n_old = _stat(_ov)
                except Exception:
                    n4_old, n_old = 0, 0
                # 旧有 4K、新无 4K：不降级覆盖
                if n4_old > 0 and n4_new <= 0:
                    return
                # 同档（都有或都无 4K）但线路变少：不缩水
                if n4_old == n4_new and n_old > n_new:
                    return
                # 旧 4K 条数明显更多：保留旧的
                if n4_old > n4_new:
                    return
            cache_put(ck, json.dumps({'list': [out]}, ensure_ascii=False),
                      self.CACHE_TTL + 120)
        except Exception:
            pass

    # ---------------- 播放 ----------------
    def _strip_label(self, name, tag):
        """剥掉线路名前缀（「小山·蓝光4K」→「蓝光4K」），子源只认自己的原始 flag。"""
        s = str(name or '').strip()
        labs = [str(self.LABELS.get(tag) or '')]
        if tag == 'jn':
            labs.extend(['橘汁新', '橘汁'])   # 橘汁改过标签，旧缓存/旧详情仍带旧前缀
        for lab in labs:
            if not lab:
                continue
            for sep in ('·', '.', ' '):
                pref = lab + sep
                if s.startswith(pref):
                    return s[len(pref):]
        return s

    def playerContent(self, flag, id, vipFlags=None):
        # 统一出口做一次地址规范化：中文路径编码、去掉首尾空白。
        # 放在最外层，子源 / 换源 / 网页回落 三条路径都能覆盖到。
        #
        # 同一集合并：详情页预取和用户点播放可能几乎同时发生。原来两边各打一遍
        # 解析站（双倍请求，还可能触发限流），现在后来的那一个直接等前一个的结果。
        raw = id[0] if isinstance(id, (list, tuple)) and id else id
        key = str(raw)
        with _PLAY_INFLIGHT_LOCK:
            ent = _PLAY_INFLIGHT.get(key)
            owner = ent is None
            if owner:
                ent = [threading.Event(), {}]
                _PLAY_INFLIGHT[key] = ent
        if not owner:
            ent[0].wait(self.PLAY_HEAD + 2.5)
            if ent[1].get('r') is not None:
                return ent[1]['r']
        try:
            got = kish_fix_url(self._play_one(flag, id, vipFlags))
            if owner:
                ent[1]['r'] = got
            try:
                self._prefetch_next(id, got)
            except Exception:
                pass
            return got
        finally:
            if owner:
                ent[0].set()
                with _PLAY_INFLIGHT_LOCK:
                    _PLAY_INFLIGHT.pop(key, None)

    # ---------------- 连看预取 ----------------
    PREFETCH_NEXT_DELAY = 1.2
    _NEXT_PREFETCHED = set()
    _NEXT_LOCK = threading.Lock()

    def _prefetch_next(self, pid, got):
        """一集出流后，后台把同一线路的下一集也解析好。

        影探的每条线每一集都要先过解析站（0.2~0.9s，偶尔 3~5s），换集时
        用户就得盯着转圈。这里在本集返回后异步解析下一集，结果落进子源
        自己的播放缓存，用户点「下一集」时直接命中。只预取一条、只取紧随
        的那一集，失败静默。
        """
        if str(self.cfg.get('prefetch', '1')).lower() in ('0', 'false', 'no', 'off'):
            return
        if not kish_play_ok(got):
            return
        tag, _oflag, _p, cid, _ep = self._dec_play(pid)
        if tag != 'yt' or not cid:
            return          # 只有影探这条两跳链路有预取价值
        rec = _DETAIL_MEMO.get(str(cid))
        if not rec:
            return
        nxt = ''
        for _name, eps in rec[1]:
            for i, (_en, code) in enumerate(eps):
                if code == pid:
                    if i + 1 < len(eps):
                        nxt = eps[i + 1][1]
                    break
            if nxt:
                break
        if not nxt:
            return
        with self._NEXT_LOCK:
            if nxt in self._NEXT_PREFETCHED:
                return
            if len(self._NEXT_PREFETCHED) > 200:
                self._NEXT_PREFETCHED.clear()
            self._NEXT_PREFETCHED.add(nxt)
        nt, noflag, np_, _ncid, _nep = self._dec_play(nxt)
        ob = self._src(nt)
        if ob is None:
            with self._NEXT_LOCK:
                self._NEXT_PREFETCHED.discard(nxt)   # 源没构造出来，别记成已预取
            return
        use = self._strip_label(noflag or '', nt)

        def run():
            time.sleep(self.PREFETCH_NEXT_DELAY)
            ob.playerContent(use, np_, None)

        # 连看预取是最典型的「可跳过」任务，必须进闸门；被跳过就把 nxt 撤回，
        # 否则这一集的下一集被永久记成「预取过」，实际从没预取。
        if _bg_spawn(run, name='prefetch-next') is None:
            with self._NEXT_LOCK:
                self._NEXT_PREFETCHED.discard(nxt)

    # 线路实测高度记忆：kish_probe_height 按 URL 缓存，可每集 URL 都不同，
    # 等于每集都重新探一次 —— 实测「影探·移动云·4K」每集 1.2s，其中 1.0s
    # 全花在这个探测上，跳过就只剩 0.2s。画质是「这条线路」的属性而不是
    # 单集的，按（线路名 + 片）缓存，换集直接复用。
    #
    # key 必须带片。2026-11-21 实测：同一个线路名在不同片上指向完全不同的文件 ——
    # 「影探·天翼云·4K」在狂飙是 2160 的 MKV、在繁花是一条读不出高度的 MP4，
    # 「影探·联通云·4K」正好反过来。旧 key 只取线路名，于是 2160 会跨片复用，
    # 一条 1080 的片子借到别人的 2160 缓存值 → 假 4K 判定失效、该换源的不换，
    # 表现就是「有些播放源画质降级」。
    LINE_H_TTL = 600       # real：实测够，这条线确实是这个画质
    LINE_H_LOW_TTL = 120   # low：实测不够，读数可能是偶发子流，短缓存后重探
    LINE_H0_TTL = 60       # unknown：探不到，既不算真也不算假，别当已验真
    _LINE_H = {}
    _LINE_H_LOCK = threading.Lock()

    @staticmethod
    def _line_h_key(name, scope=''):
        nm = str(name or '')
        if not scope:
            return nm
        # scope = 源标记 + 片 id，而影探的片 id 本身就是一串带直链信息的
        # base64（200+ 字符）。只取摘要：key 更短、内存更省，也不会把
        # 直链碎片留在长驻字典里。同源同片同线路的摘要稳定。
        try:
            dg = hashlib.sha1(str(scope).encode('utf-8', 'replace')).hexdigest()[:12]
        except Exception:
            dg = str(len(str(scope)))
        return '%s\x1f%s' % (nm, dg)

    @staticmethod
    def _line_h_state(mh, name):
        """三档：real / low / unknown。

        探不到（unknown）既不当真 4K、也不当假 4K —— 实测 7/10 条 MP4 云盘线
        连 64KB 都读不出高度（moov 在尾部/302 到分片），把它当假 4K 会误杀
        真线，把它当真 4K 又等于没校验。只能记成未知、短 TTL 后重探。
        """
        if not mh:
            return 'unknown'
        return 'low' if kish_is_fake_claim(str(name or ''), mh) else 'real'

    def _line_h_cached(self, name, scope=''):
        """只读缓存、不打网络：返回 (状态, 高度)；没探过 → (None, 0)。"""
        with self._LINE_H_LOCK:
            hit = self._LINE_H.get(self._line_h_key(name, scope))
        if not hit:
            return None, 0
        return self._line_h_state(hit[1], name), hit[1]

    def _line_height(self, name, url, timeout=1.5, scope='', label=''):
        nm = str(name or '')
        if not nm:
            return kish_probe_height(url, timeout=timeout)
        key = self._line_h_key(nm, scope)
        now = time.time()
        with self._LINE_H_LOCK:
            hit = self._LINE_H.get(key)
        if hit:
            h = hit[1]
            st = self._line_h_state(h, nm)
            ttl = (self.LINE_H_TTL if st == 'real' else
                   self.LINE_H_LOW_TTL if st == 'low' else self.LINE_H0_TTL)
            if now - hit[0] < ttl:
                return h
        _t0 = time.time()
        mh = kish_probe_height(url, timeout=timeout)
        # 三档都写缓存，只是 TTL 不同：低值不再「永不缓存」（那等于每集重探
        # 1.2s），探空也不再记 3 分钟（那等于一条降级线有 3 分钟不去校验）。
        _st = self._line_h_state(mh, nm)
        # 日志里写展示名（「影探·天翼云·4K」），判定口径仍用源内名（nm）：
        # 用户在详情页看到的是展示名，得能对上号。
        _qdiag_add('probe', label or nm, kish_claim_height(nm), mh, _st,
                   time.time() - _t0)
        with self._LINE_H_LOCK:
            _cap_put(self._LINE_H, key, (now, mh), 400, drop=40)
        return mh

    def _race_pick(self, cid, ep, skip_pid, my_h, tag='yt'):
        """抢答候选：同片、同集、同一源、名义画质不低于当前线的另一条线路。

        影探和小山都要过解析站（两跳），单条线卡住时同源别的线往往还是通的
        ——「四渡」实测 6 条小山线里 3 条 0.1~0.3s 就出直链，而用户点的
        小哔4K 在解析站上空等 20s，之前只有 yt 会抢答，sz 就干耗着。
        跨源抢答不做：别的源慢是真的没内容，抢也抢不出东西，还会白多打
        一次上游。集匹配跟换源同一套规则 —— 剧集必须集名或集序号一致，
        只有单集正片（电影）才允许直接顶，否则会播错集。
        """
        rec = _DETAIL_MEMO.get(str(cid))
        if not rec:
            return None
        wi, _, wn = str(ep or '').partition('\x1e')
        max_eps = max([len(e) for _n, e in rec[1]] or [0])
        single = max_eps <= 1
        for _name, eps in rec[1]:
            for e_name, code in eps:
                t, f, p, _c, _e = self._dec_play(code)
                if t != tag or not p or p == skip_pid:
                    continue
                if ep:
                    hi, _, hn = str(_e or '').partition('\x1e')
                    if not ((wn and wn == hn) or (wi and wi == hi)):
                        if not single:
                            continue
                # 名义画质不能降级：用户点的 4K 不能被一条 1080 抢走
                if kish_claim_height(self._qname(f)) < my_h:
                    continue
                return f, p
        return None

    def _race_start(self, cid, ep, skip_pid, my_h, tag='yt'):
        """开一条抢答线程。→ (线程, 结果箱, 线路名) 或 None。"""
        pick = self._race_pick(cid, ep, skip_pid, my_h, tag)
        if not pick:
            return None
        flag, pid = pick
        ob = self._src(tag)
        if ob is None:
            return None
        use = self._strip_label(flag, tag)
        box = {}

        def work():
            try:
                box['r'] = ob.playerContent(use or flag, pid, None)
            except Exception:
                pass

        t = threading.Thread(target=work, daemon=True, name='kish-race')
        t.start()
        nm = self._qname(flag)
        _qdiag_add('play', nm, kish_claim_height(nm), 0, 'race', 0, 'start')
        return t, box, nm

    def _race_wait(self, race, box, deadline):
        """等主线路或抢答任一给出可用地址；抢答赢时写回 box 并打标记。"""
        rbox = race[1]
        while time.time() < deadline:
            if kish_play_ok(box.get('r')):
                return False
            if kish_play_ok(rbox.get('r')):
                box['r'] = rbox.get('r')
                box['_race'] = True
                _qdiag_add('play', race[2], 0, 0, 'race', 0, 'win')
                return True
            time.sleep(0.05)
        if kish_play_ok(box.get('r')):
            return False
        if kish_play_ok(rbox.get('r')):
            box['r'] = rbox.get('r')
            box['_race'] = True
            _qdiag_add('play', race[2], 0, 0, 'race', 0, 'win')
            return True
        return False

    def _play_one(self, flag, id, vipFlags=None):
        if self._diag is not None:
            return self._diag.playerContent(flag, id, vipFlags)
        tag, oflag, pid, cid, ep = self._dec_play(id)
        empty = {'parse': 0, 'jx': 0, 'url': ''}
        # 抢答救回来的结果也按本线路记一笔：这条线自己解析不出来，下次点它
        # 不该再白等 RACE_AFTER 才转抢答（实测重播因此从 1.2s 变 0.00s）。
        agg_key = 'aggplay:%s' % str(pid or '')
        agg_hit = cache_get(agg_key)
        if isinstance(agg_hit, dict) and kish_play_ok(agg_hit):
            return agg_hit
        # 壳可能把展示名「片帝·4K官方C」「河豚·蓝光4K」当 flag 传入；
        # 编码里的 oflag 一般是源原始名，优先用它，并剥掉源前缀再交给子源。
        use_flag = self._strip_label(oflag or flag, tag)
        ob = self._src(tag)
        box = {}

        def work():
            try:
                box['r'] = ob.playerContent(use_flag or flag, pid, vipFlags)
            except Exception:
                pass

        th = None
        race = None
        t_start = time.time()
        head = self.PLAY_HEAD_SLOW.get(tag, self.PLAY_HEAD)
        if ob is not None:
            th = threading.Thread(target=work)
            th.daemon = True
            th.start()
            # 先只等 RACE_AFTER：快线（实测 0.44~1.0s）在这里就已经回来了，
            # 走原路径、不发第二个请求。超过还在跑，说明这一次解析卡住，
            # 对影探（两跳、卡解析站最明显）并行再开一条同片线抢答。
            th.join(min(self.RACE_AFTER, head))
            # 影探、小山都是「取票 + 解析」两跳，卡住时同源其它线常常还通
            # （「四渡」小哔4K 解析站 20s 超时，同片 4K/小腾4K 0.15s 出直链）。
            # 别的源不加：它们慢就是真没内容，抢答只会白打上游。
            if (tag in ('yt', 'sz') and not kish_play_ok(box.get('r'))
                    and th.is_alive()):
                try:
                    race = self._race_start(cid, ep, pid,
                                            kish_claim_height(self._qname(oflag or flag)),
                                            tag)
                except Exception:
                    race = None
            if race is not None:
                self._race_wait(race, box, t_start + head)
            else:
                th.join(max(0.1, head - self.RACE_AFTER))
        got = box.get('r')
        if kish_play_ok(got) and box.get('_race'):
            # 抢答赢的：已经等了 RACE_AFTER 以上，再叠一次高度探测只会让用户
            # 多等，候选在 _race_pick 里已经卡过「名义画质不降级」，直接出流。
            # 只缓存真直链（parse=0）：parse=1 是「交壳解析」的兜底地址，
            # 把它记 10 分钟会让同一条线一直拿兜底，而主线程稍后解出的
            # 真直链本来就在子源缓存里，下次该走那条秒开的路。
            try:
                if not int((got or {}).get('parse') or 0):
                    cache_put(agg_key, got, 600)
            except Exception:
                pass
            return got
        if kish_play_ok(got):
            # 实测分辨率：影探「4K」线路可能实为 1080（如绝命毒师）→ 换其它源真 4K
            try:
                claim_name = self._qname(oflag or flag or '')
                # 「4K」有时只写在聚合侧展示名里（「未来4K·kl」的源前缀自带 4K，
                # 但它的 kl 线实测是 1080 TS 流），所以先剥掉非画质源前缀再比：
                # 取两者中宣称更高的那个当探测口径，_qname 保证前缀里的 4K 不算宣称。
                if kish_claim_height(self._qname(flag)) > kish_claim_height(claim_name):
                    claim_name = self._qname(flag)
                # 诊断日志用壳传来的展示名，用户点的是哪个名字就记哪个
                show_name = self._qname(flag) or claim_name
                play_u = str((got or {}).get('url') or '')
                try:
                    parse0 = int((got or {}).get('parse') or 0)
                except Exception:
                    parse0 = 0
                claim_h = kish_claim_height(claim_name)
                # 四源4K 的「4K」是营销词：实测 1080 的线按 1080 处理 —— 既省一次
                # 注定读不到高度的探测（它给的是纯媒体清单，没有 RESOLUTION），
                # 也不会把本源最好的 1080 线误判成假 4K 再换到更差的线路。
                _wh4 = sk4_measure(claim_name) or sk4_measure(self._qname(flag))
                if _wh4:
                    claim_h = _wh4[1]
                # parse=1 又没宣称画质：壳自己去嗅探，没有可探的东西，直接放行
                if parse0 and not claim_h:
                    return got
                mh = 0
                # parse=1 一般是「解析接口」（小山 4K 的 jx4k.api），探它只有 0，
                # 白等 1.2s；但地址本身就是 m3u8/mp4 的照旧要探（有些源两种都给）
                _probe = (not parse0) or bool(_KISH_MEDIA_RE.search(play_u))
                if play_u.startswith('http') and _probe:
                    # 一次请求同时拿「实测高度」和「响应内容类型」：
                    #   - 高度用来判假 4K（影探「4K」线路可能实为 1080）
                    #   - 类型用来抓「状态 200 但根本不是媒体」的假地址 —— 教父系列
                    #     的 v.youku.com/v_show/id_xxx 没有 .html 后缀，旧规则只按
                    #     后缀认播放页，于是 parse=0 的优酷页面被当视频交给壳，必黑屏；
                    #     djvod 那批 /upic/ 封面图地址则回 404。
                    # 探测不到高度很常见（媒体列表不写 RESOLUTION、纯 ts 切片、
                    # CDN 不认 Range），所以 mh==0 本身不算死链，只看状态码和类型。
                    # parse=1 的地址是「解析接口」而不是媒体本身（小山 4K 那批
                    # jx4k.fuyingapi.top/api/?key=…），探它只会白等 1.2s 拿回 0。
                    # 只对宣称 4K/2K 的线探高度：假 4K 才是要抓的（影探「4K」实为
                    # 1080）。1080 线探一次要多花 0.5~1.5s，而片帝等源现在线路名
                    # 带「1080P-」前缀，全探会让首播明显变慢；详情阶段（_probe_1080
                    # _candidates）本来也是按 >=1440 才探，这里与它统一口径。
                    if claim_h >= 1440:
                        mh = self._line_height(
                            claim_name, play_u,
                            scope='%s|%s' % (tag or '', pid or ''),
                            label=show_name)
                    kind = kish_url_kind(play_u)
                    hst = kish_url_status(play_u)
                    # 408/425/429 是超时/限流，不是死链（meilinvps 打密了回 429，
                    # 返回体本身就是一页 HTML，不能拿内容类型当死链判据）
                    soft = hst in (408, 425, 429)
                    dead = 400 <= hst < 600 and not soft
                    if dead or (kind in ('html', 'json') and not soft):
                        left = max(1.0, self.PLAY_BUDGET - (time.time() - t_start))
                        # 死链换源收紧到 2.5s：真坏线路试两条就够，别让用户
                        # 干等到 PLAY_BUDGET（实测教父3 国语那条空转了 5.4s）
                        alt_dead = self._play_other(
                            cid, ep, tag, pid,
                            budget=min(2.5, left * 0.7))
                        if alt_dead and kish_play_ok(alt_dead):
                            return alt_dead
                        # 同片其它源没有这一集（多音轨电影拆出来的「国语/
                        # 同声评论」在别家根本不存在）→ 回退本线路正片
                        aud = self._play_audio_fallback(cid, tag, oflag, pid, ep)
                        if aud:
                            return aud
                if mh and kish_is_fake_claim(claim_name, mh):
                    # 只为「换个更清楚的」而换源，同样要卡预算：默认不传 budget
                    # 等于给满 PLAY_BUDGET(11s)，实测奥本海默一条假 4K 拖到 13.5s
                    left = max(1.0, self.PLAY_BUDGET - (time.time() - t_start))
                    alt0 = self._play_other(cid, ep, tag, pid,
                                            budget=min(2.5, left * 0.7))
                    if alt0 and kish_play_ok(alt0):
                        try:
                            mh2 = kish_probe_height(str(alt0.get('url') or ''), timeout=1.2)
                            if not mh2 or mh2 >= mh:
                                _qdiag_add('play', show_name, claim_h, mh, 'low',
                                           0, 'swap')
                                return alt0
                        except Exception:
                            _qdiag_add('play', show_name, claim_h, mh, 'low',
                                       0, 'swap')
                            return alt0
                    # 换源失败：仍播本线，但标记实测高度
                    _qdiag_add('play', show_name, claim_h, mh, 'low', 0, 'keep')
                if mh and isinstance(got, dict):
                    got = dict(got)
                    got['kish_h'] = mh
                    if kish_is_fake_claim(claim_name, mh):
                        got['kish_fake4k'] = 1
            except Exception:
                pass
            return got
        # 取流失败或太慢/假 4K·2K → 同集换源；换源也失败再等本线路收尾
        left = max(1.0, self.PLAY_BUDGET - (time.time() - t_start))
        # 换源上限 3.0s：好线路基本都在 1s 内回，余下的都是坏源，等满
        # left*0.7（实测 7.5s）只会让用户对着转圈干等（教父3 优酷页那条）
        alt = self._play_other(cid, ep, tag, pid, budget=min(3.0, left * 0.7))
        if alt and kish_play_ok(alt):
            return alt
        if th is not None and th.is_alive():
            # 本源线程已经超过首屏窗口还在跑（实测小山 4K 要 17~20s），
            # 再等满 PLAY_BUDGET 是白等：最多再给 2s，然后按现状返回
            th.join(min(2.0, max(0.1, self.PLAY_BUDGET - (time.time() - t_start))))
            got = box.get('r')
            if kish_play_ok(got):
                return got
        if isinstance(got, dict):
            # 所有线路都只回了网页：直接丢给播放器必黑屏，改成 parse=1 让壳去嗅探，
            # 至少还有一次机会（例如腾讯/爱奇艺的播放页）。
            try:
                u = str(got.get('url') or '')
                parse = int(got.get('parse') or 0)
            except Exception:
                u, parse = '', 0
            if u.startswith('http') and parse <= 0 and _kish_is_page(u):
                got = dict(got)
                got['parse'] = 1
            return got
        return empty

    def _call(self, fn, wait):
        """带超时调用：超时就先当失败，线程自己跑完就丢。"""
        box = {}
        def w():
            try:
                box['r'] = fn()
            except Exception:
                pass
        th = threading.Thread(target=w)
        th.daemon = True
        th.start()
        th.join(wait)
        return box.get('r'), th

    # 音轨拆分特征：老片源常把同一部电影拆成「英语 / 国语 / 同声评论」几条线路，
    # 这里的「集」其实是音轨而不是分集。某条音轨的地址挂了，换源换个遍也没用
    # （别家只有一条正片，没有这个音轨），回退本线路正片至少能看到片子。
    # 剧集的集名是「第N集」，不含这些词，不会误触发。
    _AUDIO_WORDS = ('国语', '英语', '粤语', '原声', '同声', '普通话')

    def _play_audio_fallback(self, cid, tag, oflag, pid, ep):
        """多音轨线路的某条音轨死了 → 回退同线路正片（集名不带音轨词的那条）。"""
        _wi, _, wn = str(ep or '').partition('\x1e')
        if not wn or not any(k in wn for k in self._AUDIO_WORDS):
            return None
        rec = _DETAIL_MEMO.get(str(cid))
        if not rec:
            return None
        best = None
        for _name, eps in rec[1]:
            # 真分集线路不做这种回退（错集会播错内容）
            if len(eps) < 2 or len(eps) > 6:
                continue
            for _n, code in eps:
                t, f, p, _c, e = self._dec_play(code)
                if t != tag or f != oflag or p == pid:
                    continue
                idx, _, nm = str(e or '').partition('\x1e')
                # 同声评论那条多半也是坏的，优先挑干净的正片
                if '同声' in nm or '评论' in nm:
                    continue
                try:
                    i = int(idx or 0)
                except Exception:
                    i = 99
                if best is None or i < best[0]:
                    best = (i, f, p)
        if not best:
            return None
        ob = self._src(tag)
        if ob is None:
            return None
        # 子源认的是剥掉源前缀的原始线路名（「影探·优酷·1080P」→「优酷·1080P」）。
        # 必须带超时：这里是兜底路径，卡住就把整次播放拖到十几秒。
        try:
            r, _th = self._call(
                lambda: ob.playerContent(self._strip_label(best[1], tag),
                                         best[2], None), 1.6)
        except Exception:
            return None
        return r if kish_play_ok(r) else None

    def _play_other(self, cid, ep, skip_tag='', skip_pid='', budget=None):
        """同集换源重试：先试别的源（失效常是整源坏），本源其它线路垫后。"""
        rec = _DETAIL_MEMO.get(cid)
        if not rec:
            return None
        deadline = time.time() + (self.PLAY_BUDGET if budget is None
                                  else max(0.5, budget))
        wi, _, wn = str(ep or '').partition('\x1e')
        # 电影被拆成「英语/国语/同声评论」多音轨时，各源只给一条「正片」，
        # 按集名/序号严格匹配永远换不到源 —— 这类片允许跨音轨取别家的正片。
        # 用最大集数兜住范围：只有单集~几集的电影走这条，剧集（几十集）不动。
        _max_eps = max([len(e) for _n, e in rec[1]] or [0])
        _film = _max_eps <= 6
        # 整片只有一集（纯电影）：别家那唯一一集必然是同一部片，跨线路换不算错集
        _single = _max_eps <= 1
        _audio = bool(wn) and any(k in wn for k in self._AUDIO_WORDS)
        cand = []
        for _name, eps in rec[1]:
            for e_name, code in eps:
                t, f, p, _c, _e = self._dec_play(code)
                if not t:
                    continue          # 解不出源，别塞进候选白试一遍
                if ep:
                    hi, _, hn = str(_e or '').partition('\x1e')
                    # 集名一致、或集序号一致，都算同一集
                    if not ((wn and wn == hn) or (wi and wi == hi)):
                        # 同音轨互救之外，只给「单集正片」开一个口子，别家
                        # 10 集的剧集里随便找一集顶上就是播错内容了；
                        # 对方集名是「第N集」的也当分集处理，不跨
                        if not (_single or (
                                _film and _audio and len(eps) == 1
                                and not re.search(r'第\s*\d+\s*[集话期]',
                                                  str(e_name or '')))):
                            continue
                if t == skip_tag and p == skip_pid:
                    continue
                cand.append((1 if t == skip_tag else 0, t, f, p))
        cand.sort(key=lambda x: (x[0], self.PLAY_SPEED.get(x[1], 9)))
        tried = 0
        seen = set()
        for _pri, t, f, p in cand:
            if time.time() > deadline or tried >= self.PLAY_TRY:
                return None
            # 同一片同一线路已经实测「不够格」的，别再解析+重探一遍：
            # 缓存 key 带源+片，是这片自己测出来的，不会跨片误伤。
            # 日志名带源标签：换源候选的 f 是源内线路名（「蓝光4K【推荐】」），
            # 不带源名用户根本对不上是哪个源的哪条线。
            _dn = '%s·%s' % (self.LABELS.get(t, t), self._qname(f))
            _st_c, _h_c = self._line_h_cached(self._qname(f), '%s|%s' % (t, p))
            if _st_c == 'low':
                _qdiag_add('skip', _dn, kish_claim_height(self._qname(f)),
                           _h_c, 'low', 0, 'skip')
                continue
            tried += 1
            ob = self._src(t)
            if ob is None:
                continue
            # 剥源前缀，避免「小山·蓝光4K」整串进子源
            ff = self._strip_label(f, t)
            r, _th = self._call(lambda ob=ob, ff=ff, p=p: ob.playerContent(ff, p, []),
                                min(self.PLAY_EACH,
                                    max(0.3, deadline - time.time())))
            try:
                u = str((r or {}).get('url') or '')
                parse = int((r or {}).get('parse') or 0)
            except Exception:
                u, parse = '', 0
            # 不同线路常解析到同一个流（实测「小山·4K」「河豚·蓝光4K」
            # 「影探·腾讯」三条线共用同一条 meilinvps 地址），试第二次纯属浪费
            if u and u in seen:
                continue
            if u:
                seen.add(u)
            if kish_play_ok(r):
                # 4K/2K 候选先探高度（那一步会顺手写状态码与类型缓存，
                # 后面的死链判定就免费了）；其余候选走 8KB 轻量验活。
                mh = 0
                # 四源4K 的 1080 线名字里也带 4K，按实测判档就不必再探（它的
                # 清单不带 RESOLUTION，探了只有 0，白花 1.2s）；其余源照旧。
                _wh4 = sk4_measure(self._qname(f)) or sk4_measure(f)
                _claim4 = _wh4[1] if _wh4 else kish_claim_height(self._qname(f))
                if _claim4 >= 1440 and u.startswith('http'):
                    try:
                        mh = self._line_height(self._qname(f), u, timeout=1.2,
                                               scope='%s|%s' % (t, p), label=_dn)
                    except Exception:
                        mh = 0
                # 已知死链别再交给播放器：djvod 那批 /upic/ 地址恒 400，
                # 交出去就是黑屏（实测小山 4K 换源换回来的正是它）。
                # 没探过的地址补一次 8KB 轻量验活，别为它跑 512KB。
                if u.startswith('http') and (not parse
                                             or _KISH_MEDIA_RE.search(u)):
                    hst = kish_url_status(u)
                    if not hst:
                        # 带上子源给播放器的请求头（Referer/UA）验活，
                        # 免得把「只认 Referer 的 CDN」误判成死链
                        hdr = (r or {}).get('header')
                        if isinstance(hdr, str):
                            try:
                                hdr = json.loads(hdr)
                            except Exception:
                                hdr = None
                        hst = kish_probe_light(
                            u, timeout=min(1.0, max(0.3, deadline - time.time())),
                            headers=hdr if isinstance(hdr, dict) else None)
                    if ((400 <= hst < 600 and hst not in (408, 425, 429))
                            or kish_url_kind_cached(u) in ('html', 'json')):
                        continue
                if mh and kish_is_fake_claim(str(f or ''), mh):
                    _qdiag_add('drop', _dn, kish_claim_height(self._qname(f)),
                               mh, 'low', 0, 'drop')
                    continue
                if mh and isinstance(r, dict):
                    r = dict(r)
                    r['kish_h'] = mh
                return r
        return None


# 部分内核按小写 spider 取类
spider = Spider
