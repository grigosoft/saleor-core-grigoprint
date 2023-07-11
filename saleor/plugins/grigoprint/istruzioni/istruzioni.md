# h1 
## h2

codice inline `codice`

``` py
codice
```

# installazione
## installazione saleor CORE
    clone del git saleor `git clone `
    creazione venv eserna alla cartella saleor
    installazione dipendenze `python -m pip install -r requirements.txt `
        se da errore su pg, installare `sudo dnf install libpq-devel`
    avviare postgress `sudo systemctl start postgresql.service`
    creare DB 
        `sudo su - postgres`
        ``
### settiing up postgres user.

 sudo su - postgres
 psql

 CREATE ROLE saleor WITH LOGIN PASSWORD 'saleor';
 CREATE DATABASE saleor;
 ALTER USER saleor WITH SUPERUSER;

 GRANT ALL PRIVILEGES ON DATABASE saleor TO saleor;
 ALTER USER saleor CREATEDB;
### Applying migrations
 python manage.py migrate
## create dummy data
 python manage.py populatedb
## Create superuser
 python manage.py createsuperuser
## runserver
python manage.py runserver 0.0.0.0:8000

## Concetto git
### salor originale rimane nel branch main
creare branch grigoprint, sarà il nostro riferimento
nel branch main lasciare solo il clone di saleor e aggiornarlo
nel branch grigprint allineare gli aggiornamenti con rebase
poi fare rebase anche nei branch di sviluppo


## installazione plugin
posizionare la cartella dentro "plugin"

aggiungere i seguenti collegamenti
permessi --> `saleor/core/permissions.py` non usati ora
notify --> `saleor/core/notify_events.py` non usati ora
graphql --> `saleor/graphql/api.py` 
    inserire query e mutations `from ..plugins.grigoprint.schema import GrigoprintQueries, GrigoprintMutations`
settings --> `saleor/settings.py`
    INSTALLED_APPS = [`"saleor.plugins.grigoprint.accountGrigo","saleor.plugins.grigoprint.prodottoPersonalizzato",`]
    BUILTIN_PLUGINS = [`"saleor.plugins.grigoprint.plugin.GrigoprintPlugin"`]

# Uso git
## init git
git init
git config --global user.email "grig.griganto@gmail.com"
git config --global user.user "grigoprint"
git branch -M master
## uso git
git add .
git commit -a -m "init"
git push origin NOME_BRANCH

per creare branch e spostarsi li `git checkout -b nome`

selezione branch di lavoro `git checkout nome`

# merge dopo push completo del brench di lavoro
`git checkout master`
`git pull origin master`
`git merge test`
`git push origin master`

# Uso saleor
creazione env `python3 -m venv myvenv` ( fuori dalla cartella di lavoro saleor)
attivazione env `source myvenv/bin/activate` ( fuori dalla cartella di lavoro saleor)
installazione dipendenze `pip install -r requirements.txt`
    eventuali problemi:
    `pg_config is in postgresql-devel (libpq-dev in Debian/Ubuntu,libpq-devel on Centos/Fedora/Cygwin/Babun.)`
migrate DB `python manage.py migrate`
run server `python manage.py runserver 0.0.0.0:8000`

# test saleor
install py_dev for install dependencies on venv `sudo dnf install python-devel`
install dependencies for test all saleor `python -m pip install -r requirements_dev.txt`
run test on grigoprint plugins `pytest saleor/plugins/grigoprint`
run test on all saleor `py.test`



## idea di base
### necessità
serve una gestione per i prodotti personalizzati
extra info per l'utente
### soluzione
aggiungo le informazioni alle linee di checout e ordine, cosi da avere delle personalizzazioni uniche legate al prodotto comprato
Estendo classi base e poi le richiamo tramite GraphQL:
Model: | Products --> PrdottoGrigo 
GraphQL: | gql.saleor.products(model.Product) ---> gql.grigo.products(model.PrdottoGrigo)


# Installazione Plugin Grigoprint
### plugin da aggingere a saleor


la prima volta che si compila un app bisogna forzare il nome dell'app per fargli creare la cartella

# librerie da installare
## per importazione da danea
pip install fdb
sudo dnf install libfbclient2


### running test saleor
python -m pip install -r requirements_dev.txt 
se da errore "pywatchman" -- >  pip install python-dev-tools

# avvio test
py.test
