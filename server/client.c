#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <linux/tcp.h>
#include <errno.h>


#define PORT 9000
#define MAX_LINE 2048
#define LISTENQ 60

#define SOL_TCP 6

int main(int argc , char **argv)
{
  int sockfd;
  struct sockaddr_in servaddr;
  char buffer[MAX_LINE];

  struct mptcp_info minfo;
  struct mptcp_meta_info meta_info;
  struct tcp_info initial;
  struct tcp_info others[3];
  struct mptcp_sub_info others_info[3];

  struct mptcp_sched_info sched_info;
  sched_info.len = 3;
  unsigned char quota[3];
  unsigned char segments[3];

  sched_info.quota = &quota;
  sched_info.num_segments = &segments;

  minfo.tcp_info_len = sizeof(struct tcp_info);
  minfo.sub_len = sizeof(others);
  minfo.meta_len = sizeof(struct mptcp_meta_info);
  minfo.meta_info = &meta_info;
  minfo.initial = &initial;
  minfo.subflows = &others;
  minfo.sub_info_len = sizeof(struct mptcp_sub_info);
  minfo.total_sub_info_len = sizeof(others_info);
  minfo.subflow_info = &others_info;

  if(argc != 3)
  {
    perror("usage: client <IP> <file>");
    exit(1);
  }



  if((sockfd = socket(AF_INET , SOCK_STREAM , 0)) == -1)
	{
		perror("socket error");
		exit(1);
	}

  int enable = 1;
  setsockopt(sockfd, 6, 42, &enable, sizeof(enable));
  printf("%s\n", argv[2]);

  FILE *fp = fopen(argv[2], "r");


  bzero(&servaddr , sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons(PORT);
	if(inet_pton(AF_INET , argv[1] , &servaddr.sin_addr) < 0)
	{
		printf("inet_pton error for %s\n",argv[1]);
		exit(1);
	}

  if( connect(sockfd, (struct sockaddr *)&servaddr , sizeof(servaddr)) < 0)
	{
		perror("connect error");
		exit(1);
	}

  bzero(buffer, sizeof(buffer));
  send(sockfd, argv[2], strlen(argv[2]), 0);
  recv(sockfd, buffer, MAX_LINE, 0);
  printf("tip %s. \n", buffer);
  socklen_t len=sizeof(minfo);
  socklen_t slen=sizeof(struct mptcp_sched_info);
  
  int val = MPTCP_INFO_FLAG_SAVE_MASTER;
  setsockopt(sockfd, SOL_TCP, MPTCP_INFO, &val, sizeof(val));
  getsockopt(sockfd, SOL_TCP, MPTCP_SCHED_INFO, &sched_info, &slen);

  printf("num of segments : %d\n", segments[1]);

  int length = 0;
  int write_length = 0;
  int flag = 1;
  bzero(buffer, sizeof(buffer));

  while(length = fread(buffer, sizeof(char), MAX_LINE, fp))
  {
      if(length < 0)
      {
          perror("recieve data from server error.\n");
          flag = 0;
          break;
      }

      write_length = send(sockfd, buffer, length, 0);



      if(write_length < length)
      {
          perror("write file error.\n");
          flag = 0;
          break;
      }
      bzero(buffer, sizeof(buffer));
  }

  getsockopt(sockfd, SOL_TCP, MPTCP_INFO, &minfo, &len);
  segments[0] = 2;
  segments[1] = 3;
  segments[2] = 4;
  setsockopt(sockfd, SOL_TCP, MPTCP_SCHED_INFO, &sched_info, sizeof(sched_info));

  //getsockopt(sockfd, SOL_TCP, MPTCP_SCHED_INFO, &sched_info, sizeof(sched_info));

  printf("num of segments : %d\n", segments[1]);

  printf("mptcpi_bytes_acked: %d\n", meta_info.mptcpi_bytes_acked);

  if (flag)
  {
    printf("send file %s to server finished.\n", argv[2]);
  }

  fclose(fp);
  close(sockfd);
}
