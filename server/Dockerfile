FROM node:boron

WORKDIR /src

# Install app dependencies
# COPY client/reviewminer/package.json /usr/src/reviewminer-web/client/reviewminer/
# RUN cd ../client/reviewminer/ && ls -l
# RUN cd ../client/reviewminer/ && npm install -g @angular/cli && npm install && cd ../../server/
COPY web/package.json /src/
RUN npm install --quiet


# Bundle app source
# COPY ./client/reviewminer/ /usr/src/reviewminer-web/client/reviewminer
COPY ./web/ /src/

# Expose port 8080
EXPOSE 8080

#Init command
CMD [ "npm", "run", "build" ]
