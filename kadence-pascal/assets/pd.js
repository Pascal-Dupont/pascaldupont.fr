/* Filtres de la page Films. Aucune dépendance. */
(function () {
  var barre = document.querySelector('.pd-filtres');
  if (!barre) return;
  var groupes = document.querySelectorAll('.pd-groupe');
  barre.addEventListener('click', function (e) {
    var b = e.target.closest('.pd-filtre');
    if (!b) return;
    var cle = b.getAttribute('data-cat');
    barre.querySelectorAll('.pd-filtre').forEach(function (x) {
      x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
    });
    groupes.forEach(function (g) {
      g.hidden = !(cle === 'tous' || g.getAttribute('data-groupe') === cle);
    });
  });
})();
