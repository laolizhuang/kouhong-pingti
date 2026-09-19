const 邮箱 = "2833909485@qq.com";
const 首页标题 = "觅色 — 口红平替色号库";
const 首页简介 = "觅色收录常见口红色号与同色系平替。点开自己挑，复制淘口令或点购买进店。图为示意图，屏幕有色差。广告：下单并结算后可能产生佣金。";
const 教学 = [
  ["口红图片/口红教学/01.png", "1. 打底保湿", "先涂薄薄一层润唇膏"],
  ["口红图片/口红教学/02.png", "2. 勾勒唇峰", "从唇峰两点开始画轮廓"],
  ["口红图片/口红教学/03.png", "3. 填满上唇", "沿着唇线往中间填色"],
  ["口红图片/口红教学/04.png", "4. 填满下唇", "从下唇中央向外推开"],
  ["口红图片/口红教学/05.png", "5. 抿匀修角", "轻轻抿一下，修齐嘴角"],
  ["口红图片/口红教学/06.png", "6. 完成", "左右对称就可以出门了"],
];

let 库 = [];
let 平替展开id = "";

function $(sel) {
  return document.querySelector(sel);
}

function 转义(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function 资源根() {
  return /\/p\/[^/]+\.html$/i.test(location.pathname) ? "../" : "";
}

function 图(src, alt, extra = "") {
  const 前 = 资源根();
  const url = /^(https?:)?\/\//.test(src) ? src : 前 + src;
  const fallback = 前 + "口红图片/tomato.png";
  return `<img src="${转义(url)}" alt="${转义(alt)}" loading="lazy" decoding="async" ${extra} onerror="this.onerror=null;this.src='${转义(fallback)}'">`;
}

function 介绍地址(id) {
  return 资源根() + "p/" + encodeURIComponent(id) + ".html";
}

function 解析路由() {
  if (window.MISE_PRESELECT) return { 页: "介绍", id: window.MISE_PRESELECT };
  const file = location.pathname.match(/\/p\/([^/]+)\.html$/i);
  if (file) return { 页: "介绍", id: decodeURIComponent(file[1]) };
  const raw = decodeURIComponent((location.hash || "#/").replace(/^#/, ""));
  const parts = raw.split("/").filter(Boolean);
  if (parts[0] === "i" && parts[1]) return { 页: "介绍", id: parts.slice(1).join("/") };
  return { 页: "全库" };
}

function 去介绍(id) {
  平替展开id = "";
  location.href = 介绍地址(id);
}

function 回全库() {
  平替展开id = "";
  location.href = 资源根() + "index.html";
}

function 写页头(当前) {
  const desc = document.querySelector('meta[name="description"]');
  if (!当前) {
    document.title = 首页标题;
    if (desc) desc.setAttribute("content", 首页简介);
    return;
  }
  document.title = `${当前.全名} 介绍与同色平替 | 觅色`;
  const 摘要 = String(当前.介绍 || 当前.说明 || "").slice(0, 80);
  if (desc) {
    desc.setAttribute(
      "content",
      `${摘要} 图为示意图。广告：点购买或用淘口令进店，结算后可能有佣金。`
    );
  }
}

function 妆效匹配(妆效, 偏好) {
  if (偏好 === "不限") return true;
  if (偏好 === "哑光/雾面") return 妆效 === "哑光" || 妆效 === "雾面";
  if (偏好 === "润泽/水光") return 妆效 === "润泽" || 妆效 === "水光";
  return 妆效 === 偏好;
}

function 找平替(当前, 预算, 妆效偏好, 只看更便宜) {
  return 库
    .filter((x) => {
      if (x.id === 当前.id) return false;
      if (x.色系 !== 当前.色系) return false;
      if (!妆效匹配(x.妆效, 妆效偏好)) return false;
      if (只看更便宜 && x.价格 > 预算) return false;
      return true;
    })
    .sort((a, b) => a.价格 - b.价格);
}

function 购买区(当前) {
  const 渠道 = 当前.佣金渠道;
  let 按钮 = "去购买";
  if (渠道 === "京东") 按钮 = "去京东购买";
  if (渠道 === "拼多多") 按钮 = "去拼多多购买";
  if (渠道 === "唯品会") 按钮 = "去唯品会购买";
  const 口令钮 = 当前.淘口令
    ? `<button class="btn ghost copy-kouling" type="button">复制淘口令</button>`
    : "";
  const 口令 = 当前.淘口令
    ? `<p class="cap">微信打不开链接时：复制口令，打开淘宝 APP 粘贴，就能进这支商品</p>
       <div class="kouling">${转义(当前.淘口令)}</div>`
    : "";
  return `<div class="buy">
    <div class="ad">广告 · 点购买或用淘口令进店，下单并结算后可能产生佣金</div>
    <div class="row">${口令钮}<a class="btn" href="${转义(当前.购买链接)}" target="_blank" rel="noopener noreferrer">${按钮}</a></div>
    ${口令}
  </div>`;
}

function 详细介绍(当前) {
  return `
    <h2>${转义(当前.全名)}</h2>
    <p>${转义(当前.品牌)} · ${转义(当前.名称)} · ${转义(当前.色号)}　｜　${转义(当前.色系)} · ${转义(当前.妆效)}　｜　参考价 ¥${当前.价格}</p>
    <p class="cap">下面是示意图，不是实拍保证。屏幕有色差，下手前请对照实物试色。</p>
    <div class="intro">${转义(当前.介绍)}</div>
    ${购买区(当前)}
    <div class="shots">
      <figure>${图(当前.图片, 当前.全名)}<figcaption>色号示意图</figcaption></figure>
      <figure>${图(当前.未涂, "素唇示意图")}<figcaption>素唇示意图</figcaption></figure>
      <figure>${图(当前.涂抹, "涂抹示意图")}<figcaption>涂抹示意图</figcaption></figure>
      <figure>${图(当前.涂好, "上嘴示意图")}<figcaption>上嘴示意图</figcaption></figure>
    </div>
    <div class="swatch" style="background:${转义(当前.色卡)};width:160px;margin-top:12px"></div>
  `;
}

function 建议箱() {
  return `<section class="box" id="suggest">
    <h3>建议箱</h3>
    <p class="cap">全库没有你要的色号？写在这里，我们后面补进去。</p>
    <textarea id="suggest-text" rows="3" placeholder="例如：YSL 小金条 21、香奈儿 58、某支豆沙色"></textarea>
    <div class="row"><button class="btn" type="button" id="suggest-btn">投进建议箱</button></div>
    <p class="cap" id="suggest-msg"></p>
  </section>`;
}

function 画出全库() {
  const 品牌们 = ["全部品牌", ...[...new Set(库.map((x) => x.品牌))].sort()];
  const 色系们 = ["全部色系", ...[...new Set(库.map((x) => x.色系))].sort()];
  $("#app").innerHTML = `
    ${图("口红图片/banner.png", "觅色", 'class="banner"')}
    <h1 class="hero-title">觅色</h1>
    <p class="hero-caption">全库 ${库.length} 支 · 点一支进介绍，可复制淘口令</p>
    <h2>口红全库</h2>
    <div class="filters">
      <input id="q" placeholder="例如：405、Chili、豆沙、完美日记">
      <select id="brand">${品牌们.map((b) => `<option>${转义(b)}</option>`).join("")}</select>
      <select id="tone">${色系们.map((b) => `<option>${转义(b)}</option>`).join("")}</select>
    </div>
    <div class="count" id="count"></div>
    <div class="grid" id="grid"></div>
    <p class="hint">点开任意口红进入介绍页。图是示意图，屏幕有色差，下手前请对照实物试色。微信打不开网页时，用介绍页的淘口令。没收录的名字可以投进最下面的建议箱。</p>
    <h2>先学怎么涂</h2>
    <p class="cap">对照每张图做一遍，就不会花、不会歪。</p>
    <div class="teach">${教学.map(([src, t, d]) => `<div>${图(src, t)}<p><b>${t}</b></p><p class="cap">${d}</p></div>`).join("")}</div>
    ${建议箱()}
  `;
  const 刷新 = () => {
    const q = ($("#q").value || "").trim().toLowerCase();
    const brand = $("#brand").value;
    const tone = $("#tone").value;
    const list = 库.filter((x) => {
      if (brand !== "全部品牌" && x.品牌 !== brand) return false;
      if (tone !== "全部色系" && x.色系 !== tone) return false;
      if (q && !`${x.全名} ${x.色系} ${x.说明}`.toLowerCase().includes(q)) return false;
      return true;
    });
    $("#count").textContent = `当前显示 ${list.length} / ${库.length} 支，点击色号进入介绍`;
    $("#grid").innerHTML = list.length
      ? list
          .map(
            (x) => `<a class="pick" href="${转义(介绍地址(x.id))}">
              ${图(x.图片, x.全名)}
              <div class="swatch" style="background:${转义(x.色卡)}"></div>
              <b>${转义(x.简称)}</b>
            </a>`
          )
          .join("")
      : `<p class="hint">全库暂时没有这个关键词，可以把色号写到最下面的建议箱。</p>`;
  };
  $("#q").oninput = 刷新;
  $("#brand").onchange = 刷新;
  $("#tone").onchange = 刷新;
  绑建议箱();
  刷新();
}

function 画出介绍(当前) {
  const 预算 = Number(sessionStorage.getItem("预算") || 150);
  const 妆效 = sessionStorage.getItem("妆效") || "不限";
  const 只看 = sessionStorage.getItem("只看") !== "0";
  const 平替们 = 找平替(当前, 预算, 妆效, 只看);
  const 展开 = 库.find((x) => x.id === 平替展开id);
  $("#app").innerHTML = `
    <div class="back"><button class="btn ghost" type="button" id="back">← 返回全库</button></div>
    ${详细介绍(当前)}
    <hr>
    <h3>同色系平替</h3>
    <div class="filters">
      <label class="cap">最高预算（元）
        <input id="budget" type="range" min="30" max="500" step="10" value="${预算}">
        <span id="budget-label">${预算}</span>
      </label>
      <label class="cap">妆效
        <select id="fx">
          ${["不限", "哑光/雾面", "丝绒", "润泽/水光"].map((x) => `<option ${x === 妆效 ? "selected" : ""}>${x}</option>`).join("")}
        </select>
      </label>
      <label class="cap"><input id="cheap" type="checkbox" ${只看 ? "checked" : ""}> 只看不超过预算的平替</label>
    </div>
    <div id="dupes"></div>
    ${建议箱()}
  `;
  const 画平替 = () => {
    const b = Number($("#budget").value);
    const fx = $("#fx").value;
    const cheap = $("#cheap").checked;
    sessionStorage.setItem("预算", String(b));
    sessionStorage.setItem("妆效", fx);
    sessionStorage.setItem("只看", cheap ? "1" : "0");
    $("#budget-label").textContent = b;
    const list = 找平替(当前, b, fx, cheap);
    const 展开2 = 库.find((x) => x.id === 平替展开id);
    $("#dupes").innerHTML = list.length
      ? `<p class="cap">找到 ${list.length} 支和「${转义(当前.全名)}」同色系的平替，点查看介绍会在下面展开</p>
         <div class="dupe-grid">${list
           .map(
             (x) => `<div class="dupe-card">
               ${图(x.图片, x.全名)}
               <div class="swatch" style="background:${转义(x.色卡)}"></div>
               <b>${转义(x.全名)}</b>
               <p class="cap">${转义(x.色系)} · ${转义(x.妆效)}</p>
               <p class="price">¥ ${x.价格}</p>
               <p class="meta">${转义(x.说明)}</p>
               <button class="btn" type="button" data-dupe="${转义(x.id)}">查看介绍</button>
             </div>`
           )
           .join("")}</div>
         ${
           展开2
             ? `<div id="dupe-intro"><hr><h3>这支平替的介绍</h3>${详细介绍(展开2)}</div>`
             : ""
         }`
      : `<p class="hint">这支暂时没有合适平替，可以把需求写到最下面的建议箱。</p>`;
    $("#dupes").onclick = (e) => {
      const btn = e.target.closest("[data-dupe]");
      if (!btn) return;
      平替展开id = btn.dataset.dupe;
      画平替();
      const el = $("#dupe-intro");
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    };
    绑复制口令();
  };
  $("#back").onclick = 回全库;
  $("#budget").oninput = 画平替;
  $("#fx").onchange = 画平替;
  $("#cheap").onchange = 画平替;
  绑建议箱();
  画平替();
  绑复制口令();
}

function 绑复制口令() {
  document.querySelectorAll(".copy-kouling").forEach((btn) => {
    btn.onclick = async () => {
      const box = btn.closest(".buy")?.querySelector(".kouling");
      const text = box ? box.textContent : "";
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = "已复制";
      } catch (e) {
        btn.textContent = "请长按复制";
      }
    };
  });
}

function 绑建议箱() {
  const btn = $("#suggest-btn");
  if (!btn) return;
  btn.onclick = () => {
    const 内容 = ($("#suggest-text").value || "").trim();
    const msg = $("#suggest-msg");
    if (!内容) {
      msg.textContent = "请先写下你想找的口红";
      msg.className = "warn";
      return;
    }
    const href = `mailto:${邮箱}?subject=${encodeURIComponent("【觅色】建议箱新留言")}&body=${encodeURIComponent(内容)}`;
    location.href = href;
    $("#suggest-text").value = "";
    msg.textContent = "已打开邮箱。发出去后我们会看到。";
    msg.className = "ok";
  };
}

function 渲染() {
  window.scrollTo(0, 0);
  const 路由 = 解析路由();
  if (路由.页 === "介绍") {
    const 当前 = 库.find((x) => x.id === 路由.id);
    if (!当前) {
      回全库();
      return;
    }
    写页头(当前);
    画出介绍(当前);
    window.scrollTo(0, 0);
    return;
  }
  写页头(null);
  画出全库();
  window.scrollTo(0, 0);
}

async function 启动() {
  if (/MicroMessenger/i.test(navigator.userAgent)) {
    document.body.classList.add("in-wechat");
  }
  const res = await fetch(资源根() + "kouhong.json");
  库 = await res.json();
  window.addEventListener("hashchange", 渲染);
  渲染();
}

启动().catch(() => {
  $("#app").innerHTML = "<p>口红数据没加载出来，请刷新再试。</p>";
});
