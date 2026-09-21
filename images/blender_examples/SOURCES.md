# Blender作例（デフォルメ／写実）の参考画像 元ネタ一覧

「愛車デミオをBlenderで擬人化キャラにする」案（書籍の終盤章／コラム候補）を検討する際に、
デフォルメ寄りと写実寄りのイメージを比べるために集めた参考画像の出典メモ。

- 取得日: 2026-09-21
- 取得方法: Claude（コーディングエージェント）が Web検索・WebFetch でページを調べ、画像URLを `curl` で取得
- 画像の置き場所: `images/blender_examples/`（`images/` は `.gitignore` 対象のため、画像は git には入らない。
  出典を履歴として残すため、この `SOURCES.md` だけ `git add -f` で追跡している）
- **利用範囲: 個人的な参考用のみ。書籍への掲載・再配布は不可。**
  いずれもライセンス（利用許諾）を確認できていない、または権利者が明確に別にいる画像。
  書籍に載せたい場合は、CC等で利用条件が明確な素材に差し替えるか、自作のレンダリングを使うこと。
- 加工: 画像自体は無加工。ただし `deformed_lowpoly_cartoon_car.png` のみ、取得元がWebP形式だったため
  PNGに変換している。

## デフォルメ寄り（擬人化・簡略化）

### deformed_final_windshield.jpeg
- 内容: フロントガラスに白目と黒目を貼った、Pixar「カーズ」方式の擬人化車（Blender作例）。
  ボディは通常の車のまま、目だけ足している。
- 出典ページ: [Want to make an eye rig for your anthropomorphic car model? No problem! - Blender Artists](https://blenderartists.org/t/want-to-make-an-eye-rig-for-your-anthropomorphic-car-model-no-problem/1552102)
- 画像URL: https://blenderartists.org/uploads/default/original/4X/b/9/2/b926d169010fa59af94236db75186ba82a3ddaab.jpeg
- 投稿者・ライセンス: 未確認（フォーラム投稿画像。権利は投稿者に帰属するものとして扱う）

### deformed_pixar_wireframe_ref.jpeg
- 内容: 映画「カーズ」の3Dモデルのワイヤーフレーム（メーター・ドック等のキャラクター）。
  目をフロントガラス、口をバンパー／グリルに割り当てる擬人化の考え方が分かる。
- 出典ページ: 上記と同じ Blender Artists のスレッド（スレッド内で参考画像として貼られていたもの）
- 画像URL: https://blenderartists.org/uploads/default/original/4X/b/f/9/bf98bd0e66532f9617dc57149fa19e4f67a56b01.jpeg
- 権利: 画像に Alamy（ストックフォト）の透かしが入っている。元の映像の権利はPixar/Disney。
  利用不可。

### deformed_lowpoly_cartoon_car.png
- 内容: ボディを角ばらせ、タイヤを大きくし、ヘッドライトを目に見立てた低ポリの漫画風カー。
  ボディ自体をデフォルメした例。
- 出典: BlenderKit の「Stylized cartoon Car lowpoly」（作者: Mohammad Darvishi。検索結果のタイトル表記による）
  - 元ページ: https://www.blenderkit.com/asset-gallery-detail/1581c78b-2632-43bc-99de-e693506d5d10/
  - 実際に画像URLを確認したページ: https://www.blendkit.com/asset-gallery-detail/1581c78b-2632-43bc-99de-e693506d5d10/
    （blenderkit.com からのリダイレクト先。BlenderKitのミラーと思われるが未検証）
- 画像URL（512x512サムネイル）: https://public.blenderkit.com/thumbnails/assets/958e66866b88498b828af1c9e9e9195a/files/thumbnail_20800912-8d76-4ab4-a834-2082ecff1901.jpg.512x512_q85.jpg.webp
- ライセンス: 未確認（BlenderKitのアセットはアセットごとにライセンスが異なるため、利用するなら要確認）

## 写実寄り（実車の曲面を再現したBlender作例）

### realistic_mazda3_front.png / realistic_mazda3_rear.png
- 内容: 2019年型 Mazda 3 のフォトリアルなレンダリング。フロントは 2880×1620、リアは 1440×810。
  グリルの網目、ホイール、ナンバープレート等まで作り込まれている。
- 出典ページ: [Mazda 3 (2019) - Finished Projects - Blender Artists](https://blenderartists.org/t/mazda-3-2019/1482934)
- 画像URL:
  - フロント: https://blenderartists.org/uploads/default/original/4X/8/6/a/86a8c6401bd828e6dc5127b9a186985fdb9154b0.png
  - リア: https://blenderartists.org/uploads/default/original/4X/5/2/d/52d8f629afc604564ea853d205dd9f7594167707.png
- 投稿者・ライセンス: 未確認。マツダのデザイン（ロゴ・車体形状）自体の権利もマツダ側にある。

### realistic_cx30_car.jpeg / realistic_cx30_car2.jpeg
- 内容: Mazda CX-30 のレンダリング（1920×1080）。
  検索結果の要約では「制作に約15時間」とあったが、これは検索要約による情報で、スレッド本文では未確認。
- 出典ページ: [Blender | Realistic car - Finished Projects - Blender Artists](https://blenderartists.org/t/blender-realistic-car/1476279)
- 画像URL:
  - car: https://blenderartists.org/uploads/default/original/4X/1/f/4/1f4be88d8192d0f6a12fe9996265e18b73edf480.jpeg
  - car2: https://blenderartists.org/uploads/default/original/4X/7/a/4/7a4f24deff36e60deea029364949abdb9c4f2e12.jpeg
- 投稿者・ライセンス: 未確認。上と同様にマツダ側の権利もある。

## 取得を試みたが使えなかった候補（参考）

- Blender公式デモファイル（BMW27）: 公式のデモファイル一覧ページにはBMW27の記載が見当たらなかった
  （ファイル自体は https://download.blender.org/demo/test/BMW27.blend.zip にあるとの検索結果あり。プレビュー画像は未取得）
- Blend Swap「BMW 1 Series M In Cycles」: サーバーエラー(HTTP 525)で取得できず
- Free3D「Cartoon Car」一覧: アクセス拒否(HTTP 403)で取得できず

## この比較から言えること（メモ）

- デフォルメ寄りは「目（フロントガラスやヘッドライト）を足す」だけでも顔になり、工数が小さい。
  ボディ自体を丸める/角ばらせるところまでやると「キャラ」らしさは増すが、モデリングの作業量も増える。
- 写実寄りは曲面・グリル・ホイールの再現度が全てで、工数が読みにくい。
- 本書では、解析パイプラインで抽出したサイドビュー輪郭を押し出してボディの土台にし、目を足す
  デフォルメ寄りが現実的、という方針を検討している（未決定）。
