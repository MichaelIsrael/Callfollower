#include "Children.h"
#include "GrandChildren.h"

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
    //Use macors.
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
