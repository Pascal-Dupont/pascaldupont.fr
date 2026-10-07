// Construit des pages dans le vrai éditeur de blocs WordPress, à partir d'une description JSON.
// Usage :
//   node editeur.js construire <spec.json> [--base http://127.0.0.1:8080]
//   node editeur.js valider <slug> [--base ...]
//   node editeur.js capture <url-ou-slug> <fichier.png> [largeur] [--base ...]
// Spec : { "titre": "...", "slug": "...", "meta": {...}, "blocs": [ { "name": "kadence/rowlayout", "attributes": {...}, "innerBlocks": [...] } ] }
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const iBase = args.indexOf('--base');
const BASE = iBase >= 0 ? args.splice(iBase, 2)[1] : 'http://127.0.0.1:8080';
const ETAT = path.join(__dirname, '.session-' + BASE.replace(/\W/g, '') + '.json');

async function navigateur() {
  const b = await chromium.launch();
  const ctx = await b.newContext(fs.existsSync(ETAT) ? { storageState: ETAT } : {});
  const p = await ctx.newPage();
  await p.goto(BASE + '/wp-admin/');
  if (p.url().includes('wp-login.php')) {
    await p.fill('#user_login', 'admin');
    await p.fill('#user_pass', 'admin-test-2026');
    await p.click('#wp-submit');
    await p.waitForURL(/wp-admin/);
    await ctx.storageState({ path: ETAT });
  }
  return { b, ctx, p };
}

async function attendreEditeur(p) {
  await p.waitForFunction(() => window.wp && wp.data && wp.blocks && wp.data.select('core/editor') && wp.data.select('core/editor').getCurrentPostId(), null, { timeout: 60000 });
  // fermer la fenêtre de bienvenue et le choix de modèle si présents
  await p.evaluate(() => {
    try { wp.data.dispatch('core/preferences').set('core/edit-post', 'welcomeGuide', false); } catch (e) {}
    try { wp.data.dispatch('core/preferences').set('core', 'enableChoosePatternModal', false); } catch (e) {}
  });
  await p.waitForTimeout(800);
}

async function idParSlug(p, slug) {
  return p.evaluate(async (s) => {
    const r = await wp.apiFetch({ path: '/wp/v2/pages?status=any&per_page=100&slug=' + encodeURIComponent(s) });
    return r.length ? r[0].id : 0;
  }, slug);
}

function verifier(p) {
  return p.evaluate(() => {
    const erreurs = [];
    const types = {};
    (function parcourir(blocs, chemin) {
      blocs.forEach((b, i) => {
        const c = chemin + '/' + b.name + '[' + i + ']';
        types[b.name] = (types[b.name] || 0) + 1;
        if (!b.isValid) erreurs.push(c + ' : bloc invalide');
        if (b.name === 'core/missing') erreurs.push(c + ' : type de bloc inconnu');
        if (b.validationIssues && b.validationIssues.length) erreurs.push(c + ' : ' + JSON.stringify(b.validationIssues).slice(0, 300));
        parcourir(b.innerBlocks || [], c);
      });
    })(wp.data.select('core/block-editor').getBlocks(), '');
    return { erreurs, types };
  });
}

async function construire(fichier) {
  const spec = JSON.parse(fs.readFileSync(fichier, 'utf8'));
  const { b, p } = await navigateur();
  const erreursConsole = [];
  p.on('pageerror', (e) => erreursConsole.push(e.message));
  let id = await idParSlug(p, spec.slug).catch(() => 0);
  if (!id) {
    await p.goto(BASE + '/wp-admin/post-new.php?post_type=page');
    await attendreEditeur(p);
  } else {
    await p.goto(BASE + '/wp-admin/post.php?action=edit&post=' + id);
    await attendreEditeur(p);
  }
  const inconnus = await p.evaluate((spec) => {
    const manquants = new Set();
    function fabriquer(n) {
      if (!wp.blocks.getBlockType(n.name)) { manquants.add(n.name); return null; }
      const enfants = (n.innerBlocks || []).map(fabriquer).filter(Boolean);
      return wp.blocks.createBlock(n.name, n.attributes || {}, enfants);
    }
    const blocs = spec.blocs.map(fabriquer).filter(Boolean);
    wp.data.dispatch('core/block-editor').resetBlocks(blocs);
    const modif = { title: spec.titre, slug: spec.slug, status: 'publish' };
    if (spec.meta) modif.meta = spec.meta;
    if (spec.excerpt) modif.excerpt = spec.excerpt;
    if (spec.template !== undefined) modif.template = spec.template;
    wp.data.dispatch('core/editor').editPost(modif);
    return Array.from(manquants);
  }, spec);
  // laisser les blocs Kadence s'initialiser (identifiants uniques, styles)
  await p.waitForTimeout(4000);
  await p.evaluate(() => wp.data.dispatch('core/editor').savePost());
  await p.waitForFunction(() => !wp.data.select('core/editor').isSavingPost() && !wp.data.select('core/editor').isAutosavingPost(), null, { timeout: 60000 });
  await p.waitForTimeout(1500);
  const sauvegarde = await p.evaluate(() => ({ id: wp.data.select('core/editor').getCurrentPostId(), lien: wp.data.select('core/editor').getPermalink(), sale: wp.data.select('core/editor').isEditedPostDirty() }));
  if (sauvegarde.sale) { await p.evaluate(() => wp.data.dispatch('core/editor').savePost()); await p.waitForTimeout(3000); }
  // recharger et vérifier la validité telle que l'éditeur la voit
  await p.goto(BASE + '/wp-admin/post.php?action=edit&post=' + sauvegarde.id);
  await attendreEditeur(p);
  await p.waitForTimeout(2500);
  const verif = await verifier(p);
  console.log(JSON.stringify({ id: sauvegarde.id, lien: sauvegarde.lien, blocsInconnus: inconnus, erreurs: verif.erreurs, types: verif.types, erreursJS: erreursConsole.slice(0, 10) }, null, 1));
  await b.close();
}

async function valider(slug) {
  const { b, p } = await navigateur();
  const id = await (async () => { await p.goto(BASE + '/wp-admin/edit.php?post_type=page'); return idParSlug(p, slug); })();
  if (!id) { console.log(JSON.stringify({ erreur: 'page introuvable : ' + slug })); await b.close(); return; }
  await p.goto(BASE + '/wp-admin/post.php?action=edit&post=' + id);
  await attendreEditeur(p);
  await p.waitForTimeout(2500);
  console.log(JSON.stringify(Object.assign({ id }, await verifier(p)), null, 1));
  await b.close();
}

async function capture(cible, sortie, largeur) {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: parseInt(largeur || '1280', 10), height: 900 } });
  const erreurs = [];
  p.on('pageerror', (e) => erreurs.push(e.message));
  // Vignettes YouTube : le serveur de test n'y a pas accès ; une image de remplacement (4/3 à bandes noires,
  // comme les vraies hqdefault) permet de juger la mise en page.
  await p.route(/i\.ytimg\.com/, (route) => route.fulfill({ status: 200, contentType: 'image/svg+xml', body:
    '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360"><rect width="480" height="360" fill="#000"/>' +
    '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5b6b5a"/><stop offset="1" stop-color="#1f2a25"/></linearGradient></defs>' +
    '<rect y="45" width="480" height="270" fill="url(#g)"/><text x="240" y="190" font-family="sans-serif" font-size="22" fill="#e8e6e1" text-anchor="middle">vignette YouTube</text></svg>' }));
  const url = /^https?:/.test(cible) ? cible : BASE + '/' + (cible === 'accueil' ? '' : cible.replace(/^\/|\/$/g, '') + '/');
  const r = await p.goto(url, { waitUntil: 'networkidle' }).catch(() => p.goto(url));
  await p.waitForTimeout(500);
  const debord = await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  await p.screenshot({ path: sortie, fullPage: true });
  console.log(JSON.stringify({ url, statut: r ? r.status() : null, debordementHorizontal: debord, erreursJS: erreurs }));
  await b.close();
}

(async () => {
  const [cmd, a1, a2, a3] = args;
  if (cmd === 'construire') await construire(a1);
  else if (cmd === 'valider') await valider(a1);
  else if (cmd === 'capture') await capture(a1, a2, a3);
  else console.log('commandes : construire <spec.json> | valider <slug> | capture <slug|url> <png> [largeur]');
})().catch((e) => { console.error(e); process.exit(1); });
