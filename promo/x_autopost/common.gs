// 本文の文字数とルールのチェック。
// シートに紐づくスクリプト（文字数・チェック列の計算）と、自動投稿の独立スクリプトの両方に
// 同じ内容を貼る。片方だけ直すと、シートではOKなのに投稿時に弾かれる、ということが起きる。

var X_TAGS = ['#技術書典', '#SYK出版'];
var X_MAX = 280;

// Xの加重文字数。この範囲の文字は1、それ以外（日本語・絵文字など）は2、URLは一律23。
var X_ONE_WEIGHT = [[0x0000, 0x10FF], [0x2000, 0x200D], [0x2010, 0x201F], [0x2032, 0x2037]];
var X_SELF_DEPRECATION = ['大したこと', '大した内容', 'つまらない', '面白くない', '需要ない', '誰も買わ'];

function xlen(text) {
  var t = String(text || '').normalize('NFC').replace(/https?:\/\/\S+/g, new Array(24).join('x'));
  var n = 0;
  for (var i = 0; i < t.length; i++) {
    var c = t.codePointAt(i);
    if (c > 0xFFFF) i++; // サロゲートペアは1文字として数える
    var one = false;
    for (var j = 0; j < X_ONE_WEIGHT.length; j++) {
      if (c >= X_ONE_WEIGHT[j][0] && c <= X_ONE_WEIGHT[j][1]) { one = true; break; }
    }
    n += one ? 1 : 2;
  }
  return n;
}

// errors があると投稿しない。warnings は投稿するが見直してほしい点。
function checkPost(text, part) {
  var t = String(text || '').trim();
  var p = String(part || '').trim();
  var errors = [];
  var warnings = [];
  if (!t) return { errors: ['本文が空'], warnings: [] };
  var n = xlen(t);
  if (n > X_MAX) errors.push('長すぎる（' + n + ' / ' + X_MAX + '）');
  if (!p) errors.push('パート名が空');
  else if (t.indexOf('【' + p + '】') !== 0) errors.push('先頭に【' + p + '】がない');
  X_TAGS.forEach(function (tag) { if (t.indexOf(tag) === -1) errors.push(tag + ' がない'); });
  if (/#技術書典\d/.test(t)) errors.push('#技術書典 に番号が付いている');
  if (/(明日|明後日|あさって|来週|今度の)/.test(t) && !/\d{1,2}\/\d{1,2}|\d{1,2}月\d{1,2}日/.test(t)) {
    warnings.push('「明日」などに具体的な日付がない');
  }
  if (t.indexOf('こちら') !== -1) warnings.push('「こちら」で済ませている');
  if (X_SELF_DEPRECATION.some(function (w) { return t.indexOf(w) !== -1; })) warnings.push('自分のパートを卑下していないか');
  if (/https?:\/\//.test(t)) warnings.push('リンク入りは投稿料が高い（約$0.20）');
  return { errors: errors, warnings: warnings };
}

function formatCheck(result) {
  var parts = [];
  if (result.errors.length) parts.push('NG：' + result.errors.join('／'));
  if (result.warnings.length) parts.push('注意：' + result.warnings.join('／'));
  return parts.length ? parts.join('　') : 'OK';
}
