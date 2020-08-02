tmux

-- Lancement mysql
cd pweb/mysql..../bin 
./mysqld

-- Mot de passe root
alter user 'root'@'localhost' identified by 'totororo';
flush privileges;

-- Injection export
mysql -u root -ppweb pweb_international < ../../Dump20191120.sql 


-- Run
-- Générer le dossier static pour les fichiers
python manage.py collectstatic

-- Lancer le serveur node express pour servire les pages statiques
coffee ./serveur.coffee --> listen sur 8001
-- Autoriser cors pour les accès fonts
npm install cors

export LD_LIBRARY_PATH=/home/sfrenot/pweb/mysql-8.0.18-linux-x86_64-minimal/lib
python manage.py runserver tc-net3.insa-lyon.fr:8000




