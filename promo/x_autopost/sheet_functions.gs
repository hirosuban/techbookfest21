// シートに紐づくスクリプト用（拡張機能 → Apps Script）。common.gs と一緒に貼る。
// APIキーはここに置かない。シートの編集者は、このスクリプトを見られる。

/**
 * Xの加重文字数（日本語は2、URLは23）。範囲を渡すと行ごとに返す。
 * @param {string|Array} input 本文、または本文の列
 * @customfunction
 */
function XLEN(input) {
  if (!Array.isArray(input)) return input === '' ? '' : xlen(input);
  return input.map(function (row) { return [row[0] === '' ? '' : xlen(row[0])]; });
}

/**
 * 投稿ルールのチェック結果（OK / NG：… / 注意：…）。範囲を渡すと行ごとに返す。
 * @param {string|Array} texts 本文、または本文の列
 * @param {string|Array} parts パート名、またはパート名の列
 * @customfunction
 */
function XCHECK(texts, parts) {
  if (!Array.isArray(texts)) return texts === '' ? '' : formatCheck(checkPost(texts, parts));
  return texts.map(function (row, i) {
    if (row[0] === '') return [''];
    var part = Array.isArray(parts) ? (parts[i] || [''])[0] : parts;
    return [formatCheck(checkPost(row[0], part))];
  });
}
