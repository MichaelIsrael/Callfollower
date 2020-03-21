MAKE        := make
CC          := gcc
RM          := rm -f
TEST_EXEC   := test
TEST_OBJ    := main.o
SRCS        := $(wildcard */*.c) $(wildcard */*.cpp)
OBJS        := $(patsubst %.c, %.o, $(SRCS))

%.o: %.c
	$(CC) $^ -c -o $@

clean:
	$(RM) $(OBJS) $(TEST_OBJ) $(TEST_EXEC)

build: $(OBJS)

test: $(TEST_OBJ) build
	$(CC) $(TEST_OBJ) $(OBJS) -o $(TEST_EXEC)

all: test

.PHONY: clean build test all
