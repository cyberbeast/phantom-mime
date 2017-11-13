FROM node:boron

WORKDIR /src

COPY web/package.json /src/
RUN npm install --quiet

COPY ./web/ /src/

EXPOSE 8080

CMD [ "npm", "run", "build" ]
