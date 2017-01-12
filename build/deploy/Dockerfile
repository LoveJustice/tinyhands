FROM yfix/ssh
MAINTAINER benaduggan

COPY deploycfg.encrypted /deploycfg.encrypted
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/bin/sh", "-c", "/run.sh"]
