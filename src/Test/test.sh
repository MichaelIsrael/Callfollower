echo Testing follow up...
time ../CallFollower.py -d . follow up Child1 -l 10

echo
echo Testing follow down...
time ../CallFollower.py -d . follow down Parent1 -l 10

echo
echo Testing follow all...
time ../CallFollower.py -d . follow all Relative -l 10
