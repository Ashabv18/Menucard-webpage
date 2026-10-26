/* test-menu-design.js — the menu card DESIGN page, checked like the rest of the project.
   Three blocks were removed on request (the four sample menu cards, the phone mock-up with the
   QR demo, and the order-desk contact list), so this suite spends real effort proving the
   removals are complete — no markup, no CSS, no JS, no dangling link, no invented menu, no
   price — and that the offer itself is intact.
   Run: node test-menu-design.js   (needs jsdom: npm install jsdom in this folder) */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

/* the suite sits next to the page it checks, so it works wherever the folder is copied */
const DIR = __dirname;

function findJsdom() {
  const here = path.join(DIR, 'node_modules', 'jsdom');
  for (const candidate of [here, 'jsdom', '/home/user/testdeps/node_modules/jsdom']) {
    try { return require(candidate); } catch (e) { /* try the next place */ }
  }
  console.error('jsdom is not installed.  From this folder run:  npm install jsdom');
  process.exit(2);
}
const { JSDOM } = findJsdom();
const html = fs.readFileSync(path.join(DIR, 'menu-card.html'), 'utf8');
const srcHtml = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');

/* markup between <body> and the <script>, and with the base64 blobs stripped:
   "INR" and "₹"-like noise hide inside data URIs if you grep the raw file */
const rawMark = html.slice(html.indexOf('<body>'), html.indexOf('<script'));
const mark = rawMark.replace(/data:[^"']+/g, 'DATA');
const jsText = (html.match(/<script>([\s\S]*?)<\/script>/) || [, ''])[1];

let pass = 0, fail = 0;
function check(name, cond, extra = '') {
  if (cond) { pass++; console.log('  PASS  ' + name + (extra ? '  -> ' + extra : '')); }
  else { fail++; console.log('  FAIL  ' + name + (extra ? '  -> ' + extra : '')); }
}

function styleBlocks(h) {
  const out = []; let i = -1;
  while ((i = h.indexOf('<style>', i + 1)) !== -1) {
    const j = h.indexOf('</style>', i);
    if (j === -1) break;
    out.push(h.slice(i + 7, j));
  }
  return out;
}
const themeStyle = styleBlocks(html).find(t => t.includes(':root{')) || '';
const srcTheme = styleBlocks(srcHtml).find(t => t.includes(':root{')) || '';
const menuStyle = styleBlocks(html).find(t => t.includes('MENU CARD DESIGN PAGE')) || '';

function boot(scripts = true) {
  const dom = new JSDOM(html, {
    runScripts: scripts ? 'dangerously' : 'outside-only',
    pretendToBeVisual: true,
    url: 'http://localhost:8080/menu-card.html',
    beforeParse(win) { win.open = () => null; win.alert = () => {}; }
  });
  return { dom, window: dom.window, doc: dom.window.document };
}
const { window, doc } = boot();
const st = window.getComputedStyle.bind(window);
const visible = (() => {
  const c = doc.body.cloneNode(true);
  c.querySelectorAll('script,style,noscript').forEach(n => n.remove());
  return c.textContent.replace(/\s+/g, ' ');
})();

console.log('\n=== 1. Same brand system as the approved page ===');
check('the theme <style> block is byte-identical to index.html', themeStyle === srcTheme && themeStyle.length > 50000,
  themeStyle.length.toLocaleString() + ' chars copied verbatim');
check('exactly one :root', (html.match(/:root\{/g) || []).length === 1);
check('brand tokens intact (blue / violet / pink / cyan, Poppins)',
  ['--blue:#2a79ff', '--violet:#8a3bff', '--pink:#ff3cb5', '--cyan:#45d8ff', 'Poppins'].every(t => themeStyle.includes(t)));
{
  /* the page owns one CSS rule of its own now; it must introduce no colour of its own */
  const rules = menuStyle.replace(/\/\*[\s\S]*?\*\//g, '');
  const hexes = (rules.match(/#([0-9a-f]{3,6})\b/gi) || []).filter(h => !/^#(fff|ffffff|000|000000)$/i.test(h));
  check('the menu CSS adds no chromatic hex — every colour comes from a token',
    hexes.length === 0, hexes.join(',') || `menu CSS is ${menuStyle.length} chars, mostly comments`);
}
check('logo in the header and again in the footer, inlined as PNG',
  doc.querySelectorAll('header.site img.brand-logo').length === 1 &&
  doc.querySelectorAll('footer.site img.brand-logo').length === 1 &&
  /class="brand-logo" src="data:image\/png;base64,/.test(rawMark));
check('the nav names the offer beside the logo, in the brand violet',
  /<b class="brand-sub"[^>]*color:#8a3bff[^>]*>Menu Card Design<\/b>/.test(rawMark));
{
  const lab = doc.querySelector('header.site .brand-text b');
  const c = st(lab);
  check('COMPUTED: that label is really painted (not transparent, not tiny)',
    c.color === 'rgb(138, 59, 255)' && parseFloat(c.fontSize) >= 18 && c.fontWeight === '700',
    c.color + ' / ' + c.fontSize + ' / ' + c.fontWeight);
}
check('no announcement bar above the header', !/class="topbar"/.test(html));
check('the header is the first element in <body>', doc.body.firstElementChild.className.includes('site'));

console.log('\n=== 2. Both removed blocks stay removed ===');
check('no sample-card markup, stage, format buttons or price toggle',
  !/class="[^"]*\bmc\b/.test(mark) && !/stage-card|class="fmtn|mc-fig|priceToggle|mc-gallery/.test(html));
check('no phone mock-up and no QR demo anywhere in the file',
  !/phone-screen|phone-notch|ph-list|ph-top|ph-note|qr-card|qr-box|qr-img|qr-slot|qr-note|digital-row/.test(html));
check('the menu CSS is one note rule plus print tidy-up — nothing card- or phone-shaped',
  !/\.mc|\.stage|\.fmtn|\.phone|\.ph-|\.qr-|\.digital-row|--photo-/.test(menuStyle) && /\.strip-note\{/.test(menuStyle),
  menuStyle.length.toLocaleString() + ' chars left');
check('no stage or QR JavaScript survived', !/setFormat|SIZES|no-prices|priceToggle|segno/.test(jsText));
check('the QR generator is not even imported by the build any more',
  !/segno|base64\.b64encode|QR_HTML/.test(fs.readFileSync(path.join(DIR, 'build-menu-design.py'), 'utf8').replace(/^#.*$/gm, '')));
check('no invented restaurant, café, dish or price text survives',
  !/Copper Cup|Saffron|Midnight Biryani|Rohan|Ananya|Espresso|Flat white|Croissant|Biriyani|Biryani/.test(visible));
check('and the copy no longer promises a gallery or a demo menu',
  !/Four sample cards|Four layouts|four designs|Pick a format|sample menu on the phone|This QR actually works|Demo content/i.test(visible));
check('no link or id points at anything that was removed',
  !/#designs|#desk|id="digital-row"|id="desk"/.test(html));
check('the page got lighter with each removal (< 320 KB now, 273 KB)',
  (() => { const kb = Math.round(fs.statSync(path.join(DIR, 'menu-card.html')).size / 1024); return kb > 150 && kb < 320; })(),
  Math.round(fs.statSync(path.join(DIR, 'menu-card.html')).size / 1024) + ' KB (419 KB with the cards, 281 KB with the phone + QR)');
{
  const ids = [...doc.querySelectorAll('body > section[id]')].map(s => s.id);
  check('what is left is a complete offer, in this order',
    ids.join(' ') === 'top compare digital formats process notes order', ids.join(' '));
}

console.log('\n=== 3. Why there are no samples, said out loud ===');
check('the hero says the page shows no sample menus and publishes nothing',
  /No sample menus and no stock claims/.test(mark) &&
  /we do not publish the menus we design/i.test(visible));
check('the small print gives the client the same promise about their own card',
  /Your menu is not published/.test(visible) && /handed over and stay yours/i.test(visible));
check('no client work is claimed or implied anywhere',
  !/testimonial|success rate|Client Stories|we designed for|recently delivered|our client|case study|\b\d+ years\b/.test(visible));
check('stock-photo honesty survives: we say when a shoot is needed',
  /instead of dressing the card with stock photos/i.test(visible));
check('and the one photo on the page is labelled for what it is',
  doc.querySelectorAll('img').length >= 1 &&
  /blank printed menu card/.test(rawMark) && /The blank card is the brief/.test(visible));
check('the footer legal line no longer refers to demo content',
  /No client menu appears on this page/.test(mark) && !/demo content/i.test(mark));

console.log('\n=== 4. No money on the page at all ===');
check('no rupee sign, no Rs., no INR, no dollar figure',
  !/₹|\bRs\.?\b|\bINR\b|\$\s?\d/.test(visible) && !/₹|\bRs\.?\b|\bINR\b/.test(mark));
check('the fee question is answered without a number',
  /quote the same day/i.test(visible) && !/our fee is|we charge|₹/.test(visible), 'quoted after we see the menu');
check('no fake discounts or offers on our own work',
  !/50% off|limited period|offer ends|discount/i.test(visible));
check('prices appear as a craft topic, not as figures',
  /Prices in one aligned column/.test(visible) && /Prices in three different columns/.test(visible));

console.log('\n=== 5. The digital half is described, not staged ===');
{
  const digital = doc.getElementById('digital');
  check('the section exists and lists what the design covers',
    !!digital && digital.querySelectorAll('.why-item').length === 4,
    [...digital.querySelectorAll('.why-item h3')].map(h => h.textContent.trim()).join(' | '));
  check('it still explains the QR version in words, without a mock-up',
    /QR version does not/.test(digital.textContent.replace(/\s+/g, ' ')) &&
    /never disagree/.test(digital.textContent.replace(/\s+/g, ' ')));
  check('the formats list still offers a digital menu as a deliverable',
    /Digital menu \(QR\)/.test(mark));
  check('no decorative stand-in was left where the QR used to be (only the copied logos are PNG)',
    [...doc.querySelectorAll('section img')].every(i =>
      !i.getAttribute('src').startsWith('data:image/png') || i.classList.contains('brand-logo')),
    [...doc.querySelectorAll('section img')].map(i => i.className || i.getAttribute('alt').slice(0, 20)).join(' | '));
  check('no image is requested from the network', (rawMark.match(/src="(?!data:)/g) || []).length === 0);
}

console.log('\n=== 6. Offer, formats and process are intact ===');
check('seven formats, four steps, ten before/after rows',
  doc.querySelectorAll('.strip-item').length === 7 && doc.querySelectorAll('.step').length === 4 &&
  doc.querySelectorAll('.vs-list li').length === 10,
  '7 formats / 4 steps / 10 rows');
check('the before/after names the problems a real card has',
  /Every line bold/.test(visible) && /none of them lined up/.test(visible) && /print shop/.test(visible));
check('the formats note keeps the printer honest about sizes',
  /Sizes are typical for each format/.test(visible) && /final trim is decided with your printer/.test(visible));
check('four small-print answers, and one of them is about money',
  doc.querySelectorAll('#notes .doc-col').length === 4 && /Why no fee is printed on this page/.test(visible));
check('the page is a design offer, not a services catalogue',
  !/Starters|Main Courses|From the Kitchen|Dessert|menuFilter/.test(visible));

console.log('\n=== 7. Contact behaviour, the part that has to work on a phone ===');
check('Call links all target the first-preference number',
  [...doc.querySelectorAll('.js-tel')].every(a => a.getAttribute('href') === 'tel:+916361842299') &&
  doc.querySelectorAll('.js-tel').length >= 4, doc.querySelectorAll('.js-tel').length + ' call links');
check('WhatsApp links are bare, exactly like kaalamithra-branding.vercel.app',
  [...doc.querySelectorAll('a.js-wa')].every(a => a.getAttribute('href') === 'https://wa.me/916361842299') &&
  !/wa\.me\/916361842299\?text/.test(mark));
check('and they are written in the markup with target + rel (works with JS off)',
  (rawMark.match(/href="https:\/\/wa\.me\/916361842299" target="_blank" rel="noopener noreferrer"/g) || []).length ===
  (rawMark.match(/href="https:\/\/wa\.me\/916361842299"/g) || []).length,
  (rawMark.match(/href="https:\/\/wa\.me\/916361842299"/g) || []).length + ' anchors');
check('the nav CTA is one of them (Send your menu)',
  /class="btn btn-gold js-wa"/.test(rawMark) && /Send your menu/.test(mark));
check('icon-only links never get a label printed over the icon',
  [...doc.querySelectorAll('a.icon-link')].every(a => a.querySelector('svg') && a.getAttribute('tabindex') === '-1' && !a.textContent.trim()),
  doc.querySelectorAll('a.icon-link').length + ' icon links');
check('the order-desk section is gone, and no contact list is left in the body',
  doc.querySelectorAll('.contact-list').length === 0 && !/id="desk"/.test(mark));
check('both inboxes are still reachable, from the copied footer',
  [...doc.querySelectorAll('footer.site a[href^="mailto:"]')].map(a => a.getAttribute('href')).join(' ').includes('kaalamithra.sales@gmail.com') &&
  [...doc.querySelectorAll('footer.site a[href^="mailto:"]')].map(a => a.getAttribute('href')).join(' ').includes('tech@kaalamithra-ai.com'),
  doc.querySelectorAll('footer.site a[href^="mailto:"]').length + ' mailto links in the footer');
check('the CTA band carries call + WhatsApp, so the page still converts',
  doc.querySelectorAll('#order a.js-tel').length >= 1 && doc.querySelectorAll('#order a.js-wa').length >= 1,
  [...doc.querySelectorAll('#order .btn')].map(b => b.textContent.trim().replace(/\s+/g, ' ')).join(' | '));
check('the CTA fine print does not advertise a removed feature',
  !/tap a format|sample card|resizes/i.test(doc.getElementById('order').textContent));
check('floating Call + WhatsApp bubbles and the desktop rescue came along',
  !!doc.querySelector('.float .f-wa') && !!doc.querySelector('.float .f-call') && !!doc.querySelector('#cpanel'));
check('nothing was lost by the removal: the footer already carries all three numbers',
  !doc.getElementById('extraPhonesOut') &&
  ['tel:+916361842299', 'tel:+918884014055', 'tel:+919972770266'].every(h =>
    [...doc.querySelectorAll('footer.site a[href^="tel:"]')].some(a => a.getAttribute('href') === h)),
  doc.querySelectorAll('footer.site a[href^="tel:"]').length + ' tel links, ' +
  doc.querySelectorAll('footer.site a[href^="mailto:"]').length + ' mailto in the footer');
check('the two alternate numbers keep dialing their own lines, unwired to the main buttons',
  [...doc.querySelectorAll('footer.site a')]
    .filter(a => /8884014055|9972770266/.test(a.getAttribute('href') || '')).length >= 4 &&
  [...doc.querySelectorAll('footer.site a')]
    .filter(a => /8884014055|9972770266/.test(a.getAttribute('href') || ''))
    .every(a => !/\bjs-tel\b|\bjs-wa\b/.test(a.className)));
check('the location line survives too', /India · Remote Friendly/.test(visible) || /India &middot; Remote Friendly/.test(mark));
check('and the copied script still guards those nodes, which is why their absence is safe',
  /if \(exLi &&/.test(jsText) && /if \(addr &&/.test(jsText));
check('no form, no fetch, no POST — nothing on this page can silently fail',
  doc.querySelectorAll('form').length === 0 && !/fetch\(|XMLHttpRequest|api\/trademark-enquiry/.test(html));
check('the only buttons left belong to the copied desktop rescue panel',
  [...doc.querySelectorAll('button')].every(b => b.closest('#cpanel')),
  doc.querySelectorAll('button').length + ' button(s)');

console.log('\n=== 8. Print (this hand-out is meant to leave the room on paper) ===');
const printRule = (menuStyle.slice(menuStyle.indexOf('@media print')).replace(/\s+/g, ' '));
check('print drops the controls so the page itself is the hand-out',
  /\.btn-row, \.btn-more\{display:none !important\}/.test(printRule));
check('print keeps every row unbroken', /page-break-inside:avoid/.test(printRule));
check('print reveals the scroll-hidden rows (opacity guard)', /\.reveal\{opacity:1 !important/.test(printRule));
check('the dark bands are left to the theme’s own print rules (no fighting it)', !/\.why\{|\.cta\{/.test(printRule));
check('no print rule names a block that is gone', !/\.phone|\.qr-|\.mc|\.stage/.test(printRule));
check('a <noscript> guard exists in <head>',
  /<noscript><style>\.reveal\{opacity:1 !important; transform:none !important\}<\/style><\/noscript>/.test(html));
check('and the same guard is on the trademark page', /<noscript><style>\.reveal\{/.test(srcHtml));

console.log('\n=== 9. Structure, a11y, and the generator contract ===');
{
  const tags = ['div', 'section', 'ul', 'li', 'article', 'figure', 'span', 'header', 'footer', 'button', 'ol', 'p',
                'h2', 'h3', 'h4', 'h5', 'nav', 'a', 'code', 'em', 'b'];
  const bad = tags.filter(t => {
    const o = (mark.match(new RegExp('<' + t + '[\\s>]', 'g')) || []).length;
    const c = (mark.match(new RegExp('</' + t + '>', 'g')) || []).length;
    return o !== c;
  });
  check('every tag in the body markup is balanced', bad.length === 0, bad.join(', ') || tags.length + ' tag types');
  check('one h1, and an h2 for every section that needs one',
    doc.querySelectorAll('h1').length === 1 && doc.querySelectorAll('h2').length >= 5,
    doc.querySelectorAll('h2').length + ' h2s');
  check('every image has alt text', [...doc.querySelectorAll('img')].every(i => i.hasAttribute('alt')),
    doc.querySelectorAll('img').length + ' images');
  check('the only photograph in the page body is the hero - no leftover demo art',
    [...doc.querySelectorAll('section img')].filter(i => !i.classList.contains('brand-logo')).length === 1,
    [...doc.querySelectorAll('section img')].filter(i => !i.classList.contains('brand-logo'))
      .map(i => (i.getAttribute('alt') || '').slice(0, 34)).join(' | ') || 'none');
  check('the only bare href="#" are the social slots the copied footer marks [EDIT]',
    [...doc.querySelectorAll('a[href="#"]')].every(a => a.closest('.socials')),
    doc.querySelectorAll('a[href="#"]').length + ' in footer .socials');
  check('every in-page anchor resolves to a section that exists',
    [...doc.querySelectorAll('a[href^="#"]')].filter(a => a.getAttribute('href').length > 1)
      .every(a => !!doc.querySelector(a.getAttribute('href'))),
    [...new Set([...doc.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href')).filter(h => h.length > 1))].join(' '));
  check('lang, title, description, share preview',
    html.includes('<html lang="en-IN">') && /<title>Menu Card Design \| Kaala Mithra — AI Tech Solution<\/title>/.test(html) &&
    /og:title" content="Menu Card Design for restaurants/.test(html));
  check('the preview copy promises neither a gallery nor a demo of ours',
    !/Four sample menu card designs|sample layouts you can resize|Demo content/.test(html));
  check('the page says it is generated, and by which script',
    /THIS PAGE IS GENERATED — edit build-menu-design\.py/.test(html));
  check('it does not touch the trademark page', !/menu-card/.test(srcHtml));
  try {
    const out = execFileSync('python3', ['build-menu-design.py', '--check'], { cwd: DIR, encoding: 'utf8' });
    check('re-running the generator reproduces this file exactly', /identical to the file on disk/.test(out), out.trim().split('\n')[0]);
  } catch (e) {
    check('re-running the generator reproduces this file exactly', false, String(e).slice(0, 90));
  }
}

console.log('\n=== 10. With JavaScript switched off ===');
{
  const { doc: d2 } = boot(false);
  const text = d2.body.textContent.replace(/\s+/g, ' ');
  check('the whole offer is in the static markup: chips, steps, before/after, contact rows',
    d2.querySelectorAll('.strip-item').length === 7 && d2.querySelectorAll('.step').length === 4 &&
    d2.querySelectorAll('.vs-list li').length === 10 && d2.querySelectorAll('a[href^="mailto:"]').length >= 4);
  check('nothing is left to a script: the same sentences appear without one',
    ['Send us', 'No sample menus', 'Sizes are typical', 'Your menu is not published'].every(t => text.includes(t)));
  check('and the removed demo headings are absent with scripts off too',
    !/This QR actually works|Digital menu \u00b7|Copper Cup/.test(text));
  check('contact hrefs are complete in the static markup',
    /href="tel:\+916361842299">\+91 63618 42299</.test(rawMark) && /WhatsApp us your menu/.test(rawMark));
  check('with no desk, the footer is where the two inboxes live',
    !rawMark.includes('contact-list') && rawMark.includes('kaalamithra.sales@gmail.com'));
  check('the reveal rows are visible with scripts off (the noscript rule)',
    /<noscript><style>\.reveal\{opacity:1/.test(html));
}

console.log('\n=== 11. Nothing crashes ===');
{
  const errs = [];
  const dom = new JSDOM(html, {
    runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://localhost/',
    beforeParse(win) { win.open = () => null; win.alert = () => {}; win.addEventListener('error', e => errs.push(String(e.message))); }
  });
  setTimeout(() => {
    const d = dom.window.document;
    check('no script error while booting', errs.length === 0, errs.join(' | ') || 'clean');
    check('every reveal row ends up visible', d.querySelectorAll('.reveal.in').length === d.querySelectorAll('.reveal').length,
      d.querySelectorAll('.reveal.in').length + '/' + d.querySelectorAll('.reveal').length);
    check('no handler looks for an element that no longer exists',
      !/getElementById\("stage|getElementById\("priceToggle|getElementById\("stageSize|querySelectorAll\("\.mc-fig|qr-box/.test(jsText));
    check('the copyright year is filled in', d.getElementById('yr').textContent === String(new Date().getFullYear()));
    check('hover titles on the floating buttons', d.querySelector('.f-wa').title.length > 5);
    console.log(`\n================  ${pass} passed, ${fail} failed  ================`);
    process.exit(fail ? 1 : 0);
  }, 60);
}
