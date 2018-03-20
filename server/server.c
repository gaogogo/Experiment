#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <errno.h>
#include <pthread.h>

#define PORT 9000
#define MAX_LINE 2048
#define LISTENQ 60

void *handle_Cli(void *fd)
{
    int sockfd = *(int *)fd;

    char buffer[MAX_LINE];
    bzero(buffer, sizeof(buffer));
    if(recv(sockfd, buffer, MAX_LINE, 0) < 0)
    {
        perror("recieve data error.\n");
        exit(1);
    }

    char filename[MAX_LINE];
    bzero(filename, sizeof(filename));
    strncpy(filename, buffer, strlen(buffer));

    FILE *fp = fopen(filename, "w");
    if(fp == NULL)
    {
        perror("open file error.\n");
        char tips[17] = "open file error.";
        send(sockfd, tips, 17, 0);
        close(sockfd);
        exit(0);
        
    }
    else
    {
        char ok[3] = "ok";
        send(sockfd, ok, 3, 0);

        bzero(buffer, sizeof(buffer));

        int length = 0;
        int write_length = 0;
        int flag = 1;
        while(length = recv(sockfd, buffer, MAX_LINE, 0))
        {
            if(length < 0)
            {
                perror("recieve data from server error.\n");
                flag = 0;
                break;
            }

            write_length = fwrite(buffer, sizeof(char), length, fp);
            if(write_length < length)
            {
                perror("write file error.\n");
                flag = 0;
                break;
            }
            bzero(buffer, sizeof(buffer));
        }

        if(flag)
        {
            printf("recieve file %s from client finished.\n", filename);
        }
        fclose(fp);
    }
    close(sockfd);
}

int main(int argc , char **argv)
{
	struct sockaddr_in servaddr , cliaddr;

	int listenfd , connfd;
	pid_t childpid;

	pthread_t tid;

	socklen_t clilen;

	if((listenfd = socket(AF_INET , SOCK_STREAM , 0)) < 0)
	{
		perror("socket error");
		exit(1);
	}//if

	bzero(&servaddr , sizeof(servaddr));

	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servaddr.sin_port = htons(PORT);

	if(bind(listenfd , (struct sockaddr*)&servaddr , sizeof(servaddr)) < 0)
	{
		perror("bind error");
		exit(1);
	}//if

	if(listen(listenfd , LISTENQ) < 0)
	{
		perror("listen error");
		exit(1);
	}//if

	for( ; ; )
	{
		clilen = sizeof(cliaddr);
		if((connfd = accept(listenfd , (struct sockaddr *)&cliaddr , &clilen)) < 0 )
		{
			perror("accept error");
			exit(1);
		}//if

		if(pthread_create(&tid, NULL , handle_Cli, &connfd) == -1)
        {
            perror("pthread create error.\n");
            exit(1);
        }
	}//for

	close(listenfd);
}
