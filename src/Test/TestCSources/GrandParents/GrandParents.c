#include "GrandParents.h"
#include "../Parents/Parents.h"
#include "../Relative/Relative.h"
#include "../Children/Children.h"

#if defined FOO
void GrandParent1(void)
{
    Parent1();
}
#endif

void GrandParent2(void)
{
    Parent1();
    Parent3();
}

#if defined BAR
void GrandParent3(void)
{
    Parent2();
    Parent3();
}
#else
void GrandParent3(void)
{
    Parent3();
    Relative();
    Child1();
}
#endif

#if !defined FOO
void GrandParent1(void)
{
    Parent1();
    Parent2();
}
#endif
