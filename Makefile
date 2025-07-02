# Makefile pour UniAccess
# Ce Makefile définit les cibles suivantes :
#  • install : installe les dépendances Python (via pip) à partir de requirements.txt.
#  • test : exécute les tests (unitaires, intégration, accessibilité) à l’aide de pytest.
#  • package : génère un paquet (par exemple, un .deb ou un .rpm) (à compléter par dpkg‑buildpackage ou rpmbuild).
#  • clean : supprime les fichiers générés (par exemple, les fichiers .pyc, les répertoires __pycache__, etc.).

.PHONY: install test package clean

install:
	pip install -r requirements.txt

test:
	pytest tests/

package:
	@echo "Génération du paquet (à compléter par dpkg‑buildpackage ou rpmbuild)…"

clean:
	find . -name "*.pyc" -o -name "__pycache__" | xargs rm -rf 