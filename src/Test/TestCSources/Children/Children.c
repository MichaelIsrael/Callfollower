#include "Children.h"
#include "../GrandChildren/GrandChildren.h"

#define CALL_SNEAKY(N)  SneakyChild##N()

#if defined RECURSE
#define START_SNEAKINESS()              \
{                                       \
    RecursiveChild();                   \
}
#else
#define START_SNEAKINESS()              \
{                                       \
    SneakyCaller();                     \
}
#endif

fPtr gFunc1;
fPtr gFunc2;

void Child1(void)
{
    NaughtyChild(Child2);
}

void Child2(void)
{
    GrandChild1();
    gFunc1();
    gFunc2();
}

void Child3(void)
{
    START_SNEAKINESS();
}


void RecursiveChild()
{
    RecursiveChild();
}

void SneakyCaller()
{
    if(1)
    {
        CALL_SNEAKY(1);
    }
    if(2)
    {
        CALL_SNEAKY(2);
    }
}

void SneakyChild1()
{
    gFunc1 = GrandChild2;
    GrandChild1();
}

void SneakyChild2()
{
    gFunc1 = Child1;
    gFunc2();
}

void NaughtyChild(fPtr func)
{
    gFunc2 = func;
}
