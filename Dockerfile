FROM python:3.9
WORKDIR /code

RUN python3 -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 80
COPY . .
CMD [ "python3", "main.py" ]