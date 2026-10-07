// Test d'installation de bout en bout, par l'interface d'administration, comme le fera Pascal Dupont :
//   1. envoyer le thème enfant (Apparence > Thèmes > Ajouter > Téléverser) et l'activer ;
//   2. importer les pages (Outils > Importer > WordPress) en les attribuant à son compte ;
//   3. ouvrir le tableau de bord (réglage automatique de l'accueil et des menus) ;
//   4. vérifier chaque page : statut HTTP, blocs valides dans l'éditeur, captures.
// Prérequis : un WordPress neuf avec Kadence (thème) actif, Kadence Blocks et WordPress Importer actifs
// (installer.sh <src> <cible> <port> sans-theme).
// Usage : node test-installation.js <base> <zip du thème> <xml des pages> <dossier des captures>
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const [BASE, ZIP, XML, SORTIE] = process.argv.slice(2);
const PAGES = ['', 'films', 'serie-serval', 'a-propos', 'defense-et-securite', 'lakelab', 'contact', 'mentions-legales', 'confidentialite'];
const rapport = { etapes: [], pages: {}, erreursJS: [] };
const note = (etape, ok, detail) => { rapport.etapes.push({ etape, ok, detail }); console.log((ok ? 'OK ' : 'ÉCHEC ') + etape + (detail ? ' : ' + detail : '')); };

(async () => {
  fs.mkdirSync(SORTIE, { recursive: true });
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  p.on('pageerror', (e) => rapport.erreursJS.push(p.url() + ' : ' + e.message));
  await p.route(/i\.ytimg\.com/, (r) => r.fulfill({ status: 200, contentType: 'image/svg+xml', body: '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360"><rect width="480" height="360" fill="#333"/></svg>' }));

  // connexion
  await p.goto(BASE + '/wp-login.php');
  await p.fill('#user_login', 'admin');
  await p.fill('#user_pass', 'admin-test-2026');
  await p.click('#wp-submit');
  await p.waitForURL(/wp-admin/);
  note('connexion', true);

  // 1. thème enfant
  await p.goto(BASE + '/wp-admin/theme-install.php');
  const bascule = p.locator('.upload-view-toggle').first();
  if (await bascule.isVisible().catch(() => false)) await bascule.click();
  await p.waitForSelector('#install-theme-submit', { state: 'visible' });
  await p.setInputFiles('input[type=file][name=themezip]', ZIP);
  await Promise.all([p.waitForLoadState('load'), p.click('#install-theme-submit')]);
  await p.waitForTimeout(1500);
  const texteInstall = await p.innerText('#wpbody-content');
  const lienActiver = p.locator('a.activatelink, a:has-text("Activer")').first();
  if (await lienActiver.count()) {
    await Promise.all([p.waitForLoadState('load'), lienActiver.click()]);
  }
  await p.goto(BASE + '/wp-admin/themes.php');
  const actif = await p.locator('.theme.active .theme-name').innerText().catch(() => '');
  note('thème envoyé et activé', /Pascal Dupont/.test(actif), actif.replace(/\s+/g, ' ').trim() || texteInstall.slice(0, 300));
  await p.screenshot({ path: path.join(SORTIE, '01-themes.png') });

  // 2. import des pages
  await p.goto(BASE + '/wp-admin/admin.php?import=wordpress');
  await p.setInputFiles('input[type=file]#upload', XML);
  await Promise.all([p.waitForLoadState('load'), p.click('input[type=submit]#submit, #submit')]);
  await p.waitForTimeout(1000);
  await p.screenshot({ path: path.join(SORTIE, '02-import-auteurs.png') });
  const select = p.locator('select[name^="user_map"]').first();
  if (await select.count()) {
    const valeurAdmin = await select.locator('option', { hasText: 'admin' }).first().getAttribute('value');
    await select.selectOption(valeurAdmin);
  }
  await Promise.all([p.waitForLoadState('load', { timeout: 120000 }), p.click('input[type=submit]')]);
  await p.waitForTimeout(1500);
  const texteImport = await p.innerText('#wpbody-content');
  await p.screenshot({ path: path.join(SORTIE, '03-import-fini.png'), fullPage: true });
  note('import des pages', /Terminé|All done/i.test(texteImport), texteImport.replace(/\s+/g, ' ').slice(0, 400));

  // 3. tableau de bord : réglage automatique
  await p.goto(BASE + '/wp-admin/');
  const avis = await p.locator('.notice-success').allInnerTexts();
  note('réglage automatique (avis vert)', avis.some((t) => /menus sont réglés/.test(t)), avis.join(' | ').slice(0, 300));
  await p.screenshot({ path: path.join(SORTIE, '04-tableau-de-bord.png') });

  // 4. pages publiques
  for (const slug of PAGES) {
    const url = BASE + '/' + (slug ? slug + '/' : '');
    const r = await p.goto(url, { waitUntil: 'load' });
    await p.waitForTimeout(400);
    const info = await p.evaluate(() => ({
      titre: document.title,
      h1: Array.from(document.querySelectorAll('h1')).map((h) => h.innerText.trim()),
      menu: Array.from(document.querySelectorAll('#primary-menu a')).map((a) => a.innerText.trim()),
      pied: Array.from(document.querySelectorAll('#footer-menu a')).map((a) => a.innerText.trim()),
      debord: document.documentElement.scrollWidth > window.innerWidth + 1,
      google: Array.from(document.querySelectorAll('link[href*="fonts.googleapis"], link[href*="fonts.gstatic"]')).length,
    }));
    rapport.pages[slug || 'accueil'] = Object.assign({ statut: r.status() }, info);
    await p.screenshot({ path: path.join(SORTIE, 'page-' + (slug || 'accueil') + '.png'), fullPage: true });
    note('page /' + slug, r.status() === 200 && !info.debord && info.google === 0 && info.h1.length === 1, 'statut ' + r.status() + ', h1 ' + JSON.stringify(info.h1));
  }
  // mobile : accueil + menu ouvert
  const m = await b.newPage({ viewport: { width: 390, height: 844 } });
  await m.route(/i\.ytimg\.com/, (r) => r.fulfill({ status: 200, contentType: 'image/svg+xml', body: '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360"><rect width="480" height="360" fill="#333"/></svg>' }));
  await m.goto(BASE + '/');
  await m.screenshot({ path: path.join(SORTIE, 'mobile-accueil.png'), fullPage: true });
  const bouton = m.locator('.menu-toggle-open').first();
  if (await bouton.count()) { await bouton.click(); await m.waitForTimeout(800); await m.screenshot({ path: path.join(SORTIE, 'mobile-menu.png') }); }
  const liensTiroir = await m.locator('#mobile-drawer a').allInnerTexts().catch(() => []);
  note('menu mobile', liensTiroir.filter((t) => t.trim()).length >= 5, liensTiroir.map((t) => t.trim()).filter(Boolean).join(', '));

  // 5. éditeur : blocs valides sur chaque page
  for (const slug of PAGES) {
    const s = slug || 'accueil';
    const id = await p.evaluate(async (s) => { const r = await fetch('/wp-json/wp/v2/pages?slug=' + s, { credentials: 'same-origin' }); const j = await r.json(); return j.length ? j[0].id : 0; }, s);
    await p.goto(BASE + '/wp-admin/post.php?action=edit&post=' + id);
    await p.waitForFunction(() => window.wp && wp.data && wp.data.select('core/block-editor') && wp.data.select('core/block-editor').getBlocks().length > 0, null, { timeout: 60000 });
    await p.waitForTimeout(2500);
    const inval = await p.evaluate(() => {
      const out = [];
      (function f(bs) { bs.forEach((b) => { if (!b.isValid || b.name === 'core/missing') out.push(b.name); f(b.innerBlocks || []); }); })(wp.data.select('core/block-editor').getBlocks());
      return out;
    });
    rapport.pages[s].editeur = inval;
    note('éditeur /' + slug, inval.length === 0, inval.join(', '));
    if (s === 'accueil') await p.screenshot({ path: path.join(SORTIE, '05-editeur-accueil.png') });
  }

  fs.writeFileSync(path.join(SORTIE, 'rapport.json'), JSON.stringify(rapport, null, 1));
  console.log('erreurs JS :', rapport.erreursJS.length ? rapport.erreursJS : 'aucune');
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
