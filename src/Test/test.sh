echo Testing follow up...
time ../followcalls -d . follow up Child1 -l 10 -s basic

echo
echo Testing follow down...
time ../followcalls -d . follow down Parent1 -l 10 -s file

echo
echo Testing follow all...
time ../followcalls -d . follow all Relative -l 10 -s file
