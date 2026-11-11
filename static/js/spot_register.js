// スポット登録画面（FCSR001）：位置指定・写真プレビュー・入力チェック
(function () {
  var cfg = window.OFRAA;
  var form = document.getElementById("spotForm");
  var floorSel = document.getElementById("floorSelect");
  var mapArea = document.getElementById("mapArea");
  var mapImg = document.getElementById("mapImg");
  var mapWrap = document.getElementById("mapWrap");
  var marker = document.getElementById("marker");
  var posX = document.getElementById("posX");
  var posY = document.getElementById("posY");
  var posText = document.getElementById("posText");
  var hint = document.getElementById("mapHint");
  var photo = document.getElementById("photoFile");
  var preview = document.getElementById("preview");

  function setError(name, msg) {
    var el = document.querySelector('.field-error[data-for="' + name + '"]');
    if (el) el.textContent = msg || "";
  }

  function mapUrlFor(floorId) {
    for (var i = 0; i < cfg.floors.length; i++) {
      if (String(cfg.floors[i].id) === String(floorId)) return cfg.floors[i].mapUrl;
    }
    return "";
  }

  function clearPosition() {
    posX.value = ""; posY.value = "";
    marker.hidden = true; posText.textContent = "";
  }

  function showMarker() {
    if (!posX.value || !posY.value || !mapImg.naturalWidth) return;
    var r = mapImg.getBoundingClientRect();
    marker.style.left = (posX.value * r.width / mapImg.naturalWidth) + "px";
    marker.style.top = (posY.value * r.height / mapImg.naturalHeight) + "px";
    marker.hidden = false;
    posText.textContent = "指定した位置：X=" + posX.value + "、Y=" + posY.value;
  }

  function loadMap() {
    var url = mapUrlFor(floorSel.value);
    if (!url) { mapImg.removeAttribute("src"); hint.textContent = "フロアを選んでから、登録したい地点をクリックしてください。"; return; }
    hint.textContent = "登録したい地点をクリックしてください。";
    mapImg.onload = showMarker;
    mapImg.src = url;
  }

  // 位置指定ボタン：マップを表示する
  document.getElementById("positionBtn").addEventListener("click", function () {
    mapArea.hidden = false;
    if (!floorSel.value) { setError("floorSelect", "先にフロアを選択してください。"); return; }
    setError("floorSelect", "");
    loadMap();
  });

  // フロアを変えたら地図を切り替え、指定済みの位置は消す
  floorSel.addEventListener("change", function () {
    clearPosition();
    if (!mapArea.hidden) loadMap();
  });

  // マップをクリックして位置を指定（画像の実寸に換算して保存）
  mapWrap.addEventListener("click", function (e) {
    if (!mapImg.naturalWidth) return;
    var r = mapImg.getBoundingClientRect();
    posX.value = Math.round((e.clientX - r.left) * mapImg.naturalWidth / r.width);
    posY.value = Math.round((e.clientY - r.top) * mapImg.naturalHeight / r.height);
    setError("position", "");
    showMarker();
  });
  window.addEventListener("resize", showMarker);

  // 写真プレビュー
  photo.addEventListener("change", function () {
    preview.innerHTML = "";
    Array.prototype.forEach.call(photo.files, function (f) {
      if (!/^image\/(jpeg|png)$/.test(f.type)) return;
      var img = document.createElement("img");
      img.src = URL.createObjectURL(f);
      preview.appendChild(img);
    });
  });

  // 送信前の入力チェック（サーバー側でも同じチェックをする）
  form.addEventListener("submit", function (e) {
    var ok = true;
    function fail(name, msg) { setError(name, msg); ok = false; }
    ["spotName", "typeSelect", "floorSelect", "position", "detail", "photoFile"].forEach(function (n) { setError(n, ""); });

    var name = document.getElementById("spotName").value.trim();
    if (!name) fail("spotName", "スポット名を入力してください。");
    else if (name.length > cfg.nameMax) fail("spotName", "スポット名は" + cfg.nameMax + "文字以内で入力してください。");
    if (!document.getElementById("typeSelect").value) fail("typeSelect", "種別を選択してください。");
    if (!floorSel.value) fail("floorSelect", "フロアを選択してください。");
    if (!posX.value || !posY.value) fail("position", "マップ上で位置を指定してください。");
    if (document.getElementById("detail").value.length > cfg.detailMax) fail("detail", "詳細・説明は" + cfg.detailMax + "文字以内で入力してください。");

    var files = photo.files;
    if (files.length > cfg.maxFiles) fail("photoFile", "写真は最大" + cfg.maxFiles + "枚までです。");
    else {
      for (var i = 0; i < files.length; i++) {
        if (!/\.(jpe?g|png)$/i.test(files[i].name)) { fail("photoFile", "写真は jpg / png のみ登録できます。"); break; }
        if (files[i].size > cfg.maxSize) { fail("photoFile", "写真は1枚5MB以内にしてください。"); break; }
      }
    }
    if (!ok) e.preventDefault();
  });

  // サーバーのエラーで戻ってきたとき、選択済みのフロアと位置を復元する
  if (floorSel.value) { mapArea.hidden = false; loadMap(); }
})();
