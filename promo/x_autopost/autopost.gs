// 自動投稿の本体。シートから独立したスクリプト（script.google.com で作る）に、common.gs と一緒に貼る。
// APIキーとシートIDはスクリプトプロパティに置く：
//   SHEET_ID, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
// 初回は setupSheet() を1回、以後は postDue() を15分ごとの時間トリガーで動かす。

var ACCOUNT = 'hirosuban';
var SHEET_POSTS = '投稿';
var SHEET_RULES = 'ルール';
var SHEET_PROMPT = 'AIプロンプト';
var SHEET_SETTINGS = '設定';

// 投稿シートの列（1始まり）
var COL = { PART: 1, TEXT: 2, LEN: 3, CHECK: 4, IMAGES: 5, WHEN: 6, STATUS: 7, URL: 8, POSTED_AT: 9, NOTE: 10, AUTHOR: 11 };
var HEADERS = ['パート', '本文', '文字数', 'チェック', '画像（ドライブのリンク・最大4枚・カンマ区切り）',
  '投稿日時', '状態', '投稿URL', '投稿した日時', 'エラー・メモ', '書いた人'];
var STATUS = { DRAFT: '下書き', OK: '投稿OK', POSTED: '投稿済み', ERROR: 'エラー' };
var TEST_MARK = '[テスト済み]';
var MAX_IMAGE_BYTES = 5 * 1024 * 1024;
var IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

var RULES = [
  ['どのパートの話かを頭に書く', '1つのアカウントで3人分を投稿するので、本文の先頭に【デミオ編】のようにパート名を入れる。書くのは自分のパートのことだけ。合同誌全体の告知（日付・価格・買える場所）は@hirosubanが書く。'],
  ['ハッシュタグは #技術書典 と #SYK出版 の2つ', 'ナンバリング付きの #技術書典21 は使わない。タグを増やしすぎない。（2.12・3.1）'],
  ['その1本だけで何の話か分かるように', '流れてきた1投稿だけを見た人にも、技術書典で出る合同誌の話だと分かるように書く。告知なら、いつ・どこで買えるかを入れる。（3.5・3.6）'],
  ['日付は具体的に', '「明日」ではなく「11/xx(日)」。直前になったら「今週日曜（11/xx）」のように近さも分かる書き方にする。（3.3）'],
  ['画像を付ける', '表紙がまだなら、原稿の画面キャプチャや作業中の写真でよい。（3.4）'],
  ['決まっていないことや途中経過も出す', '仮タイトル、書いている途中の悩み、うまくいかなかったことも投稿のネタになる。（2.1〜2.3）'],
  ['自分のパートを卑下しない', '「大した内容じゃないけど」は書かない。面白いところを素直に書く。（3.2）'],
  ['同じ文章のコピペはしない', '告知の繰り返しでも、毎回新しい情報を1つ入れる。（3.10）'],
  ['「こちら」で済ませない', '「試し読みはこちら」ではなく「BOOTHで試し読みできます」のように、どこで何ができるかを書く。（3.7）'],
  ['実際にやったこと・本当の数字だけ', '盛った数字や、まだやっていないことを書かない。'],
  ['個人情報を出さない', '住所や勤務先、生活圏が分かる写真や位置情報は載せない。'],
  ['1週間以上空けない', '誰かが毎週1本は出せるように、投稿OKの行が尽きそうなら書き足す。自動投稿は1日2本まで・3時間以上空けて出る。（2.1）'],
  ['長さは280まで', '日本語は1文字を2と数えるので、全角で140字くらい。「文字数」列で確認できる。'],
];

var FLOW = [
  '「投稿」シートに1行書く：パート・本文・投稿日時。書いた人の欄に自分の名前。',
  '画像は共有フォルダ「SYK出版 宣伝」に置き、ファイルのリンクを「画像」列に貼る（最大4枚、カンマ区切り）。',
  '「チェック」列がOKになるまで直す。「注意」は投稿されるが、一度見直す。',
  '出してよければ「状態」を「投稿OK」にする。投稿日時を過ぎると、15分以内に@hirosubanから自動で投稿される。',
  '「エラー」になったら「エラー・メモ」列の理由を見て直し、もう一度「投稿OK」にする。',
  '「投稿済み」の行は書き換えない。Xの投稿はあとから編集できないので、直すなら@hirosubanに消してもらう。',
];

var PROMPT_TEMPLATE = [
  'あなたは技術書典に出る合同誌（サークル：SYK出版、著者3人）の宣伝を手伝っています。著者の一人が、自分の担当パートを宣伝するX投稿の案を求めています。投稿はサークルの1つのアカウント（@hirosuban）から出ます。',
  '',
  'パート名：【ここにパート名】',
  '素材メモ（ここに無い事実・数字・予定は作らないこと）：',
  '【ここに最近やったこと・パートで書いている内容】',
  '',
  '守るルール：',
].concat(RULES.map(function (r, i) { return (i + 1) + '. ' + r[0] + '：' + r[1]; })).concat([
  '',
  '書き方：',
  '- 本文の先頭に【パート名】を置き、末尾に #技術書典 #SYK出版 を付ける。',
  '- 全角で120字前後に収める（Xの数え方で280以内。日本語は1文字2）。',
  '- 3案は切り口を変える（例：途中経過、苦労した点、読者が得られること）。',
  '- 開催日はまだ決まっていない。日付を書くなら「11月末の技術書典」までにする。',
  '',
  '出力：3案それぞれについて、本文と、付けるとよい画像の提案を書いてください。',
]).join('\n');

// ---------------------------------------------------------------- シートの準備（初回に1回）

function setupSheet() {
  var ss = openSheet_();
  var me = Session.getEffectiveUser().getEmail();

  var posts = sheetOrCreate_(ss, SHEET_POSTS);
  posts.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]).setFontWeight('bold').setBackground('#dcefeb');
  posts.setFrozenRows(1);
  posts.getRange(2, COL.LEN).setFormula('=XLEN(B2:B)');
  posts.getRange(2, COL.CHECK).setFormula('=XCHECK(B2:B, A2:A)');
  posts.getRange('B2:B').setWrap(true);
  posts.getRange('D2:D').setWrap(true);
  posts.getRange('F2:F').setNumberFormat('yyyy/mm/dd hh:mm')
    .setDataValidation(SpreadsheetApp.newDataValidation().requireDate().setAllowInvalid(false)
      .setHelpText('日付と時刻を入れてください（例：2026/10/25 20:00）').build());
  posts.getRange('I2:I').setNumberFormat('yyyy/mm/dd hh:mm');
  posts.getRange('G2:G').setDataValidation(SpreadsheetApp.newDataValidation()
    .requireValueInList([STATUS.DRAFT, STATUS.OK, STATUS.POSTED, STATUS.ERROR], true).build());
  [140, 420, 70, 260, 260, 140, 90, 220, 140, 260, 100].forEach(function (w, i) { posts.setColumnWidth(i + 1, w); });

  var rules = sheetOrCreate_(ss, SHEET_RULES);
  rules.clear();
  var rows = [['投稿までの流れ', '']].concat(FLOW.map(function (f, i) { return [(i + 1) + '.', f]; }))
    .concat([['', ''], ['投稿ルール', '「届ける工夫 改訂第2版」（mochikoAsTech）をもとに決めた。括弧内は元の本の節番号。']])
    .concat(RULES.map(function (r) { return [r[0], r[1]]; }));
  rules.getRange(1, 1, rows.length, 2).setValues(rows).setWrap(true).setVerticalAlignment('top');
  rules.getRange(1, 1).setFontWeight('bold');
  rules.getRange(FLOW.length + 3, 1).setFontWeight('bold');
  rules.setColumnWidth(1, 260);
  rules.setColumnWidth(2, 640);

  var prompt = sheetOrCreate_(ss, SHEET_PROMPT);
  prompt.clear();
  prompt.getRange(1, 1).setValue('普段使っているAI（ChatGPTなど）に、下のセルをまるごとコピーして貼り、【 】の2か所を書き換えて送る。').setFontWeight('bold');
  prompt.getRange(3, 1).setValue(PROMPT_TEMPLATE).setWrap(true).setVerticalAlignment('top');
  prompt.setColumnWidth(1, 900);

  var settings = sheetOrCreate_(ss, SHEET_SETTINGS);
  if (!settings.getRange(1, 1).getValue()) {
    settings.getRange(1, 1, 5, 3).setValues([
      ['自動投稿', 'テスト', 'ON：投稿する／OFF：何もしない／テスト：投稿せず、出す予定の内容をメールで知らせる'],
      ['1日の上限本数', 2, ''],
      ['投稿の最小間隔（時間）', 3, ''],
      ['通知メール', me, 'エラーとテスト結果の送り先'],
      ['', '', ''],
    ]);
    settings.getRange('B1').setDataValidation(SpreadsheetApp.newDataValidation()
      .requireValueInList(['ON', 'OFF', 'テスト'], true).build());
    settings.setColumnWidth(1, 200);
    settings.setColumnWidth(3, 520);
  }

  // スクリプトが書く列と設定は、オーナーだけが編集できるようにする
  ss.getProtections(SpreadsheetApp.ProtectionType.RANGE).concat(ss.getProtections(SpreadsheetApp.ProtectionType.SHEET))
    .forEach(function (p) { if (/^自動投稿：/.test(p.getDescription())) p.remove(); });
  protectForMe_(posts.getRange('C:D').protect().setDescription('自動投稿：計算列'), me);
  protectForMe_(posts.getRange('H:J').protect().setDescription('自動投稿：スクリプトが書く列'), me);
  protectForMe_(settings.protect().setDescription('自動投稿：設定'), me);
  protectForMe_(rules.protect().setDescription('自動投稿：ルール'), me);

  Logger.log('準備できました：' + ss.getUrl());
}

// ---------------------------------------------------------------- 自動投稿（15分ごと）

function postDue() {
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) return;
  try {
    var ss = openSheet_();
    var settings = readSettings_(ss);
    if (settings.mode === 'OFF') return;

    var sheet = ss.getSheetByName(SHEET_POSTS);
    var last = sheet.getLastRow();
    if (last < 2) return;
    var values = sheet.getRange(2, 1, last - 1, HEADERS.length).getValues();
    var now = new Date();

    var rows = values.map(function (v, i) { return { row: i + 2, v: v }; });
    var due = rows.filter(function (r) {
      if (r.v[COL.STATUS - 1] !== STATUS.OK) return false;
      var when = r.v[COL.WHEN - 1];
      if (!(when instanceof Date) || when > now) return false;
      return !(settings.mode === 'テスト' && String(r.v[COL.NOTE - 1]).indexOf(TEST_MARK) === 0);
    }).sort(function (a, b) { return a.v[COL.WHEN - 1] - b.v[COL.WHEN - 1]; });
    if (!due.length) return;

    // ペースの上限：越えるなら今回は出さず、次の回に回す
    var postedTimes = rows.map(function (r) { return r.v[COL.POSTED_AT - 1]; })
      .filter(function (d) { return d instanceof Date; });
    var today = Utilities.formatDate(now, 'Asia/Tokyo', 'yyyy-MM-dd');
    var todayCount = postedTimes.filter(function (d) { return Utilities.formatDate(d, 'Asia/Tokyo', 'yyyy-MM-dd') === today; }).length;
    var lastPosted = postedTimes.reduce(function (a, d) { return !a || d > a ? d : a; }, null);
    if (settings.mode === 'ON') {
      if (todayCount >= settings.dailyLimit) return;
      if (lastPosted && now - lastPosted < settings.minGapHours * 3600 * 1000) return;
    }

    var target = due[0];
    var part = target.v[COL.PART - 1];
    var text = String(target.v[COL.TEXT - 1]).trim();
    var problems = checkPost(text, part).errors;
    var images = [];
    try { images = loadImages_(target.v[COL.IMAGES - 1]); } catch (e) { problems.push(e.message); }

    if (problems.length) {
      markError_(sheet, target.row, problems.join('／'), settings);
      return;
    }

    if (settings.mode === 'テスト') {
      sheet.getRange(target.row, COL.NOTE).setValue(TEST_MARK + ' ' + stamp_(now) + ' この内容で投稿できます（まだ投稿していません）');
      notify_(settings, '【テスト】次に自動投稿される内容（' + part + '）',
        text + '\n\n画像：' + (images.map(function (b) { return b.getName(); }).join(', ') || 'なし') +
        '\n行：' + target.row + '\n\n「設定」の自動投稿をONにすると、この内容で投稿されます。');
      return;
    }

    try {
      var mediaIds = images.map(uploadMedia_);
      var body = { text: text };
      if (mediaIds.length) body.media = { media_ids: mediaIds };
      var res = xPost_('https://api.x.com/2/tweets', body);
      var id = res.data && res.data.id;
      if (!id) throw new Error('投稿IDが返ってこなかった：' + JSON.stringify(res).slice(0, 300));
      sheet.getRange(target.row, COL.STATUS).setValue(STATUS.POSTED);
      sheet.getRange(target.row, COL.URL).setValue('https://x.com/' + ACCOUNT + '/status/' + id);
      sheet.getRange(target.row, COL.POSTED_AT).setValue(now);
      sheet.getRange(target.row, COL.NOTE).setValue('');
    } catch (e) {
      markError_(sheet, target.row, '投稿に失敗：' + e.message, settings);
    }
  } finally {
    lock.releaseLock();
  }
}

// ---------------------------------------------------------------- X API

function uploadMedia_(blob) {
  var res = xPost_('https://api.x.com/2/media/upload', {
    media: Utilities.base64Encode(blob.getBytes()),
    media_category: 'tweet_image',
  });
  var id = res.data && res.data.id;
  if (!id) throw new Error('画像のアップロードでIDが返ってこなかった（' + blob.getName() + '）');
  return String(id);
}

// JSONボディはOAuth 1.0aの署名対象に含めない（署名するのはoauth_*パラメータとクエリだけ）
function xPost_(url, payload) {
  var resp = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    headers: { Authorization: oauthHeader_('POST', url) },
    muteHttpExceptions: true,
  });
  var code = resp.getResponseCode();
  var text = resp.getContentText();
  if (code >= 300) throw new Error('X API ' + code + '：' + text.slice(0, 300));
  return JSON.parse(text);
}

function oauthHeader_(method, url) {
  var props = PropertiesService.getScriptProperties();
  var oauth = {
    oauth_consumer_key: requireProp_(props, 'X_API_KEY'),
    oauth_nonce: Utilities.getUuid().replace(/-/g, ''),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: String(Math.floor(Date.now() / 1000)),
    oauth_token: requireProp_(props, 'X_ACCESS_TOKEN'),
    oauth_version: '1.0',
  };
  var paramString = Object.keys(oauth).sort().map(function (k) { return pct_(k) + '=' + pct_(oauth[k]); }).join('&');
  var base = [method.toUpperCase(), pct_(url), pct_(paramString)].join('&');
  var key = pct_(requireProp_(props, 'X_API_SECRET')) + '&' + pct_(requireProp_(props, 'X_ACCESS_TOKEN_SECRET'));
  oauth.oauth_signature = Utilities.base64Encode(
    Utilities.computeHmacSignature(Utilities.MacAlgorithm.HMAC_SHA_1, base, key, Utilities.Charset.UTF_8));
  return 'OAuth ' + Object.keys(oauth).sort().map(function (k) { return pct_(k) + '="' + pct_(oauth[k]) + '"'; }).join(', ');
}

// RFC 3986のパーセントエンコード（encodeURIComponentが残す !'()* も変換する）
function pct_(s) {
  return encodeURIComponent(s).replace(/[!'()*]/g, function (c) { return '%' + c.charCodeAt(0).toString(16).toUpperCase(); });
}

// ---------------------------------------------------------------- 補助

function openSheet_() {
  return SpreadsheetApp.openById(requireProp_(PropertiesService.getScriptProperties(), 'SHEET_ID'));
}

function requireProp_(props, name) {
  var v = props.getProperty(name);
  if (!v) throw new Error('スクリプトプロパティ ' + name + ' が未設定です');
  return v;
}

function sheetOrCreate_(ss, name) {
  return ss.getSheetByName(name) || ss.insertSheet(name);
}

function protectForMe_(protection, me) {
  protection.addEditor(me);
  protection.removeEditors(protection.getEditors().filter(function (u) { return u.getEmail() !== me; }));
  if (protection.canDomainEdit()) protection.setDomainEdit(false);
}

function readSettings_(ss) {
  var sheet = ss.getSheetByName(SHEET_SETTINGS);
  var map = {};
  if (sheet && sheet.getLastRow() > 0) {
    sheet.getRange(1, 1, sheet.getLastRow(), 2).getValues().forEach(function (r) { map[String(r[0]).trim()] = r[1]; });
  }
  var mode = String(map['自動投稿'] || 'OFF').trim();
  return {
    mode: ['ON', 'OFF', 'テスト'].indexOf(mode) === -1 ? 'OFF' : mode,
    dailyLimit: Number(map['1日の上限本数']) || 2,
    minGapHours: Number(map['投稿の最小間隔（時間）']) || 3,
    email: String(map['通知メール'] || Session.getEffectiveUser().getEmail()),
  };
}

// 画像列のドライブのリンク（/d/<ID>/ や ?id=<ID>）から画像を読む
function loadImages_(cell) {
  var links = String(cell || '').split(/[,、\s]+/).filter(function (s) { return s; });
  if (links.length > 4) throw new Error('画像は4枚まで（' + links.length + '枚ある）');
  return links.map(function (link) {
    var m = link.match(/\/d\/([\w-]+)/) || link.match(/[?&]id=([\w-]+)/);
    if (!m) throw new Error('ドライブのファイルのリンクではない：' + link);
    var file;
    try { file = DriveApp.getFileById(m[1]); } catch (e) { throw new Error('画像を開けない（共有フォルダに置いたか確認）：' + link); }
    var blob = file.getBlob();
    if (IMAGE_TYPES.indexOf(blob.getContentType()) === -1) throw new Error('画像ではない：' + file.getName());
    if (blob.getBytes().length > MAX_IMAGE_BYTES) throw new Error('5MBを超えている：' + file.getName());
    return blob;
  });
}

function markError_(sheet, row, message, settings) {
  sheet.getRange(row, COL.STATUS).setValue(STATUS.ERROR);
  sheet.getRange(row, COL.NOTE).setValue(stamp_(new Date()) + ' ' + message);
  notify_(settings, '【エラー】自動投稿できなかった行があります（' + row + '行目）', message + '\n\n' + sheet.getParent().getUrl());
}

function notify_(settings, subject, body) {
  Logger.log(subject + '\n' + body);
  if (settings.email) MailApp.sendEmail(settings.email, 'SYK出版 自動投稿：' + subject, body);
}

function stamp_(d) {
  return Utilities.formatDate(d, 'Asia/Tokyo', 'MM/dd HH:mm');
}
