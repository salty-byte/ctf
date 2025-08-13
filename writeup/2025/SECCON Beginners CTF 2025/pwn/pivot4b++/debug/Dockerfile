FROM ubuntu:22.04@sha256:08e2cd26ee66d0d46d6394df594f2877fc9b9381d9630a9ef5d86e27dfae9a95 AS base
WORKDIR /app
COPY chall run
RUN echo "ctf4b{*** REDACTED ***}" > /flag.txt
RUN  mv /flag.txt /app/flag-$(md5sum /flag.txt | awk '{print $1}').txt
RUN apt-get update && apt-get install -y gdb gdbserver socat
CMD ["socat", "TCP-LISTEN:5000,reuseaddr,fork", "EXEC:./run"]
