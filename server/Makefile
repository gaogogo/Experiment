CFLAGS = -I/usr/src/linux-headers-4.9.61-sched.6.0+/include/uapi -I/usr/src/linux-headers-4.9.61-sched.6.0+/include

client : client.o
	cc -o client client.o

clinet.o : client.c
	cc -c client.c

server : server.o
	cc -o server server.o -lpthread

server.o : server.c
	cc -c server.c

clean :
	rm  *.o
