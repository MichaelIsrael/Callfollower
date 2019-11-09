#include "GrandParents.h"
#include "Parents.h"
#include "Relative.h"
#include "Children.h"

void Parent1(void)
{
    GrandParent1();
    Child1();
}

void Parent2(void)
{
#if defined FOO
    Child1();
#else
    Child3();
#endif
}

void Parent3(void)
{
#if defined BAR
    Child1();
    Child3();
#else
    Child1();
    Relative();
    Child1();
#endif
}
