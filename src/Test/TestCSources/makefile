CC := gcc
RM := rm -f
OBJ := Children.o GrandChildren.o GrandParents.o Parents.o Relative.o 
TEST_OBJ := main.o
TEST_EXEC := test

%.o: %.c %.h
	$(CC) -c $*.c -o $*.o

clean:
	$(RM) $(OBJ) $(TEST_OBJ) $(TEST_EXEC)

build: $(OBJ)

test: $(OBJ) $(TEST_OBJ)
	$(CC) $^ -o $(TEST_EXEC)

all: test
