# PYTHON
FROM python:3.10.9-bullseye

ENV NODE_VERSION=16.13.0
RUN apt install -y curl
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
RUN node --version
RUN npm --version



# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# create and set workdir
WORKDIR /app/server
# copy local project
COPY .. .

#update pip
# install requirements
RUN pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# make our server-entrypoint.sh executable
RUN chmod +x ./deploy/config/server-entrypoint.sh
EXPOSE 8100
# execute our server-entrypoint.sh file
ENTRYPOINT ["./deploy/config/server-entrypoint.sh"]
