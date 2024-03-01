# commit
git add .
git commint -a -m "testo"
git push -u origin nomeBranch


# rebase da saleor a mio main:
git checkout main
git pull saleor main
git checkout develop
git rebase main

# rebase da main a nomeBranch
git checkout nomeBranch
git rebae develop