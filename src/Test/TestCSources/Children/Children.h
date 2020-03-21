#ifndef __CHILDREN_H__

typedef void (*fPtr)(void);

void Child1(void);
void Child2(void);
void Child3(void);

void RecursiveChild();

void SneakyCaller();
void SneakyChild1();
void SneakyChild2();

void NaughtyChild(fPtr);

#endif
