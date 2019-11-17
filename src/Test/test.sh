../CallFollower.py -vv -d . follow up Child1 -l 10
dot -Tpng -o parents.png Child1.gv 

../CallFollower.py -vv -d . follow down Parent1
dot -Tpng -o children.png Parent1.gv

../CallFollower.py -vv -d . follow all Relative
dot -Tpng -o all.png Relative.gv
